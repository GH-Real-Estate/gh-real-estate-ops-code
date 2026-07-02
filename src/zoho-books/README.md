# Zoho Books

Zoho Books is the financial source of truth for GH Real Estate.

Use this area for code and technical documentation that is owned by, installed in, or directly dependent on Zoho Books.

## Contents

```text
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

field-maps/
  books-automation-settings.md
```

## Automations

| Automation | Runtime | Purpose |
|---|---|---|
| Apply Unused Credits | Zoho Books Invoice Created workflow custom function | Applies available matching-branch customer credits to a newly-created invoice |
| Late Fee Guard | Zoho Books scheduled function | Creates lease-aligned late-fee and delinquent-rent interest invoices |

## Rules

- Do not store rent ledgers, ACH records, bank details, or real payment exports here.
- Keep only code, field maps, sanitized test data, and setup notes.
- Any production-relevant change must be recorded in `docs/runbooks/deployment-log.md`.
