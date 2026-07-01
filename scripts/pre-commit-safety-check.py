#!/usr/bin/env python3
"""Lightweight local safety scan before committing.

This is not a replacement for judgment or GitHub secret scanning. It catches
obvious risky filenames and secret-like strings in staged/working files.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RISKY_NAME_PATTERNS = [
    r"tenant", r"tenants", r"payment", r"payments", r"ledger", r"paystub",
    r"driver", r"license", r"ssn", r"social", r"bank", r"ach", r"passport",
    r"green_card", r"immigration", r"signed", r"lease.*\.pdf", r"lease.*\.docx",
]
SECRET_PATTERNS = [
    r"client_secret\s*[:=]",
    r"refresh_token\s*[:=]",
    r"api[_-]?key\s*[:=]",
    r"private[_-]?key\s*[:=]",
    r"password\s*[:=]",
    r"webhook[_-]?secret\s*[:=]",
]
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
        if not rel.startswith("samples/"):
            for pattern in RISKY_NAME_PATTERNS:
                if re.search(pattern, lower):
                    problems.append(f"Risky filename outside samples/: {rel}")
                    break
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for pattern in SECRET_PATTERNS:
            if re.search(pattern, text, flags=re.IGNORECASE):
                if ".env.example" not in rel:
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
