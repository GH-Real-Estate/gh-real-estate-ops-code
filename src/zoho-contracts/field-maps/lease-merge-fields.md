# Lease Merge Fields

The canonical field inventory and cross-application type map is [contract-field-registry.md](contract-field-registry.md). Its machine-readable source is `contract-field-registry.json`. The Residential Lease document mapping remains [`document-field-map.json`](../contract-types/residential-lease-agreement/document-field-map.json).

Do not maintain a competing field catalog here. This page records the verified CRM Lease source fields and the manual Contracts mapping boundary as of July 24, 2026.

## Verification boundary

- CRM custom-module API `Leases` and the CRM source APIs below were verified through production metadata/readback.
- Zoho Contracts contract-type API names were not available through the approved connectors and remain null/unverified in the governed mapping.
- No Contracts extension, button, related-list, counterparty, field mapping, template, signer, or contract-request change was made.
- The Residential Lease Agreement remains Draft only, unpublished, execution-blocked, attorney-review-required, and unsent with all 29 production gates open.

## Parties and relationships

| Merge concept | Verified CRM source | Governed Contracts treatment | Current status |
|---|---|---|---|
| Primary tenant | Lease Tenant -- `Tenant` -- lookup to `Contacts` | Party B counterparty; Contact Name from `Full_Name`; Contact Email Address from `Email` | Manual extension mapping. Live CRM label is `Tenant`, not Primary Tenant. |
| Tenant 2 | `Tenant_2` plus `Tenant_2_Legal_Name_Snapshot` and `Tenant_2_Email_Snapshot` | Party C Contact Name document field; GH process role R2 must be added manually at the contract's Add Signers step when present and authorized | CRM verified; Contracts mapping/routing manual. |
| Tenant 3 | `Tenant_3` plus `Tenant_3_Legal_Name_Snapshot` and `Tenant_3_Email_Snapshot` | Party D Contact Name document field; GH process role R3 must be added manually at the contract's Add Signers step when present and authorized | CRM verified; Contracts mapping/routing manual. |
| Landlord | No CRM mirror | Party A Organization Info for GH Real Estate, LLC | Must be verified in Contracts; authorized signer remains an open gate. |
| Property relationship | `Property` -- lookup to `Accounts` | Operational source for premises snapshots | CRM verified; not Party B address/jurisdiction. |
| Unit relationship | `Unit` -- lookup to `Units` | Operational source for apartment-number snapshot | CRM verified. |

Party C/D document fields do not create Zoho Sign recipients. GH process labels remain R1 Primary Tenant, R2 Tenant 2, R3 Tenant 3, and R4 GH landlord; these are not documented Zoho tokens. Actual Zoho signing order must be contiguous for the people present, with GH last. Only the counterparty primary contact can be the default counterparty-representative signer; optional tenants are added later through the contract's Add Signers step when authorized.

## Lease and premises snapshots

| Merge concept | Verified CRM Lease API | Intended Contracts destination label | Status/control |
|---|---|---|---|
| Lease record name | `Name` | Agreement Name, if verified equivalent | Manual mapping; do not infer a Contracts API. |
| Lease number | -- | Lease Number | Blocked: auto-number prefix/format not approved. |
| Agreement date | `Agreement_Date` | Agreement Effective Date | CRM source verified; exact destination label-only evidence uses `Agreement Effective Date`, but its Contracts API remains unverified. |
| Lease commencement | `Lease_Start_Date` | Lease Agreement Effective Date | CRM reuse verified; Contracts destination/API and legal gate remain open. |
| Fixed-term end | `Lease_End_Date` | Term End Date | CRM reuse verified; fixed-term validation still required. |
| Possession/move-in | `Move_In_Date` | No direct mapping unless template requires it | CRM reuse verified. |
| Premises street | `Premises_Street_Line_1` | Property Street Line 1 | CRM verified; manual mapping. |
| Premises apartment | `Premises_Apartment_Number` | Property Apartment Number | CRM verified; manual mapping. |
| Premises city | `Premises_City` | Property City | CRM verified; manual mapping. |
| Premises state | `Premises_State` | Property State | Never map to Party B Jurisdiction. |
| Premises ZIP Code | `Premises_ZIP_Code` | Property Zip Code | Text snapshot; manual mapping. |

Party B Address means the counterparty address, not the premises. Party B Jurisdiction remains unresolved and must not receive Property/Premises State.

## Charges and initial amounts

CRM Lease fields are approved transaction snapshots only. Zoho Books remains authoritative for invoices, payments, balances, deposit liabilities, and payment evidence.

| Merge concept | Verified CRM Lease API | Intended Contracts destination label | Current status |
|---|---|---|---|
| Base Rent Amount | Existing `Monthly_Rent` is ambiguous | Base Rent Amount | Blocked; reconcile existing semantics before reuse or creation. |
| Total Monthly Rent Amount | Existing `Monthly_Rent` is ambiguous | Total Monthly Rent Amount | Blocked; do not create a duplicate. |
| Security Deposit Amount | `Security_Deposit` | Security Deposit Amount | CRM reuse verified; Contracts mapping/Books liability control remain open. |
| Total Monthly Pet Rent Amount | `Total_Monthly_Pet_Rent_Amount` | Total Monthly Pet Rent Amount | CRM verified; pet approval/addendum gate remains open. |
| Base Storage Unit Rent Amount | `Base_Storage_Unit_Rent_Amount` | Base Storage Unit Rent Amount | CRM verified; storage applicability/term/addendum gate remains open. |
| Total Monthly Storage Rent Amount | `Total_Monthly_Storage_Rent_Amount` | Total Storage Unit Rent Amount | CRM verified; destination label/API must be verified live. |
| Next Total Monthly Rent Due Date | `Next_Total_Monthly_Rent_Due_Date` | Next Total Monthly Rent Due Date | CRM verified; initial-amount equation remains open. |
| Prorated Rent Start Date | `Prorated_Rent_Start_Date` | Prorated Rent Start Date | CRM verified; use only when approved proration applies. |
| Prorated Rent End Date | `Prorated_Rent_End_Date` | Prorated Rent End Date | CRM verified; use only when approved proration applies. |
| Prorated Base Rent Amount | Existing `Prorated_Rent` is ambiguous | Prorated Base Rent Amount | Blocked; reconcile semantics before mapping. |
| Pet Security Deposit Amount | `Pet_Security_Deposit_Amount` | Pet Security Deposit Amount | CRM verified; do not treat as a fee. |
| Prorated Pet Rent Amount | `Prorated_Pet_Rent_Amount` | Prorated Pet Rent Amount | CRM verified; proration/rounding remains gated. |
| Prorated Storage Unit Rent Amount | `Prorated_Storage_Unit_Rent_Amount` | Prorated Storage Unit Rent Amount | CRM verified; storage/proration gates remain open. |
| Holding Deposit Credit Applied | `Holding_Deposit_Credit_Applied` | Holding Deposit Amount | CRM verified; credit semantics and Books evidence remain gated. |
| Total Due Before Possession | `Total_Due_Before_Possession` | Total Due Before Possession | CRM verified but must not be used until the complete equation is approved. |
| First Full Month Base Rent Amount | -- | First Full Month Base Rent Amount | Confirmed field/equation gap; blocked. |

## Contract controls

The verified CRM controls `Addenda_Required`, `Nonstandard_Terms`, `Nonstandard_Terms_Notes`, and `Attorney_Review_Required` govern readiness/review. They are not permission to alter clauses, select an unapproved addendum automatically, publish, request a contract, or send an envelope.

A late-fee clause reference remains a governed template/clause decision, not a free-form transaction field. Do not duplicate lease fee logic in the merge map.

## Source and sync rules

- Zoho CRM owns approved pre-authoring relationships and frozen contract-request inputs.
- Zoho Contracts owns contract lifecycle state and the resolved agreement snapshot.
- Zoho Sign owns recipients, signatures, and signing evidence.
- Zoho Books owns financial truth.
- Use only tenant-returned Contracts `apiName` values and verified CRM API fields in an active mapping. A visible Contracts label or proposed registry name is not a deployable API identifier.
- Prefer one-way CRM-to-Contracts generation. Never overwrite an executed agreement from mutable CRM data.
- Keep signed leases and tenant-specific merged values out of GitHub.

## Production gate

Before any mapping is activated or used:

1. Reconcile the exact contract type through the Contracts `/allfields` metadata endpoint.
2. Follow the [manual Leases extension runbook](../runbooks/crm-leases-extension-manual-deployment.md), including counterparty and signer separation.
3. Resolve every applicable `review_required` entry and every Residential Lease production gate.
4. Reconcile Base Rent, Total Monthly Rent, Prorated Base Rent, First Full Month Base Rent, and Total Due Before Possession as one auditable equation.
5. Run the registry and Residential Lease validators and sanitized regression tests.
6. Render and manually compare a synthetic Draft preview against the approved source.
7. Do not publish or request/send a contract while the implementation remains blocked.

Merging this documentation does not create fields or deploy a Zoho integration.
