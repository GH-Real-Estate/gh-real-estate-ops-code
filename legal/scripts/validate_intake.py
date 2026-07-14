#!/usr/bin/env python3
"""Fail closed when legal intake evidence could be mistaken for current law."""

from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path, PurePosixPath
from typing import Any, Iterable
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[2]

TOP_LEVEL_KEYS = frozenset(
    {
        "schema_version",
        "record_id",
        "received_on",
        "classification",
        "source_document",
        "storage",
        "review",
        "scope",
        "comparison",
        "notice",
    }
)
SOURCE_DOCUMENT_KEYS = frozenset(
    {
        "original_filename",
        "media_type",
        "byte_size",
        "sha256",
        "self_reported_last_updated",
        "embedded_links",
    }
)
STORAGE_KEYS = frozenset(
    {"storage_class", "binary_stored", "rights_status", "redistribution_status"}
)
REVIEW_KEYS = frozenset(
    {"status", "reviewed_on", "excluded_from_approved_current", "disposition"}
)
SCOPE_KEYS = frozenset(
    {
        "claimed_scope",
        "observed_scope",
        "heading_count",
        "populated_operative_section_count",
        "blank_or_repealed_heading_count",
        "first_section",
        "last_section",
        "reserved_ranges",
    }
)
COMPARISON_KEYS = frozenset(
    {
        "performed_on",
        "official_index",
        "repository_current",
        "document_overlap",
        "differences",
    }
)

RECORD_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{2,127}$")
SHA256_RE = re.compile(r"^[a-f0-9]{64}$")
HOST_RE = re.compile(r"^[a-z0-9.-]+$")
SECTION_RE = re.compile(r"^58-[0-9,]+[a-z]?$")
RANGE_RE = re.compile(r"^58-[0-9,]+[a-z]? through 58-[0-9,]+[a-z]?$")
INDEX_LABEL_RE = re.compile(r"^[0-9]{4} Kansas Statutes$")
ARTICLE_25_INDEX_PATH_RE = re.compile(
    r"^/(?:b[0-9]{4}_[0-9]{2}/)?laws/"
    r"058_000_0000_chapter/058_025_0000_article/$"
)
MANIFEST_NAME_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}-[a-z0-9-]+\.json$")


class ValidationError(ValueError):
    """Raised when an intake record violates a fail-closed control."""


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValidationError(f"duplicate JSON property: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> Any:
    """Load JSON while rejecting duplicate properties that standard parsing hides."""
    try:
        return json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValidationError(f"cannot read valid UTF-8 JSON from {path}: {exc}") from exc


def _mapping(value: Any, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValidationError(f"{context} must be an object")
    return value


def _exact_keys(value: Any, expected: frozenset[str], context: str) -> dict[str, Any]:
    record = _mapping(value, context)
    keys = set(record)
    missing = expected - keys
    extra = keys - expected
    if missing or extra:
        details = []
        if missing:
            details.append(f"missing {', '.join(sorted(missing))}")
        if extra:
            details.append(f"unexpected {', '.join(sorted(extra))}")
        raise ValidationError(f"{context} has invalid properties: {'; '.join(details)}")
    return record


def _string(value: Any, context: str, *, minimum: int = 1, maximum: int = 1000) -> str:
    if not isinstance(value, str) or not (minimum <= len(value) <= maximum):
        raise ValidationError(
            f"{context} must be a string between {minimum} and {maximum} characters"
        )
    return value


def _integer(value: Any, context: str, *, minimum: int = 0) -> int:
    # bool is an int subclass; accepting it would weaken count validation.
    if type(value) is not int or value < minimum:
        raise ValidationError(
            f"{context} must be an integer greater than or equal to {minimum}"
        )
    return value


def _date(value: Any, context: str) -> date:
    text = _string(value, context, minimum=10, maximum=10)
    try:
        parsed = date.fromisoformat(text)
    except ValueError as exc:
        raise ValidationError(f"{context} must be a valid YYYY-MM-DD date") from exc
    if parsed.isoformat() != text:
        raise ValidationError(f"{context} must use canonical YYYY-MM-DD format")
    return parsed


def _unique_strings(
    value: Any,
    context: str,
    *,
    minimum_items: int = 0,
    item_pattern: re.Pattern[str] | None = None,
) -> list[str]:
    if not isinstance(value, list) or len(value) < minimum_items:
        raise ValidationError(
            f"{context} must be an array with at least {minimum_items} item(s)"
        )
    result: list[str] = []
    for index, item in enumerate(value):
        text = _string(item, f"{context}[{index}]")
        if item_pattern and not item_pattern.fullmatch(text):
            raise ValidationError(f"{context}[{index}] has an invalid format")
        result.append(text)
    if len(result) != len(set(result)):
        raise ValidationError(f"{context} must not contain duplicates")
    return result


def _constant(value: Any, expected: Any, context: str) -> None:
    if value != expected or type(value) is not type(expected):
        raise ValidationError(f"{context} must be {expected!r}")


def _safe_repository_path(
    value: Any,
    context: str,
    repo_root: Path,
    *,
    kind: str,
) -> Path:
    text = _string(value, context, maximum=500)
    if "\\" in text or ":" in text:
        raise ValidationError(f"{context} must be a portable repository-relative path")
    relative = PurePosixPath(text)
    if (
        relative.is_absolute()
        or not relative.parts
        or any(part in {"", ".", ".."} for part in relative.parts)
    ):
        raise ValidationError(f"{context} must not be absolute or traverse directories")

    root = repo_root.resolve()
    target = root.joinpath(*relative.parts).resolve()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise ValidationError(f"{context} resolves outside the repository") from exc

    if kind == "file" and not target.is_file():
        raise ValidationError(f"{context} does not identify an existing file: {text}")
    if kind == "directory" and not target.is_dir():
        raise ValidationError(f"{context} does not identify an existing directory: {text}")
    return target


def _official_https_url(value: Any, context: str) -> str:
    text = _string(value, context, maximum=1000)
    try:
        parsed = urlsplit(text)
        port = parsed.port
    except ValueError as exc:
        raise ValidationError(f"{context} is not a valid URL") from exc
    if (
        parsed.scheme != "https"
        or parsed.hostname != "www.kslegislature.gov"
        or parsed.username is not None
        or parsed.password is not None
        or port is not None
        or parsed.query
        or parsed.fragment
        or not parsed.path.startswith("/")
    ):
        raise ValidationError(
            f"{context} must be a credential-free HTTPS URL on www.kslegislature.gov "
            "without a port, query, or fragment"
        )
    if not ARTICLE_25_INDEX_PATH_RE.fullmatch(parsed.path):
        raise ValidationError(
            f"{context} must identify the Kansas Chapter 58 Article 25 index"
        )
    return text


def validate_schema_contract(repo_root: Path = ROOT) -> None:
    """Ensure the checked-in schema preserves the intake-only safety invariants."""
    schema_path = repo_root / "legal" / "schemas" / "intake-record.schema.json"
    schema = _mapping(load_json(schema_path), "intake schema")
    if schema.get("additionalProperties") is not False:
        raise ValidationError("intake schema must reject additional top-level properties")
    if set(schema.get("required", [])) != TOP_LEVEL_KEYS:
        raise ValidationError("intake schema required properties do not match the validator")
    properties = _mapping(schema.get("properties"), "intake schema properties")
    if set(properties) != TOP_LEVEL_KEYS:
        raise ValidationError("intake schema properties do not match the validator")
    definitions = _mapping(schema.get("$defs"), "intake schema $defs")
    storage = _mapping(definitions.get("storage"), "intake schema storage definition")
    storage_properties = _mapping(storage.get("properties"), "intake schema storage properties")
    review = _mapping(definitions.get("review"), "intake schema review definition")
    review_properties = _mapping(review.get("properties"), "intake schema review properties")
    if storage_properties.get("binary_stored", {}).get("const") is not False:
        raise ValidationError("intake schema must prohibit binary storage")
    if review_properties.get("excluded_from_approved_current", {}).get("const") is not True:
        raise ValidationError("intake schema must exclude records from approved current law")


def validate_record(data: Any, repo_root: Path = ROOT) -> None:
    """Validate one metadata-only intake record and its referenced repository evidence."""
    record = _exact_keys(data, TOP_LEVEL_KEYS, "record")
    _constant(record["schema_version"], 1, "schema_version")
    record_id = _string(record["record_id"], "record_id", maximum=128)
    if not RECORD_ID_RE.fullmatch(record_id):
        raise ValidationError("record_id has an invalid format")
    received_on = _date(record["received_on"], "received_on")
    if received_on > date.today():
        raise ValidationError("received_on cannot be in the future")
    _constant(
        record["classification"],
        "user-provided-historical-reference",
        "classification",
    )

    source = _exact_keys(
        record["source_document"], SOURCE_DOCUMENT_KEYS, "source_document"
    )
    filename = _string(
        source["original_filename"],
        "source_document.original_filename",
        maximum=255,
    )
    if "/" in filename or "\\" in filename or not filename.lower().endswith(".docx"):
        raise ValidationError("source_document.original_filename must be a basename ending in .docx")
    _constant(
        source["media_type"],
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "source_document.media_type",
    )
    _integer(source["byte_size"], "source_document.byte_size", minimum=1)
    digest = _string(source["sha256"], "source_document.sha256", minimum=64, maximum=64)
    if not SHA256_RE.fullmatch(digest):
        raise ValidationError("source_document.sha256 must be a lowercase SHA-256 digest")
    source_updated = _date(
        source["self_reported_last_updated"],
        "source_document.self_reported_last_updated",
    )
    if source_updated > received_on:
        raise ValidationError("the document-stated update date cannot be after receipt")

    links = _exact_keys(
        source["embedded_links"],
        frozenset({"total_count", "unique_count", "hosts"}),
        "source_document.embedded_links",
    )
    total_links = _integer(
        links["total_count"], "source_document.embedded_links.total_count"
    )
    unique_links = _integer(
        links["unique_count"], "source_document.embedded_links.unique_count"
    )
    hosts = _unique_strings(
        links["hosts"],
        "source_document.embedded_links.hosts",
        minimum_items=1,
        item_pattern=HOST_RE,
    )
    if unique_links > total_links or len(hosts) > unique_links:
        raise ValidationError("embedded-link counts are inconsistent")

    storage = _exact_keys(record["storage"], STORAGE_KEYS, "storage")
    _constant(storage["storage_class"], "hash-and-metadata-only", "storage.storage_class")
    _constant(storage["binary_stored"], False, "storage.binary_stored")
    _constant(storage["rights_status"], "unknown-review-required", "storage.rights_status")
    _constant(
        storage["redistribution_status"],
        "unknown-do-not-redistribute",
        "storage.redistribution_status",
    )

    review = _exact_keys(record["review"], REVIEW_KEYS, "review")
    _constant(
        review["status"],
        "reviewed-for-scope-and-currentness-not-approved-as-authority",
        "review.status",
    )
    reviewed_on = _date(review["reviewed_on"], "review.reviewed_on")
    if reviewed_on > date.today():
        raise ValidationError("review.reviewed_on cannot be in the future")
    _constant(
        review["excluded_from_approved_current"],
        True,
        "review.excluded_from_approved_current",
    )
    _constant(
        review["disposition"],
        "metadata-only-no-current-authority-change",
        "review.disposition",
    )

    scope = _exact_keys(record["scope"], SCOPE_KEYS, "scope")
    _string(scope["claimed_scope"], "scope.claimed_scope", maximum=500)
    _string(scope["observed_scope"], "scope.observed_scope", maximum=500)
    heading_count = _integer(scope["heading_count"], "scope.heading_count", minimum=1)
    populated_count = _integer(
        scope["populated_operative_section_count"],
        "scope.populated_operative_section_count",
    )
    blank_count = _integer(
        scope["blank_or_repealed_heading_count"],
        "scope.blank_or_repealed_heading_count",
    )
    if heading_count != populated_count + blank_count:
        raise ValidationError("scope heading counts do not reconcile")
    for field in ("first_section", "last_section"):
        section = _string(scope[field], f"scope.{field}", maximum=30)
        if not SECTION_RE.fullmatch(section):
            raise ValidationError(f"scope.{field} has an invalid Kansas section format")
    _unique_strings(
        scope["reserved_ranges"],
        "scope.reserved_ranges",
        item_pattern=RANGE_RE,
    )

    comparison = _exact_keys(record["comparison"], COMPARISON_KEYS, "comparison")
    performed_on = _date(comparison["performed_on"], "comparison.performed_on")
    if performed_on > date.today():
        raise ValidationError("comparison.performed_on cannot be in the future")
    if reviewed_on != performed_on or performed_on < received_on:
        raise ValidationError("comparison and review dates must match and not precede receipt")

    official = _exact_keys(
        comparison["official_index"],
        frozenset({"publisher", "url", "label", "operative_section_count"}),
        "comparison.official_index",
    )
    _constant(
        official["publisher"],
        "Kansas Legislature",
        "comparison.official_index.publisher",
    )
    _official_https_url(official["url"], "comparison.official_index.url")
    label = _string(official["label"], "comparison.official_index.label", maximum=50)
    if not INDEX_LABEL_RE.fullmatch(label):
        raise ValidationError(
            "comparison.official_index.label must name a dated Kansas Statutes edition"
        )
    official_count = _integer(
        official["operative_section_count"],
        "comparison.official_index.operative_section_count",
        minimum=1,
    )

    repository = _exact_keys(
        comparison["repository_current"],
        frozenset(
            {"authority_directory", "registry_path", "bundle_path", "operative_section_count"}
        ),
        "comparison.repository_current",
    )
    authority_directory = _safe_repository_path(
        repository["authority_directory"],
        "comparison.repository_current.authority_directory",
        repo_root,
        kind="directory",
    )
    registry_path = _safe_repository_path(
        repository["registry_path"],
        "comparison.repository_current.registry_path",
        repo_root,
        kind="file",
    )
    bundle_path = _safe_repository_path(
        repository["bundle_path"],
        "comparison.repository_current.bundle_path",
        repo_root,
        kind="file",
    )
    repository_count = _integer(
        repository["operative_section_count"],
        "comparison.repository_current.operative_section_count",
        minimum=1,
    )
    markdown_count = sum(
        1
        for path in authority_directory.iterdir()
        if path.is_file() and path.suffix == ".md"
    )
    if markdown_count != repository_count:
        raise ValidationError(
            "repository current-section count does not match the authority directory "
            f"({repository_count} recorded, {markdown_count} files)"
        )
    registry_records = load_json(registry_path)
    if not isinstance(registry_records, list) or len(registry_records) != repository_count:
        raise ValidationError(
            "repository current-section count does not match the Article 25 registry"
        )
    if any(
        not isinstance(item, dict)
        or item.get("group") != "core_article25"
        or item.get("release_status") != "included-in-approved-release"
        for item in registry_records
    ):
        raise ValidationError("Article 25 registry contains an unexpected group or release status")
    if bundle_path.read_bytes()[:5] != b"%PDF-":
        raise ValidationError("comparison.repository_current.bundle_path is not a PDF")

    overlap = _exact_keys(
        comparison["document_overlap"],
        frozenset(
            {
                "common_operative_section_count",
                "document_new_operative_section_count",
                "document_omitted_current_section_count",
                "document_only_blank_headings",
            }
        ),
        "comparison.document_overlap",
    )
    common_count = _integer(
        overlap["common_operative_section_count"],
        "comparison.document_overlap.common_operative_section_count",
    )
    new_count = _integer(
        overlap["document_new_operative_section_count"],
        "comparison.document_overlap.document_new_operative_section_count",
    )
    omitted_count = _integer(
        overlap["document_omitted_current_section_count"],
        "comparison.document_overlap.document_omitted_current_section_count",
    )
    blank_headings = _unique_strings(
        overlap["document_only_blank_headings"],
        "comparison.document_overlap.document_only_blank_headings",
        item_pattern=SECTION_RE,
    )
    if populated_count != common_count + new_count:
        raise ValidationError("document populated-section and overlap counts do not reconcile")
    if official_count != common_count + omitted_count:
        raise ValidationError("official-index and omitted-section counts do not reconcile")
    if repository_count != official_count:
        raise ValidationError("repository and observed official operative-section counts differ")
    if len(blank_headings) != blank_count:
        raise ValidationError("document-only blank headings do not match the recorded blank count")

    differences = _unique_strings(
        comparison["differences"],
        "comparison.differences",
        minimum_items=1,
    )
    if any(len(item) < 10 for item in differences):
        raise ValidationError("comparison differences must be descriptive")
    _string(record["notice"], "notice", minimum=40, maximum=1000)


def validate_intake_file_types(paths: Iterable[Path]) -> None:
    """Reject source binaries and every other ungoverned intake file type."""
    for path in paths:
        if path.suffix.lower() not in {".json", ".md"}:
            raise ValidationError(
                f"intake binary or unsupported file is prohibited: {path.name}"
            )


def validate_intake_files(intake_dir: Path) -> list[Path]:
    """Validate directory hygiene and return the JSON manifests to inspect."""
    if not intake_dir.is_dir():
        raise ValidationError(f"missing intake directory: {intake_dir}")
    if not (intake_dir / "README.md").is_file():
        raise ValidationError("legal intake directory must contain README.md")
    validate_intake_file_types(path for path in intake_dir.rglob("*") if path.is_file())
    manifests = sorted(intake_dir.glob("*.json"))
    if not manifests:
        raise ValidationError("legal intake directory contains no JSON records")
    for path in manifests:
        if not MANIFEST_NAME_RE.fullmatch(path.name):
            raise ValidationError(f"intake record filename must start with an ISO date: {path.name}")
        if not path.with_suffix(".md").is_file():
            raise ValidationError(f"intake record lacks a human-readable companion: {path.name}")
    return manifests


def validate_all(repo_root: Path = ROOT) -> int:
    validate_schema_contract(repo_root)
    intake_dir = repo_root / "legal" / "manifests" / "intake"
    manifests = validate_intake_files(intake_dir)
    record_ids: set[str] = set()
    for path in manifests:
        record = load_json(path)
        validate_record(record, repo_root)
        record_id = record["record_id"]
        if record_id in record_ids:
            raise ValidationError(f"duplicate intake record_id: {record_id}")
        record_ids.add(record_id)
    return len(manifests)


def main() -> int:
    try:
        count = validate_all(ROOT)
    except ValidationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(
        f"Legal intake metadata valid: {count} record(s); "
        "all are excluded from approved current law and no source binaries are stored."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
