# Late Fee Guard

Zoho Books Deluge automation for applying lease-compliant late fees.

## Production file

```text
automations/late-fee-guard/src/Late_Fee_Guard.deluge
```

Replace the placeholder with the current final Deluge script actually installed or approved for Zoho Books.

## Required safety behavior

- Must not create duplicate late fees.
- Must use Central Time rules consistently.
- Must match the final signed lease.
- Must support dry-run behavior if feasible.
- Must not log tenant PII.
- Must document all non-secret Zoho item IDs, template IDs, and custom-field API names in `zoho-books/field-maps/books-automation-settings.md`.

## Before live deployment

1. Confirm rules against final signed lease.
2. Confirm Zoho Books item IDs/template IDs/custom fields.
3. Run dry-run, if available.
4. Test duplicate prevention by running twice on the same test invoice.
5. Update `docs/runbooks/deployment-log.md`.
6. Run `docs/runbooks/smoke-test-checklist.md`.
