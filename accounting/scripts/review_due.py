#!/usr/bin/env python3
"""Report FASB topic reviews that are due or approaching.

This script does not retrieve, scrape, interpret, or modify FASB content. It
only enforces the human-review calendar stored in the locator registry.
"""

from __future__ import annotations

import argparse
import json
from datetime import date, datetime, timezone
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--registry",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "manifests/fasb_topic_registry.json",
    )
    parser.add_argument("--as-of", type=date.fromisoformat, default=date.today())
    parser.add_argument("--warning-days", type=int, default=45)
    parser.add_argument("--json-report", type=Path, default=Path("accounting-review-due.json"))
    parser.add_argument("--markdown-report", type=Path, default=Path("accounting-review-due.md"))
    args = parser.parse_args()

    data = json.loads(args.registry.read_text(encoding="utf-8"))
    results: list[dict[str, object]] = []
    for topic in data["topics"]:
        due = date.fromisoformat(topic["next_review"])
        days = (due - args.as_of).days
        if days < 0:
            status = "overdue"
        elif days <= args.warning_days:
            status = "due-soon"
        else:
            status = "current"
        results.append(
            {
                "id": topic["id"],
                "title": topic["title"],
                "classification": topic["classification"],
                "priority": topic["priority"],
                "next_review": topic["next_review"],
                "days_remaining": days,
                "status": status,
            }
        )

    actionable = [item for item in results if item["status"] != "current"]
    actionable.sort(key=lambda item: (int(item["days_remaining"]), str(item["id"])))
    counts = {
        "current": sum(item["status"] == "current" for item in results),
        "due_soon": sum(item["status"] == "due-soon" for item in results),
        "overdue": sum(item["status"] == "overdue" for item in results),
    }
    payload = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "as_of": args.as_of.isoformat(),
        "warning_days": args.warning_days,
        "notice": "Calendar alert only. Review authorized live sources; do not automatically change an accounting conclusion.",
        "counts": counts,
        "actionable": actionable,
    }
    args.json_report.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Accounting authority review calendar",
        "",
        f"As of: {args.as_of.isoformat()}",
        "",
        f"- Current: {counts['current']}",
        f"- Due within {args.warning_days} days: {counts['due_soon']}",
        f"- Overdue: {counts['overdue']}",
        "",
        "> Review authorized live FASB sources. Do not copy Codification text or automatically revise policy.",
        "",
    ]
    for item in actionable:
        lines.extend(
            [
                f"## {str(item['status']).upper()} — {item['id']} {item['title']}",
                "",
                f"- Classification: {item['classification']}",
                f"- Priority: {item['priority']}",
                f"- Review date: {item['next_review']}",
                f"- Days remaining: {item['days_remaining']}",
                "",
            ]
        )
    args.markdown_report.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(counts))
    return 2 if actionable else 0


if __name__ == "__main__":
    raise SystemExit(main())

