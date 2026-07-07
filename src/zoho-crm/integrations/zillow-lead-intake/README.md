# Zillow Lead Intake

Secure intake service for Zillow Rentals leads. It receives Zillow's `application/x-www-form-urlencoded` lead POST, validates a static inbound secret header, normalizes Zillow's official payload fields, builds a stable duplicate-prevention key, and then creates or updates a Zoho CRM `Leads` record.

This is the first automation slice. It does **not** create Contacts, Rental Applications/Deals, leases, Books invoices, tenant portal records, or WorkDrive folders. Those belong after qualification, application review, or owner approval.

## Runtime

Designed for Zoho Catalyst Advanced I/O on Node.js 18+.

The default runtime uses only Node built-ins. Optional Catalyst Cache replay defense can be enabled later if `zcatalyst-sdk-node` is available in the deployed runtime.

Runtime variables are documented in `docs/runtime-environment-template.md`. Do not commit a real `.env` file.

## Endpoint

```text
POST /zillow/leads
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
x-gh-zillow-webhook-key: <runtime secret>
```

Zillow Support confirmed they can send lead callbacks to an endpoint, configure a custom header, and test callbacks before production. Use one endpoint for the portfolio and keep it in dry-run first.

## First Deployment Mode

Start in dry-run:

```text
ZILLOW_WEBHOOK_DRY_RUN=true
DRY_RUN=true
LIVE_MODE_ENABLED=false
```

Dry-run validates the request and returns the planned Zoho mutation without creating a CRM Lead. If `ENABLE_CRM_INTAKE_EVENT_LOG=true` and `ENABLE_DRY_RUN_CRM_AUDIT_LOG=true`, dry-run can write an optional CRM audit event only; it still does not create a Lead.

## Live Mode

Only after Zillow test callbacks pass:

```text
ZILLOW_WEBHOOK_DRY_RUN=false
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
| Lead Status | `Lead_Status` | Standard picklist | Defaults to `Not Contacted`; use `New Zillow Inquiry` after the picklist is configured. |
| Requested Property | `Requested_Property` | Lookup to Properties/Accounts | Optional lookup from `PROPERTY_UNIT_MAP_JSON`. |
| Requested Unit | `Requested_Unit` | Lookup to Units | Optional lookup from `PROPERTY_UNIT_MAP_JSON`. |
| Requested Move-In Date | `Requested_Move_In_Date` | Date | Zillow `movingDate`. |
| Inquiry Message | `Inquiry_Message` | Multi-line text | Zillow `message` plus optional `introduction`. |
| Zillow Lead Key | `Zillow_Lead_Key` | Single line, unique | Required for idempotent upsert. |
| Zillow Lead ID | `Zillow_Lead_ID` | Single line | Optional. Zillow may not send a separate lead ID. |
| Zillow Listing ID | `Zillow_Listing_ID` | Single line | Zillow `listingId`; best routing key. |
| Zillow Listing URL | `Zillow_Listing_URL` | URL | Optional; Zillow's documented payload example does not include this field, but the service supports it if present. |
| Zillow Property Address | `Zillow_Property_Address` | Single line | Composed from `listingStreet`, `listingUnit`, `listingCity`, `listingState`, and `listingPostalCode`. |
| Zillow Source Payload Hash | `Zillow_Source_Payload_Hash` | Single line | SHA-256 hash of the raw callback body for troubleshooting. |
| Zillow Received At | `Zillow_Received_At` | Date-time | Endpoint receive time. |
| Last Zillow Sync At | `Last_Zillow_Sync_At` | Date-time | Updated on every successful callback/upsert. |
| Zillow Intake Status | `Zillow_Intake_Status` | Picklist | Defaults to `Received`. |
| Zillow Raw Payload | `Zillow_Raw_Payload` | Checkbox | Set to `false`; raw payload values are intentionally not stored in CRM. |
| Description | `Description` | Standard long text | Sanitized summary, Zillow profile details, and routing warnings. |

Do **not** create Phase 2 fields for `Manual_Review_Required`, `Manual_Review_Reason`, `Desired_Rent`, or `Desired_Deposit`. Manual review is a business action, not a Zillow-intake field, and rent/deposit must come from GH Real Estate's approved property/unit/lease records.

If actual CRM API names differ from the defaults above, set `ZOHO_CRM_FIELD_MAP_JSON` in the runtime config.

## Zillow Payload Notes

The Zillow Rentals guide uses a URL-encoded payload and includes fields such as:

```text
listingId
name
email
phone
movingDate
numBedroomsSought
numBathroomsSought
message
listingStreet
listingUnit
listingCity
listingPostalCode
listingState
listingContactEmail
neighborhoods
propertyTypesDesired
leaseLengthMonths
introduction
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
leadType
providerModelId
```

The service handles Zillow camelCase field names by normalizing them to internal keys.

## Local Verification

```powershell
cd "C:\Users\Admin\Documents\GH Real Estate Tenant App\src\zoho-crm\integrations\zillow-lead-intake"
npm run ci
```

## Local Dry-Run Curl

```bash
curl -i \
  -X POST "https://<your-catalyst-domain>/zillow/leads" \
  -H "Content-Type: application/x-www-form-urlencoded; charset=UTF-8" \
  -H "x-gh-zillow-webhook-key: <runtime secret>" \
  --data-binary @samples/zillow-lead.sample.urlencoded
```

Expected first result:

```text
HTTP 202
mode=dry_run
```

## Source-of-Truth Rule

Zillow remains the listing/application source for now. Zoho CRM Leads becomes the raw inquiry pipeline after intake. Contacts and Rental Applications should be created only after qualification, application review, or owner approval.
