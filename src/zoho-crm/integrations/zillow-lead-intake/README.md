# Zillow Lead Intake

Secure intake service for Zillow Rentals lead delivery. It receives Zillow's URL-encoded lead POST, authenticates the callback with a static custom header, normalizes the official Zillow fields, builds a stable duplicate-prevention key, and upserts a Zoho CRM `Leads` record.

This is only the raw inquiry intake layer. It does **not** create Contacts, Rental Applications/Deals, leases, Zoho Books invoices, tenant portal records, or WorkDrive folders. Those belong after qualification, application review, and owner approval.

## Runtime

Designed for Zoho Catalyst Advanced I/O on Node.js 18+.

No runtime npm dependencies are required. The service uses only Node built-ins so it is easy to audit and deploy.

Runtime variables are documented in `docs/runtime-environment-template.md`. Do not commit a real `.env` file.

## Endpoint

```text
POST /zillow/leads
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
Header: x-gh-zillow-webhook-key: <runtime secret>
```

Keep inbound header authentication enabled for Zillow delivery. Zillow supports a static security header/token, so do not use a secret in the query string unless Zillow later says they cannot send the header.

## First Deployment Mode

Start in dry-run:

```text
ZILLOW_WEBHOOK_DRY_RUN=true
ZILLOW_WEBHOOK_LIVE_MODE_ENABLED=false
```

Dry-run validates, parses, normalizes, and returns the planned Zoho CRM Lead fields without writing to Zoho CRM.

## Live Mode

Only after Zillow test callbacks pass:

```text
ZILLOW_WEBHOOK_DRY_RUN=false
ZILLOW_WEBHOOK_LIVE_MODE_ENABLED=true
ZILLOW_WEBHOOK_LIVE_CONFIRMATION=GH_ZILLOW_LEAD_INTAKE_LIVE_APPROVED
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
| Lead Status | `Lead_Status` | Standard picklist | Defaults to `New Zillow Inquiry`. |
| Requested Property | `Requested_Property` | Lookup to Properties/Accounts | Optional lookup from `PROPERTY_UNIT_MAP_JSON`. |
| Requested Unit | `Requested_Unit` | Lookup to Units | Optional lookup from `PROPERTY_UNIT_MAP_JSON`. |
| Requested Move-In Date | `Requested_Move_In_Date` | Date | Zillow `movingDate`. |
| Inquiry Message | `Inquiry_Message` | Multi-line text | Zillow `message` plus optional `introduction`. |
| Zillow Lead Key | `Zillow_Lead_Key` | Single line, unique | Required for idempotent upsert. |
| Zillow Lead ID | `Zillow_Lead_ID` | Single line | Optional. Zillow may not send a separate lead ID. |
| Zillow Listing ID | `Zillow_Listing_ID` | Single line | Zillow `listingId`; best routing key. |
| Zillow Listing URL | `Zillow_Listing_URL` | URL | Optional. Can be populated if Zillow sends it or via template. |
| Zillow Property Address | `Zillow_Property_Address` | Single line | Raw/composed listing address. |
| Zillow Lead Type | `Zillow_Lead_Type` | Picklist | `question`, `tourRequest`, `applicationRequest`. |
| Zillow Provider Model ID | `Zillow_Provider_Model_ID` | Single line | Zillow `providerModelId`; relevant for multifamily/floorplan routing. |
| Zillow Source Payload Hash | `Zillow_Source_Payload_Hash` | Single line | SHA-256 hash of the raw callback body. |
| Zillow Raw Field Keys | `Zillow_Raw_Field_Keys` | Multi-line or long text | Field names received, not raw values. |
| Zillow Received At | `Zillow_Received_At` | Date-time | Endpoint receive time. |
| Last Zillow Sync At | `Last_Zillow_Sync_At` | Date-time | Updated on every successful callback/upsert. |
| Zillow Intake Status | `Zillow_Intake_Status` | Picklist | Defaults to `Received`. |
| Description | `Description` | Standard long text | Sanitized summary and routing warnings. |

Do **not** create or map these removed Phase 2 fields for this intake: `Manual_Review_Required`, `Manual_Review_Reason`, `Desired_Rent`, or `Desired_Deposit`. Manual review is handled operationally by the owner, and approved rent/deposit belong on GH Real Estate property/unit/application records, not renter inquiry fields.

If actual CRM API names differ from the defaults above, set `ZOHO_CRM_FIELD_MAP_JSON` in the runtime config.

## Zillow Payload Notes

The Zillow Rentals guide uses a URL-encoded payload and includes fields such as `listingId`, `name`, `email`, `phone`, `movingDate`, `message`, listing address fields, renter preference/profile fields, `leadType`, and `providerModelId`.

The service handles official Zillow camelCase field names by normalizing them to internal keys.

## Local Verification

```powershell
cd "C:\Users\Admin\Documents\GH Real Estate Tenant App\src\zoho-crm\integrations\zillow-lead-intake"
npm run ci
```

## Manual Dry-Run Curl

```bash
curl -i -X POST "https://<catalyst-domain>/zillow/leads" \
  -H "content-type: application/x-www-form-urlencoded; charset=UTF-8" \
  -H "x-gh-zillow-webhook-key: <runtime secret>" \
  --data-binary @samples/zillow-lead.sample.urlencoded
```

## Secret Delivery to Zillow

Generate a long random value for `ZILLOW_WEBHOOK_KEY`, store it only in the runtime environment, then send the value to Zillow through a one-time secure secret link. Do not place the live secret in GitHub, normal email text, screenshots, or docs.

## Source-of-Truth Rule

Zillow remains the listing/application source for now. Zoho CRM Leads becomes the raw inquiry pipeline after intake. Contacts and Rental Applications should be created only after qualification, application review, or owner approval.
