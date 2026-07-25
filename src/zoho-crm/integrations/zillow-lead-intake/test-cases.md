# Test Cases

## Automated

Run:

```powershell
npm run ci
```

Coverage:

- URL-encoded payload parsing.
- Official Zillow camelCase field normalization.
- email/phone validation.
- stable idempotency key generation.
- property/unit map resolution.
- verified `Units`, `Unit_I_D`, and `Unit_Status` runtime defaults.
- explicit `ZOHO_CRM_UNITS_MODULE` override behavior.
- exclusion of stale `Zillow_Property_Address` and prohibited `Zillow_Raw_Payload` mappings.
- CRM Lead payload construction.
- exclusion of removed fields: `Desired_Rent`, `Desired_Deposit`, `Manual_Review_Required`, `Manual_Review_Reason`.
- URL-encoded content type default.

## Manual Dry-Run Cases

| Case | Expected |
|---|---|
| Complete fake lead | `ok=true`, `mode=dry_run`, planned Lead fields. |
| Missing email but phone present | Accepted with routing warning in response/Description. |
| Missing phone but email present | Accepted with routing warning in response/Description. |
| Missing email and phone | Rejected with `invalid_lead_payload`. |
| Unknown listing ID | Accepted with routing warning; no Contact/Application/Lease created. |
| Duplicate payload sent twice | Same `lead_reference` and same `Zillow_Lead_Key`. |
| JSON payload while `ALLOW_JSON_PAYLOADS=false` | Rejected with `unsupported_content_type`. |
| Missing shared-secret header | Rejected with `inbound_secret_invalid`. |

## Manual Live Cases

Only run after dry-run passes.

1. Send complete fake lead.
2. Confirm one CRM Lead exists.
3. Send the exact same payload again.
4. Confirm the Lead was updated, not duplicated.
5. Confirm no Contact, Rental Application/Deal, lease, Books invoice, tenant portal record, or WorkDrive folder was created.
