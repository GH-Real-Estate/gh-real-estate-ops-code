#!/usr/bin/env python3
"""Validate and monitor GH's curated tax-authority registry.

The monitor retrieves official sources, records availability and fingerprints,
and identifies records due for review. It never edits approved sourcebooks,
accounting policy, the chart of accounts, Zoho, elections, payments, or returns.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import email.utils
import hashlib
import http.client
import json
import os
import re
import ssl
import tempfile
import threading
import time
import urllib.error
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlparse


USER_AGENT = "GH-Real-Estate-Tax-Authority-Monitor/1.0"
MAX_BYTES = 30 * 1024 * 1024
TIMEOUT_SECONDS = 45
RETRY_ATTEMPTS = 3
RETRYABLE_HTTP_CODES = {408, 425, 429, 500, 502, 503, 504}
MAX_RETRY_DELAY = 15.0
DEFAULT_HOST_CONCURRENCY = 2
ISSUE_MAX_ITEMS = 25
ISSUE_MAX_CHARS = 25_000
SSL_CONTEXT = ssl.create_default_context()

ALLOWED_HOSTS = {
    "codes.opkansas.org",
    "ecfr.gov",
    "govinfo.gov",
    "irs.gov",
    "jocogov.org",
    "ksrevenue.gov",
    "ksrevisor.gov",
    "missionks.org",
    "opkansas.gov",
    "opkansas.org",
    "sos.ks.gov",
    "uscode.house.gov",
    "www.ecfr.gov",
    "www.govinfo.gov",
    "www.irs.gov",
    "www.jocogov.org",
    "www.ksrevenue.gov",
    "www.missionks.org",
    "www.opkansas.gov",
    "www.opkansas.org",
}

ALLOWED_AUTHORITY_WEIGHTS = {
    "binding-statute",
    "binding-public-law",
    "binding-regulation",
    "binding-municipal-code",
    "published-irs-guidance",
    "official-filing-form",
    "official-filing-instructions",
    "official-guidance",
    "official-administration",
}

SOURCEBOOK_PATHS = (
    "accounting/text/current/01_GH_Federal_Rental_Tax_and_US_GAAP_Sourcebook_2026-07-12.txt",
    "accounting/text/current/02_GH_Kansas_Rental_Accounting_and_Tax_Law_Sourcebook_2026-07-12.txt",
    "accounting/text/current/03_GH_Overland_Park_and_Johnson_County_Compliance_Sourcebook_2026-07-12.txt",
)


def fail(message: str) -> None:
    raise ValueError(message)


def parse_iso_date(value: object, field: str, record_id: str) -> date:
    try:
        return date.fromisoformat(str(value))
    except ValueError as exc:
        raise ValueError(f"{record_id} has invalid {field}: {value}") from exc


def validate_registry(
    payload: dict[str, object], repository_root: Path, *, check_sourcebooks: bool = True
) -> list[dict[str, object]]:
    if payload.get("schema_version") != 1:
        fail("unsupported tax-authority registry schema")
    if payload.get("formal_review_cadence") != "semiannual":
        fail("formal review cadence must be semiannual")
    if payload.get("formal_review_months") != [1, 7]:
        fail("formal review months must be January and July")

    records = payload.get("records")
    if not isinstance(records, list) or len(records) < 30:
        fail("tax-authority registry must contain at least 30 focused records")

    sourcebook_text = ""
    if check_sourcebooks:
        for relative in SOURCEBOOK_PATHS:
            path = repository_root / relative
            if not path.is_file():
                fail(f"missing approved sourcebook text: {relative}")
            sourcebook_text += path.read_text(encoding="utf-8") + "\n"

    required = {
        "id",
        "title",
        "jurisdiction",
        "tax_area",
        "authority_weight",
        "official_url",
        "sourcebook_ids",
        "applicability",
        "volatility",
        "last_reviewed",
        "next_review",
        "monitoring_mode",
        "expected_content_types",
        "approved_sha256",
        "reviewer_gate",
    }
    seen: set[str] = set()
    for item in records:
        if not isinstance(item, dict):
            fail("every tax-authority record must be an object")
        record_id = str(item.get("id", ""))
        missing = required.difference(item)
        if missing:
            fail(f"{record_id or 'record'} lacks {', '.join(sorted(missing))}")
        if not re.fullmatch(r"[A-Z0-9]+(?:-[A-Z0-9]+)+", record_id):
            fail(f"invalid record id: {record_id}")
        if record_id in seen:
            fail(f"duplicate record id: {record_id}")
        seen.add(record_id)

        if item["authority_weight"] not in ALLOWED_AUTHORITY_WEIGHTS:
            fail(f"{record_id} has unsupported authority weight")
        if item["monitoring_mode"] != "availability-and-fingerprint":
            fail(f"{record_id} has unsupported monitoring mode")
        if item["volatility"] not in {"low", "medium", "high", "annual"}:
            fail(f"{record_id} has unsupported volatility")

        parsed = urlparse(str(item["official_url"]))
        if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS:
            fail(f"{record_id} does not use an approved official HTTPS host")

        last_reviewed = parse_iso_date(item["last_reviewed"], "last_reviewed", record_id)
        next_review = parse_iso_date(item["next_review"], "next_review", record_id)
        if next_review <= last_reviewed:
            fail(f"{record_id} next_review must follow last_reviewed")

        content_types = item["expected_content_types"]
        if not isinstance(content_types, list) or not content_types:
            fail(f"{record_id} must list expected content types")
        if any(not isinstance(value, str) or "/" not in value for value in content_types):
            fail(f"{record_id} has an invalid expected content type")

        approved_sha256 = item["approved_sha256"]
        if approved_sha256 is not None and not re.fullmatch(
            r"[0-9a-f]{64}", str(approved_sha256)
        ):
            fail(f"{record_id} has an invalid approved_sha256")

        sourcebook_ids = item["sourcebook_ids"]
        if not isinstance(sourcebook_ids, list):
            fail(f"{record_id} sourcebook_ids must be a list")
        if check_sourcebooks:
            for sourcebook_id in sourcebook_ids:
                if not re.search(
                    rf"(?m)^\s*{re.escape(str(sourcebook_id))}\s+", sourcebook_text
                ):
                    fail(f"{record_id} references absent sourcebook id {sourcebook_id}")

        if not str(item["reviewer_gate"]).strip():
            fail(f"{record_id} must state a reviewer gate")

    return records


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


def download(
    record: dict[str, object],
    *,
    attempts: int = RETRY_ATTEMPTS,
    opener=urllib.request.urlopen,
    sleep=time.sleep,
) -> dict[str, object]:
    """Retrieve one trusted registry source with bounded transient retries."""
    url = str(record["official_url"])
    last_error = "retrieval failed"
    max_attempts = max(1, attempts)
    attempt = 0
    for attempt in range(1, max_attempts + 1):
        try:
            request = urllib.request.Request(
                url,
                headers={
                    "User-Agent": USER_AGENT,
                    "Accept": "text/html,application/pdf,application/json,text/plain,*/*;q=0.5",
                },
            )
            with opener(request, timeout=TIMEOUT_SECONDS, context=SSL_CONTEXT) as response:
                final_url = response.geturl()
                final_host = urlparse(final_url).hostname
                if final_host not in ALLOWED_HOSTS:
                    raise ValueError(f"redirected to unapproved host {final_host}")

                content_length = response.headers.get("Content-Length")
                if content_length and int(content_length) > MAX_BYTES:
                    raise ValueError(f"source exceeds {MAX_BYTES} bytes")

                digest = hashlib.sha256()
                received = 0
                prefix = bytearray()
                while True:
                    block = response.read(1024 * 1024)
                    if not block:
                        break
                    received += len(block)
                    if received > MAX_BYTES:
                        raise ValueError(f"source exceeds {MAX_BYTES} bytes")
                    digest.update(block)
                    if len(prefix) < 32:
                        prefix.extend(block[: 32 - len(prefix)])

                content_type = str(response.headers.get("Content-Type", ""))
                content_type = content_type.split(";", 1)[0].strip().lower()
                expected = set(record["expected_content_types"])
                if content_type and content_type not in expected:
                    if not (
                        content_type == "application/octet-stream"
                        and "application/pdf" in expected
                        and bytes(prefix).startswith(b"%PDF-")
                    ):
                        raise ValueError(
                            f"unexpected content type {content_type}; expected {sorted(expected)}"
                        )
                if "application/pdf" in expected and content_type == "application/pdf":
                    if not bytes(prefix).startswith(b"%PDF-"):
                        raise ValueError("official PDF endpoint did not return a PDF")
                return {
                    "ok": True,
                    "http_status": getattr(response, "status", 200),
                    "final_url": final_url,
                    "content_type": content_type or "unreported",
                    "bytes": received,
                    "retrieved_sha256": digest.hexdigest(),
                    "etag": response.headers.get("ETag"),
                    "last_modified": response.headers.get("Last-Modified"),
                    "attempts": attempt,
                }
        except urllib.error.HTTPError as exc:
            last_error = f"HTTPError: HTTP Error {exc.code}: {exc.reason}"
            delay = retry_delay(exc.headers, attempt)
            exc.close()
            if exc.code in RETRYABLE_HTTP_CODES and attempt < max_attempts:
                sleep(delay)
                continue
            break
        except (
            OSError,
            ValueError,
            urllib.error.URLError,
            http.client.HTTPException,
        ) as exc:
            last_error = f"{type(exc).__name__}: {exc}"
            if attempt < max_attempts:
                sleep(retry_delay({}, attempt))
                continue
            break
    return {"ok": False, "error": last_error, "attempts": attempt}


def evaluate(
    records: list[dict[str, object]], as_of: date, *, formal_review: bool, workers: int
) -> list[dict[str, object]]:
    semaphores = {
        host: threading.BoundedSemaphore(DEFAULT_HOST_CONCURRENCY)
        for host in {
            urlparse(str(record["official_url"])).hostname or "" for record in records
        }
    }

    def retrieve(record: dict[str, object]) -> dict[str, object]:
        host = urlparse(str(record["official_url"])).hostname or ""
        with semaphores[host]:
            return download(record)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
        downloads = list(executor.map(retrieve, records))

    results: list[dict[str, object]] = []
    for record, retrieval in zip(records, downloads):
        due = formal_review or parse_iso_date(
            record["next_review"], "next_review", str(record["id"])
        ) <= as_of
        result = {
            "id": record["id"],
            "title": record["title"],
            "jurisdiction": record["jurisdiction"],
            "tax_area": record["tax_area"],
            "authority_weight": record["authority_weight"],
            "official_url": record["official_url"],
            "last_reviewed": record["last_reviewed"],
            "next_review": record["next_review"],
            "reviewer_gate": record["reviewer_gate"],
            "approved_sha256": record["approved_sha256"],
            "review_due": due,
            **retrieval,
        }
        if not retrieval.get("ok"):
            result["status"] = "error"
        elif record["approved_sha256"] is not None and (
            retrieval["retrieved_sha256"] != record["approved_sha256"]
        ):
            result["status"] = "changed"
        elif due:
            result["status"] = "review-due"
        elif record["approved_sha256"] is not None:
            result["status"] = "unchanged"
        else:
            result["status"] = "manual-baseline"
        results.append(result)

    order = {"changed": 0, "error": 1, "review-due": 2, "manual-baseline": 3, "unchanged": 4}
    results.sort(key=lambda item: (order[str(item["status"])], str(item["id"])))
    return results


def write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            newline="\n",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary_name = handle.name
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
        temporary_name = None
    finally:
        if temporary_name:
            Path(temporary_name).unlink(missing_ok=True)


def report_lines(payload: dict[str, object], *, issue: bool = False) -> list[str]:
    counts = payload["counts"]
    lines = [
        "# GH tax-authority review report",
        "",
        f"Checked: {payload['checked_at']}",
        f"As of: {payload['as_of']}",
        "",
        f"- Unchanged approved fingerprints: {counts['unchanged']}",
        f"- Changed approved fingerprints: {counts['changed']}",
        f"- Retrieval errors: {counts['error']}",
        f"- Formal reviews due: {counts['review-due']}",
        f"- Reachable sources awaiting a reviewer-approved fingerprint: {counts['manual-baseline']}",
        "",
        "> This report detects review candidates only. It does not establish that law changed or that a tax position applies.",
        "",
    ]
    actionable = [
        item
        for item in payload["results"]
        if item["status"] in {"changed", "error", "review-due"}
    ]
    shown = actionable[:ISSUE_MAX_ITEMS] if issue else payload["results"]
    for item in shown:
        lines.extend(
            [
                f"## {str(item['status']).upper()} — {item['id']}",
                "",
                f"- Title: {item['title']}",
                f"- Jurisdiction / area: {item['jurisdiction']} / {item['tax_area']}",
                f"- Authority weight: {item['authority_weight']}",
                f"- Official URL: {item['official_url']}",
                f"- Last / next review: {item['last_reviewed']} / {item['next_review']}",
                f"- Retrieved SHA-256: `{item.get('retrieved_sha256', 'unavailable')}`",
                f"- Approved SHA-256: `{item.get('approved_sha256') or 'not yet approved'}`",
                f"- ETag / Last-Modified: `{item.get('etag') or 'none'}` / `{item.get('last_modified') or 'none'}`",
                f"- Error: {item.get('error', 'none')}",
                f"- Reviewer gate: {item['reviewer_gate']}",
                "",
            ]
        )
    if issue and len(actionable) > len(shown):
        lines.extend(
            [
                f"> {len(actionable) - len(shown)} additional actionable records are in the workflow artifact.",
                "",
            ]
        )
    return lines


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--registry",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "manifests/tax_authority_registry.json",
    )
    parser.add_argument(
        "--repository-root", type=Path, default=Path(__file__).resolve().parents[2]
    )
    parser.add_argument("--as-of", type=date.fromisoformat, default=date.today())
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--formal-review", action="store_true")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--skip-sourcebook-check", action="store_true")
    parser.add_argument("--json-report", type=Path, default=Path("tax-authority-review.json"))
    parser.add_argument("--markdown-report", type=Path, default=Path("tax-authority-review.md"))
    parser.add_argument("--issue-report", type=Path)
    parser.add_argument("--workflow-run-url")
    parser.add_argument("--artifact-name")
    args = parser.parse_args()

    if args.issue_report and (not args.workflow_run_url or not args.artifact_name):
        parser.error("--issue-report requires --workflow-run-url and --artifact-name")

    registry = json.loads(args.registry.read_text(encoding="utf-8"))
    records = validate_registry(
        registry,
        args.repository_root,
        check_sourcebooks=not args.skip_sourcebook_check,
    )
    if args.validate_only:
        print(f"Tax authority registry valid: {len(records)} focused official-source records.")
        return 0

    results = evaluate(
        records,
        args.as_of,
        formal_review=args.formal_review,
        workers=args.workers,
    )
    statuses = ("unchanged", "changed", "error", "review-due", "manual-baseline")
    counts = {status: sum(item["status"] == status for item in results) for status in statuses}
    payload = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "as_of": args.as_of.isoformat(),
        "formal_review": args.formal_review,
        "notice": "Review candidates only; no policy, sourcebook, account, election, payment, or return was modified.",
        "counts": counts,
        "results": results,
    }
    write_atomic(args.json_report, json.dumps(payload, indent=2) + "\n")
    write_atomic(args.markdown_report, "\n".join(report_lines(payload)) + "\n")
    if args.issue_report:
        issue_lines = report_lines(payload, issue=True)
        issue_lines.extend(
            [
                f"Full reports: artifact `{args.artifact_name}` on [this workflow run]({args.workflow_run_url}).",
                "",
                "Required disposition: identify effective dates and affected tax years; obtain CPA review; update the dated sourcebook, matrix, `last_reviewed`, `next_review`, and any approved fingerprints through a pull request. Never auto-merge an authority conclusion.",
                "",
            ]
        )
        issue_text = "\n".join(issue_lines)
        if len(issue_text) > ISSUE_MAX_CHARS:
            issue_text = issue_text[: ISSUE_MAX_CHARS - 100].rstrip() + "\n\n> Summary truncated; use the workflow artifact.\n"
        write_atomic(args.issue_report, issue_text)

    print(json.dumps(counts))
    return 2 if counts["changed"] or counts["error"] or counts["review-due"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
