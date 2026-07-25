# GH Real Estate Zoho CRM Module and Field Authoring Standard

**Standard ID:** GH-ZOHO-CRM-001  
**Version:** 1.1

**Effective date:** July 24, 2026

**Scope:** ChatGPT, Codex, repository contributors, and implementation agents discussing, designing, creating, revising, mapping, or automating GH Real Estate Zoho CRM modules and fields  
**Governed field registry:** [`../field-maps/crm-module-field-catalog.md`](../field-maps/crm-module-field-catalog.md) and [`../field-maps/crm-module-fields/`](../field-maps/crm-module-fields/)

## 1. Purpose

This standard prevents three recurring failures:

1. confusing a display label with an API name;
2. creating the wrong field type or a duplicate field;
3. giving incomplete build instructions that omit help text, picklist choices, or color coding.

The standard applies to field creation and material field revision. It does not require help text in unrelated conversations that merely mention an existing field.

## 2. Source-of-truth hierarchy

Use this order:

1. **Live Zoho CRM Modules and Fields Metadata** for actual module API names, field API names, metadata data types, tooltips, lengths, and picklist values/colors.
2. **Reviewed repository runtime code and runbooks** for API names already used by an operating integration.
3. **The governed CRM field catalog** for approved, proposed, superseded, and prohibited field decisions.
4. **Uploaded workbooks and screenshots** as design evidence only unless they are actual metadata exports.
5. **Reasoned proposals** only when clearly labeled unverified.

A record export proves that a field label appeared in exported records. It does not prove the API name or field type.

Use `verified_live_mcp` only when the approved production metadata connector returned the module or field and post-write readback confirmed the governed result. Every field row with that status must cite `LIVE_CRM_MCP_2026-07-24`; a proposed API name or repository convention is not enough.

For the July 24 created-field reconciliation, CSV `help_text` preserves the authoritative live readback. The creation tool normalized some supplied wording, so live-readback text must not be described as a verbatim copy of the original request. Any wording remediation requires a supported tooltip update followed by another readback.

## 3. Mandatory module format

Whenever a module is being created, renamed, mapped, or automated, state:

| Required item | Rule |
|---|---|
| Display label | Exact tenant-facing or administrator-facing module label |
| Zoho base module | Standard source module when renamed, such as Accounts or Deals |
| Module type | Standard, standard renamed, custom, subform, or linking module |
| API name | Actual API name, or `TBD_FROM_ZOHO_METADATA` |
| API-name status | Verified, runtime-only, proposed, or unverified |
| Purpose | One concise statement of what records the module owns |
| Primary relationships | Parent/child or lookup relationships using labels and verified API names separately |

Required prose format:

```text
Properties — Standard module renamed from Accounts — API name `Accounts`
Units — Custom module — API name `Units`
Leases — Custom module — API name `Leases` — `verified_live_mcp`
```

Do not assume a custom module's display label is its API name.

## 4. Mandatory field format

Whenever a field is being created or materially revised, identify it as:

```text
Field Label — Field Type
```

Every field specification must include:

| Required item | Rule |
|---|---|
| Field Label | Exact display label in Proper Case |
| Field Type | Exact Zoho UI field type |
| API Name | Actual verified API name, or `TBD_FROM_ZOHO_METADATA` |
| API-name status | Verified, proposed, runtime-only, superseded, prohibited, or unverified |
| Help Text | Clear user guidance, maximum 255 characters |
| Required? | Yes, No, conditional, or system-mandatory |
| Unique? | Yes/No when applicable |
| Default | Exact value or blank |
| Section/layout | Where it belongs when known |
| Purpose/source | Why the field exists and which system owns the value |
| Picklist definition | Required for every picklist, multi-select, stage, radio, or other choice field |

The help-text requirement applies when field creation or revision is in scope. Do not force help text into unrelated architecture answers.

For a live-reconciled catalog row, `required` records the actual live metadata state. Put an unenforced conditional business requirement in help text or notes; do not mark the row required merely because the process should require it. The July 24 production-created Rental Application and Lease fields read back as optional because the approved tool could not configure and verify conditional requiredness.

## 5. Help text standard

### 5.1 Limit

GH Real Estate's governed maximum is **255 characters**, including spaces and punctuation.

The public Zoho documentation confirms tooltip support but does not establish this GH-specific 255-character rule. Treat 255 as an internal fail-closed authoring limit until live product behavior or complete official documentation proves a different tenant limit.

### 5.2 Content

Good help text:

- tells the user what to enter or what the value means;
- identifies the source system when ambiguity is likely;
- explains special formatting, such as numeric-only unit numbers;
- avoids internal jargon unless the field is technical;
- does not restate the label without adding guidance;
- does not contain secrets, tenant PII, legal advice, or long policy language.

Examples:

```text
Unit Number — Number
Help Text: Store only the numeric unit value for sorting and Zillow routing.

Zillow Raw Payload Stored — Checkbox
Help Text: Indicate whether an approved secure system stores the raw payload; default is false.

Monthly Base Rent — Currency
Help Text: Enter the owner-approved monthly base rent used for the lease and Books setup.
```

## 6. API-name rules

1. Use the key `api_name` from Zoho metadata.
2. Never convert spaces to underscores and claim the result is real.
3. Keep `proposed_api_name` separate from `api_name`.
4. A proposed API name must never be used in Deluge, REST payloads, webhooks, merge maps, or environment variables until verified.
5. Renaming a label does not necessarily change the API name.
6. Standard module and field API names cannot be changed; custom API names have separate Zoho rules.
7. Use API names for modules, fields, and related lists in code.
8. Use display labels only in user-facing instructions and screenshots.

Allowed unresolved representation:

```json
{
  "field_label": "Lease Status",
  "field_type": "Pick List",
  "api_name": null,
  "api_name_status": "proposed_unverified",
  "proposed_api_name": "Lease_Status"
}
```

Disallowed:

```json
{
  "field_label": "Lease Status",
  "api_name": "Lease_Status",
  "status": "verified"
}
```

unless live metadata or a reviewed integration actually proves it.

## 7. Field-type rules

1. Confirm the field type before creation. Zoho does not permit changing a custom field's type after creation.
2. Distinguish the UI field type from the API metadata `data_type`.
3. Do not substitute Single Line for Number merely because the values look simple.
4. Use Number for `Unit Number`; keep the readable apartment label in the module Name field.
5. Store postal codes and identifiers as text when leading zeros or nonnumeric characters may matter.
6. Use Currency only for monetary amounts.
7. Use Date/Time only when the time is operationally meaningful.
8. Use Multi-Line only when users need more than a short value; choose plain small/large or rich text deliberately.
9. Treat Address, Formula, Auto-Number, Rollup Summary, Image Upload, File Upload, Subform, and multi-select lookup fields as types requiring explicit design details and live-edition verification.

Use the working type vocabulary in [`crm-field-type-catalog.md`](crm-field-type-catalog.md).

## 8. Picklist and choice-field rules

For every picklist, multi-select picklist, standard Stage, radio-style choice, or similar choice field, provide:

1. Field Label — Field Type.
2. Exact ordered values.
3. Local, global, or standard-module scope.
4. Exact default value or `None`.
5. Entered order or alphabetical order.
6. Whether history tracking is recommended.
7. Whether color coding is recommended.
8. A six-digit hex color for every value.
9. The reason for the color when the meaning is not obvious.

Do not invent a color when live metadata returns `colour_code: null`. A live-readback row may use `Label=UNCOLORED` with scope `module_local_live_uncolored` or `standard_module_live_uncolored`; this representation is allowed only with `verified_live_mcp`. Proposed choice fields still require a six-digit hex color for every value.

### 8.1 GH semantic palette

| Meaning | Color | Hex |
|---|---|---|
| New or informational | Blue | `#2563EB` |
| Waiting or pending | Amber | `#D97706` |
| Contract/signature workflow | Purple | `#7C3AED` |
| Approved, active, or complete | Green | `#16A34A` |
| Legal/nonstandard caution | Orange | `#EA580C` |
| Failed, denied, terminated, or urgent | Red | `#DC2626` |
| Inactive, archived, unknown, or N/A | Gray | `#6B7280` |
| Neutral categorical alternatives | Teal/Cyan/Indigo/Pink/Lime/Brown | See the governed catalog |

### 8.2 Example

```text
Lead Status — Pick List / Standard
API Name: `Lead_Status` — verified
Scope: Standard module picklist
Sort: Entered order
Default: New Zillow Inquiry
Values:
- New Zillow Inquiry — `#2563EB`
- Contact Attempted — `#D97706`
- Contacted — `#2563EB`
- Showing Scheduled — `#7C3AED`
- Converted To Applicant — `#16A34A`
- Not Qualified — `#DC2626`
- No Response — `#6B7280`
```

Color recommendations are GH Real Estate governance choices. They are not represented as Zoho defaults unless live metadata proves the colors are already applied.

## 9. Current GH module strategy

Preserve this model unless a documented architecture decision changes it:

| Display label | Zoho base/API direction | Role |
|---|---|---|
| Leads | Standard `Leads` | Raw Zillow and prospect intake |
| Zillow Intake Events | Optional custom runtime default `Zillow_Intake_Events`; live metadata unconfirmed | Disabled-by-default sanitized technical audit log only |
| Properties | Accounts renamed; API `Accounts` | Property-level records |
| Contacts | Standard `Contacts` | People and relationship records |
| Rental Applications | Deals renamed; API `Deals` | Application and approval pipeline |
| Units | Custom; verified API `Units` | Unit-level records |
| Leases | Custom; verified API `Leases` | Approved/executed lease record |
| Maintenance Requests | Cases renamed; API `Cases` | Maintenance workflow |
| Inspections | Custom; API TBD | Inspection/checklist records |
| Notices | Custom; API TBD | Notice tracking |
| Vendors | Standard `Vendors` | Service-provider records |
| Tasks | Standard `Tasks` | Follow-up work |
| Equipment | Custom; API TBD | Appliances and maintainable assets |
| Lease Documents / Addenda | Candidate custom module; API TBD | Optional document-status registry only |

## 10. Zillow-specific controls

1. Zillow intake writes business records to Leads only. The optional `Zillow Intake Events` technical log remains disabled by default and is not a second business source of truth.
2. Zillow `phone` maps to Mobile; Phone is secondary/alternate.
3. Use `Requested_Property` and `Requested_Unit`, not duplicate generic Property/Unit fields on Leads.
4. Use `Requested_Move_In_Date`, not a duplicate Desired Move-In Date field.
5. Use `Zillow_Lead_Type`, `Zillow_Intake_Status`, and `Zillow_Source_Payload_Hash` as governed by the repository.
6. Use `Zillow_Property_Address_Raw` exactly.
7. Do not create `Desired_Rent`, `Desired_Deposit`, `Manual_Review_Required`, or `Manual_Review_Reason` for Zillow intake.
8. Do not store raw private Zillow payload values in CRM under the current design. Store field keys, a one-way hash, and the false-by-default storage indicator instead.

## 11. Live metadata verification

Required endpoints:

```text
GET /crm/v8/settings/modules
GET /crm/v8/settings/fields?module={{module_API_name}}&type=all
```

Minimum metadata to retain:

### Module

- plural and singular labels;
- actual plural and singular labels;
- `api_name`;
- `generated_type`;
- `api_supported`;
- visibility/status.

### Field

- field label/display label;
- `api_name`;
- `data_type`;
- custom/system status;
- system mandatory status;
- length and decimal places;
- tooltip;
- textarea subtype;
- lookup target;
- formula details;
- auto-number details;
- picklist values, sequence, reference/actual value, and `colour_code`;
- `enable_colour_code`.

Never export records while performing metadata verification.

## 12. Required answer template for ChatGPT or Codex

When the user asks to create fields, use a table with at least:

| Field Label — Field Type | API Name | API Status | Required | Help Text | Picklist/Default | Notes |
|---|---|---|---|---|---|---|

When the user asks to create a module, first provide:

| Module Display Label — Module Type | Zoho Base Module | API Name | API Status | Purpose | Relationships |
|---|---|---|---|---|---|

Then provide the field table.

## 13. Testing checklist

Before implementation:

- [ ] The module display label and module API name are separated.
- [ ] Every field row uses `Field Label — Field Type`.
- [ ] Every proposed API name is visibly marked unverified.
- [ ] No field type is ambiguous.
- [ ] Every field creation row has help text no longer than 255 characters.
- [ ] Every choice value has a six-digit hex color.
- [ ] Global versus local picklist scope is explicit.
- [ ] Required, unique, default, and history behavior are documented.
- [ ] Lookup target module and relationship direction are explicit.
- [ ] No prohibited Zillow fields or raw private payload field is being added.
- [ ] No tenant PII, record IDs, credentials, or production secrets are in the repository.

After implementation:

- [ ] Export Modules Metadata.
- [ ] Export Fields Metadata with `type=all`.
- [ ] Confirm field labels, API names, data types, tooltips, lengths, and picklist colors.
- [ ] Update the governed catalog with actual metadata.
- [ ] Run `python src/zoho-crm/tools/validate-crm-field-catalog.py`.
- [ ] Smoke-test each integration with sanitized records before production use.

## 14. Rollback

This standard and catalog do not alter live Zoho CRM configuration.

To roll back a repository-only change:

1. revert the merged commit;
2. rerun repository checks;
3. do not delete or recreate live CRM fields merely to match the reverted documentation;
4. reconcile live metadata separately before any destructive CRM change.
