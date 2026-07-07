# Operations Runbook

## Setup Sequence

1. Create/confirm CRM Leads custom fields listed in `README.md`.
2. Arrange the Leads layout using `docs/crm-leads-layout.md`.
3. Mark `Zillow_Lead_Key` unique in the Leads module.
4. Create a Zoho OAuth client with CRM module create/write scopes.
5. Generate a refresh token and store it only in Catalyst environment variables.
6. Deploy the service with `DRY_RUN=true`.
7. Send the fake sample payload.
8. Send a Zillow test payload if Zillow supports test delivery.
9. Confirm dry-run planned fields match Zoho field API names.
10. Configure `PROPERTY_UNIT_MAP_JSON` with real CRM Property/Unit IDs.
11. Switch to live mode only after a dry-run sample has no field errors.

## Live Smoke Test

Use a fake lead email and phone number:

```text
test.tenant@example.com
913-555-0100
```

Expected CRM outcome:

- One CRM Lead with Lead Source `Zillow`.
- Lead has `Zillow_Lead_Key`.
- Lead has `Zillow_Intake_Status=Received`.
- Lead has `Zillow_Received_At` and `Last_Zillow_Sync_At`.
- Re-sending the same payload updates the same Lead, not a duplicate.
- No Contact or Rental Application/Deal is created by this webhook.

## Routing Review Queue

GH manually reviews every lead, so the service should not write `Manual_Review_Required` or `Manual_Review_Reason`.

Create a CRM Leads view for routing review if desired:

```text
Lead Source = Zillow
AND
(Requested Property is empty OR Requested Unit is empty)
```

Routing warnings belong in `Description`, not separate manual review fields.

## Failure Handling

| Failure | Action |
|---|---|
| `inbound_secret_invalid` | Confirm Zillow endpoint URL/header secret. Rotate if exposed. |
| `invalid_lead_payload` | Zillow sent a lead without usable email/phone. Review source payload in Zillow. |
| `zoho_oauth_not_configured` | Add OAuth environment variables in Catalyst. |
| `zoho_upsert_failed` | Check CRM field API names, required field rules, and picklist values. |
| Duplicate leads | Confirm Leads field `Zillow_Lead_Key` exists and is marked unique. |

## Rollback

1. Set `DRY_RUN=true`.
2. Redeploy or restart Catalyst function.
3. Disable Zillow delivery to the webhook if bad records continue.
4. Use CRM list view filtered by source `Zillow` and created time to inspect records.
5. Do not bulk delete live records until duplicates are understood and exported.
