from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "validate_workflows.py"
SPEC = importlib.util.spec_from_file_location("validate_workflows", SCRIPT)
assert SPEC and SPEC.loader
validate_workflows = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validate_workflows)


CHECKOUT = "actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0"


def workflow(job: str, trigger: str = "pull_request") -> str:
    return f"""name: Test

on:
  {trigger}:

permissions:
  contents: read

jobs:
{job}
"""


class WorkflowPolicyTests(unittest.TestCase):
    path = Path(".github/workflows/test.yml")

    def test_hardened_read_only_job_passes(self) -> None:
        text = workflow(
            f"""  test:
    runs-on: ubuntu-24.04
    timeout-minutes: 5
    steps:
      - uses: {CHECKOUT}
        with:
          persist-credentials: false"""
        )
        self.assertEqual([], validate_workflows.validate_workflow(self.path, text))

    def test_floating_and_third_party_actions_are_blocked(self) -> None:
        floating = workflow(
            """  test:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@main
        with:
          persist-credentials: false"""
        )
        third_party = floating.replace(
            "actions/checkout@main",
            "vendor/action@0123456789012345678901234567890123456789",
        )
        self.assertTrue(
            any(
                "full commit SHA" in problem
                for problem in validate_workflows.validate_workflow(
                    self.path, floating
                )
            )
        )
        self.assertTrue(
            any(
                "owner is not allowlisted" in problem
                for problem in validate_workflows.validate_workflow(
                    self.path, third_party
                )
            )
        )

    def test_quoted_trigger_inline_permissions_and_runner_are_blocked(self) -> None:
        text = workflow(
            """  test:
    runs-on: self-hosted
    permissions: { id-token: write }
    steps:
      - run: true""",
            '"pull_request_target"',
        )
        problems = validate_workflows.validate_workflow(self.path, text)
        self.assertTrue(any("pull_request_target" in problem for problem in problems))
        self.assertTrue(any("runner must be exactly" in problem for problem in problems))
        self.assertTrue(any("OIDC" in problem for problem in problems))

    def test_every_read_only_checkout_must_drop_credentials(self) -> None:
        text = workflow(
            f"""  test:
    runs-on: ubuntu-24.04
    steps:
      - uses: {CHECKOUT}
        with:
          persist-credentials: false
      - uses: {CHECKOUT}"""
        )
        problems = validate_workflows.validate_workflow(self.path, text)
        self.assertTrue(any("step 2" in problem for problem in problems))

    def test_allowlisted_write_publisher_can_retain_checkout_credentials(self) -> None:
        text = workflow(
            f"""  publish:
    runs-on: ubuntu-24.04
    permissions:
      contents: write
    steps:
      - uses: {CHECKOUT}"""
        )
        path = Path(".github/workflows/authority-discovery.yml")
        self.assertEqual([], validate_workflows.validate_workflow(path, text))

    def test_unlisted_write_permission_is_blocked(self) -> None:
        text = workflow(
            """  test:
    runs-on: ubuntu-24.04
    permissions:
      contents: write
    steps:
      - run: true"""
        )
        problems = validate_workflows.validate_workflow(self.path, text)
        self.assertTrue(any("write permission is not allowlisted" in p for p in problems))

    def test_node_18_and_duplicate_keys_are_blocked(self) -> None:
        node_18 = workflow(
            """  test:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/setup-node@820762786026740c76f36085b0efc47a31fe5020
        with:
          node-version: 18"""
        )
        duplicate = node_18.replace(
            "    runs-on: ubuntu-24.04\n",
            "    runs-on: ubuntu-24.04\n    runs-on: ubuntu-24.04\n",
        )
        self.assertTrue(
            any(
                "Node.js 18" in problem
                for problem in validate_workflows.validate_workflow(
                    self.path, node_18
                )
            )
        )
        self.assertTrue(
            any(
                "duplicate key" in problem
                for problem in validate_workflows.validate_workflow(
                    self.path, duplicate
                )
            )
        )


if __name__ == "__main__":
    unittest.main()
