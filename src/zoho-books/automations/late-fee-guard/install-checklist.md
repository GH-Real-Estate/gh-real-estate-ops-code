# Late Fee Guard Install Checklist

## Pre-Install

- [ ] Final late-fee Deluge code committed to `src/zoho-books/automations/late-fee-guard/Late_Fee_Guard.deluge`.
- [ ] Verify `enableInterestOnDelinquentRent = false` in the installed late-fee guard.
- [ ] Code reviewed for duplicate prevention.
- [ ] Code reviewed for no PII/secrets logging.
- [ ] Lease automation rules verified in `docs/business-rules/lease-automation-rules.md`.
- [ ] Zoho Books item/template/custom field values documented in `src/zoho-books/field-maps/books-automation-settings.md`.

## Zoho Books Setup

- [ ] Confirm Zoho Books connection name is `zbooks` or update the script before install.
- [ ] Confirm late-fee item exists.
- [ ] Confirm late-fee invoice template exists.
- [ ] Confirm rent invoice flag field `cf_is_rent_invoice` exists and is populated only on eligible rent/source invoices.
- [ ] Confirm late-fee schedule/trigger time is after the lease cutoff.
- [ ] Confirm monthly delinquent-rent interest is installed separately from `../monthly-interest-billing/Monthly_Interest_Billing.deluge`.
- [ ] Confirm returned-payment / NSF fee handling remains under the Zoho Payments returned-payment webhook unless a separate reconciliation-only schedule is later approved.

## Test

- [ ] Run late-fee guard on a non-late test invoice; no fee created.
- [ ] Run late-fee guard on a late test invoice; correct D5/D10 fee behavior.
- [ ] Run late-fee guard again on same test invoice; no duplicate fee created.
- [ ] Confirm late-fee, interest, processing-fee, NSF, security-deposit, application-fee, voided, written-off, and zero-balance invoices are excluded.
- [ ] Confirm pending ACH/online payment suppresses late-fee creation.
- [ ] Confirm failed/returned payment does not create an RF invoice from this function.
- [ ] Confirm the source rent invoice's partial-payment setting is unchanged after the ledger update.
- [ ] Confirm the created late-fee invoice inherits the source invoice's top-level `allow_partial_payments` value.
- [ ] Confirm logs contain no PII.

## Deployment

- [ ] Install `Late_Fee_Guard.deluge` as the daily Zoho Books late-fee scheduled function.
- [ ] Record deployment in `docs/runbooks/deployment-log.md`.
- [ ] Keep rollback copy/reference.
