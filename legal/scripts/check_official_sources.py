#!/usr/bin/env python3
"""Compare approved legal-source hashes with retrievable official URLs.

This monitor only reports review candidates. A hash change is not proof that
operative law changed, and the script never modifies the approved release.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import ssl
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


USER_AGENT = "GH-Real-Estate-Legal-Monitor/1.0"
MAX_BYTES = 25 * 1024 * 1024
TIMEOUT = 60


def check(record: dict[str, object]) -> dict[str, object]:
    url = str(record["official_url"])
    result = {
        "citation": record.get("citation"),
        "title": record.get("title"),
        "url": url,
        "approved_sha256": record.get("sha256"),
        "bundle": record.get("bundle_filename"),
    }
    try:
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        context = ssl.create_default_context()
        with urllib.request.urlopen(request, timeout=TIMEOUT, context=context) as response:
            content_length = response.headers.get("Content-Length")
            if content_length and int(content_length) > MAX_BYTES:
                raise ValueError(f"source exceeds {MAX_BYTES} bytes")
            digest = hashlib.sha256()
            received = 0
            while True:
                block = response.read(1024 * 1024)
                if not block:
                    break
                received += len(block)
                if received > MAX_BYTES:
                    raise ValueError(f"source exceeds {MAX_BYTES} bytes")
                digest.update(block)
        result["retrieved_sha256"] = digest.hexdigest()
        result["bytes"] = received
        result["status"] = (
            "unchanged" if result["retrieved_sha256"] == result["approved_sha256"] else "changed"
        )
    except (OSError, ValueError, urllib.error.URLError) as exc:
        result["status"] = "error"
        result["error"] = f"{type(exc).__name__}: {exc}"
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--registry",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "manifests/authority_registry.json",
    )
    parser.add_argument("--json-report", type=Path, default=Path("legal-source-monitor.json"))
    parser.add_argument("--markdown-report", type=Path, default=Path("legal-source-monitor.md"))
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()

    registry = json.loads(args.registry.read_text(encoding="utf-8"))
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        results = list(executor.map(check, registry))

    results.sort(key=lambda item: (str(item.get("status")), str(item.get("citation"))))
    counts = {status: sum(item["status"] == status for item in results) for status in ("unchanged", "changed", "error")}
    payload = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "notice": "Review candidates only; no source was promoted or modified.",
        "counts": counts,
        "results": results,
    }
    args.json_report.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    actionable = [item for item in results if item["status"] != "unchanged"]
    lines = [
        "# Legal source monitor report",
        "",
        f"Checked: {payload['checked_at']}",
        "",
        f"- Unchanged: {counts['unchanged']}",
        f"- Changed hashes: {counts['changed']}",
        f"- Retrieval errors: {counts['error']}",
        "",
        "> LEGAL REVIEW REQUIRED: a hash change or retrieval error does not establish that law changed.",
        "",
    ]
    for item in actionable:
        lines.extend(
            [
                f"## {item['status'].upper()} — {item.get('citation')}",
                "",
                f"- Title: {item.get('title')}",
                f"- Bundle: `{item.get('bundle')}`",
                f"- Official URL: {item.get('url')}",
                f"- Approved SHA-256: `{item.get('approved_sha256')}`",
                f"- Retrieved SHA-256: `{item.get('retrieved_sha256', 'unavailable')}`",
                f"- Error: {item.get('error', 'none')}",
                "",
            ]
        )
    args.markdown_report.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(counts))
    return 2 if actionable else 0


if __name__ == "__main__":
    raise SystemExit(main())
