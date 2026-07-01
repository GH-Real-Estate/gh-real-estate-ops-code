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
  -> code, field maps, sanitized samples, runbooks, version history

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

## Non-Negotiable Split

Zoho owns live business data. GitHub owns technical logic and sanitized documentation.
