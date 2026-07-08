# Operations Runbook

## Setup Sequence

1. Create/confirm CRM Leads custom fields listed in `README.md`.
2. Arrange the Leads layout using `docs/crm-leads-layout.md`.
3. Mark `Zillow_Lead_Key` unique in the Leads module.
4. Create a Zoho OAuth client with CRM module create/write/read scopes.
5. Generate a refresh token and store it only in Catalyst environment variables.
6. Generate a long random `ZILLOW_WEBHOOK_KEY`.
7. Configure the CRM Units module for routing using `docs/unit-routing-setup.md`.
8. Deploy the service with Catalyst Development set to dry-run.
9. Send the fake sample payload from `samples/zillow-lead.sample.urlencoded`.
10. Confirm dry-run planned fields match Zoho field API names.
11. Confirm the matching Unit record has `Zillow_Routing_Unit_Key` or the real Zillow `Zillow_Listing_ID`.
12. Ask Zillow to configure the endpoint in test mode and send a test callback.
13. Switch Catalyst Production to live mode only after a Zillow dry-run sample has no field errors and routing is understood.

## Catalyst Environment Rule

Development and Production must be treated as separate runtime environments.

```text
Development: dry-run, no CRM Lead writes
Production: live only after explicit approval and smoke testing
```

Do not set both environments to live as a normal operating mode. If Development is temporarily made live for an internal smoke test, revert it immediately after the test.

## Placeholder Rule

Commands in this runbook use angle-bracket placeholders such as `<your-catalyst-invocation-url>`, `<runtime secret>`, and `<your-health-token>`.

Do not paste those placeholders literally into PowerShell. Replace them with real values from the target Catalyst environment before running the command.

Bad:

```powershell
$healthEndpoint = "https://<your-catalyst-domain>/health"
```

Good:

```powershell
$healthEndpoint = "https://zillow-lead-intake-000000000.catalystserverless.com/server/Zillow-Lead-Intake/health"
```

The same rule applies to every token, key, client ID, client secret, refresh token, and endpoint URL.

## PowerShell Paste Rule

When pasting a multi-line block, prefer direct variable assignment over `Read-Host`.

Bad for pasted blocks:

```powershell
$leadEndpoint = Read-Host "https://actual-catalyst-url/server/Zillow-Lead-Intake/"
$healthToken = Read-Host "actual-token"
```

`Read-Host` treats the quoted text as the prompt and then waits for input. If several lines are pasted at once, PowerShell may accidentally store the next command as the value.

Good for pasted blocks:

```powershell
$functionBaseUrl = "https://actual-catalyst-url/server/Zillow-Lead-Intake/"
$healthToken = "actual-token"
```

## Health Check Test

Temporarily enable the protected health route in the target Catalyst environment:

```text
ENABLE_HEALTH=true
HEALTH_HEADER_NAME=x-gh-health-token
HEALTH_CHECK_TOKEN=<runtime health token>
```

Use distinct gateway versions so the response proves which environment is being hit:

```text
Development: GATEWAY_VERSION=dev-2026-07-08
Production: GATEWAY_VERSION=prod-2026-07-08
```

Then restart or redeploy that same environment and run this using the Catalyst **Invocation URL** copied from the function Overview screen:

```powershell
$functionBaseUrl = "https://<actual-catalyst-domain>/server/Zillow-Lead-Intake/"
$healthToken = "<actual-health-token>"

$functionBaseUrl = $functionBaseUrl.Trim()
if (-not $functionBaseUrl.EndsWith("/")) { $functionBaseUrl += "/" }

$healthEndpoint = $functionBaseUrl + "health"

Write-Host "Testing health endpoint:"
Write-Host $healthEndpoint

Invoke-RestMethod `
  -Method Get `
  -Uri $healthEndpoint `
  -Headers @{ "x-gh-health-token" = $healthToken }
```

Expected Production response includes:

```json
{
  "ok": true,
  "service": "gh-zillow-lead-intake",
  "version": "prod-2026-07-08",
  "mode": "live",
  "crm_target_module": "Leads"
}
```

If the response says `dev-...` or `mode=dry_run`, the request is not hitting the intended live Production runtime.

## Zillow Configuration To Request

```text
Endpoint: <Catalyst Production Invocation URL>zillow/leads
Method: POST
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
Security: static header x-gh-zillow-webhook-key
Mode: Zillow test environment only until GH confirms production approval
```

Do not send runtime secrets in plain email or commit them to GitHub.

## Local Dry-Run Test

```bash
curl -i \
  -X POST "https://<actual-catalyst-domain>/server/Zillow-Lead-Intake/zillow/leads" \
  -H "Content-Type: application/x-www-form-urlencoded; charset=UTF-8" \
  -H "x-gh-zillow-webhook-key: <runtime secret>" \
  --data-binary @samples/zillow-lead.sample.urlencoded
```

Expected response:

```text
HTTP 202
mode=dry_run
```

## Live Smoke Test

Use a fake lead email and phone number:

```text
test.tenant@example.com
913-555-0100
```

Expected CRM outcome:

- One CRM Lead with Lead Source `Zillow`.
- Lead has `Zillow_Lead_Key`.
- Lead has `Zillow_Intake_Status=Received`, `Routing Matched`, or `Routing Unmatched` depending on routing result.
- Lead has `Zillow_Received_At` and `Last_Zillow_Sync_At`.
- Re-sending the same payload updates the same Lead, not a duplicate.
- No Contact, Rental Application/Deal, lease, Books invoice, tenant portal record, or WorkDrive folder is created by this webhook.

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
| `Cannot convert value "https://<your-catalyst-domain>/health" to type System.Uri` | Replace the placeholder with the actual Catalyst endpoint URL from the target environment. |
| Health URL contains `: $healthToken = Read-Host` or another command | Stop using `Read-Host` in pasted blocks. Clear the variables and use direct assignment. |
| `mode=dry_run` after Production is supposed to be live | Confirm you are testing the Production URL, then confirm Production runtime variables and restart/redeploy Production. |
| `live_mode_disabled` | Set `LIVE_MODE_ENABLED=true` in the target Catalyst environment. |
| `live_mode_confirmation_missing` | Set exact `LIVE_MODE_CONFIRMATION=GH_ZILLOW_LEAD_INTAKE_LIVE_APPROVED` in the target Catalyst environment. |
| `inbound_header_invalid` | Confirm Zillow endpoint URL and shared header. Rotate if exposed. |
| `unsupported_content_type` | Confirm Zillow is sending URL-encoded form data, not JSON. |
| `invalid_lead_payload` | Zillow sent a lead without usable email/phone. Review with Zillow Support. |
| `zoho_oauth_not_configured` | Add OAuth environment variables in Catalyst. |
| `zoho_oauth_failed` | Exchange a new Zoho grant code for a new refresh token and update `ZOHO_REFRESH_TOKEN`. |
| `zoho_upsert_failed` | Check CRM field API names, required field rules, and picklist values. |
| Duplicate leads | Confirm Leads field `Zillow_Lead_Key` exists and is marked unique. |

## Rollback

1. Set `ZILLOW_WEBHOOK_DRY_RUN=true` and `DRY_RUN=true` in the affected Catalyst environment.
2. Redeploy or restart the Catalyst function in that same environment.
3. Disable Zillow delivery to the webhook if bad records continue.
4. Use CRM list view filtered by source `Zillow` and created time to inspect records.
5. Do not bulk delete live records until duplicates are understood and exported.
