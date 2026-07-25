# Zoho CRM Production Reconciliation

**Audit date:** July 24, 2026

**Status:** Production metadata audit, applied reconciliation, and verified readback ledger

**Organization gate:** `GH Real Estate` / `production`

**Execution surface:** Available MCP servers only; no Browser control

**Record-data boundary:** No CRM records, tenant/applicant PII, credential values, or Books transactions were read

## 1. Outcome

The production organization was inventoried through approved metadata/configuration MCP servers and reconciled against the governed repository catalog. This document is the whole-CRM control record. The earlier [Lease-system reconciliation](zoho-crm-lease-system-reconciliation.md) remains the detailed historical record for the bounded Rental Application and Lease build.

This audit established:

- 72 CRM modules returned by the production module inventory: 49 visible, 15 user-hidden, and 8 system-hidden;
- all 51 modules flagged `api_supported=true` received field and layout metadata requests: fields succeeded for 43 and were rejected for 8; layouts succeeded for 30, were rejected for 17, and returned four truncated responses;
- checksum-controlled, sanitized GitHub baselines and a deny policy for Leads, Property Assets, Pets, and Vehicles;
- a no-write boundary for those four modules;
- exact reuse, duplicate, semantic-conflict, workflow, layout-rule, and integration findings for the operating modules;
- 83 custom fields created and read back across 12 modules;
- one global picklist, `GH_Lifecycle_Status`, created and associated with `Accounts.Property_Status` and `Vendors.Vendor_Status`;
- additive standard-choice updates on Cases Status, Priority, and Case Origin and Tasks Priority, with all prior values preserved;
- professional sections and field placements applied and read back across the changed layouts;
- two Utilities relationship fields created and two ambiguous legacy Utilities labels clarified without changing their APIs;
- immediate readback of the Vendor credential-field security remediation described in section 6;
- fail-closed boundaries for Deals Stage/Pipeline, Lease calculations, Books synchronization, Zoho Contracts, and Zoho Sign.

Section 8 is the exact production readback manifest for this broader build. Proposed items omitted from that manifest remain uncreated unless another verified ledger says otherwise.

## 2. Authority and evidence boundaries

Use this precedence when sources disagree:

1. current production Modules, Fields, Layouts, Layout Rules, Workflows, and Global Picklist metadata returned by the approved MCP server;
2. production runtime code and reviewed repository integration maps;
3. governed repository target catalogs and runbooks;
4. a supplied CRM Setup screenshot or workbook.

The screenshot supplied for this audit documents UI field-type availability. It is not proof that a field exists, that a type is supported by another Zoho product, or that a field can be converted after creation. The governed [CRM field-type catalog](../../src/zoho-crm/standards/crm-field-type-catalog.md) records the UI choices and the integration verification gate.

Repository targets do not override a conflicting live API name or type. Proposed API names remain proposals until read back. Custom field types must be correct at creation; do not create a temporary type expecting to convert it later.

No available MCP server exposed current Zoho Contracts or Zoho Sign administration/documentation metadata. The Books server exposed only bounded organization-review capability for this work. Therefore, destination-specific compatibility must remain unverified rather than inferred from CRM metadata or a screenshot.

This document intentionally omits organization, module, layout, section, field, workflow, profile, picklist-value, and record IDs.

## 3. Production module inventory

The exact sanitized 72-module inventory is
[`production-module-inventory-2026-07-24.csv`](../../src/zoho-crm/field-maps/production-module-inventory-2026-07-24.csv).
The 51-module field/layout attempt ledger is
[`production-module-metadata-audit-2026-07-24.csv`](../../src/zoho-crm/field-maps/production-module-metadata-audit-2026-07-24.csv).
Both omit IDs, actors, profiles, timestamps, and record data, and their exact
counts/digests are covered by repository tests.

The table below narrows that full inventory to the operating and integration
modules material to this reconciliation. Field counts are sanitized post-write
July 24 metadata counts, not record counts.

| Display label | API name | Post-write field count | Reconciliation class |
|---|---|---:|---|
| Leads | `Leads` | 82 | Protected, audit/document only |
| Property Assets | `Equipment` | 106 | Protected, audit/document only |
| Pets | `Pets` | 44 | Protected, audit/document only |
| Vehicles | `Tenant_Vehicles` | 29 | Protected, audit/document only |
| Rental Applications | `Deals` | 52 | Six fields applied/read back; Stage/Pipeline/Amount remain blocked |
| Contacts | `Contacts` | 131 | Nine fields applied/read back |
| Properties | `Accounts` | 114 | Eight fields applied/read back; lifecycle global associated |
| Units | `Units` | 47 | 15 fields applied/read back |
| Leases | `Leases` | 67 | One Currency field applied/read back; equation/Contracts handoff remain gated |
| Maintenance Requests | `Cases` | 43 | 13 fields and additive standard choices applied/read back |
| Tasks | `Tasks` | 23 | Two fields and additive Priority value applied/read back |
| Vendors | `Vendors` | 81 | One field/global association applied; credential containment reverified |
| Inspections | `Inspections` | 35 | 18 fields applied/read back |
| Amenities | `Amenities` | 17 | Preserve; no governed target manifest |
| Storage Units | `Storage_Units` | 39 | Three relationship fields applied/read back |
| Utilities | `Utilities` | 25 | Two relationship fields and two legacy label clarifications applied/read back |
| Condition Reports | `Condition_Reports` | 29 | Five relationship fields applied/read back |
| Products | `Products` | 34 | Integration/accounting-managed boundary |
| Invoices | `Invoices` | 45 | Integration/accounting-managed boundary |
| Invoice | `CustomModule5001` | 36 | Custom integration boundary; ownership unresolved |
| Zoho Contracts | `zohocontracts__Contracts` | 34 | Extension-managed; no write |

The remaining supported modules were audited and preserved because no repository-backed business change passed the duplicate, ownership, workflow, and integration gates. `Campaigns`, `Purchase_Orders`, `Price_Books`, `Visits`, `Quotes`, `Sales_Orders`, and `Solutions`, plus some file/system pseudo-modules, rejected field/layout enumeration or were disabled/hidden. That limitation is not permission to infer their schemas or mutate them.

## 4. Protected and managed boundaries

| Module | Control |
|---|---|
| Leads -- API `Leads` | No metadata or layout writes. The Zillow/Catalyst intake depends on its live API surface. |
| Property Assets -- API `Equipment` | No metadata or layout writes. The historical `equipment.csv` target does not authorize changes to this live module. |
| Pets -- API `Pets` | No metadata or layout writes. |
| Vehicles -- API `Tenant_Vehicles` | No metadata or layout writes. |

The authoritative sanitized snapshots and deny policy are under [`src/zoho-crm/field-maps/protected-modules/`](../../src/zoho-crm/field-maps/protected-modules/). Any proposed change to those modules must fail CI unless the owner deliberately changes the policy and baseline in a separately reviewed authorization.

This is checksum drift detection and repository governance, not cryptographic
immutability. The hashes and validator live in the same repository, so an
owner-authorized change can update them together. Stronger enforcement also
requires protected-branch checks and approval rules; those controls are not
confirmed enabled. GitHub cannot prevent a Zoho administrator from changing
live metadata, so a later metadata-only audit is still required to detect
external drift.

The sanitized snapshots omit profile identities/permissions and do not retain
complete formula expressions. Their checks cannot detect every access-control
or formula-expression change. Any future decision involving those controls
requires a fresh authorized metadata-only formula and permission audit.

Also preserve these managed surfaces unless a separate integration-specific change is approved:

- Books-owned invoice, payment, balance, credit, deposit, tax, and accounting fields;
- `zohocontracts__Contracts` extension fields and related-list behavior;
- standard audit fields and Zoho system modules;
- existing global picklist associations; and
- any field or layout rule whose downstream dependency cannot be enumerated.

## 5. Verified reuse and conflict register

### Contacts -- API `Contacts`

- Reuse standard `Phone` for the primary phone and standard `Other_Phone` for a secondary phone. Do not create a duplicate `Secondary_Phone`.
- Reuse `First_Name`, `Middle_Name`, `Last_Name`, and `Full_Name` for legal/person names.
- Reuse standard `Date_of_Birth`. The unused/off-layout custom `Date_Of_Birth1` is a duplicate candidate, but must not be deleted without a dependency/value audit.
- Reuse standard mailing fields `Mailing_Street`, `Mailing_City`, `Mailing_State`, `Mailing_Zip`, and `Mailing_Country`; do not create a compound duplicate address.
- Preserve global picklist-backed `Contact_Type`. An active layout rule depends on it, and it must not be replaced by proposed `Contact_Role_Type` or `Contact_Status` without a migration design.
- Live `Preferred_Method_Of_Communication` is multi-select with Call, Email, and Text. The catalog's preferred-contact concept is single-select, so a duplicate or semantic conversion is blocked.
- Do not place a Books Customer ID or Contracts Counterparty ID on Contacts until the owning integration is verified. The current Contracts extension counterparty identifier is associated with Properties/Accounts.
- `Current_Lease` and `Current_Unit` are non-authoritative convenience lookups until an idempotent workflow owns their updates. Lease records own tenancy history; a manually maintained Contact shortcut must not override that history.

### Properties -- renamed Accounts, API `Accounts`

- Reuse `Street_Line_1`, `Street_Line_2`, `City`, `State`, `Zip_Code1`, `Country`, and `Full_Address`.
- Reuse standard `Phone` for the notice phone only after its operational/legal meaning is approved; it was unused/off-layout at audit.
- Reuse `Primary_Contact` for the property-manager name concept and `Owner` for the responsible CRM user.
- Reuse standard `Account_Type`, which is attached to the `Property_Type` global picklist. Do not create a second Property Type field.

### Units -- API `Units`

- Reuse `Current_Tenant`, `Bathrooms`, `Bedrooms`, `Square_Feet`, the existing WorkDrive URL, and the four governed Zillow routing/listing identifiers.
- Use live `Unit_Status`. Do not create proposed `Occupancy_Status`; the live values are Occupied, Vacant - Ready, Vacant - Needs Turnover, Under Renovation, Reserved, and Inactive.
- Use live auto-number `Unit_I_D`. Do not create proposed `Unit_ID`.
- `Current_Lease`, `Current_Lease_End_Date`, and `Current_Base_Rent` are non-authoritative convenience snapshots until an idempotent workflow owns their updates. Leases owns the tenancy term, while Books owns invoice, payment, and balance truth.
- `Security_Deposit_Default` and `Current_Base_Rent` are optional planning/default snapshots, not payment evidence or enforceable tenant charges. Never copy or charge them automatically; each Lease amount still requires approved terms, applicable furnished/deposit-cap review, and reconciliation to Books.
- The former generic audit section was read back as `System Ownership & Audit`.

### Rental Applications -- renamed Deals, API `Deals`

- Reuse standard `Deal_Name`, `Contact_Name`, `Account_Name`, `Closing_Date`, `Description`, `Owner`, `Pipeline`, `Stage`, and `Lead_Source`.
- The existing 15 governed application fields remain the verified application decision/approved-term surface documented in the [Lease-system reconciliation](zoho-crm-lease-system-reconciliation.md).
- Do not create duplicate Application Name, Primary Applicant, Property, Desired Move-In Date, or Applicant Notes fields.
- Keep sensitive screening detail out of broadly visible CRM fields until a field-level access, retention, and legal review is approved.
- `Amount` is blocked from reinterpretation as approved base rent because the active Big Deal Rule depends on `Amount >= 1000` and `Probability = 100`.

### Maintenance Requests -- renamed Cases, API `Cases`

- Reuse `Case_Number`, `Subject`, `Account_Name` for Property, `Related_To` for Tenant, `Case_Origin`, `Priority`, `Status`, `Description`, `Internal_Comments`, and `Solution`.
- Prefer a supported relabel of `Solution` to Resolution Notes over a duplicate resolution field, after dependency readback.
- Existing standard Status, Priority, and Origin values were preserved. Section 9 records the additive values that were applied and read back.
- Estimated Cost, Actual Cost, and Tenant Charge Amount require explicit separate currency semantics. Do not create or reuse a single ambiguous `Charge_Amount`.

### Vendors -- API `Vendors`

- Preserve the existing Vendor Type and Attorney Type taxonomy and their active layout rules.
- Preserve `GL_Account`, `Payment_Terms`, and billing/shipping address globals as Books/integration-managed.
- Credential fields are not a supported integration pattern; section 6 records the applied containment.

### Tasks -- API `Tasks`

`Task_Category` and `Important_for_PM_Handoff` were created and read back. Emergency was added to standard Priority without removing existing values. Standard task identity, owner, status, due-date, reminder, recurrence, and relationship fields remain authoritative.

### Leases -- API `Leases`

- Reuse the 33 created fields and seven compatible fields recorded in the [Lease-system reconciliation](zoho-crm-lease-system-reconciliation.md).
- Existing `Monthly_Rent` and `Prorated_Rent` are editable Currency fields with unproven semantics. Do not relabel, map, or duplicate them until dependencies and business meaning are approved.
- Existing `Total_Due_Before_Possession` is a Currency snapshot, not a verified Formula field.
- `Lease_Status` target values/colors and history are present, but target order, default Draft, and required behavior remain unenforced.
- Lease Number remains blocked until an auto-number prefix/format and collision policy are approved.
- `First_Full_Month_Base_Rent_Amount` now exists as a read-backed Currency(2) input. Its creation closes the field gap, not the unresolved equation, automation, or Contracts-mapping gates.

### Other custom/integration modules

- Inspections now has 18 read-backed operating fields in addition to its earlier minimal surface.
- Amenities has no governed target manifest; preserve it.
- Storage Units now has read-backed Property, Unit, and Lease relationships.
- Utilities now has authoritative Property and Unit lookups. The ambiguous legacy labels were clarified while their APIs and values were preserved.
- Condition Reports now has read-backed Inspection, Property, Unit, Lease, and Tenant relationships.
- Products, Invoices, custom Invoice, and the Contracts extension remain integration-managed.

## 6. Vendor credential-field containment already applied

The live Vendor fields `Username` and `Password` were plain-text custom fields. Both were readable/writable for Administrator and Standard profiles, and Password was visible in the Utility Account Information layout section.

The approved CRM configuration MCP applied and immediately read back these controls:

1. `Username` and `Password` are hidden for Administrator and Standard profiles.
2. Both fields were removed non-permanently from the active Standard Vendor layout.
3. Final metadata readback returned `visible: false`, hidden profile permissions, and no active layout association for either field.

The same containment state was re-read after the broader field/layout work and remained intact. No credential values or Vendor records were read. The fields were not deleted.

Remaining security work:

- identify every external account represented by those legacy fields without exposing values in logs or GitHub;
- rotate the credentials in the owning systems;
- migrate any still-required secrets into an approved password/secrets manager;
- audit functions, reports, exports, APIs, and integrations for dependencies; and
- retire the CRM fields only after dependency and value-retention review.

Do not roll this containment back merely to recover a forgotten credential. Any temporary re-exposure requires explicit security authorization, a time-bounded migration plan, audit-log review, and immediate re-hide/rotation.

## 7. Deals Stage, Pipeline, and workflow blocker

The Deals Stage field cannot be reconciled safely through an additive picklist edit:

- display `Move-In Scheduled` maps to underlying actual value `Closed Lost`;
- the active `ReasonForLoss RULE` is category-based and triggers on `${CATEGORY.Closed Lost}`;
- other live Stage display-to-actual mappings are stale or semantically unrelated, as preserved in [`rental-applications.csv`](../../src/zoho-crm/field-maps/crm-module-fields/rental-applications.csv);
- Pipeline display `Rental Applications` maps to underlying actual value `Lease Agreement`; and
- the active Big Deal Rule depends on Amount and Probability.

No available MCP tool can safely read and rewrite the complete pipeline, category, probability, layout-rule, workflow, and reporting semantics as one reversible transaction. Therefore:

- do not add, remove, rename, reorder, or remap Stage values;
- do not repurpose `Amount`;
- do not alter Pipeline;
- do not disable the ReasonForLoss or Big Deal rules; and
- do not automate against Stage display labels or the stale actual values.

Resolution requires a supported pipeline metadata surface, a before-state export, an approved old-to-new transition map, workflow/layout-rule regression tests, and exact post-write category/probability readback.

## 8. Applied custom-field manifest

All 83 fields below were created through the approved CRM configuration MCP and returned by post-write metadata readback. The listed APIs are actual live API names, not proposals. Readback also confirmed the field type, lookup target where applicable, and final layout placement. This classification does not imply that an intended required/default/unique rule or downstream automation exists.

### Contacts -- 9 fields

- Portal Invite Sent At -- Date/Time -- API `Portal_Invite_Sent_At`
- Portal Invite Status -- Pick List -- API `Portal_Invite_Status`
- Email Operational Consent? -- Checkbox -- API `Email_Operational_Consent`
- SMS Operational Consent? -- Checkbox -- API `SMS_Operational_Consent`
- Preferred Name -- Single Line -- API `Preferred_Name`
- Primary Language -- Pick List -- API `Primary_Language`
- Current Lease -- Lookup to `Leases` -- API `Current_Lease`
- Current Unit -- Lookup to `Units` -- API `Current_Unit`
- WorkDrive Person Folder URL -- URL -- API `WorkDrive_Person_Folder_URL`

### Properties -- API `Accounts` -- 8 fields

- County -- Single Line -- API `County`
- Emergency Maintenance Phone -- Phone -- API `Emergency_Maintenance_Phone`
- Notice Email -- Email -- API `Notice_Email`
- Owner / Landlord Legal Name -- Single Line -- API `Owner_Landlord_Legal_Name`
- Property Code -- Single Line -- API `Property_Code`
- Default Lease Template Version -- Single Line -- API `Default_Lease_Template_Version`
- WorkDrive Property Folder URL -- URL -- API `WorkDrive_Property_Folder_URL`
- Property Status -- Pick List associated with global `GH_Lifecycle_Status` -- API `Property_Status`

Property Code was not proven unique by readback. Do not use it as an idempotency key until uniqueness is supported, applied, and verified.

### Units -- 15 fields

- Current Lease -- Lookup to `Leases` -- API `Current_Lease`
- Current Lease End Date -- Date -- API `Current_Lease_End_Date`
- Move-In Checklist Status -- Pick List -- API `Move_In_Checklist_Status`
- Next Lease Start Date -- Date -- API `Next_Lease_Start_Date`
- Available Date -- Date -- API `Available_Date`
- Current Base Rent -- Currency(2) -- API `Current_Base_Rent`
- Default Storage Area -- Single Line -- API `Default_Storage_Area`
- Furnished? -- Checkbox -- API `Furnished`
- Parking Spaces -- Number/integer -- API `Parking_Spaces`
- Security Deposit Default -- Currency(2) -- API `Security_Deposit_Default`
- Storage Available? -- Checkbox -- API `Storage_Available`
- Target Market Rent -- Currency(2) -- API `Target_Market_Rent`
- Market Status -- Pick List -- API `Market_Status`
- Zillow Listing Active? -- Checkbox -- API `Zillow_Listing_Active`
- Zillow Listing URL -- URL -- API `Zillow_Listing_URL`

### Rental Applications -- API `Deals` -- 6 fields

- Application Reviewer -- User Lookup -- API `Application_Reviewer`
- Household Size -- Number/integer -- API `Household_Size`
- Pets Requested? -- Checkbox -- API `Pets_Requested`
- Requested Lease Term Months -- Number/integer -- API `Requested_Lease_Term_Months`
- Storage Requested? -- Checkbox -- API `Storage_Requested`
- Zoho Creator Application ID -- Single Line -- API `Zoho_Creator_Application_ID`

Application No., Assistance Animal Request?, Cosigner Required?, Internal Review Notes, and WorkDrive Application Folder URL were not created. Application No. still lacks an approved auto-number format; Cosigner Required has the unresolved semantic, writer, and migration design described in section 9; and the sensitive/repository-ownership candidates require separate approval.

### Maintenance Requests -- API `Cases` -- 13 fields

- Lease -- Lookup to `Leases` -- API `Lease`
- Unit -- Lookup to `Units` -- API `Unit`
- Assigned Vendor -- Lookup to `Vendors` -- API `Assigned_Vendor`
- Assigned Vendor Contact -- Lookup to `Contacts` -- API `Assigned_Vendor_Contact`
- Access Permission -- Pick List -- API `Access_Permission`
- Pets / Animals Need Secured? -- Checkbox -- API `Pets_Animals_Need_Secured`
- Reported At -- Date/Time -- API `Reported_At`
- Scheduled Date/Time -- Date/Time -- API `Scheduled_Date_Time`
- Creator Ticket ID -- Single Line -- API `Creator_Ticket_ID`
- Photos / Files Folder URL -- URL -- API `Photos_Files_Folder_URL`
- Photos Received? -- Checkbox -- API `Photos_Received`
- Emergency? -- Checkbox -- API `Emergency`
- Maintenance Category -- Pick List -- API `Maintenance_Category`

Tenant Chargeable? was not created. Any future chargeability field must remain a review control and must never create an invoice or charge without separate approval, evidence, amount, duplicate prevention, and Books readback.

### Inspections -- API `Inspections` -- 18 fields

- Inspection Type -- Pick List -- API `Inspection_Type`
- Property -- Lookup to `Accounts` -- API `Property`
- Unit -- Lookup to `Units` -- API `Unit`
- Lease -- Lookup to `Leases` -- API `Lease`
- Primary Tenant -- Lookup to `Contacts` -- API `Primary_Tenant`
- Status -- Pick List -- API `Status`
- Inspection Date -- Date -- API `Inspection_Date`
- Due Date -- Date -- API `Due_Date`
- Completed Date -- Date -- API `Completed_Date`
- Completed By -- User Lookup -- API `Completed_By`
- Related Maintenance Request -- Lookup to `Cases` -- API `Related_Maintenance_Request`
- Repair Requested? -- Checkbox -- API `Repair_Requested`
- Checklist Form URL -- URL -- API `Checklist_Form_URL`
- Signed Checklist PDF URL -- URL -- API `Signed_Checklist_PDF_URL`
- Photos Folder URL -- URL -- API `Photos_Folder_URL`
- Tenant Signed? -- Checkbox -- API `Tenant_Signed`
- Landlord Signed? -- Checkbox -- API `Landlord_Signed`
- Joint Inspection Completed? -- Checkbox -- API `Joint_Inspection_Completed`

### Leases -- API `Leases` -- 1 field

- First Full Month Base Rent Amount -- Currency(2) -- API `First_Full_Month_Base_Rent_Amount`

This is an input field, not a Formula field. Section 10's equation, snapshot, automation, and Contracts gates remain open.

### Vendors -- API `Vendors` -- 1 field

- Vendor Status -- Pick List associated with global `GH_Lifecycle_Status` -- API `Vendor_Status`

Insurance, W-9/1099, preferred/emergency vendor, service area, WorkDrive, last-used, and rating concepts remain deferred until exact APIs, types, retention/access rules, and Books ownership are governed.

### Tasks -- API `Tasks` -- 2 fields

- Task Category -- Pick List -- API `Task_Category`
- Important for PM Handoff? -- Checkbox -- API `Important_for_PM_Handoff`

### Storage Units -- API `Storage_Units` -- 3 fields

- Property -- Lookup to `Accounts` -- API `Property_Record`
- Unit -- Lookup to `Units` -- API `Unit`
- Lease Record -- Lookup to `Leases` -- API `Lease_Record`

### Utilities -- API `Utilities` -- 2 fields

- Property Record -- Lookup to `Accounts` -- API `Property_Record`
- Unit Record -- Lookup to `Units` -- API `Unit_Record`

Two existing Utilities fields were preserved and relabeled to remove ambiguity:

- existing API `Property`: label changed from Property to `Property (Legacy Text)`;
- existing API `Unit`: label changed from Units to `Property (Legacy Lookup)`.

No type, API, or record-value conversion was performed on those legacy fields.

### Condition Reports -- API `Condition_Reports` -- 5 fields

- Inspection -- Lookup to `Inspections` -- API `Inspection`
- Property -- Lookup to `Accounts` -- API `Property`
- Unit -- Lookup to `Units` -- API `Unit`
- Lease -- Lookup to `Leases` -- API `Lease`
- Tenant -- Lookup to `Contacts` -- API `Tenant`

## 9. Applied choice and global-picklist readback

Every value below was returned by post-write metadata readback. New and additive picklist values were uncolored in the live metadata; the repository's proposed semantic colors were not applied and are not claimed live.

| Field | Scope | Exact read-back values or additive values |
|---|---|---|
| Contacts `Portal_Invite_Status` | Local | Not Invited; Invite Ready; Invited; Accepted; Failed; Disabled |
| Contacts `Primary_Language` | Local | English; Spanish; Ukrainian; Russian; Other |
| Accounts `Property_Status` | Global `GH_Lifecycle_Status` | Active; Inactive; Archived |
| Units `Move_In_Checklist_Status` | Local | Not Started; Sent; In Progress; Completed; Overdue; Not Applicable |
| Units `Market_Status` | Local | Not Listed; Listed; Application Pending; Lease Pending; Leased; Renovation Hold |
| Cases `Access_Permission` | Local | Permission Granted; Appointment Required; Tenant Must Be Present; Emergency Access Only; Unknown |
| Cases `Maintenance_Category` | Local | Plumbing; Electrical; HVAC; Appliance; Pest; Lock/Key; Water Leak; Noise/Rule Issue; Common Area; Exterior/Grounds; Laundry; Other |
| Inspections `Inspection_Type` | Local | Move-In; Move-Out; Annual; Pre-Renewal; Post-Repair; Owner Walkthrough; Other |
| Inspections `Status` | Local | Not Started; Scheduled; Sent to Tenant; In Progress; Tenant Submitted; Landlord Review; Follow-Up Required; Completed; Overdue; Cancelled; Archived |
| Vendors `Vendor_Status` | Global `GH_Lifecycle_Status` | Active; Inactive; Archived |
| Tasks `Task_Category` | Local | Lease Renewal; Rent Follow-Up; Maintenance Follow-Up; Inspection; Vendor Follow-Up; PM Handoff; Accounting; Legal/Notice; Admin; Other |

Global `GH_Lifecycle_Status` was created with exact order Active, Inactive, Archived and associated only to `Accounts.Property_Status` and `Vendors.Vendor_Status`. Both associated-field readbacks were uncolored, default null, history tracking off, and color coding off.

The following standard-module values were added without deleting or renaming any existing value:

| Standard field | Added values |
|---|---|
| Cases `Status` | Triage; Scheduled; Waiting on Tenant; Waiting on Vendor; In Progress; Completed; Cancelled |
| Cases `Priority` | Emergency; Normal |
| Cases `Case_Origin` | Tenant Portal; Text; Landlord Created; Inspection |
| Tasks `Priority` | Emergency |

The added standard-field values were also uncolored in readback. Existing values, order relationships, defaults, and dependencies were preserved unless separately recorded.

The production global-picklist inventory and association evidence remain governed under [`src/zoho-crm/field-maps/global-picklists/`](../../src/zoho-crm/field-maps/global-picklists/). Do not associate `GH_Lifecycle_Status` with another field without a separate semantic and dependency review.

Deals `Cosigner_Required` was not created. The catalog now correctly assigns
red `#DC2626` to Not Approved, but the proposed question-style field label
still conflicts with its multi-state workflow values. Keep it blocked until
the field semantics, writer, and migration behavior are approved; the color
correction alone does not authorize a production field.

## 10. Lease calculation and Contracts handoff

### Recommended controlled design

Keep `Total_Due_Before_Possession` as a Currency(2) integration snapshot. Do not convert it to Formula and do not map an unverified Formula field directly to Contracts.

`First_Full_Month_Base_Rent_Amount` is now a verified Currency(2) input. No calculation, copy automation, readiness rule, or Contracts mapping was created with it.

The candidate audit equation is:

```text
Prorated Base Rent
+ First Full Month Base Rent
+ Security Deposit
+ Pet Security Deposit
+ Prorated Pet Rent
+ Prorated Storage Rent
- Holding Deposit Credit Applied
= Total Due Before Possession
```

The separate monthly equation is:

```text
Base Rent
+ Total Monthly Pet Rent
+ Total Monthly Storage Rent
= Total Monthly Rent
```

Mandatory missing inputs must block contract readiness. Optional pet/storage inputs may be treated as zero only when non-applicability is explicitly established. A negative total or a mismatch between calculated and snapshot values must block handoff.

Unresolved policy:

- whether the first full month's pet and storage rent are included before possession;
- whether any non-refundable fees belong in the equation;
- whether live `Monthly_Rent` means base rent or total monthly rent;
- whether live `Prorated_Rent` means prorated base rent or a broader amount; and
- the approved timing and source for copying the audit result into the Currency snapshot.

No available MCP server can verify that a CRM Formula field is selectable, evaluated, or refreshed correctly in a Zoho Contracts field mapping. No Contracts canary was run. The safe pattern is:

1. calculate and validate through an approved auditable automation or formula;
2. copy the result into the Currency snapshot before Ready for Contract;
3. compare audit and snapshot values;
4. map only the snapshot after a synthetic Contracts canary proves the destination type and value;
5. reconcile accounting amounts separately with Books; and
6. block request/send on any error.

## 11. Books, Contracts, and Sign capability boundary

| Product | Verified in this audit | Not verified or changed |
|---|---|---|
| Zoho Books | The default active `GH Real Estate` organization is USD and live. | No customer, invoice, payment, credit, deposit, item, tax, field map, or sync record was read or changed. |
| Zoho Contracts | CRM contains extension module metadata for `zohocontracts__Contracts`. | No Contracts MCP administration surface was available. No extension, button, related list, counterparty, field mapping, contract type, template, request, or publication was verified or changed. |
| Zoho Sign | None through the available MCP servers. | No recipient roles, routing, fields, template, request, send, or signed-document return was verified or changed. |

Zoho Books remains the accounting source of truth. CRM amounts are approved operational/contract snapshots, not evidence of invoices, balances, payments, or deposits.

The Residential Lease Agreement remains Draft only, unpublished, execution-blocked, attorney-review-required, and unsent. Repository governance does not close its production gates or deploy it.

## 12. Applied professional layout organization

The changed sections and field placements below were returned by final layout readback. Modules may retain additional standard, integration, or system sections that were not changed.

| Module | Final changed or created sections |
|---|---|
| Contacts | `General & System Fields`; `Contact Identity & Role`; `Communication & Consent`; `Current Tenancy`; `Portal & Integrations` |
| Properties -- API `Accounts` | `General & System Fields`; `Property Identity & Status`; `Address & Notice`; `Management & Maintenance`; `Leasing & Integrations` |
| Units | `Occupancy & Current Tenancy`; `Rent & Availability`; `Zillow Listing & Routing`; `Files & Integrations`; renamed `System Ownership & Audit` |
| Rental Applications -- API `Deals` | renamed main section `Pipeline, Decision & System Controls`; `Application Identity`; `Application Intake`; `Integrations` |
| Maintenance Requests -- API `Cases` | `Request Identity`; `Relationships`; `Access & Scheduling`; `Files & Evidence`; renamed `Issue Description & Notes`; `Resolution`; `Comments` |
| Inspections | renamed main section `System Ownership & Audit`; `Inspection Identity`; `Timing & Responsibility`; `Issues & Follow-Up`; `Documents & Signatures` |
| Leases | renamed `Legacy & System Fields`; renamed `Legacy Rent Fields - Unresolved`; First Full Month Base Rent Amount placed in existing `Initial Amounts` |
| Vendors | renamed `Vendor Identity & Classification`; renamed `Utility Account References` |
| Tasks | `Routing & Handoff`; renamed `Description` |
| Storage Units | `Relationships`; renamed `Rental Terms & Status`; renamed `Condition & Access` |
| Utilities | renamed `Utility Identity & Legacy Fields`; `Authoritative Relationships` |
| Condition Reports | `Relationships`; renamed `System Ownership & Audit` |

Protected-module layouts were untouched. Contracts extension, Books, system audit, and security-sensitive fields were not mixed into ordinary operational sections merely to reduce section count. Existing active layout-rule triggers and actions were preserved.

## 13. Bounded write procedure and final readback

The following procedure was used for the applied batches and remains required for future module work:

1. Reconfirm `GH Real Estate` / `production` through the write-capable MCP server.
2. Read the module, fields, layouts, profile permissions, global associations, layout rules, and workflows.
3. Capture a sanitized exact before-state: field label/API/type, tooltip, required/unique/default/history, picklist pairs/order/colors, lookup target, profile permissions, section/order, and active dependencies.
4. Search for equivalent semantics and API-name conflicts.
5. Apply one small reversible batch. Respect connector limits.
6. Immediately read back the same metadata through the independent audit server.
7. Compare actual API names, types, precision, lookup targets, tooltips, permissions, choices, order, defaults, history, section placement, and rules.
8. Stop on any difference. Do not continue into another module.
9. Update the governed CSV and this ledger only from readback.
10. Run both CRM validators and the CRM tests.

Final readback confirmed:

- all 83 custom fields by actual API name and type, including every lookup target;
- the two `GH_Lifecycle_Status` associations and exact three-value order;
- additive Cases and Tasks standard-choice values with legacy values preserved;
- the final changed sections and field placements in section 12;
- the Utilities legacy label changes without API/type conversion;
- Vendor Username/Password containment remained enforced; and
- zero field/layout changes to Leads, Property Assets, Pets, or Vehicles.

Do not use record creation as a smoke test for metadata work unless a separate sanitized-record test is expressly authorized and includes cleanup/rollback.

## 14. Rollback requirements

Rollback must preserve records and must use authoritative before-state evidence.

| Change class | Rollback control |
|---|---|
| 83 created fields | Remove from active layouts and retire only after dependency/value audit. Do not delete fields or clear record data. |
| Field move or section relabel | Restore exact prior section/order from Setup Audit Log or an authorized before-state export. Never guess. |
| Cases/Tasks standard picklist addition | Preserve historical values; deactivate only the exact introduced values after workflow/report dependency review. Restore prior order/default/history only from authoritative evidence. |
| New local picklist | Remove from active layouts and retire with its field after dependency/value audit; do not delete values that may have record history. |
| `GH_Lifecycle_Status` association | Detach only after dependent fields/modules are enumerated. Remove the global set only after both associations are safely removed and no other dependency exists. |
| Utilities legacy relabel | If rollback is approved, restore API `Property` label to Property and API `Unit` label to Units. Do not change either API, type, or value. |
| Profile permission | Restore only with explicit data-owner/security approval and exact prior permission evidence. |
| Vendor credential containment | Do not re-expose as routine rollback. Rotate/migrate credentials first; any temporary access is separately authorized and audited. |
| Repository change | Revert the focused commit. A Git revert does not undo live CRM metadata. |

The exact pre-change placement for seven legacy Lease fields moved during the earlier bounded build was not retained in the sanitized repository. An exact rollback must use Zoho Setup Audit Log, an authorized configuration export, or retained session evidence. Do not reconstruct it from the target layout.

## 15. Prior open-risk reconciliation

This table carries forward each previously reported item without overstating completion.

| Earlier item | Current disposition |
|---|---|
| Normalized/paraphrased or overly thin tooltip prose | Still requires an update-capable supported path and exact tooltip readback. The catalog preserves the current live text. Remediate at least Inspections `Unit` ("Unit."), `Property` ("Property."), `Lease` ("Parent lease."), Maintenance Requests `Unit` ("Unit."), Tasks `Task_Category` ("Custom field."), and the thin Vendor assignment/contact tooltips with source, edit, required-stage, and integration guidance. |
| Deals Stage stale/misaligned values | Still blocked. Section 7 records the Stage/Pipeline/rule conflict and required resolution evidence. |
| Lease Status order/default/required | Still unenforced. Values/colors/history do not prove the requested order, default Draft, or mandatory behavior. |
| Lease Number and rent/initial-amount concepts | First Full Month Base Rent Amount now exists as Currency(2). Lease Number format, `Monthly_Rent`/`Prorated_Rent` semantics, the total-due equation, copy automation, dependencies, and Contracts canary remain blocked. |
| Current-tenancy convenience fields | Contact and Unit current-lease/unit/end-date/base-rent fields exist but no idempotent synchronization workflow was created. Treat them as non-authoritative until a separately tested automation owns updates and reconciliation. |
| Consent and signature checkboxes | `Email_Operational_Consent` and `SMS_Operational_Consent` have no source/timestamp/revocation evidence and are not marketing-consent proof. `Tenant_Signed` and `Landlord_Signed` have no Zoho Sign evidence integration and are not signature or enforcement proof. These are manual operational flags only. |
| Creator reference fields | `Zoho_Creator_Application_ID` and `Creator_Ticket_ID` are optional Single Line fields without verified uniqueness. Do not use either as a sole upsert or idempotency key until normalization, uniqueness, collision handling, and duplicate recovery are implemented and read back. |
| Lost pre-change placement for seven moved fields | Exact rollback remains unavailable from sanitized repository evidence and must not be guessed. |
| Residential Lease Agreement | Still Draft only, unpublished, execution-blocked, attorney-review-required, and unsent. |
| Contracts extension/mapping/button/signers/request/send | Not attempted or verified through this MCP-only audit. |

## 16. Completion criteria

The approved CRM metadata/layout scope is complete: 83 fields, one global picklist with two associations, additive standard choices, the documented layout organization, Utilities relabels, and Vendor containment were read back; protected modules were untouched.

The broader cross-suite lease system is not complete. Its remaining gates are:

- keep the live uncolored/default/history variances documented unless a later supported change applies and reads back approved controls;
- remediate the earlier normalized/paraphrased tooltips through an update-capable supported path;
- reconcile Lease Status order/default/required controls;
- give Deals Stage/Pipeline a separately approved migration or keep it blocked;
- approve the Lease Number format and the unresolved monthly/prorated amount semantics;
- make the Lease amount equation and snapshot automation pass missing-input, non-applicable, negative-total, mismatch, duplicate-run, and partial-failure tests;
- prove destination mapping through a synthetic Contracts canary without publishing or sending;
- prove Books reconciliation without copying accounting truth into CRM incorrectly; and
- recover authoritative pre-change evidence before any exact layout rollback.

Repository publication also requires both CRM validators, the CRM tests, compilation, formatting checks, and branch checks to pass.
