# GH Real Estate Ops Code

Private technical source of truth for GH Real Estate automation code, Zoho setup notes, field maps, sanitized test payloads, deployment runbooks, and Codex/ChatGPT review context.

## Current recommended GitHub location

Use this final repository location:

```text
GH-Real-Estate/gh-real-estate-ops-code
```

Your screenshot appears to show an existing org-owned repo named:

```text
GH-Real-Estate/gh-real-estate
```

If that repo is the one you already created, rename it to:

```text
gh-real-estate-ops-code
```

Do not create multiple GH Real Estate code repos right now. One private repo gives Codex/ChatGPT enough context to understand how the automations, field maps, lease rules, and deployment notes work together.

## What belongs here

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

## What does not belong here

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

## Source-of-truth split

| Area | Source of truth |
|---|---|
| Tenants / applicants / leasing pipeline | Zoho CRM |
| Rent invoices, payments, deposits, fees | Zoho Books |
| Signed leases and legal documents | Zoho Contracts / Zoho Sign / Zoho WorkDrive |
| Property files, inspection photos, notices | Zoho WorkDrive |
| Tenant portal / maintenance workflows | Zoho Creator, when ready |
| Code, automations, field maps, test cases | This private GitHub repo |

## Repository map

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
  field-maps/                     # Contract merge-field maps
  templates/                      # Template notes only; no signed leases

samples/
  books/                          # Sanitized Zoho Books examples
  crm/                            # Sanitized Zoho CRM examples
  creator/                        # Sanitized Creator examples
  webhooks/                       # Sanitized webhook payloads

scripts/                          # Local helper scripts; no secrets
```

## Operating rule

```text
Zoho runs the business.
GitHub stores the code and technical map.
Codex/ChatGPT reviews and improves the code.
```

## Change workflow

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

## First files to replace

After the repo is created, replace these placeholders with your real sanitized code/docs:

| Current file | Replace with |
|---|---|
| `automations/late-fee-guard/src/Late_Fee_Guard.deluge` | Your current final Late Fee Guard Deluge code |
| `automations/returned-payment-webhook/src/index.js` | Your current returned-payment webhook code, if used |
| `zoho-books/field-maps/books-automation-settings.md` | Actual non-secret item IDs, template IDs, and API field names |
| `docs/business-rules/lease-automation-rules.md` | Automation-relevant lease rules only, verified against final signed lease |

## Safety standard

Any code that creates, updates, deletes, invoices, charges, emails, or texts must have:

- Dry-run behavior where feasible.
- Duplicate-prevention / idempotency.
- Central Time date handling if rent/late-fee deadlines are involved.
- No tenant PII in logs.
- No secrets in files.
- A rollback note.
- A deployment log entry.
