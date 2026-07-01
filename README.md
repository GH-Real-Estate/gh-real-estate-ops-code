# GH Real Estate Ops Code

Private technical source of truth for GH Real Estate automation code, Zoho setup notes, field maps, sanitized test payloads, deployment runbooks, and Codex/ChatGPT review context.

Final repository location:

```text
GH-Real-Estate/gh-real-estate-ops-code
```

## Operating Rule

```text
Zoho runs the business.
GitHub stores the code and technical map.
Codex/ChatGPT reviews and improves the code.
```

This repository is not a tenant file cabinet, accounting ledger, lease vault, or CRM replacement.

## What Belongs Here

This repo is for technical assets only:

- Deluge scripts.
- Zoho Books custom functions.
- Zoho CRM functions.
- Zoho Catalyst / webhook code.
- Sanitized Zoho Creator `.ds` exports.
- Zoho field maps.
- Zoho Contracts merge-field maps.
- Sanitized sample payloads.
- Install checklists.
- Smoke tests.
- Deployment logs.
- Codex/ChatGPT instructions.

## What Does Not Belong Here

Do not store live business records here:

- Signed leases.
- Tenant applications.
- Pay stubs.
- IDs, SSNs, immigration documents, or bank details.
- Real rent ledgers.
- ACH/payment records.
- Real tenant emails or phone numbers.
- Maintenance photos with tenant belongings.
- Raw webhook logs.
- OAuth tokens, API keys, refresh tokens, passwords, or private keys.

## Source-Of-Truth Split

| Area | Source Of Truth |
|---|---|
| Tenants / applicants / leasing pipeline | Zoho CRM |
| Rent invoices, payments, deposits, fees | Zoho Books |
| Signed leases and legal documents | Zoho Contracts / Zoho Sign / Zoho WorkDrive |
| Property files, inspection photos, notices | Zoho WorkDrive |
| Tenant portal / maintenance workflows | Zoho Creator, when ready |
| Code, automations, field maps, test cases | This private GitHub repo |

## Repository Map

```text
automations/
  late-fee-guard/                 # Zoho Books Deluge late-fee automation
  returned-payment-webhook/       # Zoho Catalyst / Node webhook for returned payments

docs/
  architecture/                   # How systems fit together
  business-rules/                 # Sanitized automation-relevant lease rules
  decision-log/                   # Why technical decisions were made
  runbooks/                       # Deploy, smoke-test, rollback, troubleshooting logs
  security/                       # PII/secrets/data classification rules
  setup/                          # GitHub, Codex, and repo setup instructions

zoho-books/
  custom-functions/               # Zoho Books custom functions and snippets
  field-maps/                     # Books item IDs, template IDs, custom fields, sanitized

zoho-crm/
  functions/                      # CRM Deluge functions and workflow snippets
  field-maps/                     # Zillow -> CRM -> Contracts -> Books mapping

zoho-creator/
  exports/                        # Sanitized .ds exports only
  docs/                           # Creator app setup/import notes

zoho-contracts/
  field-maps/                     # Contract merge-field maps only; no signed leases

samples/
  books/                          # Sanitized Zoho Books examples
  crm/                            # Sanitized Zoho CRM examples
  creator/                        # Sanitized Creator examples
  webhooks/                       # Sanitized webhook payloads
```

## Current Primary Systems

| System | Main File |
|---|---|
| Late Fee Guard | `automations/late-fee-guard/src/Late_Fee_Guard.deluge` |
| Returned Payment Webhook | `automations/returned-payment-webhook/src/index.js` |
| Zoho Books Automation Settings | `zoho-books/field-maps/books-automation-settings.md` |
| Lease Automation Rules | `docs/business-rules/lease-automation-rules.md` |
| Deployment Log | `docs/runbooks/deployment-log.md` |
| Codex/ChatGPT Instructions | `AGENTS.md` |

## Change Workflow

Use this workflow for material changes:

```text
1. Create a GitHub issue.
2. Create a branch.
3. Make the code/doc change.
4. Open a pull request.
5. Ask Codex/ChatGPT to review.
6. Merge after review.
7. Deploy manually into Zoho/Catalyst.
8. Record the deployment in docs/runbooks/deployment-log.md.
9. Run the smoke test checklist.
```

For emergency fixes, still record the final deployed commit and what was changed.

## Safety Standard

Any code that creates, updates, deletes, invoices, charges, emails, or texts must have:

- Dry-run behavior where feasible.
- Duplicate-prevention / idempotency.
- Central Time date handling if rent/late-fee deadlines are involved.
- No tenant PII in logs.
- No secrets in files.
- A rollback note.
- A deployment log entry.
