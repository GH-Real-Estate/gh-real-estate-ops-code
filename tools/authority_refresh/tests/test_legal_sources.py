from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from urllib.parse import urlsplit


TESTS_DIR = Path(__file__).resolve().parent
MODULE_DIR = TESTS_DIR.parent
FIXTURES_DIR = TESTS_DIR / "fixtures" / "legal"
CONFIG_PATH = MODULE_DIR / "config" / "legal_sources.json"
sys.path.insert(0, str(MODULE_DIR))

import legal_sources  # noqa: E402


FETCHED_AT = "2026-07-13T20:00:00Z"
REQUIRED_FIELDS = {
    "external_id",
    "title",
    "official_url",
    "published_at",
    "effective_at",
    "status",
    "metadata",
}


def fixture(name: str) -> bytes:
    return (FIXTURES_DIR / name).read_bytes()


class LegalSourceParserTests(unittest.TestCase):
    def assert_items_are_discovery_only(
        self, items: list[dict], allowed_hosts: set[str]
    ) -> None:
        for item in items:
            self.assertTrue(REQUIRED_FIELDS.issubset(item))
            self.assertEqual(item["status"], "discovered")
            self.assertIn(urlsplit(item["official_url"]).hostname, allowed_hosts)
            self.assertEqual(urlsplit(item["official_url"]).scheme, "https")

    def test_ecfr_parser_filters_titles_and_does_not_infer_effectiveness(self) -> None:
        source = {
            "adapter": "ecfr_titles_json",
            "allowed_hosts": ["www.ecfr.gov"],
            "filters": {"title_numbers": [24, 35], "include_reserved": False},
        }
        items = legal_sources.parse(
            fixture("ecfr_titles.json"),
            source,
            FETCHED_AT,
            "https://www.ecfr.gov/api/versioner/v1/titles.json",
        )

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["external_id"], "title-24")
        self.assertEqual(items[0]["published_at"], "2026-06-22")
        self.assertIsNone(items[0]["effective_at"])
        self.assertEqual(items[0]["metadata"]["up_to_date_as_of"], "2026-07-10")
        self.assert_items_are_discovery_only(items, {"www.ecfr.gov"})

    def test_ecfr_parser_rejects_malformed_payloads(self) -> None:
        source = {
            "adapter": "ecfr_titles_json",
            "allowed_hosts": ["www.ecfr.gov"],
        }
        with self.assertRaises(legal_sources.SourceParseError):
            legal_sources.parse(
                b"{not-json",
                source,
                FETCHED_AT,
                "https://www.ecfr.gov/api/versioner/v1/titles.json",
            )
        with self.assertRaises(legal_sources.SourceParseError):
            legal_sources.parse(
                b'{"titles": {}}',
                source,
                FETCHED_AT,
                "https://www.ecfr.gov/api/versioner/v1/titles.json",
            )

    def test_rss_parser_normalizes_dates_filters_hosts_and_suppresses_duplicates(self) -> None:
        source = {
            "adapter": "rss_atom",
            "allowed_hosts": ["www.govinfo.gov"],
        }
        items = legal_sources.parse(
            fixture("govinfo_rss.xml"),
            source,
            FETCHED_AT,
            "https://www.govinfo.gov/rss/plaw.xml",
        )

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["external_id"], "PLAW-119publ42")
        self.assertEqual(items[0]["published_at"], "2026-07-13T12:00:00Z")
        self.assertNotIn("#", items[0]["official_url"])
        self.assert_items_are_discovery_only(items, {"www.govinfo.gov"})

    def test_atom_parser_prefers_alternate_link_and_filters_offsite_links(self) -> None:
        source = {
            "adapter": "rss_atom",
            "allowed_hosts": ["www.govinfo.gov"],
        }
        items = legal_sources.parse(
            fixture("official_atom.xml"),
            source,
            FETCHED_AT,
            "https://www.govinfo.gov/feeds/notices.atom",
        )

        self.assertEqual(len(items), 1)
        self.assertEqual(
            items[0]["official_url"],
            "https://www.govinfo.gov/app/details/NOTICE-1",
        )
        self.assertEqual(items[0]["published_at"], "2026-07-13T19:30:00Z")
        self.assert_items_are_discovery_only(items, {"www.govinfo.gov"})

    def test_xml_parser_rejects_malformed_and_entity_payloads(self) -> None:
        source = {
            "adapter": "rss_atom",
            "allowed_hosts": ["www.govinfo.gov"],
        }
        for payload in (
            b"<rss><channel><item></rss>",
            b'<!DOCTYPE rss [<!ENTITY x "unsafe">]><rss version="2.0"/>',
        ):
            with self.subTest(payload=payload):
                with self.assertRaises(legal_sources.SourceParseError):
                    legal_sources.parse(
                        payload,
                        source,
                        FETCHED_AT,
                        "https://www.govinfo.gov/rss/plaw.xml",
                    )

    def test_html_index_filters_links_and_suppresses_canonical_duplicates(self) -> None:
        source = {
            "adapter": "official_html_index",
            "allowed_hosts": ["sos.ks.gov"],
            "link_filter": {
                "include_patterns": ["/official/"],
                "exclude_patterns": ["/archive/"],
            },
        }
        items = legal_sources.parse(
            fixture("official_index.html"),
            source,
            FETCHED_AT,
            "https://sos.ks.gov/publications/index.html",
        )

        self.assertEqual(len(items), 2)
        self.assertEqual(
            {item["official_url"] for item in items},
            {
                "https://sos.ks.gov/official/notice-1.pdf",
                "https://sos.ks.gov/official/notice-2.html",
            },
        )
        self.assertEqual(
            {item["title"] for item in items}, {"Notice One", "Notice Two"}
        )
        self.assert_items_are_discovery_only(items, {"sos.ks.gov"})

    def test_html_index_rejects_non_utf8_and_invalid_filter_configuration(self) -> None:
        source = {
            "adapter": "official_html_index",
            "allowed_hosts": ["sos.ks.gov"],
        }
        with self.assertRaises(legal_sources.SourceParseError):
            legal_sources.parse(
                b"\xff\xfe",
                source,
                FETCHED_AT,
                "https://sos.ks.gov/publications/index.html",
            )
        source["link_filter"] = {"include_patterns": ["["]}
        with self.assertRaises(legal_sources.SourceParseError):
            legal_sources.parse(
                b'<a href="/official/item">Item</a>',
                source,
                FETCHED_AT,
                "https://sos.ks.gov/publications/index.html",
            )

    def test_kansas_parser_preserves_versions_and_publisher_status_as_metadata(self) -> None:
        source = {
            "adapter": "kansas_legislature_json",
            "allowed_hosts": ["kslegislature.gov", "www.kslegislature.gov"],
            "item_url_template": (
                "https://kslegislature.gov/api/v1/bill_status/{bill_no}/"
            ),
        }
        items = legal_sources.parse(
            fixture("kansas_measures.json"),
            source,
            FETCHED_AT,
            "https://kslegislature.gov/api/v1/measures/",
        )

        self.assertEqual(len(items), 2)
        by_id = {item["external_id"]: item for item in items}
        self.assertEqual(set(by_id), {"HB2001:enrolled", "SB33:introduced"})
        self.assertEqual(
            by_id["HB2001:enrolled"]["published_at"], "2026-07-11T15:00:00Z"
        )
        self.assertEqual(
            by_id["HB2001:enrolled"]["metadata"]["publisher_status"], "signed"
        )
        self.assertEqual(by_id["HB2001:enrolled"]["status"], "discovered")
        self.assertIsNone(by_id["SB33:introduced"]["published_at"])
        self.assert_items_are_discovery_only(
            items, {"kslegislature.gov", "www.kslegislature.gov"}
        )

    def test_kansas_parser_rejects_malformed_record_collections(self) -> None:
        source = {
            "adapter": "kansas_legislature_json",
            "allowed_hosts": ["kslegislature.gov"],
        }
        for payload in (b'{"results": {}}', b'{"results": [42]}'):
            with self.subTest(payload=payload):
                with self.assertRaises(legal_sources.SourceParseError):
                    legal_sources.parse(
                        payload,
                        source,
                        FETCHED_AT,
                        "https://kslegislature.gov/api/v1/measures/",
                    )

    def test_generic_official_json_records_preserves_dates_without_applicability(self) -> None:
        source = {
            "adapter": "official_json_records",
            "allowed_hosts": ["www.federalregister.gov"],
            "records_path": "results",
            "field_map": {
                "external_id": ["document_number"],
                "title": ["title"],
                "official_url": ["html_url"],
                "published_at": ["publication_date"],
                "effective_at": ["effective_on"],
                "publisher_status": ["type"],
            },
            "metadata_fields": ["agencies"],
        }
        items = legal_sources.parse(
            fixture("federal_register.json"),
            source,
            FETCHED_AT,
            "https://www.federalregister.gov/api/v1/documents.json?page=2",
        )

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["external_id"], "2026-12345")
        self.assertEqual(items[0]["published_at"], "2026-07-13")
        self.assertEqual(items[0]["effective_at"], "2026-08-12")
        self.assertEqual(items[0]["metadata"]["publisher_status"], "Rule")
        self.assertEqual(
            items[0]["metadata"]["source_response_url"],
            "https://www.federalregister.gov/api/v1/documents.json",
        )
        self.assertNotIn("?page=2", json.dumps(items))
        self.assertEqual(items[0]["status"], "discovered")
        self.assert_items_are_discovery_only(items, {"www.federalregister.gov"})

    def test_unknown_adapter_and_missing_allowlist_fail_closed(self) -> None:
        with self.assertRaises(legal_sources.SourceParseError):
            legal_sources.parse(
                b"{}",
                {"adapter": "unknown", "allowed_hosts": ["www.ecfr.gov"]},
                FETCHED_AT,
                "https://www.ecfr.gov/",
            )
        with self.assertRaises(legal_sources.SourceParseError):
            legal_sources.parse(
                b'{"titles": []}',
                {"adapter": "ecfr_titles_json"},
                FETCHED_AT,
                "https://www.ecfr.gov/",
            )


class LegalSourceConfigurationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))

    def test_catalog_has_required_sources_fields_and_storage_classes(self) -> None:
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
        sources = self.config["sources"]
        self.assertGreaterEqual(len(sources), 12)
        self.assertEqual(len({source["source_id"] for source in sources}), len(sources))
        for source in sources:
            with self.subTest(source=source.get("source_id")):
                self.assertTrue(required.issubset(source))
                self.assertTrue(source["discovery_url"].startswith("https://"))
                self.assertIsInstance(source["critical"], bool)
        self.assertEqual(
            {source["storage_policy"] for source in sources},
            {"redistributable", "metadata-only", "manual-review"},
        )

    def test_catalog_uses_exact_official_host_allowlists(self) -> None:
        globally_allowed = set(self.config["allowed_domains"])
        self.assertIn("codes.opkansas.org", self.config["delegated_official_publishers"])
        for host in globally_allowed:
            self.assertNotIn("*", host)
            self.assertEqual(host, host.lower())
        for source in self.config["sources"]:
            with self.subTest(source=source["source_id"]):
                discovery_host = urlsplit(source["discovery_url"]).hostname
                self.assertIn(discovery_host, globally_allowed)
                self.assertTrue(set(source["allowed_hosts"]).issubset(globally_allowed))

    def test_catalog_covers_each_required_publisher_family(self) -> None:
        source_ids = {source["source_id"] for source in self.config["sources"]}
        required_prefixes = {
            "ecfr-",
            "govinfo-",
            "olrc-",
            "congress-",
            "federal-register-",
            "kansas-legislature-",
            "kansas-sos-",
            "kansas-appellate-",
            "overland-park-",
        }
        for prefix in required_prefixes:
            with self.subTest(prefix=prefix):
                self.assertTrue(any(source_id.startswith(prefix) for source_id in source_ids))

    def test_congress_api_key_requirement_is_explicit(self) -> None:
        source = next(
            source
            for source in self.config["sources"]
            if source["source_id"] == "congress-legislation-api"
        )
        self.assertTrue(source["request"]["api_key_required"])
        self.assertEqual(source["request"]["api_key_env"], "CONGRESS_API_KEY")
        self.assertEqual(source["request"]["api_key_query_param"], "api_key")

    def test_appellate_decision_page_is_treated_as_a_rolling_window(self) -> None:
        source = next(
            source
            for source in self.config["sources"]
            if source["source_id"] == "kansas-appellate-decisions"
        )

        self.assertEqual(source["missing_detection"], "rolling-window")


if __name__ == "__main__":
    unittest.main()
