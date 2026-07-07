# Zillow Lead Intake

Secure intake service for Zillow Rentals leads. It receives Zillow's URL-encoded lead POST, validates it, builds a stable duplicate-prevention key, then upserts a Zoho CRM `Leads` record.

This is the first automation slice. It does not create Contacts, Rental Applications/Deals, leases, Books invoices, tenant portal records, or WorkDrive folders. Those belong after qualification or approval.

## Runtime

Designed for Zoho Catalyst Advanced I/O on Node.js 18+.

No runtime npm dependencies are required. The service uses only Node built-ins so it is easy to audit and deploy.

Runtime variables are documented in `docs/runtime-environment-template.md`. Do not commit a real `.env` file.

## Endpoint

```text
POST /zillow/leads
Content-Type: application/x-www-form-urlencoded
```

Keep inbound header authentication enabled for Zillow delivery.

## First Deployment Mode

Start in dry-run:

```text
DRY_RUN=true
LIVE_MODE_ENABLED=false
```

Dry-run validates the payload and returns the planned Zoho mutations without writing to Zoho CRM.

## Live Mode

Only after dry-run tests pass:

```text
DRY_RUN=false
LIVE_MODE_ENABLED=true
LIVE_MODE_CONFIRMATION=GH_ZILLOW_LEAD_INTAKE_LIVE_APPROVED
```

This double switch prevents accidental live CRM writes during setup.

## Required Zoho CRM Setup

Before live mode, create or confirm these CRM fields in the Leads module.

| Business field | Default API name | Type | Notes |
|---|---|---|---|
| First Name | `First_Name` | Standard name field | Parsed from Zillow `name`. |
| Last Name | `Last_Name` | Standard single line | Required by Zoho Leads. |
| Company | `Company` | Standard single line | Required by Zoho Leads. Auto-filled from property/listing data. |
| Email | `Email` | Standard email | Renter email. |
| Phone / Mobile | `Phone`, `Mobile` | Standard phone | Normalized for US 10-digit numbers. |
| Lead Source | `Lead_Source` | Standard picklist | Defaults to `Zillow`. |
| Lead Status | `Lead_Status` | Standard picklist | Use `New Zillow Inquiry` after the picklist is configured. |
| Requested Property | `Requested_Property` | Lookup to Properties/Accounts | Optional lookup from property/unit map. |
| Requested Unit | `Requested_Unit` | Lookup to Units | Optional lookup from property/unit map. |
| Requested Move-In Date | `Requested_Move_In_Date` | Date | Zillow `movingDate`. |
| Inquiry Message | `Inquiry_Message` | Multi-line text | Zillow `message` plus optional `introduction`. |
| Zillow Lead Key | `Zillow_Lead_Key` | Single line, unique | Required for idempotent upsert. |
| Zillow Lead ID | `Zillow_Lead_ID` | Single line | Optional. Zillow may not send a separate lead ID. |
| Zillow Listing ID | `Zillow_Listing_ID` | Single line | Zillow `listingId`; best routing key. |
| Zillow Listing URL | `Zillow_Listing_URL` | URL | Optional. |
| Zillow Property Address | `Zillow_Property_Address` | Single line | Raw/composed listing address. |
| Zillow Source Payload Hash | `Zillow_Source_Payload_Hash` | Single line | Hash of the raw callback body for troubleshooting. |
| Zillow Received At | `Zillow_Received_At` | Date-time | Endpoint receive time. |
| Last Zillow Sync At | `Last_Zillow_Sync_At` | Date-time | Updated on every successful callback/upsert. |
| Zillow Intake Status | `Zillow_Intake_Status` | Picklist | Defaults to `Received`. |
| Zillow Raw Payload | `Zillow_Raw_Payload` | Checkbox | Raw callback values are not stored by this service. |
| Description | `Description` | Standard long text | Sanitized summary and routing warnings. |

Do not create Phase 2 fields for `Manual_Review_Required`, `Manual_Review_Reason`, `Desired_Rent`, or `Desired_Deposit`.

If actual CRM API names differ from the defaults above, set `ZOHO_CRM_FIELD_MAP_JSON` in the runtime config.

## Zillow Payload Notes

The Zillow Rentals guide uses a URL-encoded payload and includes fields such as `listingId`, `name`, `email`, `phone`, `movingDate`, `message`, listing address fields, `leadType`, and `providerModelId`.

The service handles official Zillow camelCase field names by normalizing them to internal keys.

## Local Verification

```powershell
cd "C:\Users\Admin\Documents\GH Real Estate Tenant App\src\zoho-crm\integrations\zillow-lead-intake"
npm run ci
```

## Source-of-Truth Rule

Zillow remains the listing/application source for now. Zoho CRM Leads becomes the raw inquiry pipeline after intake. Contacts and Rental Applications should be created only after qualification, application review, or owner approval.
