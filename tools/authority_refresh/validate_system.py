"""Validate the authority-refresh trust boundary and approved baseline metadata.

This validator is intentionally standard-library only so it can run in a clean
GitHub Actions runner.  It checks repository invariants that JSON Schema alone
cannot express, including path existence, baseline-count reconciliation,
immutable release-chain continuity, licensing controls, review-only workflows,
and ASC topic-locator integrity.
It never contacts an external source and never modifies repository content.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Callable, Iterable

try:  # Support both ``python -m`` and direct script execution.
    from . import promotion
    from .core import (
        DEFAULT_COMPLETE_INDEX_BASELINE_RATIO,
        AuthorityRefreshError,
        load_catalog,
        sha256_json,
    )
except ImportError:  # pragma: no cover - exercised by the workflow command.
    import promotion  # type: ignore[no-redef]
    from core import (  # type: ignore[no-redef]
        DEFAULT_COMPLETE_INDEX_BASELINE_RATIO,
        AuthorityRefreshError,
        load_catalog,
        sha256_json,
    )


EXPECTED_SOURCE_COUNTS = {"legal": 14, "accounting": 9}
KANSAS_ARTICLE_25_SOURCE_ID = "kansas-chapter-58-article-25-index"
KANSAS_ARTICLE_25_DISCOVERY_URL = (
    "https://www.kslegislature.gov/laws/058_000_0000_chapter/"
    "058_025_0000_article/"
)
KANSAS_ARTICLE_25_LINK_PATTERN = (
    r"^https://www\.kslegislature\.gov/b[0-9]{4}_[0-9]{2}/"
    r"laws/058_000_0000_chapter/058_025_0000_article/"
    r"(058_025_[0-9a-z]+)_section/\1_k/?$"
)
EXPECTED_WORKFLOWS = {
    "checks": Path(".github/workflows/authority-refresh-checks.yml"),
    "discovery": Path(".github/workflows/authority-discovery.yml"),
    "promotion": Path(".github/workflows/authority-release-promotion.yml"),
}
IMMUTABLE_RELEASE_FILENAMES = frozenset(
    {
        "candidate.json",
        "approval.json",
        "validation-context.json",
        "release.json",
    }
)
PROHIBITED_STATUS_KEYS = {
    "compliant",
    "compliance_certified",
    "legally_compliant",
    "gaap_compliant",
    "tax_compliant",
    "fully_current",
}
ASC_TOPIC_PATTERN = re.compile(r"ASC ([0-9]{3})")


@dataclass
class ValidationReport:
    """Collect all failures so one CI run reports every actionable defect."""

    checks: int = 0
    json_files: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    def require(self, condition: bool, message: str) -> None:
        self.checks += 1
        if not condition:
            self.errors.append(message)

    def error(self, message: str) -> None:
        self.checks += 1
        self.errors.append(message)


def _relative_label(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def _load_json(path: Path, root: Path, report: ValidationReport) -> Any | None:
    label = _relative_label(root, path)
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        report.error(f"{label}: cannot parse JSON: {exc}")
        return None
    report.require(True, f"{label}: JSON parses")
    return value


def _json_paths(root: Path) -> list[Path]:
    """Return governed JSON files without scanning generated test scratch space."""

    locations = [
        root / "legal",
        root / "accounting",
        root / "authority",
        root / "tools" / "authority_refresh" / "config",
    ]
    paths: set[Path] = set()
    for location in locations:
        if location.is_dir():
            paths.update(path for path in location.rglob("*.json") if path.is_file())
    return sorted(paths, key=lambda path: path.as_posix())


def _read_governed_json(root: Path, report: ValidationReport) -> dict[Path, Any]:
    parsed: dict[Path, Any] = {}
    paths = _json_paths(root)
    report.json_files = len(paths)
    report.require(bool(paths), "no governed JSON files were found")
    for path in paths:
        value = _load_json(path, root, report)
        if value is not None:
            parsed[path] = value
    return parsed


def _data(parsed: dict[Path, Any], root: Path, relative: str) -> Any | None:
    return parsed.get(root / Path(relative))


def _is_safe_relative_path(value: object) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    normalized = value.replace("\\", "/")
    parts = normalized.split("/")
    return (
        not normalized.startswith("/")
        and not re.match(r"^[A-Za-z]:", normalized)
        and ".." not in parts
    )


def _require_repository_path(
    root: Path,
    value: object,
    context: str,
    report: ValidationReport,
) -> None:
    safe = _is_safe_relative_path(value)
    report.require(safe, f"{context}: repository path must be safe and relative: {value!r}")
    if not safe:
        return
    path = root / Path(str(value))
    report.require(path.exists(), f"{context}: referenced path does not exist: {value}")


def _walk_keys(value: Any, location: str = "$") -> Iterable[tuple[str, str]]:
    if isinstance(value, dict):
        for key, child in value.items():
            key_name = str(key)
            yield key_name, f"{location}.{key_name}"
            yield from _walk_keys(child, f"{location}.{key_name}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk_keys(child, f"{location}[{index}]")


def _parse_iso_date(value: object, context: str, report: ValidationReport) -> date | None:
    try:
        parsed = date.fromisoformat(str(value))
    except (TypeError, ValueError):
        report.error(f"{context}: expected an ISO date, got {value!r}")
        return None
    report.require(True, f"{context}: valid ISO date")
    return parsed


def _validate_status(
    root: Path,
    parsed: dict[Path, Any],
    domain: str,
    report: ValidationReport,
) -> dict[str, Any] | None:
    relative = f"{domain}/CURRENT_STATUS.json"
    status = _data(parsed, root, relative)
    if not isinstance(status, dict):
        report.error(f"{relative}: must contain a JSON object")
        return None

    report.require(status.get("domain") == domain, f"{relative}: domain must be {domain}")
    for key, location in _walk_keys(status):
        report.require(
            key.casefold() not in PROHIBITED_STATUS_KEYS,
            f"{relative}: prohibited blanket-compliance key at {location}",
        )

    approved = status.get("approved_release")
    report.require(isinstance(approved, dict), f"{relative}: approved_release must be an object")
    if not isinstance(approved, dict):
        return status

    report.require(
        approved.get("release_status") == "approved-dated-baseline",
        f"{relative}: release_status must remain approved-dated-baseline",
    )
    overall_state = str(status.get("overall_state", "")).casefold()
    for overclaim in ("compliant", "certified-current", "fully-current", "always-current"):
        report.require(
            overclaim not in overall_state,
            f"{relative}: overall_state makes an unsupported currentness/compliance claim",
        )
    notice = str(status.get("notice", "")).casefold()
    report.require(
        "not" in notice and ("compli" in notice or "legal advice" in notice or "cpa" in notice),
        f"{relative}: notice must expressly disclaim compliance/advice certification",
    )

    status_as_of = _parse_iso_date(status.get("status_as_of"), f"{relative} status_as_of", report)
    current_through = _parse_iso_date(
        approved.get("current_through"), f"{relative} approved_release.current_through", report
    )
    if status_as_of and current_through:
        report.require(
            status_as_of <= date.today(),
            f"{relative}: status_as_of cannot be in the future",
        )
        report.require(
            current_through <= date.today(),
            f"{relative}: current_through cannot be in the future",
        )
        report.require(
            current_through <= status_as_of,
            f"{relative}: current_through cannot be later than status_as_of",
        )

    limitations = status.get("known_limitations")
    report.require(
        isinstance(limitations, list) and bool(limitations),
        f"{relative}: known_limitations must be a nonempty list",
    )

    for key, value in approved.items():
        if key.endswith("_path"):
            _require_repository_path(root, value, f"{relative} approved_release.{key}", report)
    authoritative_paths = status.get("authoritative_paths")
    report.require(
        isinstance(authoritative_paths, list) and bool(authoritative_paths),
        f"{relative}: authoritative_paths must be a nonempty list",
    )
    if isinstance(authoritative_paths, list):
        for index, value in enumerate(authoritative_paths):
            _require_repository_path(root, value, f"{relative} authoritative_paths[{index}]", report)
    return status


def _validate_kansas_article_25_source(
    sources: list[dict[str, Any]],
    label: str,
    report: ValidationReport,
) -> None:
    """Keep the stable Kansas index monitor bounded and review-only."""

    source = next(
        (
            value
            for value in sources
            if value.get("source_id") == KANSAS_ARTICLE_25_SOURCE_ID
        ),
        None,
    )
    report.require(
        source is not None,
        f"{label}: required source {KANSAS_ARTICLE_25_SOURCE_ID} is missing",
    )
    if source is None:
        return
    expected = {
        "discovery_url": KANSAS_ARTICLE_25_DISCOVERY_URL,
        "adapter": "official_html_index",
        "storage_policy": "metadata-only",
        "critical": True,
        "missing_detection": "complete-index",
        "minimum_items": 90,
        "maximum_items": 150,
        "minimum_baseline_ratio": 0.9,
        "allowed_hosts": ["www.kslegislature.gov"],
        "link_filter": {
            "include_patterns": [KANSAS_ARTICLE_25_LINK_PATTERN],
            "exclude_patterns": [],
        },
    }
    for field, value in expected.items():
        report.require(
            source.get(field) == value,
            f"{label}: {KANSAS_ARTICLE_25_SOURCE_ID}.{field} must be {value!r}",
        )


def _validate_catalogs(root: Path, report: ValidationReport) -> None:
    for domain, expected_count in EXPECTED_SOURCE_COUNTS.items():
        path = root / "tools" / "authority_refresh" / "config" / f"{domain}_sources.json"
        label = _relative_label(root, path)
        try:
            catalog = load_catalog(path, domain=domain)
        except (AuthorityRefreshError, AttributeError, TypeError, ValueError) as exc:
            report.error(f"{label}: catalog validation failed: {exc}")
            continue
        sources = catalog["sources"]
        report.require(
            len(sources) == expected_count,
            f"{label}: expected {expected_count} official source adapters, found {len(sources)}",
        )
        for source in sources:
            if source.get("missing_detection", "complete-index") != "complete-index":
                continue
            source_id = str(source.get("source_id", "unknown"))
            minimum_items = source.get("minimum_items")
            report.require(
                isinstance(minimum_items, int)
                and not isinstance(minimum_items, bool)
                and minimum_items >= 2,
                f"{label}: complete-index source {source_id} requires an explicit "
                "bootstrap minimum_items floor of at least two",
            )
            baseline_ratio = source.get(
                "minimum_baseline_ratio", DEFAULT_COMPLETE_INDEX_BASELINE_RATIO
            )
            report.require(
                isinstance(baseline_ratio, (int, float))
                and not isinstance(baseline_ratio, bool)
                and baseline_ratio >= DEFAULT_COMPLETE_INDEX_BASELINE_RATIO,
                f"{label}: complete-index source {source_id} must retain at least "
                f"{DEFAULT_COMPLETE_INDEX_BASELINE_RATIO:.0%} baseline coverage",
            )
        if domain == "legal":
            _validate_kansas_article_25_source(sources, label, report)
        if domain != "accounting":
            continue
        fasb_sources = []
        for source in sources:
            publisher = str(source.get("publisher", "")).casefold()
            hosts = [str(host).casefold() for host in source.get("allowed_hosts", [])]
            if (
                "fasb" in publisher
                or "financial accounting standards board" in publisher
                or any(host == "fasb.org" or host.endswith(".fasb.org") for host in hosts)
            ):
                fasb_sources.append(source)
        report.require(bool(fasb_sources), f"{label}: at least one FASB notice source is required")
        for source in fasb_sources:
            source_id = str(source.get("source_id", "unknown"))
            report.require(
                source.get("storage_policy") != "redistributable",
                f"{label}: FASB source {source_id} must never be redistributable",
            )
            discovery_contract = " ".join(
                str(source.get(key, ""))
                for key in ("discovery_url", "adapter", "source_id", "authority_type")
            ).casefold()
            report.require(
                "codification" not in discovery_contract and "asc.fasb.org" not in discovery_contract,
                f"{label}: FASB source {source_id} must monitor public notices, not scrape Codification",
            )


def _validate_legal_baseline(
    root: Path,
    parsed: dict[Path, Any],
    status: dict[str, Any] | None,
    report: ValidationReport,
) -> set[str]:
    approved = status.get("approved_release", {}) if status else {}
    if not isinstance(approved, dict):
        return set()
    registry_path = str(
        approved.get("authority_registry_path", "legal/manifests/authority_registry.json")
    )
    release_path = str(approved.get("manifest_path", ""))
    registry = _data(parsed, root, registry_path)
    release = _data(parsed, root, release_path)
    report.require(isinstance(registry, list), "legal authority registry must be an array")
    report.require(isinstance(release, dict), "legal release manifest must be an object")
    if not isinstance(registry, list) or not isinstance(release, dict) or not status:
        return set()

    official_urls: set[str] = set()
    for index, record in enumerate(registry):
        if isinstance(record, dict) and isinstance(record.get("official_url"), str):
            official_urls.add(record["official_url"])
        else:
            report.error(f"legal authority registry record {index} requires official_url")
    report.require(
        approved.get("authority_record_count") == len(registry),
        "legal CURRENT_STATUS authority_record_count does not match authority_registry.json",
    )
    report.require(
        approved.get("unique_official_url_count") == len(official_urls),
        "legal CURRENT_STATUS unique_official_url_count does not match the registry",
    )

    bundles = release.get("bundles")
    master = release.get("master")
    report.require(isinstance(bundles, list), "legal release bundles must be an array")
    report.require(isinstance(master, dict), "legal release master must be an object")
    if isinstance(bundles, list) and isinstance(master, dict):
        pdf_count = len(bundles) + 1
        page_values = [item.get("pages") for item in bundles if isinstance(item, dict)]
        page_values.append(master.get("pages"))
        pages_are_valid = all(
            isinstance(value, int) and not isinstance(value, bool) and value >= 0
            for value in page_values
        ) and len(page_values) == len(bundles) + 1
        report.require(
            pages_are_valid,
            "legal release manifest pages must be nonnegative integers",
        )
        report.require(
            approved.get("pdf_count") == pdf_count,
            "legal CURRENT_STATUS pdf_count does not match the release manifest",
        )
        if pages_are_valid:
            report.require(
                approved.get("page_count") == sum(page_values),
                "legal CURRENT_STATUS page_count does not match the release manifest",
            )
        source_count = sum(
            len(item.get("sources", []))
            for item in bundles
            if isinstance(item, dict) and isinstance(item.get("sources"), list)
        )
        report.require(
            source_count == len(registry),
            "legal release source count does not match the authority registry",
        )
    report.require(
        release.get("as_of") == approved.get("current_through"),
        "legal release date does not match CURRENT_STATUS current_through",
    )

    groups: set[str] = set()
    checked_paths: set[str] = set()
    for index, record in enumerate(registry):
        if not isinstance(record, dict):
            report.error(f"legal authority registry record {index} must be an object")
            continue
        if isinstance(record.get("group"), str):
            groups.add(record["group"])
        for key in ("bundle_path", "text_full_path"):
            value = record.get(key)
            if isinstance(value, str) and value not in checked_paths:
                checked_paths.add(value)
                _require_repository_path(root, value, f"legal registry record {index}.{key}", report)
    return groups


def _validate_accounting_baseline(
    root: Path,
    parsed: dict[Path, Any],
    status: dict[str, Any] | None,
    report: ValidationReport,
) -> set[int]:
    approved = status.get("approved_release", {}) if status else {}
    if not isinstance(approved, dict):
        return set()
    registry_path = str(
        approved.get("fasb_topic_registry_path", "accounting/manifests/fasb_topic_registry.json")
    )
    release_path = str(approved.get("release_manifest_path", ""))
    registry = _data(parsed, root, registry_path)
    release = _data(parsed, root, release_path)
    report.require(isinstance(registry, dict), "FASB topic registry must be an object")
    report.require(isinstance(release, dict), "accounting release manifest must be an object")
    if not isinstance(registry, dict) or not isinstance(release, dict) or not status:
        return set()
    topics = registry.get("topics")
    report.require(isinstance(topics, list), "FASB topic registry topics must be an array")
    if not isinstance(topics, list):
        return set()
    topic_numbers = {
        topic.get("topic") for topic in topics if isinstance(topic, dict) and isinstance(topic.get("topic"), int)
    }
    report.require(len(topic_numbers) == len(topics), "FASB topic numbers must be present and unique")

    report.require(
        approved.get("fasb_topic_locator_count") == len(topics),
        "accounting CURRENT_STATUS topic count does not match fasb_topic_registry.json",
    )
    report.require(
        approved.get("source_record_count") == release.get("source_record_count"),
        "accounting CURRENT_STATUS source_record_count does not match sourcebook_release.json",
    )
    files = release.get("files")
    report.require(isinstance(files, list), "accounting release files must be an array")
    if isinstance(files, list):
        page_values = [item.get("pages") for item in files if isinstance(item, dict)]
        pages_are_valid = all(
            isinstance(value, int) and not isinstance(value, bool) and value >= 0
            for value in page_values
        ) and len(page_values) == len(files)
        report.require(
            pages_are_valid,
            "accounting release manifest pages must be nonnegative integers",
        )
        report.require(
            approved.get("sourcebook_pdf_count") == len(files),
            "accounting CURRENT_STATUS PDF count does not match sourcebook_release.json",
        )
        if pages_are_valid:
            report.require(
                approved.get("sourcebook_page_count") == sum(page_values),
                "accounting CURRENT_STATUS page count does not match sourcebook_release.json",
            )
        for index, item in enumerate(files):
            if not isinstance(item, dict):
                report.error(f"accounting release file {index} must be an object")
                continue
            for key in ("repository_path", "text_path"):
                _require_repository_path(
                    root, item.get(key), f"accounting release files[{index}].{key}", report
                )
    report.require(
        release.get("release_date") == approved.get("current_through"),
        "accounting release date does not match CURRENT_STATUS current_through",
    )
    report.require(
        approved.get("fasb_codification_content_state") == "not-stored",
        "accounting CURRENT_STATUS must state that FASB Codification content is not stored",
    )
    defaults = registry.get("record_defaults", {})
    report.require(
        isinstance(defaults, dict) and defaults.get("copyrighted_text_stored") is False,
        "FASB registry must explicitly state copyrighted_text_stored=false",
    )
    return topic_numbers


def _validate_crosswalk(
    root: Path,
    parsed: dict[Path, Any],
    fasb_topics: set[int],
    legal_groups: set[str],
    report: ValidationReport,
) -> None:
    path = "authority/impact_crosswalk.json"
    crosswalk = _data(parsed, root, path)
    if not isinstance(crosswalk, dict):
        report.error(f"{path}: must contain an object")
        return
    mappings = crosswalk.get("mappings")
    report.require(isinstance(mappings, list) and bool(mappings), f"{path}: mappings must be nonempty")
    if not isinstance(mappings, list):
        return
    seen_ids: set[str] = set()
    for index, mapping in enumerate(mappings):
        context = f"{path} mappings[{index}]"
        if not isinstance(mapping, dict):
            report.error(f"{context}: must be an object")
            continue
        mapping_id = mapping.get("id")
        report.require(
            isinstance(mapping_id, str) and bool(mapping_id), f"{context}: id must be nonempty"
        )
        if isinstance(mapping_id, str):
            report.require(mapping_id not in seen_ids, f"{context}: duplicate mapping id {mapping_id}")
            seen_ids.add(mapping_id)
        report.require(
            mapping.get("automatic_change") == "prohibited",
            f"{context}: automatic_change must be prohibited",
        )

        affected_paths = mapping.get("affected_paths")
        report.require(
            isinstance(affected_paths, list) and bool(affected_paths),
            f"{context}: affected_paths must be nonempty",
        )
        if isinstance(affected_paths, list):
            for path_index, affected in enumerate(affected_paths):
                if not isinstance(affected, dict):
                    report.error(f"{context} affected_paths[{path_index}]: must be an object")
                    continue
                _require_repository_path(
                    root,
                    affected.get("repository_path"),
                    f"{context} affected_paths[{path_index}]",
                    report,
                )

        references = mapping.get("authority_references")
        report.require(
            isinstance(references, list) and bool(references),
            f"{context}: authority_references must be nonempty",
        )
        if not isinstance(references, list):
            continue
        for ref_index, reference in enumerate(references):
            ref_context = f"{context} authority_references[{ref_index}]"
            if not isinstance(reference, dict):
                report.error(f"{ref_context}: must be an object")
                continue
            ref_type = reference.get("reference_type")
            ref_value = reference.get("reference")
            if ref_type == "asc-topic-locator":
                match = ASC_TOPIC_PATTERN.fullmatch(str(ref_value))
                report.require(
                    match is not None,
                    f"{ref_context}: ASC locator must be exactly 'ASC ' plus three digits; paragraph locators are prohibited",
                )
                if match:
                    report.require(
                        int(match.group(1)) in fasb_topics,
                        f"{ref_context}: {ref_value} is absent from the FASB topic registry",
                    )
            elif ref_type == "legal-registry-group":
                report.require(
                    ref_value in legal_groups,
                    f"{ref_context}: legal registry group does not exist: {ref_value}",
                )
            if isinstance(ref_value, str):
                report.require(
                    not re.search(r"\bASC\s+[0-9]{3}[-–—][0-9]", ref_value, re.IGNORECASE)
                    and not re.search(r"\bparagraph\b", ref_value, re.IGNORECASE),
                    f"{ref_context}: invented paragraph-level locators are prohibited",
                )


def _validate_source_revision_blobs(
    node: dict[str, Any],
    load_blob: Callable[[str], bytes],
    report: ValidationReport,
) -> None:
    """Match archived context to the exact files in its recorded source commit."""

    context = node["validation_context"]
    label = node["label"]
    expected_json = {
        str(context.get("candidate_path", "")): node["candidate"],
        (
            f"authority/candidates/{node['candidate'].get('domain', '')}/"
            "latest/candidate.json"
        ): node["candidate"],
        str(context.get("approval_path", "")): node["approval"],
        str(context.get("source_catalog_path", "")): context.get("source_catalog"),
        str(context.get("impact_crosswalk_path", "")): context.get(
            "impact_crosswalk"
        ),
    }
    for path, expected in expected_json.items():
        try:
            payload = load_blob(path)
            actual = json.loads(payload.decode("utf-8"))
        except (AuthorityRefreshError, UnicodeError, json.JSONDecodeError) as exc:
            report.error(f"{label}: cannot verify source-revision JSON {path}: {exc}")
            continue
        report.require(
            actual == expected,
            f"{label}: source revision does not match archived {path}",
        )

    manifest = context.get("path_manifest")
    if not isinstance(manifest, list):
        return
    for entry in manifest:
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            continue
        path = entry["path"]
        try:
            payload = load_blob(path)
        except AuthorityRefreshError as exc:
            report.error(f"{label}: cannot verify reviewed source path {path}: {exc}")
            continue
        report.require(
            len(payload) == entry.get("size_bytes")
            and hashlib.sha256(payload).hexdigest() == entry.get("sha256"),
            f"{label}: reviewed path evidence does not match source revision: {path}",
        )


def _validate_release_introduction(
    first_parent_commits: list[str],
    *,
    release_directory: str,
    source_revision: str,
    files_at_commit: Callable[[str], set[str]],
) -> str:
    """Bind a release to the parent of its unique first-parent introduction.

    Promotion generates all immutable release files in one commit whose parent is
    the clean default-branch source revision. Following first-parent history makes
    the same invariant work on an automation branch, a pull-request test merge, a
    squash merge, and every later checkout without rebinding old releases to HEAD^.
    """

    if not first_parent_commits:
        raise AuthorityRefreshError(
            "first-parent history is unavailable for immutable release provenance"
        )
    expected_paths = {
        f"{release_directory}/{filename}"
        for filename in IMMUTABLE_RELEASE_FILENAMES
    }
    introduction_parent: str | None = None
    previous_commit: str | None = None
    release_present = False

    for commit in first_parent_commits:
        files = files_at_commit(commit)
        if files and files != expected_paths:
            missing = sorted(expected_paths.difference(files))
            extra = sorted(files.difference(expected_paths))
            raise AuthorityRefreshError(
                "immutable release files did not enter together or changed later; "
                f"commit={commit}, missing={missing}, extra={extra}"
            )
        present = files == expected_paths
        if present and not release_present:
            if previous_commit is None:
                raise AuthorityRefreshError(
                    "immutable release cannot be introduced in the repository root commit"
                )
            if introduction_parent is not None:
                raise AuthorityRefreshError(
                    "immutable release has multiple first-parent introductions"
                )
            introduction_parent = previous_commit
        elif release_present and not present:
            raise AuthorityRefreshError(
                "immutable release was removed from first-parent history"
            )
        release_present = present
        previous_commit = commit

    if not release_present or introduction_parent is None:
        raise AuthorityRefreshError(
            "immutable release introduction is unavailable from first-parent history"
        )
    if source_revision != introduction_parent:
        raise AuthorityRefreshError(
            "recorded source revision does not match the immutable release "
            f"introduction parent: expected {introduction_parent}, "
            f"actual {source_revision}"
        )
    return introduction_parent


def _validate_source_revision(
    root: Path,
    node: dict[str, Any],
    report: ValidationReport,
) -> None:
    """Verify release provenance against local Git history when it is available."""

    if not (root / ".git").exists():
        return
    context = node["validation_context"]
    revision = context.get("source_revision")
    if not isinstance(revision, str) or not re.fullmatch(
        r"(?:[0-9a-f]{40}|[0-9a-f]{64})", revision
    ):
        return

    def run_git(*arguments: str) -> subprocess.CompletedProcess[bytes]:
        try:
            return subprocess.run(
                ["git", "-C", str(root), *arguments],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=30,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            raise AuthorityRefreshError(f"cannot inspect Git history: {exc}") from exc

    try:
        commit = run_git("cat-file", "-e", f"{revision}^{{commit}}")
        if commit.returncode != 0:
            raise AuthorityRefreshError(
                "recorded source revision is unavailable; fetch full Git history"
            )
        ancestor = run_git("merge-base", "--is-ancestor", revision, "HEAD")
        if ancestor.returncode != 0:
            raise AuthorityRefreshError(
                "recorded source revision is not an ancestor of the checked-out commit"
            )
        first_parent = run_git("rev-list", "--first-parent", "--reverse", "HEAD")
        if first_parent.returncode != 0:
            raise AuthorityRefreshError("cannot read checked-out first-parent history")
        try:
            first_parent_commits = [
                line.decode("ascii")
                for line in first_parent.stdout.splitlines()
                if line.strip()
            ]
        except UnicodeDecodeError as exc:
            raise AuthorityRefreshError(
                "checked-out first-parent history contains an invalid object ID"
            ) from exc
        if (
            revision not in first_parent_commits
            or any(
                not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", value)
                for value in first_parent_commits
            )
        ):
            raise AuthorityRefreshError(
                "recorded source revision is not on the checked-out first-parent history"
            )

        release_directory = str(node["label"])

        def files_at_commit(commit_id: str) -> set[str]:
            result = run_git(
                "ls-tree",
                "-r",
                "--name-only",
                "-z",
                commit_id,
                "--",
                release_directory,
            )
            if result.returncode != 0:
                raise AuthorityRefreshError(
                    f"cannot inspect immutable release tree at {commit_id}"
                )
            try:
                return {
                    path.decode("utf-8")
                    for path in result.stdout.split(b"\0")
                    if path
                }
            except UnicodeDecodeError as exc:
                raise AuthorityRefreshError(
                    "immutable release history contains a non-UTF-8 path"
                ) from exc

        _validate_release_introduction(
            first_parent_commits,
            release_directory=release_directory,
            source_revision=revision,
            files_at_commit=files_at_commit,
        )

        def load_blob(path: str) -> bytes:
            result = run_git("cat-file", "blob", f"{revision}:{path}")
            if result.returncode != 0:
                raise AuthorityRefreshError("path is absent from the source revision")
            return result.stdout

        _validate_source_revision_blobs(node, load_blob, report)
    except AuthorityRefreshError as exc:
        report.error(f"{node['label']}: source revision verification failed: {exc}")


def _validate_release_chains(
    root: Path,
    parsed: dict[Path, Any],
    report: ValidationReport,
) -> None:
    """Require immutable discovery releases to form one snapshot-hash chain."""

    release_root = root / "authority" / "releases"
    if not release_root.is_dir():
        report.error("authority/releases: required release directory is missing")
        return
    nodes_by_domain: dict[str, list[dict[str, Any]]] = {
        "legal": [],
        "accounting": [],
    }
    for directory in sorted(
        (path for path in release_root.iterdir() if path.is_dir()),
        key=lambda path: path.name,
    ):
        label = _relative_label(root, directory)
        report.require(
            not directory.is_symlink(),
            f"{label}: release directory must not be a symlink",
        )
        expected_filenames = IMMUTABLE_RELEASE_FILENAMES
        entries = list(directory.iterdir())
        actual_filenames = {entry.name for entry in entries}
        report.require(
            actual_filenames == expected_filenames,
            f"{label}: immutable release file set must be exactly "
            f"{sorted(expected_filenames)}; actual={sorted(actual_filenames)}",
        )
        for filename in sorted(expected_filenames):
            path = directory / filename
            report.require(
                path.is_file() and not path.is_symlink(),
                f"{label}/{filename}: immutable release document must be a regular file",
            )
        documents: dict[str, dict[str, Any]] = {}
        for filename in sorted(expected_filenames):
            value = parsed.get(directory / filename)
            report.require(
                isinstance(value, dict),
                f"{label}/{filename}: immutable release document is missing or invalid",
            )
            if isinstance(value, dict):
                documents[filename] = value
        if len(documents) != 4:
            continue

        candidate = documents["candidate.json"]
        approval = documents["approval.json"]
        validation_context = documents["validation-context.json"]
        release = documents["release.json"]
        domain = candidate.get("domain")
        report.require(
            domain in nodes_by_domain,
            f"{label}: candidate domain must be legal or accounting",
        )
        if domain not in nodes_by_domain:
            continue
        report.require(
            release.get("domain") == domain and approval.get("domain") == domain,
            f"{label}: candidate, approval, and release domains must match",
        )
        report.require(
            candidate.get("schema_version") == "1.0"
            and approval.get("schema_version") == "1.0"
            and release.get("schema_version") == "1.0",
            f"{label}: immutable release documents must use schema_version 1.0",
        )
        expected_release_fields = {
            "schema_version",
            "release_id",
            "domain",
            "candidate_sha256",
            "candidate_generated_at",
            "approved_at",
            "approval",
            "validation_context_sha256",
            "notice",
        }
        report.require(
            set(release) == expected_release_fields,
            f"{label}: release fields must be exactly "
            f"{sorted(expected_release_fields)}; actual={sorted(release)}",
        )
        report.require(
            release.get("notice") == promotion.RELEASE_NOTICE,
            f"{label}: release notice must preserve the non-certification disclaimer",
        )

        candidate_body = dict(candidate)
        claimed_digest = candidate_body.pop("candidate_sha256", None)
        actual_digest = sha256_json(candidate_body)
        report.require(
            claimed_digest == actual_digest,
            f"{label}: archived candidate hash is invalid",
        )
        report.require(
            approval.get("candidate_sha256") == actual_digest
            and release.get("candidate_sha256") == actual_digest,
            f"{label}: approval/release candidate hash does not match the archive",
        )
        report.require(
            release.get("approval") == approval,
            f"{label}: release approval does not equal approval.json",
        )
        report.require(
            release.get("validation_context_sha256")
            == sha256_json(validation_context),
            f"{label}: release validation-context hash does not match "
            "validation-context.json",
        )
        report.require(
            release.get("candidate_generated_at") == candidate.get("generated_at"),
            f"{label}: release candidate_generated_at does not match candidate.json",
        )
        approved_at = _parse_iso_date(
            release.get("approved_at"), f"{label} release.approved_at", report
        )
        if approved_at is None:
            continue
        report.require(
            approved_at <= date.today(),
            f"{label}: release.approved_at cannot be in the future",
        )
        expected_release_id = f"{approved_at.isoformat()}-{domain}-{actual_digest[:12]}"
        report.require(
            directory.name == expected_release_id
            and release.get("release_id") == expected_release_id,
            f"{label}: directory and release_id must be {expected_release_id}",
        )
        items = candidate.get("items")
        report.require(
            isinstance(items, list), f"{label}: candidate.items must be a list"
        )
        baseline = candidate.get("approved_baseline")
        report.require(
            isinstance(baseline, dict),
            f"{label}: candidate.approved_baseline must be an object",
        )
        if not isinstance(items, list) or not isinstance(baseline, dict):
            continue
        report.require(
            baseline.get("path") == f"authority/snapshots/{domain}.json",
            f"{label}: approved baseline path does not match its domain snapshot",
        )
        expected_snapshot = {
            "schema_version": "1.0",
            "domain": domain,
            "release_id": expected_release_id,
            "approved_at": approved_at.isoformat(),
            "candidate_sha256": actual_digest,
            "items": items,
        }
        nodes_by_domain[domain].append(
            {
                "release_id": expected_release_id,
                "approved_at": approved_at,
                "baseline": baseline,
                "snapshot": expected_snapshot,
                "snapshot_sha256": sha256_json(expected_snapshot),
                "candidate": candidate,
                "approval": approval,
                "validation_context": validation_context,
                "label": label,
            }
        )

    for domain, nodes in nodes_by_domain.items():
        snapshot_path = root / "authority" / "snapshots" / f"{domain}.json"
        if not nodes:
            report.require(
                not snapshot_path.exists(),
                f"authority/snapshots/{domain}.json: snapshot exists without an "
                "immutable release chain",
            )
            continue

        by_snapshot_hash: dict[str, dict[str, Any]] = {}
        duplicate_hashes: set[str] = set()
        for node in nodes:
            digest = node["snapshot_sha256"]
            if digest in by_snapshot_hash:
                duplicate_hashes.add(digest)
            by_snapshot_hash[digest] = node
        report.require(
            not duplicate_hashes,
            f"authority/releases: {domain} chain has duplicate snapshot hashes",
        )

        roots: list[dict[str, Any]] = []
        children: dict[str, list[dict[str, Any]]] = {}
        for node in nodes:
            baseline = node["baseline"]
            missing = baseline.get("missing")
            predecessor = baseline.get("sha256")
            if missing is True:
                report.require(
                    predecessor is None,
                    f"authority/releases/{node['release_id']}: missing baseline "
                    "must have null sha256",
                )
                roots.append(node)
                continue
            report.require(
                missing is False
                and isinstance(predecessor, str)
                and bool(re.fullmatch(r"[0-9a-f]{64}", predecessor)),
                f"authority/releases/{node['release_id']}: existing baseline "
                "requires lowercase SHA-256",
            )
            if not isinstance(predecessor, str):
                continue
            report.require(
                predecessor in by_snapshot_hash,
                f"authority/releases/{node['release_id']}: predecessor snapshot "
                "is not archived",
            )
            parent = by_snapshot_hash.get(predecessor)
            if parent is not None:
                report.require(
                    parent["approved_at"] <= node["approved_at"],
                    f"authority/releases/{node['release_id']}: approved_at precedes "
                    "its predecessor release",
                )
            children.setdefault(predecessor, []).append(node)

        for node in nodes:
            baseline = node["baseline"]
            historical_baseline: dict[str, Any] | None
            if baseline.get("missing") is True:
                historical_baseline = None
            else:
                predecessor = baseline.get("sha256")
                parent = (
                    by_snapshot_hash.get(predecessor)
                    if isinstance(predecessor, str)
                    else None
                )
                if parent is None:
                    report.error(
                        f"{node['label']}: archived promotion replay cannot reconstruct "
                        "the predecessor snapshot"
                    )
                    continue
                historical_baseline = parent["snapshot"]
            try:
                promotion.validate_archived_release(
                    node["candidate"],
                    node["approval"],
                    node["validation_context"],
                    release_date=node["approved_at"],
                    historical_baseline=historical_baseline,
                    output_root=root,
                )
            except Exception as exc:
                # Repository content is untrusted at this boundary. Any replay
                # failure must become a validation error instead of aborting CI.
                report.error(
                    f"{node['label']}: archived promotion replay failed: {exc}"
                )
            else:
                _validate_source_revision(root, node, report)

        report.require(
            len(roots) == 1,
            f"authority/releases: {domain} chain must have exactly one missing-baseline root",
        )
        forked = [digest for digest, values in children.items() if len(values) > 1]
        report.require(
            not forked,
            f"authority/releases: {domain} chain forks from {sorted(forked)}",
        )
        predecessor_hashes = set(children)
        tips = [node for node in nodes if node["snapshot_sha256"] not in predecessor_hashes]
        report.require(
            len(tips) == 1,
            f"authority/releases: {domain} chain must have one unique tip",
        )

        if len(roots) == 1 and not forked:
            visited: set[str] = set()
            current = roots[0]
            while current["snapshot_sha256"] not in visited:
                visited.add(current["snapshot_sha256"])
                next_nodes = children.get(current["snapshot_sha256"], [])
                if len(next_nodes) != 1:
                    break
                current = next_nodes[0]
            report.require(
                len(visited) == len(nodes),
                f"authority/releases: {domain} releases are disconnected or cyclic",
            )

        snapshot = parsed.get(snapshot_path)
        report.require(
            isinstance(snapshot, dict),
            f"authority/snapshots/{domain}.json: unique chain-tip snapshot is missing or invalid",
        )
        if isinstance(snapshot, dict) and len(tips) == 1:
            report.require(
                snapshot == tips[0]["snapshot"],
                f"authority/snapshots/{domain}.json: snapshot does not equal the unique release-chain tip",
            )


def _codeowners_pattern_matches(pattern: str, target: str) -> bool:
    normalized = pattern.lstrip("/")
    if normalized.endswith("/"):
        return target.startswith(normalized)
    return fnmatch.fnmatchcase(target, normalized)


def _validate_codeowners(root: Path, report: ValidationReport) -> None:
    path = root / ".github" / "CODEOWNERS"
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        report.error(f".github/CODEOWNERS: cannot read: {exc}")
        return
    entries: list[tuple[str, list[str]]] = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        fields = stripped.split()
        if len(fields) >= 2:
            entries.append((fields[0], fields[1:]))
    targets = (
        "legal/CURRENT_STATUS.json",
        "accounting/CURRENT_STATUS.json",
        "authority/impact_crosswalk.json",
        "tools/authority_refresh/promotion.py",
        "tools/authority_refresh/config/legal_sources.json",
        "tools/authority_refresh/config/accounting_sources.json",
        ".github/workflows/legal-source-monitor.yml",
        ".github/workflows/accounting-authority-review.yml",
        ".github/workflows/authority-discovery.yml",
    )
    for target in targets:
        matching = [owners for pattern, owners in entries if _codeowners_pattern_matches(pattern, target)]
        report.require(
            bool(matching) and bool(matching[-1]),
            f".github/CODEOWNERS: no owner covers {target}",
        )
        if matching:
            report.require(
                all(owner.startswith("@") for owner in matching[-1]),
                f".github/CODEOWNERS: owners for {target} must be GitHub users or teams",
            )


def _validate_gitattributes(root: Path, report: ValidationReport) -> None:
    path = root / ".gitattributes"
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        report.error(f".gitattributes: cannot read: {exc}")
        return
    entries: dict[str, list[str]] = {}
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        fields = stripped.split()
        if len(fields) >= 2:
            entries[fields[0].casefold()] = [field.casefold() for field in fields[1:]]
    for pattern in ("*.pdf", "*.zip", "*.xlsx", "*.docx"):
        attributes = entries.get(pattern, [])
        report.require(
            "binary" in attributes or "-text" in attributes,
            f".gitattributes: {pattern} must be marked binary/-text",
        )


def _require_workflow_fragments(
    label: str, content: str, fragments: Iterable[str], report: ValidationReport
) -> None:
    folded = content.casefold()
    for fragment in fragments:
        report.require(
            fragment.casefold() in folded,
            f"{label}: missing safety contract marker {fragment!r}",
        )


def _validate_workflows(root: Path, report: ValidationReport) -> None:
    contents: dict[str, str] = {}
    for name, relative in EXPECTED_WORKFLOWS.items():
        path = root / relative
        try:
            contents[name] = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            report.error(f"{relative.as_posix()}: cannot read expected workflow: {exc}")

    checks = contents.get("checks")
    if checks is not None:
        _require_workflow_fragments(
            EXPECTED_WORKFLOWS["checks"].as_posix(),
            checks,
            (
                "validate_system.py",
                "unittest",
                "tools/authority_refresh/tests",
                "fetch-depth: 0",
            ),
            report,
        )
    discovery = contents.get("discovery")
    if discovery is not None:
        _require_workflow_fragments(
            EXPECTED_WORKFLOWS["discovery"].as_posix(),
            discovery,
            (
                "schedule:",
                "workflow_dispatch:",
                "authority/candidates",
                "pull-requests: write",
                "contents: write",
                "gh pr create",
            ),
            report,
        )
    promotion = contents.get("promotion")
    if promotion is not None:
        _require_workflow_fragments(
            EXPECTED_WORKFLOWS["promotion"].as_posix(),
            promotion,
            (
                "environment: authority-production",
                "promote_reviewed_authority_release",
                "promotion.py",
                "authority/candidates",
                "authority/reviews",
                "gh pr create",
            ),
            report,
        )

    for name in ("discovery", "promotion"):
        content = contents.get(name)
        if content is None:
            continue
        folded = content.casefold()
        label = EXPECTED_WORKFLOWS[name].as_posix()
        for prohibited in ("gh pr merge", "enable-auto-merge", "--auto"):
            report.require(
                prohibited not in folded,
                f"{label}: automatic or direct pull-request merge is prohibited",
            )


def validate_repository(root: Path) -> ValidationReport:
    """Run every offline authority-system invariant against ``root``."""

    report = ValidationReport()
    root = root.resolve()
    report.require(root.is_dir(), f"repository root does not exist: {root}")
    if not root.is_dir():
        return report

    parsed = _read_governed_json(root, report)
    _validate_catalogs(root, report)
    legal_status = _validate_status(root, parsed, "legal", report)
    accounting_status = _validate_status(root, parsed, "accounting", report)
    legal_groups = _validate_legal_baseline(root, parsed, legal_status, report)
    fasb_topics = _validate_accounting_baseline(root, parsed, accounting_status, report)
    _validate_crosswalk(root, parsed, fasb_topics, legal_groups, report)
    _validate_release_chains(root, parsed, report)
    _validate_codeowners(root, report)
    _validate_gitattributes(root, report)
    _validate_workflows(root, report)
    return report


def _default_root() -> Path:
    return Path(__file__).resolve().parents[2]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=_default_root(),
        help="repository root (defaults to the root containing this script)",
    )
    args = parser.parse_args(argv)
    report = validate_repository(args.root)
    state = "PASS" if report.ok else "FAIL"
    print(
        f"Authority system validation: {state} "
        f"({report.checks} checks; {report.json_files} JSON files)"
    )
    for error in report.errors:
        print(f"ERROR: {error}")
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main())
