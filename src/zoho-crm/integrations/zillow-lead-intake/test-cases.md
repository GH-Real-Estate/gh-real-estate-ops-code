# Test Cases

## Automated

Run:

```powershell
npm run ci
```

Coverage:

- Official URL-encoded Zillow payload parsing.
- Official Zillow camelCase field normalization.
- `YYYYMMDD` and normal date parsing.
- email/phone validation.
- stable idempotency key generation that does not depend on mutable message text.
- property/unit map resolution by Zillow `listingId`.
- CRM Lead payload construction.
- confirmation that deleted fields are not mapped: `Manual_Review_Required`, `Manual_Review_Reason`, `Desired_Rent`, `Desired_Deposit`.
- strict rejection of JSON payloads unless explicitly enabled for internal tests.
- missing security header rejection.
- authenticated dry-run response.

## Manual Dry-Run Cases

| Case | Expected |
|---|---|
| Complete fake lead | `ok=true`, `mode=dry_run`, planned Lead fields. |
| Missing email but phone present | Accepted. User reviews manually in normal Zillow lead queue. |
| Missing phone but email present | Accepted. User reviews manually in normal Zillow lead queue. |
| Missing email and phone | Rejected with `invalid_lead_payload`. |
| Unknown listing ID | Accepted with routing warning unless `REQUIRE_ROUTE_MATCH_FOR_SUCCESS=true`. |
| Duplicate payload sent twice | Same `lead_reference` and same `Zillow_Lead_Key`. |
| Missing `x-gh-zillow-webhook-key` | Rejected with `inbound_secret_invalid`. |
| Wrong `content-type` | Rejected with `unsupported_content_type`. |

## Manual Live Cases

Only run after dry-run passes.

1. Send complete fake lead.
2. Confirm one CRM Lead exists.
3. Send the exact same payload again.
4. Confirm the Lead was updated, not duplicated.
5. Confirm no Contact, Rental Application/Deal, lease, Books invoice, tenant portal record, or WorkDrive folder was created.
