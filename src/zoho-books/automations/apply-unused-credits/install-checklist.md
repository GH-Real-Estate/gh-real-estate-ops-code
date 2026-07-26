# Apply Unused Credits Install Checklist

## Pre-Install

- [ ] Final Deluge code committed to `src/zoho-books/automations/apply-unused-credits/ApplyUnusedCredits.deluge`.
- [ ] Code reviewed for null/empty-credit behavior.
- [ ] Code reviewed for Zoho API response-code handling.
- [ ] Code reviewed for pre-apply balance recheck behavior.
- [ ] Code reviewed for branch-matching behavior.
- [ ] Code reviewed to exclude every retainer payment, including an unexpectedly returned retainer.
- [ ] Code reviewed for no PII/secrets logging.
- [ ] Zoho Books connection name documented as `zbooks` or the code updated to match the actual connection link name.
- [ ] Confirm this automation should run for newly-created invoices only.
- [ ] Confirm it should not run during bulk historical invoice imports.
- [ ] Confirm whether `requireRentInvoiceFlag` should stay enabled.
- [ ] Confirm whether `allowEmptyBranchMatch` should stay disabled or be enabled for a verified single-branch setup.

## Zoho Books Setup

- [ ] Create or verify a Zoho Books connection with link name `zbooks`.
- [ ] Confirm the connection can read invoices.
- [ ] Confirm the connection can read contact unused credits / receivables.
- [ ] Confirm the connection can apply credits to invoices.
- [ ] Create or verify the invoice custom field API name `cf_is_rent_invoice` if `requireRentInvoiceFlag=true`.
- [ ] Create a Workflow Rule in Zoho Books.
- [ ] Set Module to `Invoice`.
- [ ] Set Workflow Type to `Event Based`.
- [ ] Set trigger to `Created`.
- [ ] Add filters only if the business wants to exclude specific invoice types.
- [ ] Add a Custom Function action using `ApplyUnusedCredits.deluge`.

## Test

- [ ] Create a controlled invoice that is not marked eligible; no credits applied.
- [ ] Create a controlled invoice for a customer with no unused credits; no credits applied.
- [ ] Create a controlled invoice for a customer with unused customer-payment credit; correct amount applied.
- [ ] Create a controlled invoice for a customer with a credit note; correct amount applied before customer-payment credits.
- [ ] Create a controlled invoice for a customer with only an unused retainer payment; no credit-application POST occurs and the retainer remains untouched.
- [ ] Create a controlled invoice with mixed credit-note, customer-payment, and retainer balances; only the first two sources apply.
- [ ] Confirm matching-branch credits apply.
- [ ] Confirm non-matching-branch credits do not apply.
- [ ] Confirm blank branch IDs stop the function when `allowEmptyBranchMatch=false`.
- [ ] Re-run manually against the same controlled invoice; no over-application occurs.
- [ ] Simulate or inspect a failed Zoho response; the function logs an error and does not continue.
- [ ] Confirm logs contain no PII, bank data, raw payloads, or secrets.

## Deployment

- [ ] Install code in Zoho Books.
- [ ] Record the live deployment in `docs/runbooks/deployment-log.md` with the merged commit.
- [ ] Run the smoke test checklist.
- [ ] Keep rollback copy/reference: disable the Workflow Rule or remove the Custom Function action.
