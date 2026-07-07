# Changelog

Record notable repository changes here. Production deployments belong in `docs/runbooks/deployment-log.md`.

## 2026-07-07

- Hardened Zillow Rentals lead intake for Zoho Catalyst Advanced I/O.
- Aligned the Zillow webhook with Zillow's URL-encoded lead delivery format.
- Added official Zillow field normalization coverage for `listingId`, `movingDate`, listing address fields, `leadType`, and applicant-profile fields.
- Updated Zillow CRM field mapping to Leads-only intake.
- Removed use of Zillow-intake fields that should not exist in this flow: `Desired_Rent`, `Desired_Deposit`, `Manual_Review_Required`, and `Manual_Review_Reason`.
- Updated runtime config docs, security model, install checklist, sample payload, and tests.

## 2026-07-01

- Reorganized the repo by source system/runtime under `src/`.
- Moved Late Fee Guard under `src/zoho-books/automations/late-fee-guard/`.
- Moved returned-payment webhook under `src/zoho-payments/webhooks/returned-payment-fee/`.
- Moved decision records to `docs/adr/`.
- Moved sanitized samples to source-system folders.
- Added system-level README files and updated repository guidance.
