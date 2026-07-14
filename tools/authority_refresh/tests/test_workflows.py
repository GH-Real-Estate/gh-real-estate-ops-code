from __future__ import annotations

import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
WORKFLOWS = REPO_ROOT / ".github" / "workflows"


def workflow(name: str) -> str:
    return (WORKFLOWS / name).read_text(encoding="utf-8")


class AuthorityWorkflowContractTests(unittest.TestCase):
    def test_refresh_checks_keep_required_name_and_fail_open_path_gating(self):
        content = workflow("authority-refresh-checks.yml")
        self.assertIn("name: Validate authority refresh controls", content)
        self.assertIn("fetch-depth: 0", content)
        self.assertIn("workflow_dispatch:", content)
        self.assertIn("id: scope", content)
        self.assertIn("continue-on-error: true", content)
        self.assertIn('echo "run_full=true" >> "$GITHUB_OUTPUT"', content)
        self.assertIn("git diff --name-only --no-renames -z", content)
        self.assertIn("authority/*|tools/authority_refresh/*", content)
        self.assertIn("legal/manifests/authority_registry.json", content)
        self.assertIn("accounting/manifests/fasb_topic_registry.json", content)
        self.assertIn("Confirm unrelated pull request", content)
        self.assertEqual(content.count("steps.scope.outputs.run_full != 'false'"), 3)
        self.assertIn("python tools/authority_refresh/validate_system.py", content)
        self.assertIn("python -m unittest discover -s tools/authority_refresh/tests", content)
        self.assertIn("permissions:\n  contents: read", content)
        self.assertIn("timeout-minutes:", content)
        pull_request_section, push_section = content.split("\n  push:\n", maxsplit=1)
        self.assertIn("\n  pull_request:", pull_request_section)
        self.assertNotIn("paths:", pull_request_section)
        self.assertIn("paths:", push_section)

    def test_discovery_is_weekly_manual_and_read_only_until_publish(self):
        content = workflow("authority-discovery.yml")
        self.assertRegex(content, r"cron: ['\"]17 11 \* \* 0['\"]")
        self.assertIn("retention-days: 14", content)
        self.assertNotIn("retention-days: 90", content)
        self.assertIn("workflow_dispatch:", content)
        scan, publisher = content.split("\n  publish:\n", maxsplit=1)
        self.assertIn("\n  scan:\n", scan)
        self.assertIn("permissions:\n      contents: read", scan)
        self.assertNotIn("contents: write", scan)
        self.assertNotIn("issues: write", scan)
        self.assertNotIn("pull-requests: write", scan)
        self.assertIn("needs: scan", publisher)
        self.assertIn("actions: write", publisher)
        self.assertEqual(content.count("actions: write"), 1)
        self.assertIn("contents: write", publisher)
        self.assertIn("issues: write", publisher)
        self.assertIn("pull-requests: write", publisher)

    def test_discovery_publisher_is_default_branch_only_and_candidate_scoped(self):
        content = workflow("authority-discovery.yml")
        self.assertIn(
            "github.ref == format('refs/heads/{0}', github.event.repository.default_branch)",
            content,
        )
        self.assertIn('domain_root="authority/candidates/${DOMAIN}"', content)
        self.assertIn('destination="${domain_root}/latest"', content)
        self.assertIn(
            'archive="${domain_root}/runs/${GITHUB_RUN_ID}-${GITHUB_RUN_ATTEMPT}"',
            content,
        )
        self.assertIn('git checkout -B "$branch" "origin/$branch"', content)
        self.assertIn('git merge --no-edit "origin/${DEFAULT_BRANCH}"', content)
        self.assertIn('[[ "$path" == "${domain_root}/"* ]]', content)
        self.assertIn(
            'git diff --name-only "origin/${DEFAULT_BRANCH}...HEAD"',
            content,
        )
        self.assertIn('git push origin "$branch"', content)
        self.assertIn(
            "--json number,isCrossRepository,headRepositoryOwner,headRefName,baseRefName",
            content,
        )
        self.assertIn('[[ "$cross_repository" == \'false\' ]]', content)
        self.assertIn('[[ "${head_owner,,}" == "${REPOSITORY_OWNER,,}" ]]', content)
        self.assertIn('[[ "$head_ref" == "$branch" ]]', content)
        self.assertIn('[[ "$base_ref" == "$DEFAULT_BRANCH" ]]', content)
        self.assertEqual(content.count('--head "$branch"'), 1)
        self.assertIn("gh workflow run authority-refresh-checks.yml", content)
        self.assertIn("gh workflow run repo-checks.yml", content)
        self.assertIn('--repo "$GITHUB_REPOSITORY"', content)
        self.assertIn("--draft", content)
        self.assertIn("AUTHORITY DISCOVERY DEGRADED", content)
        self.assertIn("if-no-files-found: error", content)
        self.assertIn("write_failure_report()", content)
        self.assertIn("for artifact in candidate.json candidate.md candidate-issue.md", content)
        self.assertIn(
            '"authority-refresh-output/${DOMAIN}-candidate.json") -gt 8388608',
            content,
        )
        self.assertIn(
            '"authority-refresh-output/${DOMAIN}-candidate.md") -gt 1048576',
            content,
        )
        self.assertIn(
            '"authority-refresh-output/${DOMAIN}-candidate-issue.md") -gt 61440',
            content,
        )
        self.assertLess(
            content.index("The candidate JSON exceeds the 8 MiB"),
            content.index('git add "$domain_root"'),
        )
        self.assertIn("The candidate JSON failed domain, status, or SHA-256 validation.", content)
        self.assertEqual(
            content.count('--body-file "authority-refresh-output/${DOMAIN}-candidate-issue.md"'),
            4,
        )
        self.assertNotIn(
            '--body-file "authority-refresh-output/${DOMAIN}-candidate.md"',
            content,
        )
        self.assertNotIn("--force", content)
        self.assertNotIn("git push --delete", content)
        self.assertNotIn("gh pr close", content)
        self.assertNotIn("gh pr merge", content)
        self.assertNotIn("--auto", content)
        self.assertLess(
            content.index('if [[ "$status" == \'current\' ]]'),
            content.index('branch="automation/authority-${DOMAIN}-candidate"'),
        )

    def test_promotion_requires_protected_review_and_bounded_paths(self):
        content = workflow("authority-release-promotion.yml")
        self.assertIn("workflow_dispatch:", content)
        self.assertIn("environment: authority-production", content)
        self.assertIn(
            "github.ref == format('refs/heads/{0}', github.event.repository.default_branch)",
            content,
        )
        self.assertGreaterEqual(
            content.count("PROMOTE_REVIEWED_AUTHORITY_RELEASE"),
            3,
        )
        self.assertIn('validate_path(candidate_raw, "candidates", "candidate")', content)
        self.assertIn('validate_path(approval_raw, "reviews", "approval")', content)
        self.assertIn('candidate_value.relative_to(candidate_runs)', content)
        self.assertIn('re.fullmatch(r"\\d+-\\d+", candidate_relative.parts[0])', content)
        self.assertIn('candidate_relative.parts[1] != "candidate.json"', content)
        self.assertIn('candidate.get("run_id") != candidate_relative.parts[0]', content)
        self.assertIn('path.resolve(strict=True).relative_to(expected_root)', content)
        self.assertIn('release.get("domain") != domain', content)
        self.assertIn('release_dir.resolve(strict=True).relative_to(release_root)', content)
        self.assertIn('actual != expected or any(path.is_symlink()', content)
        self.assertIn('"${release_dir}/approval.json"', content)
        self.assertIn('"${release_dir}/candidate.json"', content)
        self.assertIn('"${release_dir}/release.json"', content)
        self.assertIn('"${release_dir}/validation-context.json"', content)
        self.assertIn('"authority/snapshots/${DOMAIN}.json"', content)
        self.assertGreaterEqual(
            content.count('--source-revision "$(git rev-parse HEAD)"'),
            2,
        )
        self.assertIn("git status --porcelain --untracked-files=all", content)
        self.assertIn('git diff --cached --name-only | sort', content)
        self.assertIn('git diff --name-only', content)
        self.assertIn('git ls-files --others --exclude-standard', content)
        self.assertNotIn('git add "authority/releases"', content)
        self.assertNotIn('authority/releases/*|', content)
        self.assertNotIn('--candidate "${{ inputs.candidate_path }}"', content)
        self.assertNotIn('--approval "${{ inputs.approval_path }}"', content)
        self.assertNotIn('--release-date "${{ inputs.release_date }}"', content)
        self.assertRegex(
            content,
            r'gh pr create \\\n\s+--repo "\$GITHUB_REPOSITORY"',
        )
        self.assertIn("actions: write", content)
        self.assertEqual(content.count("actions: write"), 1)
        self.assertIn("Block unresolved authority pull requests", content)
        self.assertIn('gh pr list \\', content)
        self.assertIn(
            "--json number,headRefName,baseRefName,isCrossRepository,headRepositoryOwner,url",
            content,
        )
        self.assertIn(
            '[[ "${head_owner,,}" != "${REPOSITORY_OWNER,,}" ]]',
            content,
        )
        self.assertIn(
            '[[ "$head_ref" == "automation/authority-${DOMAIN}-candidate" ]]',
            content,
        )
        self.assertIn('[[ "$base_ref" == "$DEFAULT_BRANCH" ]]', content)
        self.assertIn('"automation/authority-promotion-${DOMAIN}-"*', content)
        self.assertLess(
            content.index("Block unresolved authority pull requests"),
            content.index("Generate immutable release evidence"),
        )
        self.assertIn("gh workflow run authority-refresh-checks.yml", content)
        self.assertIn("gh workflow run repo-checks.yml", content)
        self.assertIn("--draft", content)
        self.assertNotIn("gh pr merge", content)
        self.assertNotIn("--auto", content)

    def test_accounting_review_separates_scan_and_issue_permissions(self):
        content = workflow("accounting-authority-review.yml")
        scan, publisher = content.split("\n  publish-accounting-review:\n", maxsplit=1)
        self.assertNotIn("issues: write", scan)
        self.assertIn("issues: write", publisher)
        self.assertIn("needs: review-calendar", publisher)
        self.assertIn(
            "github.ref == format('refs/heads/{0}', github.event.repository.default_branch)",
            publisher,
        )
        self.assertIn('--repo "$GITHUB_REPOSITORY"', publisher)
        self.assertRegex(
            publisher,
            r"actions/download-artifact@[0-9a-f]{40}\s+# v[0-9]+\.[0-9]+\.[0-9]+",
        )
        self.assertIn("if-no-files-found: error", scan)
        self.assertRegex(content, r"timeout-minutes: 10")
        self.assertIn("retention-days: 14", content)
        self.assertNotIn("retention-days: 90", content)

    def test_authority_workflows_do_not_contain_automatic_merge_commands(self):
        for name in (
            "authority-refresh-checks.yml",
            "authority-discovery.yml",
            "authority-release-promotion.yml",
        ):
            with self.subTest(workflow=name):
                content = workflow(name).lower()
                self.assertNotIn("gh pr merge", content)
                self.assertNotIn("enablepullrequestautomerge", content)
                self.assertIsNone(re.search(r"\bauto-?merge\b", content))

    def test_repo_checks_are_main_only_and_fail_open_by_changed_path(self):
        content = workflow("repo-checks.yml")
        self.assertIn("workflow_dispatch:", content)
        self.assertIn("permissions:\n  contents: read", content)
        self.assertNotIn("actions: write", content)
        self.assertNotIn("codex/**", content)
        self.assertIn("name: Safety scan", content)
        self.assertIn("name: Zillow lead intake checks", content)
        self.assertIn("name: Returned fee webhook checks", content)
        self.assertIn("fetch-depth: 0", content)
        self.assertIn("continue-on-error: true", content)
        self.assertIn("'run_zillow=true' 'run_returned=true'", content)
        self.assertIn("git diff --name-only --no-renames -z", content)
        self.assertIn("src/zoho-crm/integrations/zillow-lead-intake/*", content)
        self.assertIn("src/zoho-payments/webhooks/returned-payment-fee/*", content)
        self.assertEqual(content.count("needs: safety-scan"), 2)
        self.assertIn(
            "always() && !cancelled() && needs.safety-scan.outputs.run_zillow != 'false'",
            content,
        )
        self.assertIn(
            "always() && !cancelled() && needs.safety-scan.outputs.run_returned != 'false'",
            content,
        )

    def test_official_actions_are_pinned_to_immutable_commits(self):
        mutable_reference = re.compile(r"uses:\s+actions/[^@\s]+@(?![0-9a-f]{40}(?:\s|$))")
        for path in sorted(WORKFLOWS.glob("*.yml")):
            with self.subTest(workflow=path.name):
                self.assertIsNone(mutable_reference.search(path.read_text(encoding="utf-8")))


if __name__ == "__main__":
    unittest.main()
