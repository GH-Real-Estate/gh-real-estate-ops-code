# Zillow Lead Intake

Secure intake service for Zillow Rentals lead callbacks. It receives Zillow's URL-encoded lead POST, validates it, builds a stable duplicate-prevention key, then upserts a Zoho CRM `Leads` record.

This first automation slice creates or updates CRM Leads only. It does not create Contacts, Rental Applications/Deals, leases, Books invoices, Creator tenant portal records, or WorkDrive folders. Those belong after qualification or approval.

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

| Business field | Default API name | Type | Notes |
|---|---|---|---|
| First Name | `First_Name` | Standard | Parsed from Zillow `name`. |
| Last Name | `Last_Name` | Standard | Required by Zoho Leads. Uses `Zillow Prospect` if no name is supplied. |
| Company | `Company` | Standard / Single Line | Hidden is fine, but the API write still populates it. |
| Email | `Email` | Email | Maps to Zillow `email`. |
| Mobile | `Mobile` | Phone | Maps to Zillow `phone`. |
| Lead Source | `Lead_Source` | Picklist | Use `Zillow`. |
| Lead Status | `Lead_Status` | Picklist | Default for new intake should be `New Zillow Inquiry`. |
| Requested Property | `Requested_Property` | Lookup to Properties | Optional lookup resolved from property/unit map. |
| Requested Unit | `Requested_Unit` | Lookup to Units | Optional lookup resolved from property/unit map. |
| Requested Move-In Date | `Requested_Move_In_Date` | Date | Maps to Zillow `movingDate`. |
| Inquiry Message | `Inquiry_Message` | Multi-Line | Maps to Zillow `message`. |
| Zillow Renter Profile Summary | `Zillow_Renter_Profile_Summary` | Multi-Line | Summary of optional renter profile fields. |
| Zillow Lead Key | `Zillow_Lead_Key` | Single Line / Unique | Main idempotent upsert key. Mark unique. |
| Zillow Lead ID | `Zillow_Lead_ID` | Single Line | Optional compatibility field. Zillow's guide does not require this. |
| Zillow Listing ID | `Zillow_Listing_ID` | Single Line | Maps to Zillow `listingId`; strongest routing key. |
| Zillow Listing URL | `Zillow_Listing_URL` | URL | Optional if supplied. |
| Zillow Lead Type | `Zillow_Lead_Type` | Picklist | `question`, `tourRequest`, `applicationRequest`. |
| Zillow Provider Model ID | `Zillow_Provider_Model_ID` | Single Line | Maps to Zillow `providerModelId`. |
| Zillow Move-In Timeframe | `Zillow_Move_In_Timeframe` | Picklist | `asap`, `flexible`, `week`, `month`, `twoWeeks`, `twoMonths`. |
| Zillow Property Address Raw | `Zillow_Property_Address_Raw` | Single Line | Combined readable listing address. |
| Zillow Listing Street | `Zillow_Listing_Street` | Single Line | Maps to Zillow `listingStreet`. |
| Zillow Listing Unit | `Zillow_Listing_Unit` | Single Line | Maps to Zillow `listingUnit`. |
| Zillow Listing City | `Zillow_Listing_City` | Single Line | Maps to Zillow `listingCity`. |
| Zillow Listing State | `Zillow_Listing_State` | Single Line | Maps to Zillow `listingState`. |
| Zillow Listing Postal Code | `Zillow_Listing_Postal_Code` | Single Line | Maps to Zillow `listingPostalCode`; keep as text, not number. |
| Zillow Listing Contact Email | `Zillow_Listing_Contact_Email` | Email | Maps to Zillow `listingContactEmail`. |
| Zillow Received At | `Zillow_Received_At` | Date-Time | Endpoint receipt timestamp. |
| Last Zillow Sync At | `Last_Zillow_Sync_At` | Date-Time | Last processed timestamp. |
| Zillow Intake Status | `Zillow_Intake_Status` | Picklist | Technical intake/routing status. |
| Zillow Source Payload Hash | `Zillow_Source_Payload_Hash` | Single Line | Hash for audit/debugging. |
| Zillow Raw Field Keys | `Zillow_Raw_Field_Keys` | Multi-Line | Field names received, not raw private values. |
| Zillow Raw Payload Stored | `Zillow_Raw_Payload_Stored` | Checkbox | Leave false unless raw payloads are stored in an approved secure system. |
| Description | `Description` | Standard Multi-Line | Sanitized internal summary. |

Do not use `Desired_Rent`, `Desired_Deposit`, `Manual_Review_Required`, or `Manual_Review_Reason` for this intake. GH Real Estate manually reviews every Zillow Lead through Lead Status and saved views. Rent and deposit must come from approved property/unit/lease records, not a prospect preference.

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
- Converted to Applicant
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

Zillow remains the listing inquiry source for now. Zoho CRM Leads becomes the raw inquiry pipeline after intake. Contacts and Rental Applications should be created only after qualification, application review, or owner approval.
