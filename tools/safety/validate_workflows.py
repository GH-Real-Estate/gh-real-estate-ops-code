#!/usr/bin/env python3
"""Enforce the repository's fail-closed GitHub Actions security policy."""

from __future__ import annotations

import re
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[2]
FULL_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
NODE_18_RE = re.compile(r"^18(?:\.x)?$", re.IGNORECASE)
ALLOWED_ACTION_OWNERS = {"actions", "github"}

# Write permissions are denied unless the exact workflow and job are listed.
# This keeps a syntactically valid workflow edit from silently expanding the
# repository token's authority.
WRITE_PERMISSION_ALLOWLIST: dict[str, dict[str, frozenset[str]]] = {
    ".github/workflows/accounting-authority-review.yml": {
        "publish-accounting-review": frozenset({"issues"}),
    },
    ".github/workflows/authority-discovery.yml": {
        "publish": frozenset({"actions", "contents", "issues", "pull-requests"}),
    },
    ".github/workflows/authority-release-promotion.yml": {
        "promote-reviewed-evidence": frozenset(
            {"actions", "contents", "pull-requests"}
        ),
    },
    ".github/workflows/ci-failure-response.yml": {
        "incident": frozenset({"issues"}),
    },
    ".github/workflows/legal-source-monitor.yml": {
        "publish-legal-review": frozenset({"issues"}),
    },
    ".github/workflows/security-checks.yml": {
        "codeql": frozenset({"security-events"}),
    },
}


class GitHubActionsLoader(yaml.SafeLoader):
    """Safe YAML loader with YAML 1.2 booleans and duplicate-key rejection."""


# PyYAML defaults to YAML 1.1, where the GitHub key `on` becomes boolean True.
# Copy the resolver table, remove YAML 1.1 booleans, and restore true/false only.
GitHubActionsLoader.yaml_implicit_resolvers = {
    key: list(resolvers)
    for key, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}
for first_char, resolvers in GitHubActionsLoader.yaml_implicit_resolvers.items():
    GitHubActionsLoader.yaml_implicit_resolvers[first_char] = [
        resolver
        for resolver in resolvers
        if resolver[0] != "tag:yaml.org,2002:bool"
    ]
GitHubActionsLoader.add_implicit_resolver(
    "tag:yaml.org,2002:bool",
    re.compile(r"^(?:true|false)$", re.IGNORECASE),
    list("tTfF"),
)


def _construct_unique_mapping(
    loader: GitHubActionsLoader, node: yaml.MappingNode, deep: bool = False
) -> dict[Any, Any]:
    loader.flatten_mapping(node)
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"duplicate key: {key!r}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


GitHubActionsLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


def _lower(value: object) -> str:
    return str(value).strip().lower()


def _trigger_names(value: object) -> set[str]:
    if isinstance(value, Mapping):
        return {_lower(key) for key in value}
    if isinstance(value, list):
        return {_lower(item) for item in value}
    if value is None:
        return set()
    return {_lower(value)}


def _permissions(value: object) -> dict[str, str] | None:
    if not isinstance(value, Mapping):
        return None
    return {_lower(key): _lower(permission) for key, permission in value.items()}


def _validate_action_reference(reference: object, context: str) -> list[str]:
    if not isinstance(reference, str) or not reference.strip():
        return [f"{context} action reference must be a non-empty string"]
    reference = reference.strip()
    if reference.startswith("./"):
        return []
    if "@" not in reference:
        return [f"{context} action reference is not pinned: {reference}"]
    action, revision = reference.rsplit("@", 1)
    if not action or not FULL_SHA_RE.fullmatch(revision):
        return [f"{context} action reference must use a full commit SHA: {reference}"]
    owner = action.split("/", 1)[0].lower()
    if owner not in ALLOWED_ACTION_OWNERS:
        return [f"{context} action owner is not allowlisted: {owner}"]
    return []


def _persist_credentials_disabled(value: object) -> bool:
    return value is False or (isinstance(value, str) and value.lower() == "false")


def validate_workflow(path: Path, text: str) -> list[str]:
    rel = path.as_posix()
    problems: list[str] = []
    try:
        document = yaml.load(text, Loader=GitHubActionsLoader)
    except yaml.YAMLError as exc:
        return [f"{rel}: workflow YAML is invalid or ambiguous: {exc}"]

    if not isinstance(document, Mapping):
        return [f"{rel}: workflow must be a YAML mapping"]

    top_permissions_raw = document.get("permissions")
    top_permissions = _permissions(top_permissions_raw)
    if top_permissions is None or top_permissions.get("contents") != "read":
        problems.append("top-level permissions must include contents: read")
    if _lower(top_permissions_raw) == "write-all":
        problems.append("write-all permissions are prohibited")
    if top_permissions:
        for name, value in top_permissions.items():
            if value == "write":
                problems.append(f"top-level {name}: write permission is prohibited")

    if "pull_request_target" in _trigger_names(document.get("on")):
        problems.append("pull_request_target is prohibited")

    jobs = document.get("jobs")
    if not isinstance(jobs, Mapping) or not jobs:
        problems.append("workflow must define at least one job")
        return [f"{rel}: {problem}" for problem in problems]

    allowed_jobs = WRITE_PERMISSION_ALLOWLIST.get(rel, {})
    for raw_job_name, raw_job in jobs.items():
        job_name = str(raw_job_name)
        if not isinstance(raw_job, Mapping):
            problems.append(f"job {job_name} must be a mapping")
            continue

        if raw_job.get("runs-on") != "ubuntu-24.04":
            problems.append(
                f"job {job_name} runner must be exactly ubuntu-24.04"
            )

        job_permissions_raw = raw_job.get("permissions", top_permissions_raw)
        job_permissions = _permissions(job_permissions_raw)
        if _lower(job_permissions_raw) == "write-all":
            problems.append(f"job {job_name} uses prohibited write-all permissions")
            job_permissions = {}
        elif job_permissions is None:
            problems.append(f"job {job_name} permissions must be an explicit mapping")
            job_permissions = {}

        allowed_writes = allowed_jobs.get(job_name, frozenset())
        for name, value in job_permissions.items():
            if name == "id-token" and value == "write":
                problems.append(f"job {job_name} OIDC write permission is prohibited")
            elif value == "write" and name not in allowed_writes:
                problems.append(
                    f"job {job_name} {name}: write permission is not allowlisted"
                )

        job_reference = raw_job.get("uses")
        if job_reference is not None:
            problems.extend(
                _validate_action_reference(job_reference, f"job {job_name}")
            )

        steps = raw_job.get("steps", [])
        if not isinstance(steps, list):
            problems.append(f"job {job_name} steps must be a list")
            continue
        for index, step in enumerate(steps, start=1):
            if not isinstance(step, Mapping):
                problems.append(f"job {job_name} step {index} must be a mapping")
                continue
            reference = step.get("uses")
            if reference is not None:
                problems.extend(
                    _validate_action_reference(
                        reference, f"job {job_name} step {index}"
                    )
                )

            step_with = step.get("with", {})
            if isinstance(step_with, Mapping):
                node_version = step_with.get("node-version")
                if node_version is not None and NODE_18_RE.fullmatch(
                    str(node_version).strip()
                ):
                    problems.append(f"job {job_name} Node.js 18 is prohibited")

            if isinstance(reference, str) and reference.lower().startswith(
                "actions/checkout@"
            ):
                contents_write = job_permissions.get("contents") == "write"
                persist = step_with.get("persist-credentials") if isinstance(
                    step_with, Mapping
                ) else None
                if not contents_write and not _persist_credentials_disabled(persist):
                    problems.append(
                        f"read-only job {job_name} step {index} must set "
                        "persist-credentials: false"
                    )

    return [f"{rel}: {problem}" for problem in problems]


def validate_repository(root: Path = ROOT) -> list[str]:
    workflow_dir = root / ".github" / "workflows"
    paths = sorted((*workflow_dir.glob("*.yml"), *workflow_dir.glob("*.yaml")))
    if not paths:
        return ["No GitHub Actions workflows were found"]
    problems: list[str] = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        problems.extend(validate_workflow(path.relative_to(root), text))
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
