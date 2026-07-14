# GH Real Estate System Overview

## System Roles

```text
Zillow / Zoho Forms
  -> application intake and verification forms

Zoho CRM
  -> applicant, tenant, property/unit relationship tracking

Zoho Contracts / Zoho Sign / WorkDrive
  -> lease generation, signature, signed document storage

Zoho Books / Zoho Payments
  -> invoices, rent, payments, deposits, fees, accounting truth

Zoho Creator
  -> tenant portal / maintenance workflows when ready

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

Authority governance is separated from runtime code:

```text
allowlisted official indexes
  -> daily read-only discovery (13 legal + 9 accounting)
  -> current | review_required | degraded
  -> candidate evidence and draft pull request
  -> counsel / CPA / tax / licensing review as applicable
  -> protected evidence-promotion workflow
  -> draft promotion pull request
  -> separately reviewed dated legal or accounting release
```

`legal/` and `accounting/` remain the approved dated research baselines. `authority/` contains unapproved candidates, structured review evidence, discovery snapshots, and the impact crosswalk. `tools/authority_refresh/` contains standard-library discovery, validation, and promotion controls. No discovery or promotion workflow deploys to Zoho, changes books, edits a lease, changes tenant treatment, updates runtime code, or merges itself.

The daily discovery workflow runs at `11:17 UTC`. It supplements, but does not replace, the weekly Monday `12:27 UTC` legal approved-source hash monitor or the monthly day-1 `13:41 UTC` accounting review-date calendar. FASB discovery stores metadata only; exact GAAP conclusions require authorized live access and qualified review. Source failures preserve the approved baseline and visibly degrade the affected currentness claim.

## CI Failure Response

```text
completed monitored GitHub Actions run
  -> trusted default-branch incident responder
  -> deduplicated GitHub issue
  -> recurring Codex diagnosis
  -> focused draft repair PR only when low risk
  -> normal checks and human review
  -> intentional merge
  -> newer successful run closes the incident
```

The event responder cannot push code, approve, merge, deploy, execute the failed revision, or read its artifacts. High-risk and governed domains remain diagnosis-only. See `docs/runbooks/ci-failure-response.md`.

## Non-Negotiable Split

Zoho owns live business data. GitHub owns technical logic and sanitized documentation.

Official law, authorized accounting authority, signed agreements, and reviewed professional conclusions control over repository summaries and automation output. GitHub provides versioned evidence and review gates; it does not certify legal, GAAP, tax, or operational compliance.
