from __future__ import annotations

import importlib.util
import hashlib
import io
import json
import unittest
from unittest import mock
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
        line = "ZOHO_CLIENT_" + f"SECRET={secret}\n"
        problems = safety_check.scan_text(".env.example", line)
        self.assertTrue(any("secret assignment" in problem for problem in problems))

    def test_env_example_placeholders_are_allowed(self) -> None:
        problems = safety_check.scan_text(
            ".env.example",
            "ZOHO_CLIENT_SECRET=replace_me\nZOHO_REFRESH_TOKEN=${ZOHO_REFRESH_TOKEN}\n",
        )
        self.assertEqual([], problems)

    def test_scanner_source_is_not_exempt_from_secret_detection(self) -> None:
        secret = "actual" + "-production-secret-value"
        line = "ZOHO_CLIENT_" + f"SECRET={secret}\n"
        problems = safety_check.scan_text(
            "tools/safety/pre-commit-safety-check.py", line
        )
        self.assertTrue(any("secret assignment" in problem for problem in problems))

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

    def test_binary_content_after_prefix_is_blocked(self) -> None:
        path = InMemoryFile(".bin", (b"A" * 8192) + b"\x00hidden")
        problems, allowed_pdf, scan_as_text = safety_check.scan_file_policy(
            "payload.bin", path
        )
        self.assertTrue(any("binary content" in problem for problem in problems))
        self.assertFalse(allowed_pdf)
        self.assertFalse(scan_as_text)

    def test_hash_pinned_control_text_requires_exact_reviewed_bytes(self) -> None:
        content = b"reviewed\x00legacy"
        rel = "legal/text/current/authorities/federal/example.md"
        digest = hashlib.sha256(content).hexdigest()
        with mock.patch.dict(
            safety_check.HASH_PINNED_CONTROL_TEXT_SHA256,
            {rel: digest},
            clear=True,
        ):
            allowed = safety_check.scan_file_policy(rel, InMemoryFile(".md", content))
            changed = safety_check.scan_file_policy(
                rel, InMemoryFile(".md", content + b"changed")
            )
        self.assertEqual(([], False, True), allowed)
        self.assertTrue(any("binary content" in problem for problem in changed[0]))

    def test_skipped_directory_name_cannot_hide_symlink(self) -> None:
        path = SimpleNamespace(
            parts=("repo", "node_modules"),
            is_symlink=lambda: True,
            is_file=lambda: False,
        )
        self.assertEqual("symlink", safety_check.classify_path_for_scan(path))

    def test_utf8_prefix_ending_inside_multibyte_character_is_allowed(self) -> None:
        path = InMemoryFile(".md", (b"a" * 8191) + "Ã©".encode("utf-8"))
        problems, allowed_pdf, scan_as_text = safety_check.scan_file_policy("authority.md", path)
        self.assertEqual([], problems)
        self.assertFalse(allowed_pdf)
        self.assertTrue(scan_as_text)

    def test_code_references_and_explicit_negative_fixtures_are_allowed(self) -> None:
        problems = safety_check.scan_text(
            "src/example.js",
            "const accessToken = await getToken();\n"
            "tokenCache.accessToken = response.access_token;\n"
            "url = 'https://official.example/?access_token=do-not-archive';\n",
        )
        self.assertEqual([], problems)

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

    def test_accounting_content_manifest_verifies_paths_and_hashes(self) -> None:
        digest = hashlib.sha256(b"safe\n").hexdigest()
        root = mock.MagicMock()
        manifest = mock.MagicMock()
        target = mock.MagicMock()
        manifest.relative_to.return_value = Path(
            "accounting/chart-of-accounts/manifest.json"
        )
        manifest.read_text.return_value = json.dumps(
            {
                "files": {
                    "artifact.csv": {
                        "repository_path": "accounting/artifact.csv",
                        "sha256": digest,
                    }
                }
            }
        )
        root.joinpath.return_value = target
        target.is_symlink.return_value = False
        target.is_file.return_value = True

        with mock.patch.object(safety_check, "sha256_file", return_value=digest):
            self.assertEqual(
                [], safety_check.validate_accounting_content_manifest(root, manifest)
            )
        with mock.patch.object(
            safety_check, "sha256_file", return_value="0" * 64
        ):
            problems = safety_check.validate_accounting_content_manifest(root, manifest)
        self.assertTrue(any("hash mismatch" in problem for problem in problems))


if __name__ == "__main__":
    unittest.main()
