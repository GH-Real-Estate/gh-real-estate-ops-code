# Zoho Books Automation Settings

Document non-secret IDs and API names needed by automation. Do not include tenant PII, payment records, or credentials.

## Known settings

| Setting | Value | Notes |
|---|---|---|
| Zoho Books connection name | TODO | Example: `zbooks`; verify in Zoho |
| Late-fee item ID | TODO | Non-secret, but verify before live deployment |
| Late-fee invoice template name | TODO | Example: `Fee Invoice - Late Fee` if still current |
| Late-fee invoice template ID | TODO | Verify before live deployment |
| Interest item ID | TODO | Do not enable interest automation until set |
| Returned-payment fee item ID | TODO | Separate automation |
| Duplicate-prevention custom field | TODO | Strongly recommended before live deployment |
| Rent invoice type/filter | TODO | Define how code identifies rent invoices |
| Excluded invoices/items | TODO | Prevent accidental fees on non-rent invoices |

## Field naming convention

Use Zoho API names, not display labels, whenever possible.

## Change log

| Date | Change | Verified by |
|---|---|---|
| 2026-07-01 | Starter placeholder created | Gabriel |
