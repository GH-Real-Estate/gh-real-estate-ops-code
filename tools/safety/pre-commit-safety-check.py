#!/usr/bin/env python3
"""Lightweight local safety scan before committing.

This is not a replacement for judgment or GitHub secret scanning. It catches
obvious risky filenames and secret-like strings in working files.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Filename checks focus on documents/exports that are likely to contain live data.
# System names such as src/zoho-payments are allowed.
RISKY_FILE_PATTERNS = [
    r"paystub",
    r"driver.*license",
    r"ssn",
    r"social.*security",
    r"bank.*statement",
    r"ach.*detail",
    r"passport",
    r"green_card",
    r"immigration",
    r"signed.*lease",
    r"lease.*\.pdf",
    r"lease.*\.docx",
    r"tenant.*export",
    r"customer.*export",
    r"payment.*export",
    r"invoice.*export",
    r"ledger.*export",
]

SECRET_PATTERNS = [
    r"client_secret\s*[:=]",
    r"refresh_token\s*[:=]",
    r"api[_-]?key\s*[:=]",
    r"private[_-]?key\s*[:=]",
    r"password\s*[:=]",
    r"webhook[_-]?secret\s*[:=]",
]

ALLOWLISTED_FILES = {
    ".env.example",
    "tools/safety/pre-commit-safety-check.py",
}

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv"}


def should_skip(path: Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts)


def main() -> int:
    problems: list[str] = []

    for path in ROOT.rglob("*"):
        if should_skip(path) or not path.is_file():
            continue

        rel = path.relative_to(ROOT).as_posix()
        lower = rel.lower()

        for pattern in RISKY_FILE_PATTERNS:
            if re.search(pattern, lower):
                problems.append(f"Risky filename: {rel}")
                break

        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        if rel not in ALLOWLISTED_FILES:
            for pattern in SECRET_PATTERNS:
                if re.search(pattern, text, flags=re.IGNORECASE):
                    problems.append(f"Possible secret pattern in {rel}: {pattern}")

    if problems:
        print("Safety check found issues:\n")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print("Safety check passed. Still manually verify no PII/secrets are committed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
