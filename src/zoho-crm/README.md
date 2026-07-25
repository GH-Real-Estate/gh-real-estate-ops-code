# Zoho CRM

Use this area for CRM governance, functions, field maps, validation tools, and integration notes.

Zoho CRM owns prospect, applicant, tenant relationship, property/unit, and leasing pipeline records. Do not store real applicant or tenant records in GitHub.

## Contents

```text
AGENTS.md
field-maps/
  crm-module-field-catalog.md
  crm-module-fields/
    leads.csv
    properties.csv
    ... one or more CSV segments per known module
  zillow-to-crm-to-contracts.md
integrations/
  zillow-lead-intake/
standards/
  crm-module-field-authoring-standard.md
  crm-field-type-catalog.md
tools/
  export-crm-metadata.py
  validate-crm-field-catalog.py
```

## Governed CRM references

Before ChatGPT, Codex, or an implementer creates, revises, maps, or automates a CRM module or field, read:

1. [`AGENTS.md`](AGENTS.md)
2. [`standards/crm-module-field-authoring-standard.md`](standards/crm-module-field-authoring-standard.md)
3. [`standards/crm-field-type-catalog.md`](standards/crm-field-type-catalog.md)
4. [`field-maps/crm-module-field-catalog.md`](field-maps/crm-module-field-catalog.md) and the per-module CSV files under [`field-maps/crm-module-fields/`](field-maps/crm-module-fields/)
5. [`../../docs/runbooks/zoho-crm-lease-system-reconciliation.md`](../../docs/runbooks/zoho-crm-lease-system-reconciliation.md) for the July 24, 2026 production Lease-system configuration boundary and readback

The per-module CSV catalog separates actual verified API names from workbook proposals, runtime defaults, legacy candidates, superseded aliases, and fields prohibited by the current design.

## Core rules

- Use fake examples only.
- Do not store actual applications, IDs, pay stubs, employment verification records, landlord references, signed documents, OAuth values, or tenant records here.
- Keep live records in Zoho CRM, Zoho Forms, Zoho Creator, Zoho Contracts, Zoho Sign, or WorkDrive as appropriate.
- Always separate display labels from API names.
- State fields as `Field Label — Field Type`.
- When field creation or material revision is in scope, provide help text no longer than 255 characters.
- For every choice field, provide exact ordered values, scope, default, and a six-digit hex color for each value.
- Never use a proposed API name in code until live metadata or a reviewed operating integration verifies it.
- Confirm field type before creation; Zoho does not permit changing a custom field's type later.
- Run `python src/zoho-crm/tools/validate-crm-field-catalog.py` after catalog changes.

## Current module strategy

- Properties = Accounts renamed; API name `Accounts`.
- Rental Applications = Deals renamed; API name `Deals`.
- Maintenance Requests = Cases renamed; API name `Cases`.
- Units = custom module; verified API name `Units`.
- Leases = custom module; live API name `Leases`, verified through production metadata readback on July 24, 2026.
- Leads, Contacts, Vendors, and Tasks retain their standard API names.
- `Zillow Intake Events` is an optional disabled-by-default runtime candidate; its live module/API existence must be verified before use.
- Inspections, Notices, Equipment, and Lease Documents / Addenda require live metadata before a custom module API name is claimed.

## Lease-system deployment boundary

The production CRM configuration and the manual Zoho Contracts remainder are intentionally separate:

- [`zoho-crm-lease-system-reconciliation.md`](../../docs/runbooks/zoho-crm-lease-system-reconciliation.md) records the sanitized production CRM fields, actual read-back API names, layout/choice results, blocked items, and rollback.
- [`crm-leases-extension-manual-deployment.md`](../zoho-contracts/runbooks/crm-leases-extension-manual-deployment.md) covers the unsupported manual Contracts extension, button, related-list, counterparty, mapping, and signer-routing steps.
- The approved Application-to-Lease automation remains unsupported by the current MCP surface. Do not substitute one-time record creation for a durable, idempotent automation.
- The Residential Lease Agreement remains Draft only, unpublished, execution-blocked, attorney-review-required, and unsent with all 29 production gates open.
- A repository update is not proof that a live Zoho Contracts configuration was performed.

## Zillow intake rules

- Zillow lead intake writes raw Zillow inquiries to CRM `Leads` only.
- It must not create `Contacts`, rental application pipeline records, leases, Books records, tenant portal access, or WorkDrive folders.
- Convert or promote a Lead only after qualification, application review, owner approval, or the approved business workflow for the tenant stage.
- Zillow `phone` maps to `Mobile`; `Phone` is secondary or alternate.
- Do not create `Desired_Rent`, `Desired_Deposit`, `Manual_Review_Required`, or `Manual_Review_Reason`.
- Do not store raw private Zillow payload values under the current design.

## Live metadata verification

Use the metadata-only helper:

```bash
export ZOHO_CRM_ACCESS_TOKEN='set-in-your-shell-or-secure-runtime'
python src/zoho-crm/tools/export-crm-metadata.py \
  --module Leads \
  --module Accounts \
  --module Contacts \
  --module Deals \
  --module Units \
  --module Leases \
  --module Cases
```

The helper reads only Modules and Fields Metadata. It omits records, authentication values, and metadata IDs from the output.

Required endpoints:

```text
GET /crm/v8/settings/modules
GET /crm/v8/settings/fields?module={{module_API_name}}&type=all
```

A repository catalog is not proof of live Zoho deployment. Update the catalog only after reconciling the metadata export.

## Zoho Contracts field crosswalk

Use `../zoho-contracts/field-maps/contract-field-registry.json` as the governed, machine-readable source for Contracts-to-CRM field planning. Its `proposed_crm` entries document portable CRM field types and proposed API names; they are not proof that those API names exist in the live CRM tenant.

Before creating or syncing Contracts-to-CRM fields:

1. Verify the Zoho Contracts field through the contract type `allfields` metadata endpoint.
2. Verify the target CRM module and field through CRM metadata.
3. Record confirmed API names in a reviewed registry update.
4. Keep fields marked `review_required`, `tenant_api_required`, `deprecated_alias`, proposed, superseded, or prohibited out of automated synchronization.

Do not copy contract-party personal data into GitHub while performing that verification.
