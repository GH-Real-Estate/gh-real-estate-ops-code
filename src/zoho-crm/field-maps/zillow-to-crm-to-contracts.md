# Zillow to Zoho CRM to Zoho Contracts Field Map

Use sanitized examples only. Do not store real applications, screening reports, IDs, pay stubs, or tenant documents in GitHub.

## Intake Rule

Zillow is the listing/application source for now. Zoho CRM owns the operational pipeline after intake.

The Zillow lead intake service creates or updates:

- `Contacts` for the person
- `Deals` renamed to `Rental Applications` for the application pipeline record

It does not create leases, Books records, tenant portal access, or WorkDrive folders.

## CRM Field Map

| Source field | CRM module | Default CRM API field | Contracts merge field | Notes |
|---|---|---|---|---|
| Applicant first name | Contacts | `First_Name` | `tenant_first_name` | Parsed from Zillow name if needed. |
| Applicant last name | Contacts | `Last_Name` | `tenant_last_name` | Required by Zoho Contacts. Uses `Zillow Prospect` only if name is missing. |
| Applicant email | Contacts | `Email` | `tenant_email` | Primary duplicate check where available. |
| Applicant phone | Contacts | `Phone`, `Mobile` | `tenant_phone` | Normalized to `+1XXXXXXXXXX` for US 10-digit numbers. |
| Contact type | Contacts | `Contact_Type` | None | Set to `Applicant`. |
| Lead source | Contacts | `Lead_Source` | None | Set to `Zillow`. |
| Portal access status | Contacts | `Portal_Access_Status` | None | Set to `Not Invited` until approved/move-in workflow. |
| Related property | Contacts | `Related_Property` | None | Optional lookup to Properties, resolved from `PROPERTY_UNIT_MAP_JSON`. |
| Related unit | Contacts | `Related_Unit` | None | Optional lookup to Units, resolved from `PROPERTY_UNIT_MAP_JSON`. |
| Application name | Deals/Rental Applications | `Deal_Name` | None | Example: `Zillow - Test Tenant - Unit 1 - 2026-07-01`. |
| Application stage | Deals/Rental Applications | `Stage` | None | Defaults to `New Inquiry`. |
| Pipeline | Deals/Rental Applications | `Pipeline` | None | Only set if your CRM requires named pipelines. |
| Closing date | Deals/Rental Applications | `Closing_Date` | None | Required by Zoho Deals. Defaults to intake date + 14 days. |
| Applicant contact lookup | Deals/Rental Applications | `Contact_Name` | None | Links the application to the Contact. |
| Property lookup | Deals/Rental Applications | `Property` | `property_name` | Custom lookup to Properties. |
| Unit lookup | Deals/Rental Applications | `Unit` | `unit_name` | Custom lookup to Units. |
| Zillow lead key | Deals/Rental Applications | `Zillow_Lead_Key` | None | Mark unique. Used for idempotent upsert. |
| Zillow lead ID | Deals/Rental Applications | `Zillow_Lead_ID` | None | Stored if Zillow sends one. |
| Zillow listing ID | Deals/Rental Applications | `Zillow_Listing_ID` | None | Best key for unit mapping. |
| Zillow listing URL | Deals/Rental Applications | `Zillow_Listing_URL` | None | Link back to source listing. |
| Zillow message | Deals/Rental Applications | `Zillow_Message` | None | Inquiry message only. Do not store screening documents here. |
| Raw field keys | Deals/Rental Applications | `Zillow_Raw_Field_Keys` | None | Stores field names received, not raw payload values. |
| Application received date | Deals/Rental Applications | `Application_Received_Date` | None | Date only. |
| Desired move-in date | Deals/Rental Applications | `Desired_Move_In_Date` | `lease_start_date_candidate` | Candidate only until approved. |
| Screening status | Deals/Rental Applications | `Screening_Status` | None | Defaults to `Not Started`. |
| Owner decision | Deals/Rental Applications | `Owner_Decision` | None | Defaults to `New Inquiry`. |
| Approved rent | Deals/Rental Applications | `Approved_Rent` | `monthly_rent` | Do not invoice from this. Books remains financial truth. |
| Approved deposit | Deals/Rental Applications | `Approved_Deposit` | `security_deposit` | Do not invoice from this. Books remains financial truth. |
| Manual review required | Deals/Rental Applications | `Manual_Review_Required` | None | True when key data or mapping is missing. |
| Manual review reason | Deals/Rental Applications | `Manual_Review_Reason` | None | Human-readable reasons. |
| WorkDrive folder URL | Deals/Rental Applications | `WorkDrive_Folder_URL` | None | Blank until folder automation exists. |

## Promotion to Lease

Only after owner approval should CRM/Contracts use these fields for lease generation:

| Lease data | Source before approval | Source after approval | Notes |
|---|---|---|---|
| Tenant name/email/phone | Contact | Contact | Confirm spelling before lease. |
| Property/unit | Rental Application lookup | Lease record | Must be mapped to real CRM Property and Unit. |
| Lease start/end | Rental Application candidate fields | Lease record | Owner-approved dates only. |
| Monthly rent | Rental Application approved rent | Lease record and Books setup | Books owns invoicing. |
| Security deposit | Rental Application approved deposit | Lease record and Books setup | Books owns deposits. |
| Pets/ESA | Manual review / application docs | Lease/addenda fields | Do not store sensitive docs in GitHub. |
| Signature routing | CRM/Contacts | Contracts/Sign | Legal text stays in Zoho Contracts templates. |
