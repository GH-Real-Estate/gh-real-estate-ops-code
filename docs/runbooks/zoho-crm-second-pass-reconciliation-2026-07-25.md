# Zoho CRM Second-Pass Reconciliation — July 25, 2026

**Runbook ID:** GH-ZOHO-CRM-RECON-2026-07-25

**Status:** Bounded production metadata/layout work completed and read back

**Tool boundary:** Approved MCP servers only; no Browser control

**Data boundary:** No CRM records, applicant/tenant PII, documents, screening
data, credentials, or financial transactions were read or changed

## 1. Purpose

This second pass resolves the bounded layout and application-intake changes
that could be applied and verified safely after the July 24 production
reconciliation. It also records the approved target architecture for Rental
Applications, Leases, Properties, Zillow-related data, and the operations
dashboard.

Repository documentation governs future implementation and review. It does
not prove that a target marked deferred is live.

## 2. Source-of-truth order

Use this precedence when evidence conflicts:

1. current production metadata returned and read back through an approved MCP;
2. reviewed production integration code and runbooks;
3. the governed CRM field catalog;
4. screenshots, workbooks, and historical proposals;
5. clearly labeled architecture recommendations.

Zoho Books owns invoices, payments, credits, deposits, balances, and actual
income. Leases owns contractual tenancy and approved lease-charge snapshots.
Rental Applications owns application review and proposed/approved terms.

## 3. Completed live changes and readback

Every change below was applied through the approved CRM configuration MCP and
was followed by metadata or layout readback.

### 3.1 Contacts — API `Contacts`

The following fields were removed non-permanently from the active Contacts
layout:

- API `Name1`
- API `F_Name`
- API `L_Name`
- API `Parent_Property`
- API `Account_Type`
- API `Current_Lease`
- API `Current_Unit`

Final layout readback found none of those APIs present. No field was deleted,
and no Contact record or field value was read.

This removes redundant or stale layout inputs without pretending that an
unverified current-tenancy snapshot is authoritative. Leases remains the
tenancy-history source.

### 3.2 Properties — standard Accounts module, API `Accounts`

The inherited hierarchy field API `Parent_Account` was removed
non-permanently from the active Properties layout. Final readback found it
absent.

Two sections were renamed and read back exactly:

- `Property Address & Legal Notice`
- `Owner & Emergency Contact`

No standard field was deleted. The revised labels describe the actual purpose
of the retained physical-address, notice-contact, owner, and emergency-contact
fields without implying that GH Real Estate currently uses a third-party
property manager.

### 3.3 Rental Applications — standard Deals module, API `Deals`

Two whole-number intake fields were created, placed in `Application Intake`,
and read back:

| Field Label — Field Type | Actual API name | Base required | Conditional behavior |
|---|---|---:|---|
| Requested Pet Count — Number | `Requested_Pet_Count` | No | Show and require when `Pets_Requested` is selected |
| Requested Storage Unit Count — Number | `Requested_Storage_Unit_Count` | No | Show and require when `Storage_Requested` is selected |

Both active layout rules were read back with show-and-mandatory behavior. The
base field remains optional so that the conditional rule, not a global
mandatory setting, governs applicability.

When shown, each count must be a whole number of at least one. The available
layout-rule MCP enforced presence but did not expose a safely verifiable
minimum-value constraint. Until a supported validation rule is deployed,
operators must reject zero or negative values during application review.

The counts represent application-stage requests:

- `Requested_Pet_Count` counts ordinary pets for which approval is requested;
  it must not be used to classify an assistance-animal request.
- `Requested_Storage_Unit_Count` records requested quantity, not an assignment
  of a specific storage record.
- A later approved workflow may create or associate specific Pet and Storage
  records only after the protected-Pets relationship design and storage
  assignment rules are separately approved.

The existing `Pets_Requested` and `Storage_Requested` checkboxes remain live.
Do not create a second manual writer for the same fact. A future workflow must
either derive the checkbox from a count or retire the checkbox after dependency
and data review.

### 3.4 Protected modules

The following production modules remained metadata-audit/documentation-only
and were not changed:

- Leads — API `Leads`
- Property Assets — API `Equipment`
- Pets — API `Pets`
- Vehicles — API `Tenant_Vehicles`

## 4. Rental Applications pipeline decision

Use one Deals pipeline named `Rental Applications`. Do not carry showing,
contract drafting, signature, move-in, or active-tenancy lifecycle into the
application pipeline.

Target Stage scope: standard Deals Stage

Default: `Application Received`

History tracking: enabled

Sort: entered order

| Order | Exact target Stage | Category | Probability | Color | Transition evidence |
|---:|---|---|---:|---|---|
| 1 | Application Received | Open | 10% | `#2563EB` | A completed application record exists |
| 2 | Screening In Progress | Open | 35% | `#D97706` | Authorized screening/review has started |
| 3 | Decision Pending | Open | 60% | `#EA580C` | Required review is complete and a decision is pending |
| 4 | Approved - Lease Pending | Open | 90% | `#16A34A` | `Decision` is Approved or Approved with Conditions and approved terms are complete |
| 5 | Lease Created | Closed Won | 100% | `#16A34A` | A separate Lease exists and links to the Rental Application |
| 6 | Closed - Not Proceeding | Closed Lost | 0% | `#DC2626` | `Decision` records Denied, Withdrawn, Duplicate, or No Response |

The verified local `Decision` field retains the detailed outcome. Stage
represents the broad operating state and must not duplicate decision reasons.

### Live Stage and Pipeline status

No Stage or Pipeline write was attempted in this second pass.

The current live configuration remains unsafe to migrate additively:

- Stage display values map to stale or unrelated underlying actual values;
- display `Move-In Scheduled` maps to an underlying Closed Lost value;
- the Pipeline display `Rental Applications` maps to an underlying
  `Lease Agreement` value;
- an active loss-reason rule depends on the Closed Lost category; and
- an active Big Deal rule depends on `Amount` and Probability.

The available MCP surface cannot rewrite and read back the complete pipeline,
categories, probabilities, rules, reports, and existing-record transitions as
one reversible operation. The six-stage definition is therefore the approved
target, not a claim of live deployment.

Before migration:

1. obtain a complete before-state through an approved metadata MCP;
2. enumerate every Stage, Pipeline, probability, category, rule, Blueprint,
   report, dashboard, and integration dependency;
3. approve an old-to-new record transition map;
4. require an actual linked Lease before setting `Lease Created`;
5. migrate through a supported MCP; and
6. read back every definition and regression-test dependent behavior.

## 5. Lease lifecycle decision

Do not create a second Deals-style pipeline for the custom Leases module.
Lease records persist through drafting, signature, occupancy, ending, and
archive. One governed local `Lease_Status` picklist plus controlled transitions
is the simpler source of truth.

Target default: `Draft`

Target required: yes

Target history tracking: enabled

Target sort: entered order

| Order | Exact target value | Color |
|---:|---|---|
| 1 | Draft | `#2563EB` |
| 2 | Ready For Contract | `#7C3AED` |
| 3 | Contract Requested | `#7C3AED` |
| 4 | Sent For Signature | `#7C3AED` |
| 5 | Signed - Pending Move-In | `#D97706` |
| 6 | Active | `#16A34A` |
| 7 | Month-to-Month | `#2563EB` |
| 8 | Ended | `#6B7280` |
| 9 | Terminated | `#DC2626` |
| 10 | Cancelled | `#6B7280` |
| 11 | Archived | `#6B7280` |

Target consolidation:

| Current/legacy concept | Target treatment |
|---|---|
| Contract in Progress; Contract Drafting | `Contract Requested` |
| Draft Lease Data | `Draft` |
| Signed - Future | `Signed - Pending Move-In` |
| Lease Active | `Active` |
| Expired; Moved Out | `Ended` |
| Renewal Pending; Non-Renewing | Separate Renewal Status workflow |
| Notice Given | Separate Notices workflow |

No Lease Status value, order, default, mandatory flag, history setting, rule,
or record was changed in this second pass. Existing records must not be
reclassified from labels alone.

## 6. Contacts retirement decision

The seven Contacts fields were removed from the active layout, not permanently
deleted. That is the correct first retirement step because field deletion
without a dependency and value-retention audit can break reports, functions,
integrations, layout rules, or historical interpretation.

Continue to reuse standard identity fields:

- `First_Name`
- `Middle_Name`
- `Last_Name`
- `Full_Name`
- `Email`
- `Mobile`
- `Phone`
- `Other_Phone`

Keep the following duplicate proposals prohibited:

- `Secondary_Phone`
- `Legal_First_Name`
- `Legal_Middle_Name`
- `Legal_Last_Name`
- `Zoho_Contracts_Counterparty_ID` on Contacts

Do not reintroduce current Lease, Unit, Property, move-in, or move-out
snapshots until one tested, idempotent synchronization owner and reconciliation
process exist.

## 7. Properties and relationship decisions

### 7.1 Parent/child model

For the present portfolio model:

- one Property record represents the building;
- Units are children through verified lookup API `Units.Property`; and
- the standard Accounts hierarchy field `Parent_Account` is not needed on the
  active Property layout.

This does not delete the inherited standard field or prevent a future
multi-property hierarchy.

### 7.2 Address, notice, ownership, and maintenance

Retain the property address because it supplies the premises/building identity
for Leases, Contracts preparation, reporting, and current or future Zillow
listing work.

Retain the owner, legal-notice contact, and emergency-maintenance contact
concepts even while GH Real Estate is self-managed. They should contain the
approved GH contact, not unnecessary duplicate property-manager fields.

Do not create separate Property Manager Name or Property Manager User fields.
Reuse the governed `Primary_Contact` and standard record `Owner` concepts.

### 7.3 Current Tenants and Tenant Pets subforms

No subform was changed in this second pass.

The existing `Tenants` and `Tenant_Pets` modules are generated subforms
parented to Accounts, not ordinary lookup-generated related lists.

- Current tenancy should be derived from governed Lease relationships and
  Lease status, not duplicated as an independently edited Property subform.
- A Property can use the Leases related list because Leases has verified
  Property, Unit, and tenant relationships.
- The protected Pets module currently has no governed Property, Unit, Lease,
  or Contact lookup that could generate the requested Property related list.

The Pets module cannot remain permanently unchanged while also gaining a new
lookup-generated Property related list. Preserve the protected-module boundary
and defer that relationship decision rather than silently creating a second
pet source of truth.

## 8. Zillow and listing-field decision

The current Catalyst Zillow integration is inbound Lead intake only. No
outbound Zillow listing feed, publisher, scheduled job, or live publication
control is deployed.

Keep the ownership boundary:

| Data | CRM owner |
|---|---|
| Building name, physical address, shared description, shared amenities, and shared photos | Property |
| Unit number, asking rent, bedrooms, bathrooms, square feet, unit amenities, availability, parking, storage, and unit-specific utility/lease terms | Unit |
| Occupancy and executed terms | Lease |
| Actual publication state | Zillow Rental Manager until an approved feed exists |

A Property-level `Active on Zillow?` field is too ambiguous when individual
units have different availability. If retained later, it must be a read-only
summary. Unit market status may start listing preparation but must never
publish without a separate authorized approval control.

## 9. Rent and income decision

Rental Applications may hold a proposed or approved monthly-rent term, but an
application is not income. The standard Deals `Amount` field was not
repurposed in this pass because its meaning and active Big Deal rule dependency
remain unresolved.

Use these labels precisely:

| Measure | Meaning | Source |
|---|---|---|
| Potential Monthly Rent | Application-stage opportunity value after `Amount` is formally reconciled | Rental Applications |
| Contracted Monthly Rent | Approved recurring contractual charge under an Active or Month-to-Month Lease | Leases |
| Actual Gross Rental Income | Accounting income supported by invoices, receipts, credits, and the accounting method | Zoho Books |

Do not sum open or duplicate Rental Applications as revenue. Do not infer
income from Unit rent defaults. Do not present refundable deposits as income.

## 10. Initial amounts and Contracts handoff

No change was made to:

- `Total_Due_Before_Possession`;
- any Lease Formula field;
- any calculation workflow or custom function;
- any Zoho Contracts mapping;
- any Zoho Sign mapping or signer configuration; or
- any contract request, publication, or signature send.

`Total_Due_Before_Possession` remains a Currency snapshot. Formula portability
to Contracts is not verified by the available MCP surface. The calculation
must remain blocked until the governed component fields and null/zero/credit
semantics are final and a synthetic Contracts mapping canary can be created
and read back without publication or sending.

See
[`../../src/zoho-contracts/field-maps/lease-initial-amounts-readiness.md`](../../src/zoho-contracts/field-maps/lease-initial-amounts-readiness.md)
for the fail-closed calculation and readiness gate.

## 11. Dashboard decision

The approved MCP surface has no Zoho CRM report or dashboard CRUD/readback
tool. No live dashboard or report was created.

The governed MCP-only target specification is:

[`../../src/zoho-crm/dashboards/gh-real-estate-operations-dashboard.md`](../../src/zoho-crm/dashboards/gh-real-estate-operations-dashboard.md)

It separates:

- CRM application pipeline value;
- Lease contracted rent; and
- Books actual income.

Do not use Browser control as a substitute. Deploy only when an approved MCP
can create and read back the reports, dashboard, components, filters, and
sharing controls.

## 12. Verification evidence

The second-pass readback confirmed:

- all seven selected Contact field APIs are absent from the active layout;
- `Parent_Account` is absent from the active Properties layout;
- the two new Properties section labels match exactly;
- both requested-count fields exist as integer/Number fields;
- both requested-count fields are in `Application Intake`;
- both corresponding layout rules are active and enforce show plus mandatory
  behavior when applicable; and
- the four protected modules remain outside the mutation scope.

Tenant-scoped Zoho organization, profile, layout, section, field, and rule
identifiers are intentionally omitted from this sanitized repository.

## 13. Deferred work

- Full Deals Pipeline and Stage migration, including record transition,
  probabilities, categories, rule dependencies, reports, and readback.
- Lease Status consolidation, order, default, mandatory behavior, and workflow
  controls.
- Permanent retirement of hidden Contacts fields after dependency and
  value-retention review.
- Positive-integer validation for both requested-count fields.
- Current Tenants/Tenant Pets subform retirement and the protected Pets
  relationship decision.
- A single authoritative Lease monthly-rent model.
- `Total_Due_Before_Possession` calculation and idempotent snapshot workflow.
- Zoho Contracts field-mapping canary and Zoho Sign evidence integration.
- Zoho CRM reports and the GH Real Estate Operations dashboard.
- Books reconciliation and any combined Zoho Analytics executive dashboard.

## 14. Rollback

Rollback must preserve records and avoid guessing:

### Contacts

1. Add `Name1`, `F_Name`, `L_Name`, `Parent_Property`, and `Account_Type` back
   to `General & System Fields`, and add `Current_Lease` and `Current_Unit`
   back to `Current Tenancy`, through an approved MCP.
2. Read back their presence and placement.
3. Do not delete or recreate the underlying fields.

### Properties

1. Add `Parent_Account` back to `General & System Fields` on the active
   Properties layout if the hierarchy field is again required.
2. Restore the prior section labels `Address & Notice` and
   `Management & Maintenance` if rollback is approved.
3. Read back the exact labels and field placement.

### Rental Applications counts

1. Deactivate the conditional show-and-mandatory rules.
2. Read back the inactive state.
3. Remove `Requested_Pet_Count` and `Requested_Storage_Unit_Count`
   non-permanently from the active layout.
4. Retire rather than immediately delete the fields until every report, rule,
   function, integration, and value-retention dependency is reviewed.
5. Preserve `Pets_Requested` and `Storage_Requested` unless a separately
   approved migration governs them.

### Repository

Revert the repository commit independently. A documentation rollback does not
roll back live Zoho metadata, and a live metadata rollback does not alter
GitHub.

## 15. Completion statement

The bounded second-pass layout and count-field work is complete and read back.
The six-stage Rental Applications model, 11-value Lease lifecycle, subform
cleanup, initial-amount calculation, and dashboard remain governed targets or
deferred work, not live completion claims.
