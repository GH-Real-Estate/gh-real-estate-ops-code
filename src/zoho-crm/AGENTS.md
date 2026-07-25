# Zoho CRM Contributor Instructions

These rules apply to every file under `src/zoho-crm/` and to ChatGPT/Codex work that designs or implements GH Real Estate CRM modules, fields, layouts, workflows, Deluge, REST payloads, or integrations.

## Required references

Before creating, revising, mapping, or automating modules or fields, read:

- `standards/crm-module-field-authoring-standard.md`
- `standards/crm-field-type-catalog.md`
- `field-maps/crm-module-field-catalog.md`
- `field-maps/crm-module-fields/*.csv`
- the relevant integration field map or runbook

## Module rules

- Always separate the module display label from the module API name.
- State the module as `Display Label — Module Type`.
- State the Zoho base module when a standard module is renamed.
- Use `TBD_FROM_ZOHO_METADATA` for an unverified custom module API name.
- Never infer a custom module API name from its label.

## Field rules

When field creation or material field revision is in scope:

- Always state the field as `Field Label — Field Type`.
- Provide the actual API name and verification status.
- Keep a proposed API name separate from the actual `api_name`.
- Use `TBD_FROM_ZOHO_METADATA` when no verified API name exists.
- Provide help text no longer than 255 characters.
- Provide required, unique, default, section, lookup target, and source-of-truth details when relevant.
- Do not claim a field exists merely because it appears in a workbook or record export.
- Confirm field type before creation; do not create a temporary type with the intent to change it later.

The help-text rule applies to field creation/revision work, not unrelated architecture discussions that only mention existing fields.

## Picklist and choice rules

For every picklist, Stage, multi-select, radio-style choice, or similar choice field, provide:

- exact ordered values;
- local, global, or standard-module scope;
- default;
- history-tracking recommendation;
- color-coding recommendation;
- a six-digit `#RRGGBB` color for every value.

Use the governed GH semantic palette in the authoring standard and field catalog.

## API and live-verification rules

- Use module, field, and related-list API names in code and integration settings.
- Use labels only for user-facing instructions.
- Verify actual values with the Modules and Fields Metadata APIs before production use.
- Runtime defaults are not equivalent to a live metadata export.
- Do not enable the optional `Zillow Intake Events` module merely to create a duplicate source of truth.
- Do not use `proposed_unverified`, `not_proposed_unverified`, `blocked_protected_module`, `historical_target_only_non_deployable`, superseded, or prohibited entries in automation.
- Do not create duplicate fields to work around a label/API-name mismatch.

## Data safety

- Never commit tenant PII, applications, screening reports, signed leases, record exports containing IDs, OAuth tokens, client secrets, refresh tokens, passwords, or production payloads.
- Metadata exports must omit CRM records and authentication values.
- Keep raw Zillow private payload values out of CRM under the current design.

## Validation

Run:

```bash
python src/zoho-crm/tools/validate-crm-field-catalog.py
python src/zoho-crm/tools/validate-protected-module-baselines.py
python -m py_compile \
  src/zoho-crm/tools/validate-crm-field-catalog.py \
  src/zoho-crm/tools/validate-protected-module-baselines.py \
  src/zoho-crm/tools/export-crm-metadata.py
```

A repository catalog change is not complete until the validator passes.

The live API names `Leads`, `Equipment` (display label Property Assets),
`Pets`, and `Tenant_Vehicles` (display label Vehicles) are protected by the
baselines under `field-maps/protected-modules/`. Treat their mutation policy
as deny. The historical `equipment.csv` target design does not authorize
writes to live API `Equipment`.
