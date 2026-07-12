#!/usr/bin/env python3
"""Validate the GH accounting authority registry and dated sourcebook release."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path


ACCOUNTING = Path(__file__).resolve().parents[1]
REGISTRY = ACCOUNTING / "manifests/fasb_topic_registry.json"
RELEASE = ACCOUNTING / "manifests/sourcebook_release.json"
INDEX = ACCOUNTING / "FASB_APPLICABILITY_INDEX.md"


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_date(value: object, field: str, topic_id: str) -> date:
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        fail(f"{topic_id} has invalid {field}: {value}")


def validate_topics() -> int:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    topics = data.get("topics", [])
    defaults = data.get("record_defaults", {})
    allowed = set(data.get("allowed_classifications", []))
    suffixes = set(data.get("section_suffixes", {}))
    index_text = INDEX.read_text(encoding="utf-8")

    if len(topics) != 54:
        fail(f"expected 54 FASB topic records, found {len(topics)}")
    if defaults.get("copyrighted_text_stored") is not False:
        fail("record default copyrighted_text_stored must be false")
    if not str(defaults.get("official_url", "")).startswith("https://"):
        fail("record default official_url must be HTTPS")

    required = {
        "id",
        "topic",
        "title",
        "classification",
        "priority",
        "gh_relevance",
        "triggers",
        "research_sections",
        "private_company_review_required",
        "next_review",
    }
    seen_ids: set[str] = set()
    seen_topics: set[int] = set()
    for record in topics:
        missing = required.difference(record)
        if missing:
            fail(f"topic record lacks {', '.join(sorted(missing))}: {record.get('id')}")

        topic_id = str(record["id"])
        topic = int(record["topic"])
        if not re.fullmatch(r"ASC-[0-9]{3}", topic_id):
            fail(f"invalid topic id: {topic_id}")
        if topic_id != f"ASC-{topic:03d}":
            fail(f"topic/id mismatch: {topic_id} versus {topic}")
        if topic_id in seen_ids or topic in seen_topics:
            fail(f"duplicate topic: {topic_id}")
        seen_ids.add(topic_id)
        seen_topics.add(topic)

        if record["classification"] not in allowed:
            fail(f"{topic_id} has unsupported classification: {record['classification']}")
        if not isinstance(record["triggers"], list) or not record["triggers"]:
            fail(f"{topic_id} must have at least one trigger")
        sections = record["research_sections"]
        if not isinstance(sections, list) or "15" not in sections:
            fail(f"{topic_id} must prioritize section 15 scope research")
        unknown = set(sections).difference(suffixes)
        if unknown:
            fail(f"{topic_id} uses unknown section suffixes: {sorted(unknown)}")
        if not isinstance(record["private_company_review_required"], bool):
            fail(f"{topic_id} private_company_review_required must be boolean")
        parse_date(record["next_review"], "next_review", topic_id)
        if f"ASC {topic}" not in index_text:
            fail(f"{topic_id} is absent from FASB_APPLICABILITY_INDEX.md")

    required_core = {105, 205, 210, 230, 235, 250, 305, 310, 326, 360, 405, 450, 470, 505, 835, 842, 850, 855, 970}
    if not required_core.issubset(seen_topics):
        fail(f"core topic set incomplete: {sorted(required_core.difference(seen_topics))}")
    return len(topics)


def validate_release() -> tuple[int, int]:
    data = json.loads(RELEASE.read_text(encoding="utf-8"))
    records = data.get("files", [])
    if len(records) != 4:
        fail(f"expected 4 accounting sourcebook PDFs, found {len(records)}")

    pages = 0
    source_text = []
    for record in records:
        pdf = ACCOUNTING.parent / record["repository_path"]
        text = ACCOUNTING.parent / record["text_path"]
        if not pdf.is_file() or pdf.read_bytes()[:5] != b"%PDF-":
            fail(f"missing or invalid PDF: {pdf}")
        if pdf.stat().st_size != int(record["bytes"]):
            fail(f"byte-size mismatch: {pdf}")
        if sha256(pdf) != record["sha256"]:
            fail(f"SHA-256 mismatch: {pdf}")
        if not text.is_file() or text.stat().st_size < 10_000:
            fail(f"missing or empty searchable text: {text}")
        source_text.append(text.read_text(encoding="utf-8"))
        pages += int(record["pages"])

    if pages != 33:
        fail(f"expected 33 sourcebook pages, found {pages}")
    joined = "\n".join(source_text)
    joined = re.sub(r"(JC-[A-Z]+-)\s*\n\s*([0-9A-Z]+)", r"\1\2", joined)
    source_pattern = re.compile(
        r"^\s+(?:FED-[0-9A-Z]+|GAAP-[0-9A-Z]+|KS-[A-Z]+-[0-9A-Z]+|"
        r"OP-[A-Z]+-[0-9A-Z]+|JC-[A-Z]+-[0-9A-Z]+)\s+",
        re.MULTILINE,
    )
    source_records = len(source_pattern.findall(joined))
    if "JC-SEARCH-" in joined and re.search(r"^\s+001\s*$", joined, re.MULTILINE):
        source_records += 1
    expected_sources = int(data["source_record_count"])
    if source_records != expected_sources:
        fail(f"expected {expected_sources} source-register records, found {source_records}")
    return len(records), pages


def main() -> int:
    topic_count = validate_topics()
    file_count, pages = validate_release()
    print(
        f"Accounting authority release valid: {topic_count} FASB topic records, "
        f"{file_count} sourcebook PDFs, {pages} pages."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
