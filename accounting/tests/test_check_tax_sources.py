#!/usr/bin/env python3
"""Regression tests for the report-only tax-authority monitor."""

from __future__ import annotations

import importlib.util
import io
import json
import tempfile
import unittest
import urllib.error
from datetime import date
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "accounting" / "scripts" / "check_tax_sources.py"
SPEC = importlib.util.spec_from_file_location("check_tax_sources", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"could not load {SCRIPT}")
monitor = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(monitor)


class FakeResponse:
    def __init__(
        self,
        payload: bytes,
        *,
        content_type: str = "text/html",
        final_url: str = "https://www.irs.gov/publications/p527",
    ) -> None:
        self._stream = io.BytesIO(payload)
        self._final_url = final_url
        self.headers = {"Content-Type": content_type, "Content-Length": str(len(payload))}
        self.status = 200

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self, size: int = -1) -> bytes:
        return self._stream.read(size)

    def geturl(self) -> str:
        return self._final_url


def sample_record(**overrides):
    record = {
        "id": "FED-TEST-001",
        "title": "Test source",
        "jurisdiction": "federal",
        "tax_area": "test",
        "authority_weight": "official-guidance",
        "official_url": "https://www.irs.gov/publications/p527",
        "sourcebook_ids": [],
        "applicability": "test only",
        "volatility": "annual",
        "last_reviewed": "2026-07-13",
        "next_review": "2027-01-15",
        "monitoring_mode": "availability-and-fingerprint",
        "expected_content_types": ["text/html"],
        "approved_sha256": None,
        "reviewer_gate": "review required",
    }
    record.update(overrides)
    return record


class TaxSourceMonitorTests(unittest.TestCase):
    def test_repository_registry_is_valid(self):
        payload = json.loads(
            (ROOT / "accounting" / "manifests" / "tax_authority_registry.json").read_text(
                encoding="utf-8"
            )
        )
        records = monitor.validate_registry(payload, ROOT, check_sourcebooks=False)
        self.assertEqual(40, len(records))

    def test_registry_rejects_unapproved_host(self):
        payload = {
            "schema_version": 1,
            "formal_review_cadence": "semiannual",
            "formal_review_months": [1, 7],
            "records": [sample_record(id=f"FED-TEST-{index:03d}") for index in range(30)],
        }
        payload["records"][0]["official_url"] = "https://example.com/tax"
        with self.assertRaisesRegex(ValueError, "approved official HTTPS host"):
            monitor.validate_registry(payload, ROOT, check_sourcebooks=False)

    def test_download_retries_rate_limit_and_records_actual_attempts(self):
        calls = []
        sleeps = []

        def opener(request, **_kwargs):
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

        result = monitor.download(
            sample_record(), attempts=2, opener=opener, sleep=sleeps.append
        )
        self.assertTrue(result["ok"])
        self.assertEqual(2, result["attempts"])
        self.assertEqual(2, len(calls))
        self.assertEqual([0.0], sleeps)

    def test_download_does_not_retry_missing_source(self):
        calls = []

        def opener(request, **_kwargs):
            calls.append(request.full_url)
            raise urllib.error.HTTPError(request.full_url, 404, "Not Found", {}, None)

        result = monitor.download(
            sample_record(), attempts=3, opener=opener, sleep=lambda _delay: None
        )
        self.assertFalse(result["ok"])
        self.assertEqual(1, result["attempts"])
        self.assertEqual(1, len(calls))

    def test_download_rejects_unexpected_payload_type(self):
        result = monitor.download(
            sample_record(),
            attempts=1,
            opener=lambda *_args, **_kwargs: FakeResponse(
                b"%PDF-1.7", content_type="application/pdf"
            ),
            sleep=lambda _delay: None,
        )
        self.assertFalse(result["ok"])
        self.assertIn("unexpected content type", result["error"])

    def test_evaluate_separates_change_detection_from_formal_review(self):
        records = [
            sample_record(id="FED-TEST-001", approved_sha256="a" * 64),
            sample_record(id="FED-TEST-002", next_review="2026-07-13"),
            sample_record(id="FED-TEST-003"),
        ]

        def fake_download(record):
            digest = "b" * 64 if record["id"] == "FED-TEST-001" else "c" * 64
            return {"ok": True, "retrieved_sha256": digest, "attempts": 1}

        with mock.patch.object(monitor, "download", side_effect=fake_download):
            results = monitor.evaluate(
                records, date(2026, 7, 13), formal_review=False, workers=2
            )
        by_id = {item["id"]: item["status"] for item in results}
        self.assertEqual("changed", by_id["FED-TEST-001"])
        self.assertEqual("review-due", by_id["FED-TEST-002"])
        self.assertEqual("manual-baseline", by_id["FED-TEST-003"])

    def test_atomic_report_write_replaces_complete_target(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "report.json"
            target.write_text("old\n", encoding="utf-8")
            monitor.write_atomic(target, "new\n")
            self.assertEqual("new\n", target.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
