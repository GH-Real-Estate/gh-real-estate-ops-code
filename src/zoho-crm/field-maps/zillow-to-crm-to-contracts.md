# Zillow to Zoho CRM to Zoho Contracts Field Map

Use sanitized examples only. Do not store real applications, screening reports, IDs, pay stubs, tenant documents, webhook header values, or raw Zillow payloads in GitHub.

## Intake Rule

Zillow is the listing inquiry source. Zoho CRM owns the operational pipeline after intake.

The Zillow lead intake service creates or updates only:

- `Leads` for the raw Zillow prospect inquiry

It does not create `Contacts`, rental application pipeline records, leases, Books records, tenant portal access, or WorkDrive folders. Those records are created later by the approved qualification, application, and lease workflow.

This is intentional. A Zillow inquiry is a prospect, not a tenant and not yet an applicant record with verified screening, owner approval, or lease terms.

## CRM Lead Field Map

| Zillow/source field | CRM module | Default CRM API field | Contracts merge field | Notes |
|---|---|---|---|---|
| Renter first name | Leads | `First_Name` | None | Parsed from Zillow `name` if needed. |
| Renter last name | Leads | `Last_Name` | None | Required by Zoho Leads. Uses `Zillow Prospect` only if name is missing. |
| Prospect display/company name | Leads | `Company` | None | Required by Zoho Leads. Defaults from mapped property or listing address. |
| `email` | Leads | `Email` | None | Used for follow-up, not as the only duplicate key. |
| `phone` | Leads | `Phone`, `Mobile` | None | Normalized to `+1XXXXXXXXXX` for US 10-digit numbers. |
| Lead source | Leads | `Lead_Source` | None | Set to `Zillow`. |
| Lead status | Leads | `Lead_Status` | None | Defaults to `New Zillow Inquiry`. |
| Mapped property | Leads | `Requested_Property` | None | Optional lookup resolved from `PROPERTY_UNIT_MAP_JSON`. |
| Mapped unit | Leads | `Requested_Unit` | None | Optional lookup resolved from `PROPERTY_UNIT_MAP_JSON`. |
| `movingDate` | Leads | `Requested_Move_In_Date` | None | Candidate move-in request only. Owner-approved dates belong later on application/lease records. |
| `message` + `introduction` | Leads | `Inquiry_Message` | None | Inquiry text only. Do not store screening documents here. |
| Generated duplicate key | Leads | `Zillow_Lead_Key` | None | Mark unique. Used for idempotent upsert. |
| Optional Zillow lead ID | Leads | `Zillow_Lead_ID` | None | Stored if Zillow sends one. |
| `listingId` | Leads | `Zillow_Listing_ID` | None | Best key for property/unit routing. |
| Optional listing URL | Leads | `Zillow_Listing_URL` | None | Link back to source listing if available. |
| Listing address fields | Leads | `Zillow_Property_Address` | None | Composed from `listingStreet`, `listingUnit`, `listingCity`, `listingState`, `listingPostalCode`. |
| `leadType` | Leads | `Zillow_Lead_Type` | None | Picklist: `question`, `tourRequest`, `applicationRequest`. |
| `providerModelId` | Leads | `Zillow_Provider_Model_ID` | None | Supports multifamily/floorplan routing where provided. |
| Raw callback body hash | Leads | `Zillow_Source_Payload_Hash` | None | Stores SHA-256 hash for troubleshooting without storing raw PII values. |
| Raw field names | Leads | `Zillow_Raw_Field_Keys` | None | Stores received field names only. |
| Endpoint receive time | Leads | `Zillow_Received_At` | None | Date-time. |
| Last successful sync | Leads | `Last_Zillow_Sync_At` | None | Date-time. |
| Intake status | Leads | `Zillow_Intake_Status` | None | Defaults to `Received`. |
| Intake summary | Leads | `Description` | None | Sanitized operational summary and routing warnings. |

## Zillow Fields Preserved In Summary

The service does not create a CRM custom field for every renter preference value. Instead, less operationally critical fields are summarized in `Description` to keep the Leads module usable:

```text
numBedroomsSought
numBathroomsSought
neighborhoods
propertyTypesDesired
leaseLengthMonths
smoker
parkingTypeDesired
incomeYearly
creditScoreRangeJson
movingFromCity
movingFromState
moveInTimeframe
reasonForMoving
employmentStatus
jobTitle
employer
employmentStartDate
employmentDetailsJson
petDetailsJson
```

This keeps intake useful without making CRM Leads the system of record for underwriting or leasing decisions.

## Fields Intentionally Not Used

Do not use these fields in the Zillow intake:

| Removed field | Reason |
|---|---|
| `Manual_Review_Required` | Manual review is always done by the owner/operator. |
| `Manual_Review_Reason` | Routing warnings already appear in `Description`; no workflow should bypass owner review. |
| `Desired_Rent` | Renter inquiry data must not control rent. Use GH Real Estate property/unit/application records. |
| `Desired_Deposit` | Renter inquiry data must not control deposits. Use approved lease/application records and Zoho Books. |

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
| Pets/ESA | Manual owner review / application docs | Lease/addenda fields | Do not store sensitive docs in GitHub. |
| Signature routing | Contact/application record | Contracts/Sign | Legal text stays in Zoho Contracts templates. |
