# Zoho CRM Leads Layout for Zillow Intake

Use this layout for Zillow Rentals lead delivery.

## Section Order

```text
1. Lead Information
2. Zillow
3. Reference
4. System Notes
5. Visit Summary
```

Hide `Title`, `Middle Name`, and `Visit Summary` unless those standard fields are actively used.

## Lead Information

Use two columns.

| Row | Left | Type | Right | Type |
|---|---|---|---|---|
| 1 | First Name | Standard name | Lead Status | Picklist |
| 2 | Last Name | Standard text, required | Requested Property | Lookup |
| 3 | Company | Standard text, required | Requested Unit | Lookup |
| 4 | Email | Email | Requested Move-In Date | Date |
| 5 | Phone | Phone | Inquiry Message | Multi-line text |
| 6 | Mobile | Phone |  |  |

`Inquiry Message` should be multi-line text.

## Zillow

Use two columns.

| Row | Left | Type | Right | Type |
|---|---|---|---|---|
| 1 | Zillow Lead Key | Single line, unique | Zillow Intake Status | Picklist |
| 2 | Zillow Lead ID | Single line | Zillow Property Address | Single line |
| 3 | Zillow Listing ID | Single line | Zillow Lead Type | Picklist |
| 4 | Zillow Listing URL | URL | Zillow Provider Model ID | Single line |
| 5 | Zillow Source Payload Hash | Single line | Zillow Received At | Date-time |
| 6 | Zillow Raw Field Keys | Multi-line/long text | Last Zillow Sync At | Date-time |

`Zillow Property Address` should stay single line because it stores the raw/composed Zillow listing address. The clean operating address remains on the Property and Unit records.

## Picklists

### Lead Status

```text
New Zillow Inquiry
Contact Attempted
Contacted
Showing Scheduled
Showing Completed
Application Invited
Application Received
Not Qualified
No Response
Converted to Applicant
Closed - Duplicate
Closed - Not Interested
```

### Zillow Lead Type

```text
question
tourRequest
applicationRequest
```

### Zillow Intake Status

```text
Received
Parsed
Upserted
Updated
Failed
Ignored
```

## Reference

Use two columns.

| Row | Left | Type | Right | Type |
|---|---|---|---|---|
| 1 | Lead Source | Picklist | Lead Owner | User lookup |
| 2 | Created By | System | Modified By | System |

## System Notes

Use one column.

| Row | Field | Type |
|---|---|---|
| 1 | Description | Standard long text |

## Fields Not Used

Do not create or map these for this intake:

```text
Manual Review Required
Manual Review Reason
Desired Rent
Desired Deposit
```

Manual review is always done by the owner. Rent and deposit are controlled by GH Real Estate records, not renter-submitted Zillow inquiry values.
