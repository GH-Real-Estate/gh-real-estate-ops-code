"""Shared discovery, provenance, comparison, and report primitives.

The discovery layer is intentionally separate from the approved authority library.
It may identify candidate changes, but it never promotes legal or accounting content.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable


SCHEMA_VERSION = "1.0"
USER_AGENT = "GH-Real-Estate-Authority-Refresh/1.0 (+private compliance research)"
DEFAULT_TIMEOUT_SECONDS = 45
DEFAULT_MAX_BYTES = 10 * 1024 * 1024
DEFAULT_ATTEMPTS = 3
MAX_TIMEOUT_SECONDS = 120
MAX_RESPONSE_BYTES = 25 * 1024 * 1024
MAX_ATTEMPTS = 5
DEFAULT_COMPLETE_INDEX_BASELINE_RATIO = 0.8
DEFAULT_MAXIMUM_ITEMS = 5_000
MAXIMUM_ITEMS_PER_SOURCE = 10_000
MAXIMUM_ITEMS_PER_DOMAIN = 10_000
MAX_CANDIDATE_JSON_BYTES = 8 * 1024 * 1024
MAX_CANDIDATE_MARKDOWN_BYTES = 1024 * 1024
ALLOWED_STORAGE_POLICIES = {
    "redistributable",
    "metadata-only",
    "licensed-no-store",
    "manual-review",
}
ALLOWED_MISSING_DETECTION = {"complete-index", "rolling-window"}
NON_SUBSTANTIVE_METADATA_FIELDS = {
    # eCFR advances this currency date even when the title's amendment state is
    # unchanged. Keep it as evidence, but do not create a daily false change.
    "up_to_date_as_of",
}
ITEM_FIELDS = {
    "external_id",
    "title",
    "official_url",
    "published_at",
    "effective_at",
    "status",
    "metadata",
}


class AuthorityRefreshError(RuntimeError):
    """Raised when a source or candidate violates the trust contract."""


@dataclass(frozen=True)
class FetchResult:
    payload: bytes
    final_url: str
    content_type: str
    payload_sha256: str
    attempts: int


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_json(value: object) -> str:
    return sha256_bytes(canonical_json(value).encode("utf-8"))


def write_text_atomic(path: Path, content: str) -> None:
    """Replace a generated report only after the complete file is durable."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            temporary_path = temporary.name
            temporary.write(content)
            temporary.flush()
            os.fsync(temporary.fileno())
        os.replace(temporary_path, path)
        temporary_path = None
    finally:
        if temporary_path:
            Path(temporary_path).unlink(missing_ok=True)


def write_json_atomic(path: Path, value: object) -> None:
    write_text_atomic(path, json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def _host_allowed(host: str, allowed_hosts: Iterable[str]) -> bool:
    normalized = host.rstrip(".").lower()
    return any(normalized == allowed.rstrip(".").lower() for allowed in allowed_hosts)


def validate_official_url(
    url: str,
    allowed_hosts: Iterable[str],
    *,
    allow_http: bool = False,
) -> None:
    parsed = urllib.parse.urlsplit(url)
    if parsed.username or parsed.password:
        raise AuthorityRefreshError("official URLs must not contain credentials")
    if parsed.scheme not in ({"https", "http"} if allow_http else {"https"}):
        raise AuthorityRefreshError("unsupported official URL scheme")
    if not parsed.hostname or not _host_allowed(parsed.hostname, allowed_hosts):
        host = parsed.hostname or "<missing>"
        raise AuthorityRefreshError(f"URL host is not allowlisted: {host}")
    try:
        port = parsed.port
    except ValueError as exc:
        raise AuthorityRefreshError("official URL contains an invalid port") from exc
    if parsed.scheme == "https" and port not in {None, 443}:
        raise AuthorityRefreshError("official HTTPS URLs must use port 443")
    if parsed.scheme == "http" and port not in {None, 80}:
        raise AuthorityRefreshError("official HTTP URLs must use port 80")


class _AllowlistedRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Reject a redirect before urllib can request an off-allowlist target."""

    def __init__(self, allowed_hosts: Iterable[str], *, allow_http: bool = False):
        super().__init__()
        self._allowed_hosts = tuple(allowed_hosts)
        self._allow_http = allow_http

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        target = urllib.parse.urljoin(req.full_url, newurl)
        validate_official_url(
            target,
            self._allowed_hosts,
            allow_http=self._allow_http,
        )
        return super().redirect_request(req, fp, code, msg, headers, target)


def _redact_error(message: str, secret_values: Iterable[str]) -> str:
    """Keep credentials out of persisted candidate and issue error messages."""

    redacted = message
    for value in secret_values:
        if not value:
            continue
        for representation in {value, urllib.parse.quote(value), urllib.parse.quote_plus(value)}:
            redacted = redacted.replace(representation, "REDACTED")
    return redacted


def redact_url(url: str, secret_parameters: Iterable[str] = ()) -> str:
    parsed = urllib.parse.urlsplit(url)
    blocked = {name.lower() for name in secret_parameters}
    query = [
        (name, "REDACTED" if name.lower() in blocked else value)
        for name, value in urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    ]
    return urllib.parse.urlunsplit(
        (parsed.scheme, parsed.netloc, parsed.path, urllib.parse.urlencode(query), "")
    )


def load_catalog(path: Path, *, domain: str) -> dict[str, Any]:
    try:
        catalog = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AuthorityRefreshError(f"cannot load {path}: {exc}") from exc
    if not isinstance(catalog, dict) or not isinstance(catalog.get("sources"), list):
        raise AuthorityRefreshError(f"{path} must contain a sources list")
    allowed_domains = catalog.get("allowed_domains")
    if not isinstance(allowed_domains, list) or not allowed_domains:
        raise AuthorityRefreshError(f"{path} must declare allowed_domains")

    seen: set[str] = set()
    for source in catalog["sources"]:
        if not isinstance(source, dict):
            raise AuthorityRefreshError(f"{path} contains a non-object source")
        required = {
            "source_id",
            "publisher",
            "jurisdiction",
            "authority_type",
            "discovery_url",
            "adapter",
            "storage_policy",
            "cadence",
            "critical",
            "allowed_hosts",
        }
        missing = required.difference(source)
        if missing:
            raise AuthorityRefreshError(
                f"{source.get('source_id', 'unknown')} lacks {', '.join(sorted(missing))}"
            )
        source_id = str(source["source_id"])
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]{2,79}", source_id):
            raise AuthorityRefreshError(f"invalid source_id: {source_id}")
        if source_id in seen:
            raise AuthorityRefreshError(f"duplicate source_id: {source_id}")
        seen.add(source_id)
        if source["storage_policy"] not in ALLOWED_STORAGE_POLICIES:
            raise AuthorityRefreshError(f"invalid storage policy for {source_id}")
        missing_detection = source.get("missing_detection", "complete-index")
        if missing_detection not in ALLOWED_MISSING_DETECTION:
            raise AuthorityRefreshError(
                f"invalid missing_detection policy for {source_id}: {missing_detection}"
            )
        baseline_ratio = source.get(
            "minimum_baseline_ratio",
            DEFAULT_COMPLETE_INDEX_BASELINE_RATIO
            if missing_detection == "complete-index"
            else 0,
        )
        if (
            isinstance(baseline_ratio, bool)
            or not isinstance(baseline_ratio, (int, float))
            or not 0 <= baseline_ratio <= 1
            or (missing_detection == "complete-index" and baseline_ratio == 0)
        ):
            raise AuthorityRefreshError(
                f"minimum_baseline_ratio must be greater than zero and at most one "
                f"for complete-index source {source_id}"
            )
        minimum_items = source.get("minimum_items", 1)
        if (
            isinstance(minimum_items, bool)
            or not isinstance(minimum_items, int)
            or minimum_items < 0
        ):
            raise AuthorityRefreshError(
                f"minimum_items must be a non-negative integer for {source_id}"
            )
        maximum_items = source.get("maximum_items", DEFAULT_MAXIMUM_ITEMS)
        if (
            isinstance(maximum_items, bool)
            or not isinstance(maximum_items, int)
            or maximum_items < max(1, minimum_items)
            or maximum_items > MAXIMUM_ITEMS_PER_SOURCE
        ):
            raise AuthorityRefreshError(
                f"maximum_items must be an integer from max(1, minimum_items) through "
                f"{MAXIMUM_ITEMS_PER_SOURCE} for {source_id}"
            )
        request_config = source.get("request", {})
        if not isinstance(request_config, dict):
            raise AuthorityRefreshError(
                f"request configuration must be an object for {source_id}"
            )
        request_limits = {
            "timeout_seconds": (DEFAULT_TIMEOUT_SECONDS, 1, MAX_TIMEOUT_SECONDS),
            "max_bytes": (DEFAULT_MAX_BYTES, 1, MAX_RESPONSE_BYTES),
            "attempts": (DEFAULT_ATTEMPTS, 1, MAX_ATTEMPTS),
        }
        for setting, (default, minimum, maximum) in request_limits.items():
            configured = request_config.get(setting, default)
            if (
                isinstance(configured, bool)
                or not isinstance(configured, int)
                or not minimum <= configured <= maximum
            ):
                raise AuthorityRefreshError(
                    f"{setting} must be an integer from {minimum} through {maximum} "
                    f"for {source_id}"
                )
        if not isinstance(source["critical"], bool):
            raise AuthorityRefreshError(f"critical must be boolean for {source_id}")
        hosts = source["allowed_hosts"]
        if not isinstance(hosts, list) or not hosts:
            raise AuthorityRefreshError(f"allowed_hosts must be nonempty for {source_id}")
        if any(host not in allowed_domains for host in hosts):
            raise AuthorityRefreshError(f"{source_id} uses a host outside allowed_domains")
        validate_official_url(
            str(source["discovery_url"]),
            hosts,
            allow_http=bool(source.get("allow_http", False)),
        )
        if domain == "accounting" and source["publisher"].lower().startswith(
            ("fasb", "financial accounting")
        ) and source["storage_policy"] == "redistributable":
            raise AuthorityRefreshError(
                f"FASB source {source_id} cannot default to redistributable storage"
            )
    return catalog


def _bounded_read(response: Any, max_bytes: int) -> bytes:
    length = response.headers.get("Content-Length")
    if length:
        try:
            declared_length = int(length)
        except ValueError:
            # Content-Length is advisory; the bounded read loop below still
            # enforces max_bytes when an upstream server sends malformed data.
            declared_length = None
        if declared_length is not None and declared_length > max_bytes:
            raise AuthorityRefreshError(
                f"response exceeds configured {max_bytes}-byte limit"
            )
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = response.read(min(1024 * 1024, max_bytes + 1 - total))
        if not chunk:
            break
        chunks.append(chunk)
        total += len(chunk)
        if total > max_bytes:
            raise AuthorityRefreshError(
                f"response exceeds configured {max_bytes}-byte limit"
            )
    return b"".join(chunks)


def fetch_source(
    source: dict[str, Any],
    *,
    opener: Callable[..., Any] | None = None,
    sleep: Callable[[float], None] = time.sleep,
) -> FetchResult:
    request_config = source.get("request") or {}
    if not isinstance(request_config, dict):
        raise AuthorityRefreshError("request configuration must be an object")
    url = str(source["discovery_url"])
    secret_parameters: list[str] = []
    secret_values: list[str] = []
    api_key_env = request_config.get("api_key_env")
    if api_key_env:
        value = os.environ.get(str(api_key_env), "")
        if not value and request_config.get("api_key_required", False):
            raise AuthorityRefreshError(
                f"required environment variable is unavailable: {api_key_env}"
            )
        if value:
            parameter = str(request_config.get("api_key_query_param", "api_key"))
            secret_parameters.append(parameter)
            secret_values.append(value)
            parsed = urllib.parse.urlsplit(url)
            query = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
            query.append((parameter, value))
            url = urllib.parse.urlunsplit(
                (parsed.scheme, parsed.netloc, parsed.path, urllib.parse.urlencode(query), "")
            )

    allowed_hosts = source["allowed_hosts"]
    validate_official_url(
        url,
        allowed_hosts,
        allow_http=bool(source.get("allow_http", False)),
    )
    timeout = int(request_config.get("timeout_seconds", DEFAULT_TIMEOUT_SECONDS))
    max_bytes = int(request_config.get("max_bytes", DEFAULT_MAX_BYTES))
    attempts = int(request_config.get("attempts", DEFAULT_ATTEMPTS))
    accept = str(request_config.get("accept", "application/json, application/xml, text/html;q=0.9"))
    headers = {"Accept": accept, "User-Agent": USER_AGENT}
    last_error = "unknown fetch failure"
    if opener is None:
        opener = urllib.request.build_opener(
            _AllowlistedRedirectHandler(
                allowed_hosts,
                allow_http=bool(source.get("allow_http", False)),
            )
        ).open

    for attempt in range(1, max(1, attempts) + 1):
        request = urllib.request.Request(url, headers=headers)
        try:
            with opener(request, timeout=timeout) as response:
                final_url = str(response.geturl())
                validate_official_url(
                    final_url,
                    allowed_hosts,
                    allow_http=bool(source.get("allow_http", False)),
                )
                payload = _bounded_read(response, max_bytes)
                content_type = str(response.headers.get("Content-Type", "")).split(";", 1)[0]
                return FetchResult(
                    payload=payload,
                    final_url=_redact_error(
                        redact_url(final_url, secret_parameters),
                        secret_values,
                    ),
                    content_type=content_type,
                    payload_sha256=sha256_bytes(payload),
                    attempts=attempt,
                )
        except urllib.error.HTTPError as exc:
            last_error = _redact_error(f"HTTP {exc.code}: {exc.reason}", secret_values)
            if exc.code not in {408, 425, 429, 500, 502, 503, 504}:
                break
        except (AuthorityRefreshError, OSError, ValueError, urllib.error.URLError) as exc:
            last_error = _redact_error(f"{type(exc).__name__}: {exc}", secret_values)
        if attempt < max(1, attempts):
            sleep(min(8.0, float(2 ** (attempt - 1))))
    raise AuthorityRefreshError(
        f"fetch failed after {attempt} attempt(s): {last_error}"
    )


def _sanitize_metadata(value: Any, *, depth: int = 0) -> Any:
    if depth > 5:
        raise AuthorityRefreshError("metadata nesting exceeds five levels")
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, str):
        return value[:10_000]
    if isinstance(value, list):
        return [_sanitize_metadata(item, depth=depth + 1) for item in value[:100]]
    if isinstance(value, dict):
        result: dict[str, Any] = {}
        for key, item in list(value.items())[:100]:
            name = str(key)
            if name.lower() in {"content", "body", "raw", "codification_text"}:
                raise AuthorityRefreshError(f"prohibited metadata field: {name}")
            result[name] = _sanitize_metadata(item, depth=depth + 1)
        return result
    raise AuthorityRefreshError(f"unsupported metadata type: {type(value).__name__}")


def normalize_item(
    raw: dict[str, Any],
    source: dict[str, Any],
    *,
    domain: str,
) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise AuthorityRefreshError("adapter returned a non-object item")
    unexpected = set(raw).difference(ITEM_FIELDS)
    if unexpected:
        raise AuthorityRefreshError(
            f"adapter returned unsupported fields: {', '.join(sorted(unexpected))}"
        )
    external_id = str(raw.get("external_id", "")).strip()
    title = str(raw.get("title", "")).strip()
    official_url = str(raw.get("official_url", "")).strip()
    if not external_id or not title or not official_url:
        raise AuthorityRefreshError("item requires external_id, title, and official_url")
    validate_official_url(
        official_url,
        source["allowed_hosts"],
        allow_http=bool(source.get("allow_http", False)),
    )
    source_id = str(source["source_id"])
    item_id = f"{domain}-{source_id}-{sha256_bytes(external_id.encode('utf-8'))[:16]}"
    metadata = _sanitize_metadata(raw.get("metadata") or {})
    # Retrieval telemetry belongs to the per-source result. Removing it from the
    # item keeps fingerprints stable when official metadata has not changed.
    for transient_key in (
        "fetched_at",
        "retrieved_at",
        "source_response_url",
        "response_url",
    ):
        metadata.pop(transient_key, None)
    normalized = {
        "item_id": item_id,
        "source_id": source_id,
        "external_id": external_id[:500],
        "title": title[:2_000],
        "official_url": official_url,
        "publisher": str(source["publisher"]),
        "jurisdiction": str(source["jurisdiction"]),
        "authority_type": str(source["authority_type"]),
        "storage_policy": str(source["storage_policy"]),
        "published_at": raw.get("published_at"),
        "effective_at": raw.get("effective_at"),
        "status": str(raw.get("status") or "discovered"),
        "metadata": metadata,
    }
    fingerprint_value = {
        key: normalized[key]
        for key in normalized
        if key not in {"item_id", "source_id"}
    }
    fingerprint_value["metadata"] = {
        key: value
        for key, value in metadata.items()
        if key not in NON_SUBSTANTIVE_METADATA_FIELDS
    }
    normalized["fingerprint"] = sha256_json(fingerprint_value)
    return normalized


def deduplicate_items(items: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id: dict[str, dict[str, Any]] = {}
    for item in items:
        existing = by_id.get(item["item_id"])
        if existing and existing["fingerprint"] != item["fingerprint"]:
            raise AuthorityRefreshError(
                f"conflicting duplicate item: {item['item_id']}"
            )
        by_id[item["item_id"]] = item
    return [by_id[key] for key in sorted(by_id)]


def load_baseline(path: Path, *, domain: str) -> tuple[dict[str, Any], bool]:
    if not path.exists():
        return {"schema_version": SCHEMA_VERSION, "domain": domain, "items": []}, True
    try:
        baseline = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AuthorityRefreshError(f"cannot load baseline {path}: {exc}") from exc
    if baseline.get("domain") != domain or not isinstance(baseline.get("items"), list):
        raise AuthorityRefreshError(f"invalid {domain} baseline: {path}")
    return baseline, False


def complete_index_baseline_floor(
    source: dict[str, Any],
    baseline_items: Iterable[dict[str, Any]],
) -> int:
    """Return the minimum credible item count for a complete-index response."""

    if source.get("missing_detection", "complete-index") != "complete-index":
        return 0
    source_id = str(source["source_id"])
    baseline_item_count = sum(
        item.get("source_id") == source_id
        for item in baseline_items
        if isinstance(item, dict)
    )
    baseline_ratio = float(
        source.get(
            "minimum_baseline_ratio",
            DEFAULT_COMPLETE_INDEX_BASELINE_RATIO,
        )
    )
    return math.ceil(baseline_item_count * baseline_ratio)


def validate_complete_index_baseline_coverage(
    source: dict[str, Any],
    baseline_items: Iterable[dict[str, Any]],
    observed_items: Iterable[dict[str, Any]],
) -> None:
    """Fail closed when a complete index no longer retains enough approved IDs."""

    baseline_values = list(baseline_items)
    baseline_floor = complete_index_baseline_floor(source, baseline_values)
    if baseline_floor == 0:
        return
    source_id = str(source["source_id"])
    baseline_ids = {
        str(item.get("item_id"))
        for item in baseline_values
        if isinstance(item, dict) and item.get("source_id") == source_id
    }
    observed_ids = {
        str(item.get("item_id"))
        for item in observed_items
        if isinstance(item, dict) and item.get("source_id") == source_id
    }
    retained = len(baseline_ids.intersection(observed_ids))
    if retained < baseline_floor:
        baseline_ratio = float(
            source.get(
                "minimum_baseline_ratio",
                DEFAULT_COMPLETE_INDEX_BASELINE_RATIO,
            )
        )
        raise AuthorityRefreshError(
            f"complete-index source retained {retained} approved item(s), below "
            f"the {baseline_floor}-item baseline coverage floor "
            f"({baseline_ratio:.0%} of its approved baseline)"
        )


def compare_items(
    baseline_items: Iterable[dict[str, Any]],
    current_items: Iterable[dict[str, Any]],
    *,
    healthy_sources: set[str],
) -> list[dict[str, Any]]:
    before = {item["item_id"]: item for item in baseline_items}
    after = {item["item_id"]: item for item in current_items}
    changes: list[dict[str, Any]] = []
    for item_id in sorted(after.keys() - before.keys()):
        changes.append(
            {
                "change_type": "new",
                "item_id": item_id,
                "source_id": after[item_id]["source_id"],
                "before": None,
                "after": after[item_id],
            }
        )
    for item_id in sorted(after.keys() & before.keys()):
        if after[item_id].get("fingerprint") != before[item_id].get("fingerprint"):
            changes.append(
                {
                    "change_type": "modified",
                    "item_id": item_id,
                    "source_id": after[item_id]["source_id"],
                    "before": before[item_id],
                    "after": after[item_id],
                }
            )
    for item_id in sorted(before.keys() - after.keys()):
        source_id = str(before[item_id].get("source_id", ""))
        if source_id in healthy_sources:
            changes.append(
                {
                    "change_type": "missing",
                    "item_id": item_id,
                    "source_id": source_id,
                    "before": before[item_id],
                    "after": None,
                }
            )
    return changes


def retain_unobserved_baseline_items(
    baseline_items: Iterable[dict[str, Any]],
    discovered_items: Iterable[dict[str, Any]],
    *,
    source_results: Iterable[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Preserve items a bounded or unavailable source could not disprove.

    Only a healthy, complete-index source may remove an item from the next reviewed
    snapshot. Rolling feeds and unavailable optional sources cannot establish that an
    older authority item disappeared.
    """

    results = {str(result.get("source_id", "")): result for result in source_results}
    merged = {item["item_id"]: item for item in deduplicate_items(discovered_items)}
    for item in deduplicate_items(baseline_items):
        if item["item_id"] in merged:
            continue
        result = results.get(str(item.get("source_id", "")))
        can_establish_absence = bool(
            result
            and result.get("status") == "healthy"
            and result.get("missing_detection", "complete-index") == "complete-index"
        )
        if not can_establish_absence:
            merged[item["item_id"]] = item
    return [merged[key] for key in sorted(merged)]


def build_candidate(
    *,
    domain: str,
    generated_at: str,
    run_id: str,
    baseline_path: Path,
    baseline: dict[str, Any],
    baseline_missing: bool,
    source_results: list[dict[str, Any]],
    items: list[dict[str, Any]],
    impact_crosswalk: dict[str, Any] | None = None,
) -> dict[str, Any]:
    successful_sources = {
        result["source_id"]
        for result in source_results
        if result["status"] == "healthy"
    }
    missing_eligible_sources = {
        result["source_id"]
        for result in source_results
        if result["status"] == "healthy"
        and result.get("missing_detection", "complete-index") == "complete-index"
    }
    snapshot_items = retain_unobserved_baseline_items(
        baseline.get("items", []),
        items,
        source_results=source_results,
    )
    changes = compare_items(
        baseline.get("items", []),
        snapshot_items,
        healthy_sources=missing_eligible_sources,
    )
    degraded = any(
        result["status"] == "error"
        or (result["status"] == "configuration_required" and result["critical"])
        for result in source_results
    )
    status = "degraded" if degraded else ("review_required" if changes else "current")
    potential_impacts = build_potential_impacts(
        domain=domain,
        impact_crosswalk=impact_crosswalk,
        include=bool(changes) or degraded,
    )
    candidate: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "domain": domain,
        "generated_at": generated_at,
        "run_id": run_id,
        "status": status,
        "notice": (
            "Automated discovery evidence only. Official sources and qualified review "
            "control; this candidate is not approved law, GAAP, or compliance advice."
        ),
        "approved_baseline": {
            "path": baseline_path.as_posix(),
            "missing": baseline_missing,
            "sha256": None if baseline_missing else sha256_json(baseline),
        },
        "counts": {
            "sources": len(source_results),
            "healthy_sources": len(successful_sources),
            "items": len(snapshot_items),
            "new": sum(c["change_type"] == "new" for c in changes),
            "modified": sum(c["change_type"] == "modified" for c in changes),
            "missing_items": sum(c["change_type"] == "missing" for c in changes),
            "source_errors": sum(r["status"] == "error" for r in source_results),
            "configuration_required": sum(
                r["status"] == "configuration_required" for r in source_results
            ),
            "potential_impacts": len(potential_impacts),
        },
        "source_results": source_results,
        "changes": changes,
        "potential_impacts": potential_impacts,
        "items": snapshot_items,
    }
    candidate["candidate_sha256"] = sha256_json(candidate)
    return candidate


def load_impact_crosswalk(path: Path) -> dict[str, Any]:
    """Load the conservative alert-routing map used in discovery reports."""
    try:
        crosswalk = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AuthorityRefreshError(f"cannot load impact crosswalk {path}: {exc}") from exc
    mappings = crosswalk.get("mappings") if isinstance(crosswalk, dict) else None
    if not isinstance(mappings, list) or not mappings:
        raise AuthorityRefreshError("impact crosswalk must contain nonempty mappings")
    seen: set[str] = set()
    for mapping in mappings:
        if not isinstance(mapping, dict):
            raise AuthorityRefreshError("impact crosswalk contains a non-object mapping")
        mapping_id = str(mapping.get("id", ""))
        if not mapping_id or mapping_id in seen:
            raise AuthorityRefreshError(f"invalid or duplicate impact mapping: {mapping_id}")
        seen.add(mapping_id)
        if mapping.get("automatic_change") != "prohibited":
            raise AuthorityRefreshError(
                f"impact mapping {mapping_id} must prohibit automatic changes"
            )
        if not isinstance(mapping.get("authority_references"), list):
            raise AuthorityRefreshError(
                f"impact mapping {mapping_id} lacks authority_references"
            )
        if not isinstance(mapping.get("affected_paths"), list) or not mapping["affected_paths"]:
            raise AuthorityRefreshError(
                f"impact mapping {mapping_id} lacks affected_paths"
            )
    return crosswalk


def build_potential_impacts(
    *,
    domain: str,
    impact_crosswalk: dict[str, Any] | None,
    include: bool,
) -> list[dict[str, Any]]:
    """Return conservative review routes, never automated implementation instructions.

    Discovery metadata is not sufficiently precise to infer legal or GAAP scope.
    When a domain has a change or source failure, include every crosswalk mapping
    that references that domain (and tax references for the accounting scan). A
    qualified reviewer narrows the result and records a resolution during promotion.
    """
    if not include or impact_crosswalk is None:
        return []
    relevant_domains = {domain}
    if domain == "accounting":
        relevant_domains.add("tax")
    impacts: list[dict[str, Any]] = []
    for mapping in impact_crosswalk["mappings"]:
        references = mapping.get("authority_references", [])
        if not any(
            isinstance(reference, dict)
            and reference.get("domain") in relevant_domains
            for reference in references
        ):
            continue
        impacts.append(
            {
                "mapping_id": mapping["id"],
                "name": mapping.get("name", mapping["id"]),
                "affected_paths": mapping["affected_paths"],
                "review_gate": mapping.get("review_gate", {}),
                "automatic_change": "prohibited",
                "fail_closed_action": mapping.get("fail_closed_action"),
            }
        )
    return sorted(impacts, key=lambda impact: impact["mapping_id"])


def candidate_markdown(candidate: dict[str, Any], *, max_changes: int = 100) -> str:
    counts = candidate["counts"]
    lines = [
        f"# {candidate['domain'].title()} authority discovery candidate",
        "",
        f"- Status: **{candidate['status']}**",
        f"- Generated: {candidate['generated_at']}",
        f"- Candidate SHA-256: `{candidate['candidate_sha256']}`",
        f"- Sources: {counts['healthy_sources']} healthy / {counts['sources']} configured",
        f"- Discovered items: {counts['items']}",
        f"- New: {counts['new']}",
        f"- Modified: {counts['modified']}",
        f"- Missing from successful source responses: {counts['missing_items']}",
        f"- Source errors: {counts['source_errors']}",
        f"- Optional source configuration required: {counts['configuration_required']}",
        f"- Conservative potential-impact routes: {counts.get('potential_impacts', 0)}",
        "",
        "> This is unapproved discovery evidence. It must not be cited as current law,",
        "> authoritative GAAP, or an approved GH policy.",
        "",
        "## Source health",
        "",
    ]
    for result in candidate["source_results"]:
        detail = result.get("error") or f"{result.get('item_count', 0)} item(s)"
        lines.append(f"- `{result['source_id']}` — **{result['status']}** — {detail}")
    lines.extend(["", "## Candidate changes", ""])
    for change in candidate["changes"][:max_changes]:
        item = change.get("after") or change.get("before") or {}
        lines.extend(
            [
                f"### {change['change_type'].upper()}: {item.get('title', change['item_id'])}",
                "",
                f"- Item: `{change['item_id']}`",
                f"- Source: `{change['source_id']}`",
                f"- Official URL: {item.get('official_url', 'unavailable')}",
                "",
            ]
        )
    omitted = len(candidate["changes"]) - max_changes
    if omitted > 0:
        lines.extend(
            [
                f"> {omitted} additional changes are available in the JSON candidate.",
                "",
            ]
        )
    impacts = candidate.get("potential_impacts", [])
    lines.extend(
        [
            "## Potential repository impacts",
            "",
            (
                "These are conservative review routes, not findings that every listed "
                "artifact must change. Each route requires an evidence-backed human disposition."
            ),
            "",
        ]
    )
    if not impacts:
        lines.extend(["- None for this run.", ""])
    for impact in impacts:
        paths = ", ".join(
            f"`{entry.get('repository_path')}`"
            for entry in impact.get("affected_paths", [])
            if isinstance(entry, dict)
        )
        lines.extend(
            [
                f"### {impact['name']}",
                "",
                f"- Mapping: `{impact['mapping_id']}`",
                f"- Automatic change: **{impact['automatic_change']}**",
                f"- Review paths: {paths or 'See impact crosswalk.'}",
                "",
            ]
        )
    lines.extend(
        [
            "## Required review",
            "",
            "1. Verify the official source, legal/accounting status, effective date, and scope.",
            "2. Resolve every candidate change with evidence.",
            "3. Regenerate affected approved materials separately when required.",
            "4. Use the protected promotion workflow; do not edit approved current paths directly.",
            "",
        ]
    )
    return "\n".join(lines)


def bounded_issue_markdown(candidate: dict[str, Any]) -> str:
    report = candidate_markdown(candidate, max_changes=20)
    limit = 20_000
    encoded = report.encode("utf-8")
    if len(encoded) <= limit:
        return report
    suffix = "\n\n> Summary truncated. Review the workflow artifact and candidate PR.\n"
    suffix_bytes = suffix.encode("utf-8")
    prefix = encoded[: limit - len(suffix_bytes)]
    while True:
        try:
            decoded = prefix.decode("utf-8")
            break
        except UnicodeDecodeError:
            prefix = prefix[:-1]
    return decoded.rstrip() + suffix


def _fixture_path(fixture_dir: Path, source: dict[str, Any]) -> Path:
    configured = source.get("fixture_filename")
    if configured:
        return fixture_dir / str(configured)
    return fixture_dir / f"{source['source_id']}.fixture"


def scan_domain(
    *,
    domain: str,
    catalog_path: Path,
    baseline_path: Path,
    parser: Callable[[bytes, dict[str, Any], str, str], list[dict[str, Any]]],
    output_dir: Path,
    run_id: str,
    fixture_dir: Path | None = None,
    impact_crosswalk_path: Path | None = None,
) -> tuple[dict[str, Any], int]:
    catalog = load_catalog(catalog_path, domain=domain)
    baseline, baseline_missing = load_baseline(baseline_path, domain=domain)
    impact_crosswalk = (
        load_impact_crosswalk(impact_crosswalk_path)
        if impact_crosswalk_path is not None
        else None
    )
    generated_at = utc_now()
    source_results: list[dict[str, Any]] = []
    items: list[dict[str, Any]] = []

    for source in catalog["sources"]:
        source_id = str(source["source_id"])
        result: dict[str, Any] = {
            "source_id": source_id,
            "critical": bool(source["critical"]),
            "storage_policy": source["storage_policy"],
            "discovery_url": source["discovery_url"],
            "retrieved_at": generated_at,
            "missing_detection": source.get(
                "missing_detection", "complete-index"
            ),
        }
        try:
            if fixture_dir is not None:
                fixture = _fixture_path(fixture_dir, source)
                if not fixture.is_file():
                    raise AuthorityRefreshError(f"fixture is missing: {fixture}")
                fetched = FetchResult(
                    payload=fixture.read_bytes(),
                    final_url=str(source["discovery_url"]),
                    content_type="application/octet-stream",
                    payload_sha256=sha256_bytes(fixture.read_bytes()),
                    attempts=1,
                )
            else:
                fetched = fetch_source(source)
            parsed = parser(
                fetched.payload, source, generated_at, fetched.final_url
            )
            normalized = deduplicate_items(
                normalize_item(item, source, domain=domain) for item in parsed
            )
            minimum_items = int(source.get("minimum_items", 1))
            if len(normalized) < minimum_items:
                raise AuthorityRefreshError(
                    f"source returned {len(normalized)} item(s); "
                    f"minimum_items is {minimum_items}"
                )
            maximum_items = int(source.get("maximum_items", DEFAULT_MAXIMUM_ITEMS))
            if len(normalized) > maximum_items:
                raise AuthorityRefreshError(
                    f"source returned {len(normalized)} item(s); "
                    f"maximum_items is {maximum_items}"
                )
            validate_complete_index_baseline_coverage(
                source,
                baseline.get("items", []),
                normalized,
            )
            if len(items) + len(normalized) > MAXIMUM_ITEMS_PER_DOMAIN:
                raise AuthorityRefreshError(
                    f"domain discovery would exceed the {MAXIMUM_ITEMS_PER_DOMAIN}-item limit"
                )
            items.extend(normalized)
            result.update(
                {
                    "status": "healthy",
                    "final_url": fetched.final_url,
                    "content_type": fetched.content_type,
                    "payload_sha256": fetched.payload_sha256,
                    "attempts": fetched.attempts,
                    "item_count": len(normalized),
                    "observed_item_ids": sorted(item["item_id"] for item in normalized),
                }
            )
        except AuthorityRefreshError as exc:
            configuration_required = "environment variable is unavailable" in str(exc)
            result.update(
                {
                    "status": (
                        "configuration_required" if configuration_required else "error"
                    ),
                    "error": str(exc),
                    "item_count": 0,
                    "observed_item_ids": [],
                }
            )
        except Exception as exc:  # defensive boundary around source-specific parsers
            result.update(
                {
                    "status": "error",
                    "error": f"{type(exc).__name__}: {exc}",
                    "item_count": 0,
                    "observed_item_ids": [],
                }
            )
        source_results.append(result)

    items = deduplicate_items(items)
    candidate = build_candidate(
        domain=domain,
        generated_at=generated_at,
        run_id=run_id,
        baseline_path=Path("authority") / "snapshots" / f"{domain}.json",
        baseline=baseline,
        baseline_missing=baseline_missing,
        source_results=source_results,
        items=items,
        impact_crosswalk=impact_crosswalk,
    )
    candidate_json = json.dumps(candidate, indent=2, ensure_ascii=False) + "\n"
    if len(candidate_json.encode("utf-8")) > MAX_CANDIDATE_JSON_BYTES:
        raise AuthorityRefreshError(
            f"candidate JSON exceeds the {MAX_CANDIDATE_JSON_BYTES}-byte limit"
        )
    candidate_report = candidate_markdown(candidate)
    if len(candidate_report.encode("utf-8")) > MAX_CANDIDATE_MARKDOWN_BYTES:
        raise AuthorityRefreshError(
            f"candidate Markdown exceeds the {MAX_CANDIDATE_MARKDOWN_BYTES}-byte limit"
        )
    output_dir.mkdir(parents=True, exist_ok=True)
    write_text_atomic(output_dir / f"{domain}-candidate.json", candidate_json)
    write_text_atomic(
        output_dir / f"{domain}-candidate.md", candidate_report
    )
    write_text_atomic(
        output_dir / f"{domain}-candidate-issue.md",
        bounded_issue_markdown(candidate),
    )
    exit_code = 3 if candidate["status"] == "degraded" else (
        2 if candidate["status"] == "review_required" else 0
    )
    return candidate, exit_code
