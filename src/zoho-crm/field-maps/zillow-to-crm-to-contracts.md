# Zillow to Zoho CRM to Zoho Contracts Field Map

Use sanitized examples only. Do not store real applications, screening reports, IDs, pay stubs, or tenant documents in GitHub.

## Intake Rule

Zillow is the listing inquiry source. Zoho CRM owns the operational pipeline after intake.

The Zillow lead intake service creates or updates only:

- `Leads` for the raw Zillow prospect inquiry

It does not create `Contacts`, rental application pipeline records, leases, Books records, tenant portal access, or WorkDrive folders. Those records are created later by the approved qualification, application, and lease workflow.

This is intentional. A Zillow inquiry is a prospect, not a tenant and not yet an applicant record with verified screening, owner approval, or lease terms.

## CRM Lead Field Map

| Source field | CRM module | Default CRM API field | Contracts merge field | Notes |
|---|---|---|---|---|
| Zillow `name` | Leads | `First_Name`, `Last_Name` | None | Parsed from full name when possible. |
| Required CRM display/company value | Leads | `Company` | None | Required by Zoho Leads. Defaults to matched property name, Zillow listing address, or listing ID. |
| Zillow `email` | Leads | `Email` | None | Used for follow-up, not as the only duplicate key. |
| Zillow `phone` | Leads | `Phone`, `Mobile` | None | Normalized to `+1XXXXXXXXXX` for US 10-digit numbers. |
| System default | Leads | `Lead_Source` | None | Set to `Zillow`. |
| System default | Leads | `Lead_Status` | None | Defaults to `Not Contacted`; may be changed to `New Zillow Inquiry` after picklist setup. |
| Resolved property | Leads | `Requested_Property` | None | Optional lookup resolved from `PROPERTY_UNIT_MAP_JSON`. |
| Resolved unit | Leads | `Requested_Unit` | None | Optional lookup resolved from `PROPERTY_UNIT_MAP_JSON`. |
| Zillow `movingDate` | Leads | `Requested_Move_In_Date` | None | Candidate date only until qualified. |
| Zillow `message` + `introduction` | Leads | `Inquiry_Message` | None | Inquiry text only. |
| Computed duplicate key | Leads | `Zillow_Lead_Key` | None | Mark unique. Used for idempotent upsert. |
| Zillow lead ID if present | Leads | `Zillow_Lead_ID` | None | Stored only if Zillow sends one. |
| Zillow `listingId` | Leads | `Zillow_Listing_ID` | None | Best key for unit mapping. |
| Zillow listing URL if present | Leads | `Zillow_Listing_URL` | None | Optional link back to source listing. |
| Composed Zillow listing address | Leads | `Zillow_Property_Address` | None | Built from `listingStreet`, `listingUnit`, `listingCity`, `listingState`, and `listingPostalCode`. |
| Raw callback hash | Leads | `Zillow_Source_Payload_Hash` | None | SHA-256 hash only; raw values are not stored as a blob. |
| Endpoint receive time | Leads | `Zillow_Received_At` | None | Date-time. |
| Last successful sync time | Leads | `Last_Zillow_Sync_At` | None | Date-time. |
| Intake status | Leads | `Zillow_Intake_Status` | None | Defaults to `Received`. |
| Raw payload indicator | Leads | `Zillow_Raw_Payload` | None | Set to `false`; raw payload values are intentionally not stored. |
| Sanitized Zillow summary | Leads | `Description` | None | Includes Zillow profile fields and routing warnings. |

Do not use or recreate these removed Zillow-intake fields:

- `Desired_Rent`
- `Desired_Deposit`
- `Manual_Review_Required`
- `Manual_Review_Reason`

Rent/deposit must come from approved GH Real Estate property/unit/lease records and Zoho Books. Manual review is always performed by Gabriel/business process when needed, not by a Zillow field flag.

## Promotion to Application and Lease

Only after qualification should CRM convert or promote the Lead into application-stage records.

| Stage | Source before promotion | Target after promotion | Notes |
|---|---|---|---|
| Qualified prospect | Lead | Contact | Confirm name, email, and phone before conversion. |
| Application started | Lead plus application form | Rental Application or Deal | Create only when the prospect actually enters the application workflow. |
| Screening and review | Application record | Application record | Store sensitive documents in approved Zoho systems, not GitHub. |
| Owner approval | Application record | Lease candidate fields | Approved rent, deposit, dates, pets, and conditions must be explicit. |
| Lease generation | Approved application | Zoho Contracts/Sign | Legal text stays in Zoho Contracts templates. |
| Invoicing and deposits | Approved lease terms | Zoho Books | Books owns financial truth. Do not invoice from Zillow inquiry fields. |
| Tenant portal access | Approved tenant | Tenant app or portal | Invite only after approval and onboarding decision. |

## Promotion to Lease

Only after owner approval should CRM/Contracts use approved application or lease fields for lease generation:

| Lease data | Source before approval | Source after approval | Notes |
|---|---|---|---|
| Tenant name/email/phone | Lead or application candidate | Contact | Confirm spelling before lease. |
| Property/unit | Lead or application lookup | Lease record | Must be mapped to real CRM Property and Unit. |
| Lease start/end | Application candidate fields | Lease record | Owner-approved dates only. |
| Monthly rent | Application approved rent | Lease record and Books setup | Books owns invoicing. |
| Security deposit | Application approved deposit | Lease record and Books setup | Books owns deposits. |
| Pets/ESA | Manual business review / application docs | Lease/addenda fields | Do not store sensitive docs in GitHub. |
| Signature routing | Contact/application record | Contracts/Sign | Legal text stays in Zoho Contracts templates. |
