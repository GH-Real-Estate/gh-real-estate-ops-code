# Operations Runbook

## Setup Sequence

1. Create/confirm CRM custom fields listed in `README.md`.
2. Mark `Zillow_Lead_Key` unique in the Rental Applications/Deals module.
3. Create a Zoho OAuth client with CRM module create/write scopes.
4. Generate a refresh token and store it only in Catalyst environment variables.
5. Deploy the service with `DRY_RUN=true`.
6. Send the fake sample payload.
7. Send a Zillow test payload if Zillow supports test delivery.
8. Confirm dry-run planned fields match Zoho field API names.
9. Configure `PROPERTY_UNIT_MAP_JSON` with real CRM Property/Unit IDs.
10. Switch to live mode only after a dry-run sample has no field errors.

## Live Smoke Test

Use a fake lead email and phone number:

```text
test.tenant@example.com
913-555-0100
```

Expected CRM outcome:

- One Contact with Contact Type `Applicant`.
- One Rental Application/Deal in stage `New Inquiry`.
- Rental Application has `Zillow_Lead_Key`.
- Re-sending the same payload updates the same Rental Application, not a duplicate.

## Manual Review Queue

The service marks `Manual_Review_Required=true` when:

- name is missing
- email is missing
- phone is missing
- Zillow listing ID/address is missing
- no property/unit mapping matched
- desired move-in date is missing

Create a CRM view for Rental Applications where `Manual_Review_Required` is true.

## Failure Handling

| Failure | Action |
|---|---|
| `inbound_secret_invalid` | Confirm Zillow endpoint URL/header secret. Rotate if exposed. |
| `invalid_lead_payload` | Zillow sent a lead without usable email/phone. Review source payload in Zillow. |
| `zoho_oauth_not_configured` | Add OAuth environment variables in Catalyst. |
| `zoho_upsert_failed` | Check CRM field API names and required field rules. |
| Duplicate applications | Confirm `Zillow_Lead_Key` exists and is marked unique. |

## Rollback

1. Set `DRY_RUN=true`.
2. Redeploy or restart Catalyst function.
3. Disable Zillow delivery to the webhook if bad records continue.
4. Use CRM list view filtered by source `Zillow` and created time to inspect records.
5. Do not bulk delete live records until duplicates are understood and exported.
