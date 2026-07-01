# Late Fee Guard Install Checklist

## Pre-install

- [ ] Final Deluge code committed to `automations/late-fee-guard/src/Late_Fee_Guard.deluge`.
- [ ] Code reviewed for duplicate prevention.
- [ ] Code reviewed for Central Time handling.
- [ ] Code reviewed for no PII/secrets logging.
- [ ] Lease automation rules verified in `docs/business-rules/lease-automation-rules.md`.
- [ ] Zoho Books item/template/custom field values documented in `zoho-books/field-maps/books-automation-settings.md`.

## Zoho Books setup

- [ ] Confirm Zoho Books connection name.
- [ ] Confirm late-fee item exists.
- [ ] Confirm late-fee invoice template exists.
- [ ] Confirm any duplicate-prevention custom field exists.
- [ ] Confirm any interest item exists only if interest automation is enabled.
- [ ] Confirm schedule/trigger time.

## Test

- [ ] Run on a non-late test invoice; no fee created.
- [ ] Run on a late test invoice; correct fee created.
- [ ] Run again on same test invoice; no duplicate fee created.
- [ ] Confirm invoice template.
- [ ] Confirm logs contain no PII.

## Deployment

- [ ] Install code in Zoho Books / target runtime.
- [ ] Record deployment in `docs/runbooks/deployment-log.md`.
- [ ] Run smoke test.
- [ ] Keep rollback copy/reference.
