# GH Real Estate Zoho CRM Module and Field Catalog

- **Catalog ID:** GH-ZOHO-CRM-FIELDS-001
- **Version:** 1.4.0
- **Effective date:** July 29, 2026
- **Machine-readable field registry:** governed CSV files under [`crm-module-fields/`](crm-module-fields/)
- **Production reconciliation ledger:** [`zoho-crm-production-reconciliation-2026-07-24.md`](../../../docs/runbooks/zoho-crm-production-reconciliation-2026-07-24.md)
- **Second-pass decision ledger:** [`zoho-crm-second-pass-reconciliation-2026-07-25.md`](../../../docs/runbooks/zoho-crm-second-pass-reconciliation-2026-07-25.md)
- **Application Groups schema reconciliation:** [`zoho-crm-application-groups-schema-reconciliation-2026-07-29.md`](../../../docs/runbooks/zoho-crm-application-groups-schema-reconciliation-2026-07-29.md)
- **Rental Applications layout manifest:** [`rental-applications-layout.json`](rental-applications-layout.json)
- **Operations dashboard specification:** [`gh-real-estate-operations-dashboard.md`](../dashboards/gh-real-estate-operations-dashboard.md)
- **Protected-module baselines:** [`protected-modules/`](protected-modules/)
- **Production global-picklist registry:** [`global-picklists/`](global-picklists/)

## Purpose and source-of-truth boundary

This catalog is the human-readable index for GH Real Estate's Zoho CRM field
governance. The per-module CSV files are the machine-readable field registry.
They include verified live fields, repository/runtime fields, proposed fields,
blocked decisions, historical aliases, and legacy setup candidates.

A row in the registry is not proof that a proposed field exists. A live field
is authoritative only when its `api_name_status` is `verified_live_mcp` and its
exact post-write/readback facts are protected by the validator. Repository
runtime fields are authoritative only for the named integration contract.

When evidence conflicts, use this precedence:

1. current production metadata returned by the approved CRM MCP servers;
2. reviewed production runtime code and integration maps;
3. the governed repository catalog and runbooks;
4. screenshots, workbooks, and historical target designs.

Live metadata proves configuration, not record accuracy, synchronization,
accounting truth, legal consent, signature enforceability, or contract
readiness. No CRM records or tenant/applicant PII belong in this repository.

## Non-negotiable rules

1. Refer to fields as **Field Label — Field Type**.
2. Never infer an API name from a label. A proposed API name is not an actual
   API name.
3. Use actual API names in Deluge, REST payloads, functions, webhooks, merge
   maps, and integration settings.
4. Field type is a creation-time control. A CRM type must also pass the
   destination-specific Books, Contracts, Sign, Catalyst, or Creator
   compatibility gate before integration use.
5. A choice-field change must preserve exact display/reference/actual values,
   order, default, used state, colors, history, and global-set association when
   those facts are available.
6. `UNCOLORED` is allowed only as exact live evidence under
   `module_local_live_uncolored`, `standard_module_live_uncolored`, or
   `global_live_uncolored`. Those scopes are evidence modes, never substitutes
   for a designed target value/color specification.
7. Respect each row's `api_name_status`, `disposition`, and `phase`. Blocked,
   superseded, and `do_not_create` rows must not return to a build queue without
   a separately reviewed migration decision.
8. Do not hardcode secrets or store CRM records, signed documents, screening
   reports, financial transactions, or tenant PII in this catalog.

## Governed CSV inventory

“Verified field APIs” includes `verified_live_mcp`,
`verified_repo_live_integration`, and `verified_repo_runtime`. It does not mean
that every verified field is automatically populated or safe for every
integration.

| CSV module label | Zoho base/module API | Module API status | Catalog rows | Verified field APIs | Still unverified |
|---|---|---|---:|---:|---:|
| Application Groups | `ApplicationGroups` | `verified_live_mcp` | 6 | 6 | 0 |
| Condition Reports | `Condition_Reports` | `verified_live_mcp` | 5 | 5 | 0 |
| Contacts | `Contacts` | `verified_standard_zoho` | 57 | 18 | 39 |
| Equipment (historical target CSV only) | Not authoritative for a live module | `historical_target_only_non_deployable` | 13 | 0 | 13 |
| Inspections | `Inspections` | `verified_live_mcp` | 36 | 19 | 17 |
| Leads | `Leads` | `verified_standard_zoho_and_repo_runtime` | 60 | 34 | 26 |
| Lease Documents / Addenda | Custom candidate | `tbd_from_live_module_metadata` | 16 | 0 | 16 |
| Leases | `Leases` | `verified_live_mcp` | 249 | 43 | 206 |
| Maintenance Requests | `Cases` | `verified_standard_zoho` | 46 | 16 | 30 |
| Notices | Custom candidate | `tbd_from_live_module_metadata` | 21 | 0 | 21 |
| Properties | `Accounts` | `verified_standard_zoho` | 77 | 15 | 62 |
| Rental Applications | `Deals` | `verified_standard_zoho` | 122 | 78 | 44 |
| Storage Units | `Storage_Units` | `verified_live_mcp` | 3 | 3 | 0 |
| Tasks | `Tasks` | `verified_standard_zoho` | 10 | 3 | 7 |
| Units | `Units` | `verified_repo_live_integration` | 54 | 29 | 25 |
| Utilities | `Utilities` | `verified_live_mcp` | 2 | 2 | 0 |
| Vendors | `Vendors` | `verified_standard_zoho` | 24 | 1 | 23 |
| Zillow Intake Events | `Zillow_Intake_Events` | `repo_runtime_default_needs_live_metadata` | 10 | 0 | 10 |
| **Total** | — | — | **811** | **272** | **539** |

The 272 verified APIs comprise 234 current live metadata readbacks, 34
Zillow/Lead runtime APIs, and four Unit APIs documented by the live
integration. The remaining 539 rows are intentionally not represented as
verified live configuration.

The historical [`equipment.csv`](crm-module-fields/equipment.csv) is not the
live Property Assets schema. Production API `Equipment` is the protected
**Property Assets** module described below. The historical CSV cannot
authorize a create, update, delete, choice, or layout operation.

## Protected production modules

These modules are metadata-audit/documentation only. Their sanitized baselines
are checksum-controlled under the default-deny policy in
[`protected-module-policy.json`](protected-modules/protected-module-policy.json).

| Live display label | Module API | Baseline fields | Captured sections | Mutation policy |
|---|---|---:|---:|---|
| Leads | `Leads` | 82 | 10 | Deny; preserve Zillow/Catalyst API contract |
| Property Assets | `Equipment` | 106 | 13 | Deny |
| Pets | `Pets` | 44 | 7 | Deny |
| Vehicles | `Tenant_Vehicles` | 29 | 5 | Deny |

Do not create, update, rename, retire, or delete fields; change choices,
formulas, lookups, rollups, auto-number settings, required/default/unique
flags, tooltips, permissions, sections, or layouts; or attach/detach global
picklists in these modules. A baseline refresh is documentation work and does
not authorize a live mutation. An explicitly authorized same-repository
baseline, checksum, validator, and documentation update remains possible after
fresh metadata readback and review. Checksums detect repository drift; they are
not independent attestation of current live state.

## Current verified reconciliation surface

The July 24 production ledger records 83 custom fields created and read back
across 12 operating modules, additive reconciliation of four standard
picklists, professional field/section placement, and verified reuse of
compatible live fields. The July 25 second pass adds two verified intake
fields and six previously uncataloged live field identities while recording
the current layout disposition of reused fields. The July 29 Application Groups
reconciliation adds six custom-module fields and 47 new Deals fields, upgrades
the governed WorkDrive application-folder URL from candidate to verified live
state, verifies the pre-existing folder resource-ID field, records four
standard Deals relabels, and records final live section placements. The
complete governed live snapshot now contains 234 `verified_live_mcp` rows.
Exact field facts remain in the module CSVs; the validator freezes every
column of every live row.

### Exact standard picklist readback

`-None-` is a Zoho field-level platform sentinel. It is retained in readback
notes and validator rules but omitted from governed business-choice strings.
All choices below had null colors, null default, and history off at readback.

| Module / field | Exact live order |
|---|---|
| Cases / `Status` | New; Escalated; On Hold; Closed; Triage; Scheduled; Waiting on Tenant; Waiting on Vendor; In Progress; Completed; Cancelled |
| Cases / `Priority` | `-None-`; High; Medium; Low; Emergency; Normal |
| Cases / `Case_Origin` | `-None-`; Email; Phone; Web; Tenant Portal; Text; Landlord Created; Inspection |
| Tasks / `Priority` | High; Highest; Low; Lowest; Normal; Emergency |

Tasks Priority is a standard module picklist, not the unverified “GH Priority”
global set previously suggested by repository material.

### Production global picklists

The exact metadata-only registry contains ten visible global sets. Confirmed
GH-governed sets are `States`, `Countries`, `Contact_Type`,
`Property_Type`, and `GH_Lifecycle_Status`; `Building_Entry_Type` is an
unassociated candidate whose values remain unknown. Zoho/system sets
`team_member_role__s`, `access__s`, `Country__s`, and `States__s` are
non-mutation boundaries.

`GH_Lifecycle_Status` is associated with
`Accounts.Property_Status` and `Vendors.Vendor_Status`, with exact order
Active, Inactive, Archived. The full 50-state and 195-country lists and all
confirmed associations are stored in
[`production-global-picklist-registry.json`](global-picklists/production-global-picklist-registry.json).
Unknown or unused values must never be interpreted as safe to delete.

## July 29 Application Groups and per-adult application reconciliation

The July 29 production reconciliation added:

- Application Groups — Custom module — API `ApplicationGroups`;
- six governed Application Groups custom fields;
- one Rental Application Deal per adult applicant;
- `Application_Group`, a Deals lookup to `ApplicationGroups`;
- `Applicant_Role`, with one designated `Primary Applicant`;
- `Application_Promotion_Key`, a case-insensitive unique promotion control;
- 47 new Deals fields, all matched by post-write metadata readback;
- verification and reuse of the pre-existing exact
  `WorkDrive_Application_Folder_URL` and
  `WorkDrive_Application_Folder_Resource_ID` fields, neither counted as a 48th
  created field;
- verified standard-field labels `Rental Application Name`, `Applicant`,
  `Property`, and `Requested Move-In Date`;
- nine exact operational Deals sections plus the unavoidable platform-managed
  `Rental Application Image` section;
- three new active Deals layout rules; and
- Administrator-only access to Application Groups and the restricted
  credit-score provenance bundle.

No Application Group, Rental Application, Contact, Lease, or other CRM record
was created, changed, or backfilled. No application, score, report, screening
value, or document content was read or populated.

### Application Groups ownership

Application Groups owns only the non-PII household/application control layer:

- opaque unique group key;
- expected count of separate adult applications;
- household application status;
- governed internal WorkDrive folder URL and immutable resource ID; and
- the designated `Primary_Rental_Application` lookup to Deals.

The platform primary display Name is an Auto-Number with prefix `AG-`, starting
at 1. Application Groups must not become a person record, screening-report
store, Lease, Contracts request, tenant portal, or accounting record.

The Standard profile is hidden from the module and all six governed fields.
The Administrator profile has read/write access. Exact metadata is in
[`application-groups.csv`](crm-module-fields/application-groups.csv).

### One Rental Application per adult

Each adult applicant owns one Rental Application Deal linked to:

- one Contact through standard `Contact_Name`;
- one Application Group through `Application_Group`; and
- one explicit `Applicant_Role`.

Exactly one Deal in a group is designated `Primary Applicant`, and the group
lookup `Primary_Rental_Application` points to that Deal. Household/request and
future Lease-promotion snapshots appear only in the two primary-only sections.
Schema and layout rules do not yet enforce group completeness or exactly one
primary across records; those remain workflow gates.

The complete 47-field manifest remains in
[`rental-applications.csv`](crm-module-fields/rental-applications.csv). Do not
duplicate it in prose or infer that a field may be populated merely because
its metadata exists.

### Restricted credit-score provenance

The per-adult score/provenance bundle is:

`Credit_Score`, `Credit_Score_Created_Date`, `Credit_Score_Range_Min`,
`Credit_Score_Range_Max`, `Credit_Score_Provider`,
`Credit_Report_Reference_ID`, `Credit_Report_WorkDrive_Resource_ID`,
`Credit_Score_Used_In_Decision`, `Credit_Score_Reviewed_By`, and
`Credit_Score_Reviewed_At`.

Every bundle field is Administrator read/write and hidden from the Standard
profile. The reconciliation did not populate any value or create a score
threshold, formula, pass/fail result, decision automation, adverse-action
workflow, or backfill. Population and use remain blocked until written
screening, permissible-purpose, access, retention, dispute, fair-housing, and
adverse-action controls are separately approved.

Raw reports, OCR, key factors, reason-code narratives, tradelines, creditor or
account data, balances, debt totals, Social Security numbers, license/state-ID
data, banking data, criminal or eviction narratives, public/token-bearing
report URLs, and AI-generated risk scores or recommendations stay out of CRM.
Restricted WorkDrive remains the source-document/evidence boundary.

### Exact layout sections and new rules

The nine exact operational Deals sections, in order, are:

1. `Application Identity & Group`
2. `Property & Requested Terms`
3. `Applicant Income & Rental History`
4. `Screening Summary`
5. `Verification & Adverse Action`
6. `Household & Requests — Primary Only`
7. `Lease Promotion Snapshot — Primary Only`
8. `Documents & Integrations`
9. `System & Legacy`

`Rental Application Image` remains an unavoidable platform-managed section and
is not one of the nine operational sections. It must not hold applications,
identity documents, or screening evidence.

The four verified standard-field labels are:

| API | Live label |
|---|---|
| `Deal_Name` | `Rental Application Name` |
| `Contact_Name` | `Applicant` |
| `Account_Name` | `Property` |
| `Closing_Date` | `Requested Move-In Date` |

The three new active rules are:

| Rule | Trigger | Action |
|---|---|---|
| `Require Vehicle Count When Vehicles Declared` | `Vehicle_Declaration_Status` equals `Vehicle(s) Declared` | Show and set mandatory `Declared_Vehicle_Count` |
| `Require Parking Count When Parking Requested` | `Parking_Request_Status` equals `Requested` | Show and set mandatory `Requested_Parking_Space_Count` |
| `Show Primary Applicant Household and Lease Sections` | `Applicant_Role` equals `Primary Applicant` | Show `Household & Requests — Primary Only` and `Lease Promotion Snapshot — Primary Only` |

Final readback returned seven Deals layout rules total. The existing pet-count
and storage-count rules remained unchanged.

The exact sanitized section order, labels, and rule signatures are governed in
[`rental-applications-layout.json`](rental-applications-layout.json).

### Unchanged production boundaries

The operating Zillow/Catalyst runtime remains Leads-only. Deals Stage,
Pipeline, Probability, `Amount`, and the active Big Deal rule retained their
definitions, values, semantics, and dependencies; their approved layout
placement moved into `System & Legacy`. Leads, Property Assets (`Equipment`),
Pets, and Vehicles
(`Tenant_Vehicles`) remained protected and unchanged. Leases, Zoho Contracts,
Zoho Sign, Zoho Books, WorkDrive documents, and all CRM records were unchanged.
No Application-to-Lease automation is deployed.

See the complete
[`July 29 reconciliation runbook`](../../../docs/runbooks/zoho-crm-application-groups-schema-reconciliation-2026-07-29.md)
for readback totals, privacy/operational authority references, deployment
boundaries, verification, and rollback.

## July 25 second-pass decisions and verified changes

The second-pass ledger separates verified metadata changes from target designs.
No pipeline, dashboard, Contracts mapping, or custom-function deployment is
implied by this catalog.

### Rental Applications pipeline target

Rental Applications uses the standard Deals module API `Deals`. The reviewed
target is one compact Rental Applications pipeline, not parallel screening,
leasing, or tenant pipelines:

| Order | Target stage | State category |
|---:|---|---|
| 1 | Application Received | Open |
| 2 | Screening In Progress | Open |
| 3 | Decision Pending | Open |
| 4 | Approved - Lease Pending | Open |
| 5 | Lease Created | Closed won |
| 6 | Closed - Not Proceeding | Closed lost |

This is a target-only pipeline specification. No live Pipeline or Stage write
occurred on July 25. The current MCP surface has no pipeline CRUD operation and
cannot safely replace the existing stale Stage display-to-actual mappings or
their probability and rule dependencies. `Decision` remains the detailed
application outcome field; Stage should remain the concise operational funnel
after a supported pipeline migration is available.

Leases must not receive a second pipeline. The custom `Leases` module uses
verified field API `Lease_Status` as its lifecycle source. Blueprint transition
control and a Lease Status Kanban view are reviewed future targets only; neither
is asserted live. This keeps applicant conversion separate from lease
administration and prevents the same agreement from being counted as two
revenue opportunities.

### Verified request-count fields

The following Integer fields and active conditional show-and-mandatory layout
rules were read back from production metadata.

| Module | Field label | Exact API name | Type | Verified rule behavior | Placement |
|---|---|---|---|---|---|
| Rental Applications (`Deals`) | Requested Pet Count | `Requested_Pet_Count` | Integer | Conditionally shown and mandatory when pets are requested | Household & Requests — Primary Only |
| Rental Applications (`Deals`) | Requested Storage Unit Count | `Requested_Storage_Unit_Count` | Integer | Conditionally shown and mandatory when storage is requested | Household & Requests — Primary Only |

The Boolean request fields remain the fast yes/no intake controls. Their count
fields capture requested quantity only when applicable. Specific pet details
may belong in the protected Pets module only after its relationship design is
separately approved; storage assignment belongs in Storage Units after
approval. Neither detail set should be duplicated in the application.

### Reversible layout retirement

Redundant or misleading fields were removed from active Standard layouts only.
All fields remain live; no field, record, value, or data was deleted.

| Module / layout | Exact field APIs removed from the layout | Live field disposition |
|---|---|---|
| Contacts / Standard | `Name1`; `F_Name`; `L_Name`; `Parent_Property`; `Account_Type`; `Current_Lease`; `Current_Unit` | Retained live; layout-only retirement |
| Properties (`Accounts`) / Standard | `Parent_Account` | Retained live; layout-only retirement |

This is the rollback boundary: restore `Name1`, `F_Name`, `L_Name`,
`Parent_Property`, and `Account_Type` to Contacts `General & System Fields`;
restore `Current_Lease` and `Current_Unit` to Contacts `Current Tenancy`; and
restore Accounts `Parent_Account` to `General & System Fields` if a dependency
requires them. Read every placement back. Do not describe this retirement as
field deletion or infer that historical record values are empty.

### Dashboard and accounting boundary

The governed dashboard design is
[`gh-real-estate-operations-dashboard.md`](../dashboards/gh-real-estate-operations-dashboard.md).
It is a specification, not a live CRM dashboard. CRM may report application
funnel and lease-operating snapshots, but Zoho Books is authoritative for
actual rent income, invoices, payments, credits, deposits, balances, and
recognized accounting results. Deals `Amount`, lease rent fields, or
closed-stage totals must not be presented as actual gross income.

## Duplicate prevention and field ownership

The validator locks reviewed outcomes for duplicate-prone fields:

- Contacts reuses standard `Other_Phone`, `First_Name`, `Middle_Name`, and
  `Last_Name`; proposed duplicates are `do_not_create`.
- Contacts preferred-contact, contact-role/status, Books-customer-ID, and
  Contracts-counterparty concepts remain blocked where live type, active-rule,
  or integration ownership conflicts exist.
- Properties reuses `Primary_Contact`, `Owner`, and global-backed
  `Account_Type`; Notice Phone remains blocked until the legal/operational
  meaning of standard `Phone` is approved.
- Units reuses `Unit_I_D`, `Unit_Status`, `Current_Tenant`, `Bathrooms`,
  `Bedrooms`, `Square_Feet`, and `Zoho_WorkDrive_Folder_URL`. Historical
  `Unit_ID`, `Occupancy_Status`, and WorkDrive aliases are not create targets.
- Inspections reuses module name API `Name`, `Status`, `Primary_Tenant`,
  `Signed_Checklist_PDF_URL`, and `Photos_Folder_URL`; historical duplicate
  labels are not create targets.

### Operational and evidence-only fields

- Contacts `Email_Operational_Consent` and `SMS_Operational_Consent` are
  history-off operational flags with no source, timestamp, or revocation
  evidence. They are not marketing-consent proof or sole messaging
  authorization.
- Inspections `Tenant_Signed` and `Landlord_Signed` are manual operational
  checkboxes. No Zoho Sign evidence integration is verified, so they are not
  signature or enforcement proof.
- Deals `Zoho_Creator_Application_ID` and Cases `Creator_Ticket_ID` are optional
  Single Line fields without verified uniqueness. They are prohibited as sole
  upsert/idempotency keys until uniqueness, normalization, collision/duplicate
  handling, and post-write readback exist.

### Convenience and financial snapshots

Contacts `Current_Lease` and `Current_Unit`, plus Units `Current_Lease`,
`Current_Lease_End_Date`, and `Current_Base_Rent`, are non-authoritative
convenience/snapshot fields. No idempotent sync workflow currently owns them.
Operators must not treat them as automatically current.

Leases owns tenancy and lease history. Zoho Books owns invoice, payment,
credit, deposit, balance, and actual-income truth. Units
`Security_Deposit_Default` and `Current_Base_Rent` are optional editable
planning/default snapshots only: they are not payment evidence or enforceable
tenant amounts and must not be automatically copied or charged. Lease-specific
amounts require approved terms, policy review, applicable
furnished/deposit-cap review, and readback.

## Lease and Contracts readiness

The live Lease field `First_Full_Month_Base_Rent_Amount` is Currency(2), with
the exact tooltip:

> First full-month base-rent input for the due-before-possession calculation.
> Reconcile to approved lease terms and Zoho Books before contract readiness.

That input does not close the calculation or mapping gate:

- `Total_Due_Before_Possession` is an editable Currency snapshot, not a
  verified Formula field.
- No available MCP server exposed Zoho Contracts or Zoho Sign field-mapping
  administration, so Formula-field portability to Contracts is unverified.
- Do not convert the total to Formula or claim it is contract-ready without a
  destination mapping test and readback. The safest integration shape is a
  controlled, idempotent calculation that materializes the approved result
  into a Currency snapshot for Contracts, with component and output readback.
- Existing `Monthly_Rent` and `Prorated_Rent` semantics remain ambiguous.
- Lease Number remains blocked until its auto-number format and collision
  policy are approved.
- Lease Status values/history exist, but target order, default Draft, and
  required behavior remain unenforced.
- Exact pre-change placement for seven moved legacy fields was not captured;
  rollback must use an authorized Zoho audit/export and must not guess.

The Residential Lease Agreement remains Draft, unpublished, unsent,
execution-blocked, and attorney-review-required. No Contracts extension,
mapping, button, signer configuration, contract request, publication, or
signature send is asserted by this CRM catalog.

## Field-type governance

The supplied UI screenshot is evidence of CRM field types available in the
layout editor; it is not proof that a field exists or that another Zoho product
can map it. The companion
[`crm-field-type-catalog.md`](../standards/crm-field-type-catalog.md) records
the reviewed CRM type vocabulary and integration gates.

Before creating or mapping a field, verify:

- exact CRM metadata type and constraints;
- lookup target or multi-select lookup behavior;
- precision for Currency, Decimal, Percent, and Long Integer;
- auto-number prefix/start/suffix;
- formula return type and recomputation behavior;
- default, mandatory, unique, history, and color-coding settings; and
- destination-specific Books, Contracts, Sign, Catalyst, or Creator support.

If the necessary product metadata/documentation MCP is unavailable, mark the
compatibility `unverified` and stop. Do not infer it from the CRM UI.

## Verification statuses

| Status | Meaning |
|---|---|
| `verified_live_mcp` | Exact production metadata was returned through the approved CRM MCP and preserved by readback validation. |
| `verified_repo_runtime` | API name is used by reviewed runtime code; this is not current live metadata proof. |
| `verified_repo_live_integration` | API name is documented by the reviewed live integration boundary. |
| `proposed_unverified` | Target proposal only; not safe for integration use. |
| `not_proposed_unverified` | Known label/type without a safe API proposal. |
| `repo_runtime_default_needs_live_metadata` | Runtime contains a default that still requires live metadata verification. |
| `blocked_protected_module` | Proposal is absent from a protected live baseline and is explicitly nondeployable; do not create. |
| `historical_target_only_non_deployable` | Historical target-design evidence only; never a live create/update manifest. |
| `blocked_ambiguous` | Semantic, ownership, type, or dependency conflict blocks creation/reuse. |
| `superseded_by_verified_live_mcp_field` | A verified live field replaces the historical proposal; do not create. |
| `superseded_by_verified_repo_field` | A governed repository field replaces the historical alias; do not create. |
| `unsupported_by_current_mcp` | The current MCP surface cannot safely apply or verify the requested behavior. |
| `prohibited_current_design` | Intentionally excluded by the current security/data-minimization design. |

## Validation and change gate

Run from the repository root:

```text
python src/zoho-crm/tools/validate-crm-field-catalog.py
python src/zoho-crm/tools/validate-protected-module-baselines.py
python -m unittest discover -s src/zoho-crm/tests -p "test_*.py" -v
```

The field-catalog validator checks required columns, API-name syntax, live
evidence source IDs, exact live manifests, lookup targets, choices/order/colors,
sentinel readback, policy warnings, duplicate-prevention decisions, and a
canonical digest of all 234 live rows. It also freezes the sanitized Rental
Applications section order, four standard-field labels, three new layout-rule
signatures, final rule count, and privacy boundaries. Protected-baseline
checksums fail closed on unauthorized field/layout drift.

Any live change still requires:

1. an exact organization/environment gate;
2. metadata-only preflight and dependency review;
3. a bounded, reviewable mutation manifest;
4. immediate post-write readback;
5. rollback evidence that does not guess prior state; and
6. repository updates in the same reviewed change.

## Known limitations

- The live audit used approved metadata/configuration MCP servers only. No
  Browser control, CRM records, PII, credentials, or Books transactions were
  accessed.
- The 811-row CSV registry is broader than the verified live surface; it
  intentionally retains unverified and blocked planning evidence.
- Deals Stage definitions and values remain unchanged because their
  display/actual values are stale/misaligned and pipeline/probability
  dependencies were not safely writable through the available MCP. Only
  placement in `System & Legacy` changed. The July 25 six-stage specification
  is a migration target, not evidence of a live pipeline.
- Required/default controls and complete Lease readiness are not implemented by
  catalog documentation alone.
- `Zillow_Intake_Events` remains an optional disabled-by-default runtime
  candidate, not a second source of truth.
- Zoho Contracts contract-type API names, field mappings, extension behavior,
  signer routing, and Zoho Sign evidence remain unverified on the available MCP
  surface.
- The approved MCP surface has no pipeline, CRM dashboard/component, Zoho
  Contracts, or reusable custom-function CRUD. Repository specifications do
  not close those live-administration gaps.

## References

- [CRM field authoring standard](../standards/crm-module-field-authoring-standard.md)
- [CRM field-type catalog](../standards/crm-field-type-catalog.md)
- [Protected module policy and baselines](protected-modules/README.md)
- [Production global-picklist registry](global-picklists/README.md)
- [Production reconciliation ledger](../../../docs/runbooks/zoho-crm-production-reconciliation-2026-07-24.md)
- [Second-pass reconciliation ledger](../../../docs/runbooks/zoho-crm-second-pass-reconciliation-2026-07-25.md)
- [Application Groups schema reconciliation](../../../docs/runbooks/zoho-crm-application-groups-schema-reconciliation-2026-07-29.md)
- [GH Real Estate operations dashboard specification](../dashboards/gh-real-estate-operations-dashboard.md)
- [Lease-system reconciliation](../../../docs/runbooks/zoho-crm-lease-system-reconciliation.md)
- Official Zoho CRM Modules Metadata: https://www.zoho.com/crm/developer/docs/api/v8/modules-api.html
- Official Zoho CRM Fields Metadata: https://www.zoho.com/crm/developer/docs/api/v8/field-meta.html
- Official Zoho CRM field types: https://help.zoho.com/portal/en/kb/crm/customize-crm-account/customizing-fields/articles/types-of-fields
