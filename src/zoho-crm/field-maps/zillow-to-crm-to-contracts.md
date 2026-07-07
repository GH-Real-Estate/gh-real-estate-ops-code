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
| `phone` | Leads | `Mobile` | None | Zillow sends one phone value; GH layout uses Mobile. |
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
