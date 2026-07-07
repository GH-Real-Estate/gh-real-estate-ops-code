# Zillow Lead Intake

Secure intake service for Zillow rental leads. It receives Zillow's URL-encoded lead POST, validates it, builds a stable duplicate-prevention key, then upserts a Zoho CRM `Leads` record.

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

Keep `REQUIRE_INBOUND_SECRET=true`. Prefer a secret header if Zillow supports it. If Zillow only supports a plain webhook URL, use an unguessable URL/route at the Catalyst layer or temporarily enable `ALLOW_SECRET_QUERY_PARAM=true` with a long random value.

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

Leads:

| Business field | Default API name | Type | Notes |
|---|---|---|---|
| First Name | `First_Name` | Standard | Standard Leads field. |
| Last Name | `Last_Name` | Standard | Required by Zoho Leads. Uses `Zillow Prospect` only if name is missing. |
| Company | `Company` | Standard / Single Line | Required by Zoho Leads. Uses mapped property, address, listing ID, or GH default. |
| Email | `Email` | Email | Used for human follow-up. |
| Phone / Mobile | `Phone`, `Mobile` | Phone | Normalized to `+1XXXXXXXXXX` for US 10-digit numbers. |
| Lead Source | `Lead_Source` | Picklist | Defaults to `Zillow`. |
| Lead Status | `Lead_Status` | Picklist | Defaults to `New Zillow Inquiry`. |
| Requested Property | `Requested_Property` | Lookup to Properties | Optional lookup resolved from `PROPERTY_UNIT_MAP_JSON`. |
| Requested Unit | `Requested_Unit` | Lookup to Units | Optional lookup resolved from `PROPERTY_UNIT_MAP_JSON`. |
| Requested Move-In Date | `Requested_Move_In_Date` | Date | From Zillow `movingDate` when supplied. |
| Inquiry Message | `Inquiry_Message` | Multi-Line | Main Zillow message text. |
| Zillow Lead Key | `Zillow_Lead_Key` | Single Line / Unique | Mark unique. Used for idempotent upsert. |
| Zillow Lead ID | `Zillow_Lead_ID` | Single Line | Stored if Zillow sends a source lead ID. |
| Zillow Listing ID | `Zillow_Listing_ID` | Single Line | Best field for listing/unit mapping. |
| Zillow Listing URL | `Zillow_Listing_URL` | URL | Optional link back to source listing when supplied. |
| Zillow Lead Type | `Zillow_Lead_Type` | Picklist | Values: `question`, `tourRequest`, `applicationRequest`. |
| Zillow Provider Model ID | `Zillow_Provider_Model_ID` | Single Line | Useful for multi-family/floorplan routing. |
| Zillow Property Address | `Zillow_Property_Address` | Single Line | Combined address from Zillow's listing address components. |
| Zillow Listing Contact Email | `Zillow_Listing_Contact_Email` | Email | Useful if Zillow routes by contact email/domain. |
| Zillow Move-In Timeframe | `Zillow_Move_In_Timeframe` | Picklist or Single Line | Zillow values include `asap`, `flexible`, `week`, `twoWeeks`, `month`, `twoMonths`. |
| Zillow Raw Field Keys | `Zillow_Raw_Field_Keys` | Multi-Line | Stores received field names only, not raw private payload values. |
| Zillow Source Payload Hash | `Zillow_Source_Payload_Hash` | Single Line | SHA-256 hash of the received payload for audit/dedupe troubleshooting. |
| Zillow Raw Payload Stored | `Zillow_Raw_Payload` | Checkbox | Leave false unless raw payloads are stored in an approved secure system. |
| Zillow Received At | `Zillow_Received_At` | Date-Time | Server receipt timestamp. |
| Last Zillow Sync At | `Last_Zillow_Sync_At` | Date-Time | Last processed timestamp. |
| Zillow Intake Status | `Zillow_Intake_Status` | Picklist | Defaults to `Received`. |
| Description | `Description` | Standard Multi-Line | Sanitized operational summary for CRM users. |

Do not create `Desired_Rent`, `Desired_Deposit`, `Manual_Review_Required`, or `Manual_Review_Reason` for this intake. GH Real Estate manually reviews every lead, and rent/deposit must come from approved property/unit/lease records, not a prospect's preference.

When the prospect becomes qualified, use a CRM conversion/owner-review workflow to create the Contact and Rental Application/Deal.

## Local Verification

```powershell
cd "C:\Users\Admin\Documents\GH Real Estate Tenant App\src\zoho-crm\integrations\zillow-lead-intake"
npm run ci
```

## Manual Smoke Test

In dry-run mode, post the fake sample:

```powershell
$body = Get-Content -Raw ".\samples\zillow-lead.sample.urlencoded"
Invoke-WebRequest `
  -Uri "https://your-catalyst-domain/zillow/leads" `
  -Method POST `
  -ContentType "application/x-www-form-urlencoded" `
  -Headers @{ "x-gh-zillow-webhook-key" = "replace-with-long-random-secret" } `
  -Body $body
```

Expected result:

- `ok=true`
- `mode=dry_run`
- response includes a non-PII `lead_reference`
- response includes planned `lead` action

## Source-of-Truth Rule

Zillow remains the listing/application source for now. Zoho CRM Leads becomes the raw inquiry pipeline after intake. Contacts and Rental Applications should be created only after qualification, application review, or owner approval.
