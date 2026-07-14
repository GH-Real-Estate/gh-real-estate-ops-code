from __future__ import annotations

import contextlib
import io
import json
import unittest
from pathlib import Path

from tools.authority_refresh import core, validate_system
from test_support import workspace_temp_directory


def write_text(root: Path, relative: str, value: str = "fixture\n") -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def write_json(root: Path, relative: str, value: object) -> None:
    write_text(root, relative, json.dumps(value, indent=2) + "\n")


def read_json(root: Path, relative: str) -> object:
    return json.loads((root / relative).read_text(encoding="utf-8"))


def write_authority_release(
    root: Path,
    *,
    domain: str,
    approved_at: str,
    run_id: str,
    baseline_snapshot: dict | None,
) -> dict:
    candidate = {
        "schema_version": "1.0",
        "domain": domain,
        "generated_at": f"{approved_at}T00:00:00+00:00",
        "run_id": run_id,
        "status": "review_required",
        "notice": "Synthetic immutable release-chain fixture.",
        "approved_baseline": {
            "path": f"authority/snapshots/{domain}.json",
            "missing": baseline_snapshot is None,
            "sha256": None if baseline_snapshot is None else core.sha256_json(baseline_snapshot),
        },
        "counts": {},
        "source_results": [],
        "changes": [],
        "potential_impacts": [],
        "items": [{"item_id": f"{domain}-{run_id}"}],
    }
    candidate["candidate_sha256"] = core.sha256_json(candidate)
    approval = {
        "schema_version": "1.0",
        "domain": domain,
        "candidate_sha256": candidate["candidate_sha256"],
        "approvals": [],
        "change_resolutions": [],
        "impact_resolutions": [],
    }
    release_id = f"{approved_at}-{domain}-{candidate['candidate_sha256'][:12]}"
    release = {
        "schema_version": "1.0",
        "release_id": release_id,
        "domain": domain,
        "candidate_sha256": candidate["candidate_sha256"],
        "candidate_generated_at": candidate["generated_at"],
        "approved_at": approved_at,
        "approval": approval,
        "notice": "Synthetic release-chain fixture.",
    }
    snapshot = {
        "schema_version": "1.0",
        "domain": domain,
        "release_id": release_id,
        "approved_at": approved_at,
        "candidate_sha256": candidate["candidate_sha256"],
        "items": candidate["items"],
    }
    directory = f"authority/releases/{release_id}"
    write_json(root, f"{directory}/candidate.json", candidate)
    write_json(root, f"{directory}/approval.json", approval)
    write_json(root, f"{directory}/release.json", release)
    write_json(root, f"authority/snapshots/{domain}.json", snapshot)
    return snapshot


def source(
    source_id: str,
    *,
    publisher: str,
    host: str,
    storage_policy: str = "metadata-only",
    path: str = "index",
) -> dict[str, object]:
    return {
        "source_id": source_id,
        "publisher": publisher,
        "jurisdiction": "United States",
        "authority_type": "official-publication-notice",
        "discovery_url": f"https://{host}/{path}",
        "adapter": "fixture_adapter",
        "storage_policy": storage_policy,
        "cadence": "daily",
        "critical": False,
        "allowed_hosts": [host],
        "minimum_items": 2,
    }


def build_valid_workspace(root: Path) -> None:
    legal_sources = [
        source(
            f"legal-source-{index:02d}",
            publisher="Official Legal Publisher",
            host="official.example.gov",
            path=f"legal/{index}",
        )
        for index in range(13)
    ]
    accounting_sources = [
        source(
            "fasb-public-notices",
            publisher="Financial Accounting Standards Board (FASB)",
            host="www.fasb.org",
            path="standards/accounting-standard-updates",
        )
    ] + [
        source(
            f"accounting-source-{index:02d}",
            publisher="Official Tax Publisher",
            host="www.irs.gov",
            path=f"accounting/{index}",
        )
        for index in range(8)
    ]
    write_json(
        root,
        "tools/authority_refresh/config/legal_sources.json",
        {"allowed_domains": ["official.example.gov"], "sources": legal_sources},
    )
    write_json(
        root,
        "tools/authority_refresh/config/accounting_sources.json",
        {"allowed_domains": ["www.fasb.org", "www.irs.gov"], "sources": accounting_sources},
    )

    for relative in (
        "authority/releases/README.md",
        "authority/snapshots/README.md",
        "legal/CURRENT_AUTHORITY_INDEX.md",
        "legal/artifacts/legal-bundle.pdf",
        "legal/artifacts/legal-master.pdf",
        "legal/text/first.txt",
        "legal/text/second.txt",
        "accounting/CURRENT_AUTHORITY_INDEX.md",
        "accounting/FASB_APPLICABILITY_INDEX.md",
        "accounting/artifacts/sourcebook.pdf",
        "accounting/text/sourcebook.txt",
        "src/rule.py",
    ):
        write_text(root, relative)

    legal_registry = [
        {
            "group": "group-a",
            "official_url": "https://official.example.gov/a",
            "bundle_path": "legal/artifacts/legal-bundle.pdf",
            "text_full_path": "legal/text/first.txt",
        },
        {
            "group": "group-b",
            "official_url": "https://official.example.gov/b",
            "bundle_path": "legal/artifacts/legal-bundle.pdf",
            "text_full_path": "legal/text/second.txt",
        },
    ]
    write_json(root, "legal/manifests/authority_registry.json", legal_registry)
    write_json(
        root,
        "legal/manifests/releases/2026-07-12.json",
        {
            "as_of": "2026-07-12",
            "bundles": [{"pages": 2, "sources": legal_registry}],
            "master": {"pages": 1},
        },
    )
    write_json(
        root,
        "legal/CURRENT_STATUS.json",
        {
            "schema_version": 1,
            "domain": "legal",
            "status_as_of": "2026-07-13",
            "overall_state": "approved-dated-baseline-with-monitoring-limits",
            "notice": "This is not legal advice or a representation of compliance.",
            "known_limitations": ["Fixture coverage is intentionally bounded."],
            "approved_release": {
                "release_status": "approved-dated-baseline",
                "current_through": "2026-07-12",
                "manifest_path": "legal/manifests/releases/2026-07-12.json",
                "authority_registry_path": "legal/manifests/authority_registry.json",
                "authority_record_count": 2,
                "unique_official_url_count": 2,
                "pdf_count": 2,
                "page_count": 3,
            },
            "authoritative_paths": ["legal/CURRENT_AUTHORITY_INDEX.md"],
        },
    )

    write_json(
        root,
        "accounting/manifests/fasb_topic_registry.json",
        {
            "topics": [
                {"id": "ASC-310", "topic": 310},
                {"id": "ASC-842", "topic": 842},
            ],
            "record_defaults": {"copyrighted_text_stored": False},
        },
    )
    write_json(
        root,
        "accounting/manifests/sourcebook_release.json",
        {
            "release_date": "2026-07-12",
            "source_record_count": 7,
            "files": [
                {
                    "pages": 4,
                    "repository_path": "accounting/artifacts/sourcebook.pdf",
                    "text_path": "accounting/text/sourcebook.txt",
                }
            ],
        },
    )
    write_json(
        root,
        "accounting/CURRENT_STATUS.json",
        {
            "schema_version": 1,
            "domain": "accounting",
            "status_as_of": "2026-07-13",
            "overall_state": "approved-dated-baseline-with-live-research-required",
            "notice": "This is not a CPA opinion or representation of GAAP compliance.",
            "known_limitations": ["Fixture coverage is intentionally bounded."],
            "approved_release": {
                "release_status": "approved-dated-baseline",
                "current_through": "2026-07-12",
                "release_manifest_path": "accounting/manifests/sourcebook_release.json",
                "fasb_topic_registry_path": "accounting/manifests/fasb_topic_registry.json",
                "fasb_topic_locator_count": 2,
                "source_record_count": 7,
                "sourcebook_pdf_count": 1,
                "sourcebook_page_count": 4,
                "fasb_codification_content_state": "not-stored",
            },
            "authoritative_paths": [
                "accounting/CURRENT_AUTHORITY_INDEX.md",
                "accounting/FASB_APPLICABILITY_INDEX.md",
            ],
        },
    )

    write_json(
        root,
        "authority/impact_crosswalk.json",
        {
            "schema_version": 1,
            "updated_on": "2026-07-13",
            "notice": "Human review controls.",
            "mappings": [
                {
                    "id": "rent-accounting",
                    "automatic_change": "prohibited",
                    "affected_paths": [{"repository_path": "src/rule.py"}],
                    "authority_references": [
                        {
                            "domain": "legal",
                            "reference_type": "legal-registry-group",
                            "reference": "group-a",
                        },
                        {
                            "domain": "accounting",
                            "reference_type": "asc-topic-locator",
                            "reference": "ASC 842",
                        },
                    ],
                }
            ],
        },
    )

    write_text(
        root,
        ".github/CODEOWNERS",
        """/legal/ @owner
/accounting/ @owner
/authority/ @owner
/tools/authority_refresh/ @owner
/.github/workflows/legal-*.yml @owner
/.github/workflows/accounting-*.yml @owner
/.github/workflows/authority-*.yml @owner
""",
    )
    write_text(
        root,
        ".gitattributes",
        """*.pdf binary
*.zip binary
*.xlsx binary
*.docx binary
""",
    )
    write_text(
        root,
        ".github/workflows/authority-refresh-checks.yml",
        """name: Authority checks
jobs:
  validate:
    steps:
      - run: python tools/authority_refresh/validate_system.py
      - run: python -m unittest discover -s tools/authority_refresh/tests
""",
    )
    write_text(
        root,
        ".github/workflows/authority-discovery.yml",
        """name: Authority discovery
on:
  schedule:
    - cron: '17 11 * * *'
  workflow_dispatch:
permissions:
  contents: write
  pull-requests: write
jobs:
  candidate:
    steps:
      - run: cp report authority/candidates/legal/latest
      - run: gh pr create --draft
""",
    )
    write_text(
        root,
        ".github/workflows/authority-release-promotion.yml",
        """name: Authority promotion
on:
  workflow_dispatch:
permissions:
  contents: write
  pull-requests: write
jobs:
  promote:
    environment: authority-production
    steps:
      - run: test "$CONFIRM" = "PROMOTE_REVIEWED_AUTHORITY_RELEASE"
      - run: python tools/authority_refresh/promotion.py authority/candidates/legal/candidate.json authority/reviews/legal/approval.json
      - run: gh pr create --draft
""",
    )


class ValidateSystemTests(unittest.TestCase):
    def test_valid_workspace_passes(self):
        with workspace_temp_directory() as directory:
            root = Path(directory)
            build_valid_workspace(root)

            report = validate_system.validate_repository(root)

            self.assertTrue(report.ok, "\n".join(report.errors))
            self.assertGreater(report.checks, 50)

    def test_rejects_paragraph_locator_and_automatic_change(self):
        with workspace_temp_directory() as directory:
            root = Path(directory)
            build_valid_workspace(root)
            crosswalk = read_json(root, "authority/impact_crosswalk.json")
            crosswalk["mappings"][0]["automatic_change"] = "allowed"
            crosswalk["mappings"][0]["authority_references"][1]["reference"] = "ASC 842-10-25-1"
            crosswalk["mappings"][0]["affected_paths"][0]["repository_path"] = "src/missing.py"
            crosswalk["mappings"].append(dict(crosswalk["mappings"][0]))
            write_json(root, "authority/impact_crosswalk.json", crosswalk)

            report = validate_system.validate_repository(root)

            messages = "\n".join(report.errors)
            self.assertIn("automatic_change must be prohibited", messages)
            self.assertIn("paragraph locators are prohibited", messages)
            self.assertIn("duplicate mapping id", messages)
            self.assertIn("referenced path does not exist", messages)

    def test_rejects_recursive_compliance_key_and_count_drift(self):
        with workspace_temp_directory() as directory:
            root = Path(directory)
            build_valid_workspace(root)
            status = read_json(root, "legal/CURRENT_STATUS.json")
            status["currentness"] = {
                "claim": {"compliant": True, "compliance_certified": True}
            }
            status["approved_release"]["authority_record_count"] = 99
            write_json(root, "legal/CURRENT_STATUS.json", status)

            report = validate_system.validate_repository(root)

            messages = "\n".join(report.errors)
            self.assertIn("prohibited blanket-compliance key", messages)
            self.assertIn("authority_record_count does not match", messages)

    def test_rejects_fasb_redistribution(self):
        with workspace_temp_directory() as directory:
            root = Path(directory)
            build_valid_workspace(root)
            catalog = read_json(root, "tools/authority_refresh/config/accounting_sources.json")
            catalog["sources"][0]["storage_policy"] = "redistributable"
            write_json(root, "tools/authority_refresh/config/accounting_sources.json", catalog)

            report = validate_system.validate_repository(root)

            self.assertIn("FASB", "\n".join(report.errors))
            self.assertFalse(report.ok)

    def test_rejects_codification_scraping(self):
        with workspace_temp_directory() as directory:
            root = Path(directory)
            build_valid_workspace(root)
            catalog = read_json(root, "tools/authority_refresh/config/accounting_sources.json")
            catalog["allowed_domains"].append("asc.fasb.org")
            catalog["sources"][0]["allowed_hosts"] = ["asc.fasb.org"]
            catalog["sources"][0]["discovery_url"] = "https://asc.fasb.org/codification"
            write_json(root, "tools/authority_refresh/config/accounting_sources.json", catalog)

            report = validate_system.validate_repository(root)

            self.assertIn("not scrape Codification", "\n".join(report.errors))

    def test_rejects_auto_merge_and_missing_binary_rule(self):
        with workspace_temp_directory() as directory:
            root = Path(directory)
            build_valid_workspace(root)
            workflow = root / ".github/workflows/authority-discovery.yml"
            workflow.write_text(workflow.read_text(encoding="utf-8") + "\n# gh pr merge --auto\n")
            write_text(root, ".gitattributes", "*.pdf text\n*.zip binary\n*.xlsx binary\n*.docx binary\n")

            report = validate_system.validate_repository(root)

            messages = "\n".join(report.errors)
            self.assertIn("automatic or direct pull-request merge is prohibited", messages)
            self.assertIn("*.pdf must be marked binary", messages)

    def test_invalid_json_is_reported_without_crashing(self):
        with workspace_temp_directory() as directory:
            root = Path(directory)
            build_valid_workspace(root)
            write_text(root, "authority/broken.json", "{not-json")

            report = validate_system.validate_repository(root)

            self.assertIn("authority/broken.json: cannot parse JSON", "\n".join(report.errors))

    def test_rejects_missing_authority_refresh_code_owner(self):
        with workspace_temp_directory() as directory:
            root = Path(directory)
            build_valid_workspace(root)
            codeowners = root / ".github" / "CODEOWNERS"
            codeowners.write_text(
                codeowners.read_text(encoding="utf-8").replace(
                    "/tools/authority_refresh/ @owner\n",
                    "",
                ),
                encoding="utf-8",
            )

            report = validate_system.validate_repository(root)

            self.assertIn(
                "no owner covers tools/authority_refresh/promotion.py",
                "\n".join(report.errors),
            )

    def test_accepts_single_immutable_release_chain_with_matching_tip(self):
        with workspace_temp_directory() as directory:
            root = Path(directory)
            build_valid_workspace(root)
            first = write_authority_release(
                root,
                domain="legal",
                approved_at="2026-07-11",
                run_id="root",
                baseline_snapshot=None,
            )
            write_authority_release(
                root,
                domain="legal",
                approved_at="2026-07-12",
                run_id="tip",
                baseline_snapshot=first,
            )

            report = validate_system.validate_repository(root)

            self.assertTrue(report.ok, "\n".join(report.errors))

    def test_rejects_release_chain_fork(self):
        with workspace_temp_directory() as directory:
            root = Path(directory)
            build_valid_workspace(root)
            first = write_authority_release(
                root,
                domain="legal",
                approved_at="2026-07-10",
                run_id="root",
                baseline_snapshot=None,
            )
            write_authority_release(
                root,
                domain="legal",
                approved_at="2026-07-11",
                run_id="child-a",
                baseline_snapshot=first,
            )
            write_authority_release(
                root,
                domain="legal",
                approved_at="2026-07-12",
                run_id="child-b",
                baseline_snapshot=first,
            )

            report = validate_system.validate_repository(root)

            messages = "\n".join(report.errors)
            self.assertIn("chain forks", messages)
            self.assertIn("one unique tip", messages)

    def test_rejects_snapshot_that_is_not_the_unique_chain_tip(self):
        with workspace_temp_directory() as directory:
            root = Path(directory)
            build_valid_workspace(root)
            first = write_authority_release(
                root,
                domain="accounting",
                approved_at="2026-07-11",
                run_id="root",
                baseline_snapshot=None,
            )
            write_authority_release(
                root,
                domain="accounting",
                approved_at="2026-07-12",
                run_id="tip",
                baseline_snapshot=first,
            )
            write_json(root, "authority/snapshots/accounting.json", first)

            report = validate_system.validate_repository(root)

            self.assertIn(
                "snapshot does not equal the unique release-chain tip",
                "\n".join(report.errors),
            )

    def test_rejects_future_dated_immutable_release(self):
        with workspace_temp_directory() as directory:
            root = Path(directory)
            build_valid_workspace(root)
            write_authority_release(
                root,
                domain="legal",
                approved_at="2999-01-01",
                run_id="future",
                baseline_snapshot=None,
            )

            report = validate_system.validate_repository(root)

            self.assertIn(
                "release.approved_at cannot be in the future",
                "\n".join(report.errors),
            )

    def test_rejects_child_release_backdated_before_predecessor(self):
        with workspace_temp_directory() as directory:
            root = Path(directory)
            build_valid_workspace(root)
            first = write_authority_release(
                root,
                domain="legal",
                approved_at="2026-07-12",
                run_id="root",
                baseline_snapshot=None,
            )
            write_authority_release(
                root,
                domain="legal",
                approved_at="2026-07-11",
                run_id="backdated-child",
                baseline_snapshot=first,
            )

            report = validate_system.validate_repository(root)

            self.assertIn(
                "approved_at precedes its predecessor release",
                "\n".join(report.errors),
            )

    def test_cli_returns_zero_and_prints_summary(self):
        with workspace_temp_directory() as directory:
            root = Path(directory)
            build_valid_workspace(root)
            output = io.StringIO()

            with contextlib.redirect_stdout(output):
                result = validate_system.main(["--root", str(root)])

            self.assertEqual(0, result)
            self.assertIn("Authority system validation: PASS", output.getvalue())


if __name__ == "__main__":
    unittest.main()
