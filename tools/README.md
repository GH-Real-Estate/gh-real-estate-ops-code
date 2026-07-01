# Tools

Small local helper scripts for repository hygiene.

These tools are optional and do not deploy anything.

## Available Tools

- `tools/safety/pre-commit-safety-check.py`: local scan for obvious secret/PII mistakes before committing.

Run from the repository root:

```bash
python3 tools/safety/pre-commit-safety-check.py
```

This is only a helper. Manual review is still required.
