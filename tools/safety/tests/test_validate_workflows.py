from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "validate_workflows.py"
SPEC = importlib.util.spec_from_file_location("validate_workflows", SCRIPT)
assert SPEC and SPEC.loader
validate_workflows = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validate_workflows)


def workflow(job: str) -> str:
    return f"""name: Test

on:
  pull_request:

permissions:
  contents: read

jobs:
{job}
"""


class WorkflowPolicyTests(unittest.TestCase):
    path = Path(".github/workflows/test.yml")

    def test_hardened_read_only_job_passes(self) -> None:
        text = workflow(
            """  test:
    runs-on: ubuntu-24.04
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0
        with:
          persist-credentials: false"""
        )
        self.assertEqual([], validate_workflows.validate_workflow(self.path, text))

    def test_floating_action_reference_is_blocked(self) -> None:
        text = workflow(
            """  test:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@main
        with:
          persist-credentials: false"""
        )
        problems = validate_workflows.validate_workflow(self.path, text)
        self.assertTrue(any("full commit SHA" in problem for problem in problems))

    def test_dangerous_triggers_permissions_and_runners_are_blocked(self) -> None:
        text = workflow(
            """  test:
    runs-on: self-hosted
    permissions:
      id-token: write
    steps:
      - run: true"""
        ).replace("  pull_request:\n", "  pull_request_target:\n")
        problems = validate_workflows.validate_workflow(self.path, text)
        self.assertTrue(any("pull_request_target" in problem for problem in problems))
        self.assertTrue(any("self-hosted" in problem for problem in problems))
        self.assertTrue(any("OIDC" in problem for problem in problems))

    def test_read_only_checkout_must_drop_credentials(self) -> None:
        text = workflow(
            """  test:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0"""
        )
        problems = validate_workflows.validate_workflow(self.path, text)
        self.assertTrue(any("persist-credentials" in problem for problem in problems))

    def test_write_publisher_checkout_is_exempt(self) -> None:
        text = workflow(
            """  publish:
    runs-on: ubuntu-24.04
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0"""
        )
        self.assertEqual([], validate_workflows.validate_workflow(self.path, text))


if __name__ == "__main__":
    unittest.main()
