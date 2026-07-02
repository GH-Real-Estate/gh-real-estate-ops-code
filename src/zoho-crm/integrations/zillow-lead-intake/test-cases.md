# Test Cases

## Automated

Run:

```powershell
npm run ci
```

Coverage:

- URL-encoded payload parsing.
- Zillow field alias normalization.
- email/phone validation.
- stable idempotency key generation.
- property/unit map resolution.
- CRM Lead payload construction.

## Manual Dry-Run Cases

| Case | Expected |
|---|---|
| Complete fake lead | `ok=true`, `mode=dry_run`, planned Lead fields. |
| Missing email but phone present | Accepted, manual review required. |
| Missing phone but email present | Accepted, manual review required. |
| Missing email and phone | Rejected with `invalid_lead_payload`. |
| Unknown listing ID | Accepted, manual review required. |
| Duplicate payload sent twice | Same `lead_reference` and same `Zillow_Lead_Key`. |

## Manual Live Cases

Only run after dry-run passes.

1. Send complete fake lead.
2. Confirm one CRM Lead exists.
3. Send the exact same payload again.
4. Confirm the Lead was updated, not duplicated.
5. Confirm no Contact, Rental Application/Deal, lease, Books invoice, or tenant portal record was created.
