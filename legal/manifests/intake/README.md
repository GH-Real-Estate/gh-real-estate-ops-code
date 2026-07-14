# Legal document intake

This directory records user-provided legal documents as evidence, not as approved legal authority. Intake records are deliberately separate from `legal/text/current/`, the authority registry, generated `CURRENT` bundles, and dated release manifests.

## Rules

- Store a cryptographic hash and bounded metadata by default; do not copy the source binary into this directory.
- Treat the filename and any date stated inside the document as unverified source assertions.
- Compare the document with a live official publisher source and the approved repository release, then record omissions and other material differences.
- Keep every intake record excluded from the approved current-law path, even when it appears identical to official text.
- Do not promote intake content directly. A qualified reviewer must resolve authority, effective date, applicability, provenance, and redistribution rights through the complete dated-release process.
- Official source text controls over an intake record, user-provided document, extract, summary, or AI output.

Run `python legal/scripts/validate_intake.py` after adding or changing an intake record. The validator fails if a record permits binary storage, claims approved/current status, uses an unsafe official-source URL, contains inconsistent counts, or points to missing current-release evidence.

This directory is a records and review aid, not legal advice.
