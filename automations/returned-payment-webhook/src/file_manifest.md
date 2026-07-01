# File Manifest

## Keep In Catalyst

The following files are appropriate to keep in the Catalyst function package.

| File | Keep? | Purpose |
|---|---:|---|
| `index.js` | Yes | Main runtime code. Handles webhook verification, OAuth2 API calls, idempotency, and invoice creation. |
| `package.json` | Yes | Declares Node dependencies and function package metadata. |
| `package-lock.json` | Yes | Locks dependency versions for reproducible deployments. |
| `catalyst-config.json` | Yes | Catalyst deployment metadata. Must not contain real environment variables or secrets. |
| `node_modules/` | Yes | Installed dependencies. Do not edit manually. |
| `README.md` | Yes | High-level explanation of the function. |
| `ENVIRONMENT_VARIABLES.md` | Yes | Explains required environment variables and safe live values. |
| `SECURITY_MODEL.md` | Yes | Explains the security architecture and why HMAC + OAuth2 are both used. |
| `OPERATIONS_RUNBOOK.md` | Yes | Practical operating procedures for dry runs, live mode, duplicate handling, and troubleshooting. |
| `CHANGELOG.md` | Optional | Human-readable record of major changes. |

## Delete From Catalyst To Reduce Clutter

These files are useful during development but should not remain in the production function view unless you specifically want an archive inside Catalyst.

| File | Delete? | Reason |
|---|---:|---|
| `README_PATCH.txt` | Yes | Patch-only artifact. No longer needed after production hardening. |
| `SETUP_NEXT_STEPS.md` | Yes | Temporary setup checklist. Superseded by `OPERATIONS_RUNBOOK.md`. |
| `index.security-hardening.diff` | Yes | Development diff artifact. Keep locally if desired, but remove from Catalyst production view. |
| `.env.example` | Yes | Can confuse operators into thinking secrets belong in files. Secrets belong in Catalyst Environment Variables. |
| `ENV_LIVE_HARDENED.example` | Yes | Replace with `ENVIRONMENT_VARIABLES.md`. Avoid keeping example env files in production code view. |
| `scripts/` | Usually Yes | Useful locally for testing, not needed in the Catalyst production function package. |

## Rule

Catalyst production should contain runtime files plus clear documentation. It should not contain patch notes, temporary migration files, token examples, or old setup debris.
