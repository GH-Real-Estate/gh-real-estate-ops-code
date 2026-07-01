# Lease Automation Rules

This file summarizes only the lease rules needed by code. It is not the lease. The final signed lease/template in Zoho Contracts or WorkDrive remains the legal source document.

## Required before live automation

- [ ] Confirm this file matches the final signed lease/template.
- [ ] Confirm the late-fee code matches this file.
- [ ] Confirm Zoho Books item/template/custom field IDs are updated.
- [ ] Confirm returned-payment logic is separate from late-fee logic.

## Rent / late fee rules

| Rule | Current value | Source / verification status |
|---|---|---|
| Rent due date | TODO | Verify against final lease |
| Rent due time zone | America/Chicago / Central Time | Verify code behavior |
| Grace/late threshold #1 | TODO | Verify against final lease |
| Fee amount #1 | TODO | Verify against final lease |
| Grace/late threshold #2 | TODO | Verify against final lease |
| Fee amount #2 | TODO | Verify against final lease |
| Maximum late-fee cap | TODO | Verify against final lease and Kansas reasonableness risk |
| Interest start | TODO | Verify against final lease |
| Interest rate | TODO | Verify against final lease and applicable law |
| Returned-payment fee | TODO | Verify against final lease |
| Non-approved payment method admin fee | TODO | Verify against final lease |

## Automation constraints

- Fees must be idempotent.
- No duplicate late-fee or returned-payment fee invoices.
- Zoho Books remains the accounting source of truth.
- All production changes must be documented in `docs/runbooks/deployment-log.md`.
- Do not use this file as legal advice. Use it only as an automation checklist against the final lease.
