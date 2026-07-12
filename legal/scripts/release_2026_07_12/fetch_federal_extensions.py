#!/usr/bin/env python3
"""Extend the federal cache with conditional program and litigation sources."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "tmp/pdfs/source_downloads/federal"
RAW = OUT / "raw/extensions"
ECFR_DATE = "2026-07-09"


def load_builder():
    path = OUT / "build_sources.py"
    spec = importlib.util.spec_from_file_location("federal_builder", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(path: Path, *, group: str, title: str, citation: str, authority: str,
           applicability: str, url: str, currentness: str, archive: Path | None = None) -> dict:
    result = {
        "group": group,
        "title": title,
        "citation": citation,
        "authority": authority,
        "applicability": applicability,
        "official_url": url,
        "retrieved": "2026-07-12",
        "currentness": currentness,
        "sha256": sha(path),
        "local_path": str(path.relative_to(ROOT)),
        "pages": len(PdfReader(path).pages),
        "bytes": path.stat().st_size,
    }
    if archive:
        result["source_archive_path"] = str(archive.relative_to(ROOT))
        result["source_archive_sha256"] = sha(archive)
        result["render_note"] = "Searchable PDF rendered from versioned official eCFR XML; exact XML retained."
    return result


def download(url: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["curl", "-L", "--fail", "--silent", "--show-error", "--max-time", "180", url, "-o", str(path)],
        check=True,
    )
    if path.read_bytes()[:5] != b"%PDF-":
        raise RuntimeError(f"not a PDF: {path}")
    PdfReader(path)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    b = load_builder()
    records: list[dict] = []

    ecfr_specs = [
        (
            b.ECFRSpec(
                "31_24_CFR_Part_180_Fair_Housing_Adjudication_2026-07-09.pdf",
                "Consolidated HUD Fair Housing Act Administrative Proceedings",
                "24 C.F.R. part 180",
                "Tier 1 — binding federal regulation",
                "Triggered by administrative adjudication of a Fair Housing Act charge; useful for litigation procedure and sanctions.",
                24, 180,
            ),
            "fair_housing",
        ),
        (
            b.ECFRSpec(
                "32_24_CFR_Part_982_Housing_Choice_Voucher_2026-07-09.pdf",
                "Section 8 Tenant-Based Assistance: Housing Choice Voucher Program",
                "24 C.F.R. part 982",
                "Tier 1 — binding federal regulation; HCV participation dependent",
                "Conditional: applies when a unit/tenancy participates in the Housing Choice Voucher program and interacts with the HAP contract, tenancy addendum and PHA plan.",
                24, 982,
            ),
            "conditional_hud",
        ),
        (
            b.ECFRSpec(
                "33_24_CFR_Part_1_Title_VI_HUD_Programs_2026-07-09.pdf",
                "Nondiscrimination in Federally Assisted Programs of HUD",
                "24 C.F.R. part 1",
                "Tier 1 — binding federal regulation; federal-assistance dependent",
                "Conditional: applies to recipients of federal financial assistance from HUD under Title VI.",
                24, 1,
            ),
            "conditional_hud",
        ),
        (
            b.ECFRSpec(
                "34_24_CFR_Part_146_Age_Discrimination_HUD_2026-07-09.pdf",
                "Nondiscrimination on the Basis of Age in HUD Programs",
                "24 C.F.R. part 146",
                "Tier 1 — binding federal regulation; federal-assistance dependent",
                "Conditional: applies to covered HUD programs or activities receiving federal financial assistance.",
                24, 146,
            ),
            "conditional_hud",
        ),
        (
            b.ECFRSpec(
                "35_24_CFR_Part_35_Subpart_M_Tenant_Based_Lead_2026-07-09.pdf",
                "Tenant-Based Rental Assistance Lead-Safe Housing Rule",
                "24 C.F.R. part 35, subpart M",
                "Tier 1 — binding federal regulation; covered assistance dependent",
                "Conditional: applies to covered tenant-based rental assistance in pre-1978 housing, subject to the subpart's exemptions and thresholds.",
                24, 35, "M",
            ),
            "conditional_hud",
        ),
    ]
    for spec, group in ecfr_specs:
        api = f"https://www.ecfr.gov/api/versioner/v1/full/{ECFR_DATE}/title-{spec.title_no}.xml?part={spec.part}"
        xml = RAW / f"title-{spec.title_no}_part-{spec.part}_{ECFR_DATE}.xml"
        if not xml.exists():
            xml.write_bytes(b.request_bytes(api))
        pdf = OUT / spec.filename
        b.render_ecfr(spec, xml, pdf)
        records.append(
            record(
                pdf,
                group=group,
                title=spec.title,
                citation=spec.citation,
                authority=spec.authority_tier,
                applicability=spec.applicability,
                url=api,
                currentness=f"Official eCFR XML as of {ECFR_DATE}.",
                archive=xml,
            )
        )
        print(f"Rendered {spec.citation}: {records[-1]['pages']} pages", flush=True)

    direct = [
        (
            "36_VAWA_34_USC_12471-12495_USCode_2024.pdf",
            "Violence Against Women Act housing rights and covered housing programs",
            "34 U.S.C. chapter 121, subchapter III",
            "Tier 1 — binding federal statute; covered-housing-program dependent",
            "Conditional: applies to covered housing programs; Kansas survivor protections may apply independently.",
            "https://www.govinfo.gov/content/pkg/USCODE-2024-title34/pdf/USCODE-2024-title34-subtitleI-chap121-subchapIII.pdf",
            "conditional_hud",
        ),
        (
            "37_Section_504_29_USC_794_USCode_2024.pdf",
            "Section 504 of the Rehabilitation Act",
            "29 U.S.C. § 794",
            "Tier 1 — binding federal statute; federal-financial-assistance dependent",
            "Conditional: applies to a program or activity receiving federal financial assistance; 24 C.F.R. part 8 implements HUD duties.",
            "https://www.govinfo.gov/content/pkg/USCODE-2024-title29/pdf/USCODE-2024-title29-chap16-subchapV-sec794.pdf",
            "conditional_hud",
        ),
        (
            "38_Title_VI_42_USC_2000d-et-seq_USCode_2024.pdf",
            "Title VI of the Civil Rights Act of 1964",
            "42 U.S.C. §§ 2000d–2000d-7",
            "Tier 1 — binding federal statute; federal-assistance dependent",
            "Conditional: prohibits race, color and national-origin discrimination in programs receiving federal financial assistance.",
            "https://www.govinfo.gov/content/pkg/USCODE-2024-title42/pdf/USCODE-2024-title42-chap21-subchapV.pdf",
            "conditional_hud",
        ),
        (
            "39_Lead_Disclosure_Statute_42_USC_4852d_USCode_2024.pdf",
            "Lead-based paint disclosure statute",
            "42 U.S.C. § 4852d (within chapter 63A, subchapter IV, part B)",
            "Tier 1 — binding federal statute",
            "Directly relevant to most leases of pre-1978 housing, subject to statutory and regulatory exemptions.",
            "https://www.govinfo.gov/content/pkg/USCODE-2024-title42/pdf/USCODE-2024-title42-chap63A.pdf",
            "lead_screening_overlays",
        ),
        (
            "40_Bankruptcy_Code_11_USC_Chapter_3_USCode_2024.pdf",
            "Bankruptcy case administration, including automatic stay and unexpired leases",
            "11 U.S.C. chapter 3, including §§ 362 and 365",
            "Tier 1 — binding federal statute; bankruptcy-event dependent",
            "Conditional: do not continue collection or possession activity after a bankruptcy filing without analyzing the automatic stay and eviction exceptions.",
            "https://www.govinfo.gov/content/pkg/USCODE-2024-title11/pdf/USCODE-2024-title11-chap3.pdf",
            "lead_screening_overlays",
        ),
        (
            "41_SCRA_2026_Housing_Rent_Ceiling_91_FR.pdf",
            "2026 SCRA housing price inflation adjustment",
            "91 Fed. Reg. notice dated March 10, 2026",
            "Tier 2 — official annual statutory-adjustment notice",
            "Conditional: applies to SCRA residential eviction protection; 2026 monthly rent ceiling is $10,542.60.",
            "https://www.govinfo.gov/content/pkg/FR-2026-03-10/pdf/2026-04689.pdf",
            "lead_screening_overlays",
        ),
    ]
    for filename, title, citation, authority, applicability, url, group in direct:
        pdf = OUT / filename
        download(url, pdf)
        records.append(
            record(
                pdf,
                group=group,
                title=title,
                citation=citation,
                authority=authority,
                applicability=applicability,
                url=url,
                currentness="Official 2024 U.S. Code edition or dated 2026 Federal Register notice; verify later changes.",
            )
        )
        print(f"Downloaded {citation}: {records[-1]['pages']} pages", flush=True)

    # Files downloaded separately from stable official DOJ/GovInfo endpoints.
    stable = [
        (
            "17_HUD_DOJ_Reasonable_Accommodations_Joint_Statement_2004.pdf",
            "HUD/DOJ reasonable accommodations joint statement",
            "HUD/DOJ Joint Statement (May 17, 2004)",
            "Tier 2 — official interpretive guidance; nonbinding",
            "Relevant to disability-related changes to rules, policies, practices and services; binding law controls.",
            "https://www.justice.gov/sites/default/files/crt/legacy/2010/12/14/joint_statement_ra.pdf",
            "fair_housing",
        ),
        (
            "18_HUD_DOJ_Reasonable_Modifications_Joint_Statement_2008.pdf",
            "HUD/DOJ reasonable modifications joint statement",
            "HUD/DOJ Joint Statement (Mar. 5, 2008)",
            "Tier 2 — official interpretive guidance; nonbinding",
            "Relevant to disability-related structural-change requests and cost allocation; binding law controls.",
            "https://www.justice.gov/sites/default/files/crt/legacy/2010/12/15/reasonable_modifications_mar08.pdf",
            "fair_housing",
        ),
        (
            "15_HUD_Keating_Occupancy_Standards_Memorandum.pdf",
            "Keating occupancy enforcement policy",
            "63 Fed. Reg. 70256 (Dec. 18, 1998)",
            "Tier 2 — statutorily preserved HUD enforcement policy; rebuttable",
            "Two persons per bedroom is a starting point, not a hard limit; unit facts and selective enforcement matter.",
            "https://www.govinfo.gov/content/pkg/FR-1998-12-18/pdf/98-33568.pdf",
            "fair_housing",
        ),
    ]
    # These are already present in the main manifest; do not duplicate them.

    payload = {
        "title": "GH federal source extensions",
        "as_of": "2026-07-12",
        "ecfr_as_of": ECFR_DATE,
        "records": records,
    }
    (OUT / "federal_extension_manifest.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {OUT / 'federal_extension_manifest.json'} with {len(records)} records")


if __name__ == "__main__":
    main()
