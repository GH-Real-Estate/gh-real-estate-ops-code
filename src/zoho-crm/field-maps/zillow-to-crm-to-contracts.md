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
| Prospect first name | Leads | `First_Name` | None | Parsed from Zillow name if needed. |
| Prospect last name | Leads | `Last_Name` | None | Required by Zoho Leads. Uses `Zillow Prospect` only if name is missing. |
| Prospect display/company name | Leads | `Company` | None | Required by Zoho Leads in many layouts. Defaults to `Zillow Prospect`. |
| Prospect email | Leads | `Email` | None | Used for follow-up, not as the primary duplicate key. |
| Prospect phone | Leads | `Phone`, `Mobile` | None | Normalized to `+1XXXXXXXXXX` for US 10-digit numbers. |
| Lead source | Leads | `Lead_Source` | None | Set to `Zillow`. |
| Lead status | Leads | `Lead_Status` | None | Defaults to `Not Contacted`. |
| Related property | Leads | `Property` | None | Optional lookup resolved from `PROPERTY_UNIT_MAP_JSON`. |
| Related unit | Leads | `Unit` | None | Optional lookup resolved from `PROPERTY_UNIT_MAP_JSON`. |
| Zillow lead key | Leads | `Zillow_Lead_Key` | None | Mark unique. Used for idempotent upsert. |
| Zillow lead ID | Leads | `Zillow_Lead_ID` | None | Stored if Zillow sends one. |
| Zillow listing ID | Leads | `Zillow_Listing_ID` | None | Best key for unit mapping. |
| Zillow listing URL | Leads | `Zillow_Listing_URL` | None | Link back to source listing. |
| Zillow message | Leads | `Zillow_Message` | None | Inquiry message only. Do not store screening documents here. |
| Zillow source | Leads | `Zillow_Source` | None | Defaults to `Zillow`. |
| Raw field keys | Leads | `Zillow_Raw_Field_Keys` | None | Stores field names received, not raw payload values. |
| Lead received date | Leads | `Lead_Received_Date` | None | Date only. |
| Desired move-in date | Leads | `Desired_Move_In_Date` | None | Candidate only until qualified. |
| Desired rent | Leads | `Desired_Rent` | None | Inquiry value only. Do not invoice from this. |
| Desired deposit | Leads | `Desired_Deposit` | None | Inquiry value only. Do not invoice from this. |
| Manual review required | Leads | `Manual_Review_Required` | None | True when key data or mapping is missing. |
| Manual review reason | Leads | `Manual_Review_Reason` | None | Human-readable reasons. |
| Intake summary | Leads | `Description` | None | Sanitized operational summary for CRM users. |

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
| Pets/ESA | Manual review / application docs | Lease/addenda fields | Do not store sensitive docs in GitHub. |
| Signature routing | Contact/application record | Contracts/Sign | Legal text stays in Zoho Contracts templates. |
