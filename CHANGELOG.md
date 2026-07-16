# Changelog

Record notable repository changes here. Production deployments belong in `docs/runbooks/deployment-log.md`.

## 2026-07-15

- Added a governed Zoho Contracts field registry covering all 46 submitted system fields and 19 submitted custom fields.
- Recorded Zoho Contracts native/expected types, portable cross-application types, proposed CRM field types, sensitivity, constraints, aliases, and official-source evidence.
- Added a checked-in JSON Schema, dependency-free validator, generated human-readable catalog, and regression tests enforced by the repository safety workflow.
- Added fail-closed metadata gates for tenant-specific or ambiguous fields; unverified Contracts and CRM API names remain unset and cannot be used for synchronization.
- Designated `Storage Term Starts` as a deprecated alias of `Storage Term Begins` and flagged `Lease Agreement Effective Date` for review against the system `Agreement Date`.
- This is a sanitized design/governance update only; it does not create, alter, or deploy fields in the live Zoho tenant.

## 2026-07-14

- Hardened the public boundary with CodeQL, dependency review, workflow-policy enforcement, fail-closed binary/PDF controls, full CODEOWNERS coverage, security/contribution templates, and immutable runtime pins.
- Removed live-looking operational identifiers and property examples from public runtime/reference files, replacing account IDs with consistent public aliases and deployment values with fail-closed placeholders.
- Moved both Catalyst packages and CI from unsupported Node.js 18 to Node.js 24.
- Reduced GitHub Actions fan-out without weakening the unconditional repository safety scan or changing required check names.
- Moved `Authority Discovery` from daily execution to Sunday at `11:17 UTC`, while retaining manual dispatch.
- Added fail-open changed-path gating so the Zillow, returned-payment, and authority suites run fully whenever their governed scope changes or diff detection is uncertain.
- Disabled automatic `workflow_run` incident/recovery execution; `CI Failure Response` now supports manual simulation and validation only, with normal GitHub notifications as the default alert.
- Reduced authority-discovery, legal-monitor, and accounting-review artifact retention from 90 days to 14 days after verifying their publishers consume artifacts within the same workflow run.

## 2026-07-12

- Added the governed GH accounting authority library under `accounting/`.
- Added four dated accounting Project Source PDFs and searchable text covering 114 federal, GAAP-locator, Kansas, Overland Park, and Johnson County source-register records across 33 pages.
- Added a 54-topic FASB applicability registry covering baseline GAAP, transaction triggers, future structures, and explicit nonapplicability watchpoints.
- Added transaction-policy, evidence, licensing, and ChatGPT/Codex controls; no FASB Codification text or licensed-source substitute is stored.
- Added accounting-release validation and a monthly review calendar that opens `ACCOUNTING REVIEW REQUIRED` issues without changing policy.
- Added the GH Real Estate legal authority library under `legal/`.
- Added eight verified project-source PDF bundles covering 447 canonical Kansas, federal, HUD, and Overland Park sources across 1,718 pages.
- Added 463 search-sized authority Markdown files for GitHub connector retrieval, plus full bundle text, hashes, release manifests, and source ledgers.
- Added legal-release validation and a weekly official-source change monitor that opens a `LEGAL REVIEW REQUIRED` issue without automatically changing approved law.
- Documented corpus limitations, HUD retrieval exceptions, authority-status rules, and the requirement for live-source/counsel verification before high-risk action.

## 2026-07-08

- Updated Zillow lead intake runtime docs to separate Catalyst Development dry-run settings from Production live settings.
- Set the Catalyst root entrypoint to default the verified GH Real Estate CRM Units module API name to `Units` before loading the intake implementation.
- Updated environment variable documentation to use `ZOHO_CRM_UNITS_MODULE=Units` and `UNIT_PROPERTY_LOOKUP_FIELD=Property`.
- Added health-check runbook guidance that explicitly says to replace angle-bracket placeholders with real Catalyst endpoint and token values before running PowerShell tests.
- Normalized the Catalyst `/server/Zillow-Lead-Intake/...` invocation URL prefix before routing requests, so `/server/Zillow-Lead-Intake/health` and `/server/Zillow-Lead-Intake/zillow/leads` reach the intended internal routes.
- Updated PowerShell guidance to use direct variable assignment instead of `Read-Host` when pasting multi-line test blocks.
- Added complete Development and Production Catalyst variable blocks, including the temporary protected health-check variables.
- Added a desktop-first deployment policy that distinguishes GitHub/local code updates, Catalyst ZIP uploads, Catalyst variable restarts, and optional Catalyst CLI deployment.
- Clarified that Catalyst CLI/code uploads are development-first and that Production still requires a successful Catalyst production migration/deploy step.
- Added support and runbook instructions for a `POST /health` probe because some Catalyst function invocation URLs reject `GET` before the Advanced I/O handler runs.
- Added root-entrypoint startup diagnostics so module-load failures return JSON instead of an empty Catalyst 500 when the latest code is deployed.
- Recorded that Catalyst migration succeeded after reconstructing the uploaded bundle as real `docs/`, `src/`, `samples/`, and `test/` folders in the web editor instead of flat path-name files.
- Expanded live upsert troubleshooting to distinguish Zoho Accounts refresh-token failures, CRM Units search failures, and CRM Leads upsert failures after logs showed `zoho_request_failed`.
- Allowed PowerShell variable references such as `$refreshToken` and `$clientSecret` in the repository safety scan so diagnostic docs do not fail CI as false-positive literal secret assignments.
- Disabled Zoho cadence-skip payloads for Zillow intake by setting `SKIP_CADENCES_ON_INSERT=false` and `SKIP_CADENCES_ON_UPDATE=false` in docs and forcing both values off in the root Catalyst entrypoint.
- Replaced the temporary omission of `Zillow_Received_At` and `Last_Zillow_Sync_At` with a root Date formatting patch that converts JavaScript millisecond UTC timestamps to Zoho-friendly offset timestamps before loading the implementation.
- Documented the timestamp formatting behavior in the Zillow intake README so the audit-field handling is visible outside the root Catalyst entrypoint.

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
