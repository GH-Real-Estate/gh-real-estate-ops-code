# Zoho CRM Leads Layout for Zillow Intake

Use this layout for Zillow Rentals Lead Delivery API intake.

## Section Order

```text
1. Lead Information
2. Inquiry Details
3. Zillow Routing
4. Zillow Listing Address
5. Zillow Audit
6. System Reference
7. Visit Summary hidden/unused
```

Hide `Title`, `Middle Name`, standard address fields, and `Visit Summary` unless those standard fields are actively used outside Zillow intake.

## Lead Information

Use two columns.

| Row | Left | Type | Right | Type |
|---|---|---|---|---|
| 1 | First Name | Standard name | Lead Status | Picklist |
| 2 | Last Name | Standard text, required | Lead Source | Picklist |
| 3 | Email | Email | Requested Property | Lookup |
| 4 | Mobile | Phone | Requested Unit | Lookup |
| 5 | Zillow Lead Type | Picklist | Requested Move-In Date | Date |

`Company` may stay in unused items visually, but it must remain available for API writes because Zoho Leads may require it.

## Inquiry Details

Use one column.

| Row | Field | Type |
|---|---|---|
| 1 | Inquiry Message | Multi Line Large preferred; Rich Text acceptable if already created |
| 2 | Zillow Renter Profile Summary | Multi Line Large preferred; Rich Text acceptable if already created |
| 3 | Description | Standard long text |

`Inquiry Message` stores Zillow `message` plus optional `introduction`. `Zillow Renter Profile Summary` stores optional renter profile fields without creating too many raw Lead fields. The service writes plain text to both fields.

Do not add `Desired Rent`, `Desired Deposit`, `Manual Review Required`, or `Manual Review Reason` to this layout.

## Zillow Routing

Use two columns.

| Row | Left | Type | Right | Type |
|---|---|---|---|---|
| 1 | Zillow Lead Key | Single line, unique | Zillow Intake Status | Picklist |
| 2 | Zillow Listing ID | Single line | Zillow Received At | Date-time |
| 3 | Zillow Provider Model ID | Single line | Last Zillow Sync At | Date-time |
| 4 | Zillow Listing Contact Email | Email | Zillow Source Payload Hash | Single line |
| 5 | Zillow Move-In Timeframe | Picklist |  |  |

Recommended `Zillow Intake Status` values:

```text
Received
Updated
Routing Matched
Routing Unmatched
Test Callback
Failed
```

## Zillow Listing Address

Use two columns.

| Row | Left | Type | Right | Type |
|---|---|---|---|---|
| 1 | Zillow Property Address Raw | Single line | Zillow Listing Unit | Single line |
| 2 | Zillow Listing Street | Single line | Zillow Listing State | Single line |
| 3 | Zillow Listing City | Single line | Zillow Listing URL | URL |
| 4 | Zillow Listing Postal Code | Single line |  |  |

`Zillow Property Address Raw` should stay single line because it stores the raw/composed Zillow listing address. The verified API name is `Zillow_Property_Address`. The clean operating address remains on the Property and Unit records.

## Zillow Audit

Use one column.

| Row | Field | Type |
|---|---|---|
| 1 | Zillow Raw Field Keys | Multi Line Large |
| 2 | Zillow Raw Payload Stored | Checkbox |
| 3 | Zillow Lead ID | Single line |

`Zillow Raw Payload Stored` should be left as a checkbox indicator. The service sets it to `false` because raw payload values are not stored in CRM by default.

## System Reference

Use two columns.

| Row | Left | Type | Right | Type |
|---|---|---|---|---|
| 1 | Created By | System | Lead Owner | User lookup |
| 2 | Modified By | System |  |  |
