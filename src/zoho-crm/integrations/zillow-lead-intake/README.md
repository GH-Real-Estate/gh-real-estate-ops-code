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

Before live mode, create or confirm these CRM fields in the Leads module.

Leads:

| Business field | Default API name | Notes |
|---|---|---|
| First Name | `First_Name` | Standard Leads field. |
| Last Name | `Last_Name` | Required by Zoho Leads. Uses `Zillow Prospect` only if name is missing. |
| Company | `Company` | Required by Zoho Leads. Uses mapped property, address, listing ID, or GH default. |
| Email | `Email` | Used for human follow-up and optional duplicate views. |
| Phone / Mobile | `Phone`, `Mobile` | Normalized to `+1XXXXXXXXXX` for US 10-digit numbers. |
| Lead Source | `Lead_Source` | Defaults to `Zillow`. |
| Lead Status | `Lead_Status` | Defaults to `Not Contacted`; override if your picklist uses `New Inquiry`. |
| Property | `Property` | Lookup to Properties. |
| Unit | `Unit` | Lookup to Units. |
| Zillow Lead Key | `Zillow_Lead_Key` | Mark unique. Used for idempotency. |
| Zillow Lead ID | `Zillow_Lead_ID` | Store source lead ID if Zillow sends one. |
| Zillow Listing ID | `Zillow_Listing_ID` | Useful for unit mapping. |
| Zillow Listing URL | `Zillow_Listing_URL` | Link field or URL. |
| Zillow Message | `Zillow_Message` | Multi-line text. |
| Zillow Raw Field Keys | `Zillow_Raw_Field_Keys` | Stores keys received, not raw private payload. |
| Lead Received Date | `Lead_Received_Date` | Date. |
| Desired Move-In Date | `Desired_Move_In_Date` | Date. |
| Desired Rent | `Desired_Rent` | Informational only. Books remains financial truth. |
| Desired Deposit | `Desired_Deposit` | Informational only. Books remains financial truth. |
| Manual Review Required | `Manual_Review_Required` | Checkbox. |
| Manual Review Reason | `Manual_Review_Reason` | Multi-line text. |

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
