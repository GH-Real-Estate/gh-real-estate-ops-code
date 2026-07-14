from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "legal" / "scripts" / "validate_release.py"
SPEC = importlib.util.spec_from_file_location("validate_release", SCRIPT)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class ValidateReleaseTests(unittest.TestCase):
    def test_text_size_is_independent_of_checkout_line_endings(self):
        lf = b"first line\nsecond line\n"
        crlf = b"first line\r\nsecond line\r\n"

        self.assertEqual(
            validator.normalized_text_size(lf),
            validator.normalized_text_size(crlf),
        )


if __name__ == "__main__":
    unittest.main()
