# Changelog

Record notable repository changes here. Production deployments belong in `docs/runbooks/deployment-log.md`.

## 2026-07-16

- Added a Draft-only, attorney-review-required Zoho Contracts implementation package for the July 14, 2026 Lead-First Residential Lease Agreement.
- Added 59 governed clause records, a 161-unit source-to-clause crosswalk, sanitized document-field mappings, native template-component guidance, attachment requirements, visual QA controls, and one-, two-, and three-tenant Ending Text and Addendum B variants.
- Added three document-specific Zoho Sign recipient manifests that keep GH Real Estate, LLC as the final actual recipient and final signer for each supported tenant count.
- Added four package schemas, a dependency-free Residential Lease implementation validator, regression tests, and a required repository-check step.
- Kept all 29 production gates open, including rent and deposit source ownership, statutory notice information, legal review, live metadata verification, lead and HOA applicability, parking, storage, lease-end time, initial amounts, pets, appliances, required contacts, signer authority, municipality applicability, required initials, signer-fragment selection, visual QA, and signature smoke testing.
- This repository change does not publish, send, execute, or alter a live lease. Any live Zoho copy must remain Draft, unpublished, blocked from execution, and unsent until every gate is closed.
- Added a governed Zoho CRM module-and-field catalog covering 14 known GH Real Estate modules, 736 known fields or candidates, and 120 choice fields.
- Required field specifications to use `Field Label — Field Type`, separate actual API names from proposed names, include creation help text no longer than 255 characters, and assign a six-digit hex color to every choice value.
- Added a working Zoho CRM field-type catalog, a metadata-only Modules/Fields export helper, a dependency-free catalog validator, and a path-scoped GitHub Actions check.
- Reconciled current Zillow Lead and Unit API names against reviewed runtime code and runbooks, while retaining conflicting workbook proposals only as superseded aliases.
- This is a sanitized repository-governance update only. It does not create, modify, or verify fields in the live Zoho CRM tenant; unverified API names remain unset or explicitly proposed.

## 2026-07-15

- Added a governed 16-item Zoho Contracts Clause Type master list, clause-definition schema/template, generated authoring reference, and CI validation for every checked-in `.clause.json` record.
- Added a Contracts-scoped typography profile for Inter, the Title/Heading 1-5/Normal hierarchy, US Letter layout, 0.75-inch margins, 1.15 line spacing, and non-justified text.
- Added a separate Zoho Sign field/tag registry covering all current document fields, canonical simple tags, user-confirmed compatibility aliases, and fail-closed advanced/unsupported syntax.
- Added a controlled Contracts-to-Sign smoke-test and live-template runbook, including Inter installation, preview-versus-completed Sign Date checks, republish controls, and forward-repair rollback because a republished prior version cannot be natively restored.
- Added a canonical Zoho Sign recipient-manifest policy that treats R1-R25 as contiguous indexes for actual envelope recipients rather than permanent business-role IDs or signing-order positions.
- Required GH Real Estate, LLC to be the final actual recipient and final signer in every document GH signs: R2 with one tenant, R3 with two tenants, R4 with three tenants, and the next contiguous role when additional governed signers precede GH.
- Prohibited placeholder recipients, recipient-number gaps, and any signer routed after GH; added a dependency-free recipient-policy validator, regression tests, and a required repository-check step.
- This update governs future drafting and CI only; it does not change, republish, or restyle live or existing contracts.
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
