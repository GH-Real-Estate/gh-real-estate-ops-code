#!/usr/bin/env python3
"""Fetch official Kansas statutes and related primary-source PDFs.

The output is deliberately granular.  The build step concatenates these official
files without altering their text and adds a dated retrieval manifest.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

from lxml import html
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "tmp/pdfs/source_downloads/kansas"
BASE = "https://www.kslegislature.gov"
SESSION = f"{BASE}/b2025_26/laws"
UA = "GH-Legal-Source-Pack/2026-07-12 (document retrieval)"


@dataclass(frozen=True)
class Item:
    group: str
    citation: str
    title: str
    url: str
    filename: str
    authority: str = "Binding statute (official consolidated text)"
    applicability: str = "See master applicability index"


def request_bytes(url: str, attempts: int = 4) -> bytes:
    last: Exception | None = None
    for n in range(attempts):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=45) as resp:
                data = resp.read()
            return data
        except Exception as exc:  # pragma: no cover - network retry path
            last = exc
            time.sleep(1.2 * (n + 1))
    raise RuntimeError(f"failed after {attempts} attempts: {url}: {last}")


def article_url(chapter: str, article: str) -> str:
    match = re.fullmatch(r"(\d+)([A-Za-z]*)", article)
    if not match:
        raise ValueError(f"invalid article identifier: {article}")
    article_slug = f"{int(match.group(1)):03d}{match.group(2).lower()}"
    return (
        f"{SESSION}/{int(chapter):03d}_000_0000_chapter/"
        f"{int(chapter):03d}_{article_slug}_0000_article/"
    )


def safe_name(text: str) -> str:
    text = text.replace(",", "_")
    text = re.sub(r"[^A-Za-z0-9._-]+", "-", text).strip("-.")
    return text[:180]


def parse_article(group: str, chapter: str, article: str, keep=None) -> list[Item]:
    url = article_url(chapter, article)
    tree = html.fromstring(request_bytes(url))
    found: list[Item] = []
    for anchor in tree.xpath('//table[@id="statute"]//a'):
        bold = anchor.xpath(".//b")
        if not bold:
            continue
        citation = " ".join(bold[0].itertext()).strip()
        label = " ".join(" ".join(anchor.itertext()).split())
        title = label.split(" - ", 1)[1] if " - " in label else label
        if keep is not None and not keep(citation):
            continue
        section_page = urllib.parse.urljoin(url, anchor.get("href"))
        marker = "/laws/"
        rel = section_page.split(marker, 1)[1].rstrip("/")
        pdf_url = f"{BASE}/media/statute/{rel}.pdf"
        found.append(
            Item(
                group=group,
                citation=f"K.S.A. {citation}",
                title=title,
                url=pdf_url,
                filename=f"{safe_name(citation)}.pdf",
            )
        )
    if not found:
        raise RuntimeError(f"no sections found at {url}")
    return found


def norm_cite(citation: str) -> str:
    return citation.replace(" ", "")


def relevant_consumer(cite: str) -> bool:
    c = norm_cite(cite)
    if c == "50-6,139b":
        return True
    m = re.fullmatch(r"50-(\d+)", c)
    return bool(m and 623 <= int(m.group(1)) <= 643)


def fire_sections(cite: str) -> bool:
    c = norm_cite(cite)
    if c == "31-132a":
        return True
    m = re.fullmatch(r"31-(\d+)", c)
    return bool(m and 133 <= int(m.group(1)) <= 164)


def exact(*citations: str):
    wanted = {norm_cite(c) for c in citations}
    return lambda c: norm_cite(c) in wanted


def external_items() -> list[Item]:
    return [
        Item(
            "2026_addenda",
            "2026 Sub. HB 2357 (enrolled)",
            "Eviction record expungement and mediation amendments; effective July 1, 2026",
            "https://www.kslegislature.gov/b2025_26/bills/download/?apn=b2025_26%2Fyear2%2Fready_for_publication%2Fhb_2357%2Fhb2357_enrolled.pdf",
            "2026_Sub_HB_2357_Enrolled.pdf",
            "Enacted session law / enrolled bill",
            "Direct; amends eviction procedure",
        ),
        Item(
            "2026_addenda",
            "2026 SB 391 (enrolled)",
            "Local housing-policy preemption; effective July 1, 2026",
            "https://www.kslegislature.gov/b2025_26/bills/download/?apn=b2025_26%2Fyear2%2Fready_for_publication%2Fsb_391%2Fsb391_enrolled.pdf",
            "2026_SB_391_Enrolled.pdf",
            "Enacted session law / enrolled bill",
            "Direct state-local overlay",
        ),
        Item(
            "fair_housing_regulations",
            "K.A.R. Agency 21 compilation",
            "Kansas Human Rights Commission rules and regulations (Article 60 fair housing at PDF pp. 39–47)",
            "http://www.khrc.net/pdf/RulesAndRegs.pdf",
            "KAR_Agency_21_Human_Rights_Commission.pdf",
            "Official agency regulation compilation; verify live SOS text before enforcement",
            "Direct fair-housing rules; compilation date requires live currentness check",
        ),
        Item(
            "fair_housing_regulations",
            "KHRC fair housing poster",
            "Kansas fair housing poster",
            "http://www.khrc.net/pdf/kshousing_poster.pdf",
            "KHRC_Fair_Housing_Poster.pdf",
            "Official agency poster / guidance",
            "Operational posting and protected-class reference",
        ),
        Item(
            "agency_guidance",
            "Kansas State Fire Marshal",
            "Apartment inspection checklist",
            "https://firemarshal.ks.gov/DocumentCenter/View/1681/Apartment-Checklist",
            "KSFM_Apartment_Checklist.pdf",
            "Nonbinding agency checklist",
            "Operational safety reference; local adopted codes also control",
        ),
        Item(
            "court_guidance",
            "Kansas Supreme Court Task Force",
            "Best practices for eviction proceedings",
            "https://kscourts.gov/kscourts/media/kscourts/court%20administration/Committees/eviction/best-practices-eviction-proceedings.pdf",
            "Kansas_Judiciary_Eviction_Best_Practices.pdf",
            "Nonbinding judicial-administration guidance",
            "Eviction workflow reference",
        ),
    ]


def all_items() -> list[Item]:
    items: list[Item] = []
    # Entire Article 25 is intentionally preserved, including mobile-home and
    # agricultural provisions, so no Article 25 text is silently omitted.
    items += parse_article("core_article25", "58", "25")

    # Kansas limited-actions procedure surrounding eviction.
    for art in range(28, 42):
        items += parse_article("eviction_procedure", "61", str(art))

    items += parse_article("fair_housing", "44", "10")
    items += parse_article("service_animals", "39", "11")
    items += parse_article("consumer_protection", "50", "6", relevant_consumer)
    items += parse_article("state_fcra", "50", "7")
    items += parse_article("data_breach", "50", "7a")
    items += parse_article("electronic_transactions", "16", "16")
    items += parse_article("fire_smoke", "31", "1", fire_sections)
    items += parse_article(
        "lead_statutes",
        "65",
        "1",
        lambda c: bool(
            (m := re.fullmatch(r"65-1,(\d+)", norm_cite(c)))
            and 200 <= int(m.group(1)) <= 214
        ),
    )
    items += parse_article(
        "state_local_overlays", "12", "16", exact("12-16,120", "12-16,123", "12-16,138")
    )
    items += parse_article("misc_financial", "60", "26", exact("60-2610"))
    items += parse_article("misc_financial", "16", "2", exact("16-201"))
    items += parse_article("licensing_conditional", "58", "30", exact("58-3037"))
    items += external_items()
    return items


def fetch_one(item: Item) -> dict:
    folder = OUT / item.group
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / item.filename
    data = request_bytes(item.url)
    if not data.startswith(b"%PDF"):
        raise RuntimeError(f"not a PDF: {item.url} ({data[:80]!r})")
    path.write_bytes(data)
    reader = PdfReader(path)
    return {
        "group": item.group,
        "citation": item.citation,
        "title": item.title,
        "authority": item.authority,
        "applicability": item.applicability,
        "official_url": item.url,
        "retrieved": "2026-07-12",
        "sha256": hashlib.sha256(data).hexdigest(),
        "local_path": str(path.relative_to(ROOT)),
        "pages": len(reader.pages),
        "bytes": len(data),
    }


def local_case_records() -> list[dict]:
    """Register exact opinion extracts made from official Kansas advance sheets."""
    specs = [
        (
            "Case_Washburn_South_Apartments_v_Hession_2025.pdf",
            "Washburn South Apartments v. Hession, 65 Kan. App. 2d 626 (2025)",
            "Habitability duties and purported as-is terms",
            "https://searchdro.kscourts.gov/documents/pdf/caseDecisions/35eb8078-f850-4db2-88f5-7dee881cc1ae_126456.pdf",
            "Direct habitability interpretation; check subsequent history",
        ),
        (
            "Case_Schutt_v_Foster_2025.pdf",
            "Schutt v. Foster, 320 Kan. 852 (2025)",
            "Late fee and unconscionability preservation issues",
            "https://searchdro.kscourts.gov/documents/pdf/caseDecisions/e8a35794-dc62-47c6-9184-09c89c4b9bda_126555.pdf",
            "Direct to fee-policy review; not categorical approval of any fee schedule",
        ),
        (
            "Case_Housing_Authority_v_McConnell_2026.pdf",
            "Housing Authority v. McConnell, 66 Kan. App. 2d 566 (2026)",
            "Specificity required in a K.S.A. 58-2564 cure notice",
            "https://searchdro.kscourts.gov/documents/pdf/caseDecisions/9b383f12-cd71-4187-8223-da58dfb25543_128977.pdf",
            "Direct to breach and cure notices; check subsequent history",
        ),
    ]
    out = []
    for filename, citation, title, url, applicability in specs:
        path = OUT / "cases" / filename
        if not path.exists():
            raise FileNotFoundError(
                f"Missing exact case extract {path}; create it from the official Kansas advance sheet"
            )
        data = path.read_bytes()
        out.append(
            {
                "group": "cases",
                "citation": citation,
                "title": title,
                "authority": "Published judicial opinion; exact pages extracted from official advance sheet",
                "applicability": applicability,
                "official_url": url,
                "retrieved": "2026-07-12",
                "sha256": hashlib.sha256(data).hexdigest(),
                "local_path": str(path.relative_to(ROOT)),
                "pages": len(PdfReader(path).pages),
                "bytes": len(data),
            }
        )
    return out


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    items = all_items()
    records: list[dict] = []
    errors: list[dict] = []
    with ThreadPoolExecutor(max_workers=12) as pool:
        jobs = {pool.submit(fetch_one, item): item for item in items}
        for job in as_completed(jobs):
            item = jobs[job]
            try:
                record = job.result()
                records.append(record)
                print(f"Fetched {record['citation']} ({record['pages']}p)", flush=True)
            except Exception as exc:
                errors.append({"citation": item.citation, "url": item.url, "error": str(exc)})
                print(f"ERROR {item.citation}: {exc}", flush=True)
    records.extend(local_case_records())
    records.sort(key=lambda r: (r["group"], r["citation"]))
    payload = {
        "title": "GH Kansas legal source retrieval manifest",
        "as_of": "2026-07-12",
        "session": "2025-2026 Kansas Legislature",
        "record_count": len(records),
        "error_count": len(errors),
        "records": records,
        "errors": errors,
    }
    (OUT / "kansas_manifest.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {OUT / 'kansas_manifest.json'}: {len(records)} records, {len(errors)} errors")
    if errors:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
