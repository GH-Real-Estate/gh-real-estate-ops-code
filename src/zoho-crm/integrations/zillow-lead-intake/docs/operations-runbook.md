# Operations Runbook

## Setup Sequence

1. Create/confirm CRM Leads custom fields listed in `README.md`.
2. Mark `Zillow_Lead_Key` unique in the Leads module.
3. Confirm hidden standard/system fields remain available for API writes when required.
4. Create the Zoho CRM API credentials needed by the runtime.
5. Store runtime values only in the approved runtime environment manager.
6. Deploy the service with dry-run enabled.
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
- Lead Status is `New Zillow Inquiry`.
- Re-sending the same payload updates the same Lead, not a duplicate.
- No Contact or Rental Application/Deal is created by this webhook.

## Review Queues

GH Real Estate manually reviews every Zillow Lead. Use saved views instead of separate manual-review fields.

Create these CRM Leads views:

| View | Filter |
|---|---|
| Zillow Leads - New Inquiry | `Lead Source = Zillow` and `Lead Status = New Zillow Inquiry` |
| Zillow Leads - Routing Unmatched | `Lead Source = Zillow` and `Zillow Intake Status = Routing Unmatched` |
| Zillow Leads - Recently Synced | `Lead Source = Zillow` and `Last Zillow Sync At` is recent |

## Failure Handling

| Failure | Action |
|---|---|
| `inbound_secret_invalid` | Confirm Zillow endpoint URL/header configuration. Rotate if exposed. |
| `invalid_lead_payload` | Zillow sent a lead without usable email/phone. Review source payload with Zillow. |
| `zoho_oauth_not_configured` | Add the missing CRM API runtime values. |
| `zoho_upsert_failed` | Check CRM field API names and required field rules. |
| Duplicate leads | Confirm Leads field `Zillow_Lead_Key` exists and is marked unique. |
| Routing unmatched | Update `PROPERTY_UNIT_MAP_JSON` or review the listing address/contact email. |

## Rollback

1. Re-enable dry-run mode.
2. Redeploy or restart the runtime.
3. Ask Zillow to pause delivery to the endpoint if bad records continue.
4. Use CRM list view filtered by source `Zillow` and created time to inspect records.
5. Do not bulk delete live records until duplicates are understood and exported.
