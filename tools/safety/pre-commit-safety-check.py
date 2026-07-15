#!/usr/bin/env python3
"""Fail-closed repository safety scan for public GH Real Estate assets.

This complements GitHub secret scanning. It blocks risky file types and names,
obvious credentials, and common PII before a pull request can merge. It does not
certify that governed PDF contents are free of PII; legal/accounting validators
and human review remain required for those explicitly allowed files.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# The example environment file is exempt only from the risky filename rule. Its
# contents must always be scanned so a pasted production value cannot bypass CI.
FILENAME_ALLOWLIST = {".env.example"}
CONTENT_SCAN_SKIP = {"tools/safety/pre-commit-safety-check.py"}

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
    ".ds",
    ".env",
    ".example",
    ".gitattributes",
    ".gitignore",
    ".gitkeep",
    ".html",
    ".js",
    ".json",
    ".md",
    ".mjs",
    ".py",
    ".sh",
    ".toml",
    ".txt",
    ".urlencoded",
    ".xml",
    ".yaml",
    ".yml",
}

GOVERNED_PDF_PREFIXES = (
    "legal/generated/project-sources/current/",
    "accounting/generated/project-sources/current/",
)

ACCOUNTING_PDF_MANIFEST = "accounting/manifests/sourcebook_release.json"
LEGAL_CHECKSUM_MANIFEST = "legal/manifests/SHA256SUMS"

BLOCKED_BINARY_SUFFIXES = {
    ".7z",
    ".avi",
    ".bak",
    ".bmp",
    ".db",
    ".doc",
    ".docm",
    ".docx",
    ".dump",
    ".gif",
    ".gz",
    ".heic",
    ".jpeg",
    ".jpg",
    ".kdbx",
    ".keystore",
    ".mov",
    ".mp3",
    ".mp4",
    ".p12",
    ".pfx",
    ".png",
    ".psd",
    ".rar",
    ".sqlite",
    ".sqlite3",
    ".tar",
    ".tif",
    ".tiff",
    ".wav",
    ".webp",
    ".xls",
    ".xlsm",
    ".xlsx",
    ".zip",
}

MAX_TEXT_BYTES = 5 * 1024 * 1024
MAX_PDF_BYTES = 25 * 1024 * 1024
MAX_TOTAL_PDF_BYTES = 75 * 1024 * 1024

DANGEROUS_EXACT_NAMES = {
    ".npmrc",
    ".pypirc",
    ".netrc",
    "auth.json",
    "credentials",
    "credentials.json",
    "id_dsa",
    "id_ed25519",
    "id_ecdsa",
    "id_rsa",
    "kubeconfig",
    "service-account.json",
    "terraform.tfstate",
}

DANGEROUS_SUFFIXES = {
    ".jks",
    ".key",
    ".ovpn",
    ".pem",
    ".tfstate",
}

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

PRIVATE_KEY_RE = re.compile(r"-----BEGIN (RSA |DSA |EC |OPENSSH )?PRIVATE KEY-----", re.IGNORECASE)
SECRET_ASSIGNMENT_RE = re.compile(
    r"\b(?P<name>access[_-]?token|api[_-]?key|auth[_-]?token|client[_-]?secret|"
    r"password|private[_-]?key|refresh[_-]?token|secret[_-]?key|"
    r"webhook[_-]?(secret|signing[_-]?key)|zoho_client_secret|zoho_refresh_token)\b"
    r"\s*[:=]\s*['\"]?(?P<value>[^'\"\s,})\]]+)",
    re.IGNORECASE,
)

TOKEN_PATTERNS = [
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{30,}\b")),
    ("AWS access key", re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
    ("Slack token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b")),
    ("Stripe secret key", re.compile(r"\bsk_(?:live|test)_[A-Za-z0-9]{16,}\b")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("Bearer credential", re.compile(r"\bBearer\s+[A-Za-z0-9._~+/-]{24,}={0,2}\b", re.IGNORECASE)),
    ("credentialed URL", re.compile(r"\bhttps?://[^/@\s:]+:[^/@\s]+@", re.IGNORECASE)),
]

SAFE_SECRET_VALUE_PREFIXES = (
    "<",
    "${",
    "$",
    "{{",
    "[",
    "config.",
    "env(",
    "os.environ",
    "paste_",
    "process.env",
    "replace_",
    "runtime",
    "secrets.",
    "settings.",
)

SAFE_SECRET_VALUE_WORDS = {
    "example",
    "sample",
    "changeme",
    "change_me",
    "replace_me",
    "redacted",
    "runtime",
    "placeholder",
    "none",
    "null",
    "undefined",
    "''",
    '""',
}

PUBLIC_LEGAL_TEXT_PREFIXES = (
    "legal/text/current/authorities/",
    "legal/text/current/chunks/",
    "legal/text/current/full/",
)

OPERATIONAL_ID_PREFIXES = (
    "accounting/chart-of-accounts/",
    "src/zoho-books/",
    "src/zoho-crm/integrations/zillow-lead-intake/",
    "src/zoho-payments/",
)
LONG_OPERATIONAL_ID_RE = re.compile(r"\b\d{15,20}\b")

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


def is_safe_secret_reference(value: str) -> bool:
    raw = value.strip().strip("'\"")
    lowered = raw.lower()
    if lowered in SAFE_SECRET_VALUE_WORDS:
        return True
    return any(lowered.startswith(prefix) for prefix in SAFE_SECRET_VALUE_PREFIXES)


def scan_filename(rel: str) -> list[str]:
    if rel in FILENAME_ALLOWLIST:
        return []

    path = Path(rel)
    lowered_name = path.name.lower()
    if lowered_name in DANGEROUS_EXACT_NAMES or path.suffix.lower() in DANGEROUS_SUFFIXES:
        return [f"Credential-bearing filename is prohibited: {rel}"]

    for label, pattern in RISKY_FILE_PATTERNS:
        if pattern.search(rel):
            return [f"Risky filename ({label}): {rel}"]
    return []


def scan_file_policy(rel: str, path: Path) -> tuple[list[str], bool, bool]:
    """Return problems, whether this is an allowed PDF, and whether to scan text."""

    suffix = path.suffix.lower()
    size = path.stat().st_size

    if suffix == ".pdf":
        if not rel.startswith(GOVERNED_PDF_PREFIXES):
            return [f"PDF outside governed source directories is prohibited: {rel}"], False, False
        if size > MAX_PDF_BYTES:
            return [f"Governed PDF exceeds {MAX_PDF_BYTES}-byte limit: {rel}"], False, False
        with path.open("rb") as handle:
            if handle.read(5) != b"%PDF-":
                return [f"File uses .pdf without a PDF signature: {rel}"], False, False
        return [], True, False

    if suffix in BLOCKED_BINARY_SUFFIXES:
        return [f"Unapproved binary/document type {suffix}: {rel}"], False, False

    if size > MAX_TEXT_BYTES:
        return [f"Text or unknown file exceeds {MAX_TEXT_BYTES}-byte limit: {rel}"], False, False

    with path.open("rb") as handle:
        sample = handle.read(min(size, 8192))
    if b"\x00" in sample:
        return [f"Unapproved binary content: {rel}"], False, False
    try:
        sample.decode("utf-8")
    except UnicodeDecodeError:
        return [f"Non-UTF-8 or unapproved binary content: {rel}"], False, False

    return [], False, True


def scan_text(rel: str, text: str) -> list[str]:
    if rel in CONTENT_SCAN_SKIP:
        return []

    problems: list[str] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        if rel.startswith(OPERATIONAL_ID_PREFIXES) and LONG_OPERATIONAL_ID_RE.search(line):
            problems.append(f"long operational identifier in {rel}:{line_no}")

        if PRIVATE_KEY_RE.search(line):
            problems.append(f"private key block in {rel}:{line_no}")

        for label, pattern in TOKEN_PATTERNS:
            if pattern.search(line):
                problems.append(f"{label} in {rel}:{line_no}")

        for match in SECRET_ASSIGNMENT_RE.finditer(line):
            if not is_safe_secret_reference(match.group("value")):
                problems.append(f"secret assignment in {rel}:{line_no}")

        for label, pattern in PII_PATTERNS:
            if label == "non-sample email address" and rel.startswith(PUBLIC_LEGAL_TEXT_PREFIXES):
                continue
            if pattern.search(line):
                problems.append(f"{label} in {rel}:{line_no}")

    return problems


def parse_checksum_manifest(text: str) -> dict[str, str]:
    approved: dict[str, str] = {}
    for line in text.splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})\s+(.+\.pdf)", line.strip(), re.IGNORECASE)
        if match:
            approved[match.group(2).replace("\\", "/")] = match.group(1).lower()
    return approved


def parse_accounting_pdf_manifest(payload: object) -> dict[str, str]:
    if not isinstance(payload, dict) or not isinstance(payload.get("files"), list):
        return {}
    approved: dict[str, str] = {}
    for item in payload["files"]:
        if not isinstance(item, dict):
            continue
        path = item.get("repository_path")
        digest = item.get("sha256")
        if isinstance(path, str) and isinstance(digest, str) and re.fullmatch(r"[0-9a-f]{64}", digest):
            approved[path.replace("\\", "/")] = digest
    return approved


def load_approved_pdf_hashes(root: Path) -> tuple[dict[str, str], list[str]]:
    approved: dict[str, str] = {}
    problems: list[str] = []

    accounting_manifest = root / ACCOUNTING_PDF_MANIFEST
    legal_manifest = root / LEGAL_CHECKSUM_MANIFEST
    try:
        approved.update(
            parse_accounting_pdf_manifest(json.loads(accounting_manifest.read_text(encoding="utf-8")))
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        problems.append(f"Could not load governed PDF manifest {ACCOUNTING_PDF_MANIFEST}: {exc}")
    try:
        approved.update(parse_checksum_manifest(legal_manifest.read_text(encoding="utf-8")))
    except (OSError, UnicodeError) as exc:
        problems.append(f"Could not load governed PDF manifest {LEGAL_CHECKSUM_MANIFEST}: {exc}")

    return approved, problems


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def scan_repository(root: Path = ROOT) -> list[str]:
    global ROOT
    previous_root = ROOT
    ROOT = root
    problems: list[str] = []
    governed_pdf_bytes = 0
    approved_pdf_hashes, manifest_problems = load_approved_pdf_hashes(root)
    problems.extend(manifest_problems)
    try:
        for path in sorted(root.rglob("*")):
            if should_skip(path):
                continue
            if path.is_symlink():
                problems.append(f"Symbolic links are prohibited: {rel_path(path)}")
                continue
            if not path.is_file():
                continue

            rel = rel_path(path)
            problems.extend(scan_filename(rel))

            try:
                policy_problems, allowed_pdf, scan_as_text = scan_file_policy(rel, path)
            except OSError as exc:
                problems.append(f"Could not inspect file {rel}: {exc}")
                continue

            problems.extend(policy_problems)
            if policy_problems:
                continue
            if allowed_pdf:
                governed_pdf_bytes += path.stat().st_size
                expected_hash = approved_pdf_hashes.get(rel)
                if not expected_hash:
                    problems.append(f"Governed PDF is not present in an approved hash manifest: {rel}")
                elif sha256_file(path) != expected_hash:
                    problems.append(f"Governed PDF hash does not match its approved manifest: {rel}")
                continue
            if not scan_as_text:
                continue

            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeError) as exc:
                problems.append(f"Could not read UTF-8 text file {rel}: {exc}")
                continue
            problems.extend(scan_text(rel, text))

        if governed_pdf_bytes > MAX_TOTAL_PDF_BYTES:
            problems.append(
                "Governed PDFs total "
                f"{governed_pdf_bytes} bytes, exceeding {MAX_TOTAL_PDF_BYTES}-byte repository limit"
            )
        return problems
    finally:
        ROOT = previous_root


def main() -> int:
    problems = scan_repository(ROOT)
    if problems:
        print("Safety check found issues:\n")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print("Safety check passed. Still manually verify no PII/secrets are committed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
