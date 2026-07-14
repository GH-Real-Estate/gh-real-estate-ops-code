#!/usr/bin/env python3
"""Validate and archive a reviewed authority-discovery candidate.

Promotion updates only the reviewed discovery baseline and immutable evidence release.
Approved legal text, accounting conclusions, and CURRENT_STATUS records remain separate
reviewed changes in separate pull requests.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import parse_qsl, unquote, urlsplit


PACKAGE_DIR = Path(__file__).resolve().parent
REPO_ROOT = PACKAGE_DIR.parents[1]
if str(PACKAGE_DIR) not in sys.path:
    sys.path.insert(0, str(PACKAGE_DIR))

try:  # package import in tests and modules
    from .core import (
        DEFAULT_MAXIMUM_ITEMS,
        MAXIMUM_ITEMS_PER_DOMAIN,
        MAX_CANDIDATE_JSON_BYTES,
        SCHEMA_VERSION,
        AuthorityRefreshError,
        build_candidate,
        load_catalog,
        load_impact_crosswalk,
        normalize_item,
        sha256_json,
        source_minimum_items,
        validate_catalog,
        validate_complete_index_baseline_coverage,
        validate_impact_crosswalk,
        validate_official_url,
        write_json_atomic,
    )
except ImportError:  # direct `python tools/authority_refresh/promotion.py`
    from core import (  # type: ignore[no-redef]
        DEFAULT_MAXIMUM_ITEMS,
        MAXIMUM_ITEMS_PER_DOMAIN,
        MAX_CANDIDATE_JSON_BYTES,
        SCHEMA_VERSION,
        AuthorityRefreshError,
        build_candidate,
        load_catalog,
        load_impact_crosswalk,
        normalize_item,
        sha256_json,
        source_minimum_items,
        validate_catalog,
        validate_complete_index_baseline_coverage,
        validate_impact_crosswalk,
        validate_official_url,
        write_json_atomic,
    )


CONFIRMATION = "PROMOTE_REVIEWED_AUTHORITY_RELEASE"
VALIDATION_CONTRACT_VERSION = "1.0"
RELEASE_NOTICE = (
    "Reviewed discovery baseline only. Official source text controls. "
    "This release is not a legal or GAAP compliance certification."
)
MAX_CANDIDATE_AGE = timedelta(days=7)
BASE_REQUIRED_ROLE = {
    "legal": "qualified-legal-reviewer",
    "accounting": "cpa-or-qualified-accounting-reviewer",
}
ALLOWED_CANDIDATE_STATUSES = {"current", "review_required", "degraded"}
ALLOWED_REVIEWER_ROLES = {
    "kansas-counsel",
    "qualified-legal-reviewer",
    "cpa-or-qualified-accounting-reviewer",
    "tax-professional",
    "finance-operator",
    "system-owner",
    "records-and-licensing-reviewer",
}
ALLOWED_RESOLUTIONS = {
    "no_material_change",
    "not_applicable",
    "superseded",
    "approved_release_updated",
}
ALLOWED_IMPACT_DETERMINATIONS = {
    "no_change_required",
    "not_applicable",
    "approved_paths_updated",
}
SENSITIVE_EVIDENCE_QUERY_KEYS = {
    "access_token",
    "api_key",
    "apikey",
    "auth_token",
    "authorization",
    "credential",
    "key",
    "password",
    "secret",
    "sig",
    "signature",
    "token",
}
SENSITIVE_EVIDENCE_QUERY_PREFIXES = ("x-amz-", "x-goog-")
SENSITIVE_EVIDENCE_FRAGMENT = re.compile(
    r"(?:access[_-]?token|api[_-]?key|auth(?:orization)?|password|secret|sig(?:nature)?|token)\s*=",
    re.IGNORECASE,
)

CANDIDATE_FIELDS = {
    "schema_version",
    "domain",
    "generated_at",
    "run_id",
    "status",
    "notice",
    "approved_baseline",
    "counts",
    "source_results",
    "changes",
    "potential_impacts",
    "items",
    "candidate_sha256",
}
COUNT_FIELDS = {
    "sources",
    "healthy_sources",
    "items",
    "new",
    "modified",
    "missing_items",
    "source_errors",
    "configuration_required",
    "potential_impacts",
}
SOURCE_RESULT_BASE_FIELDS = {
    "source_id",
    "critical",
    "storage_policy",
    "discovery_url",
    "retrieved_at",
    "missing_detection",
    "status",
    "item_count",
    "observed_item_ids",
}
SOURCE_RESULT_HEALTHY_FIELDS = SOURCE_RESULT_BASE_FIELDS | {
    "final_url",
    "content_type",
    "payload_sha256",
    "attempts",
}
SOURCE_RESULT_UNAVAILABLE_FIELDS = SOURCE_RESULT_BASE_FIELDS | {"error"}
ITEM_FIELDS = {
    "item_id",
    "source_id",
    "external_id",
    "title",
    "official_url",
    "publisher",
    "jurisdiction",
    "authority_type",
    "storage_policy",
    "published_at",
    "effective_at",
    "status",
    "metadata",
    "fingerprint",
}
APPROVAL_FIELDS = {
    "schema_version",
    "domain",
    "candidate_sha256",
    "approvals",
    "change_resolutions",
    "impact_resolutions",
}
VALIDATION_CONTEXT_FIELDS = {
    "contract_version",
    "domain",
    "candidate_sha256",
    "source_revision",
    "candidate_path",
    "approval_path",
    "source_catalog_path",
    "impact_crosswalk_path",
    "source_catalog",
    "impact_crosswalk",
    "path_manifest",
}
PATH_MANIFEST_FIELDS = {"path", "sha256", "size_bytes"}
_USE_CURRENT_BASELINE = object()


def _load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AuthorityRefreshError(f"cannot load {label} {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise AuthorityRefreshError(f"{label} must be a JSON object")
    return value


def _require_exact_keys(
    value: object,
    required: set[str],
    *,
    optional: set[str] | None = None,
    label: str,
) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise AuthorityRefreshError(f"{label} must be an object")
    optional = optional or set()
    missing = sorted(required.difference(value))
    extra = sorted(set(value).difference(required | optional))
    if missing or extra:
        raise AuthorityRefreshError(
            f"{label} fields do not match the contract; missing={missing}, extra={extra}"
        )
    return value


def _require_list(value: object, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise AuthorityRefreshError(f"{label} must be a list")
    return value


def _require_nonnegative_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise AuthorityRefreshError(f"{label} must be a non-negative integer")
    return value


def _require_nonempty_string(value: object, label: str, *, max_length: int) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > max_length:
        raise AuthorityRefreshError(
            f"{label} must be a nonempty string no longer than {max_length} characters"
        )
    return value


def candidate_digest(candidate: dict[str, Any]) -> str:
    value = dict(candidate)
    claimed = value.pop("candidate_sha256", None)
    actual = sha256_json(value)
    if claimed != actual:
        raise AuthorityRefreshError(
            f"candidate hash mismatch: expected {claimed}, calculated {actual}"
        )
    return actual


def _parse_timestamp(value: object, field: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError as exc:
        raise AuthorityRefreshError(f"invalid {field}: {value}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise AuthorityRefreshError(f"{field} must include a UTC offset")
    return parsed


def _validate_latest_candidate(
    candidate: dict[str, Any],
    *,
    output_root: Path,
    now: datetime | None = None,
) -> None:
    """Require promotion to use the merged, recent tip of discovery evidence."""

    domain = str(candidate.get("domain", ""))
    latest_path = (
        output_root / "authority" / "candidates" / domain / "latest" / "candidate.json"
    )
    if latest_path.is_symlink() or not latest_path.is_file():
        raise AuthorityRefreshError(
            f"latest merged {domain} candidate is missing or unsafe: {latest_path}"
        )
    latest = _load_json(latest_path, "latest candidate")
    if latest != candidate:
        raise AuthorityRefreshError(
            "selected candidate is not the latest merged candidate; reconcile discovery first"
        )
    generated_at = _parse_timestamp(candidate.get("generated_at"), "candidate.generated_at")
    current_time = now or datetime.now(timezone.utc)
    if current_time.tzinfo is None or current_time.utcoffset() is None:
        raise AuthorityRefreshError("promotion current time must include a UTC offset")
    if current_time - generated_at > MAX_CANDIDATE_AGE:
        raise AuthorityRefreshError(
            f"latest merged candidate is older than {MAX_CANDIDATE_AGE.days} days; "
            "run and reconcile discovery again"
        )


def _parse_date(value: object, field: str) -> date:
    try:
        return date.fromisoformat(str(value))
    except ValueError as exc:
        raise AuthorityRefreshError(f"invalid {field}: {value}") from exc


def _validate_evidence_urls(value: object, label: str) -> None:
    if not isinstance(value, list) or not value:
        raise AuthorityRefreshError(f"{label} requires HTTPS evidence URLs")
    seen: set[str] = set()
    for raw_url in value:
        if not isinstance(raw_url, str) or raw_url in seen:
            raise AuthorityRefreshError(f"{label} requires unique HTTPS evidence URLs")
        if len(raw_url) > 2_048 or any(character.isspace() for character in raw_url):
            raise AuthorityRefreshError(f"{label} has an unsafe evidence URL")
        seen.add(raw_url)
        try:
            parsed = urlsplit(str(raw_url))
            port = parsed.port
        except ValueError as exc:
            raise AuthorityRefreshError(f"{label} has an invalid evidence URL") from exc
        if (
            parsed.scheme != "https"
            or not parsed.hostname
            or parsed.username is not None
            or parsed.password is not None
            or port not in (None, 443)
        ):
            raise AuthorityRefreshError(f"{label} requires HTTPS evidence URLs")
        query_keys = {name.lower() for name, _ in parse_qsl(parsed.query, keep_blank_values=True)}
        if any(
            key in SENSITIVE_EVIDENCE_QUERY_KEYS
            or key.startswith(SENSITIVE_EVIDENCE_QUERY_PREFIXES)
            for key in query_keys
        ) or SENSITIVE_EVIDENCE_FRAGMENT.search(unquote(parsed.fragment)):
            raise AuthorityRefreshError(
                f"{label} evidence URLs must not contain credentials or signed tokens"
            )


def _normalized_repo_path(raw_path: object, label: str) -> tuple[str, PurePosixPath]:
    value = str(raw_path)
    pure = PurePosixPath(value)
    if "\\" in value or pure.is_absolute() or ".." in pure.parts:
        raise AuthorityRefreshError(f"{label} must be a repository-relative POSIX path")
    normalized = pure.as_posix()
    if normalized in {"", "."}:
        raise AuthorityRefreshError(f"{label} must not be empty")
    return normalized, pure


def _repo_relative_path(
    raw_path: object,
    label: str,
    *,
    repo_root: Path = REPO_ROOT,
) -> tuple[str, Path]:
    normalized, pure = _normalized_repo_path(raw_path, label)
    resolved_root = repo_root.resolve()
    resolved = (resolved_root / Path(*pure.parts)).resolve()
    try:
        resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise AuthorityRefreshError(f"{label} escapes the repository") from exc
    return normalized, resolved


def _validate_source_results(
    candidate: dict[str, Any],
    sources: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    results = _require_list(candidate.get("source_results"), "candidate.source_results")
    expected_ids = [str(source["source_id"]) for source in sources]
    actual_ids: list[str] = []
    by_id: dict[str, dict[str, Any]] = {}
    source_by_id = {str(source["source_id"]): source for source in sources}
    for index, raw_result in enumerate(results):
        label = f"candidate.source_results[{index}]"
        if not isinstance(raw_result, dict):
            raise AuthorityRefreshError(f"{label} must be an object")
        source_id = str(raw_result.get("source_id", ""))
        if source_id not in source_by_id or source_id in by_id:
            raise AuthorityRefreshError(f"{label} has an unknown or duplicate source_id")
        source = source_by_id[source_id]
        status = raw_result.get("status")
        fields = (
            SOURCE_RESULT_HEALTHY_FIELDS
            if status == "healthy"
            else SOURCE_RESULT_UNAVAILABLE_FIELDS
        )
        result = _require_exact_keys(raw_result, fields, label=label)
        if not isinstance(result.get("critical"), bool):
            raise AuthorityRefreshError(f"{label}.critical must be boolean")
        actual_ids.append(source_id)
        by_id[source_id] = result

        static_values = {
            "critical": bool(source["critical"]),
            "storage_policy": source["storage_policy"],
            "discovery_url": source["discovery_url"],
            "retrieved_at": candidate["generated_at"],
            "missing_detection": source.get("missing_detection", "complete-index"),
        }
        for field, expected in static_values.items():
            if result.get(field) != expected:
                raise AuthorityRefreshError(
                    f"{label}.{field} does not match the canonical source catalog"
                )
        item_count = _require_nonnegative_int(result.get("item_count"), f"{label}.item_count")
        observed_item_ids = _require_list(
            result.get("observed_item_ids"), f"{label}.observed_item_ids"
        )
        if (
            any(not isinstance(item_id, str) or not item_id for item_id in observed_item_ids)
            or observed_item_ids != sorted(set(observed_item_ids))
        ):
            raise AuthorityRefreshError(
                f"{label}.observed_item_ids must be sorted unique nonempty strings"
            )
        if item_count != len(observed_item_ids):
            raise AuthorityRefreshError(
                f"{label}.item_count must equal len(observed_item_ids)"
            )
        if status == "healthy":
            validate_official_url(
                str(result.get("final_url", "")),
                source["allowed_hosts"],
                allow_http=bool(source.get("allow_http", False)),
            )
            _require_nonempty_string(
                result.get("content_type"), f"{label}.content_type", max_length=500
            )
            if not re.fullmatch(r"[0-9a-f]{64}", str(result.get("payload_sha256", ""))):
                raise AuthorityRefreshError(f"{label}.payload_sha256 must be lowercase SHA-256")
            attempts = _require_nonnegative_int(result.get("attempts"), f"{label}.attempts")
            maximum_attempts = int((source.get("request") or {}).get("attempts", 3))
            if attempts < 1 or attempts > maximum_attempts:
                raise AuthorityRefreshError(
                    f"{label}.attempts must be between 1 and {maximum_attempts}"
                )
            minimum_items = source_minimum_items(source)
            if item_count < minimum_items:
                raise AuthorityRefreshError(
                    f"{label}.item_count is below canonical minimum_items={minimum_items}"
                )
            maximum_items = int(source.get("maximum_items", DEFAULT_MAXIMUM_ITEMS))
            if item_count > maximum_items:
                raise AuthorityRefreshError(
                    f"{label}.item_count exceeds canonical maximum_items={maximum_items}"
                )
        elif status in {"error", "configuration_required"}:
            if item_count != 0 or observed_item_ids:
                raise AuthorityRefreshError(
                    f"{label} must have zero items when unavailable"
                )
            error = _require_nonempty_string(
                result.get("error"), f"{label}.error", max_length=10_000
            )
            if status == "configuration_required":
                request = source.get("request") or {}
                environment = str(request.get("api_key_env", ""))
                expected_error = f"required environment variable is unavailable: {environment}"
                if (
                    not request.get("api_key_required")
                    or not environment
                    or error != expected_error
                ):
                    raise AuthorityRefreshError(
                        f"{label} cannot claim configuration_required for this source"
                    )
        else:
            raise AuthorityRefreshError(f"{label} has unsupported status: {status}")

    if actual_ids != expected_ids:
        raise AuthorityRefreshError(
            "candidate source coverage/order does not match the canonical catalog; "
            f"expected={expected_ids}, actual={actual_ids}"
        )
    return by_id


def _validate_items(
    value: object,
    *,
    domain: str,
    source_by_id: dict[str, dict[str, Any]],
    label: str,
) -> list[dict[str, Any]]:
    items = _require_list(value, label)
    if len(items) > MAXIMUM_ITEMS_PER_DOMAIN:
        raise AuthorityRefreshError(
            f"{label} exceeds the {MAXIMUM_ITEMS_PER_DOMAIN}-item domain limit"
        )
    normalized_items: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, raw_item in enumerate(items):
        item_label = f"{label}[{index}]"
        item = _require_exact_keys(raw_item, ITEM_FIELDS, label=item_label)
        item_id = _require_nonempty_string(
            item.get("item_id"), f"{item_label}.item_id", max_length=200
        )
        if item_id in seen:
            raise AuthorityRefreshError(f"{label} contains duplicate item_id: {item_id}")
        seen.add(item_id)
        source_id = str(item.get("source_id", ""))
        source = source_by_id.get(source_id)
        if source is None:
            raise AuthorityRefreshError(f"{item_label} references unknown source: {source_id}")
        if not isinstance(item.get("metadata"), dict):
            raise AuthorityRefreshError(f"{item_label}.metadata must be an object")
        raw = {
            "external_id": item.get("external_id"),
            "title": item.get("title"),
            "official_url": item.get("official_url"),
            "published_at": item.get("published_at"),
            "effective_at": item.get("effective_at"),
            "status": item.get("status"),
            "metadata": item.get("metadata"),
        }
        try:
            normalized = normalize_item(raw, source, domain=domain)
        except AuthorityRefreshError as exc:
            raise AuthorityRefreshError(f"{item_label} is not normalized: {exc}") from exc
        if normalized != item:
            raise AuthorityRefreshError(
                f"{item_label} does not match its canonical normalized value/fingerprint"
            )
        normalized_items.append(normalized)
    if [item["item_id"] for item in normalized_items] != sorted(seen):
        raise AuthorityRefreshError(f"{label} must be sorted by unique item_id")
    return normalized_items


def _validate_candidate(
    candidate: dict[str, Any],
    *,
    output_root: Path,
    source_catalog: dict[str, Any] | None = None,
    impact_crosswalk: dict[str, Any] | None = None,
    historical_baseline: object = _USE_CURRENT_BASELINE,
) -> tuple[str, datetime]:
    if (
        len((json.dumps(candidate, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
        > MAX_CANDIDATE_JSON_BYTES
    ):
        raise AuthorityRefreshError(
            f"candidate JSON exceeds the {MAX_CANDIDATE_JSON_BYTES}-byte limit"
        )
    _require_exact_keys(candidate, CANDIDATE_FIELDS, label="candidate")
    if candidate.get("schema_version") != SCHEMA_VERSION:
        raise AuthorityRefreshError(
            f"candidate.schema_version must be {SCHEMA_VERSION}"
        )
    domain = str(candidate.get("domain", ""))
    if domain not in BASE_REQUIRED_ROLE:
        raise AuthorityRefreshError(f"unsupported candidate domain: {domain}")
    generated_at = _parse_timestamp(candidate.get("generated_at"), "candidate.generated_at")
    if generated_at > datetime.now(timezone.utc):
        raise AuthorityRefreshError("candidate.generated_at cannot be in the future")
    _require_nonempty_string(candidate.get("run_id"), "candidate.run_id", max_length=200)
    _require_nonempty_string(candidate.get("notice"), "candidate.notice", max_length=5_000)
    status = candidate.get("status")
    if status not in ALLOWED_CANDIDATE_STATUSES:
        raise AuthorityRefreshError(f"unsupported candidate status: {status}")
    digest = candidate_digest(candidate)
    baseline_descriptor, baseline = _load_candidate_baseline(
        candidate,
        output_root=output_root,
        historical_baseline=historical_baseline,
    )

    catalog = (
        load_catalog(
            output_root
            / "tools"
            / "authority_refresh"
            / "config"
            / f"{domain}_sources.json",
            domain=domain,
        )
        if source_catalog is None
        else validate_catalog(
            source_catalog,
            domain=domain,
            label="archived source catalog",
        )
    )
    sources = catalog["sources"]
    source_by_id = {str(source["source_id"]): source for source in sources}
    results_by_id = _validate_source_results(candidate, sources)

    if baseline.get("domain") != domain:
        raise AuthorityRefreshError("approved baseline has the wrong domain")
    if not baseline_descriptor["missing"]:
        baseline_approved_at = _parse_date(
            baseline.get("approved_at"), "approved baseline.approved_at"
        )
        if baseline_approved_at > generated_at.astimezone(timezone.utc).date():
            raise AuthorityRefreshError(
                "candidate.generated_at cannot precede the approved baseline"
            )
    baseline_items = _validate_items(
        baseline.get("items"),
        domain=domain,
        source_by_id=source_by_id,
        label="approved baseline.items",
    )
    candidate_items = _validate_items(
        candidate.get("items"),
        domain=domain,
        source_by_id=source_by_id,
        label="candidate.items",
    )

    crosswalk = (
        load_impact_crosswalk(
            output_root / "authority" / "impact_crosswalk.json"
        )
        if impact_crosswalk is None
        else validate_impact_crosswalk(
            impact_crosswalk,
            label="archived impact crosswalk",
        )
    )
    candidate_by_id = {item["item_id"]: item for item in candidate_items}
    observed_items: list[dict[str, Any]] = []
    observed_ids: set[str] = set()
    for source_id, result in results_by_id.items():
        for item_id in result["observed_item_ids"]:
            item = candidate_by_id.get(item_id)
            if item is None or item["source_id"] != source_id or item_id in observed_ids:
                raise AuthorityRefreshError(
                    f"source {source_id} declares an invalid observed item: {item_id}"
                )
            observed_ids.add(item_id)
            observed_items.append(item)

    for source_id, result in results_by_id.items():
        if result["status"] != "healthy":
            continue
        validate_complete_index_baseline_coverage(
            source_by_id[source_id],
            baseline_items,
            observed_items,
        )

    canonical_candidate = build_candidate(
        domain=domain,
        generated_at=candidate["generated_at"],
        run_id=candidate["run_id"],
        baseline_path=Path(str(baseline_descriptor["path"])),
        baseline=baseline,
        baseline_missing=bool(baseline_descriptor["missing"]),
        source_results=candidate["source_results"],
        items=observed_items,
        impact_crosswalk=crosswalk,
    )
    counts = _require_exact_keys(candidate.get("counts"), COUNT_FIELDS, label="candidate.counts")
    for field, value in counts.items():
        _require_nonnegative_int(value, f"candidate.counts.{field}")
    for field in sorted(CANDIDATE_FIELDS):
        if candidate[field] != canonical_candidate[field]:
            raise AuthorityRefreshError(
                f"candidate.{field} does not match the canonical reconstruction"
            )
    return digest, generated_at


def _required_roles(candidate: dict[str, Any]) -> set[str]:
    domain = str(candidate.get("domain", ""))
    roles = {BASE_REQUIRED_ROLE[domain]}
    for impact in candidate["potential_impacts"]:
        review_gate = impact.get("review_gate")
        if not isinstance(review_gate, dict):
            raise AuthorityRefreshError(
                f"canonical impact {impact.get('mapping_id')} lacks a review gate"
            )
        required = review_gate.get("required_roles")
        if not isinstance(required, list) or not required:
            raise AuthorityRefreshError(
                f"canonical impact {impact.get('mapping_id')} lacks required roles"
            )
        roles.update(str(role) for role in required)
    unsupported = roles.difference(ALLOWED_REVIEWER_ROLES)
    if unsupported:
        raise AuthorityRefreshError(
            "canonical impact crosswalk has unsupported reviewer roles: "
            + ", ".join(sorted(unsupported))
        )
    return roles


def validate_approval(
    candidate: dict[str, Any],
    approval: dict[str, Any],
    *,
    output_root: Path = REPO_ROOT,
    source_catalog: dict[str, Any] | None = None,
    impact_crosswalk: dict[str, Any] | None = None,
    historical_baseline: object = _USE_CURRENT_BASELINE,
    require_existing_paths: bool = True,
) -> str:
    digest, generated_at = _validate_candidate(
        candidate,
        output_root=output_root,
        source_catalog=source_catalog,
        impact_crosswalk=impact_crosswalk,
        historical_baseline=historical_baseline,
    )
    domain = str(candidate["domain"])
    status = candidate.get("status")
    if status == "degraded":
        raise AuthorityRefreshError("a degraded candidate cannot be promoted")
    _require_exact_keys(approval, APPROVAL_FIELDS, label="approval")
    if approval.get("schema_version") != SCHEMA_VERSION:
        raise AuthorityRefreshError(f"approval.schema_version must be {SCHEMA_VERSION}")
    if approval.get("candidate_sha256") != digest:
        raise AuthorityRefreshError("approval does not target this candidate hash")
    if approval.get("domain") != domain:
        raise AuthorityRefreshError("approval domain does not match candidate")

    approvals = _require_list(approval.get("approvals"), "approval.approvals")
    if not approvals:
        raise AuthorityRefreshError("at least one structured approval is required")
    required_roles = _required_roles(candidate)
    approved_roles: set[str] = set()
    rejected_roles: set[str] = set()
    for index, raw_record in enumerate(approvals):
        record = _require_exact_keys(
            raw_record,
            {"role", "reviewer", "reviewed_at", "determination", "evidence_urls"},
            optional={"notes"},
            label=f"approval.approvals[{index}]",
        )
        if not isinstance(record.get("reviewer"), str):
            raise AuthorityRefreshError("reviewer login must be a string")
        reviewer = record["reviewer"]
        if not re.fullmatch(r"@?[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?", reviewer):
            raise AuthorityRefreshError(f"invalid reviewer login: {reviewer}")
        reviewed_at = _parse_timestamp(record.get("reviewed_at"), "reviewed_at")
        if reviewed_at < generated_at:
            raise AuthorityRefreshError("reviewed_at cannot precede candidate.generated_at")
        if reviewed_at > datetime.now(timezone.utc):
            raise AuthorityRefreshError("reviewed_at cannot be in the future")
        _validate_evidence_urls(
            record.get("evidence_urls"), "each approval"
        )
        if "notes" in record and not isinstance(record["notes"], str):
            raise AuthorityRefreshError("approval notes must be a string")
        role = str(record.get("role", ""))
        determination = record.get("determination")
        if role not in ALLOWED_REVIEWER_ROLES:
            raise AuthorityRefreshError(f"unsupported reviewer role: {role}")
        if determination not in {"approved", "rejected"}:
            raise AuthorityRefreshError(
                f"unsupported reviewer determination: {determination}"
            )
        if role in required_roles:
            if determination == "approved":
                approved_roles.add(role)
            elif determination == "rejected":
                rejected_roles.add(role)
    if rejected_roles:
        raise AuthorityRefreshError(
            "required reviewer rejected the candidate: "
            + ", ".join(sorted(rejected_roles))
        )
    missing_roles = required_roles.difference(approved_roles)
    if missing_roles:
        raise AuthorityRefreshError(
            "missing approved reviewer determination: "
            + ", ".join(sorted(missing_roles))
        )

    changes = candidate["changes"]
    resolutions = _require_list(
        approval.get("change_resolutions"), "approval.change_resolutions"
    )
    by_key: dict[tuple[str, str], dict[str, Any]] = {}
    for index, raw_resolution in enumerate(resolutions):
        resolution = _require_exact_keys(
            raw_resolution,
            {"item_id", "change_type", "resolution", "evidence_urls"},
            optional={"approved_paths", "notes"},
            label=f"approval.change_resolutions[{index}]",
        )
        key = (str(resolution.get("item_id", "")), str(resolution.get("change_type", "")))
        if not all(key) or key in by_key:
            raise AuthorityRefreshError(f"invalid or duplicate change resolution: {key}")
        if key[1] not in {"new", "modified", "missing"}:
            raise AuthorityRefreshError(f"unsupported change type for {key}")
        if resolution.get("resolution") not in ALLOWED_RESOLUTIONS:
            raise AuthorityRefreshError(f"unsupported resolution for {key}")
        _validate_evidence_urls(
            resolution.get("evidence_urls"), f"resolution {key}"
        )
        if "notes" in resolution and not isinstance(resolution["notes"], str):
            raise AuthorityRefreshError(f"resolution {key} notes must be a string")
        if resolution.get("resolution") == "approved_release_updated":
            paths = resolution.get("approved_paths")
            if (
                not isinstance(paths, list)
                or not paths
                or any(not isinstance(path, str) for path in paths)
                or len(paths) != len(set(paths))
            ):
                raise AuthorityRefreshError(
                    f"approved_release_updated resolution {key} requires unique approved_paths"
                )
            for raw_path in paths:
                normalized_path, path = _repo_relative_path(
                    raw_path,
                    "approved path",
                    repo_root=output_root,
                )
                allowed_prefixes = (f"{domain}/", "authority/")
                if not normalized_path.startswith(allowed_prefixes):
                    raise AuthorityRefreshError(
                        f"approved path is outside {domain}/ or authority/: {raw_path}"
                    )
                if require_existing_paths and not path.is_file():
                    raise AuthorityRefreshError(f"approved path is missing: {raw_path}")
        elif "approved_paths" in resolution:
            raise AuthorityRefreshError(
                f"approved_paths is only valid for approved_release_updated: {key}"
            )
        by_key[key] = resolution

    expected = {
        (str(change.get("item_id", "")), str(change.get("change_type", "")))
        for change in changes
    }
    if set(by_key) != expected:
        missing = sorted(expected.difference(by_key))
        extra = sorted(set(by_key).difference(expected))
        raise AuthorityRefreshError(
            f"change resolutions do not match candidate; missing={missing}, extra={extra}"
        )

    impacts = candidate["potential_impacts"]
    impact_resolutions = _require_list(
        approval.get("impact_resolutions"), "approval.impact_resolutions"
    )
    expected_impacts: dict[str, dict[str, Any]] = {}
    for impact in impacts:
        if not isinstance(impact, dict) or not str(impact.get("mapping_id", "")):
            raise AuthorityRefreshError("candidate contains an invalid potential impact")
        mapping_id = str(impact["mapping_id"])
        if mapping_id in expected_impacts:
            raise AuthorityRefreshError(f"duplicate candidate impact: {mapping_id}")
        if impact.get("automatic_change") != "prohibited":
            raise AuthorityRefreshError(
                f"candidate impact does not prohibit automatic change: {mapping_id}"
            )
        expected_impacts[mapping_id] = impact

    resolved_impacts: set[str] = set()
    for index, raw_resolution in enumerate(impact_resolutions):
        resolution = _require_exact_keys(
            raw_resolution,
            {"mapping_id", "determination", "evidence_urls", "reviewed_paths"},
            optional={"notes"},
            label=f"approval.impact_resolutions[{index}]",
        )
        mapping_id = str(resolution.get("mapping_id", ""))
        if not mapping_id or mapping_id in resolved_impacts:
            raise AuthorityRefreshError(
                f"invalid or duplicate impact resolution: {mapping_id}"
            )
        if mapping_id not in expected_impacts:
            raise AuthorityRefreshError(f"unexpected impact resolution: {mapping_id}")
        determination = resolution.get("determination")
        if determination not in ALLOWED_IMPACT_DETERMINATIONS:
            raise AuthorityRefreshError(
                f"unsupported impact determination for {mapping_id}: {determination}"
            )
        _validate_evidence_urls(
            resolution.get("evidence_urls"),
            f"impact resolution {mapping_id}",
        )
        if "notes" in resolution and not isinstance(resolution["notes"], str):
            raise AuthorityRefreshError(
                f"impact resolution {mapping_id} notes must be a string"
            )
        reviewed_paths = resolution["reviewed_paths"]
        if (
            not isinstance(reviewed_paths, list)
            or any(not isinstance(path, str) for path in reviewed_paths)
            or len(reviewed_paths) != len(set(reviewed_paths))
        ):
            raise AuthorityRefreshError(
                f"reviewed_paths must contain unique paths for impact {mapping_id}"
            )
        allowed_paths = {
            str(entry.get("repository_path", ""))
            for entry in expected_impacts[mapping_id].get("affected_paths", [])
            if isinstance(entry, dict)
        }
        if determination == "approved_paths_updated" and not reviewed_paths:
            raise AuthorityRefreshError(
                f"approved_paths_updated impact {mapping_id} requires reviewed_paths"
            )
        for raw_path in reviewed_paths:
            normalized, path = _repo_relative_path(
                raw_path,
                "impact path",
                repo_root=output_root,
            )
            if normalized not in allowed_paths:
                raise AuthorityRefreshError(
                    f"impact {mapping_id} path is outside its crosswalk: {raw_path}"
                )
            if require_existing_paths and not path.is_file():
                raise AuthorityRefreshError(f"impact path is missing: {raw_path}")
        resolved_impacts.add(mapping_id)
    missing_impacts = sorted(set(expected_impacts).difference(resolved_impacts))
    if missing_impacts:
        raise AuthorityRefreshError(
            f"impact resolutions do not match candidate; missing={missing_impacts}"
        )
    return digest


def _approval_referenced_paths(approval: dict[str, Any]) -> list[str]:
    """Return the exact sorted path set whose existence review relied on."""

    referenced: set[str] = set()
    for resolution in approval["change_resolutions"]:
        for raw_path in resolution.get("approved_paths", []):
            normalized, _ = _normalized_repo_path(raw_path, "approved path")
            referenced.add(normalized)
    for resolution in approval["impact_resolutions"]:
        for raw_path in resolution["reviewed_paths"]:
            normalized, _ = _normalized_repo_path(raw_path, "impact path")
            referenced.add(normalized)
    return sorted(referenced)


def _hash_file(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    try:
        with path.open("rb") as handle:
            while chunk := handle.read(1024 * 1024):
                digest.update(chunk)
                size += len(chunk)
    except OSError as exc:
        raise AuthorityRefreshError(f"cannot hash reviewed path {path}: {exc}") from exc
    return digest.hexdigest(), size


def _build_path_manifest(
    approval: dict[str, Any],
    *,
    output_root: Path,
) -> list[dict[str, Any]]:
    manifest: list[dict[str, Any]] = []
    resolved_root = output_root.resolve()
    for normalized in _approval_referenced_paths(approval):
        _, pure = _normalized_repo_path(normalized, "reviewed path")
        unresolved = resolved_root / Path(*pure.parts)
        current = resolved_root
        for part in pure.parts:
            current /= part
            if current.is_symlink():
                raise AuthorityRefreshError(
                    f"reviewed path must not traverse a symlink: {normalized}"
                )
        _, resolved = _repo_relative_path(
            normalized,
            "reviewed path",
            repo_root=resolved_root,
        )
        if not unresolved.is_file() or not resolved.is_file():
            raise AuthorityRefreshError(f"reviewed path is missing: {normalized}")
        digest, size = _hash_file(resolved)
        manifest.append({"path": normalized, "sha256": digest, "size_bytes": size})
    return manifest


def _validate_path_manifest(
    approval: dict[str, Any],
    value: object,
) -> list[dict[str, Any]]:
    manifest = _require_list(value, "validation_context.path_manifest")
    validated: list[dict[str, Any]] = []
    paths: list[str] = []
    for index, raw_entry in enumerate(manifest):
        label = f"validation_context.path_manifest[{index}]"
        entry = _require_exact_keys(raw_entry, PATH_MANIFEST_FIELDS, label=label)
        path, _ = _normalized_repo_path(entry.get("path"), f"{label}.path")
        digest = entry.get("sha256")
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise AuthorityRefreshError(f"{label}.sha256 must be lowercase SHA-256")
        size = entry.get("size_bytes")
        if isinstance(size, bool) or not isinstance(size, int) or size < 0:
            raise AuthorityRefreshError(f"{label}.size_bytes must be non-negative")
        paths.append(path)
        validated.append({"path": path, "sha256": digest, "size_bytes": size})
    if paths != sorted(set(paths)):
        raise AuthorityRefreshError(
            "validation_context.path_manifest must use sorted unique paths"
        )
    expected = _approval_referenced_paths(approval)
    if paths != expected:
        raise AuthorityRefreshError(
            "validation_context.path_manifest does not match approval paths; "
            f"expected={expected}, actual={paths}"
        )
    return validated


def _relative_source_path(path: Path, *, output_root: Path, label: str) -> str:
    resolved_root = output_root.resolve()
    try:
        relative = path.resolve(strict=True).relative_to(resolved_root)
    except (OSError, ValueError) as exc:
        raise AuthorityRefreshError(f"{label} must resolve inside the repository") from exc
    normalized, _ = _normalized_repo_path(relative.as_posix(), label)
    return normalized


def _validate_context_path(
    raw_path: object,
    *,
    prefix: PurePosixPath,
    label: str,
) -> str:
    normalized, pure = _normalized_repo_path(raw_path, label)
    try:
        relative = pure.relative_to(prefix)
    except ValueError as exc:
        raise AuthorityRefreshError(f"{label} must be under {prefix.as_posix()}/") from exc
    if len(relative.parts) < 1 or pure.suffix != ".json":
        raise AuthorityRefreshError(f"{label} must identify a JSON file")
    return normalized


def _validate_candidate_context_path(
    raw_path: object,
    *,
    domain: str,
    label: str,
) -> str:
    prefix = PurePosixPath("authority") / "candidates" / domain / "runs"
    normalized = _validate_context_path(raw_path, prefix=prefix, label=label)
    pure = PurePosixPath(normalized)
    relative = pure.relative_to(prefix)
    if (
        len(relative.parts) != 2
        or not re.fullmatch(r"[0-9]+-[0-9]+", relative.parts[0])
        or relative.parts[1] != "candidate.json"
    ):
        raise AuthorityRefreshError(
            f"{label} must be runs/<workflow-run-id>-<attempt>/candidate.json"
        )
    return normalized


def build_validation_context(
    *,
    candidate: dict[str, Any],
    approval: dict[str, Any],
    candidate_path: Path,
    approval_path: Path,
    output_root: Path,
    source_revision: str,
    source_catalog: dict[str, Any],
    impact_crosswalk: dict[str, Any],
) -> dict[str, Any]:
    """Capture immutable inputs needed to replay the promotion decision."""

    if not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", source_revision):
        raise AuthorityRefreshError(
            "source-revision must be a lowercase 40- or 64-character Git object ID"
        )
    domain = str(candidate["domain"])
    candidate_relative = _relative_source_path(
        candidate_path,
        output_root=output_root,
        label="candidate path",
    )
    approval_relative = _relative_source_path(
        approval_path,
        output_root=output_root,
        label="approval path",
    )
    validated_candidate_path = _validate_candidate_context_path(
        candidate_relative,
        domain=domain,
        label="candidate path",
    )
    if PurePosixPath(validated_candidate_path).parent.name != candidate.get("run_id"):
        raise AuthorityRefreshError(
            "candidate path run directory does not match candidate.run_id"
        )
    _validate_context_path(
        approval_relative,
        prefix=PurePosixPath("authority") / "reviews" / domain,
        label="approval path",
    )
    return {
        "contract_version": VALIDATION_CONTRACT_VERSION,
        "domain": domain,
        "candidate_sha256": candidate["candidate_sha256"],
        "source_revision": source_revision,
        "candidate_path": candidate_relative,
        "approval_path": approval_relative,
        "source_catalog_path": (
            f"tools/authority_refresh/config/{domain}_sources.json"
        ),
        "impact_crosswalk_path": "authority/impact_crosswalk.json",
        "source_catalog": source_catalog,
        "impact_crosswalk": impact_crosswalk,
        "path_manifest": _build_path_manifest(approval, output_root=output_root),
    }


def validate_archived_release(
    candidate: dict[str, Any],
    approval: dict[str, Any],
    validation_context: dict[str, Any],
    *,
    release_date: date,
    historical_baseline: dict[str, Any] | None,
    output_root: Path = REPO_ROOT,
) -> str:
    """Replay promotion using only one release's immutable validation inputs."""

    context = _require_exact_keys(
        validation_context,
        VALIDATION_CONTEXT_FIELDS,
        label="validation_context",
    )
    if context.get("contract_version") != VALIDATION_CONTRACT_VERSION:
        raise AuthorityRefreshError(
            "validation_context.contract_version is unsupported"
        )
    domain = str(candidate.get("domain", ""))
    if context.get("domain") != domain:
        raise AuthorityRefreshError("validation_context domain does not match candidate")
    if context.get("candidate_sha256") != candidate_digest(candidate):
        raise AuthorityRefreshError(
            "validation_context candidate hash does not match candidate"
        )
    source_revision = context.get("source_revision")
    if not isinstance(source_revision, str) or not re.fullmatch(
        r"(?:[0-9a-f]{40}|[0-9a-f]{64})", source_revision
    ):
        raise AuthorityRefreshError("validation_context source_revision is invalid")
    validated_candidate_path = _validate_candidate_context_path(
        context.get("candidate_path"),
        domain=domain,
        label="validation_context.candidate_path",
    )
    if PurePosixPath(validated_candidate_path).parent.name != candidate.get("run_id"):
        raise AuthorityRefreshError(
            "validation_context candidate path does not match candidate.run_id"
        )
    _validate_context_path(
        context.get("approval_path"),
        prefix=PurePosixPath("authority") / "reviews" / domain,
        label="validation_context.approval_path",
    )
    expected_catalog_path = f"tools/authority_refresh/config/{domain}_sources.json"
    if context.get("source_catalog_path") != expected_catalog_path:
        raise AuthorityRefreshError(
            f"validation_context.source_catalog_path must be {expected_catalog_path}"
        )
    if context.get("impact_crosswalk_path") != "authority/impact_crosswalk.json":
        raise AuthorityRefreshError(
            "validation_context.impact_crosswalk_path must be authority/impact_crosswalk.json"
        )
    source_catalog = validate_catalog(
        context.get("source_catalog"),
        domain=domain,
        label="validation_context.source_catalog",
    )
    impact_crosswalk = validate_impact_crosswalk(
        context.get("impact_crosswalk"),
        label="validation_context.impact_crosswalk",
    )
    digest = validate_approval(
        candidate,
        approval,
        output_root=output_root,
        source_catalog=source_catalog,
        impact_crosswalk=impact_crosswalk,
        historical_baseline=historical_baseline,
        require_existing_paths=False,
    )
    _validate_path_manifest(approval, context.get("path_manifest"))
    baseline_approved_at = (
        None
        if historical_baseline is None
        else _parse_date(
            historical_baseline.get("approved_at"),
            "archived predecessor.approved_at",
        )
    )
    validate_release_date(
        candidate=candidate,
        approval=approval,
        release_date=release_date,
        baseline_approved_at=baseline_approved_at,
    )
    return digest


def _load_candidate_baseline(
    candidate: dict[str, Any],
    *,
    output_root: Path,
    historical_baseline: object = _USE_CURRENT_BASELINE,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Validate the candidate's baseline descriptor and return that baseline.

    Normal promotion reads the current snapshot from ``output_root``. Historical
    replay supplies the exact predecessor snapshot (or ``None`` for the bootstrap
    release), so later snapshot changes cannot alter archive validation.
    """

    domain = str(candidate.get("domain", ""))
    expected_relative = f"authority/snapshots/{domain}.json"
    descriptor = _require_exact_keys(
        candidate.get("approved_baseline"),
        {"path", "missing", "sha256"},
        label="candidate.approved_baseline",
    )
    if descriptor.get("path") != expected_relative:
        raise AuthorityRefreshError(
            f"candidate approved_baseline.path must be {expected_relative}"
        )
    missing = descriptor.get("missing")
    if not isinstance(missing, bool):
        raise AuthorityRefreshError("candidate approved_baseline.missing must be boolean")
    expected_sha = descriptor.get("sha256")
    if historical_baseline is _USE_CURRENT_BASELINE:
        snapshot_path = output_root / "authority" / "snapshots" / f"{domain}.json"
        baseline_value: object = (
            _load_json(snapshot_path, "current approved baseline")
            if snapshot_path.is_file()
            else None
        )
    else:
        baseline_value = historical_baseline

    if missing:
        if expected_sha is not None:
            raise AuthorityRefreshError("a missing baseline must have a null sha256")
        if baseline_value is not None:
            raise AuthorityRefreshError(
                "candidate is stale: an approved snapshot now exists"
            )
        return descriptor, {
            "schema_version": SCHEMA_VERSION,
            "domain": domain,
            "items": [],
        }
    if not isinstance(expected_sha, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_sha):
        raise AuthorityRefreshError("existing baseline requires a lowercase SHA-256")
    if not isinstance(baseline_value, dict):
        raise AuthorityRefreshError("candidate is stale: approved snapshot is now missing")
    if sha256_json(baseline_value) != expected_sha:
        raise AuthorityRefreshError("candidate is stale: approved snapshot has changed")
    return descriptor, baseline_value


def _current_baseline_approved_at(
    candidate: dict[str, Any],
    *,
    output_root: Path,
) -> date | None:
    if candidate["approved_baseline"]["missing"]:
        return None
    snapshot = _load_json(
        output_root / "authority" / "snapshots" / f"{candidate['domain']}.json",
        "current approved baseline",
    )
    return _parse_date(snapshot.get("approved_at"), "current approved baseline.approved_at")


def validate_release_date(
    *,
    candidate: dict[str, Any],
    approval: dict[str, Any],
    release_date: date,
    baseline_approved_at: date | None,
) -> None:
    """Apply the same chronology gate to live and archived promotions."""

    generated_at = _parse_timestamp(
        candidate.get("generated_at"),
        "candidate.generated_at",
    )
    latest_review_date = max(
        _parse_timestamp(record.get("reviewed_at"), "reviewed_at")
        .astimezone(timezone.utc)
        .date()
        for record in approval["approvals"]
    )
    if release_date > date.today():
        raise AuthorityRefreshError("release-date cannot be in the future")
    if baseline_approved_at is not None and release_date < baseline_approved_at:
        raise AuthorityRefreshError(
            "release-date cannot precede the approved baseline"
        )
    if (
        release_date < generated_at.astimezone(timezone.utc).date()
        or release_date < latest_review_date
    ):
        raise AuthorityRefreshError(
            "release-date cannot precede the candidate or its latest review"
        )
    candidate_date = generated_at.astimezone(timezone.utc).date()
    if release_date - candidate_date > MAX_CANDIDATE_AGE:
        raise AuthorityRefreshError(
            f"release-date cannot be more than {MAX_CANDIDATE_AGE.days} days "
            "after candidate.generated_at"
        )


def promote(
    *,
    candidate_path: Path,
    approval_path: Path,
    release_date: date,
    output_root: Path,
    source_revision: str,
    confirmation: str | None,
    now: datetime | None = None,
) -> dict[str, Any]:
    candidate = _load_json(candidate_path, "candidate")
    approval = _load_json(approval_path, "approval")
    _validate_latest_candidate(candidate, output_root=output_root, now=now)
    domain = candidate["domain"]
    source_catalog = load_catalog(
        output_root
        / "tools"
        / "authority_refresh"
        / "config"
        / f"{domain}_sources.json",
        domain=domain,
    )
    impact_crosswalk = load_impact_crosswalk(
        output_root / "authority" / "impact_crosswalk.json"
    )
    digest = validate_approval(
        candidate,
        approval,
        output_root=output_root,
        source_catalog=source_catalog,
        impact_crosswalk=impact_crosswalk,
    )
    baseline_approved_at = _current_baseline_approved_at(
        candidate, output_root=output_root
    )
    validate_release_date(
        candidate=candidate,
        approval=approval,
        release_date=release_date,
        baseline_approved_at=baseline_approved_at,
    )
    validation_context = build_validation_context(
        candidate=candidate,
        approval=approval,
        candidate_path=candidate_path,
        approval_path=approval_path,
        output_root=output_root,
        source_revision=source_revision,
        source_catalog=source_catalog,
        impact_crosswalk=impact_crosswalk,
    )
    release_id = f"{release_date.isoformat()}-{domain}-{digest[:12]}"
    release = {
        "schema_version": "1.0",
        "release_id": release_id,
        "domain": domain,
        "candidate_sha256": digest,
        "candidate_generated_at": candidate.get("generated_at"),
        "approved_at": release_date.isoformat(),
        "approval": approval,
        "validation_context_sha256": sha256_json(validation_context),
        "notice": RELEASE_NOTICE,
    }
    if confirmation != CONFIRMATION:
        return release

    release_dir = output_root / "authority" / "releases" / release_id
    if release_dir.exists():
        raise AuthorityRefreshError(f"release already exists: {release_dir}")
    write_json_atomic(release_dir / "candidate.json", candidate)
    write_json_atomic(release_dir / "approval.json", approval)
    write_json_atomic(release_dir / "validation-context.json", validation_context)
    write_json_atomic(release_dir / "release.json", release)
    snapshot = {
        "schema_version": "1.0",
        "domain": domain,
        "release_id": release_id,
        "approved_at": release_date.isoformat(),
        "candidate_sha256": digest,
        "items": candidate.get("items", []),
    }
    write_json_atomic(output_root / "authority" / "snapshots" / f"{domain}.json", snapshot)
    return release


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--approval", type=Path, required=True)
    parser.add_argument("--release-date", type=date.fromisoformat, required=True)
    parser.add_argument("--output-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--source-revision", required=True)
    parser.add_argument("--confirm")
    args = parser.parse_args()
    try:
        release = promote(
            candidate_path=args.candidate,
            approval_path=args.approval,
            release_date=args.release_date,
            output_root=args.output_root,
            source_revision=args.source_revision,
            confirmation=args.confirm,
        )
    except AuthorityRefreshError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    mode = "promoted" if args.confirm == CONFIRMATION else "validated"
    print(json.dumps({"mode": mode, "release": release}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
