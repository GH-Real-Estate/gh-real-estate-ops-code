#!/usr/bin/env python3
"""Monitor approved legal sources without changing the approved release.

The release registry stores hashes for both direct source files and derived
artifacts. This monitor compares like with like, reports sources that need a
purpose-built manual comparison, and never promotes a retrieved payload.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import email.utils
import functools
import hashlib
import io
import json
import re
import ssl
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse


USER_AGENT = "GH-Real-Estate-Legal-Monitor/1.1"
MAX_BYTES = 25 * 1024 * 1024
TIMEOUT = 60
RETRY_ATTEMPTS = 5
RETRYABLE_HTTP_CODES = {408, 425, 429, 500, 502, 503, 504}
MAX_RETRY_DELAY = 15.0
DEFAULT_HOST_CONCURRENCY = 4
HOST_CONCURRENCY = {
    "www.ecfr.gov": 1,
    "searchdro.kscourts.gov": 1,
    "online.encodeplus.com": 2,
}
ECFR_TITLES_URL = "https://www.ecfr.gov/api/versioner/v1/titles.json"
ECFR_URL_RE = re.compile(
    r"^(?P<prefix>https://www\.ecfr\.gov/api/versioner/v1/full/)"
    r"(?P<date>\d{4}-\d{2}-\d{2})"
    r"(?P<suffix>/title-(?P<title>\d+)\.xml(?:\?.*)?)$"
)
ENCODEPLUS_BASE = "https://online.encodeplus.com/regs/overlandpark-ks"
ENCODEPLUS_EXPORT_POLLS = 12
ENCODEPLUS_POLL_DELAY = 2.0
SSL_CONTEXT = ssl.create_default_context()


def retry_delay(headers: object, attempt: int) -> float:
    """Return a bounded Retry-After or exponential-backoff delay."""
    retry_after = headers.get("Retry-After") if hasattr(headers, "get") else None
    if retry_after:
        try:
            return min(MAX_RETRY_DELAY, max(0.0, float(retry_after)))
        except (TypeError, ValueError):
            try:
                retry_at = email.utils.parsedate_to_datetime(str(retry_after))
                if retry_at.tzinfo is None:
                    retry_at = retry_at.replace(tzinfo=timezone.utc)
                seconds = (retry_at - datetime.now(timezone.utc)).total_seconds()
                return min(MAX_RETRY_DELAY, max(0.0, seconds))
            except (TypeError, ValueError, OverflowError):
                pass
    return min(MAX_RETRY_DELAY, float(2 ** (attempt - 1)))


def download_url(
    url: str,
    *,
    capture_body: bool = False,
    attempts: int = RETRY_ATTEMPTS,
    opener=urllib.request.urlopen,
    sleep=time.sleep,
) -> dict[str, object]:
    """Download and fingerprint one URL with bounded transient retries."""
    last_error = "download failed"
    for attempt in range(1, max(1, attempts) + 1):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with opener(request, timeout=TIMEOUT, context=SSL_CONTEXT) as response:
                content_length = response.headers.get("Content-Length")
                if content_length and int(content_length) > MAX_BYTES:
                    raise ValueError(f"source exceeds {MAX_BYTES} bytes")

                digest = hashlib.sha256()
                received = 0
                prefix = bytearray()
                body = bytearray() if capture_body else None
                while True:
                    block = response.read(1024 * 1024)
                    if not block:
                        break
                    received += len(block)
                    if received > MAX_BYTES:
                        raise ValueError(f"source exceeds {MAX_BYTES} bytes")
                    digest.update(block)
                    if len(prefix) < 64:
                        prefix.extend(block[: 64 - len(prefix)])
                    if body is not None:
                        body.extend(block)

                geturl = getattr(response, "geturl", None)
                final_url = geturl() if callable(geturl) else url
                content_type = str(response.headers.get("Content-Type", ""))
                return {
                    "ok": True,
                    "url": url,
                    "final_url": final_url,
                    "http_status": getattr(response, "status", 200),
                    "content_type": content_type.split(";", 1)[0].strip().lower(),
                    "retrieved_sha256": digest.hexdigest(),
                    "bytes": received,
                    "prefix": bytes(prefix),
                    "body": bytes(body) if body is not None else None,
                    "attempts": attempt,
                }
        except urllib.error.HTTPError as exc:
            last_error = f"HTTPError: HTTP Error {exc.code}: {exc.reason}"
            delay = retry_delay(exc.headers, attempt)
            exc.close()
            if exc.code in RETRYABLE_HTTP_CODES and attempt < max(1, attempts):
                sleep(delay)
                continue
            break
        except (OSError, ValueError, urllib.error.URLError) as exc:
            last_error = f"{type(exc).__name__}: {exc}"
            if attempt < max(1, attempts):
                sleep(retry_delay({}, attempt))
                continue
            break

    return {
        "ok": False,
        "url": url,
        "error": last_error,
        "attempts": max(1, attempts),
    }


def load_overrides(path: Path) -> dict[str, dict[str, str]]:
    """Load explicit policies for sources without comparable artifact hashes."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1:
        raise ValueError(f"unsupported source-monitor override schema: {path}")
    overrides = payload.get("overrides")
    if not isinstance(overrides, dict):
        raise ValueError(f"source-monitor overrides must be an object: {path}")

    validated: dict[str, dict[str, str]] = {}
    for citation, override in overrides.items():
        if not isinstance(override, dict) or override.get("mode") != "availability":
            raise ValueError(f"unsupported monitor override for {citation}")
        official_url = override.get("official_url")
        reason = override.get("reason")
        if not isinstance(official_url, str) or not official_url:
            raise ValueError(f"missing official_url override for {citation}")
        if not isinstance(reason, str) or not reason:
            raise ValueError(f"missing override reason for {citation}")
        validated[str(citation)] = {
            "mode": "availability",
            "official_url": official_url,
            "reason": reason,
        }
    return validated


def monitor_policy(
    record: dict[str, object], overrides: dict[str, dict[str, str]]
) -> dict[str, object]:
    """Select an explicit comparison policy for one registry record."""
    citation = str(record.get("citation", ""))
    official_url = str(record.get("official_url", ""))
    override = overrides.get(citation)
    if override:
        if override["official_url"] != official_url:
            raise ValueError(f"official_url mismatch in monitor override for {citation}")
        return {
            "mode": "availability",
            "baseline_kind": "manual-comparison",
            "expected_sha256": None,
            "reason": override["reason"],
        }

    if encodeplus_tocid(official_url) is not None:
        return {
            "mode": "semantic-pdf-pages",
            "baseline_kind": "semantic-approved-bundle-pages",
            "expected_sha256": None,
            "reason": None,
        }

    source_archive_sha256 = record.get("source_archive_sha256")
    expected_sha256 = source_archive_sha256 or record.get("sha256")
    if not isinstance(expected_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_sha256):
        raise ValueError(f"missing valid monitor hash for {citation}")
    return {
        "mode": "hash",
        "baseline_kind": (
            "source_archive_sha256" if source_archive_sha256 else "artifact_sha256"
        ),
        "expected_sha256": expected_sha256,
        "reason": None,
    }


def encodeplus_tocid(url: str) -> str | None:
    """Return an Overland Park enCodePlus table-of-contents id, if applicable."""
    parsed = urlparse(url)
    if (
        parsed.scheme != "https"
        or parsed.hostname != "online.encodeplus.com"
        or parsed.path != "/regs/overlandpark-ks/export2doc.aspx"
    ):
        return None

    query = parse_qs(parsed.query, keep_blank_values=True)
    tocid_values = query.get("tocid", [])
    if query.get("pdf") != ["1"] or len(tocid_values) != 1:
        raise ValueError(f"invalid Overland Park enCodePlus export URL: {url}")
    tocid = tocid_values[0]
    if not re.fullmatch(r"\d+(?:\.\d+)*", tocid):
        raise ValueError(f"invalid Overland Park enCodePlus tocid: {tocid}")
    return tocid


def fetch_encodeplus_pdf(
    source_url: str,
    *,
    downloader=download_url,
    sleep=time.sleep,
) -> dict[str, object]:
    """Generate and download an enCodePlus PDF using its required file token."""
    tocid = encodeplus_tocid(source_url)
    if tocid is None:
        raise ValueError(f"not an Overland Park enCodePlus export URL: {source_url}")

    component_url = f"{ENCODEPLUS_BASE}/component.aspx?" + urlencode(
        {
            "name": "export2doc",
            "doctype": "p",
            "pid": 561,
            "tocid": tocid,
            "catid": 0,
        }
    )
    request_attempts = 0
    export_result: dict[str, object] | None = None
    poll_attempt = 0
    for poll_attempt in range(1, ENCODEPLUS_EXPORT_POLLS + 1):
        metadata = downloader(component_url, capture_body=True)
        request_attempts += int(metadata.get("attempts", 1))
        if not metadata.get("ok"):
            metadata.update(
                url=source_url,
                fetch_method="encodeplus-token-export",
                export_poll_attempts=poll_attempt,
                attempts=request_attempts,
            )
            return metadata
        try:
            export_result = json.loads(bytes(metadata["body"]).decode("utf-8"))
        except (KeyError, TypeError, ValueError, UnicodeDecodeError) as exc:
            return {
                "ok": False,
                "url": source_url,
                "error": f"invalid enCodePlus export metadata: {exc}",
                "fetch_method": "encodeplus-token-export",
                "export_poll_attempts": poll_attempt,
                "attempts": request_attempts,
            }
        if not isinstance(export_result, dict):
            return {
                "ok": False,
                "url": source_url,
                "error": "invalid enCodePlus export metadata type",
                "fetch_method": "encodeplus-token-export",
                "export_poll_attempts": poll_attempt,
                "attempts": request_attempts,
            }
        failed = export_result.get("Failed")
        ready = export_result.get("Ready")
        if failed is not None and not isinstance(failed, bool):
            return {
                "ok": False,
                "url": source_url,
                "error": "invalid enCodePlus Failed flag",
                "fetch_method": "encodeplus-token-export",
                "export_poll_attempts": poll_attempt,
                "attempts": request_attempts,
            }
        if not isinstance(ready, bool):
            return {
                "ok": False,
                "url": source_url,
                "error": "invalid enCodePlus Ready flag",
                "fetch_method": "encodeplus-token-export",
                "export_poll_attempts": poll_attempt,
                "attempts": request_attempts,
            }
        if failed is True:
            return {
                "ok": False,
                "url": source_url,
                "error": f"enCodePlus export failed: {export_result.get('Msg', 'unknown error')}",
                "fetch_method": "encodeplus-token-export",
                "export_poll_attempts": poll_attempt,
                "attempts": request_attempts,
            }
        if ready is True:
            break
        sleep(ENCODEPLUS_POLL_DELAY)
    else:
        return {
            "ok": False,
            "url": source_url,
            "error": f"enCodePlus export was not ready after {ENCODEPLUS_EXPORT_POLLS} polls",
            "fetch_method": "encodeplus-token-export",
            "export_poll_attempts": poll_attempt,
            "attempts": request_attempts,
        }

    remote_file = export_result.get("File") if export_result else None
    if not isinstance(remote_file, str) or not remote_file.strip():
        return {
            "ok": False,
            "url": source_url,
            "error": "enCodePlus export metadata omitted the generated file token",
            "fetch_method": "encodeplus-token-export",
            "export_poll_attempts": poll_attempt,
            "attempts": request_attempts,
        }
    generated_url = f"{ENCODEPLUS_BASE}/export2doc.aspx?" + urlencode(
        {"pdf": 1, "tocid": tocid, "file": remote_file}
    )
    response = downloader(generated_url, capture_body=True)
    request_attempts += int(response.get("attempts", 1))
    response.update(
        url=source_url,
        # Do not persist the temporary file token in reports.
        final_url=source_url,
        fetch_method="encodeplus-token-export",
        export_poll_attempts=poll_attempt,
        attempts=request_attempts,
    )
    return response


def current_ecfr_url(url: str, title_dates: dict[str, str]) -> str:
    """Resolve a pinned eCFR URL to the latest completely processed title date."""
    match = ECFR_URL_RE.match(url)
    if not match:
        return url
    title = match.group("title")
    current_date = title_dates.get(title)
    if not current_date or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", current_date):
        raise ValueError(f"eCFR title {title} has no valid up_to_date_as_of value")
    if current_date < match.group("date"):
        raise ValueError(
            f"eCFR title {title} current date {current_date} precedes approved snapshot "
            f"{match.group('date')}"
        )
    return f"{match.group('prefix')}{current_date}{match.group('suffix')}"


def fetch_ecfr_title_dates(downloader=download_url) -> dict[str, str]:
    """Return the official eCFR up_to_date_as_of date for each title."""
    response = downloader(ECFR_TITLES_URL, capture_body=True)
    if not response.get("ok"):
        raise RuntimeError(str(response.get("error", "eCFR title metadata unavailable")))
    try:
        payload = json.loads(bytes(response["body"]).decode("utf-8"))
        return {
            str(item["number"]): str(item["up_to_date_as_of"])
            for item in payload["titles"]
        }
    except (KeyError, TypeError, ValueError, UnicodeDecodeError) as exc:
        raise RuntimeError(f"invalid eCFR title metadata: {exc}") from exc


def resolve_checked_urls(
    registry: list[dict[str, object]], downloader=download_url
) -> tuple[dict[str, str], dict[str, str]]:
    """Resolve current eCFR URLs and fail those records closed if metadata fails."""
    ecfr_urls = {
        str(record["official_url"])
        for record in registry
        if ECFR_URL_RE.match(str(record.get("official_url", "")))
    }
    if not ecfr_urls:
        return {}, {}
    try:
        title_dates = fetch_ecfr_title_dates(downloader)
        return ({url: current_ecfr_url(url, title_dates) for url in ecfr_urls}, {})
    except (RuntimeError, ValueError) as exc:
        message = f"eCFR currentness metadata error: {exc}"
        return ({}, {url: message for url in ecfr_urls})


def fetch_unique_urls(
    urls: set[str], *, workers: int, downloader=download_url
) -> dict[str, dict[str, object]]:
    """Fetch each URL once while limiting concurrency for sensitive hosts."""
    unique_urls = sorted(urls)
    semaphores = {
        host: threading.BoundedSemaphore(HOST_CONCURRENCY.get(host, DEFAULT_HOST_CONCURRENCY))
        for host in {urlparse(url).hostname or "" for url in unique_urls}
    }

    def fetch(url: str) -> tuple[str, dict[str, object]]:
        host = urlparse(url).hostname or ""
        with semaphores[host]:
            if encodeplus_tocid(url) is not None:
                return url, fetch_encodeplus_pdf(url, downloader=downloader)
            return url, downloader(url)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
        return dict(executor.map(fetch, unique_urls))


def payload_error(record: dict[str, object], response: dict[str, object]) -> str | None:
    """Reject successful HTML/challenge responses where a PDF or XML is expected."""
    official_url = str(record.get("official_url", ""))
    prefix = bytes(response.get("prefix", b""))
    if ECFR_URL_RE.match(official_url):
        if not prefix.lstrip().startswith(b"<"):
            return "official eCFR endpoint did not return XML"
        return None

    if "ftc.gov/business-guidance/" in official_url:
        if not prefix.lstrip().lower().startswith((b"<!doctype html", b"<html")):
            return "official FTC endpoint did not return HTML"
        return None

    build_source_path = str(record.get("build_source_path", "")).lower()
    if build_source_path.endswith(".pdf") or official_url.lower().split("?", 1)[0].endswith(".pdf"):
        if not prefix.startswith(b"%PDF-"):
            return "official PDF endpoint did not return a PDF"
    return None


def normalize_source_text(value: str) -> str:
    """Normalize layout-only whitespace while preserving substantive characters."""
    # PDF extractors may either preserve or remove a visual line wrap after a
    # compound-word hyphen (for example, ``Fifth-\nwheel``). Treat that as
    # layout so a regenerated PDF does not create a false ordinance change.
    value = re.sub(r"(?<=\w)-[ \t]*\r?\n[ \t]*(?=\w)", "-", value)
    return re.sub(r"\s+", " ", value).strip()


def sha256_file(path: Path) -> str:
    """Return a streaming SHA-256 for a local release artifact."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def pdf_reader_factory():
    """Load the pinned PDF reader only when municipal comparison is required."""
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError(
            "pypdf is required for Overland Park source comparison; "
            "install legal/requirements-source-monitor.txt"
        ) from exc
    return PdfReader


def approved_bundle_pages(
    record: dict[str, object],
    repository_root: Path,
    bundle_cache: dict[tuple[str, str], object],
    *,
    reader_factory=None,
) -> list[object]:
    """Load the hash-verified approved bundle slice for one source record."""
    bundle_path_value = record.get("bundle_path")
    bundle_sha256 = record.get("bundle_sha256")
    if not isinstance(bundle_path_value, str) or not bundle_path_value:
        raise RuntimeError(f"missing approved bundle path for {record.get('citation')}")
    if not isinstance(bundle_sha256, str) or not re.fullmatch(
        r"[0-9a-f]{64}", bundle_sha256
    ):
        raise RuntimeError(f"invalid approved bundle hash for {record.get('citation')}")

    root = repository_root.resolve()
    bundle_path = (root / bundle_path_value).resolve()
    try:
        bundle_path.relative_to(root)
    except ValueError as exc:
        raise RuntimeError(f"approved bundle path escapes repository: {bundle_path}") from exc
    if not bundle_path.is_file():
        raise RuntimeError(f"approved bundle is missing: {bundle_path}")

    cache_key = (str(bundle_path), bundle_sha256)
    if cache_key not in bundle_cache:
        actual_sha256 = sha256_file(bundle_path)
        if actual_sha256 != bundle_sha256:
            raise RuntimeError(
                f"approved bundle hash mismatch for {bundle_path_value}: "
                f"expected {bundle_sha256}, got {actual_sha256}"
            )
        reader_type = reader_factory or pdf_reader_factory()
        try:
            reader = reader_type(bundle_path)
        except Exception as exc:
            raise RuntimeError(f"could not read approved bundle {bundle_path}: {exc}") from exc
        if getattr(reader, "is_encrypted", False):
            raise RuntimeError(f"approved bundle is encrypted: {bundle_path}")
        bundle_cache[cache_key] = reader

    reader = bundle_cache[cache_key]
    start = record.get("bundle_start_page")
    end = record.get("bundle_end_page")
    expected_pages = record.get("pages")
    if not all(type(value) is int for value in (start, end, expected_pages)):
        raise RuntimeError(f"invalid approved page range for {record.get('citation')}")
    try:
        total_bundle_pages = len(reader.pages)
    except Exception as exc:
        raise RuntimeError(f"could not enumerate approved bundle pages: {exc}") from exc
    if start < 1 or end < start or end > total_bundle_pages:
        raise RuntimeError(f"approved page range is out of bounds for {record.get('citation')}")
    try:
        pages = list(reader.pages[start - 1 : end])
    except Exception as exc:
        raise RuntimeError(f"could not materialize approved bundle pages: {exc}") from exc
    if len(pages) != expected_pages:
        raise RuntimeError(
            f"approved page count mismatch for {record.get('citation')}: "
            f"registry says {expected_pages}, bundle slice has {len(pages)}"
        )
    return pages


def stable_pdf_value(value: object) -> object:
    """Convert selected PDF metadata into deterministic JSON-safe values."""
    get_object = getattr(value, "get_object", None)
    if callable(get_object):
        value = get_object()
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, bytes):
        return {"bytes_sha256": hashlib.sha256(value).hexdigest()}
    if isinstance(value, (list, tuple)):
        return [stable_pdf_value(item) for item in value]
    if isinstance(value, dict):
        metadata = {
            str(key): stable_pdf_value(item)
            for key, item in sorted(value.items(), key=lambda entry: str(entry[0]))
            if str(key) not in {"/Length", "/Filter"}
        }
        get_data = getattr(value, "get_data", None)
        if callable(get_data):
            return {
                "stream_sha256": hashlib.sha256(get_data()).hexdigest(),
                "metadata": metadata,
            }
        return metadata
    return str(value)


def xobject_fingerprints(page: object) -> list[dict[str, object]]:
    """Fingerprint embedded images/forms so text-equal graphic changes still alert."""
    def for_resources(
        resources: object, recursion_stack: set[int]
    ) -> list[dict[str, object]]:
        get_resources = getattr(resources, "get_object", None)
        if callable(get_resources):
            resources = get_resources()
        xobjects = resources.get("/XObject") if isinstance(resources, dict) else None
        get_xobjects = getattr(xobjects, "get_object", None)
        if callable(get_xobjects):
            xobjects = get_xobjects()
        if not isinstance(xobjects, dict):
            return []

        fingerprints: list[dict[str, object]] = []
        for name, reference in sorted(xobjects.items(), key=lambda entry: str(entry[0])):
            get_object = getattr(reference, "get_object", None)
            xobject = get_object() if callable(get_object) else reference
            get_data = getattr(xobject, "get_data", None)
            if not isinstance(xobject, dict) or not callable(get_data):
                raise RuntimeError(f"invalid PDF XObject {name}")
            identity = id(xobject)
            if identity in recursion_stack:
                raise RuntimeError(f"recursive PDF XObject {name}")
            recursion_stack.add(identity)
            nested = for_resources(xobject.get("/Resources") or {}, recursion_stack)
            recursion_stack.remove(identity)
            fingerprints.append(
                {
                    "name": str(name),
                    "subtype": str(xobject.get("/Subtype", "")),
                    "width": stable_pdf_value(xobject.get("/Width")),
                    "height": stable_pdf_value(xobject.get("/Height")),
                    "bits_per_component": stable_pdf_value(
                        xobject.get("/BitsPerComponent")
                    ),
                    "color_space": stable_pdf_value(xobject.get("/ColorSpace")),
                    "bbox": stable_pdf_value(xobject.get("/BBox")),
                    "matrix": stable_pdf_value(xobject.get("/Matrix")),
                    "data_sha256": hashlib.sha256(get_data()).hexdigest(),
                    "nested_xobjects": nested,
                }
            )
        return fingerprints

    return for_resources(page.get("/Resources") or {}, set())


def semantic_pdf_fingerprint(pages: list[object]) -> str:
    """Fingerprint page-scoped legal text, geometry, and embedded graphics."""
    semantic_pages: list[dict[str, object]] = []
    for page in pages:
        try:
            text = normalize_source_text(str(page.extract_text() or ""))
            semantic_pages.append(
                {
                    "text": text,
                    "media_box": [str(value) for value in page.mediabox],
                    "crop_box": [str(value) for value in page.cropbox],
                    "rotate": int(page.get("/Rotate", 0)),
                    "xobjects": xobject_fingerprints(page),
                }
            )
        except Exception as exc:
            raise RuntimeError(f"could not inspect PDF page semantics: {exc}") from exc
    if not pages or not any(item["text"] for item in semantic_pages):
        raise RuntimeError("PDF contained no extractable legal text")
    encoded = json.dumps(
        semantic_pages, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def encodeplus_semantic_fingerprints(
    record: dict[str, object],
    response: dict[str, object],
    repository_root: Path,
    bundle_cache: dict[tuple[str, str], object],
    *,
    reader_factory=None,
) -> dict[str, object]:
    """Compare a generated export with its hash-verified approved bundle pages."""
    body = response.get("body")
    if not isinstance(body, bytes):
        raise RuntimeError("enCodePlus PDF body was not retained for comparison")
    approved_pages = approved_bundle_pages(
        record,
        repository_root,
        bundle_cache,
        reader_factory=reader_factory,
    )
    reader_type = reader_factory or pdf_reader_factory()
    try:
        retrieved_reader = reader_type(io.BytesIO(body))
        if getattr(retrieved_reader, "is_encrypted", False):
            raise RuntimeError("generated enCodePlus PDF is encrypted")
        retrieved_pages = list(retrieved_reader.pages)
    except RuntimeError:
        raise
    except Exception as exc:
        raise RuntimeError(f"could not read generated enCodePlus PDF: {exc}") from exc
    expected_pages = record.get("pages")
    if type(expected_pages) is not int or len(retrieved_pages) != expected_pages:
        raise RuntimeError(
            f"retrieved page count mismatch for {record.get('citation')}: "
            f"expected {expected_pages}, got {len(retrieved_pages)}"
        )
    return {
        "expected_sha256": semantic_pdf_fingerprint(approved_pages),
        "retrieved_sha256": semantic_pdf_fingerprint(retrieved_pages),
        "retrieved_pages": len(retrieved_pages),
    }


def evaluate_records(
    registry: list[dict[str, object]],
    overrides: dict[str, dict[str, str]],
    checked_urls: dict[str, str],
    resolution_errors: dict[str, str],
    downloads: dict[str, dict[str, object]],
    repository_root: Path,
) -> list[dict[str, object]]:
    """Evaluate downloaded payloads against explicit per-record policies."""
    results: list[dict[str, object]] = []
    bundle_cache: dict[tuple[str, str], object] = {}
    for record in registry:
        official_url = str(record["official_url"])
        checked_url = checked_urls.get(official_url, official_url)
        policy = monitor_policy(record, overrides)
        result: dict[str, object] = {
            "citation": record.get("citation"),
            "title": record.get("title"),
            "url": official_url,
            "checked_url": checked_url,
            "approved_sha256": record.get("sha256"),
            "expected_sha256": policy["expected_sha256"],
            "baseline_kind": policy["baseline_kind"],
            "bundle": record.get("bundle_filename"),
        }

        if official_url in resolution_errors:
            result.update(status="error", error=resolution_errors[official_url])
            results.append(result)
            continue

        response = downloads[checked_url]
        if not response.get("ok"):
            result.update(
                status="error",
                error=response.get("error", "download failed"),
                attempts=response.get("attempts"),
            )
            results.append(result)
            continue

        result.update(
            retrieved_payload_sha256=response["retrieved_sha256"],
            bytes=response["bytes"],
            final_url=response["final_url"],
            http_status=response["http_status"],
            content_type=response["content_type"],
            attempts=response["attempts"],
            fetch_method=response.get("fetch_method", "direct"),
            export_poll_attempts=response.get("export_poll_attempts"),
        )
        invalid_payload = payload_error(record, response)
        if invalid_payload:
            result.update(status="error", error=invalid_payload)
            results.append(result)
            continue

        if policy["mode"] == "availability":
            result.update(
                status="manual",
                retrieved_sha256=response["retrieved_sha256"],
                manual_reason=policy["reason"],
            )
        elif policy["mode"] == "semantic-pdf-pages":
            try:
                fingerprints = encodeplus_semantic_fingerprints(
                    record, response, repository_root, bundle_cache
                )
            except (RuntimeError, ValueError) as exc:
                result.update(status="error", error=str(exc))
                results.append(result)
                continue
            result.update(fingerprints)
            result["status"] = (
                "unchanged"
                if result["retrieved_sha256"] == result["expected_sha256"]
                else "changed"
            )
        else:
            result["retrieved_sha256"] = response["retrieved_sha256"]
            result["status"] = (
                "unchanged"
                if result["retrieved_sha256"] == policy["expected_sha256"]
                else "changed"
            )
        results.append(result)
    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--registry",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "manifests/authority_registry.json",
    )
    parser.add_argument(
        "--overrides",
        type=Path,
        default=Path(__file__).resolve().parents[1]
        / "manifests/source_monitor_overrides.json",
    )
    parser.add_argument(
        "--repository-root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
    )
    parser.add_argument("--json-report", type=Path, default=Path("legal-source-monitor.json"))
    parser.add_argument("--markdown-report", type=Path, default=Path("legal-source-monitor.md"))
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--retry-attempts", type=int, default=RETRY_ATTEMPTS)
    args = parser.parse_args()

    registry = json.loads(args.registry.read_text(encoding="utf-8"))
    overrides = load_overrides(args.overrides)
    for record in registry:
        monitor_policy(record, overrides)

    downloader = functools.partial(
        download_url, attempts=max(1, args.retry_attempts)
    )
    checked_urls, resolution_errors = resolve_checked_urls(registry, downloader)
    urls = {
        checked_urls.get(str(record["official_url"]), str(record["official_url"]))
        for record in registry
        if str(record["official_url"]) not in resolution_errors
    }
    downloads = fetch_unique_urls(
        urls, workers=max(1, args.workers), downloader=downloader
    )
    results = evaluate_records(
        registry,
        overrides,
        checked_urls,
        resolution_errors,
        downloads,
        args.repository_root,
    )

    status_order = {"changed": 0, "error": 1, "manual": 2, "unchanged": 3}
    results.sort(
        key=lambda item: (
            status_order.get(str(item.get("status")), 99),
            str(item.get("citation")),
        )
    )
    counts = {
        status: sum(item["status"] == status for item in results)
        for status in ("unchanged", "changed", "error", "manual")
    }
    payload = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "notice": "Review candidates only; no source was promoted or modified.",
        "counts": counts,
        "results": results,
    }
    args.json_report.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    report_items = [item for item in results if item["status"] != "unchanged"]
    lines = [
        "# Legal source monitor report",
        "",
        f"Checked: {payload['checked_at']}",
        "",
        f"- Unchanged: {counts['unchanged']}",
        f"- Changed fingerprints: {counts['changed']}",
        f"- Retrieval errors: {counts['error']}",
        f"- Manual-comparison sources reached: {counts['manual']}",
        "",
        (
            "> LEGAL REVIEW REQUIRED for changed fingerprints or retrieval errors; "
            "neither establishes that law changed."
        ),
        "",
        (
            "> MANUAL COMPARISON means the source was reachable, but its official "
            "payload is not byte-comparable to the approved derived artifact."
        ),
        "",
    ]
    for item in report_items:
        lines.extend(
            [
                f"## {str(item['status']).upper()} - {item.get('citation')}",
                "",
                f"- Title: {item.get('title')}",
                f"- Bundle: `{item.get('bundle')}`",
                f"- Official URL: {item.get('url')}",
                f"- Checked URL: {item.get('checked_url')}",
                f"- Final URL: {item.get('final_url', 'unavailable')}",
                f"- Baseline kind: `{item.get('baseline_kind')}`",
                f"- Approved artifact SHA-256: `{item.get('approved_sha256')}`",
                f"- Expected monitor SHA-256: `{item.get('expected_sha256', 'not applicable')}`",
                f"- Retrieved comparison SHA-256: `{item.get('retrieved_sha256', 'unavailable')}`",
                (
                    "- Retrieved payload SHA-256: "
                    f"`{item.get('retrieved_payload_sha256', 'unavailable')}`"
                ),
                f"- Fetch method: `{item.get('fetch_method', 'unavailable')}`",
                f"- Export polls: {item.get('export_poll_attempts', 'not applicable')}",
                f"- Attempts: {item.get('attempts', 'unavailable')}",
                f"- Manual reason: {item.get('manual_reason', 'none')}",
                f"- Error: {item.get('error', 'none')}",
                "",
            ]
        )
    args.markdown_report.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(counts))
    return 2 if counts["changed"] or counts["error"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
