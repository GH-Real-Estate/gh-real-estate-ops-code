from __future__ import annotations

import importlib.util
import io
import json
import unittest
import urllib.error
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "legal" / "scripts" / "check_official_sources.py"
SPEC = importlib.util.spec_from_file_location("check_official_sources", SCRIPT)
assert SPEC and SPEC.loader
monitor = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(monitor)


class FakeResponse:
    def __init__(
        self,
        body: bytes,
        headers: dict[str, str] | None = None,
        url: str = "https://example.test/source",
    ):
        self._body = io.BytesIO(body)
        self.headers = headers or {}
        self.status = 200
        self._url = url

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self, size: int = -1) -> bytes:
        return self._body.read(size)

    def geturl(self) -> str:
        return self._url


class SourceMonitorTests(unittest.TestCase):
    def test_source_archive_hash_is_used_for_derived_source(self):
        record = {
            "citation": "24 C.F.R. part 100",
            "official_url": "https://www.ecfr.gov/example.xml",
            "sha256": "a" * 64,
            "source_archive_sha256": "b" * 64,
        }

        policy = monitor.monitor_policy(record, {})

        self.assertEqual("source_archive_sha256", policy["baseline_kind"])
        self.assertEqual("b" * 64, policy["expected_sha256"])

    def test_manual_override_never_reuses_artifact_hash(self):
        record = {
            "citation": "Derived source",
            "official_url": "https://example.test/source.pdf",
            "sha256": "a" * 64,
        }
        overrides = {
            "Derived source": {
                "mode": "availability",
                "official_url": record["official_url"],
                "reason": "Derived artifact.",
            }
        }

        policy = monitor.monitor_policy(record, overrides)

        self.assertEqual("availability", policy["mode"])
        self.assertIsNone(policy["expected_sha256"])

    def test_encodeplus_policy_uses_approved_bundle_page_semantics(self):
        record = {
            "citation": "OPMC toc 005.024",
            "official_url": (
                "https://online.encodeplus.com/regs/overlandpark-ks/"
                "export2doc.aspx?pdf=1&tocid=005.024"
            ),
            "sha256": "a" * 64,
        }

        policy = monitor.monitor_policy(record, {})

        self.assertEqual("semantic-pdf-pages", policy["mode"])
        self.assertEqual("semantic-approved-bundle-pages", policy["baseline_kind"])
        self.assertIsNone(policy["expected_sha256"])

    def test_source_text_normalization_ignores_pdf_hyphen_line_wrap(self):
        self.assertEqual(
            monitor.normalize_source_text("Fifth-wheel Trailer"),
            monitor.normalize_source_text("Fifth-\nwheel Trailer"),
        )

    def test_ecfr_url_uses_latest_processed_title_date(self):
        pinned = "https://www.ecfr.gov/api/versioner/v1/full/2026-07-09/title-24.xml?part=100"

        current = monitor.current_ecfr_url(pinned, {"24": "2026-07-10"})

        self.assertEqual(
            "https://www.ecfr.gov/api/versioner/v1/full/2026-07-10/title-24.xml?part=100",
            current,
        )

    def test_download_retries_rate_limit(self):
        calls = []
        sleeps = []

        def opener(request, **kwargs):
            calls.append(request.full_url)
            if len(calls) == 1:
                raise urllib.error.HTTPError(
                    request.full_url,
                    429,
                    "Too Many Requests",
                    {"Retry-After": "0"},
                    None,
                )
            return FakeResponse(b"stable payload")

        result = monitor.download_url(
            "https://example.test/source",
            attempts=2,
            opener=opener,
            sleep=sleeps.append,
        )

        self.assertTrue(result["ok"])
        self.assertEqual(2, result["attempts"])
        self.assertEqual(2, len(calls))
        self.assertEqual([0.0], sleeps)

    def test_shared_url_is_downloaded_once(self):
        calls = []

        def downloader(url: str):
            calls.append(url)
            return {"ok": True, "url": url}

        url = "https://example.test/shared.pdf"
        downloads = monitor.fetch_unique_urls(
            {url, url}, workers=8, downloader=downloader
        )

        self.assertEqual([url], calls)
        self.assertEqual({url}, set(downloads))

    def test_encodeplus_export_uses_generated_file_token(self):
        source_url = (
            "https://online.encodeplus.com/regs/overlandpark-ks/"
            "export2doc.aspx?pdf=1&tocid=005.024"
        )
        calls = []

        def downloader(url: str, *, capture_body: bool = False):
            calls.append((url, capture_body))
            if "component.aspx" in url:
                body = b'{"Ready": true, "File": "generated/source.pdf"}'
                return {
                    "ok": True,
                    "body": body,
                    "attempts": 1,
                }
            self.assertIn("file=generated%2Fsource.pdf", url)
            return {
                "ok": True,
                "retrieved_sha256": "b" * 64,
                "bytes": 9,
                "prefix": b"%PDF-1.7",
                "body": b"%PDF-1.7",
                "final_url": url,
                "http_status": 200,
                "content_type": "application/pdf",
                "attempts": 1,
            }

        result = monitor.fetch_encodeplus_pdf(
            source_url, downloader=downloader, sleep=lambda _: None
        )

        self.assertTrue(result["ok"])
        self.assertEqual("encodeplus-token-export", result["fetch_method"])
        self.assertEqual(source_url, result["final_url"])
        self.assertEqual(2, result["attempts"])
        self.assertEqual(2, len(calls))
        self.assertTrue(all(capture_body for _, capture_body in calls))

    def test_encodeplus_rejects_non_boolean_ready_flag(self):
        source_url = (
            "https://online.encodeplus.com/regs/overlandpark-ks/"
            "export2doc.aspx?pdf=1&tocid=005.024"
        )

        def downloader(_url: str, *, capture_body: bool = False):
            self.assertTrue(capture_body)
            return {
                "ok": True,
                "body": b'{"Ready": "true", "File": "generated/source.pdf"}',
                "attempts": 1,
            }

        result = monitor.fetch_encodeplus_pdf(
            source_url, downloader=downloader, sleep=lambda _: None
        )

        self.assertFalse(result["ok"])
        self.assertEqual("invalid enCodePlus Ready flag", result["error"])

    def test_encodeplus_rejects_non_object_metadata(self):
        source_url = (
            "https://online.encodeplus.com/regs/overlandpark-ks/"
            "export2doc.aspx?pdf=1&tocid=005.024"
        )

        def downloader(_url: str, *, capture_body: bool = False):
            self.assertTrue(capture_body)
            return {"ok": True, "body": b"[]", "attempts": 1}

        result = monitor.fetch_encodeplus_pdf(
            source_url, downloader=downloader, sleep=lambda _: None
        )

        self.assertFalse(result["ok"])
        self.assertEqual("invalid enCodePlus export metadata type", result["error"])

    def test_encodeplus_semantic_fingerprint_uses_verified_bundle_slice(self):
        try:
            from pypdf import PdfWriter
        except ImportError:
            self.skipTest("pypdf is installed by the source-monitor workflows")

        registry = json.loads(
            (ROOT / "legal" / "manifests" / "authority_registry.json").read_text(
                encoding="utf-8"
            )
        )
        record = next(
            item for item in registry if item["citation"] == "OPMC toc 005.024"
        )
        pages = monitor.approved_bundle_pages(record, ROOT, {})
        writer = PdfWriter()
        for page in pages:
            writer.add_page(page)
        writer.add_metadata({"/ComparisonProbe": "metadata is not legal content"})
        stream = io.BytesIO()
        writer.write(stream)

        fingerprints = monitor.encodeplus_semantic_fingerprints(
            record,
            {"body": stream.getvalue()},
            ROOT,
            {},
        )

        self.assertEqual(
            fingerprints["expected_sha256"], fingerprints["retrieved_sha256"]
        )
        self.assertEqual(record["pages"], fingerprints["retrieved_pages"])

    def test_malformed_encodeplus_pdf_fails_as_source_error(self):
        try:
            __import__("pypdf")
        except ImportError:
            self.skipTest("pypdf is installed by the source-monitor workflows")

        registry = json.loads(
            (ROOT / "legal" / "manifests" / "authority_registry.json").read_text(
                encoding="utf-8"
            )
        )
        record = next(
            item for item in registry if item["citation"] == "OPMC toc 005.024"
        )

        with self.assertRaisesRegex(RuntimeError, "could not read generated"):
            monitor.encodeplus_semantic_fingerprints(
                record,
                {"body": b"%PDF-1.7\ntruncated"},
                ROOT,
                {},
            )

    def test_approved_bundle_hash_mismatch_fails_closed(self):
        registry = json.loads(
            (ROOT / "legal" / "manifests" / "authority_registry.json").read_text(
                encoding="utf-8"
            )
        )
        record = dict(
            next(item for item in registry if item["citation"] == "OPMC toc 005.024")
        )
        record["bundle_sha256"] = "0" * 64

        with self.assertRaisesRegex(RuntimeError, "approved bundle hash mismatch"):
            monitor.approved_bundle_pages(record, ROOT, {})

    def test_semantic_pdf_fingerprint_preserves_pages_and_graphics(self):
        class FakeXObject(dict):
            def __init__(self, payload: bytes):
                super().__init__(
                    {
                        "/Subtype": "/Image",
                        "/Width": 10,
                        "/Height": 10,
                        "/BitsPerComponent": 8,
                        "/ColorSpace": "/DeviceRGB",
                    }
                )
                self.payload = payload

            def get_object(self):
                return self

            def get_data(self):
                return self.payload

        class FakePage:
            mediabox = [0, 0, 612, 792]
            cropbox = [0, 0, 612, 792]

            def __init__(self, text: str, image: bytes):
                self.text = text
                self.resources = {"/XObject": {"/X1": FakeXObject(image)}}

            def extract_text(self):
                return self.text

            def get(self, key, default=None):
                if key == "/Resources":
                    return self.resources
                return default

        page_a = FakePage("First page", b"image-a")
        page_b = FakePage("Second page", b"image-b")

        baseline = monitor.semantic_pdf_fingerprint([page_a, page_b])

        self.assertNotEqual(
            baseline, monitor.semantic_pdf_fingerprint([page_b, page_a])
        )
        self.assertNotEqual(
            baseline,
            monitor.semantic_pdf_fingerprint(
                [FakePage("First page", b"changed-image"), page_b]
            ),
        )

    def test_repository_overrides_match_exact_registry_records(self):
        registry = json.loads(
            (ROOT / "legal" / "manifests" / "authority_registry.json").read_text(
                encoding="utf-8"
            )
        )
        overrides = monitor.load_overrides(
            ROOT / "legal" / "manifests" / "source_monitor_overrides.json"
        )
        by_citation = {str(record["citation"]): record for record in registry}

        self.assertEqual(5, len(overrides))
        for citation, override in overrides.items():
            self.assertIn(citation, by_citation)
            self.assertEqual(
                by_citation[citation]["official_url"], override["official_url"]
            )


if __name__ == "__main__":
    unittest.main()
