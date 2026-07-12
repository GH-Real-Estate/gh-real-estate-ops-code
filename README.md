# GH Real Estate Ops Code

Private source of truth for GH Real Estate automation code, Zoho setup notes, field maps, sanitized test payloads, deployment runbooks, Codex/ChatGPT review context, and the approved public legal-authority library.

Final repository location:

```text
GH-Real-Estate/gh-real-estate-ops-code
```

## Operating Rule

```text
Zoho runs the business.
GitHub stores the code, technical map, and approved public legal-authority library.
Codex/ChatGPT reviews and improves the code.
```

This repository is not a tenant file cabinet, accounting ledger, lease vault, or CRM replacement.

## Structure Rule

This repo is organized by **source system / runtime**, not by generic workflow labels.

That means:

- Zoho Books automations live under `src/zoho-books/`.
- Zoho Payments webhooks live under `src/zoho-payments/`.
- Zoho CRM field maps and functions live under `src/zoho-crm/`.
- Zoho Creator exports/docs live under `src/zoho-creator/`.
- Zoho Contracts merge maps live under `src/zoho-contracts/`.

Within each source system, each production automation gets its own folder unless it is truly the same runtime responsibility. Late fees, monthly delinquent-rent interest, and returned-payment fees are separate responsibilities and are stored separately.

The top-level `legal/` tree is a governed public-authority reference library, not runtime source code. Its own README, manifests, status labels, validation, and review rules control that subtree.

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
- Local repo hygiene tools.
- Approved public legal-authority sources, release manifests, searchable extracts, and monitoring tools under `legal/`.

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
| Approved public legal authorities and source history | `legal/` in this private GitHub repo; live official source controls |

## Repository Map

```text
src/
  zoho-books/
    README.md
    automations/
      apply-unused-credits/
        ApplyUnusedCredits.deluge
        README.md
        install-checklist.md
        test-cases.md
      late-fee-guard/
        Late_Fee_Guard.deluge
        README.md
        install-checklist.md
        test-cases.md
      monthly-interest-billing/
        Monthly_Interest_Billing.deluge
        README.md
        install-checklist.md
        test-cases.md
    field-maps/
      books-automation-settings.md

  zoho-payments/
    README.md
    webhooks/
      returned-payment-fee/
        README.md
        catalyst-config.json
        package.json
        package-lock.json
        src/
          index.js
        test/
          source-contract.test.js
        docs/
          changelog.md
          environment-variables.md
          file-manifest.md
          operations-runbook.md
          security-model.md
        install-checklist.md
        test-cases.md

  zoho-crm/
    README.md
    field-maps/
      zillow-to-crm-to-contracts.md

  zoho-creator/
    README.md
    docs/
      import-notes.md

  zoho-contracts/
    README.md
    field-maps/
      lease-merge-fields.md

legal/
  README.md
  CURRENT_AUTHORITY_INDEX.md
  PROJECT_INSTRUCTIONS.md
  SOURCE_GAPS.md
  generated/project-sources/current/
  manifests/
  text/current/authorities/
  scripts/

docs/
  architecture/
    system-overview.md
  adr/
    0001-one-private-repo-for-gh-real-estate.md
  business-rules/
    lease-automation-rules.md
  runbooks/
    deployment-log.md
    rollback-checklist.md
    smoke-test-checklist.md
  security/
    data-classification.md
    security-incidents.md
  setup/
    github-settings-checklist.md

samples/
  zoho-books/
    invoice.sample.json
  zoho-crm/
    applicant.sample.json
  zoho-creator/
    maintenance-request.sample.json
  zoho-payments/
    returned-payment.sample.json

tools/
  README.md
  safety/
    pre-commit-safety-check.py
```

## Current Primary Systems

| System | Main File |
|---|---|
| Apply Unused Credits | `src/zoho-books/automations/apply-unused-credits/ApplyUnusedCredits.deluge` |
| Late Fee Guard | `src/zoho-books/automations/late-fee-guard/Late_Fee_Guard.deluge` |
| Monthly Interest Billing | `src/zoho-books/automations/monthly-interest-billing/Monthly_Interest_Billing.deluge` |
| Returned Payment Webhook | `src/zoho-payments/webhooks/returned-payment-fee/src/index.js` |
| Zoho Books Automation Settings | `src/zoho-books/field-maps/books-automation-settings.md` |
| Lease Automation Rules | `docs/business-rules/lease-automation-rules.md` |
| Deployment Log | `docs/runbooks/deployment-log.md` |
| Codex/ChatGPT Instructions | `AGENTS.md` |
| Legal Authority Index | `legal/CURRENT_AUTHORITY_INDEX.md` |

## Change Workflow

Default Codex/ChatGPT workflow for code, scripts, workflow files, configuration, tests, and production-relevant operational docs:

```text
1. Inspect the relevant repo files and current GitHub state.
2. Create a short-lived branch.
3. Make a focused, reviewable change.
4. Open a pull request into main.
5. Run or wait for all relevant local and GitHub checks.
6. Fix any code, documentation, formatting, test, or GitHub-check issues until checks pass.
7. Merge the pull request into main after checks pass and no blocker remains.
8. Verify main contains the final merged commit.
9. Confirm the merged head branch was deleted automatically, or delete it if tooling supports that.
10. Deploy manually into Zoho/Catalyst only when the change requires runtime deployment.
11. Record production-relevant deployments in docs/runbooks/deployment-log.md.
12. Run the smoke test checklist for live automation changes.
```

Do not merge if required checks are failing, unresolved requested changes remain, secrets/PII are suspected, the diff includes unrelated work, or a payment/tenant/lease/security risk requires human approval.

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
