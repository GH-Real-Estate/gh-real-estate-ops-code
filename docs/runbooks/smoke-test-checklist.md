# Smoke Test Checklist

Use before and after any live automation change.

## General

- [ ] Code in GitHub matches code installed in Zoho/runtime.
- [ ] Change is documented in deployment log.
- [ ] No secrets committed.
- [ ] No real tenant PII committed.
- [ ] Dry-run completed or not applicable.
- [ ] One controlled test completed.

## Apply Unused Credits

- [ ] New invoice not marked eligible by `cf_is_rent_invoice` does not apply anything.
- [ ] New invoice with no unused credits does not apply anything.
- [ ] New invoice with matching-branch customer-payment credit applies the correct amount.
- [ ] New invoice with matching-branch credit note applies the correct amount before customer-payment credits.
- [ ] New invoice with only an unused retainer payment does not POST credits and leaves the retainer untouched.
- [ ] New invoice with mixed credit-note, customer-payment, and retainer balances applies only the first two sources.
- [ ] Retainer unexpectedly returned by Zoho is skipped and never enters `invoice_payments`.
- [ ] Non-matching-branch credit is skipped.
- [ ] Blank branch IDs fail closed unless `allowEmptyBranchMatch=true` was intentionally verified.
- [ ] Running the function twice does not over-apply credits.
- [ ] Balance change before POST stops the function instead of over-applying.
- [ ] Simulated Zoho API failure logs an error and does not report success.
- [ ] Logs contain no PII, bank data, raw payloads, or secrets.

## Late Fee Guard

- [ ] Test invoice below threshold does not create a fee.
- [ ] Test invoice above threshold creates correct fee.
- [ ] Running the function twice does not duplicate the fee.
- [ ] Invoice template is correct.
- [ ] Time-zone behavior is correct.
- [ ] Logs contain no PII.

## Monthly Interest Billing

- [ ] Mid-month run exits unless `MANUAL_INTEREST_RUN_OVERRIDE=true`.
- [ ] Dry run reports tenants checked, invoices checked, exclusions, eligible principal, eligible days, and calculated interest.
- [ ] Interest below `$10.00` is skipped and logged.
- [ ] One tenant with multiple eligible rent invoices produces at most one monthly interest invoice.
- [ ] Existing `GHRE_INT_{customer_id}_{YYYYMM}` invoice prevents duplicates.
- [ ] Late-fee, interest, processing-fee, NSF, security-deposit, application-fee, voided, written-off, and zero-balance invoices are excluded.
- [ ] Logs contain no PII.

## Returned Payment Webhook

- [ ] Valid event accepted.
- [ ] Invalid signature rejected.
- [ ] Replayed event rejected or ignored.
- [ ] Duplicate returned-payment fee not created.
- [ ] Logs contain no bank data, PII, or secrets.

## Field maps

- [ ] Zoho Books item IDs verified.
- [ ] Zoho Books custom-field API names verified.
- [ ] Zoho CRM field names verified.
- [ ] Zoho Contracts merge fields verified.
