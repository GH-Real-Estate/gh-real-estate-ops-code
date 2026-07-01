# Data Classification

## Green: allowed in GitHub

- Code.
- Sanitized sample payloads.
- Fake tenant/customer IDs.
- Non-secret API field names.
- Non-secret Zoho item/template IDs used by automation.
- Technical setup notes.
- Deployment logs without PII.

## Yellow: allowed only if sanitized

- Zoho Creator `.ds` exports.
- Webhook payloads.
- CRM/Books examples.
- Lease-rule summaries.
- Error messages.

Sanitized means no real tenant, payment, bank, signature, ID, lease, phone, email, or private document data.

## Red: never allowed in GitHub

- API keys, OAuth tokens, refresh tokens, passwords, private keys.
- SSNs, IDs, bank details, pay stubs, immigration docs.
- Signed leases and tenant applications.
- Real rent ledgers or payment records.
- Raw logs with tenant/client information.
- Maintenance photos with tenant belongings or private information.
