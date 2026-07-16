# GH Real Estate Ops Code

Public, sanitized technical source of truth for GH Real Estate automation code, Zoho setup notes, field maps, synthetic test payloads, deployment runbooks, Codex/ChatGPT review context, the approved public legal-authority library, and the governed accounting-authority registry.

Final repository location:

```text
GH-Real-Estate/gh-real-estate-ops-code
```

## Operating Rule

```text
Zoho runs the business.
GitHub stores the code, technical map, approved public legal-authority library, and governed accounting authority/control layer.
Codex/ChatGPT reviews and improves the code.
```

This repository is not a tenant file cabinet, accounting ledger, lease vault, CRM replacement, or production configuration store.

Because the repository is public, every commit must be treated as permanently disclosed. Keep credentials, operational IDs, tenant/customer data, private documents, production payloads, and licensed non-redistributable material outside GitHub. See `SECURITY.md` and `docs/security/data-classification.md` before contributing.

## Structure Rule

This repo is organized by **source system / runtime**, not by generic workflow labels.

That means:

- Zoho Books automations live under `src/zoho-books/`.
- Zoho Payments webhooks live under `src/zoho-payments/`.
- Zoho CRM field maps and functions live under `src/zoho-crm/`.
- Zoho Creator exports/docs live under `src/zoho-creator/`.
- Zoho Contracts field governance, clause authoring standards, Draft implementation packages, validation, and merge maps live under `src/zoho-contracts/`.
- Zoho Sign field/tag governance lives separately under `src/zoho-sign/`.

Within each source system, each production automation gets its own folder unless it is truly the same runtime responsibility. Late fees, monthly delinquent-rent interest, and returned-payment fees are separate responsibilities and are stored separately.

The top-level `legal/` tree is a governed public-authority reference library, not runtime source code. Its own README, manifests, status labels, validation, and review rules control that subtree.

The top-level `accounting/` tree is the governed accounting research and policy-control layer. It stores GH-authored analysis, tax/GAAP sourcebooks, FASB locators, applicability metadata, review dates, and generated Project Sources. It does not store FASB Codification text.

The top-level `authority/` tree and `tools/authority_refresh/` package provide a review queue around those two approved libraries. A weekly Sunday workflow polls 14 legal and 9 accounting official-source indexes, preserves bounded discovery evidence, and opens a draft pull request only when a human review is required. Discovery never rewrites approved legal text, accounting conclusions, effective dates, or production automation.

## What Belongs Here

This repo is for technical and governed authority assets:

- Deluge scripts.
- Zoho Books custom functions.
- Zoho CRM functions.
- Zoho Catalyst / webhook code.
- Sanitized Zoho Creator `.ds` exports.
- Zoho field maps.
- Zoho Contracts field maps, clause definitions, authoring standards, and sanitized Draft implementation packages.
- Zoho Sign field/tag references and integration guardrails.
- Sanitized sample payloads.
- Install checklists.
- Smoke tests.
- Deployment logs.
- Codex/ChatGPT instructions.
- Repository-wide document drafting, typography, and output-QA standards.
- Local repo hygiene tools.
- Approved public legal-authority sources, release manifests, searchable extracts, and monitoring tools under `legal/`.
- GH-authored accounting policies, tax/GAAP sourcebooks, FASB locators, applicability registries, and review controls under `accounting/`.
- Unapproved discovery candidates, structured review evidence, dated refresh snapshots, and authority-to-code impact mappings under `authority/`.

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
- FASB Codification text, screenshots, print exports, scraped FASB content, or licensed commercial accounting material without explicit permission for repository and generative-AI use.

## Source-Of-Truth Split

| Area | Source Of Truth |
|---|---|
| Tenants / applicants / leasing pipeline | Zoho CRM |
| Rent invoices, payments, deposits, fees | Zoho Books |
| Signed leases and legal documents | Zoho Contracts / Zoho Sign / Zoho WorkDrive |
| Property files, inspection photos, notices | Zoho WorkDrive |
| Tenant portal / maintenance workflows | Zoho Creator, when ready |
| Code, automations, field maps, test cases | This public, sanitized GitHub repo |
| Approved public legal authorities and source history | `legal/` in this public, sanitized GitHub repo; live official source controls |
| Accounting policies, sourcebooks, FASB locators, and review history | `accounting/` in this public, sanitized GitHub repo; authorized live FASB access and reviewed professional conclusions control |
| Discovery candidates and review evidence | `authority/` in this public, sanitized GitHub repo; candidates are never current authority or production inputs |

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
    clauses/
      README.md
      residential-lease-agreement/
    contract-types/
      residential-lease-agreement/
    field-maps/
      contract-field-registry.json
      contract-field-registry.md
      lease-merge-fields.md
      animal-addendum-merge-fields.md
    runbooks/
      apply-contract-authoring-standard.md
    schemas/
      clause-definition.schema.json
      contract-type-implementation.schema.json
      contract-field-registry.schema.json
      document-field-map.schema.json
      source-manifest.schema.json
      source-to-clause-crosswalk.schema.json
    scripts/
      validate_contract_authoring_standard.py
      validate_contract_field_registry.py
      validate_residential_lease_implementation.py
    standards/
      contract-authoring-standard.json
      contract-authoring-standard.md
    templates/
      clause-definition.template.json
    tests/
      test_validate_contract_authoring_standard.py
      test_validate_contract_field_registry.py
      test_validate_recipient_policy.py
      test_validate_residential_lease_implementation.py

  zoho-sign/
    README.md
    field-tags/
      zoho-contracts-text-tag-registry.json
      zoho-contracts-text-tag-registry.md
    recipient-manifests/
      ghre-canonical-recipient-policy.json
      residential-lease-one-tenant.recipient-manifest.json
      residential-lease-two-tenants.recipient-manifest.json
      residential-lease-three-tenants.recipient-manifest.json

legal/
  README.md
  CURRENT_AUTHORITY_INDEX.md
  PROJECT_INSTRUCTIONS.md
  SOURCE_GAPS.md
  generated/project-sources/current/
  manifests/
  text/current/authorities/
  scripts/

accounting/
  README.md
  CURRENT_AUTHORITY_INDEX.md
  PROJECT_INSTRUCTIONS.md
  FASB_APPLICABILITY_INDEX.md
  ACCOUNTING_POLICY_MATRIX.md
  SOURCE_GAPS.md
  generated/project-sources/current/
  manifests/
  text/current/
  scripts/

authority/
  README.md
  candidates/
  reviews/
  releases/
  snapshots/
  schemas/
  impact_crosswalk.json

docs/
  standards/
    document-drafting-standard.md
    document-style-profile.json
  architecture/
    system-overview.md
  adr/
    0001-one-private-repo-for-gh-real-estate.md
  business-rules/
    lease-automation-rules.md
  runbooks/
    authority-refresh.md
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
  authority_refresh/
    README.md
    refresh.py
    promotion.py
    validate_system.py
    config/
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
| Zoho Contracts Field Registry | `src/zoho-contracts/field-maps/contract-field-registry.md` |
| Zoho Contracts Authoring Standard | `src/zoho-contracts/standards/contract-authoring-standard.md` |
| Residential Lease Draft Implementation | `src/zoho-contracts/contract-types/residential-lease-agreement/README.md` |
| Zoho Sign Text Tag Registry | `src/zoho-sign/field-tags/zoho-contracts-text-tag-registry.md` |
| Zoho Sign Recipient Policy | `src/zoho-sign/recipient-manifests/README.md` |
| Lease Automation Rules | `docs/business-rules/lease-automation-rules.md` |
| Deployment Log | `docs/runbooks/deployment-log.md` |
| Codex/ChatGPT Instructions | `AGENTS.md` |
| Document Drafting and Typography Standard | `docs/standards/document-drafting-standard.md` |
| Legal Authority Index | `legal/CURRENT_AUTHORITY_INDEX.md` |
| Accounting Authority Index | `accounting/CURRENT_AUTHORITY_INDEX.md` |
| Authority Refresh Governance | `authority/README.md` |
| Authority Refresh Runbook | `docs/runbooks/authority-refresh.md` |
| CI Failure Response | `docs/runbooks/ci-failure-response.md` |

## Authority Refresh Controls

- **Weekly discovery:** `Authority Discovery` runs every Sunday at `11:17 UTC` and can also be started manually. It checks the 14-source legal catalog and 9-source accounting catalog, then reports `current`, `review_required`, or `degraded`.
- **Existing monitors:** `Legal Source Monitor` still performs its weekly approved-payload comparison at `12:27 UTC` each Monday. `Accounting Authority Review Calendar` still checks stored FASB/accounting review dates monthly at `13:41 UTC` on day 1.
- **No automatic currentness decision:** a discovery change creates or updates candidate evidence and a draft pull request. It does not auto-promote, auto-merge, change the dated approved libraries, or change operational code.
- **Qualified review:** legal effect and applicability require counsel; GAAP conclusions require a CPA or qualified accounting reviewer using authorized FASB access; tax conclusions require tax-year-specific professional review. Evidence and every candidate resolution must be recorded.
- **Protected promotion:** reviewed discovery evidence can be archived only through the `authority-production` GitHub environment and exact confirmation `PROMOTE_REVIEWED_AUTHORITY_RELEASE`. That workflow opens another draft pull request and never merges it.

The July 12, 2026 approved legal and accounting baselines remain unchanged by this automation. A green run is evidence that configured checks completed, not a compliance, completeness, legal-currentness, GAAP, or tax certification. See [`docs/runbooks/authority-refresh.md`](docs/runbooks/authority-refresh.md) for triage, review, promotion, and rollback.

## CI Failure Response

`CI Failure Response` is retained as a manual simulation and validation tool; it no longer subscribes to completed workflow events or automatically creates and recovers real incident issues. Normal GitHub failed-check notifications are the default alerting mechanism, and the external `GH Repo CI Auto-Repair` Codex task should remain paused or disabled.

Manual simulations still use trusted default-branch code, never execute a failed revision or artifacts, and store no OpenAI key in GitHub. See [`docs/runbooks/ci-failure-response.md`](docs/runbooks/ci-failure-response.md) for current behavior, smoke testing, real-failure triage, and historical verification.

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
