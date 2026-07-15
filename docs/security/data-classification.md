# Public Repository Data Classification

Everything committed here must be treated as permanently public, including deleted history and forks.

## Green: allowed

- Original code and technical documentation.
- Synthetic payloads and fake contact/property values.
- Synthetic aliases that cannot authenticate and have never been publicly correlated to private records.
- Public statutes, regulations, court material, government guidance, and official-source locators.
- GH-authored legal/accounting analysis that does not reproduce restricted licensed content.
- Sanitized deployment records with no private configuration or production payload.

## Yellow: maintainer review required

- Zoho Creator `.ds` exports; webhook, CRM, Books, Contracts, or lease-rule examples.
- Error messages, stack traces, screenshots, generated authority files, and third-party material.

Yellow material is allowed only when synthetic or irreversibly sanitized, redistributable, operational IDs are replaced with public aliases, provenance is documented, and governed hashes remain valid.

## Red: never allowed

- Credentials, secrets, tokens, private keys, cookies, webhook secrets, or credentialed URLs.
- Real tenant, applicant, customer, employee, or vendor PII.
- Identity/immigration records, bank data, pay stubs, signatures, applications, signed leases, payment records, or private photos.
- Raw production logs/payloads/exports, backups, databases, operational IDs, or the private alias crosswalk.
- FASB Codification text, screenshots, print exports, or licensed commercial material without explicit redistribution and AI-use rights.

## Known legacy identifier exposure

Before the 2026-07-14 current-tree redaction, live Zoho Account IDs existed in this public repository. The public pull-request diff correlates those historic IDs with the replacement aliases. Treat both values as public, non-secret identifiers and never use them as credentials or authorization factors.

The current safety controls prevent new operational IDs from entering the current tree, but they cannot retract public clones, forks, caches, or pull-request diffs. A history rewrite and GitHub Support cache review would be a separate destructive incident-response project and still could not recall third-party copies. This repository therefore makes no claim that the legacy alias crosswalk is private.
