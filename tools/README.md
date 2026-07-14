# Tools

Small local helper scripts for repository hygiene.

These tools are optional and do not deploy anything.

## Available Tools

- `tools/safety/pre-commit-safety-check.py`: local scan for obvious secret/PII mistakes before committing.
- `tools/authority_refresh/refresh.py`: allowlisted legal/accounting official-index discovery that writes unapproved candidate evidence only.
- `tools/authority_refresh/validate_system.py`: validates authority catalogs, governance files, crosswalk paths, schemas, CODEOWNERS, and workflow safety contracts.
- `tools/authority_refresh/promotion.py`: validates structured human approval and, only with the protected exact confirmation, archives immutable review evidence and a discovery snapshot.

Run from the repository root:

```bash
python3 tools/safety/pre-commit-safety-check.py
python3 tools/authority_refresh/validate_system.py
python3 -m unittest discover -s tools/authority_refresh/tests -p "test_*.py" -v
```

Run a local discovery without modifying approved authority content:

```bash
python3 tools/authority_refresh/refresh.py --domain all --output-dir authority-refresh-output
```

The output states are `current`, `review_required`, and `degraded`. `current` means only that no candidate change was detected under the configured comparison policies and no degradation condition occurred. Any source `error`, or `configuration_required` on a critical source, makes the run `degraded`. Feed/API sources with `rolling-window` semantics do not report old items leaving a recent-results window as missing. An absent optional `CONGRESS_API_KEY` reports `configuration_required` for the noncritical Library of Congress source while critical enacted-law discovery continues through GovInfo.

These are operator tools, not legal, GAAP, tax, licensing, or compliance decision engines. They do not deploy anything, edit `legal/` or `accounting/`, change production systems, or merge pull requests. Follow [`../docs/runbooks/authority-refresh.md`](../docs/runbooks/authority-refresh.md) for review and protected promotion.
