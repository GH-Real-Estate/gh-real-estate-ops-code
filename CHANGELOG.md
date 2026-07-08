# Changelog

Record notable repository changes here. Production deployments belong in `docs/runbooks/deployment-log.md`.

## 2026-07-08

- Updated Zillow lead intake runtime docs to separate Catalyst Development dry-run settings from Production live settings.
- Set the Catalyst root entrypoint to default the verified GH Real Estate CRM Units module API name to `Units` before loading the intake implementation.
- Updated environment variable documentation to use `ZOHO_CRM_UNITS_MODULE=Units` and `UNIT_PROPERTY_LOOKUP_FIELD=Property`.
- Added health-check runbook guidance that explicitly says to replace angle-bracket placeholders with real Catalyst endpoint and token values before running PowerShell tests.
- Normalized the Catalyst `/server/Zillow-Lead-Intake/...` invocation URL prefix before routing requests, so `/server/Zillow-Lead-Intake/health` and `/server/Zillow-Lead-Intake/zillow/leads` reach the intended internal routes.
- Updated PowerShell guidance to use direct variable assignment instead of `Read-Host` when pasting multi-line test blocks.
- Added complete Development and Production Catalyst variable blocks, including the temporary protected health-check variables.
- Added a desktop-first deployment policy that distinguishes GitHub/local code updates, Catalyst ZIP uploads, Catalyst variable restarts, and optional Catalyst CLI deployment.

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
