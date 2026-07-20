# GH Real Estate System Overview

## System Roles

```text
Zillow / Zoho Forms
  -> application intake and verification forms

Zoho Sites / Zoho Bookings
  -> approved public entry points and appointment scheduling

Zoho One / Zoho Directory
  -> organization identity, user lifecycle, application assignment, and access governance

Zoho API Console / Zoho Accounts
  -> OAuth client registration, consent, regional authorization, and token lifecycle

Zoho CRM
  -> applicant, tenant, property/unit relationship tracking

Zoho Contracts / Zoho Sign / WorkDrive
  -> lease generation, signature, signed document storage

Zoho Books / Zoho Payments
  -> invoices, rent, payments, deposits, fees, accounting truth

Zoho Creator
  -> tenant portal / maintenance workflows when ready

Zoho Catalyst / Zoho Flow
  -> governed custom runtime, webhooks, event processing, and bounded orchestration

Zoho Calendar / Zoho Meeting / Zoho ToDo
  -> scheduling, collaboration, and task coordination; these do not replace the owning business system

Zoho People
  -> employee HR and workforce operations when adopted; never tenant or applicant authority

Zoho Mail / Zoho Voice / Twilio
  -> approved email, telephony, SMS, and voice delivery; delivery or call status is not business-state authority

Zoho Analytics
  -> derivative reporting and dashboards; corrections return to the owning system

GitHub
  -> code, field maps, sanitized samples, runbooks, approved dated authority libraries, version history

Codex / ChatGPT
  -> review, debugging, patching, documentation, test planning
```

## Repository Organization

Code and technical docs are grouped under `src/` by owning system:

```text
src/zoho-books/      # Books-owned automations, field maps, and financial automation docs
src/zoho-payments/   # Payments-originated webhooks and event handling
src/zoho-crm/        # CRM field maps and CRM functions
src/zoho-creator/    # Creator import/export notes and sanitized exports
src/zoho-contracts/  # Contracts merge-field maps only
```

Cross-system docs remain under `docs/`. Sanitized sample payloads remain under `samples/`.

The dated, official-source-anchored product knowledge collection lives under
`docs/reference/zoho-suite/`. Its Markdown files are retrieval context for
ChatGPT, Codex, and the GitHub connector; they do not override current official
provider documentation, approved policy, authenticated live metadata, or
runtime deployment evidence.

Authority governance is separated from runtime code:

```text
allowlisted official indexes
  -> weekly Sunday read-only discovery (14 legal + 9 accounting)
  -> current | review_required | degraded
  -> candidate evidence and draft pull request
  -> counsel / CPA / tax / licensing review as applicable
  -> protected evidence-promotion workflow
  -> draft promotion pull request
  -> separately reviewed dated legal or accounting release
```

`legal/` and `accounting/` remain the approved dated research baselines. `authority/` contains unapproved candidates, structured review evidence, discovery snapshots, and the impact crosswalk. `tools/authority_refresh/` contains standard-library discovery, validation, and promotion controls. No discovery or promotion workflow deploys to Zoho, changes books, edits a lease, changes tenant treatment, updates runtime code, or merges itself.

The weekly discovery workflow runs every Sunday at `11:17 UTC`. It supplements, but does not replace, the weekly Monday `12:27 UTC` legal approved-source hash monitor or the monthly day-1 `13:41 UTC` accounting review-date calendar. FASB discovery stores metadata only; exact GAAP conclusions require authorized live access and qualified review. Source failures preserve the approved baseline and visibly degrade the affected currentness claim.

## CI Failure Response

```text
failed GitHub Actions check
  -> normal GitHub notification
  -> operator inspects the current run
  -> focused repair PR only when a repository defect is proven
  -> normal checks and human review
  -> intentional merge
```

The repository responder is manual-simulation-only; automatic `workflow_run` incidents and recovery closure are disabled. The external `GH Repo CI Auto-Repair` Codex task should remain paused or disabled. High-risk and governed domains remain human-gated. See `docs/runbooks/ci-failure-response.md`.

## Non-Negotiable Split

Zoho owns live business data. GitHub owns technical logic and sanitized documentation.

Official law, authorized accounting authority, signed agreements, and reviewed professional conclusions control over repository summaries and automation output. GitHub provides versioned evidence and review gates; it does not certify legal, GAAP, tax, or operational compliance.
