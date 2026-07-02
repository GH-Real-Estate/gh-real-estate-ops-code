#!/usr/bin/env python3
"""Repository safety scan for GH Real Estate technical assets.

This is not a replacement for judgment or GitHub secret scanning. It catches
risky filenames, obvious secret assignments, and common PII patterns before a
change is merged or copied into a runtime package.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

ALLOWLISTED_FILES = {
    ".env.example",
    "tools/safety/pre-commit-safety-check.py",
}

SKIP_DIRS = {
    ".git",
    ".pytest_cache",
    "__pycache__",
    ".venv",
    "venv",
    "node_modules",
}

TEXT_SUFFIXES = {
    ".cjs",
    ".css",
    ".csv",
    ".deluge",
    ".env",
    ".example",
    ".html",
    ".js",
    ".json",
    ".md",
    ".mjs",
    ".py",
    ".sh",
    ".toml",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}

# Filename checks focus on documents/exports that are likely to contain live data.
# System names such as src/zoho-payments are allowed.
RISKY_FILE_PATTERNS = [
    ("environment file", re.compile(r"(^|/)\.env($|\.)", re.IGNORECASE)),
    ("pay stub", re.compile(r"pay\s*-?\s*stub|paystub", re.IGNORECASE)),
    ("driver license", re.compile(r"driver.*license", re.IGNORECASE)),
    ("social security", re.compile(r"ssn|social.*security", re.IGNORECASE)),
    ("bank statement", re.compile(r"bank.*statement", re.IGNORECASE)),
    ("ACH detail", re.compile(r"ach.*detail", re.IGNORECASE)),
    ("passport", re.compile(r"passport", re.IGNORECASE)),
    ("immigration document", re.compile(r"green[_ -]?card|immigration", re.IGNORECASE)),
    ("signed lease", re.compile(r"signed.*lease|lease.*\.(pdf|docx)$", re.IGNORECASE)),
    ("tenant export", re.compile(r"tenant.*export", re.IGNORECASE)),
    ("customer export", re.compile(r"customer.*export", re.IGNORECASE)),
    ("payment export", re.compile(r"payment.*export", re.IGNORECASE)),
    ("invoice export", re.compile(r"invoice.*export", re.IGNORECASE)),
    ("ledger export", re.compile(r"ledger.*export", re.IGNORECASE)),
]

SECRET_PATTERNS = [
    (
        "private key block",
        re.compile(r"-----BEGIN (RSA |DSA |EC |OPENSSH )?PRIVATE KEY-----", re.IGNORECASE),
    ),
    (
        "secret assignment",
        re.compile(
            r"\b(client[_-]?secret|zoho_client_secret|refresh[_-]?token|zoho_refresh_token|"
            r"api[_-]?key|private[_-]?key|password|webhook[_-]?(secret|signing[_-]?key))\b"
            r"\s*[:=]\s*['\"]?(?!<|\{|\[|example|sample|changeme|replace_me|redacted|runtime|$)"
            r"[A-Za-z0-9_./+=@:-]{8,}",
            re.IGNORECASE,
        ),
    ),
]

PII_PATTERNS = [
    ("SSN-like value", re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
    (
        "bank account/routing marker",
        re.compile(r"\b(routing|account)\s*(number|no\.?|#)?\s*[:=]\s*\d{4,}\b", re.IGNORECASE),
    ),
    (
        "non-sample email address",
        re.compile(
            r"\b[A-Z0-9._%+-]+@(?!example\.com\b|example\.org\b|test\.invalid\b)"
            r"[A-Z0-9.-]+\.[A-Z]{2,}\b",
            re.IGNORECASE,
        ),
    ),
]


def rel_path(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def should_skip(path: Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts)


def is_text_candidate(path: Path) -> bool:
    if path.suffix.lower() in TEXT_SUFFIXES:
        return True
    return path.name.startswith(".env")


def scan_filename(rel: str) -> list[str]:
    if rel in ALLOWLISTED_FILES:
        return []

    problems: list[str] = []
    for label, pattern in RISKY_FILE_PATTERNS:
        if pattern.search(rel):
            problems.append(f"Risky filename ({label}): {rel}")
            break
    return problems


def scan_text(rel: str, text: str) -> list[str]:
    if rel in ALLOWLISTED_FILES:
        return []

    problems: list[str] = []
    checks = SECRET_PATTERNS + PII_PATTERNS
    for line_no, line in enumerate(text.splitlines(), start=1):
        for label, pattern in checks:
            if pattern.search(line):
                problems.append(f"{label} in {rel}:{line_no}")
    return problems


def main() -> int:
    problems: list[str] = []

    for path in sorted(ROOT.rglob("*")):
        if should_skip(path) or not path.is_file():
            continue

        rel = rel_path(path)
        problems.extend(scan_filename(rel))

        if not is_text_candidate(path):
            continue

        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception as exc:
            problems.append(f"Could not read text file {rel}: {exc}")
            continue

        problems.extend(scan_text(rel, text))

    if problems:
        print("Safety check found issues:\n")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print("Safety check passed. Still manually verify no PII/secrets are committed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
