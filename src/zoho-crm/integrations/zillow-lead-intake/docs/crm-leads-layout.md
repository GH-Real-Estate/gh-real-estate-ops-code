# Zoho CRM Leads Layout for Zillow Intake

Use this layout for Phase 2 Zillow Rentals lead delivery.

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
| 3 | Zillow Listing ID | Single line | Zillow Source Payload Hash | Single line |
| 4 | Zillow Listing URL | URL | Zillow Received At | Date-time |
| 5 | Zillow Raw Payload | Checkbox | Last Zillow Sync At | Date-time |

`Zillow Property Address` should stay single line because it stores the raw/composed Zillow listing address. The clean operating address remains on the Property and Unit records.

Recommended `Zillow Intake Status` values:

```text
Received
Duplicate Updated
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
