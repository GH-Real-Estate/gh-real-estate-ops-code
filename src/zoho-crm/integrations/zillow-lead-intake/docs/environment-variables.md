# Environment Variables

Use placeholders only in Git. Configure real values in Zoho Catalyst or another approved runtime secret/config manager.

## Required / Primary Runtime Settings

| Variable | Required | Default | Purpose |
|---|---:|---|---|
| `ALLOWED_PATHS` | Yes | `/zillow/leads` | Comma-separated POST paths accepted by the service. |
| `MAX_BODY_BYTES` | Yes | `65536` | Rejects oversized webhook bodies. |
| `INBOUND_BODY_TIMEOUT_MS` | Yes | `8000` | Rejects slow/incomplete inbound requests. |
| `SUCCESS_STATUS_CODE` | Yes | `202` | Success response returned after authenticated parse/plan or live upsert. |
| `REQUIRE_INBOUND_SECRET` | Yes | `true` | Requires a shared secret before processing. |
| `ZILLOW_WEBHOOK_HEADER_NAME` | Yes | `x-gh-zillow-webhook-key` | Header checked for the inbound secret. |
| `ZILLOW_WEBHOOK_KEY` | Yes | blank | Long random Zillow webhook secret. |
| `ALLOW_SECRET_QUERY_PARAM` | No | `false` | Allows secret in query string only if header delivery becomes impossible. |
| `INBOUND_SECRET_QUERY_PARAM` | No | `key` | Query parameter name for fallback shared secret. |
| `REQUIRE_URLENCODED` | Yes | `true` | Requires Zillow's official URL-encoded payload format. |
| `ALLOW_JSON_TEST_PAYLOADS` | No | `false` | Allows JSON only for internal development tests. Keep false for Zillow. |
| `ZILLOW_WEBHOOK_DRY_RUN` | Yes | `true` | Validates and plans without writing to Zoho. |
| `ZILLOW_WEBHOOK_LIVE_MODE_ENABLED` | Yes | `false` | First live-mode circuit breaker. |
| `ZILLOW_WEBHOOK_LIVE_CONFIRMATION` | Yes for live | blank | Must match expected value before CRM writes. |
| `EXPECTED_LIVE_MODE_CONFIRMATION` | Yes | `GH_ZILLOW_LEAD_INTAKE_LIVE_APPROVED` | Second live-mode circuit breaker value. |
| `REQUIRE_ROUTE_MATCH_FOR_SUCCESS` | No | `false` | When true, rejects leads if no property/unit mapping is found. Keep false during first Zillow test unless you want redelivery on unmapped leads. |

Backward-compatible names `INBOUND_SECRET_HEADER_NAME`, `INBOUND_SECRET_VALUE`, `DRY_RUN`, `LIVE_MODE_ENABLED`, and `LIVE_MODE_CONFIRMATION` are still read as fallbacks, but the `ZILLOW_WEBHOOK_*` names should be used for new deployments.

## Optional Source Restrictions

| Variable | Required | Default | Purpose |
|---|---:|---|---|
| `ENFORCE_IP_ALLOWLIST` | No | `false` | Rejects requests unless source IP is in `ALLOWED_IPS`. Enable only after confirming the IP visible to Catalyst. |
| `ALLOWED_IPS` | No | blank | Comma-separated IP allowlist. |

## Health Check

| Variable | Required | Default | Purpose |
|---|---:|---|---|
| `ENABLE_HEALTH` | No | `true` | Enables protected `GET /health`. |
| `HEALTH_HEADER_NAME` | No | `x-gh-health-token` | Header used for health token. |
| `HEALTH_CHECK_TOKEN` | Recommended | blank | If set, hides health behind the token. |

## Zoho OAuth And API Roots

| Variable | Required | Default | Purpose |
|---|---:|---|---|
| `ZOHO_CLIENT_ID` | Yes for live | blank | Zoho OAuth client ID. |
| `ZOHO_CLIENT_SECRET` | Yes for live | blank | Zoho OAuth client secret. |
| `ZOHO_REFRESH_TOKEN` | Yes for live | blank | Zoho OAuth refresh token. |
| `ZOHO_ACCOUNTS_BASE_URL` | Yes | `https://accounts.zoho.com` | Zoho Accounts base URL. |
| `ZOHO_CRM_BASE_URL` | Yes | `https://www.zohoapis.com` | Zoho CRM API base URL. |
| `ZOHO_CRM_API_VERSION` | Yes | `v8` | CRM API version. |
| `ZOHO_ACCOUNTS_ALLOWED_HOST_SUFFIXES` | Yes | `accounts.zoho.com` | Outbound host allowlist for OAuth. |
| `ZOHO_CRM_ALLOWED_HOST_SUFFIXES` | Yes | `zohoapis.com` | Outbound host allowlist for CRM. |
| `OUTBOUND_TIMEOUT_MS` | Yes | `15000` | Timeout for outbound Zoho requests. |

## CRM Modules And Triggers

| Variable | Required | Default | Purpose |
|---|---:|---|---|
| `ZOHO_CRM_LEADS_MODULE` | Yes | `Leads` | CRM Leads module API name. |
| `ZOHO_CRM_INTAKE_EVENTS_MODULE` | No | `Zillow_Intake_Events` | Optional custom audit module. |
| `ENABLE_CRM_INTAKE_EVENT_LOG` | No | `false` | Writes optional audit events to a custom CRM module. |
| `LEAD_DUPLICATE_CHECK_FIELDS` | Yes | `Zillow_Lead_Key` | Unique lead key. Create and mark this field unique. |
| `INTAKE_EVENT_DUPLICATE_CHECK_FIELDS` | No | `External_Event_Key` | Optional audit-event duplicate key. |
| `CRM_TRIGGER_WORKFLOWS` | No | `false` | Enables CRM workflow triggers on upsert. |
| `CRM_TRIGGER_APPROVALS` | No | `false` | Enables CRM approval triggers on upsert. |
| `CRM_TRIGGER_BLUEPRINTS` | No | `false` | Enables CRM blueprint triggers on upsert. |
| `SKIP_CADENCES_ON_INSERT` | No | `true` | Skips CRM cadences on insert by default. |
| `SKIP_CADENCES_ON_UPDATE` | No | `false` | Skips CRM cadences on update if set. |

## Business Defaults

| Variable | Required | Default | Purpose |
|---|---:|---|---|
| `DEFAULT_LEAD_SOURCE` | Yes | `Zillow` | CRM Lead Source value. |
| `DEFAULT_LEAD_STATUS` | Yes | `New Zillow Inquiry` | CRM Lead Status value. |
| `DEFAULT_ZILLOW_INTAKE_STATUS` | Yes | `Received` | Zillow Intake Status value. |
| `ZILLOW_LISTING_URL_TEMPLATE` | No | blank | Optional URL template using `{listingId}` when Zillow does not send a listing URL. |

## Property/Unit Map Example

```json
{
  "listing:2097508172": {
    "propertyId": "1111111111111111111",
    "unitId": "2222222222222222222",
    "propertyName": "9401 Nieman Road",
    "unitName": "Unit 3"
  }
}
```

Keys are normalized to lowercase letters/numbers/spaces. Listing IDs are safer than address matching when Zillow provides them.

Supported keys:

```text
listing:<zillow listingId>
model:<providerModelId>
contact-email:<listingContactEmail>
address:<composed address>|<unit>
default
```

## Field Map Override Example

Use this only if your Zoho CRM API names differ.

```json
{
  "lead": {
    "zillowLeadKey": "GHRE_Zillow_Lead_Key",
    "requestedProperty": "GHRE_Requested_Property",
    "requestedUnit": "GHRE_Requested_Unit"
  }
}
```
