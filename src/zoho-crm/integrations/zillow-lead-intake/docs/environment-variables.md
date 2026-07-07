# Environment Variables

Use placeholders only in Git. Configure real values in Zoho Catalyst or another approved runtime configuration manager.

Do not store a Zoho `access_token` as an environment variable. Access tokens are short-lived. Store the refresh token only; the function exchanges it for fresh access tokens at runtime.

| Variable | Required | Default | Purpose |
|---|---:|---|---|
| `GATEWAY_VERSION` | Yes | `2026-07-07.v6` | Runtime version label surfaced in health checks. |
| `ALLOWED_PATHS` | Yes | `/zillow/leads` | Comma-separated POST paths accepted by the service. |
| `MAX_BODY_BYTES` | Yes | `65536` | Rejects oversized webhook bodies. |
| `INBOUND_BODY_TIMEOUT_MS` | Yes | `8000` | Rejects slow/incomplete request bodies. |
| `REQUIRE_INBOUND_SECRET` | Yes | `true` | Requires a shared header value before processing. |
| `INBOUND_SECRET_HEADER_NAME` | Yes | `x-gh-zillow-webhook-key` | Header checked for the inbound Zillow shared value. |
| `ZILLOW_WEBHOOK_KEY` | Yes | blank | Preferred runtime variable for the long random Zillow shared header value. |
| `INBOUND_SECRET_VALUE` | Alias | blank | Backward-compatible alias for `ZILLOW_WEBHOOK_KEY`. |
| `ALLOW_SECRET_QUERY_PARAM` | No | `false` | Allows key in query string only if Zillow cannot send headers. Keep disabled. |
| `INBOUND_SECRET_QUERY_PARAM` | No | `key` | Query parameter name for fallback shared key. |
| `ENFORCE_IP_ALLOWLIST` | No | `false` | Optional source IP gate. Enable only after confirming Zillow's observed source IPs in Catalyst logs. |
| `ALLOWED_IPS` | No | blank | Comma-separated IPs when `ENFORCE_IP_ALLOWLIST=true`. |
| `ZILLOW_WEBHOOK_DRY_RUN` | Yes | `true` | Preferred dry-run switch. |
| `DRY_RUN` | Yes | `true` | General dry-run switch retained for consistency with other Catalyst deployments. |
| `LIVE_MODE_ENABLED` | Yes | `false` | First live-mode circuit breaker. |
| `LIVE_MODE_CONFIRMATION` | Yes for live | blank | Must match expected value before CRM writes. Leave blank during dry-run. |
| `EXPECTED_LIVE_MODE_CONFIRMATION` | Yes | `GH_ZILLOW_LEAD_INTAKE_LIVE_APPROVED` | Second live-mode circuit breaker value. |
| `ALLOW_JSON_PAYLOADS` | No | `false` | Allows JSON only for internal testing. Zillow production should remain URL-encoded. |
| `GENERIC_PUBLIC_ERRORS` | No | `true` | Redacts 5xx details from public responses. 4xx errors still return useful codes. |
| `ENABLE_HEALTH` | No | `false` | Enables protected `GET /health`. |
| `HEALTH_HEADER_NAME` | No | `x-gh-health-token` | Header checked on health route. |
| `HEALTH_CHECK_TOKEN` | Required if health enabled | blank | Required token for health route. |
| `ENABLE_CACHE_REPLAY_DEFENSE` | No | `false` | Optional Catalyst Cache duplicate/replay guard. CRM upsert remains the main duplicate control. |
| `STRICT_REPLAY_FAILURE` | No | `false` | If true, cache failure rejects webhook with 503. |
| `REPLAY_CACHE_SEGMENT_ID` | No | blank | Optional Catalyst Cache segment ID. |
| `REPLAY_WINDOW_SECONDS` | No | `300` | Recent duplicate cache window. |
| `ZOHO_CLIENT_ID` | Yes for live | blank | Zoho OAuth client ID. |
| `ZOHO_CLIENT_SECRET` | Yes for live | blank | Zoho OAuth client credential. |
| `ZOHO_REFRESH_TOKEN` | Yes for live | blank | Zoho OAuth refresh token for CRM Leads. |
| `ZOHO_ACCOUNTS_BASE_URL` | Yes | `https://accounts.zoho.com` | Zoho Accounts base URL. |
| `ZOHO_CRM_BASE_URL` | Yes | `https://www.zohoapis.com` | Zoho CRM API base URL. |
| `ZOHO_CRM_API_VERSION` | Yes | `v8` | CRM API version. |
| `ACCOUNTS_ALLOWED_HOST_SUFFIXES` | Yes | `accounts.zoho.com` | Outbound host allowlist for Zoho Accounts. |
| `CRM_ALLOWED_HOST_SUFFIXES` | Yes | `zohoapis.com` | Outbound host allowlist for Zoho CRM. |
| `OUTBOUND_TIMEOUT_MS` | Yes | `15000` | Zoho API request timeout. |
| `ZOHO_CRM_LEADS_MODULE` | Yes | `Leads` | CRM Leads module API name. |
| `LEAD_DUPLICATE_CHECK_FIELDS` | Yes | `Zillow_Lead_Key` | Unique lead key. Create and mark this field unique. |
| `PROPERTY_UNIT_MAP_JSON` | No | `{}` | Maps Zillow listing/address/contact-email routing keys to CRM Property and Unit record IDs. |
| `ZOHO_CRM_FIELD_MAP_JSON` | No | `{}` | Overrides default API field names. Leave `{}` if the verified CRM API names match the README. |
| `ENABLE_CRM_INTAKE_EVENT_LOG` | No | `false` | Writes optional audit events to a custom CRM module. |
| `ENABLE_DRY_RUN_CRM_AUDIT_LOG` | No | `false` | Allows dry-run audit-event writes without creating Leads. |
| `ZOHO_CRM_INTAKE_EVENTS_MODULE` | No | `Zillow_Intake_Events` | Optional audit module API name. |
| `INTAKE_EVENT_DUPLICATE_CHECK_FIELDS` | No | `External_Event_Key` | Optional audit module duplicate key. |
| `CRM_TRIGGER_WORKFLOWS` | No | `false` | Enables Zoho CRM workflow triggers on upsert. |
| `CRM_TRIGGER_APPROVALS` | No | `false` | Enables Zoho CRM approval triggers on upsert. |
| `CRM_TRIGGER_BLUEPRINTS` | No | `false` | Enables Zoho CRM blueprint triggers on upsert. |
| `SKIP_CADENCES_ON_INSERT` | No | `true` | Skips CRM cadences on insert. |
| `SKIP_CADENCES_ON_UPDATE` | No | `false` | Skips CRM cadences on update. |
| `DEFAULT_LEAD_SOURCE` | Yes | `Zillow` | Default Lead Source. |
| `DEFAULT_LEAD_STATUS` | Yes | `New Zillow Inquiry` | Default Lead Status. |
| `DEBUG_ERRORS` | No | `false` | Adds sanitized error detail to server logs only. |

## Property/Unit Map Example

```json
{
  "listing:2097508172": {
    "propertyId": "1111111111111111111",
    "unitId": "2222222222222222222",
    "propertyName": "9401 Nieman Rd",
    "unitName": "Unit 3"
  },
  "address:9401 nieman road|unit 3|overland park|ks|66214": {
    "propertyId": "1111111111111111111",
    "unitId": "2222222222222222222",
    "propertyName": "9401 Nieman Rd",
    "unitName": "Unit 3"
  }
}
```

Keys are normalized to lowercase letters/numbers/spaces. Listing IDs are safer than address matching when Zillow provides them.

Do not put approved rent or deposit in this Zillow routing map. Rent and deposit belong to GH Real Estate property/unit/lease records and Zoho Books setup, not Zillow prospect intake.

## Field Map Override Example

Use this only if your Zoho CRM API names differ.

```json
{
  "lead": {
    "zillowLeadKey": "GHRE_Zillow_Lead_Key",
    "property": "GHRE_Requested_Property",
    "unit": "GHRE_Requested_Unit"
  }
}
```
