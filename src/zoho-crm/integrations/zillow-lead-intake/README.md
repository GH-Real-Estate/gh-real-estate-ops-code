# Zillow Lead Intake

Secure intake service for Zillow rental leads. It receives Zillow's URL-encoded lead POST, validates it, builds a stable duplicate-prevention key, then upserts:

- a Zoho CRM `Contacts` record for the person
- a Zoho CRM `Deals` record renamed as `Rental Applications`

This is the first automation slice. It does not create leases, Books invoices, tenant portal records, or WorkDrive folders.

## Runtime

Designed for Zoho Catalyst Advanced I/O on Node.js 18+.

No runtime npm dependencies are required. The service uses only Node built-ins so it is easy to audit and deploy.

## Endpoint

```text
POST /zillow/leads
Content-Type: application/x-www-form-urlencoded
```

Keep `REQUIRE_INBOUND_SECRET=true`. Prefer a secret header if Zillow supports it for your integration. If Zillow only supports a plain webhook URL, use an unguessable URL/route at the Catalyst layer or temporarily enable `ALLOW_SECRET_QUERY_PARAM=true` with a long random value.

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

Before live mode, create or confirm these CRM fields.

Contacts:

| Business field | Default API name | Notes |
|---|---|---|
| Contact Type | `Contact_Type` | Picklist. Include `Applicant`. |
| Related Property | `Related_Property` | Optional lookup to Properties. |
| Related Unit | `Related_Unit` | Optional lookup to Units. |
| Portal Access Status | `Portal_Access_Status` | Optional picklist. |

Deals / Rental Applications:

| Business field | Default API name | Notes |
|---|---|---|
| Application Name | `Deal_Name` | Standard Deals field. |
| Stage | `Stage` | Standard Deals field. |
| Closing Date | `Closing_Date` | Standard Deals field, required by Zoho Deals. |
| Applicant Contact | `Contact_Name` | Standard Deals contact lookup. |
| Property | `Property` | Lookup to Properties. |
| Unit | `Unit` | Lookup to Units. |
| Zillow Lead Key | `Zillow_Lead_Key` | Mark unique. Used for idempotency. |
| Zillow Lead ID | `Zillow_Lead_ID` | Store source lead ID if Zillow sends one. |
| Zillow Listing ID | `Zillow_Listing_ID` | Useful for unit mapping. |
| Zillow Listing URL | `Zillow_Listing_URL` | Link field or URL. |
| Zillow Message | `Zillow_Message` | Multi-line text. |
| Zillow Raw Field Keys | `Zillow_Raw_Field_Keys` | Stores keys received, not raw private payload. |
| Application Received Date | `Application_Received_Date` | Date. |
| Desired Move-In Date | `Desired_Move_In_Date` | Date. |
| Screening Status | `Screening_Status` | Defaults to `Not Started`. |
| Owner Decision | `Owner_Decision` | Defaults to `New Inquiry`. |
| Manual Review Required | `Manual_Review_Required` | Checkbox. |
| Manual Review Reason | `Manual_Review_Reason` | Multi-line text. |
| WorkDrive Folder URL | `WorkDrive_Folder_URL` | Blank until WorkDrive automation exists. |

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
- response includes planned `contact` and `application` actions

## Source-of-Truth Rule

Zillow remains the listing/application source for now. Zoho CRM becomes the operational pipeline after intake. This service only moves inquiry/application metadata into CRM so GH Real Estate can stop manually retyping lead data.
