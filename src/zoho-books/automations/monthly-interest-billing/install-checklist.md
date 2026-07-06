# Monthly Interest Billing Install Checklist

## Pre-Install

- [ ] Final monthly interest Deluge code committed to `src/zoho-books/automations/monthly-interest-billing/Monthly_Interest_Billing.deluge`.
- [ ] Code saved successfully in the Zoho Books schedule editor.
- [ ] Code reviewed for duplicate prevention.
- [ ] Code reviewed for no PII/secrets logging.
- [ ] Lease automation rules verified in `docs/business-rules/lease-automation-rules.md`.
- [ ] Zoho Books item/template/custom field values documented in `src/zoho-books/field-maps/books-automation-settings.md`.

## Zoho Books Setup

- [ ] Schedule name is `GHRE Monthly Interest Billing`.
- [ ] Confirm Zoho Books connection name is `zbooks` or update the script before install.
- [ ] Confirm interest item ID `5858793000003568001` exists and maps to delinquent-rent interest.
- [ ] Confirm rent invoice flag field `cf_is_rent_invoice` exists and is populated only on eligible rent/source invoices.
- [ ] Confirm source invoice token field `cf_late_fee_stages_applied` exists.
- [ ] Confirm interest invoices are not marked as rent.
- [ ] Confirm monthly interest schedule runs monthly after close of business.
- [ ] Confirm returned-payment / NSF fee handling remains under the Zoho Payments returned-payment webhook.

## Config

- [ ] `interestAprPct = 10.00` matches the current lease template.
- [ ] `interestMinimumInvoiceAmount = 10.00` is intentional.
- [ ] `interestStartsDaysAfterDue = 30` is intentional.
- [ ] `interestFirstEligibleDaysAfterDue = 31` is intentional.
- [ ] `autoEmailInterestInvoices = true` is approved before production email sending.

## Test

- [ ] Run against an invoice fewer than 31 days overdue; no interest invoice created.
- [ ] Run against one eligible rent invoice; one interest row is prepared.
- [ ] Run against one customer with multiple eligible rent invoices; one consolidated monthly interest invoice is created.
- [ ] Run again for the same customer and period; no duplicate invoice is created.
- [ ] Confirm source rent invoice tokens include `INTPERIOD_YYYYMM`, `INTINV_YYYYMM=...`, `INTTHRU=...`, and `INTTOTAL=...`.
- [ ] Confirm late-fee, RF, NSF, processing-fee, application-fee, security-deposit, voided, deleted, and zero-balance invoices are excluded.
- [ ] Confirm logs contain no PII.

## Deployment

- [ ] Install `Monthly_Interest_Billing.deluge` as the separate Zoho Books monthly interest scheduled function.
- [ ] Record deployment in `docs/runbooks/deployment-log.md`.
- [ ] Keep rollback copy/reference.
