# Security Policy

## Scope

This repo is private but should still be treated as a code repository, not a secure tenant-document vault.

## Never commit

- API keys.
- OAuth client secrets.
- OAuth refresh tokens.
- Passwords.
- Private keys.
- Webhook secrets.
- Real tenant PII.
- Signed leases.
- Tenant applications.
- Pay stubs.
- Bank details.
- ACH/payment records.
- Raw production logs.
- Unredacted webhook payloads.
- Real Zoho exports containing customers, invoices, payments, portal users, files, or signatures.

## Allowed

- Code.
- Sanitized sample payloads.
- Field API names.
- Non-secret Zoho item IDs/template IDs if needed for automation.
- Install checklists.
- Deployment logs with no PII.
- Technical architecture diagrams/notes.

## If a secret is committed

1. Rotate the secret immediately in the source system.
2. Remove the secret from the repository.
3. Treat Git history as exposed unless fully cleaned.
4. Add a sanitized incident entry to `docs/security/security-incidents.md`.
5. Update `.gitignore`, docs, or review checklist to prevent repeat mistakes.

## If tenant PII is committed

1. Remove the file immediately.
2. Do not add more tenant data while trying to fix it.
3. Record a sanitized incident in `docs/security/security-incidents.md`.
4. Clean history if needed.
5. Move the data back to the proper system: Zoho CRM, Zoho Books, Zoho WorkDrive, Zoho Contracts, or Zoho Creator.
