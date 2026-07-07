# Zillow Lead Intake

Secure intake service for Zillow Rentals leads. It receives Zillow's `application/x-www-form-urlencoded` lead POST, normalizes Zillow's official payload fields, builds a stable duplicate-prevention key, and creates or updates a Zoho CRM `Leads` record.

This automation slice creates or updates CRM Leads only. It does not create Contacts, Rental Applications/Deals, leases, Books invoices, tenant portal records, or WorkDrive folders. Those belong after qualification, application review, or owner approval.

## Endpoint

```text
POST /zillow/leads
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
```

Zillow Support confirmed they can send lead callbacks to an endpoint, configure a custom header, and test callbacks before production. Use one endpoint for the portfolio and keep it in dry-run first.

## CRM Lead Layout

Use the GH Real Estate Leads layout as the Phase 2 intake target.

### Lead Information

Two-column section.

| Left | Right |
|---|---|
| First Name | Lead Status |
| Last Name | Lead Source |
| Email | Requested Property |
| Mobile | Requested Unit |
| Zillow Lead Type | Requested Move-In Date |

`Company` may remain unused/hidden in the layout, but the intake service still populates it because Zoho Leads may require it at the API level.

### Inquiry Details

Single-column section.

1. Inquiry Message
2. Zillow Renter Profile Summary
3. Description

Prefer Multi Line Large for `Inquiry Message`, `Zillow Renter Profile Summary`, and `Zillow Raw Field Keys`. Rich Text can work for plain text, but it is unnecessary for this integration and can create formatting friction later.

### Zillow Routing

Two-column section.

| Left | Right |
|---|---|
| Zillow Lead Key | Zillow Intake Status |
| Zillow Listing ID | Zillow Received At |
| Zillow Provider Model ID | Last Zillow Sync At |
| Zillow Listing Contact Email | Zillow Source Payload Hash |
| Zillow Move-In Timeframe | |

### Zillow Listing Address

Two-column section.

| Left | Right |
|---|---|
| Zillow Property Address Raw | Zillow Listing Unit |
| Zillow Listing Street | Zillow Listing State |
| Zillow Listing City | Zillow Listing URL |
| Zillow Listing Postal Code | |

### Zillow Audit

Single-column section.

1. Zillow Raw Field Keys
2. Zillow Raw Payload Stored
3. Zillow Lead ID

### System Reference

Two-column section.

| Left | Right |
|---|---|
| Created By | Lead Owner |
| Modified By | |

Keep the standard Visit Summary and unused system lead fields out of this GH Real Estate layout.

## Required Zoho CRM Fields

Before live mode, create or confirm these CRM fields in the Leads module.

| Business field | Verified API name | Type | Notes |
|---|---|---|---|
| First Name | `First_Name` | Standard name field | Parsed from Zillow `name`. |
| Last Name | `Last_Name` | Standard single line | Required by Zoho Leads. |
| Company | `Company` | Standard single line | Hidden is fine, but the API write still populates it. |
| Email | `Email` | Standard email | Zillow `email`. |
| Mobile | `Mobile` | Standard phone | Zillow `phone`; normalized for US 10-digit numbers. |
| Lead Source | `Lead_Source` | Standard picklist | Use `Zillow`. |
| Lead Status | `Lead_Status` | Standard picklist | Use `New Zillow Inquiry` for new intake. |
| Requested Property | `Requested_Property` | Lookup to Properties/Accounts | Optional lookup from `PROPERTY_UNIT_MAP_JSON`. |
| Requested Unit | `Requested_Unit` | Lookup to Units | Optional lookup from `PROPERTY_UNIT_MAP_JSON`. |
| Requested Move-In Date | `Requested_Move_In_Date` | Date | Zillow `movingDate`. |
| Inquiry Message | `Inquiry_Message` | Multi Line Large | Zillow `message` plus optional `introduction`. |
| Zillow Renter Profile Summary | `Zillow_Renter_Profile_Summary` | Multi Line Large | Summary of optional renter profile fields. |
| Zillow Lead Key | `Zillow_Lead_Key` | Single line, unique | Required for idempotent upsert. |
| Zillow Lead ID | `Zillow_Lead_ID` | Single line | Optional. Zillow may not send a separate lead ID. |
| Zillow Listing ID | `Zillow_Listing_ID` | Single line | Zillow `listingId`; best routing key. |
| Zillow Listing URL | `Zillow_Listing_URL` | URL | Optional; Zillow's documented payload example does not include this field. |
| Zillow Lead Type | `Zillow_Lead_Type` | Picklist | `question`, `tourRequest`, `applicationRequest`. |
| Zillow Provider Model ID | `Zillow_Provider_Model_ID` | Single line | Zillow `providerModelId`. |
| Zillow Move-In Timeframe | `Zillow_Move_In_Timeframe` | Picklist | `asap`, `flexible`, `week`, `month`, `twoWeeks`, `twoMonths`. |
| Zillow Property Address Raw | `Zillow_Property_Address_Raw` | Single line | Composed from Zillow listing address components. |
| Zillow Listing Street | `Zillow_Listing_Street` | Single line | Zillow `listingStreet`. |
| Zillow Listing Unit | `Zillow_Listing_Unit` | Single line | Zillow `listingUnit`. |
| Zillow Listing City | `Zillow_Listing_City` | Single line | Zillow `listingCity`. |
| Zillow Listing State | `Zillow_Listing_State` | Single line | Zillow `listingState`. |
| Zillow Listing Postal Code | `Zillow_Listing_Postal_Code` | Single line | Zillow `listingPostalCode`; keep as text, not number. |
| Zillow Listing Contact Email | `Zillow_Listing_Contact_Email` | Email | Zillow `listingContactEmail`. |
| Zillow Source Payload Hash | `Zillow_Source_Payload_Hash` | Single line | SHA-256 hash of the raw callback body for troubleshooting. |
| Zillow Received At | `Zillow_Received_At` | Date-time | Endpoint receive time. |
| Last Zillow Sync At | `Last_Zillow_Sync_At` | Date-time | Updated on every successful callback/upsert. |
| Zillow Intake Status | `Zillow_Intake_Status` | Picklist | Technical intake/routing status. |
| Zillow Raw Field Keys | `Zillow_Raw_Field_Keys` | Multi Line Large | Field names received, not raw private values. |
| Zillow Raw Payload Stored | `Zillow_Raw_Payload_Stored` | Checkbox | Set to false unless raw payloads are stored in an approved secure system. |
| Description | `Description` | Standard long text | Sanitized summary, Zillow profile details, and routing warnings. |

Do **not** create Phase 2 fields for `Manual_Review_Required`, `Manual_Review_Reason`, `Desired_Rent`, or `Desired_Deposit`. Manual review is a business action, not a Zillow-intake field, and rent/deposit must come from GH Real Estate's approved property/unit/lease records.

If actual CRM API names differ from the verified names above, set `ZOHO_CRM_FIELD_MAP_JSON` in the runtime config.

## Picklists

### Lead Status

- New Zillow Inquiry
- Contact Attempted
- Contacted
- Showing Scheduled
- Showing Completed
- Application Invited
- Application Received
- Not Qualified
- No Response
- Converted To Applicant
- Closed - Duplicate
- Closed - Not Interested

### Zillow Intake Status

- Received
- Updated
- Routing Matched
- Routing Unmatched
- Test Callback
- Failed

### Zillow Lead Type

- question
- tourRequest
- applicationRequest

### Zillow Move-In Timeframe

- asap
- flexible
- week
- month
- twoWeeks
- twoMonths

## Source-of-Truth Rule

Zillow remains the listing/application source for now. Zoho CRM Leads becomes the raw inquiry pipeline after intake. Contacts and Rental Applications should be created only after qualification, application review, or owner approval.
