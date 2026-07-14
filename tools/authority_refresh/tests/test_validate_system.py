from __future__ import annotations

import contextlib
import io
import json
import unittest
from pathlib import Path

from tools.authority_refresh import core, promotion, validate_system
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
    failed_source: bool = False,
    generated_at_override: str | None = None,
) -> dict:
    run_digest = core.sha256_bytes(run_id.encode("utf-8"))
    workflow_run_id = (
        f"{int(run_digest[:12], 16)}-{int(run_digest[12:20], 16)}"
    )
    catalog = core.load_catalog(
        root / "tools" / "authority_refresh" / "config" / f"{domain}_sources.json",
        domain=domain,
    )
    crosswalk = core.load_impact_crosswalk(
        root / "authority" / "impact_crosswalk.json"
    )
    generated_at = generated_at_override or f"{approved_at}T00:00:00+00:00"
    source_results: list[dict] = []
    items: list[dict] = []
    failed_source_id = catalog["sources"][0]["source_id"] if failed_source else None
    for configured_source in catalog["sources"]:
        source_id = configured_source["source_id"]
        result = {
            "source_id": source_id,
            "critical": bool(configured_source["critical"]),
            "storage_policy": configured_source["storage_policy"],
            "discovery_url": configured_source["discovery_url"],
            "retrieved_at": generated_at,
            "missing_detection": configured_source.get(
                "missing_detection", "complete-index"
            ),
        }
        if source_id == failed_source_id:
            result.update(
                {
                    "status": "error",
                    "error": "simulated archived source failure",
                    "item_count": 0,
                    "observed_item_ids": [],
                }
            )
        else:
            observed: list[dict] = []
            for item_index in range(core.source_minimum_items(configured_source)):
                item = core.normalize_item(
                    {
                        "external_id": f"fixture-{source_id}-{item_index}",
                        "title": f"Official fixture {item_index} for {source_id}",
                        "official_url": configured_source["discovery_url"],
                        "published_at": "2026-07-01",
                        "effective_at": None,
                        "status": "published",
                        "metadata": {"fixture": True},
                    },
                    configured_source,
                    domain=domain,
                )
                observed.append(item)
                items.append(item)
            result.update(
                {
                    "status": "healthy",
                    "final_url": configured_source["discovery_url"],
                    "content_type": "application/json",
                    "payload_sha256": core.sha256_bytes(source_id.encode("utf-8")),
                    "attempts": 1,
                    "item_count": len(observed),
                    "observed_item_ids": sorted(
                        item["item_id"] for item in observed
                    ),
                }
            )
        source_results.append(result)

    baseline = baseline_snapshot or {
        "schema_version": core.SCHEMA_VERSION,
        "domain": domain,
        "items": [],
    }
    candidate = core.build_candidate(
        domain=domain,
        generated_at=generated_at,
        run_id=workflow_run_id,
        baseline_path=Path("authority") / "snapshots" / f"{domain}.json",
        baseline=baseline,
        baseline_missing=baseline_snapshot is None,
        source_results=source_results,
        items=items,
        impact_crosswalk=crosswalk,
    )
    approval = {
        "schema_version": core.SCHEMA_VERSION,
        "domain": domain,
        "candidate_sha256": candidate["candidate_sha256"],
        "approvals": [
            {
                "role": role,
                "reviewer": "@GHRealEstate",
                "reviewed_at": f"{approved_at}T12:00:00+00:00",
                "determination": "approved",
                "evidence_urls": ["https://official.example/evidence"],
            }
            for role in sorted(promotion._required_roles(candidate))
        ],
        "change_resolutions": [
            {
                "item_id": change["item_id"],
                "change_type": change["change_type"],
                "resolution": "no_material_change",
                "evidence_urls": ["https://official.example/evidence"],
            }
            for change in candidate["changes"]
        ],
        "impact_resolutions": [
            {
                "mapping_id": impact["mapping_id"],
                "determination": "no_change_required",
                "evidence_urls": ["https://official.example/evidence"],
                "reviewed_paths": [],
            }
            for impact in candidate["potential_impacts"]
        ],
    }
    validation_context = {
        "contract_version": promotion.VALIDATION_CONTRACT_VERSION,
        "domain": domain,
        "candidate_sha256": candidate["candidate_sha256"],
        "source_revision": "1" * 40,
        "candidate_path": (
            f"authority/candidates/{domain}/runs/{workflow_run_id}/candidate.json"
        ),
        "approval_path": f"authority/reviews/{domain}/{workflow_run_id}.json",
        "source_catalog_path": (
            f"tools/authority_refresh/config/{domain}_sources.json"
        ),
        "impact_crosswalk_path": "authority/impact_crosswalk.json",
        "source_catalog": catalog,
        "impact_crosswalk": crosswalk,
        "path_manifest": [],
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
        "validation_context_sha256": core.sha256_json(validation_context),
        "notice": promotion.RELEASE_NOTICE,
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
    write_json(root, f"{directory}/validation-context.json", validation_context)
    write_json(root, f"{directory}/release.json", release)
    write_json(root, f"authority/snapshots/{domain}.json", snapshot)
    return snapshot


def archived_release_directory(root: Path, snapshot: dict) -> Path:
    return root / "authority" / "releases" / snapshot["release_id"]


def replace_archived_approval(
    root: Path,
    snapshot: dict,
    approval: dict,
) -> None:
    directory = archived_release_directory(root, snapshot)
    write_json(root, str((directory / "approval.json").relative_to(root)), approval)
    release = read_json(root, str((directory / "release.json").relative_to(root)))
    release["approval"] = approval
    write_json(root, str((directory / "release.json").relative_to(root)), release)


def replace_validation_context(
    root: Path,
    snapshot: dict,
    context: dict,
    *,
    update_release_hash: bool,
) -> None:
    directory = archived_release_directory(root, snapshot)
    context_path = str((directory / "validation-context.json").relative_to(root))
    write_json(root, context_path, context)
    if update_release_hash:
        release_path = str((directory / "release.json").relative_to(root))
        release = read_json(root, release_path)
        release["validation_context_sha256"] = core.sha256_json(context)
        write_json(root, release_path, release)


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
                    "review_gate": {"required_roles": ["system-owner"]},
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
      - uses: actions/checkout@fixture
        with:
          fetch-depth: 0
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


class ReleaseIntroductionTopologyTests(unittest.TestCase):
    RELEASE_DIRECTORY = "authority/releases/2026-07-13-legal-0123456789ab"
    RELEASE_FILES = {
        f"authority/releases/2026-07-13-legal-0123456789ab/{filename}"
        for filename in validate_system.IMMUTABLE_RELEASE_FILENAMES
    }
    ROOT = "0" * 40
    SOURCE = "1" * 40
    INTRODUCTION = "2" * 40
    LATER = "3" * 40
    REINTRODUCTION = "4" * 40

    def validate_topology(
        self,
        commits: list[str],
        states: dict[str, set[str]],
        *,
        source_revision: str,
    ) -> str:
        return validate_system._validate_release_introduction(
            commits,
            release_directory=self.RELEASE_DIRECTORY,
            source_revision=source_revision,
            files_at_commit=lambda commit: states[commit],
        )

    def test_binds_to_introduction_parent_across_supported_git_topologies(self):
        cases = {
            "promotion branch": (
                [self.SOURCE, self.INTRODUCTION],
                {self.SOURCE: set(), self.INTRODUCTION: self.RELEASE_FILES},
            ),
            "pull-request synthetic merge": (
                [self.ROOT, self.SOURCE, self.INTRODUCTION],
                {
                    self.ROOT: set(),
                    self.SOURCE: set(),
                    self.INTRODUCTION: self.RELEASE_FILES,
                },
            ),
            "squash merge": (
                [self.ROOT, self.SOURCE, self.INTRODUCTION],
                {
                    self.ROOT: set(),
                    self.SOURCE: set(),
                    self.INTRODUCTION: self.RELEASE_FILES,
                },
            ),
            "later unrelated commit": (
                [self.ROOT, self.SOURCE, self.INTRODUCTION, self.LATER],
                {
                    self.ROOT: set(),
                    self.SOURCE: set(),
                    self.INTRODUCTION: self.RELEASE_FILES,
                    self.LATER: self.RELEASE_FILES,
                },
            ),
        }
        for name, (commits, states) in cases.items():
            with self.subTest(topology=name):
                parent = self.validate_topology(
                    commits,
                    states,
                    source_revision=self.SOURCE,
                )
                self.assertEqual(self.SOURCE, parent)

    def test_rejects_an_older_first_parent_as_the_recorded_source(self):
        states = {
            self.ROOT: set(),
            self.SOURCE: set(),
            self.INTRODUCTION: self.RELEASE_FILES,
        }

        with self.assertRaisesRegex(
            core.AuthorityRefreshError,
            "does not match the immutable release introduction parent",
        ):
            self.validate_topology(
                [self.ROOT, self.SOURCE, self.INTRODUCTION],
                states,
                source_revision=self.ROOT,
            )

    def test_rejects_unavailable_root_partial_and_removed_release_history(self):
        cases = {
            "unavailable": (
                [],
                {},
                "history is unavailable",
            ),
            "root introduction": (
                [self.INTRODUCTION],
                {self.INTRODUCTION: self.RELEASE_FILES},
                "repository root commit",
            ),
            "partial introduction": (
                [self.SOURCE, self.INTRODUCTION],
                {
                    self.SOURCE: set(),
                    self.INTRODUCTION: self.RELEASE_FILES
                    - {f"{self.RELEASE_DIRECTORY}/approval.json"},
                },
                "did not enter together",
            ),
            "delete and re-add": (
                [
                    self.SOURCE,
                    self.INTRODUCTION,
                    self.LATER,
                    self.REINTRODUCTION,
                ],
                {
                    self.SOURCE: set(),
                    self.INTRODUCTION: self.RELEASE_FILES,
                    self.LATER: set(),
                    self.REINTRODUCTION: self.RELEASE_FILES,
                },
                "was removed from first-parent history",
            ),
        }
        for name, (commits, states, message) in cases.items():
            with self.subTest(case=name):
                with self.assertRaisesRegex(core.AuthorityRefreshError, message):
                    self.validate_topology(
                        commits,
                        states,
                        source_revision=self.SOURCE,
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

    def test_rejects_degraded_archived_candidate(self):
        with workspace_temp_directory() as directory:
            root = Path(directory)
            build_valid_workspace(root)
            write_authority_release(
                root,
                domain="legal",
                approved_at="2026-07-12",
                run_id="degraded",
                baseline_snapshot=None,
                failed_source=True,
            )

            report = validate_system.validate_repository(root)

            self.assertIn(
                "archived promotion replay failed: a degraded candidate cannot be promoted",
                "\n".join(report.errors),
            )

    def test_rejects_archived_release_backdated_before_candidate_and_review(self):
        with workspace_temp_directory() as directory:
            root = Path(directory)
            build_valid_workspace(root)
            snapshot = write_authority_release(
                root,
                domain="legal",
                approved_at="2026-07-12",
                run_id="backdated-root",
                baseline_snapshot=None,
            )
            old_directory = archived_release_directory(root, snapshot)
            release = read_json(root, f"{old_directory.relative_to(root)}/release.json")
            backdated_release_id = (
                f"2026-07-11-legal-{release['candidate_sha256'][:12]}"
            )
            new_directory = old_directory.parent / backdated_release_id
            old_directory.rename(new_directory)
            release["approved_at"] = "2026-07-11"
            release["release_id"] = backdated_release_id
            write_json(
                root,
                f"{new_directory.relative_to(root)}/release.json",
                release,
            )
            snapshot["approved_at"] = "2026-07-11"
            snapshot["release_id"] = backdated_release_id
            write_json(root, "authority/snapshots/legal.json", snapshot)

            report = validate_system.validate_repository(root)

            self.assertIn(
                "release-date cannot precede the candidate or its latest review",
                "\n".join(report.errors),
            )

    def test_rejects_release_notice_that_claims_compliance_certification(self):
        with workspace_temp_directory() as directory:
            root = Path(directory)
            build_valid_workspace(root)
            snapshot = write_authority_release(
                root,
                domain="legal",
                approved_at="2026-07-12",
                run_id="certifying-notice",
                baseline_snapshot=None,
            )
            release_directory = archived_release_directory(root, snapshot)
            release_path = f"{release_directory.relative_to(root)}/release.json"
            release = read_json(root, release_path)
            release["notice"] = "This release certifies complete legal compliance."
            write_json(root, release_path, release)

            report = validate_system.validate_repository(root)

            self.assertIn(
                "release notice must preserve the non-certification disclaimer",
                "\n".join(report.errors),
            )

    def test_rejects_archived_release_of_a_stale_candidate(self):
        with workspace_temp_directory() as directory:
            root = Path(directory)
            build_valid_workspace(root)
            write_authority_release(
                root,
                domain="legal",
                approved_at="2026-07-12",
                run_id="stale-candidate",
                baseline_snapshot=None,
                generated_at_override="2026-06-01T00:00:00+00:00",
            )

            report = validate_system.validate_repository(root)

            self.assertIn(
                "release-date cannot be more than 7 days after candidate.generated_at",
                "\n".join(report.errors),
            )

    def test_rejects_missing_or_empty_archived_approval(self):
        with self.subTest(case="missing approval document"):
            with workspace_temp_directory() as directory:
                root = Path(directory)
                build_valid_workspace(root)
                snapshot = write_authority_release(
                    root,
                    domain="legal",
                    approved_at="2026-07-12",
                    run_id="missing-approval",
                    baseline_snapshot=None,
                )
                (archived_release_directory(root, snapshot) / "approval.json").unlink()

                report = validate_system.validate_repository(root)

                self.assertIn(
                    "approval.json: immutable release document is missing or invalid",
                    "\n".join(report.errors),
                )

        with self.subTest(case="empty approval records"):
            with workspace_temp_directory() as directory:
                root = Path(directory)
                build_valid_workspace(root)
                snapshot = write_authority_release(
                    root,
                    domain="legal",
                    approved_at="2026-07-12",
                    run_id="empty-approvals",
                    baseline_snapshot=None,
                )
                release_dir = archived_release_directory(root, snapshot)
                approval = json.loads(
                    (release_dir / "approval.json").read_text(encoding="utf-8")
                )
                approval["approvals"] = []
                replace_archived_approval(root, snapshot, approval)

                report = validate_system.validate_repository(root)

                self.assertIn(
                    "at least one structured approval is required",
                    "\n".join(report.errors),
                )

    def test_rejects_archived_approval_missing_required_role(self):
        with workspace_temp_directory() as directory:
            root = Path(directory)
            build_valid_workspace(root)
            snapshot = write_authority_release(
                root,
                domain="legal",
                approved_at="2026-07-12",
                run_id="missing-role",
                baseline_snapshot=None,
            )
            release_dir = archived_release_directory(root, snapshot)
            approval = json.loads(
                (release_dir / "approval.json").read_text(encoding="utf-8")
            )
            approval["approvals"].pop()
            replace_archived_approval(root, snapshot, approval)

            report = validate_system.validate_repository(root)

            self.assertIn(
                "missing approved reviewer determination",
                "\n".join(report.errors),
            )

    def test_rejects_missing_archived_change_or_impact_resolutions(self):
        for field, expected in (
            ("change_resolutions", "change resolutions do not match candidate"),
            ("impact_resolutions", "impact resolutions do not match candidate"),
        ):
            with self.subTest(field=field):
                with workspace_temp_directory() as directory:
                    root = Path(directory)
                    build_valid_workspace(root)
                    snapshot = write_authority_release(
                        root,
                        domain="legal",
                        approved_at="2026-07-12",
                        run_id=f"missing-{field}",
                        baseline_snapshot=None,
                    )
                    release_dir = archived_release_directory(root, snapshot)
                    approval = json.loads(
                        (release_dir / "approval.json").read_text(encoding="utf-8")
                    )
                    self.assertTrue(approval[field])
                    approval[field] = []
                    replace_archived_approval(root, snapshot, approval)

                    report = validate_system.validate_repository(root)

                    self.assertIn(expected, "\n".join(report.errors))

    def test_rejects_rejected_or_invalid_archived_determination(self):
        for determination, expected in (
            ("rejected", "required reviewer rejected the candidate"),
            ("uncertain", "unsupported reviewer determination: uncertain"),
        ):
            with self.subTest(determination=determination):
                with workspace_temp_directory() as directory:
                    root = Path(directory)
                    build_valid_workspace(root)
                    snapshot = write_authority_release(
                        root,
                        domain="legal",
                        approved_at="2026-07-12",
                        run_id=f"determination-{determination}",
                        baseline_snapshot=None,
                    )
                    release_dir = archived_release_directory(root, snapshot)
                    approval = json.loads(
                        (release_dir / "approval.json").read_text(encoding="utf-8")
                    )
                    approval["approvals"][0]["determination"] = determination
                    replace_archived_approval(root, snapshot, approval)

                    report = validate_system.validate_repository(root)

                    self.assertIn(expected, "\n".join(report.errors))

    def test_rejects_missing_extra_or_tampered_validation_context(self):
        with self.subTest(case="missing"):
            with workspace_temp_directory() as directory:
                root = Path(directory)
                build_valid_workspace(root)
                snapshot = write_authority_release(
                    root,
                    domain="legal",
                    approved_at="2026-07-12",
                    run_id="missing-context",
                    baseline_snapshot=None,
                )
                context_path = (
                    archived_release_directory(root, snapshot)
                    / "validation-context.json"
                )
                context_path.unlink()

                report = validate_system.validate_repository(root)

                self.assertIn(
                    "validation-context.json: immutable release document is missing or invalid",
                    "\n".join(report.errors),
                )

        with self.subTest(case="extra field"):
            with workspace_temp_directory() as directory:
                root = Path(directory)
                build_valid_workspace(root)
                snapshot = write_authority_release(
                    root,
                    domain="legal",
                    approved_at="2026-07-12",
                    run_id="extra-context",
                    baseline_snapshot=None,
                )
                release_dir = archived_release_directory(root, snapshot)
                context = json.loads(
                    (release_dir / "validation-context.json").read_text(
                        encoding="utf-8"
                    )
                )
                context["unexpected"] = True
                replace_validation_context(
                    root,
                    snapshot,
                    context,
                    update_release_hash=True,
                )

                report = validate_system.validate_repository(root)

                self.assertIn(
                    "validation_context fields do not match the contract",
                    "\n".join(report.errors),
                )

        with self.subTest(case="tampered content"):
            with workspace_temp_directory() as directory:
                root = Path(directory)
                build_valid_workspace(root)
                snapshot = write_authority_release(
                    root,
                    domain="legal",
                    approved_at="2026-07-12",
                    run_id="tampered-context",
                    baseline_snapshot=None,
                )
                release_dir = archived_release_directory(root, snapshot)
                context = json.loads(
                    (release_dir / "validation-context.json").read_text(
                        encoding="utf-8"
                    )
                )
                context["source_catalog"]["sources"][0]["discovery_url"] = (
                    "https://official.example.gov/legal/tampered"
                )
                replace_validation_context(
                    root,
                    snapshot,
                    context,
                    update_release_hash=False,
                )

                report = validate_system.validate_repository(root)

                self.assertIn(
                    "release validation-context hash does not match",
                    "\n".join(report.errors),
                )

    def test_rejects_extra_file_in_immutable_release_directory(self):
        with workspace_temp_directory() as directory:
            root = Path(directory)
            build_valid_workspace(root)
            snapshot = write_authority_release(
                root,
                domain="legal",
                approved_at="2026-07-12",
                run_id="extra-file",
                baseline_snapshot=None,
            )
            extra_path = archived_release_directory(root, snapshot) / "notes.txt"
            extra_path.write_text("untracked archive mutation\n", encoding="utf-8")

            report = validate_system.validate_repository(root)

            self.assertIn(
                "immutable release file set must be exactly",
                "\n".join(report.errors),
            )

    def test_archived_replay_is_independent_of_current_configuration_drift(self):
        with workspace_temp_directory() as directory:
            root = Path(directory)
            build_valid_workspace(root)
            write_authority_release(
                root,
                domain="legal",
                approved_at="2026-07-12",
                run_id="historical-context",
                baseline_snapshot=None,
            )
            catalog_path = "tools/authority_refresh/config/legal_sources.json"
            catalog = read_json(root, catalog_path)
            catalog["sources"][0]["discovery_url"] = (
                "https://official.example.gov/legal/current-revision"
            )
            write_json(root, catalog_path, catalog)
            crosswalk_path = "authority/impact_crosswalk.json"
            crosswalk = read_json(root, crosswalk_path)
            crosswalk["mappings"][0]["id"] = "rent-accounting-v2"
            write_json(root, crosswalk_path, crosswalk)

            report = validate_system.validate_repository(root)

            self.assertTrue(report.ok, "\n".join(report.errors))

    def test_source_revision_blobs_must_match_archived_context(self):
        reviewed_payload = b"reviewed evidence\n"
        context = {
            "candidate_path": "authority/candidates/legal/runs/1-1/candidate.json",
            "approval_path": "authority/reviews/legal/1-1.json",
            "source_catalog_path": "tools/authority_refresh/config/legal_sources.json",
            "impact_crosswalk_path": "authority/impact_crosswalk.json",
            "source_catalog": {"sources": ["catalog"]},
            "impact_crosswalk": {"mappings": ["crosswalk"]},
            "path_manifest": [
                {
                    "path": "legal/reviewed.txt",
                    "sha256": core.sha256_bytes(reviewed_payload),
                    "size_bytes": len(reviewed_payload),
                }
            ],
        }
        candidate = {"candidate": "archived", "domain": "legal"}
        approval = {"approval": "archived"}
        node = {
            "label": "authority/releases/fixture",
            "candidate": candidate,
            "approval": approval,
            "validation_context": context,
        }
        blobs = {
            context["candidate_path"]: json.dumps(candidate).encode("utf-8"),
            "authority/candidates/legal/latest/candidate.json": json.dumps(
                candidate
            ).encode("utf-8"),
            context["approval_path"]: json.dumps(approval).encode("utf-8"),
            context["source_catalog_path"]: json.dumps(
                context["source_catalog"]
            ).encode("utf-8"),
            context["impact_crosswalk_path"]: json.dumps(
                context["impact_crosswalk"]
            ).encode("utf-8"),
            "legal/reviewed.txt": reviewed_payload,
        }

        report = validate_system.ValidationReport()
        validate_system._validate_source_revision_blobs(
            node,
            blobs.__getitem__,
            report,
        )
        self.assertTrue(report.ok, "\n".join(report.errors))

        blobs[context["candidate_path"]] = b'{"candidate":"tampered"}'
        tampered_report = validate_system.ValidationReport()
        validate_system._validate_source_revision_blobs(
            node,
            blobs.__getitem__,
            tampered_report,
        )
        self.assertIn(
            "source revision does not match archived",
            "\n".join(tampered_report.errors),
        )

        blobs[context["candidate_path"]] = json.dumps(candidate).encode("utf-8")
        blobs["authority/candidates/legal/latest/candidate.json"] = (
            b'{"candidate":"stale","domain":"legal"}'
        )
        stale_report = validate_system.ValidationReport()
        validate_system._validate_source_revision_blobs(
            node,
            blobs.__getitem__,
            stale_report,
        )
        self.assertIn(
            "latest/candidate.json",
            "\n".join(stale_report.errors),
        )

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
