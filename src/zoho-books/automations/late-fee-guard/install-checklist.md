# Late Fee Guard Install Checklist

## Pre-Install

- [ ] Final late-fee Deluge code committed to `src/zoho-books/automations/late-fee-guard/Late_Fee_Guard.deluge`.
- [ ] Final monthly interest Deluge code committed to `src/zoho-books/automations/late-fee-guard/Monthly_Interest_Billing.deluge`.
- [ ] Verify `enableInterestOnDelinquentRent = false` in the installed late-fee guard.
- [ ] Code reviewed for duplicate prevention.
- [ ] Code reviewed for Central Time handling and monthly interest schedule window.
- [ ] Code reviewed for no PII/secrets logging.
- [ ] Lease automation rules verified in `docs/business-rules/lease-automation-rules.md`.
- [ ] Zoho Books item/template/custom field values documented in `src/zoho-books/field-maps/books-automation-settings.md`.

## Zoho Books Setup

- [ ] Confirm Zoho Books connection name is `zbooks` or update both scripts before install.
- [ ] Confirm late-fee item exists.
- [ ] Confirm interest item exists and is appropriate for a line named `Monthly Interest Charge`.
- [ ] Confirm late-fee invoice template exists.
- [ ] Confirm any duplicate-prevention custom field exists if `interestIdempotencyFieldApiName` is configured.
- [ ] Confirm rent invoice flag field `cf_is_rent_invoice` exists and is populated only on eligible rent/source invoices.
- [ ] Confirm interest invoices are not marked as rent.
- [ ] Confirm schedule/trigger time for the late-fee guard.
- [ ] Confirm monthly interest schedule runs only on the last day after close of business or on the first day of the following month.

## Monthly Interest Config

- [ ] `DRY_RUN = true` for first deployment run.
- [ ] `POST_INTEREST_INVOICES = false` for first deployment run.
- [ ] `SEND_INTEREST_INVOICES = false` unless live sending is explicitly approved.
- [ ] `INTEREST_ANNUAL_RATE = 10.00` unless a reviewed lease/legal change requires another rate.
- [ ] `interestMinimumPostingAmount = 10.00`.
- [ ] Keep `MANUAL_INTEREST_RUN_OVERRIDE = false` except for controlled manual testing.

## Test

- [ ] Run late-fee guard on a non-late test invoice; no fee created.
- [ ] Run late-fee guard on a late test invoice; correct D5/D10 fee behavior.
- [ ] Run late-fee guard again on same test invoice; no duplicate fee created.
- [ ] Run monthly interest in dry-run mode for the current billing period; report shows tenants checked, invoices checked, exclusions, principal, eligible days, calculated interest, and would-create decisions.
- [ ] Confirm interest below `$10.00` is skipped and logged.
- [ ] Confirm a tenant with multiple eligible rent invoices produces one consolidated monthly interest invoice in dry run.
- [ ] Confirm existing `GHRE_INT_{customer_id}_{YYYYMM}` invoice prevents duplicates.
- [ ] Confirm late-fee, interest, processing-fee, NSF, security-deposit, application-fee, voided, written-off, and zero-balance invoices are excluded.
- [ ] Confirm invoice template.
- [ ] Confirm logs contain no PII.

## Deployment

- [ ] Install late-fee guard code in Zoho Books / target runtime.
- [ ] Install monthly interest code as a separate Zoho Books scheduled function.
- [ ] Record deployment in `docs/runbooks/deployment-log.md`.
- [ ] Run dry-run smoke test and review output before enabling posting.
- [ ] Enable posting only by setting `DRY_RUN=false` and `POST_INTEREST_INVOICES=true`.
- [ ] Keep `SEND_INTEREST_INVOICES=false` until Draft invoice output is reviewed.
- [ ] Keep rollback copy/reference.
