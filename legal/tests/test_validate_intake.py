from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "legal" / "scripts" / "validate_intake.py"
MANIFEST = (
    ROOT
    / "legal"
    / "manifests"
    / "intake"
    / "2026-07-14-kansas-article-25-user-document.json"
)
SPEC = importlib.util.spec_from_file_location("validate_intake", SCRIPT)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class ValidateIntakeTests(unittest.TestCase):
    def setUp(self):
        self.record = validator.load_json(MANIFEST)

    def assert_invalid(self, record, expected_message):
        with self.assertRaisesRegex(validator.ValidationError, expected_message):
            validator.validate_record(record, ROOT)

    def test_checked_in_record_and_schema_are_valid(self):
        validator.validate_schema_contract(ROOT)
        validator.validate_record(self.record, ROOT)

    def test_rejects_malformed_source_digest(self):
        self.record["source_document"]["sha256"] = "0" * 63
        self.assert_invalid(self.record, "sha256")

    def test_rejects_unsafe_official_source_urls(self):
        unsafe_urls = (
            "http://www.kslegislature.gov/statutes/",
            "https://www.kslegislature.gov.evil.example/statutes/",
            "https://credential" + chr(64) + "www.kslegislature.gov/statutes/",
            "https://www.kslegislature.gov/statutes/?token=secret",
        )
        for url in unsafe_urls:
            with self.subTest(url=url):
                record = copy.deepcopy(self.record)
                record["comparison"]["official_index"]["url"] = url
                self.assert_invalid(record, "credential-free HTTPS URL")

    def test_rejects_wrong_official_source_path(self):
        self.record["comparison"]["official_index"]["url"] = (
            "https://www.kslegislature.gov/laws/059_000_0000_chapter/"
        )
        self.assert_invalid(self.record, "Chapter 58 Article 25 index")

    def test_rejects_future_dated_review(self):
        self.record["review"]["reviewed_on"] = "2099-01-01"
        self.record["comparison"]["performed_on"] = "2099-01-01"
        self.assert_invalid(self.record, "cannot be in the future")

    def test_rejects_attempted_binary_storage(self):
        self.record["storage"]["binary_stored"] = True
        self.assert_invalid(self.record, "binary_stored")

    def test_rejects_attempted_current_law_promotion(self):
        promotion_attempts = (
            ("excluded_from_approved_current", False),
            ("status", "approved-current"),
            ("disposition", "promote-to-current"),
        )
        for field, value in promotion_attempts:
            with self.subTest(field=field):
                record = copy.deepcopy(self.record)
                record["review"][field] = value
                self.assert_invalid(record, f"review\\.{field}")

    def test_rejects_section_count_drift(self):
        self.record["comparison"]["document_overlap"][
            "document_omitted_current_section_count"
        ] += 1
        self.assert_invalid(self.record, "official-index and omitted-section counts")

    def test_rejects_repository_path_traversal(self):
        self.record["comparison"]["repository_current"]["registry_path"] = (
            "../outside.json"
        )
        self.assert_invalid(self.record, "must not be absolute or traverse directories")

    def test_rejects_binary_files_in_intake_directory(self):
        with self.assertRaisesRegex(
            validator.ValidationError,
            "binary or unsupported file is prohibited",
        ):
            validator.validate_intake_file_types([Path("source.docx")])

    def test_full_intake_directory_is_valid(self):
        self.assertEqual(validator.validate_all(ROOT), 1)


if __name__ == "__main__":
    unittest.main()
