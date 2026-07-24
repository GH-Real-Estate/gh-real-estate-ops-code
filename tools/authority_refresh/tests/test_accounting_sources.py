"""Offline tests for metadata-only accounting source discovery."""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from urllib.parse import urlsplit

from tools.authority_refresh import accounting_sources, core


HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures" / "accounting"
CONFIG = HERE.parent / "config" / "accounting_sources.json"


def _fixture(name: str) -> bytes:
    return (FIXTURES / name).read_bytes()


def _source(
    adapter: str,
    *,
    discovery_url: str = "https://www.fasb.org/standards/accounting-standard-updates",
    allowed_hosts: list[str] | None = None,
    publisher: str = "Financial Accounting Standards Board (FASB)",
    storage_policy: str = "metadata-only",
) -> dict[str, object]:
    return {
        "source_id": f"test_{adapter}",
        "publisher": publisher,
        "jurisdiction": "United States",
        "authority_type": "test-index",
        "discovery_url": discovery_url,
        "adapter": adapter,
        "storage_policy": storage_policy,
        "cadence": "daily",
        "critical": True,
        "allowed_hosts": allowed_hosts
        or ["fasb.org", "www.fasb.org", "storage.fasb.org"],
        "request": {"max_bytes": 1_000_000},
    }


class AccountingSourcesConfigTests(unittest.TestCase):
    def test_config_uses_official_allowlists_and_safe_fasb_storage(self) -> None:
        config = core.load_catalog(CONFIG, domain="accounting")
        required = {
            "source_id",
            "publisher",
            "jurisdiction",
            "authority_type",
            "discovery_url",
            "adapter",
            "storage_policy",
            "cadence",
            "critical",
            "allowed_hosts",
        }
        configured_ids: set[str] = set()
        for source in config["sources"]:
            self.assertLessEqual(required, set(source.keys()))
            self.assertNotIn(source["source_id"], configured_ids)
            configured_ids.add(source["source_id"])
            discovery_host = urlsplit(source["discovery_url"]).hostname
            self.assertEqual("https", urlsplit(source["discovery_url"]).scheme)
            self.assertIn(discovery_host, source["allowed_hosts"])
            self.assertLessEqual(
                set(source["allowed_hosts"]), set(config["allowed_domains"])
            )
            if "fasb" in source["publisher"].lower():
                self.assertIn(
                    source["storage_policy"], {"metadata-only", "licensed-no-store"}
                )
                self.assertNotEqual("asc.fasb.org", discovery_host)

        required_ids = {
            "fasb-accounting-standards-updates",
            "fasb-effective-dates",
            "fasb-current-projects",
            "fasb-taxonomy-resources",
            "irs-internal-revenue-bulletins",
            "treasury-accounting-and-tax-releases",
            "kansas-revenue-current-tax-notices",
        }
        self.assertEqual(required_ids, required_ids & configured_ids)

    def test_adapter_output_normalizes_through_shared_core(self) -> None:
        catalog = core.load_catalog(CONFIG, domain="accounting")
        source = next(
            source
            for source in catalog["sources"]
            if source["source_id"] == "fasb-accounting-standards-updates"
        )
        raw_items = accounting_sources.parse(
            _fixture("fasb_asu_index.html"),
            source,
            "2026-07-13T20:00:00Z",
            source["discovery_url"],
        )
        normalized = [
            core.normalize_item(item, source, domain="accounting")
            for item in raw_items
        ]
        self.assertTrue(all(item["status"] == "discovered" for item in normalized))
        self.assertTrue(all(item["storage_policy"] == "metadata-only" for item in normalized))


class AccountingSourcesParserTests(unittest.TestCase):
    fetched_at = "2026-07-13T20:00:00Z"

    def test_fasb_asu_metadata_filters_official_hosts_and_duplicates(self) -> None:
        source = _source("fasb_asu_index")
        items = accounting_sources.parse(
            _fixture("fasb_asu_index.html"),
            source,
            self.fetched_at,
            source["discovery_url"],
        )
        self.assertEqual(
            ["FASB-ASU-2026-01", "FASB-ASU-2026-02"],
            [item["external_id"] for item in items],
        )
        self.assertTrue(
            all(urlsplit(item["official_url"]).hostname in source["allowed_hosts"] for item in items)
        )
        self.assertEqual(2, len(items))
        self.assertEqual(
            {
                "external_id",
                "title",
                "official_url",
                "published_at",
                "effective_at",
                "status",
                "metadata",
            },
            set(items[0]),
        )

    def test_fasb_payload_never_stores_codification_body_text(self) -> None:
        source = _source("fasb_asu_index")
        items = accounting_sources.parse(
            _fixture("fasb_asu_index.html"),
            source,
            self.fetched_at,
            source["discovery_url"],
        )
        serialized = json.dumps(items).lower()
        self.assertNotIn("copyrighted codification paragraph", serialized)
        self.assertNotIn("asc 842-10-25-1", serialized)
        for item in items:
            self.assertFalse({"body", "content", "summary", "codification_text"} & set(item))
            self.assertFalse(
                {"body", "content", "summary", "codification_text"}
                & set(item["metadata"])
            )

    def test_fasb_unsafe_storage_policy_fails_closed(self) -> None:
        source = _source("fasb_asu_index", storage_policy="full-text-copy")
        with self.assertRaises(accounting_sources.SourceConfigurationError):
            accounting_sources.parse(
                _fixture("fasb_asu_index.html"),
                source,
                self.fetched_at,
                source["discovery_url"],
            )

    def test_fasb_host_detection_requires_dns_label_boundary(self) -> None:
        source = _source(
            "treasury_press_index",
            discovery_url="https://notfasb.org/publications",
            allowed_hosts=["notfasb.org"],
            publisher="Independent Accounting Publisher",
            storage_policy="full-text-copy",
        )
        self.assertEqual(
            [],
            accounting_sources.parse(
                b"<html></html>",
                source,
                self.fetched_at,
                source["discovery_url"],
            ),
        )

    def test_fasb_host_detection_handles_apex_subdomain_and_trailing_dot(
        self,
    ) -> None:
        for host in ("fasb.org", "updates.fasb.org", "updates.fasb.org."):
            with self.subTest(host=host):
                source = _source(
                    "fasb_asu_index",
                    discovery_url=f"https://{host}/standards",
                    allowed_hosts=[host.rstrip(".")],
                    publisher="Independent Accounting Publisher",
                    storage_policy="full-text-copy",
                )
                with self.assertRaisesRegex(
                    accounting_sources.SourceConfigurationError,
                    "FASB discovery is restricted",
                ):
                    accounting_sources.parse(
                        b"<html></html>",
                        source,
                        self.fetched_at,
                        source["discovery_url"],
                    )

    def test_fasb_codification_application_is_not_a_discovery_source(self) -> None:
        source = _source(
            "fasb_asu_index",
            discovery_url="https://asc.fasb.org/",
            allowed_hosts=["asc.fasb.org"],
        )
        with self.assertRaises(accounting_sources.SourceConfigurationError):
            accounting_sources.parse(
                b"<html></html>", source, self.fetched_at, source["discovery_url"]
            )

    def test_malformed_html_is_tolerated_without_accepting_off_host_link(self) -> None:
        source = _source("fasb_asu_index")
        items = accounting_sources.parse(
            _fixture("fasb_malformed.html"),
            source,
            self.fetched_at,
            source["discovery_url"],
        )
        self.assertEqual(["FASB-ASU-2026-03"], [item["external_id"] for item in items])

    def test_off_host_final_redirect_fails_closed(self) -> None:
        source = _source("fasb_asu_index")
        with self.assertRaises(accounting_sources.SourceConfigurationError):
            accounting_sources.parse(
                _fixture("fasb_asu_index.html"),
                source,
                self.fetched_at,
                "https://example.com/captive-portal",
            )

    def test_nonstandard_https_port_fails_closed(self) -> None:
        source = _source("fasb_asu_index")
        with self.assertRaises(accounting_sources.SourceConfigurationError):
            accounting_sources.parse(
                _fixture("fasb_asu_index.html"),
                source,
                self.fetched_at,
                "https://www.fasb.org:444/standards/accounting-standard-updates",
            )

    def test_fasb_effective_dates_are_evidence_not_applicability(self) -> None:
        source = _source(
            "fasb_effective_dates",
            discovery_url=(
                "https://www.fasb.org/standards/"
                "accounting-standard-updated-effective-date"
            ),
        )
        items = accounting_sources.parse(
            _fixture("fasb_effective_dates.html"),
            source,
            self.fetched_at,
            source["discovery_url"],
        )
        self.assertEqual(1, len(items))
        self.assertEqual("2026-05-19", items[0]["published_at"])
        self.assertIsNone(items[0]["effective_at"])
        self.assertEqual(
            ["2027-12-15", "2028-12-15"],
            items[0]["metadata"]["effective_date_mentions"],
        )
        self.assertTrue(items[0]["metadata"]["entity_specific_dates_present"])
        self.assertNotIn("applicable", json.dumps(items[0]).lower())

    def test_fasb_effective_date_link_may_be_in_action_column(self) -> None:
        source = _source(
            "fasb_effective_dates",
            discovery_url=(
                "https://www.fasb.org/standards/"
                "accounting-standard-updated-effective-date"
            ),
        )
        payload = b"""
        <table><tr>
          <td>Accounting Standards Update 2026-01</td>
          <td>May 19, 2026</td>
          <td>Annual periods after December 15, 2027</td>
          <td><a href='/page/document?pdf=ASU-2026-01.pdf'>View document</a></td>
        </tr></table>
        """
        items = accounting_sources.parse(
            payload,
            source,
            self.fetched_at,
            source["discovery_url"],
        )
        self.assertEqual(1, len(items))
        self.assertIn("ASU-2026-01.pdf", items[0]["official_url"])

    def test_fasb_projects_and_taxonomies_remain_metadata_only(self) -> None:
        project_source = _source(
            "fasb_project_index",
            discovery_url="https://www.fasb.org/projects/current-projects",
        )
        projects = accounting_sources.parse(
            _fixture("fasb_projects.html"),
            project_source,
            self.fetched_at,
            project_source["discovery_url"],
        )
        self.assertEqual(2, len(projects))
        self.assertTrue(all(item["status"] == "discovered" for item in projects))

        taxonomy_source = _source(
            "fasb_taxonomy_index",
            discovery_url="https://www.fasb.org/projects/fasb-taxonomies",
        )
        taxonomies = accounting_sources.parse(
            _fixture("fasb_taxonomy.html"),
            taxonomy_source,
            self.fetched_at,
            taxonomy_source["discovery_url"],
        )
        self.assertEqual(2, len(taxonomies))
        self.assertTrue(
            all(item["metadata"].get("taxonomy_year") == "2026" for item in taxonomies)
        )

    def test_irs_irb_parser_extracts_exact_dates_and_deduplicates(self) -> None:
        source = _source(
            "irs_irb_index",
            discovery_url="https://www.irs.gov/internal-revenue-bulletins",
            allowed_hosts=["irs.gov", "www.irs.gov"],
            publisher="Internal Revenue Service",
        )
        items = accounting_sources.parse(
            _fixture("irs_irb.html"),
            source,
            self.fetched_at,
            source["discovery_url"],
        )
        self.assertEqual(["IRS-IRB-2026-27", "IRS-IRB-2026-28"], [i["external_id"] for i in items])
        self.assertEqual("2026-07-02", items[1]["published_at"])

    def test_kansas_revenue_parser_preserves_publisher_status_labels(self) -> None:
        source = _source(
            "kansas_revenue_index",
            discovery_url="https://www.ksrevenue.gov/prnewtaxnotices.html",
            allowed_hosts=["www.ksrevenue.gov"],
            publisher="Kansas Department of Revenue",
        )
        items = accounting_sources.parse(
            _fixture("kansas_revenue.html"),
            source,
            self.fetched_at,
            source["discovery_url"],
        )
        statuses = {
            item["external_id"]: item["metadata"]["publisher_status"]
            for item in items
        }
        self.assertEqual(
            {
                "KDOR-NOTICE-12-16": "revoked",
                "KDOR-NOTICE-26-10": "published",
                "KDOR-REVENUE-RULING-19-2010-04": "revised",
            },
            statuses,
        )

    def test_treasury_parser_keeps_only_relevant_official_releases(self) -> None:
        source = _source(
            "treasury_press_index",
            discovery_url="https://home.treasury.gov/news/press-releases",
            allowed_hosts=["home.treasury.gov"],
            publisher="United States Department of the Treasury",
        )
        items = accounting_sources.parse(
            _fixture("treasury_index.html"),
            source,
            self.fetched_at,
            source["discovery_url"],
        )
        self.assertEqual(1, len(items))
        self.assertIn("IRS Issue Tax Guidance", items[0]["title"])

    def test_official_atom_feed_ignores_bodies_off_host_links_and_duplicates(self) -> None:
        source = _source(
            "official_feed",
            discovery_url="https://www.irs.gov/newsroom/feed",
            allowed_hosts=["irs.gov", "www.irs.gov"],
            publisher="Internal Revenue Service",
        )
        items = accounting_sources.parse(
            _fixture("official_feed.xml"),
            source,
            self.fetched_at,
            source["discovery_url"],
        )
        self.assertEqual(1, len(items))
        self.assertEqual("2026-07-02T14:30:00Z", items[0]["published_at"])
        self.assertNotIn("body content", json.dumps(items).lower())

    def test_official_feed_rejects_dtd_and_entity_payloads(self) -> None:
        source = _source(
            "official_feed",
            discovery_url="https://www.irs.gov/newsroom/feed",
            allowed_hosts=["irs.gov", "www.irs.gov"],
            publisher="Internal Revenue Service",
        )
        payload = (
            b'<?xml version="1.0"?><!DOCTYPE rss [<!ENTITY x "unsafe">]>'
            b"<rss><channel><item><title>&x;</title></item></channel></rss>"
        )
        with self.assertRaises(accounting_sources.PayloadParseError):
            accounting_sources.parse(
                payload, source, self.fetched_at, source["discovery_url"]
            )

    def test_official_feed_rejects_entity_declaration_after_large_preamble(self) -> None:
        source = _source(
            "official_feed",
            discovery_url="https://www.irs.gov/newsroom/feed",
            allowed_hosts=["irs.gov", "www.irs.gov"],
            publisher="Internal Revenue Service",
        )
        payload = (
            b'<?xml version="1.0"?>'
            + b" " * 5_000
            + b'<!DOCTYPE rss [<!ENTITY x "unsafe">]>'
            + b"<rss><channel><item><title>&x;</title></item></channel></rss>"
        )
        with self.assertRaises(accounting_sources.PayloadParseError):
            accounting_sources.parse(
                payload, source, self.fetched_at, source["discovery_url"]
            )

    def test_payload_size_limit_fails_closed(self) -> None:
        source = _source("fasb_asu_index")
        source["request"] = {"max_bytes": 10}
        with self.assertRaises(accounting_sources.PayloadParseError):
            accounting_sources.parse(
                _fixture("fasb_asu_index.html"),
                source,
                self.fetched_at,
                source["discovery_url"],
            )


if __name__ == "__main__":
    unittest.main()
