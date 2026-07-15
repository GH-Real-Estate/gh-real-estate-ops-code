from __future__ import annotations

import importlib.util
import io
import unittest
from pathlib import Path
from types import SimpleNamespace


SCRIPT = Path(__file__).resolve().parents[1] / "pre-commit-safety-check.py"
SPEC = importlib.util.spec_from_file_location("safety_check", SCRIPT)
assert SPEC and SPEC.loader
safety_check = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(safety_check)


class InMemoryFile:
    """Minimal Path-like object for deterministic file-policy tests."""

    def __init__(self, suffix: str, content: bytes) -> None:
        self.suffix = suffix
        self._content = content

    def stat(self) -> SimpleNamespace:
        return SimpleNamespace(st_size=len(self._content))

    def open(self, mode: str) -> io.BytesIO:
        assert mode == "rb"
        return io.BytesIO(self._content)


class SafetyCheckTests(unittest.TestCase):
    def test_env_example_content_is_scanned(self) -> None:
        secret = "super" + "-secret-production-value"
        problems = safety_check.scan_text(".env.example", f"ZOHO_CLIENT_SECRET={secret}\n")
        self.assertTrue(any("secret assignment" in problem for problem in problems))

    def test_env_example_placeholders_are_allowed(self) -> None:
        problems = safety_check.scan_text(
            ".env.example",
            "ZOHO_CLIENT_SECRET=replace_me\nZOHO_REFRESH_TOKEN=${ZOHO_REFRESH_TOKEN}\n",
        )
        self.assertEqual([], problems)

    def test_long_operational_identifiers_are_blocked(self) -> None:
        problems = safety_check.scan_text(
            "src/zoho-books/example.deluge", 'itemId = "123456789012345678";\n'
        )
        self.assertTrue(any("long operational identifier" in problem for problem in problems))

    def test_dangerous_credential_filenames_are_blocked(self) -> None:
        self.assertTrue(safety_check.scan_filename("config/.npmrc"))
        self.assertTrue(safety_check.scan_filename("keys/id_ed25519"))
        self.assertTrue(safety_check.scan_filename("state/prod.tfstate"))

    def test_binary_documents_are_blocked(self) -> None:
        path = InMemoryFile(".docx", b"PK\x03\x04")
        problems, allowed_pdf, scan_as_text = safety_check.scan_file_policy("notes.docx", path)
        self.assertTrue(problems)
        self.assertFalse(allowed_pdf)
        self.assertFalse(scan_as_text)

    def test_only_governed_pdfs_are_allowed(self) -> None:
        path = InMemoryFile(".pdf", b"%PDF-1.7\n")
        blocked, _, _ = safety_check.scan_file_policy("uploads/authority.pdf", path)
        allowed, allowed_pdf, scan_as_text = safety_check.scan_file_policy(
            "legal/generated/project-sources/current/authority.pdf", path
        )
        self.assertTrue(blocked)
        self.assertEqual([], allowed)
        self.assertTrue(allowed_pdf)
        self.assertFalse(scan_as_text)

    def test_unknown_binary_content_is_blocked(self) -> None:
        path = InMemoryFile(".bin", b"value\x00hidden")
        problems, allowed_pdf, scan_as_text = safety_check.scan_file_policy("payload.bin", path)
        self.assertTrue(any("binary content" in problem for problem in problems))
        self.assertFalse(allowed_pdf)
        self.assertFalse(scan_as_text)

    def test_checksum_manifest_parser_keeps_only_pdf_hashes(self) -> None:
        digest = "a" * 64
        approved = safety_check.parse_checksum_manifest(
            f"{digest}  legal/generated/project-sources/current/authority.pdf\n"
            f"{digest}  legal/README.md\n"
        )
        self.assertEqual(
            {"legal/generated/project-sources/current/authority.pdf": digest}, approved
        )

    def test_accounting_manifest_parser_uses_repository_paths(self) -> None:
        digest = "b" * 64
        approved = safety_check.parse_accounting_pdf_manifest(
            {
                "files": [
                    {
                        "repository_path": "accounting/generated/project-sources/current/source.pdf",
                        "sha256": digest,
                    }
                ]
            }
        )
        self.assertEqual(
            {"accounting/generated/project-sources/current/source.pdf": digest}, approved
        )


if __name__ == "__main__":
    unittest.main()
