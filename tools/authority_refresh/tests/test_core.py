from __future__ import annotations

import io
import json
import unittest
import unittest.mock
from pathlib import Path

from tools.authority_refresh import core
from test_support import workspace_temp_directory


class FakeResponse:
    def __init__(self, payload: bytes, url: str, content_type: str = "application/json"):
        self._stream = io.BytesIO(payload)
        self._url = url
        self.headers = {"Content-Type": content_type, "Content-Length": str(len(payload))}

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, size: int = -1) -> bytes:
        return self._stream.read(size)

    def geturl(self) -> str:
        return self._url


def source(**updates):
    value = {
        "source_id": "official-index",
        "publisher": "Official Publisher",
        "jurisdiction": "Kansas",
        "authority_type": "official-index",
        "discovery_url": "https://official.example/index.json",
        "adapter": "fixture",
        "storage_policy": "metadata-only",
        "cadence": "daily",
        "critical": True,
        "allowed_hosts": ["official.example"],
        "request": {"max_bytes": 1024, "attempts": 1},
    }
    value.update(updates)
    return value


def raw_item(**updates):
    value = {
        "external_id": "item-1",
        "title": "Official item",
        "official_url": "https://official.example/items/1",
        "published_at": "2026-07-13",
        "effective_at": None,
        "status": "discovered",
        "metadata": {},
    }
    value.update(updates)
    return value


class CatalogTests(unittest.TestCase):
    def test_catalog_rejects_nonallowlisted_discovery_host(self):
        with workspace_temp_directory() as directory:
            path = Path(directory) / "catalog.json"
            path.write_text(
                json.dumps(
                    {
                        "allowed_domains": ["official.example"],
                        "sources": [source(discovery_url="https://evil.example/index")],
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(core.AuthorityRefreshError, "allowlisted"):
                core.load_catalog(path, domain="legal")

    def test_catalog_rejects_redistributable_fasb_source(self):
        with workspace_temp_directory() as directory:
            path = Path(directory) / "catalog.json"
            path.write_text(
                json.dumps(
                    {
                        "allowed_domains": ["official.example"],
                        "sources": [
                            source(
                                publisher="Financial Accounting Standards Board (FASB)",
                                storage_policy="redistributable",
                            )
                        ],
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(core.AuthorityRefreshError, "FASB"):
                core.load_catalog(path, domain="accounting")

    def test_catalog_rejects_invalid_missing_detection_policy(self):
        with workspace_temp_directory() as directory:
            path = Path(directory) / "catalog.json"
            path.write_text(
                json.dumps(
                    {
                        "allowed_domains": ["official.example"],
                        "sources": [source(missing_detection="guess")],
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(core.AuthorityRefreshError, "missing_detection"):
                core.load_catalog(path, domain="legal")

    def test_catalog_rejects_unsafe_request_limits(self):
        for setting, value in (
            ("timeout_seconds", 0),
            ("max_bytes", -1),
            ("attempts", core.MAX_ATTEMPTS + 1),
        ):
            with self.subTest(setting=setting), workspace_temp_directory() as directory:
                path = Path(directory) / "catalog.json"
                configured = source(request={setting: value})
                path.write_text(
                    json.dumps(
                        {
                            "allowed_domains": ["official.example"],
                            "sources": [configured],
                        }
                    ),
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(core.AuthorityRefreshError, setting):
                    core.load_catalog(path, domain="legal")

    def test_complete_index_requires_a_nonzero_baseline_coverage_ratio(self):
        with workspace_temp_directory() as directory:
            path = Path(directory) / "catalog.json"
            path.write_text(
                json.dumps(
                    {
                        "allowed_domains": ["official.example"],
                        "sources": [source(minimum_baseline_ratio=0)],
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(core.AuthorityRefreshError, "baseline_ratio"):
                core.load_catalog(path, domain="legal")

    def test_catalog_rejects_unsafe_maximum_items(self):
        with workspace_temp_directory() as directory:
            path = Path(directory) / "catalog.json"
            path.write_text(
                json.dumps(
                    {
                        "allowed_domains": ["official.example"],
                        "sources": [source(minimum_items=2, maximum_items=1)],
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(core.AuthorityRefreshError, "maximum_items"):
                core.load_catalog(path, domain="legal")


class FetchTests(unittest.TestCase):
    def test_fetch_revalidates_redirect_host_without_leaking_api_key(self):
        sensitive_value = "-".join(("top", "secret"))
        redirect_url = "".join(
            ("https://evil.example/redirect?", "api", "_key=", sensitive_value)
        )

        def opener(request, **kwargs):
            return FakeResponse(
                b"{}",
                redirect_url,
            )

        configured = source(
            request={
                "max_bytes": 1024,
                "attempts": 1,
                "api_key_env": "TEST_AUTHORITY_API_KEY",
                "api_key_required": True,
                "api_key_query_param": "api_key",
            }
        )
        with unittest.mock.patch.dict(
            "os.environ", {"TEST_AUTHORITY_API_KEY": sensitive_value}
        ):
            with self.assertRaisesRegex(core.AuthorityRefreshError, "fetch failed") as caught:
                core.fetch_source(configured, opener=opener, sleep=lambda _: None)
        self.assertNotIn(sensitive_value, str(caught.exception))

    def test_redirect_handler_blocks_off_host_target_before_creating_request(self):
        handler = core._AllowlistedRedirectHandler(["official.example"])
        request = core.urllib.request.Request("https://official.example/index.json")

        with unittest.mock.patch.object(
            core.urllib.request.HTTPRedirectHandler,
            "redirect_request",
        ) as parent_redirect:
            with self.assertRaisesRegex(core.AuthorityRefreshError, "allowlisted"):
                handler.redirect_request(
                    request,
                    None,
                    302,
                    "Found",
                    {},
                    "https://evil.example/internal",
                )
        parent_redirect.assert_not_called()

    def test_official_url_allowlist_is_exact_and_errors_omit_query(self):
        sensitive_value = "-".join(("top", "secret"))
        unsafe_url = "".join(
            ("https://child.official.example/path?", "api", "_key=", sensitive_value)
        )
        with self.assertRaisesRegex(core.AuthorityRefreshError, "allowlisted") as caught:
            core.validate_official_url(
                unsafe_url,
                ["official.example"],
            )
        self.assertNotIn(sensitive_value, str(caught.exception))

    def test_fetch_does_not_return_api_key(self):
        captured = []

        def opener(request, **kwargs):
            captured.append(request.full_url)
            return FakeResponse(request.data or b"{}", request.full_url)

        configured = source(
            request={
                "max_bytes": 1024,
                "attempts": 1,
                "api_key_env": "TEST_AUTHORITY_API_KEY",
                "api_key_required": True,
                "api_key_query_param": "api_key",
            }
        )
        with unittest.mock.patch.dict(
            "os.environ", {"TEST_AUTHORITY_API_KEY": "top-secret"}
        ):
            result = core.fetch_source(configured, opener=opener, sleep=lambda _: None)
        self.assertIn("top-secret", captured[0])
        self.assertNotIn("top-secret", result.final_url)
        self.assertIn("REDACTED", result.final_url)

    def test_fetch_redacts_secret_value_if_redirect_renames_query_parameter(self):
        def opener(request, **kwargs):
            return FakeResponse(
                b"{}",
                "https://official.example/redirect?token=top-secret",
            )

        configured = source(
            request={
                "max_bytes": 1024,
                "attempts": 1,
                "api_key_env": "TEST_AUTHORITY_API_KEY",
                "api_key_required": True,
                "api_key_query_param": "api_key",
            }
        )
        with unittest.mock.patch.dict(
            "os.environ", {"TEST_AUTHORITY_API_KEY": "top-secret"}
        ):
            result = core.fetch_source(configured, opener=opener, sleep=lambda _: None)

        self.assertNotIn("top-secret", result.final_url)
        self.assertIn("REDACTED", result.final_url)


class CandidateTests(unittest.TestCase):
    def test_item_fingerprint_excludes_retrieval_telemetry(self):
        first = core.normalize_item(
            raw_item(metadata={"fetched_at": "2026-07-13T00:00:00+00:00", "version": 1}),
            source(),
            domain="legal",
        )
        second = core.normalize_item(
            raw_item(metadata={"fetched_at": "2026-07-14T00:00:00+00:00", "version": 1}),
            source(),
            domain="legal",
        )
        self.assertEqual(first["fingerprint"], second["fingerprint"])
        self.assertNotIn("fetched_at", first["metadata"])

    def test_ecfr_currency_date_is_evidence_not_a_daily_change_signal(self):
        first = core.normalize_item(
            raw_item(metadata={"up_to_date_as_of": "2026-07-12"}),
            source(),
            domain="legal",
        )
        second = core.normalize_item(
            raw_item(metadata={"up_to_date_as_of": "2026-07-13"}),
            source(),
            domain="legal",
        )

        self.assertEqual(first["fingerprint"], second["fingerprint"])
        self.assertEqual("2026-07-13", second["metadata"]["up_to_date_as_of"])

    def test_failed_source_does_not_create_false_missing_change(self):
        before = core.normalize_item(raw_item(), source(), domain="legal")
        changes = core.compare_items([before], [], healthy_sources=set())
        self.assertEqual([], changes)

    def test_rolling_window_source_does_not_create_false_missing_change(self):
        before = core.normalize_item(raw_item(), source(), domain="legal")
        candidate = core.build_candidate(
            domain="legal",
            generated_at="2026-07-13T00:00:00+00:00",
            run_id="test",
            baseline_path=Path("authority/snapshots/legal.json"),
            baseline={"domain": "legal", "items": [before]},
            baseline_missing=False,
            source_results=[
                {
                    "source_id": "official-index",
                    "status": "healthy",
                    "critical": True,
                    "missing_detection": "rolling-window",
                    "item_count": 0,
                    "observed_item_ids": [],
                }
            ],
            items=[],
        )
        self.assertEqual([], candidate["changes"])
        self.assertEqual("current", candidate["status"])
        self.assertEqual([before], candidate["items"])

    def test_optional_unavailable_source_item_is_retained_during_other_changes(self):
        congress_source = source(
            source_id="congress-api",
            critical=False,
        )
        govinfo_source = source(source_id="govinfo-laws")
        congress_item = core.normalize_item(
            raw_item(external_id="bill-1"),
            congress_source,
            domain="legal",
        )
        new_law = core.normalize_item(
            raw_item(external_id="law-2"),
            govinfo_source,
            domain="legal",
        )
        candidate = core.build_candidate(
            domain="legal",
            generated_at="2026-07-13T00:00:00+00:00",
            run_id="test",
            baseline_path=Path("authority/snapshots/legal.json"),
            baseline={"domain": "legal", "items": [congress_item]},
            baseline_missing=False,
            source_results=[
                {
                    "source_id": "congress-api",
                    "status": "configuration_required",
                    "critical": False,
                    "missing_detection": "rolling-window",
                    "item_count": 0,
                    "observed_item_ids": [],
                },
                {
                    "source_id": "govinfo-laws",
                    "status": "healthy",
                    "critical": True,
                    "missing_detection": "complete-index",
                    "item_count": 1,
                    "observed_item_ids": [new_law["item_id"]],
                },
            ],
            items=[new_law],
        )

        self.assertEqual("review_required", candidate["status"])
        self.assertEqual(
            {congress_item["item_id"], new_law["item_id"]},
            {item["item_id"] for item in candidate["items"]},
        )
        self.assertEqual(
            ["new"],
            [change["change_type"] for change in candidate["changes"]],
        )

    def test_scan_fails_closed_when_parser_silently_returns_too_few_items(self):
        with workspace_temp_directory() as directory:
            root = Path(directory)
            catalog = root / "catalog.json"
            catalog.write_text(
                json.dumps(
                    {
                        "allowed_domains": ["official.example"],
                        "sources": [source(fixture_filename="official.json")],
                    }
                ),
                encoding="utf-8",
            )
            fixtures = root / "fixtures"
            fixtures.mkdir()
            (fixtures / "official.json").write_text("{}", encoding="utf-8")

            candidate, exit_code = core.scan_domain(
                domain="legal",
                catalog_path=catalog,
                baseline_path=root / "missing-baseline.json",
                parser=lambda *_: [],
                output_dir=root / "output",
                run_id="fixture",
                fixture_dir=fixtures,
            )
            self.assertEqual(3, exit_code)
            self.assertEqual("degraded", candidate["status"])
            self.assertIn("minimum_items", candidate["source_results"][0]["error"])
            self.assertEqual([], candidate["source_results"][0]["observed_item_ids"])
            self.assertEqual(
                "authority/snapshots/legal.json",
                candidate["approved_baseline"]["path"],
            )

    def test_complete_index_fails_closed_below_baseline_coverage_floor(self):
        with workspace_temp_directory() as directory:
            root = Path(directory)
            configured_source = source(
                fixture_filename="official.json",
                minimum_baseline_ratio=0.8,
            )
            catalog = root / "catalog.json"
            catalog.write_text(
                json.dumps(
                    {
                        "allowed_domains": ["official.example"],
                        "sources": [configured_source],
                    }
                ),
                encoding="utf-8",
            )
            baseline_items = [
                core.normalize_item(
                    raw_item(
                        external_id=f"item-{index}",
                        official_url=f"https://official.example/items/{index}",
                    ),
                    configured_source,
                    domain="legal",
                )
                for index in range(10)
            ]
            baseline = root / "baseline.json"
            baseline.write_text(
                json.dumps({"domain": "legal", "items": baseline_items}),
                encoding="utf-8",
            )
            fixtures = root / "fixtures"
            fixtures.mkdir()
            (fixtures / "official.json").write_text("{}", encoding="utf-8")

            candidate, exit_code = core.scan_domain(
                domain="legal",
                catalog_path=catalog,
                baseline_path=baseline,
                parser=lambda *_: [raw_item()],
                output_dir=root / "output",
                run_id="partial-index",
                fixture_dir=fixtures,
            )

            self.assertEqual(3, exit_code)
            self.assertEqual("degraded", candidate["status"])
            self.assertIn("baseline coverage floor", candidate["source_results"][0]["error"])
            self.assertEqual(10, len(candidate["items"]))
            self.assertEqual([], candidate["changes"])

    def test_source_and_domain_item_limits_fail_closed(self):
        for source_limit, domain_limit, expected in (
            (2, core.MAXIMUM_ITEMS_PER_DOMAIN, "maximum_items"),
            (10, 2, "domain discovery"),
        ):
            with self.subTest(expected=expected), workspace_temp_directory() as directory:
                root = Path(directory)
                configured_source = source(
                    fixture_filename="official.json",
                    maximum_items=source_limit,
                )
                catalog = root / "catalog.json"
                catalog.write_text(
                    json.dumps(
                        {
                            "allowed_domains": ["official.example"],
                            "sources": [configured_source],
                        }
                    ),
                    encoding="utf-8",
                )
                fixtures = root / "fixtures"
                fixtures.mkdir()
                (fixtures / "official.json").write_text("{}", encoding="utf-8")
                parsed = [
                    raw_item(
                        external_id=f"item-{index}",
                        official_url=f"https://official.example/items/{index}",
                    )
                    for index in range(3)
                ]
                with unittest.mock.patch.object(
                    core, "MAXIMUM_ITEMS_PER_DOMAIN", domain_limit
                ):
                    candidate, exit_code = core.scan_domain(
                        domain="legal",
                        catalog_path=catalog,
                        baseline_path=root / "missing.json",
                        parser=lambda *_: parsed,
                        output_dir=root / "output",
                        run_id="oversize-items",
                        fixture_dir=fixtures,
                    )
                self.assertEqual(3, exit_code)
                self.assertEqual("degraded", candidate["status"])
                self.assertIn(expected, candidate["source_results"][0]["error"])

    def test_candidate_file_size_limit_fails_before_writing(self):
        with workspace_temp_directory() as directory:
            root = Path(directory)
            catalog = root / "catalog.json"
            catalog.write_text(
                json.dumps(
                    {
                        "allowed_domains": ["official.example"],
                        "sources": [source(fixture_filename="official.json")],
                    }
                ),
                encoding="utf-8",
            )
            fixtures = root / "fixtures"
            fixtures.mkdir()
            (fixtures / "official.json").write_text("{}", encoding="utf-8")
            with unittest.mock.patch.object(core, "MAX_CANDIDATE_JSON_BYTES", 100):
                with self.assertRaisesRegex(core.AuthorityRefreshError, "candidate JSON"):
                    core.scan_domain(
                        domain="legal",
                        catalog_path=catalog,
                        baseline_path=root / "missing.json",
                        parser=lambda *_: [raw_item()],
                        output_dir=root / "output",
                        run_id="oversize-file",
                        fixture_dir=fixtures,
                    )
            self.assertFalse((root / "output").exists())

    def test_issue_summary_limit_is_utf8_bytes(self):
        candidate = core.build_candidate(
            domain="legal",
            generated_at="2026-07-13T00:00:00+00:00",
            run_id="unicode",
            baseline_path=Path("authority/snapshots/legal.json"),
            baseline={"domain": "legal", "items": []},
            baseline_missing=True,
            source_results=[
                {
                    "source_id": "official-index",
                    "status": "error",
                    "critical": True,
                    "item_count": 0,
                    "observed_item_ids": [],
                    "error": "\U0001f642" * 10_000,
                }
            ],
            items=[],
        )
        report = core.bounded_issue_markdown(candidate)
        self.assertLessEqual(len(report.encode("utf-8")), 20_000)
        self.assertIn("Summary truncated", report)

    def test_complete_index_fails_closed_on_same_count_with_zero_id_overlap(self):
        with workspace_temp_directory() as directory:
            root = Path(directory)
            configured_source = source(
                fixture_filename="official.json",
                minimum_baseline_ratio=0.8,
            )
            catalog = root / "catalog.json"
            catalog.write_text(
                json.dumps(
                    {
                        "allowed_domains": ["official.example"],
                        "sources": [configured_source],
                    }
                ),
                encoding="utf-8",
            )
            baseline_items = [
                core.normalize_item(
                    raw_item(external_id=f"approved-{index}"),
                    configured_source,
                    domain="legal",
                )
                for index in range(10)
            ]
            baseline = root / "baseline.json"
            baseline.write_text(
                json.dumps({"domain": "legal", "items": baseline_items}),
                encoding="utf-8",
            )
            fixtures = root / "fixtures"
            fixtures.mkdir()
            (fixtures / "official.json").write_text("{}", encoding="utf-8")

            candidate, exit_code = core.scan_domain(
                domain="legal",
                catalog_path=catalog,
                baseline_path=baseline,
                parser=lambda *_: [
                    raw_item(external_id=f"replacement-{index}") for index in range(10)
                ],
                output_dir=root / "output",
                run_id="replaced-index",
                fixture_dir=fixtures,
            )

            self.assertEqual(3, exit_code)
            self.assertEqual("degraded", candidate["status"])
            self.assertIn(
                "retained 0 approved item(s)",
                candidate["source_results"][0]["error"],
            )
            self.assertEqual(
                {item["item_id"] for item in baseline_items},
                {item["item_id"] for item in candidate["items"]},
            )
            self.assertEqual([], candidate["changes"])

    def test_candidate_is_degraded_when_critical_source_fails(self):
        candidate = core.build_candidate(
            domain="legal",
            generated_at="2026-07-13T00:00:00+00:00",
            run_id="test",
            baseline_path=Path("authority/snapshots/legal.json"),
            baseline={"domain": "legal", "items": []},
            baseline_missing=True,
            source_results=[
                {
                    "source_id": "official-index",
                    "status": "error",
                    "critical": True,
                    "item_count": 0,
                    "observed_item_ids": [],
                }
            ],
            items=[],
        )
        self.assertEqual("degraded", candidate["status"])
        self.assertEqual(1, candidate["counts"]["source_errors"])

    def test_candidate_routes_domain_changes_through_conservative_crosswalk(self):
        impact_crosswalk = {
            "mappings": [
                {
                    "id": "late-fees",
                    "name": "Late fees",
                    "authority_references": [
                        {"domain": "legal", "reference": "landlord-tenant"}
                    ],
                    "affected_paths": [
                        {"repository_path": "src/late-fee.deluge"}
                    ],
                    "review_gate": {"required_roles": ["kansas-counsel"]},
                    "automatic_change": "prohibited",
                    "fail_closed_action": "block-affected-release-and-preserve-production",
                },
                {
                    "id": "tax",
                    "name": "Tax",
                    "authority_references": [
                        {"domain": "tax", "reference": "IRS"}
                    ],
                    "affected_paths": [
                        {"repository_path": "accounting/policy.md"}
                    ],
                    "review_gate": {"required_roles": ["tax-professional"]},
                    "automatic_change": "prohibited",
                    "fail_closed_action": "open-review-and-preserve-approved-baseline",
                },
            ]
        }
        item = core.normalize_item(raw_item(), source(), domain="legal")
        candidate = core.build_candidate(
            domain="legal",
            generated_at="2026-07-13T00:00:00+00:00",
            run_id="test",
            baseline_path=Path("authority/snapshots/legal.json"),
            baseline={"domain": "legal", "items": []},
            baseline_missing=True,
            source_results=[
                {
                    "source_id": "official-index",
                    "status": "healthy",
                    "critical": True,
                    "item_count": 1,
                    "observed_item_ids": [item["item_id"]],
                }
            ],
            items=[item],
            impact_crosswalk=impact_crosswalk,
        )
        self.assertEqual(["late-fees"], [i["mapping_id"] for i in candidate["potential_impacts"]])
        self.assertEqual("prohibited", candidate["potential_impacts"][0]["automatic_change"])

    def test_scan_writes_deterministic_candidate_reports(self):
        with workspace_temp_directory() as directory:
            root = Path(directory)
            catalog = root / "catalog.json"
            catalog.write_text(
                json.dumps(
                    {
                        "allowed_domains": ["official.example"],
                        "sources": [source(fixture_filename="official.json")],
                    }
                ),
                encoding="utf-8",
            )
            fixtures = root / "fixtures"
            fixtures.mkdir()
            (fixtures / "official.json").write_text("{}", encoding="utf-8")

            def parser(payload, configured, fetched_at, final_url):
                return [raw_item()]

            candidate, exit_code = core.scan_domain(
                domain="legal",
                catalog_path=catalog,
                baseline_path=root / "missing-baseline.json",
                parser=parser,
                output_dir=root / "output",
                run_id="fixture",
                fixture_dir=fixtures,
            )
            self.assertEqual(2, exit_code)
            self.assertEqual("review_required", candidate["status"])
            self.assertEqual(
                [candidate["items"][0]["item_id"]],
                candidate["source_results"][0]["observed_item_ids"],
            )
            self.assertTrue((root / "output" / "legal-candidate.json").is_file())
            self.assertTrue((root / "output" / "legal-candidate.md").is_file())


if __name__ == "__main__":
    unittest.main()
