from __future__ import annotations

import json
import unittest
from datetime import date, datetime, timezone
from pathlib import Path

from tools.authority_refresh import core, promotion
from test_support import workspace_temp_directory


GENERATED_AT = "2026-07-13T00:00:00+00:00"
REVIEWED_AT = "2026-07-13T12:00:00+00:00"
EVIDENCE_URL = "https://official.example/evidence"
CURRENT_TIME = datetime(2026, 7, 13, 23, 0, tzinfo=timezone.utc)


def rehash(value: dict) -> None:
    value["candidate_sha256"] = core.sha256_json(
        {key: item for key, item in value.items() if key != "candidate_sha256"}
    )


def canonical_candidate(
    domain: str = "legal",
    *,
    failed_source_id: str | None = None,
) -> dict:
    catalog = core.load_catalog(
        promotion.PACKAGE_DIR / "config" / f"{domain}_sources.json",
        domain=domain,
    )
    crosswalk = core.load_impact_crosswalk(
        promotion.REPO_ROOT / "authority" / "impact_crosswalk.json"
    )
    source_results: list[dict] = []
    items: list[dict] = []
    for source in catalog["sources"]:
        source_id = source["source_id"]
        result = {
            "source_id": source_id,
            "critical": bool(source["critical"]),
            "storage_policy": source["storage_policy"],
            "discovery_url": source["discovery_url"],
            "retrieved_at": GENERATED_AT,
            "missing_detection": source.get("missing_detection", "complete-index"),
        }
        if source_id == failed_source_id:
            result.update(
                {
                    "status": "error",
                    "error": "simulated official source failure",
                    "item_count": 0,
                    "observed_item_ids": [],
                }
            )
        else:
            observed: list[dict] = []
            for item_index in range(max(1, int(source.get("minimum_items", 1)))):
                item = core.normalize_item(
                    {
                        "external_id": f"fixture-{source_id}-{item_index}",
                        "title": f"Official fixture {item_index} for {source_id}",
                        "official_url": source["discovery_url"],
                        "published_at": "2026-07-12",
                        "effective_at": None,
                        "status": "published",
                        "metadata": {"fixture": True},
                    },
                    source,
                    domain=domain,
                )
                observed.append(item)
                items.append(item)
            result.update(
                {
                    "status": "healthy",
                    "final_url": source["discovery_url"],
                    "content_type": "application/json",
                    "payload_sha256": core.sha256_bytes(source_id.encode("utf-8")),
                    "attempts": 1,
                    "item_count": len(observed),
                    "observed_item_ids": sorted(item["item_id"] for item in observed),
                }
            )
        source_results.append(result)
    return core.build_candidate(
        domain=domain,
        generated_at=GENERATED_AT,
        run_id="test-run",
        baseline_path=Path("authority") / "snapshots" / f"{domain}.json",
        baseline={"schema_version": core.SCHEMA_VERSION, "domain": domain, "items": []},
        baseline_missing=True,
        source_results=source_results,
        items=items,
        impact_crosswalk=crosswalk,
    )


def approval(candidate_value: dict) -> dict:
    return {
        "schema_version": core.SCHEMA_VERSION,
        "domain": candidate_value["domain"],
        "candidate_sha256": candidate_value["candidate_sha256"],
        "approvals": [
            {
                "role": role,
                "reviewer": "@GHRealEstate",
                "reviewed_at": REVIEWED_AT,
                "determination": "approved",
                "evidence_urls": [EVIDENCE_URL],
            }
            for role in sorted(promotion._required_roles(candidate_value))
        ],
        "change_resolutions": [
            {
                "item_id": change["item_id"],
                "change_type": change["change_type"],
                "resolution": "no_material_change",
                "evidence_urls": [EVIDENCE_URL],
            }
            for change in candidate_value["changes"]
        ],
        "impact_resolutions": [
            {
                "mapping_id": impact["mapping_id"],
                "determination": "no_change_required",
                "evidence_urls": [EVIDENCE_URL],
                "reviewed_paths": [],
            }
            for impact in candidate_value["potential_impacts"]
        ],
    }


def write_latest_candidate(root: Path, candidate_value: dict) -> None:
    path = (
        root
        / "authority"
        / "candidates"
        / candidate_value["domain"]
        / "latest"
        / "candidate.json"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(candidate_value), encoding="utf-8")


class PromotionTests(unittest.TestCase):
    def test_degraded_candidate_cannot_be_promoted(self):
        healthy = canonical_candidate()
        failed_source_id = healthy["source_results"][0]["source_id"]
        value = canonical_candidate(failed_source_id=failed_source_id)
        with self.assertRaisesRegex(core.AuthorityRefreshError, "degraded"):
            promotion.validate_approval(value, approval(value))

    def test_every_change_requires_a_resolution(self):
        value = canonical_candidate()
        review = approval(value)
        review["change_resolutions"].pop()
        with self.assertRaisesRegex(core.AuthorityRefreshError, "do not match"):
            promotion.validate_approval(value, review)

    def test_every_potential_impact_requires_a_resolution(self):
        value = canonical_candidate()
        review = approval(value)
        review["impact_resolutions"].pop()
        with self.assertRaisesRegex(core.AuthorityRefreshError, "impact resolutions"):
            promotion.validate_approval(value, review)

    def test_all_canonical_crosswalk_roles_are_required(self):
        value = canonical_candidate()
        review = approval(value)
        review["approvals"] = [
            entry for entry in review["approvals"] if entry["role"] != "finance-operator"
        ]
        with self.assertRaisesRegex(core.AuthorityRefreshError, "finance-operator"):
            promotion.validate_approval(value, review)

    def test_rejected_required_reviewer_blocks_promotion(self):
        value = canonical_candidate()
        review = approval(value)
        review["approvals"].append(
            {
                "role": "qualified-legal-reviewer",
                "reviewer": "@SecondReviewer",
                "reviewed_at": REVIEWED_AT,
                "determination": "rejected",
                "evidence_urls": ["https://official.example/conflict"],
            }
        )
        with self.assertRaisesRegex(core.AuthorityRefreshError, "rejected"):
            promotion.validate_approval(value, review)

    def test_review_cannot_predate_candidate(self):
        value = canonical_candidate()
        review = approval(value)
        review["approvals"][0]["reviewed_at"] = "2026-07-12T23:59:59+00:00"
        with self.assertRaisesRegex(core.AuthorityRefreshError, "cannot precede"):
            promotion.validate_approval(value, review)

    def test_candidate_and_review_timestamps_cannot_be_in_the_future(self):
        value = canonical_candidate()
        value["generated_at"] = "2999-01-01T00:00:00+00:00"
        rehash(value)
        with self.assertRaisesRegex(
            core.AuthorityRefreshError, "generated_at cannot be in the future"
        ):
            promotion.validate_approval(value, approval(value))

        value = canonical_candidate()
        review = approval(value)
        review["approvals"][0]["reviewed_at"] = "2999-01-01T00:00:00+00:00"
        with self.assertRaisesRegex(
            core.AuthorityRefreshError, "reviewed_at cannot be in the future"
        ):
            promotion.validate_approval(value, review)

    def test_evidence_url_requires_a_real_https_host(self):
        value = canonical_candidate()
        review = approval(value)
        review["approvals"][0]["evidence_urls"] = ["https://"]
        with self.assertRaisesRegex(core.AuthorityRefreshError, "HTTPS"):
            promotion.validate_approval(value, review)

    def test_evidence_url_rejects_archived_credentials_and_signed_tokens(self):
        for evidence_url in (
            "https://official.example/review?access_token=do-not-archive",
            "https://official.example/review?key=do-not-archive",
            "https://official.example/review?X-Amz-Signature=do-not-archive",
            "https://official.example/review#token=do-not-archive",
        ):
            with self.subTest(evidence_url=evidence_url):
                value = canonical_candidate()
                review = approval(value)
                review["approvals"][0]["evidence_urls"] = [evidence_url]
                with self.assertRaisesRegex(
                    core.AuthorityRefreshError, "credentials or signed tokens"
                ):
                    promotion.validate_approval(value, review)

    def test_source_coverage_and_catalog_fields_are_not_self_asserted(self):
        value = canonical_candidate()
        value["source_results"].pop()
        rehash(value)
        with self.assertRaisesRegex(core.AuthorityRefreshError, "source coverage"):
            promotion.validate_approval(value, approval(value))

        value = canonical_candidate()
        value["source_results"][0]["critical"] = not value["source_results"][0]["critical"]
        rehash(value)
        with self.assertRaisesRegex(core.AuthorityRefreshError, "canonical source catalog"):
            promotion.validate_approval(value, approval(value))

        value = canonical_candidate()
        value["source_results"][0]["item_count"] = core.DEFAULT_MAXIMUM_ITEMS + 1
        value["source_results"][0]["observed_item_ids"] = [
            f"invented-{index:05d}"
            for index in range(core.DEFAULT_MAXIMUM_ITEMS + 1)
        ]
        rehash(value)
        with self.assertRaisesRegex(core.AuthorityRefreshError, "maximum_items"):
            promotion.validate_approval(value, approval(value))

    def test_observed_item_ids_must_match_count_and_canonical_items(self):
        value = canonical_candidate()
        value["source_results"][0]["item_count"] += 1
        rehash(value)
        with self.assertRaisesRegex(core.AuthorityRefreshError, "must equal"):
            promotion.validate_approval(value, approval(value))

        value = canonical_candidate()
        catalog = core.load_catalog(
            promotion.PACKAGE_DIR / "config" / "legal_sources.json", domain="legal"
        )
        source = catalog["sources"][0]
        extra = core.normalize_item(
            {
                "external_id": "undeclared-extra",
                "title": "Undeclared extra item",
                "official_url": source["discovery_url"],
                "metadata": {},
            },
            source,
            domain="legal",
        )
        forged = core.build_candidate(
            domain="legal",
            generated_at=GENERATED_AT,
            run_id="test-run",
            baseline_path=Path("authority/snapshots/legal.json"),
            baseline={"schema_version": core.SCHEMA_VERSION, "domain": "legal", "items": []},
            baseline_missing=True,
            source_results=value["source_results"],
            items=value["items"] + [extra],
            impact_crosswalk=core.load_impact_crosswalk(
                promotion.REPO_ROOT / "authority" / "impact_crosswalk.json"
            ),
        )
        with self.assertRaisesRegex(core.AuthorityRefreshError, "canonical reconstruction"):
            promotion.validate_approval(forged, approval(forged))

    def test_promotion_rejects_same_count_complete_index_with_zero_overlap(self):
        initial = canonical_candidate()
        baseline = {
            "schema_version": "1.0",
            "domain": "legal",
            "release_id": "2026-07-12-legal-prior",
            "approved_at": "2026-07-12",
            "candidate_sha256": "0" * 64,
            "items": initial["items"],
        }
        catalog = core.load_catalog(
            promotion.PACKAGE_DIR / "config" / "legal_sources.json", domain="legal"
        )
        target = next(
            source
            for source in catalog["sources"]
            if source.get("missing_detection", "complete-index") == "complete-index"
        )
        target_id = target["source_id"]
        baseline_target_items = [
            item for item in initial["items"] if item["source_id"] == target_id
        ]
        replacements = [
            core.normalize_item(
                {
                    "external_id": f"replacement-{index}",
                    "title": f"Replacement {index}",
                    "official_url": target["discovery_url"],
                    "metadata": {},
                },
                target,
                domain="legal",
            )
            for index in range(len(baseline_target_items))
        ]
        observed = [
            item for item in initial["items"] if item["source_id"] != target_id
        ] + replacements
        source_results = json.loads(json.dumps(initial["source_results"]))
        target_result = next(
            result for result in source_results if result["source_id"] == target_id
        )
        target_result["item_count"] = len(replacements)
        target_result["observed_item_ids"] = sorted(
            item["item_id"] for item in replacements
        )
        forged = core.build_candidate(
            domain="legal",
            generated_at=GENERATED_AT,
            run_id="replacement-run",
            baseline_path=Path("authority/snapshots/legal.json"),
            baseline=baseline,
            baseline_missing=False,
            source_results=source_results,
            items=observed,
            impact_crosswalk=core.load_impact_crosswalk(
                promotion.REPO_ROOT / "authority" / "impact_crosswalk.json"
            ),
        )
        with workspace_temp_directory() as directory:
            root = Path(directory)
            snapshot_path = root / "authority" / "snapshots" / "legal.json"
            snapshot_path.parent.mkdir(parents=True)
            snapshot_path.write_text(json.dumps(baseline), encoding="utf-8")

            with self.assertRaisesRegex(
                core.AuthorityRefreshError, "retained 0 approved item"
            ):
                promotion.validate_approval(
                    forged,
                    approval(forged),
                    output_root=root,
                )

    def test_off_host_or_wrong_fingerprint_item_is_rejected_after_rehash(self):
        value = canonical_candidate()
        value["items"][0]["official_url"] = "https://evil.example/forged"
        value["items"][0]["fingerprint"] = "0" * 64
        rehash(value)
        with self.assertRaisesRegex(core.AuthorityRefreshError, "not normalized"):
            promotion.validate_approval(value, approval(value))

    def test_claimed_counts_status_and_impacts_are_recomputed(self):
        for field, mutate in (
            ("counts", lambda value: value["counts"].__setitem__("items", 999)),
            ("status", lambda value: value.__setitem__("status", "current")),
            (
                "potential_impacts",
                lambda value: value["potential_impacts"][0]["review_gate"].__setitem__(
                    "required_roles", []
                ),
            ),
        ):
            with self.subTest(field=field):
                value = canonical_candidate()
                review = approval(value)
                mutate(value)
                rehash(value)
                with self.assertRaisesRegex(core.AuthorityRefreshError, "canonical reconstruction"):
                    promotion.validate_approval(value, review)

    def test_runtime_schema_rejects_extra_fields(self):
        value = canonical_candidate()
        value["invented_override"] = True
        rehash(value)
        with self.assertRaisesRegex(core.AuthorityRefreshError, "extra"):
            promotion.validate_approval(value, approval(value))

        value = canonical_candidate()
        review = approval(value)
        review["bypass"] = True
        with self.assertRaisesRegex(core.AuthorityRefreshError, "extra"):
            promotion.validate_approval(value, review)

        value = canonical_candidate()
        value["source_results"][0]["critical"] = 1
        rehash(value)
        with self.assertRaisesRegex(core.AuthorityRefreshError, "critical must be boolean"):
            promotion.validate_approval(value, approval(value))

        value = canonical_candidate()
        review = approval(value)
        review["approvals"][0]["reviewer"] = 1
        with self.assertRaisesRegex(core.AuthorityRefreshError, "login must be a string"):
            promotion.validate_approval(value, review)

    def test_unresolved_change_and_impact_determinations_block_promotion(self):
        value = canonical_candidate()
        review = approval(value)
        review["change_resolutions"][0]["resolution"] = "future_effective"
        with self.assertRaisesRegex(core.AuthorityRefreshError, "unsupported resolution"):
            promotion.validate_approval(value, review)

        review = approval(value)
        review["impact_resolutions"][0]["determination"] = "blocked_pending_implementation"
        with self.assertRaisesRegex(core.AuthorityRefreshError, "unsupported impact"):
            promotion.validate_approval(value, review)

    def test_check_only_does_not_write_release(self):
        value = canonical_candidate()
        review = approval(value)
        with workspace_temp_directory() as directory:
            root = Path(directory)
            candidate_path = root / "candidate.json"
            approval_path = root / "approval.json"
            candidate_path.write_text(json.dumps(value), encoding="utf-8")
            approval_path.write_text(json.dumps(review), encoding="utf-8")
            write_latest_candidate(root, value)
            release = promotion.promote(
                candidate_path=candidate_path,
                approval_path=approval_path,
                release_date=date(2026, 7, 13),
                output_root=root,
                confirmation=None,
                now=CURRENT_TIME,
            )
            self.assertIn(value["candidate_sha256"][:12], release["release_id"])
            self.assertFalse((root / "authority" / "releases").exists())
            self.assertFalse((root / "authority" / "snapshots").exists())

    def test_confirmed_promotion_writes_immutable_release_and_snapshot(self):
        value = canonical_candidate()
        review = approval(value)
        with workspace_temp_directory() as directory:
            root = Path(directory)
            candidate_path = root / "candidate.json"
            approval_path = root / "approval.json"
            candidate_path.write_text(json.dumps(value), encoding="utf-8")
            approval_path.write_text(json.dumps(review), encoding="utf-8")
            write_latest_candidate(root, value)
            release = promotion.promote(
                candidate_path=candidate_path,
                approval_path=approval_path,
                release_date=date(2026, 7, 13),
                output_root=root,
                confirmation=promotion.CONFIRMATION,
                now=CURRENT_TIME,
            )
            release_dir = root / "authority" / "releases" / release["release_id"]
            self.assertTrue((release_dir / "candidate.json").is_file())
            self.assertTrue((release_dir / "approval.json").is_file())
            snapshot = json.loads(
                (root / "authority" / "snapshots" / "legal.json").read_text(encoding="utf-8")
            )
            self.assertEqual(value["items"], snapshot["items"])

    def test_candidate_is_stale_when_a_previously_missing_snapshot_now_exists(self):
        value = canonical_candidate()
        review = approval(value)
        with workspace_temp_directory() as directory:
            root = Path(directory)
            candidate_path = root / "candidate.json"
            approval_path = root / "approval.json"
            snapshot_path = root / "authority" / "snapshots" / "legal.json"
            snapshot_path.parent.mkdir(parents=True)
            snapshot_path.write_text(json.dumps({"domain": "legal", "items": []}), encoding="utf-8")
            candidate_path.write_text(json.dumps(value), encoding="utf-8")
            approval_path.write_text(json.dumps(review), encoding="utf-8")
            write_latest_candidate(root, value)

            with self.assertRaisesRegex(core.AuthorityRefreshError, "stale"):
                promotion.promote(
                    candidate_path=candidate_path,
                    approval_path=approval_path,
                    release_date=date(2026, 7, 13),
                    output_root=root,
                    confirmation=None,
                    now=CURRENT_TIME,
                )

    def test_candidate_is_stale_when_approved_snapshot_hash_changed(self):
        original = {"schema_version": "1.0", "domain": "legal", "items": []}
        value = canonical_candidate()
        value["approved_baseline"] = {
            "path": "authority/snapshots/legal.json",
            "missing": False,
            "sha256": core.sha256_json(original),
        }
        rehash(value)
        review = approval(value)
        with workspace_temp_directory() as directory:
            root = Path(directory)
            candidate_path = root / "candidate.json"
            approval_path = root / "approval.json"
            snapshot_path = root / "authority" / "snapshots" / "legal.json"
            snapshot_path.parent.mkdir(parents=True)
            changed = {"schema_version": "1.0", "domain": "legal", "items": [{"id": "new"}]}
            snapshot_path.write_text(json.dumps(changed), encoding="utf-8")
            candidate_path.write_text(json.dumps(value), encoding="utf-8")
            approval_path.write_text(json.dumps(review), encoding="utf-8")
            write_latest_candidate(root, value)

            with self.assertRaisesRegex(core.AuthorityRefreshError, "stale"):
                promotion.promote(
                    candidate_path=candidate_path,
                    approval_path=approval_path,
                    release_date=date(2026, 7, 13),
                    output_root=root,
                    confirmation=None,
                    now=CURRENT_TIME,
                )

    def test_candidate_and_release_cannot_precede_approved_baseline(self):
        for baseline_date, release_date, expected in (
            ("2026-07-14", date(2026, 7, 14), "generated_at cannot precede"),
            ("2026-07-13", date(2026, 7, 12), "release-date cannot precede"),
        ):
            with self.subTest(baseline_date=baseline_date, release_date=release_date):
                baseline = {
                    "schema_version": "1.0",
                    "domain": "legal",
                    "release_id": f"{baseline_date}-legal-prior",
                    "approved_at": baseline_date,
                    "candidate_sha256": "0" * 64,
                    "items": [],
                }
                value = canonical_candidate()
                value["approved_baseline"] = {
                    "path": "authority/snapshots/legal.json",
                    "missing": False,
                    "sha256": core.sha256_json(baseline),
                }
                rehash(value)
                review = approval(value)
                with workspace_temp_directory() as directory:
                    root = Path(directory)
                    snapshot_path = root / "authority" / "snapshots" / "legal.json"
                    snapshot_path.parent.mkdir(parents=True)
                    snapshot_path.write_text(json.dumps(baseline), encoding="utf-8")
                    candidate_path = root / "candidate.json"
                    approval_path = root / "approval.json"
                    candidate_path.write_text(json.dumps(value), encoding="utf-8")
                    approval_path.write_text(json.dumps(review), encoding="utf-8")
                    write_latest_candidate(root, value)

                    with self.assertRaisesRegex(core.AuthorityRefreshError, expected):
                        promotion.promote(
                            candidate_path=candidate_path,
                            approval_path=approval_path,
                            release_date=release_date,
                            output_root=root,
                            confirmation=None,
                            now=CURRENT_TIME,
                        )

    def test_promotion_requires_latest_merged_and_recent_candidate(self):
        value = canonical_candidate()
        review = approval(value)
        with workspace_temp_directory() as directory:
            root = Path(directory)
            candidate_path = root / "candidate.json"
            approval_path = root / "approval.json"
            candidate_path.write_text(json.dumps(value), encoding="utf-8")
            approval_path.write_text(json.dumps(review), encoding="utf-8")
            different = canonical_candidate(domain="accounting")
            latest_path = root / "authority" / "candidates" / "legal" / "latest"
            latest_path.mkdir(parents=True)
            (latest_path / "candidate.json").write_text(
                json.dumps(different), encoding="utf-8"
            )

            with self.assertRaisesRegex(core.AuthorityRefreshError, "not the latest"):
                promotion.promote(
                    candidate_path=candidate_path,
                    approval_path=approval_path,
                    release_date=date(2026, 7, 13),
                    output_root=root,
                    confirmation=None,
                    now=CURRENT_TIME,
                )

            write_latest_candidate(root, value)
            with self.assertRaisesRegex(core.AuthorityRefreshError, "older than 7 days"):
                promotion.promote(
                    candidate_path=candidate_path,
                    approval_path=approval_path,
                    release_date=date(2026, 7, 13),
                    output_root=root,
                    confirmation=None,
                    now=datetime(2026, 7, 21, 0, 0, tzinfo=timezone.utc),
                )


if __name__ == "__main__":
    unittest.main()
