#!/usr/bin/env python3
"""Enforce the repository's fail-closed GitHub Actions security policy."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_DIR = ROOT / ".github" / "workflows"
FULL_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
USES_RE = re.compile(r"^\s*(?:-\s*)?uses:\s*([^#\s]+)", re.MULTILINE)


def job_blocks(text: str) -> list[tuple[str, str]]:
    """Return top-level job blocks without requiring a YAML dependency."""

    lines = text.splitlines()
    try:
        jobs_index = next(index for index, line in enumerate(lines) if line == "jobs:")
    except StopIteration:
        return []

    starts: list[tuple[int, str]] = []
    for index in range(jobs_index + 1, len(lines)):
        match = re.fullmatch(r"  ([A-Za-z0-9_-]+):", lines[index])
        if match:
            starts.append((index, match.group(1)))

    blocks: list[tuple[str, str]] = []
    for position, (start, name) in enumerate(starts):
        end = starts[position + 1][0] if position + 1 < len(starts) else len(lines)
        blocks.append((name, "\n".join(lines[start:end])))
    return blocks


def validate_workflow(path: Path, text: str) -> list[str]:
    problems: list[str] = []

    if not re.search(r"(?m)^permissions:\s*\n(?:(?:  [^\n]*\n)*)  contents:\s*read\s*$", text):
        problems.append("top-level permissions must include contents: read")

    forbidden = {
        "pull_request_target is prohibited": r"(?m)^\s*pull_request_target\s*:",
        "self-hosted runners are prohibited": r"\bself-hosted\b",
        "OIDC write permission is prohibited": r"(?m)^\s*id-token:\s*write\s*$",
        "write-all permissions are prohibited": r"(?m)^\s*(?:permissions:\s*)?write-all\s*$",
        "floating latest runner labels are prohibited": r"(?m)^\s*runs-on:\s*[^#\n]*-latest\s*$",
        "Node.js 18 is prohibited": r"(?m)^\s*node-version:\s*['\"]?18(?:\.x)?['\"]?\s*$",
    }
    for message, pattern in forbidden.items():
        if re.search(pattern, text, re.IGNORECASE):
            problems.append(message)

    for reference in USES_RE.findall(text):
        if reference.startswith("./"):
            continue
        if "@" not in reference:
            problems.append(f"action reference is not pinned: {reference}")
            continue
        action, revision = reference.rsplit("@", 1)
        if not action or not FULL_SHA_RE.fullmatch(revision):
            problems.append(f"action reference must use a full commit SHA: {reference}")

    for job_name, block in job_blocks(text):
        checkout_count = block.count("actions/checkout@")
        if not checkout_count or re.search(r"(?m)^\s{6}contents:\s*write\s*$", block):
            continue
        hardened_count = len(re.findall(r"(?m)^\s+persist-credentials:\s*false\s*$", block))
        if hardened_count < checkout_count:
            problems.append(
                f"read-only job {job_name} must set persist-credentials: false on every checkout"
            )

    return [f"{path.as_posix()}: {problem}" for problem in problems]


def validate_repository(root: Path = ROOT) -> list[str]:
    workflow_dir = root / ".github" / "workflows"
    problems: list[str] = []
    for path in sorted((*workflow_dir.glob("*.yml"), *workflow_dir.glob("*.yaml"))):
        text = path.read_text(encoding="utf-8")
        problems.extend(validate_workflow(path.relative_to(root), text))
    if not list(workflow_dir.glob("*.yml")) and not list(workflow_dir.glob("*.yaml")):
        problems.append("No GitHub Actions workflows were found")
    return problems


def main() -> int:
    problems = validate_repository()
    if problems:
        print("Workflow security policy violations:\n")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print("Workflow security policy passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
