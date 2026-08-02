# Zoho CRM Formula Field Notes — July 29, 2026

**Status:** Current tenant evidence and implementation reference  
**Scope:** Zoho CRM Formula custom fields only  
**Evidence date:** July 29, 2026

> A Zoho CRM Formula Field is not Deluge. Use the Formula Properties expression grammar, exact inserted field tokens, supported functions, operators, and parentheses.

## 1. String Return-Type Migration Warning

The GH Real Estate production Setup page displayed this warning on July 29, 2026:

> Formula String return type will soon be split based on character limit to enhance performance. Please review and update your formula string return types to ensure correct mapping. Click here to update the types in all modules. Complete it before Jul 31, 2026 to avoid disruption.

**Evidence classification:** `TENANT_UI_OBSERVED`

The screenshot establishes a live tenant deadline, but it does not show the new subtype names, exact character bands, API representation, or whether Zoho will auto-map any formulas. Do not invent those values.

### Required Operator Action

1. Open the tenant-wide review action before July 31, 2026.
2. Inventory every existing String-return Formula Field across all modules.
3. Record module, layout, field label, verified API name, exact expression, current metadata, expected maximum output length, and downstream consumers.
4. Select only among the exact character-limit options shown by the live Zoho migration wizard.
5. Test blank/null behavior, ordinary output, longest legitimate output, API metadata/readback, search/filter/report behavior, exports, and any Contracts or other downstream mapping.
6. Preserve before/after evidence and a rollback or replacement-field plan.

Changing the String return mapping is a CRM configuration change. It does not prove that an expression, report, API consumer, export, or downstream mapping remains compatible.

## 2. Property Ownership Duration Recipe

### Requirement

Calculate elapsed calendar duration from `${Properties.Purchase Date}` through `Now()` and return text such as:

- `3 Years, 2 Months, 23 Days`
- `1 Year, 4 Months, 16 Days`
- `1 Year, 1 Month, 1 Day`

Zero uses the plural label, for example `0 Years` or `0 Days`. A blank Purchase Date returns an empty string.

### Field Configuration

| Property | Value |
|---|---|
| Module | Properties — standard Accounts module renamed for display |
| Formula Return Type | String |
| Participating Field | `${Properties.Purchase Date}` |
| Current-Time Function | `Now()` |
| Real-Time Auto-Refresh | **Disabled**; see limitation below |
| Existing-Record Backfill | Requires a controlled update of a participating field |

### Paste-Ready Formula Expression

```text
If(IsEmpty(${Properties.Purchase Date}),'',Concat(Tostring(DateBetween(${Properties.Purchase Date},Now(),'years')),If(DateBetween(${Properties.Purchase Date},Now(),'years')==1,' Year, ',' Years, '),Tostring(DateBetween(Adddate(${Properties.Purchase Date},DateBetween(${Properties.Purchase Date},Now(),'years'),'YEAR'),Now(),'months')),If(DateBetween(Adddate(${Properties.Purchase Date},DateBetween(${Properties.Purchase Date},Now(),'years'),'YEAR'),Now(),'months')==1,' Month, ',' Months, '),Tostring(DateBetween(Adddate(Adddate(${Properties.Purchase Date},DateBetween(${Properties.Purchase Date},Now(),'years'),'YEAR'),DateBetween(Adddate(${Properties.Purchase Date},DateBetween(${Properties.Purchase Date},Now(),'years'),'YEAR'),Now(),'months'),'MONTH'),Now(),'days')),If(DateBetween(Adddate(Adddate(${Properties.Purchase Date},DateBetween(${Properties.Purchase Date},Now(),'years'),'YEAR'),DateBetween(Adddate(${Properties.Purchase Date},DateBetween(${Properties.Purchase Date},Now(),'years'),'YEAR'),Now(),'months'),'MONTH'),Now(),'days')==1,' Day',' Days')))
```

### Calculation Method

The expression:

1. calculates whole elapsed years;
2. advances Purchase Date by those whole years;
3. calculates whole remaining months;
4. advances the intermediate date by those whole months;
5. calculates whole remaining days; and
6. selects singular or plural labels independently for Years, Months, and Days.

This avoids the inaccurate shortcut of dividing total days by 365 and 30.

### Material Auto-Refresh Limitation

Current official Zoho CRM help lists both `DateBetween` and `Tostring` as unsupported in Formula Fields configured for real-time `Now()` auto-refresh. Therefore, do **not** enable **Automatically refresh formula fields containing the Now function in real-time** for this expression.

Without real-time auto-refresh, a `Now()` formula refreshes when the record is manually refreshed or edited, or when an automation updates the record. Auto-refresh itself is not treated as a record edit and does not reliably produce an auditable daily update event.

If GH requires a persisted text value to update every day without user activity, use a separately approved scheduled CRM Function or other controlled automation that writes a normal text snapshot field. Do not approximate calendar years and months merely to force the logic into an auto-refresh Formula Field.

## 3. Required Canary Tests

Before relying on the formula, use sanitized test records covering:

| Case | Expected Behavior |
|---|---|
| Purchase Date blank | Empty string |
| Purchase Date today | `0 Years, 0 Months, 0 Days` |
| Exactly one year, one month, one day elapsed | `1 Year, 1 Month, 1 Day` |
| Component equals zero | Plural label for that component |
| January 29–31 purchase | Verify Zoho month-end rollover semantics |
| February 29 purchase | Verify leap-year anniversary semantics |
| Future Purchase Date | Reject operationally or document the negative-result behavior |
| Existing production record | Confirm a participating-field update computes the new field |
| July 2026 String migration | Confirm the selected live String subtype accepts the maximum expected output |
| Metadata readback | Exact expression, return type, API name, and dynamic setting match the approved specification |

## 4. Official Technical Anchors

- Zoho CRM Help — Creating Formula Fields: `https://help.zoho.com/portal/en/kb/crm/customize-crm-account/customizing-fields/articles/create-formula-fields`
- Zoho CRM API V8 — Create Custom Field: `https://www.zoho.com/crm/developer/docs/api/v8/create-custom-field.html`

## 5. Change Boundary

This documentation does not create or modify a live Formula Field, remap an existing String formula, update CRM records, backfill existing records, enable auto-refresh, or prove target-tenant compiler behavior. Live implementation requires Formula Properties syntax validation, representative canaries, Fields Metadata readback, and controlled existing-record handling.