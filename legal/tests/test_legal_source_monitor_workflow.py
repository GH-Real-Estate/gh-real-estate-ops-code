from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "legal-source-monitor.yml"


class LegalSourceMonitorWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")

    def test_failure_publisher_has_explicit_repository_context(self):
        publisher = self.workflow.split("  publish-legal-review:", 1)[1]

        self.assertEqual(3, publisher.count('--repo "$GITHUB_REPOSITORY"'))

    def test_failure_path_has_bounded_summary_and_artifact_fallback(self):
        self.assertIn("--issue-report legal-source-monitor-issue.md", self.workflow)
        self.assertIn("Ensure failure reports exist", self.workflow)
        self.assertIn("if-no-files-found: error", self.workflow)
        self.assertIn("continue-on-error: true", self.workflow)
        self.assertIn("--body-file legal-source-monitor-issue.md", self.workflow)
        self.assertIn('"results":[{"status":"error"', self.workflow)
        self.assertIn(
            "[[ $(wc -c < legal-source-monitor-issue.md) -gt 60000 ]]",
            self.workflow,
        )
        self.assertNotIn(
            "cp legal-source-monitor.md legal-source-monitor-issue.md",
            self.workflow,
        )

    def test_artifact_retention_is_bounded(self):
        self.assertIn("retention-days: 14", self.workflow)
        self.assertNotIn("retention-days: 90", self.workflow)

    def test_issue_publication_is_default_branch_only_and_runs_are_serialized(self):
        self.assertIn(
            "github.ref == format('refs/heads/{0}', github.event.repository.default_branch)",
            self.workflow,
        )
        self.assertIn("group: legal-source-monitor-${{ github.ref }}", self.workflow)
        self.assertNotIn(
            "group: legal-source-monitor-${{ github.event_name }}-${{ github.ref }}",
            self.workflow,
        )


if __name__ == "__main__":
    unittest.main()
