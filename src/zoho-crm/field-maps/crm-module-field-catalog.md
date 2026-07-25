# GH Real Estate Zoho CRM Module and Field Catalog

- **Catalog ID:** GH-ZOHO-CRM-FIELDS-001
- **Version:** 1.1.0
- **Effective date:** July 24, 2026
- **Machine-readable sources:** one or more governed CSV files per module under [`crm-module-fields/`](crm-module-fields/)

## Purpose

This catalog records every GH Real Estate CRM business, integration, planned, and legacy-candidate field currently known from the reviewed repository and the supplied CRM workbooks.

It is a governed planning and verification registry. It is **not** proof that every proposed field or custom module exists in the live Zoho CRM organization.

## Non-negotiable rules

1. Refer to every field as **Field Label — Field Type**.
2. For field creation or material field revision, provide:
   - field label;
   - Zoho UI field type;
   - actual API name and verification status;
   - help text of no more than 255 characters;
   - required/unique/default behavior when relevant;
   - picklist values, order, scope, default, and six-digit hex colors when relevant. `UNCOLORED` is allowed only for `verified_live_mcp` rows with scope `module_local_live_uncolored` or `standard_module_live_uncolored` when live metadata returns null colors; proposed choice fields still require six-digit hex colors.
3. Never infer an API name from a label. Use `TBD_FROM_ZOHO_METADATA` until the live metadata API or a reviewed runtime integration proves it.
4. A proposed API name is not an actual API name.
5. Use actual API names, never labels, in Deluge, REST payloads, functions, webhooks, merge maps, and integration settings.
6. Do not build every candidate field automatically. Use the `disposition`, `phase`, and verification status in the per-module CSV registry.
7. Keep tenant PII, applications, screening reports, signed documents, and production secrets out of this repository.

## Module inventory

| Display label | Zoho base module | Module type | API name | API-name status | Known fields | Verified field APIs | Still unverified |
|---|---|---|---|---|---:|---:|---:|
| Leads | Leads | standard | `Leads` | verified_standard_zoho_and_repo_runtime | 60 | 34 | 26 |
| Zillow Intake Events | Custom | custom_optional_integration_log | `Zillow_Intake_Events` | repo_runtime_default_needs_live_metadata | 10 | 0 | 10 |
| Properties | Accounts | standard_renamed | `Accounts` | verified_standard_zoho | 76 | 6 | 70 |
| Contacts | Contacts | standard | `Contacts` | verified_standard_zoho | 52 | 4 | 48 |
| Rental Applications | Deals | standard_renamed | `Deals` | verified_standard_zoho | 80 | 20 | 60 |
| Units | Custom | custom | `Units` | verified_repo_live_integration | 54 | 7 | 47 |
| Leases | Custom | custom | `Leases` | verified_live_mcp | 249 | 42 | 207 |
| Maintenance Requests | Cases | standard_renamed | `Cases` | verified_standard_zoho | 46 | 0 | 46 |
| Inspections | Custom | custom | `TBD_FROM_ZOHO_METADATA` | tbd_from_live_module_metadata | 36 | 0 | 36 |
| Notices | Custom | custom | `TBD_FROM_ZOHO_METADATA` | tbd_from_live_module_metadata | 21 | 0 | 21 |
| Vendors | Vendors | standard | `Vendors` | verified_standard_zoho | 24 | 0 | 24 |
| Tasks | Tasks | standard | `Tasks` | verified_standard_zoho | 10 | 0 | 10 |
| Equipment | Custom | custom | `TBD_FROM_ZOHO_METADATA` | tbd_from_live_module_metadata | 13 | 0 | 13 |
| Lease Documents / Addenda | Custom | custom_candidate | `TBD_FROM_ZOHO_METADATA` | tbd_from_live_module_metadata | 16 | 0 | 16 |
| **Total** | -- | -- | -- | -- | **747** | **113** | **634** |

## Verification status

- `verified_standard_zoho`: a standard module API name confirmed by official Zoho metadata documentation.
- `verified_repo_runtime`: a field API name used by the reviewed Zillow integration and documented in the repository.
- `verified_repo_live_integration`: a module or field API name documented as verified by the integration runbook.
- `verified_live_mcp`: a module or field API name returned by the approved production metadata connector and confirmed by post-write readback.
- `repo_runtime_default_needs_live_metadata`: code contains the value, but no live Fields Metadata export has been checked in.
- `proposed_unverified`: workbook suggestion only.
- `not_proposed_unverified`: known label/type without a safe API-name proposal.
- `tbd_from_live_module_metadata`: custom module API name must be read from the live Modules Metadata response.
- `superseded_by_verified_repo_field`: an older proposal conflicts with a governed field; do not create a duplicate.
- `prohibited_current_design`: intentionally excluded by the current data-minimization design.

## Current verified integration surface

### Leads — Standard module — API name `Leads`

The reviewed Zillow integration currently governs 34 Lead field API names. Examples include:

| Field Label — Field Type | Verified API name | Status |
|---|---|---|
| Mobile — Phone / Standard | `Mobile` | Governed current |
| Phone — Phone / Standard | `Phone` | Governed current |
| Requested Property — Lookup | `Requested_Property` | Governed current |
| Requested Unit — Lookup | `Requested_Unit` | Governed current |
| Requested Move-In Date — Date | `Requested_Move_In_Date` | Governed current |
| Zillow Property Address Raw — Single Line | `Zillow_Property_Address_Raw` | Governed current |
| Zillow Intake Status — Pick List | `Zillow_Intake_Status` | Governed current |
| Zillow Raw Payload Stored — Checkbox | `Zillow_Raw_Payload_Stored` | Governed current |

The catalog also retains older workbook aliases, but marks conflicting proposals as `superseded_alias` so ChatGPT or Codex does not create duplicate Lead fields.

### Units — Custom module — API name `Units`

The Units module API name and core routing fields are documented as verified:

| Field Label — Field Type | Verified API name | Status |
|---|---|---|
| Unit Name — Single Line / Module Name | `Name` | Governed current |
| Property — Lookup | `Property` | Governed current |
| Unit Number — Number | `Unit_Number` | Governed current |
| Zillow Listing ID — Single Line | `Zillow_Listing_ID` | Governed current |
| Zillow Provider Model ID — Single Line | `Zillow_Provider_Model_ID` | Governed current |
| Zillow Listing Contact Prefix — Single Line | `Zillow_Listing_Contact_Prefix` | Governed current |
| Zillow Routing Unit Key — Single Line | `Zillow_Routing_Unit_Key` | Governed current |

`Occupancy_Status` and `Unit_ID` remain runtime defaults that still require a live Fields Metadata response.

### Rental Applications -- Standard Deals module renamed -- API name `Deals`

The July 24, 2026 production reconciliation created and read back 15 bounded application fields. The governed CSV records the exact API name, type, tooltip, lookup target, choices/colors, and disposition for each.

The standard `Stage` field remains the application-stage field. No custom `Application Stage` field was created, and the requested target Stage list is not claimed to exist live. Final readback found 18 uncolored display options, default null, history enabled, and stale/misaligned underlying actual values; the governed CSV row preserves every exact pair. Stage values were not changed because the current tool could not safely reconcile those pairs with pipeline/probability semantics. Standard `Amount` was not repurposed because an active Big Deal Rule depends on Amount and Probability.

CSV `help_text` preserves the exact live readback. The submitted creation payload used normalized/paraphrased wording for some values instead of the user-supplied prose, and the tool stored/read that payload exactly. The rows therefore do not prove verbatim prompt-text equality. The current update schema cannot change tooltips; a later supported update must apply the supplied exact text and read it back.

### Leases -- Custom module -- API name `Leases`

The custom module API `Leases` and its post-write metadata were verified through the approved production metadata connector on July 24, 2026. The bounded build created 33 fields, reused seven compatible fields, created eight ordered sections, and read back all 40 reconciled placements. The inventory counts 42 verified Lease APIs because the live APIs `Monthly_Rent` and `Prorated_Rent` were also verified even though their target semantics remain blocked and they are not governed-current mappings.

Important live variances and unresolved items:

- live `Tenant` (`Tenant`) is the primary-tenant relationship; no duplicate field labeled Primary Tenant was created;
- live `Lease_Start_Date`, `Lease_End_Date`, `Move_In_Date`, and `Security_Deposit` were reused for the approved Lease snapshots;
- Lease Status history tracking is enabled, target choices/colors are present, and legacy values remain; the live label is `Ready For Contract`, but order interleaves target/legacy values with new `Draft` last, default is null, and the field remains optional;
- required/default/readiness controls remain unsupported by the current configuration tool;
- `Monthly_Rent` and `Prorated_Rent` remain semantically ambiguous, so no duplicate Base/Total/Prorated Base Rent fields were created;
- Lease Number remains blocked until an auto-number prefix/format is approved; and
- First Full Month Base Rent Amount remains a confirmed field/equation gap.

See the sanitized [production reconciliation](../../../docs/runbooks/zoho-crm-lease-system-reconciliation.md) for the full applied/blocked manifest and rollback.

## Picklist color standard

These are GH Real Estate's recommended semantic colors. They are not claimed to be Zoho's default colors.

| Color | Hex |
|---|---|
| Blue | `#2563EB` |
| Amber | `#D97706` |
| Purple | `#7C3AED` |
| Green | `#16A34A` |
| Red | `#DC2626` |
| Gray | `#6B7280` |
| Orange | `#EA580C` |
| Teal | `#0F766E` |
| Cyan | `#0891B2` |
| Indigo | `#4F46E5` |
| Pink | `#DB2777` |
| Lime | `#65A30D` |
| Brown | `#92400E` |

Use semantic colors first:

- blue: new, informational, or unworked;
- amber: waiting, pending, or action required;
- purple: showing, contract, or signature workflow;
- green: approved, active, verified, or complete;
- orange: legal review, nonstandard handling, or heightened caution;
- red: denied, failed, terminated, or urgent;
- gray: inactive, archived, unknown, duplicate, or not applicable.

The per-module CSV registry gives every known picklist value a six-digit hex recommendation and identifies whether the assignment came from the supplied color matrix, a semantic fallback, or a categorical rotation.

## Field-type status

The companion [`crm-field-type-catalog.md`](../standards/crm-field-type-catalog.md) is a working type vocabulary. Zoho does not permit changing a custom field's type after creation, so field type must be confirmed before the field is built.

The registry separates:

- `field_type`: the proposed or governed Zoho UI type;
- `expected_api_data_type`: the expected metadata type when the mapping is clear;
- actual live metadata: not claimed until exported from Zoho CRM.

## Live verification procedure

Use:

```text
GET /crm/v8/settings/modules
GET /crm/v8/settings/fields?module={module_API_name}&type=all
```

The repository helper [`export-crm-metadata.py`](../tools/export-crm-metadata.py) exports sanitized module and field metadata without reading CRM records. Compare that export to this catalog before creating automations or treating a proposed API name as real.

## Known limitations and next gate

- Live metadata was read only through the approved CRM audit/configuration connectors; no CRM records or PII were retrieved.
- Production readback verified the bounded Rental Application/Lease fields documented in their governed CSV rows. It did not certify every historical workbook candidate.
- `Zillow Intake Events` remains an optional, disabled-by-default runtime candidate; it is not approved as a second source of truth and its live existence is unconfirmed.
- Current Zillow Lead and Unit routing API names remain reconciled against reviewed repository code/runbooks; only the targeted related-source fields used by the Lease handoff received current live readback.
- Unverified custom-module and field candidates remain explicitly unset or proposed and cannot be used in automation.
- The June 29 Properties workbook is a record export. Its headers are label evidence only; it cannot prove API names or field types.
- Zoho Contracts contract-type API names, extension mappings, button tokens, counterparty settings, and signer routing remain manual/unverified.
- The Approved Application-to-Lease automation is unsupported by the current tool surface and must be implemented later as a durable, idempotent workflow.

## Sources

- Official Zoho CRM API v8 Modules Metadata: https://www.zoho.com/crm/developer/docs/api/v8/modules-api.html
- Official Zoho CRM API v8 Fields Metadata: https://www.zoho.com/crm/developer/docs/api/v8/field-meta.html
- Official Zoho CRM custom field types: https://help.zoho.com/portal/en/kb/crm/customize-crm-account/customizing-fields/articles/types-of-fields
- Repository Zillow field map and Lead/Unit integration runbooks
- `GH_Zoho_CRM_Field_Matrix_Contracts_Zillow_Portal_2026-07-08.xlsx`
- `GH_Real_Estate_Zoho_CRM_Setup_Spec.xlsx`
- `Properties_2026_06_29.xlsx`
