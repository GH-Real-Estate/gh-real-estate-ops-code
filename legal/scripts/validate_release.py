#!/usr/bin/env python3
"""Validate the approved GH Real Estate legal-source release."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


LEGAL = Path(__file__).resolve().parents[1]
RELEASE = LEGAL / "manifests/releases/2026-07-12.json"
PDF_DIR = LEGAL / "generated/project-sources/current"
TEXT_DIR = LEGAL / "text/current/full"
CHUNK_DIR = LEGAL / "text/current/chunks"
AUTHORITY_TEXT_DIR = LEGAL / "text/current/authorities"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def normalized_text_size(content: bytes) -> int:
    """Measure repository text independently of checkout line-ending conversion."""
    return len(content.replace(b"\r\n", b"\n"))


def connector_text_size(path: Path) -> int:
    return normalized_text_size(path.read_bytes())


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    if not RELEASE.is_file():
        fail(f"missing release manifest: {RELEASE}")

    data = json.loads(RELEASE.read_text(encoding="utf-8"))
    records = [data["master"], *data["bundles"]]
    if len(records) != 8:
        fail(f"expected 8 release PDFs, found {len(records)}")

    total_pages = 0
    source_count = 0
    for record in records:
        filename = record["filename"]
        path = PDF_DIR / filename
        if not path.is_file():
            fail(f"missing PDF: {path}")
        if path.read_bytes()[:5] != b"%PDF-":
            fail(f"invalid PDF signature: {path}")
        actual = sha256(path)
        if actual != record["sha256"]:
            fail(f"SHA-256 mismatch for {filename}: {actual}")
        total_pages += int(record["pages"])
        source_count += len(record.get("sources", []))

        text_path = TEXT_DIR / f"{Path(filename).stem}.txt"
        if not text_path.is_file() or connector_text_size(text_path) < 500:
            fail(f"missing or empty searchable text: {text_path}")
        chunks = sorted(CHUNK_DIR.glob(f"{Path(filename).stem}.part-*.txt"))
        if not chunks or any(connector_text_size(chunk) > 220_000 for chunk in chunks):
            fail(f"missing or oversized connector-search chunk for {filename}")

    if total_pages != 1718:
        fail(f"expected 1,718 pages, found {total_pages}")
    if source_count != 447:
        fail(f"expected 447 source records, found {source_count}")

    registry = LEGAL / "manifests/authority_registry.json"
    authority_records = json.loads(registry.read_text(encoding="utf-8"))
    if len(authority_records) != 447:
        fail(f"expected 447 registry entries, found {len(authority_records)}")

    required = {"citation", "title", "authority", "official_url", "sha256", "bundle_filename"}
    for index, record in enumerate(authority_records, start=1):
        missing = required.difference(record)
        if missing:
            fail(f"registry entry {index} lacks: {', '.join(sorted(missing))}")
        if not str(record["official_url"]).startswith(("https://", "http://")):
            fail(f"registry entry {index} has invalid official URL")

    authority_text = sorted(AUTHORITY_TEXT_DIR.rglob("*.md"))
    if len(authority_text) < 447:
        fail(f"expected at least 447 per-authority Markdown files, found {len(authority_text)}")
    if any(connector_text_size(path) > 180_000 for path in authority_text):
        fail("one or more connector-search Markdown files exceed 180,000 bytes")

    print(
        f"Legal release valid: {len(records)} PDFs, {total_pages:,} pages, "
        f"{source_count} source records, {len(authority_text)} connector Markdown files."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
