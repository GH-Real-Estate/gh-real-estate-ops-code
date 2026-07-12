#!/usr/bin/env python3
"""Export one searchable Markdown authority record per canonical source PDF."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path

from pypdf import PdfReader


MAX_TEXT_CHARS = 150_000


def slug(value: str) -> str:
    value = value.lower().replace("§", " section ")
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value[:110] or "authority"


def jurisdiction(filename: str) -> str:
    if filename.startswith("GH-KS"):
        return "kansas"
    if filename.startswith("GH-FED"):
        return "federal"
    if filename.startswith("GH-OP"):
        return "overland-park"
    return "other"


def legal_status(authority: str) -> str:
    lowered = authority.lower()
    if "withdrawn" in lowered:
        return "withdrawn"
    if "proposed" in lowered:
        return "proposed-monitoring-only"
    if any(
        marker in lowered
        for marker in ("nonbinding", "guidance", "checklist", "poster", "pamphlet", "compliance aid", "enforcement policy", "model form")
    ):
        return "guidance"
    if "conditional" in lowered or "dependent" in lowered:
        return "conditional-binding"
    if "published judicial opinion" in lowered:
        return "published-case-law"
    if "federal register notice" in lowered or "statutory-adjustment notice" in lowered:
        return "official-notice"
    if any(marker in lowered for marker in ("binding", "statute", "regulation", "code", "enacted session law")):
        return "binding"
    return "other-review-required"


def chunks(pages: list[str]) -> list[str]:
    output: list[str] = []
    current = ""
    for page_no, text in enumerate(pages, start=1):
        section = f"\n\n## Official source page {page_no}\n\n{text.strip()}\n"
        if current and len(current) + len(section) > MAX_TEXT_CHARS:
            output.append(current)
            current = ""
        if len(section) <= MAX_TEXT_CHARS:
            current += section
            continue
        for start in range(0, len(section), MAX_TEXT_CHARS):
            if current:
                output.append(current)
                current = ""
            output.append(section[start : start + MAX_TEXT_CHARS])
    if current or not output:
        output.append(current)
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True, help="Original release-build root")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    data = json.loads(args.manifest.read_text(encoding="utf-8"))
    if args.output.exists():
        shutil.rmtree(args.output)
    args.output.mkdir(parents=True)

    count = 0
    for bundle in data["bundles"]:
        place = jurisdiction(bundle["filename"])
        for source in bundle["sources"]:
            source_path = args.root / source["local_path"]
            reader = PdfReader(source_path)
            page_text = [(page.extract_text() or "") for page in reader.pages]
            parts = chunks(page_text)
            short_hash = str(source["sha256"])[:10]
            base = f"{slug(str(source['citation']))}-{short_hash}"
            folder = args.output / place / slug(str(source.get("group", "other")))
            folder.mkdir(parents=True, exist_ok=True)

            for part_no, body in enumerate(parts, start=1):
                suffix = f"-part-{part_no:02d}" if len(parts) > 1 else ""
                path = folder / f"{base}{suffix}.md"
                header = [
                    f"# {source['citation']} — {source['title']}",
                    "",
                    f"- Jurisdiction: {place}",
                    f"- Legal status: {legal_status(str(source['authority']))}",
                    f"- Authority label: {source['authority']}",
                    f"- Applicability: {source['applicability']}",
                    f"- Official source: {source['official_url']}",
                    f"- Retrieved: {source.get('retrieved', source.get('retrieved_at', '2026-07-12'))}",
                    f"- Official-source SHA-256: `{source['sha256']}`",
                    f"- Approved bundle: `{bundle['filename']}`",
                    f"- Bundle pages: {source['bundle_start_page']}–{source['bundle_end_page']}",
                    f"- Release verified through: {data['as_of']}",
                    f"- Extract part: {part_no} of {len(parts)}",
                    "",
                    "> Official source text controls over this extraction and all summaries. This record is an internal research aid, not legal advice.",
                ]
                if not body.strip():
                    body = "\n\n_No machine-readable text was extracted. Use the approved PDF and official source URL._\n"
                path.write_text("\n".join(header) + body, encoding="utf-8")
                count += 1

    print(f"Wrote {count} Markdown authority files to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
