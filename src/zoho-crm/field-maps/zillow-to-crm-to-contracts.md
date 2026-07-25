# Zillow to Zoho CRM to Zoho Contracts Field Map

Use sanitized examples only. Do not store real applications, screening reports, IDs, pay stubs, or tenant documents in GitHub.

## Current-state answer

The operating Zillow/Catalyst integration creates or updates CRM Leads only. It does not:

- create or convert Contacts;
- create Rental Applications in the renamed Deals module;
- retrieve a completed Zillow rental application or screening reports;
- create Leases;
- request a Zoho Contract; or
- trigger CRM workflows, approvals, or blueprints under the documented production configuration.

The Zillow Lead API field `leadType=applicationRequest` is only an application-related lead signal. Zillow's public guide does not define it as a completed submission event, and the payload does not contain the complete application, credit report, background report, housing-court report, attachments, report IDs, or report URLs. Completed applications and reports remain in Zillow Rental Manager's Applications tab unless Zillow supplies a separate approved partner integration.

Therefore, a Zillow application does not automatically appear in the CRM Rental Applications module under the current system.

## Governed lifecycle

```mermaid
flowchart TD
    A["Zillow callback"] --> B["CRM Lead"]
    B --> C{"Application verified?"}
    C -- "No" --> B
    C -- "Yes" --> D["Contact + Rental Application"]
    D --> E{"Application approved?"}
    E -- "No" --> F["Close application"]
    E -- "Yes" --> G["Create CRM Lease"]
    G --> H["Request Zoho Contract"]
    H --> I["Zoho Sign and status/PDF return"]
```

### 1. Zillow callback to Lead

Zillow is an inquiry and application-interest source. Zoho CRM owns the operational pipeline after intake.

The Catalyst service upserts only:

- Leads — standard module — API `Leads`

It reads Units for routing but does not modify them. Deduplication uses the verified `Zillow_Lead_Key`.

A callback is a prospect signal, not proof of approval, a tenant relationship, or an executable lease.

### 2. Verified application to Contact plus Rental Application

Zoho's native conversion starts from a Lead, not from a Rental Application. It can create a Contact and optionally a Deal in one conversion operation.

For GH Real Estate, the safe operator action is a controlled **Promote to Rental Application** action on the Lead:

1. Confirm the person and whether a completed application actually exists.
2. Check for an existing Contact by approved duplicate rules.
3. Reuse or create the Contact.
4. Create one Rental Application in Deals.
5. Link the Contact, source Lead, requested Property, and requested Unit.
6. Copy only the permitted application-stage data.
7. Record an idempotency link so repeating the action cannot create another Contact or Application.

Properties are the renamed Accounts module. Do not let renter text in Lead Company create a new Account/Property during conversion. Use the already resolved Property record and a controlled B2C conversion path.

If a live custom button currently appears on Rental Applications and says it converts the applicant to a Contact, audit it before reuse. The preferred architecture establishes the Contact when the Lead is promoted and makes the Rental Application reference that Contact.

### 3. Completed Zillow application data

The current public Zillow Lead API cannot populate the complete Rental Application automatically.

Until Zillow provides an approved application-data API, use one of these controlled paths:

- review the completed application and reports in Zillow Rental Manager, then enter only the operational facts and decision results needed in CRM;
- collect the application through an approved Zoho form/application workflow that writes the Rental Application securely; or
- implement a Zillow private-partner interface only after written access, schema, consent, retention, and security review.

Do not scrape Zillow, automate a signed-in browser, share Zillow credentials, or copy screening reports into Contact or Lease records.

### 4. Approved Rental Application to Lease

Contact creation must not create a Lease. A person can exist without an approved application, and one Contact can have multiple applications over time.

Use one guarded **Create Lease** action on the approved Rental Application:

1. Require an approved decision and all approved rent, deposit, date, Property, Unit, and tenant fields.
2. Search for an existing Lease linked to the Rental Application.
3. Stop or return that Lease if one already exists.
4. Create one Lease in Draft status.
5. Copy approved terms and frozen Property/Unit/tenant snapshots.
6. Link the Lease back to its source Rental Application through the Lease lookup.
7. Advance the Application to Lease Record Created only after creation succeeds.

A simple workflow Create Record action may be sufficient only if the live layout supports all required lookups and duplicate protection. Prefer a custom function/button when validation, lookup traversal, snapshotting, or idempotency cannot be proven with the native action.

### 5. Lease to Zoho Contracts

Lease creation and contract creation are separate controls.

From the Lease record:

1. Verify the Lease is Ready for Contract.
2. Use the Zoho Contracts extension's **Request Contract** button.
3. Configure Primary Tenant as the counterparty.
4. Map the Lease snapshot fields to the Residential Lease Agreement.
5. Route any additional signers separately in Zoho Sign.
6. Use the Lease's Zoho Contracts related list for lifecycle status and returned documents.

The public extension workflow is an intentional request action. It does not document automatic contract creation merely because a Lease record was created.

## Data ownership through the lifecycle

| Module/system | Owns | Must not become |
|---|---|---|
| Leads | Raw Zillow identity, contact, inquiry, routing, and enriched profile fields supplied by the Lead API | Completed application or screening source of truth |
| Contacts | Reusable person identity and current contact details | A copy of every application, report, or lease term |
| Rental Applications — Deals | Application instance, screening workflow/status, verification, decision, and proposed/approved terms | Executed lease lifecycle |
| Leases | Approved tenant relationships, Property/Unit links, dates, charges, and frozen contract inputs | Screening-report repository or payment ledger |
| Zoho Contracts | Drafting, approvals, contract lifecycle, and legal agreement snapshot | CRM relationship master |
| Zoho Sign | Recipient routing, signatures, and signing evidence | Lease-term source of truth |
| Zoho Books | Customers, invoices, payments, credits, deposits, and balances | Applicant-screening store |
| Zillow Rental Manager | Complete Zillow application and reports under current public capabilities | CRM lifecycle master |
| GitHub | Sanitized code, schemas, tests, and operating documentation | Tenant/applicant data store |

## CRM Lead field map

| Zillow source field | CRM module | Verified CRM API field | Contracts merge field | Notes |
|---|---|---|---|---|
| Parsed first name from `name` | Leads | `First_Name` | None | Parsed from Zillow renter name. |
| Parsed last name from `name` | Leads | `Last_Name` | None | Required by Zoho Leads. Uses a sanitized fallback only if missing. |
| System company value | Leads | `Company` | None | Runtime placeholder only; never convert it into a Property. |
| `email` | Leads | `Email` | None | Used for follow-up, not as the sole duplicate key. |
| `phone` | Leads | `Mobile` | None | Zillow sends one phone value; GH uses Mobile as primary. |
| Secondary/alternate phone | Leads | `Phone` | None | Runtime compatibility support; not listed in the current public guide. |
| Fixed value Zillow | Leads | `Lead_Source` | None | Source attribution. |
| Intake default | Leads | `Lead_Status` | None | New Zillow Inquiry. |
| Property lookup from routing | Leads | `Requested_Property` | None | Optional lookup from the Unit routing map. |
| Unit lookup from routing | Leads | `Requested_Unit` | None | Optional lookup from the Unit routing map. |
| `movingDate` | Leads | `Requested_Move_In_Date` | None | Zillow `YYYYMMDD` converted to CRM Date. |
| `message` plus `introduction` | Leads | `Inquiry_Message` | None | Zillow inquiry text. |
| Optional renter profile fields | Leads | `Zillow_Renter_Profile_Summary` | None | Includes supplied income/employment/pet/credit-range summaries; it is not a completed application. |
| Generated key | Leads | `Zillow_Lead_Key` | None | Unique idempotent upsert key. |
| Source lead ID if supplied | Leads | `Zillow_Lead_ID` | None | Optional compatibility field. |
| `listingId` | Leads | `Zillow_Listing_ID` | None | Strongest inbound routing key. |
| Source URL if supplied | Leads | `Zillow_Listing_URL` | None | Optional link. |
| `leadType` | Leads | `Zillow_Lead_Type` | None | question, tourRequest, or applicationRequest; not completion proof. |
| `providerModelId` | Leads | `Zillow_Provider_Model_ID` | None | Multifamily/floorplan routing. |
| `moveInTimeframe` | Leads | `Zillow_Move_In_Timeframe` | None | Current documented enum. |
| Combined listing address | Leads | `Zillow_Property_Address_Raw` | None | Raw/composed listing address. |
| `listingStreet` | Leads | `Zillow_Listing_Street` | None | Listing street. |
| `listingUnit` | Leads | `Zillow_Listing_Unit` | None | Listing unit. |
| `listingCity` | Leads | `Zillow_Listing_City` | None | Listing city. |
| `listingState` | Leads | `Zillow_Listing_State` | None | Listing state. |
| `listingPostalCode` | Leads | `Zillow_Listing_Postal_Code` | None | Text preserves formatting. |
| `listingContactEmail` | Leads | `Zillow_Listing_Contact_Email` | None | Routing diagnostics. |
| Receipt timestamp | Leads | `Zillow_Received_At` | None | Date-Time. |
| Last processing timestamp | Leads | `Last_Zillow_Sync_At` | None | Date-Time. |
| Technical intake status | Leads | `Zillow_Intake_Status` | None | Sanitized processing state. |
| Payload hash | Leads | `Zillow_Source_Payload_Hash` | None | One-way audit/debug hash. |
| Received field names | Leads | `Zillow_Raw_Field_Keys` | None | Keys only, not private values. |
| Payload storage flag | Leads | `Zillow_Raw_Payload_Stored` | None | False under the current design. |
| Intake summary | Leads | `Description` | None | Sanitized operational summary. |

Do not create `Desired_Rent`, `Desired_Deposit`, `Manual_Review_Required`, or `Manual_Review_Reason` for Zillow intake.

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

## Promotion mapping

Use the production-verified APIs in the crosswalk above. Any additional Lead-conversion or promotion field still requires exact live CRM metadata verification before implementation.

| Data | Lead to Contact | Lead/application to Rental Application | Approved Application to Lease |
|---|---|---|---|
| Name, email, phone | Copy/reconcile reusable identity | Reference Primary Applicant | Freeze approved tenant/signing snapshots where required |
| Source Lead | Keep conversion trace if approved | Link Source Lead | Do not duplicate unless needed for audit |
| Property/Unit | Do not place on person | Link requested/approved records | Link approved records and freeze premises address |
| Income/employment/profile | Do not make reusable Contact truth | Store only permitted application-stage facts | Do not copy screening facts |
| Screening outcome | None | Application decision/status | Only approval conditions that affect the agreement |
| Dates, rent, deposit | None | Proposed then owner-approved values | Copy owner-approved values only |
| Pets/addenda/nonstandard terms | None | Review/approval fields | Copy only approved contract inputs |

## Separate outbound listing publication

Outbound Zillow listing publication is not part of this inbound Lead-to-Lease service. See [Zillow Listing Publication](../integrations/zillow-listing-publish/README.md).

The recommended current model is:

- Unit controls whether a rentable space is ready for marketing and owns asking rent/availability.
- Property supplies shared building/address data.
- Gabriel approves and publishes manually in Zillow Rental Manager.
- If Zillow later approves a feed, use a separate Catalyst integration and one multifamily property listing with nested unit models, subject to onboarding confirmation.
- Never publish merely because a Unit becomes vacant, and never remove a listing merely because someone applies.

## Verification still required

Before implementing the promotion or Lease actions:

- audit live Lead conversion mappings, workflows, buttons, functions, and duplicate rules;
- verify whether the apparent Rental Application Contact-conversion button exists and what it executes;
- verify every additional Deals, Contacts, Properties, Units, and Leases field API/type not covered by the governed July 24 production snapshot;
- confirm required Lease creation lookups and snapshot fields;
- test idempotency with sanitized records;
- configure the Zoho Contracts custom-module extension and field mappings;
- confirm Zillow's exact applicationRequest event semantics or continue treating it as a non-authoritative signal.

## Official sources

Reviewed July 24, 2026:

- [Zillow Rentals Lead API](https://www.zillowgroup.com/developers/api/rentals/lead-api/)
- [Zillow Lead Delivery API Guide](https://s3.amazonaws.com/files.hotpads.com/+guides/Lead+API+Guide.pdf)
- [Zillow completed-application availability](https://help.zillowrentalmanager.com/hc/en-us/articles/360058413213-A-renter-said-they-applied-When-will-I-receive-their-application)
- [Zillow application and report printing](https://help.zillowrentalmanager.com/hc/en-us/articles/360000964667-How-do-I-download-and-print-their-application-for-my-records)
- [Zoho CRM lead conversion](https://help.zoho.com/portal/en/kb/crm/sales-force-automation/leads/articles/convert-leads)
- [Zoho CRM Convert Lead API](https://www.zoho.com/crm/developer/docs/api/v8/convert-lead.html)
- [Zoho CRM workflow record creation](https://help.zoho.com/portal/en/kb/crm/automate-business-processes/workflows/articles/configuring-workflow-rules)
- [Zoho Contracts CRM extension setup](https://help.zoho.com/portal/en/kb/contracts/admin-guide/integrations/zoho-crm/articles/setting-up-zoho-contracts-extension-in-zoho-crm)
- [Requesting contracts from CRM](https://help.zoho.com/portal/en/kb/contracts/user-guide/integrations/zoho-crm/articles/initiating-contract-requests-from-zoho-crm)
