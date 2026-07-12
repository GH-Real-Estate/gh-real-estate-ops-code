#!/usr/bin/env python3
"""Normalize the mirrored HUD assistance-animal PDF's malformed font objects."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "tmp/pdfs/source_downloads/federal"
PDF = FOLDER / "14_HUD_2026_Assistance_Animal_Enforcement_Guidance.pdf"
RAW = FOLDER / "raw/14_HUD_2026_Assistance_Animal_Enforcement_Guidance_original_mirror.pdf"
MANIFEST = FOLDER / "federal_source_manifest.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    RAW.parent.mkdir(parents=True, exist_ok=True)
    if not RAW.exists():
        shutil.copy2(PDF, RAW)
    fixed = PDF.with_suffix(".normalized.pdf")
    subprocess.run(
        [
            "gs", "-q", "-dNOPAUSE", "-dBATCH", "-dSAFER",
            "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.7",
            "-dPDFSETTINGS=/prepress", f"-sOutputFile={fixed}", str(RAW),
        ],
        check=True,
    )
    if len(PdfReader(fixed).pages) != len(PdfReader(RAW).pages):
        raise RuntimeError("normalization changed page count")
    subprocess.run(["pdftotext", str(fixed), "/dev/null"], check=True)
    fixed.replace(PDF)

    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for item in data["documents"]:
        if item.get("local_path", "").endswith(PDF.name):
            item["sha256"] = digest(PDF)
            item["page_count"] = len(PdfReader(PDF).pages)
            item["source_archive_path"] = str(RAW.relative_to(ROOT))
            item["source_archive_sha256"] = digest(RAW)
            item["render_note"] = (
                "The public-mirror PDF was normalized with Ghostscript to repair malformed font objects; "
                "the original mirror file is retained for provenance. Compare content with the official HUD URL before reliance."
            )
            break
    else:
        raise RuntimeError("assistance-animal record not found")
    MANIFEST.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Normalized {PDF.name}: {len(PdfReader(PDF).pages)} pages; SHA-256 {digest(PDF)}")


if __name__ == "__main__":
    main()
