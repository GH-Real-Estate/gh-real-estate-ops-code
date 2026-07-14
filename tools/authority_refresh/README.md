# Authority refresh tooling

This standard-library Python package discovers potential legal and accounting source
changes without modifying approved authority content.

## Trust boundary

- Discovery jobs fetch only allowlisted official hosts.
- Source payloads are bounded and redirects are revalidated.
- Complete indexes require explicit bootstrap item floors and at least 80% of the
  prior approved source-item count before they can assert that an item is missing.
- Per-source, per-domain, candidate JSON, and report byte ceilings fail closed before
  write-enabled publication, preventing malformed indexes from bloating the repository.
- Accounting sources carry explicit storage policies; current FASB indexes are
  metadata-only, and licensed payloads can be classified `licensed-no-store`.
- Reports contain provenance, deterministic item fingerprints, source failures,
  candidate changes, and conservative impact-crosswalk review routes.
- Candidate output is unapproved and must never be consumed as current authority.
- Promotion requires structured reviewer evidence and creates a separate review change.
- Security-sensitive official Actions are pinned to reviewed commit SHAs; Dependabot
  proposes controlled weekly update pull requests instead of moving tags at runtime.

## Commands

```powershell
python tools/authority_refresh/refresh.py --domain all --output-dir authority-refresh-output
python -m unittest discover -s tools/authority_refresh/tests -p "test_*.py"
python tools/authority_refresh/validate_system.py
```

Validate a reviewed candidate without writing anything:

```powershell
python tools/authority_refresh/promotion.py `
  --candidate authority/candidates/legal/runs/123456789-1/candidate.json `
  --approval authority/reviews/legal/2026-07-13-123456789-1.json `
  --release-date 2026-07-13
```

Use the immutable per-run candidate, not `latest`. Both candidate evidence and its
separately reviewed approval JSON must already be merged to `main` before the protected
workflow is dispatched. Every candidate change and potential-impact route requires an
exact structured resolution.

Replace the example workflow run ID, review filename, and dates with the selected merged evidence.
Only the protected GitHub workflow supplies the exact promotion confirmation string.
Even then, promotion archives the reviewed discovery baseline; approved legal PDFs,
accounting conclusions, and current-status assertions remain separately reviewed files.
