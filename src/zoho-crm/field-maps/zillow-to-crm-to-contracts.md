# Zillow to Zoho CRM to Zoho Contracts Field Map

Use sanitized examples only. Do not store real applications, screening reports, IDs, pay stubs, or tenant documents in GitHub.

## Intake Rule

Zillow is the listing inquiry source. Zoho CRM owns the operational pipeline after intake.

The Zillow lead intake service creates or updates only:

- `Leads` for the raw Zillow prospect inquiry

It does not create `Contacts`, rental application pipeline records, leases, Books records, tenant portal access, or WorkDrive folders. Those records are created later by the approved qualification, application, and lease workflow.

A Zillow inquiry is a prospect, not a tenant and not yet an applicant record with verified screening, owner approval, or lease terms.

## CRM Lead Field Map

| Zillow source field | CRM module | Verified CRM API field | Contracts merge field | Notes |
|---|---|---|---|---|
| Parsed first name from `name` | Leads | `First_Name` | None | Parsed from Zillow renter name. |
| Parsed last name from `name` | Leads | `Last_Name` | None | Required by Zoho Leads. Uses `Zillow Prospect` only if name is missing. |
| System company value | Leads | `Company` | None | Hidden from layout is fine. API still populates because Zoho may require it. |
| `email` | Leads | `Email` | None | Used for follow-up, not as primary duplicate key. |
| `phone` | Leads | `Mobile` | None | Zillow sends one phone value; GH layout uses Mobile as the primary phone field. |
| Secondary/alternate phone if supplied | Leads | `Phone` | None | Zillow's current guide does not list this, but the runtime supports common alternate phone aliases for future compatibility. |
| Fixed value `Zillow` | Leads | `Lead_Source` | None | Set to `Zillow`. |
| Intake default | Leads | `Lead_Status` | None | Use `New Zillow Inquiry`. |
| Property lookup from routing map | Leads | `Requested_Property` | None | Optional lookup resolved from property/unit map. |
| Unit lookup from routing map | Leads | `Requested_Unit` | None | Optional lookup resolved from property/unit map. |
| `movingDate` | Leads | `Requested_Move_In_Date` | None | Zillow format is `YYYYMMDD`; CRM stores Date. |
| `message` plus `introduction` | Leads | `Inquiry_Message` | None | Text blob from Zillow lead form. |
| Optional renter profile fields | Leads | `Zillow_Renter_Profile_Summary` | None | Multi-line/rich-text summary; do not overbuild raw lead fields. |
| Generated key | Leads | `Zillow_Lead_Key` | None | Mark unique. Used for idempotent upsert. |
| Source lead ID if supplied | Leads | `Zillow_Lead_ID` | None | Optional compatibility field. |
| `listingId` | Leads | `Zillow_Listing_ID` | None | Strongest Zillow routing key. |
| Source URL if supplied | Leads | `Zillow_Listing_URL` | None | Optional link field. |
| `leadType` | Leads | `Zillow_Lead_Type` | None | Values: `question`, `tourRequest`, `applicationRequest`. |
| `providerModelId` | Leads | `Zillow_Provider_Model_ID` | None | Useful for multi-family/floorplan routing. |
| `moveInTimeframe` | Leads | `Zillow_Move_In_Timeframe` | None | Values: `asap`, `flexible`, `week`, `month`, `twoWeeks`, `twoMonths`. |
| Combined listing address | Leads | `Zillow_Property_Address_Raw` | None | Raw/composed listing address. |
| `listingStreet` | Leads | `Zillow_Listing_Street` | None | Listing street address. |
| `listingUnit` | Leads | `Zillow_Listing_Unit` | None | Listing unit number. |
| `listingCity` | Leads | `Zillow_Listing_City` | None | Listing city. |
| `listingState` | Leads | `Zillow_Listing_State` | None | Listing state code. |
| `listingPostalCode` | Leads | `Zillow_Listing_Postal_Code` | None | Store as text to preserve formatting. |
| `listingContactEmail` | Leads | `Zillow_Listing_Contact_Email` | None | Useful for account/routing diagnostics. |
| Endpoint receipt timestamp | Leads | `Zillow_Received_At` | None | Date-Time. |
| Last processing timestamp | Leads | `Last_Zillow_Sync_At` | None | Date-Time. |
| Technical intake status | Leads | `Zillow_Intake_Status` | None | Received, Updated, Routing Matched, Routing Unmatched, Test Callback, Failed. |
| Payload hash | Leads | `Zillow_Source_Payload_Hash` | None | Audit/debug hash only. |
| Received field names | Leads | `Zillow_Raw_Field_Keys` | None | Stores keys received, not raw private payload values. |
| Payload storage flag | Leads | `Zillow_Raw_Payload_Stored` | None | Checkbox. Leave false unless raw payloads are stored in an approved secure system. |
| Intake summary | Leads | `Description` | None | Sanitized operational summary for CRM users. |

Do not use `Desired_Rent`, `Desired_Deposit`, `Manual_Review_Required`, or `Manual_Review_Reason` for the Zillow intake. GH Real Estate manually reviews every lead through Lead Status/views, and approved rent/deposit come from property, unit, application, and lease records.

## Governed promotion architecture

Promotion is a sequence of durable records, not one record changing meaning:

```text
Zillow Inquiry
-> Lead (`Leads`)
-> Contact (`Contacts`) + Rental Application (`Deals`)
-> approved Rental Application
-> separate Lease (`Leases`)
-> Request Contract from Lease
-> Zoho Contracts
-> Zoho Sign
-> signed status/PDF related back to Lease
-> Books and portal activation as later workflows
```

| Stage | Record owner | Control |
|---|---|---|
| Raw inquiry | `Leads` | Zillow/Catalyst may create/update only the Lead. |
| Qualified person | `Contacts` | Confirm identity and contact channels before conversion. |
| Application and screening | Rental Applications, API `Deals` | Standard `Stage` plus the verified decision/approval fields own review. Sensitive evidence stays in approved Zoho systems. |
| Approved contract inputs | Leases, API `Leases` | Create a separate Lease and freeze the approved relationships, dates, premises, charges, additional tenants, and controls. |
| Drafting and lifecycle | Zoho Contracts | Request from the Lease only after every readiness/legal gate is satisfied. |
| Signature evidence | Zoho Sign | Recipients are configured separately from Party C/D document fields. |
| Accounting | Zoho Books | Invoices, payments, balances, deposits, and accounting truth are never derived from raw Zillow inquiry values. |
| Tenant access | Tenant app/portal | Activate later under a separate approved onboarding workflow. |

The approved Application-to-Lease automation is not deployed. No reusable workflow task was verified, and the current approved CRM tool surface cannot enumerate or create the durable custom function/button. Do not use a one-time record create as a substitute.

## Approved Application to Lease crosswalk

Only an approved Rental Application should supply a new Lease. The actual API names below were verified through production metadata/readback on July 24, 2026.

| Rental Application source | API | Lease destination | API | Status/control |
|---|---|---|---|---|
| Contact Name (primary applicant) | `Contact_Name` | Tenant (primary-tenant role) | `Tenant` | Reuse standard/live lookups; live Lease label is `Tenant`, not Primary Tenant. |
| Account Name (Property) | `Account_Name` | Property | `Property` | Reuse standard Deals relationship; target lookup is `Accounts`. |
| Unit | `Unit` | Unit | `Unit` | Verified lookup to `Units`. |
| Source Lead | `Source_Lead` | None | -- | Preserve application provenance; do not map to Contracts. |
| Co-Applicant 1 | `Co_Applicant_1` | Tenant 2 | `Tenant_2` | Copy only when applicable; populate verified name/email snapshots before contract request. |
| Co-Applicant 2 | `Co_Applicant_2` | Tenant 3 | `Tenant_3` | Copy only when applicable; populate verified name/email snapshots before contract request. |
| Approved Security Deposit | `Approved_Security_Deposit` | Security Deposit | `Security_Deposit` | Approved Lease snapshot only; Books remains accounting truth. |
| Approved Lease Commencement Date | `Approved_Lease_Commencement_Date` | Lease Start Date | `Lease_Start_Date` | Distinct from Lease `Agreement_Date`. |
| Approved Lease Term End Date | `Approved_Lease_Term_End_Date` | Lease End Date | `Lease_End_Date` | Required for fixed terms. |
| Approved Possession Date | `Approved_Possession_Date` | Move-In Date | `Move_In_Date` | Possession snapshot; not automatically a Contracts destination. |
| Addenda Required | `Addenda_Required` | Addenda Required | `Addenda_Required` | Workflow/packet control; not itself legal-text automation. |
| Nonstandard Terms? | `Nonstandard_Terms` | Nonstandard Terms? | `Nonstandard_Terms` | Requires review; do not request/send while unresolved. |
| Nonstandard Terms Notes | `Nonstandard_Terms_Notes` | Nonstandard Terms Notes | `Nonstandard_Terms_Notes` | Copy only with authorized approved wording. |
| Attorney Review Required? | `Attorney_Review_Required` | Attorney Review Required? | `Attorney_Review_Required` | A true value blocks contract use/sending. |
| Approved base rent | Standard `Amount` was not approved for this meaning | Base/Total Monthly Rent | Existing `Monthly_Rent` is ambiguous | Blocked; the active Big Deal Rule depends on Amount/Probability. Reconcile before mapping. |

The Lease must copy premises values into the verified `Premises_*` snapshot fields before a contract request. Related Property/Unit values are operational sources, but the generated agreement must not depend on later mutable address/unit changes.

## Lease to Contracts handoff

- Zoho Contracts extension setup is manual and not yet performed.
- Use the verified Lease module API `Leases` and the live primary-tenant lookup label/API `Tenant`/`Tenant`.
- Map Contacts Full Name (`Full_Name`) to Contracts Contact Name and Contacts Email (`Email`) to Contracts Contact Email Address.
- Party B Address is the counterparty address, not the premises. Never map Premises State to Party B Jurisdiction; that meaning remains unresolved.
- Party C/D Contact Name document fields do not create Tenant 2/Tenant 3 signer recipients.
- Preserve GH process labels R1 Primary Tenant, R2 Tenant 2, R3 Tenant 3, and R4 GH landlord. Configure the actual Zoho signing order contiguously for signers present and keep GH last; optional tenants are later Add Signers, not conditional type-level defaults.
- Do not guess the custom Request Contract button URL tokens.
- Do not request a contract, publish the Residential Lease Agreement, or send a signature request while any production gate is open.

Follow the exact [manual Leases extension runbook](../../zoho-contracts/runbooks/crm-leases-extension-manual-deployment.md). Production CRM readback and rollback evidence are in the [Lease-system reconciliation](../../../docs/runbooks/zoho-crm-lease-system-reconciliation.md).
