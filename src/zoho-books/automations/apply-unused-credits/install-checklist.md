# Apply Unused Credits Install Checklist

## Pre-Install

- [ ] Final Deluge code committed to `src/zoho-books/automations/apply-unused-credits/ApplyUnusedCredits.deluge`.
- [ ] Code reviewed for null/empty-credit behavior.
- [ ] Code reviewed for branch-matching behavior.
- [ ] Code reviewed for no PII/secrets logging.
- [ ] Zoho Books connection name documented as `zbooks` or the code updated to match the actual connection link name.
- [ ] Confirm this automation should run for newly-created invoices only.
- [ ] Confirm it should not run during bulk historical invoice imports.

## Zoho Books Setup

- [ ] Create or verify a Zoho Books connection with link name `zbooks`.
- [ ] Confirm the connection can read invoices.
- [ ] Confirm the connection can read contact unused credits / receivables.
- [ ] Confirm the connection can apply credits to invoices.
- [ ] Create a Workflow Rule in Zoho Books.
- [ ] Set Module to `Invoice`.
- [ ] Set Workflow Type to `Event Based`.
- [ ] Set trigger to `Created`.
- [ ] Add filters only if the business wants to exclude specific invoice types.
- [ ] Add a Custom Function action using `ApplyUnusedCredits.deluge`.

## Test

- [ ] Create a controlled invoice for a customer with no unused credits; no credits applied.
- [ ] Create a controlled invoice for a customer with unused customer-payment credit; correct amount applied.
- [ ] Create a controlled invoice for a customer with a credit note; correct amount applied.
- [ ] Create a controlled invoice for a customer with unused retainer payment; correct amount applied.
- [ ] Confirm matching-branch credits apply.
- [ ] Confirm non-matching-branch credits do not apply.
- [ ] Re-run manually against the same controlled invoice; no over-application occurs.
- [ ] Confirm logs contain no PII, bank data, raw payloads, or secrets.

## Deployment

- [ ] Install code in Zoho Books.
- [ ] Record the live deployment in `docs/runbooks/deployment-log.md` with the merged commit.
- [ ] Run the smoke test checklist.
- [ ] Keep rollback copy/reference: disable the Workflow Rule or remove the Custom Function action.
