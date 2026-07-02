# Environment Variables

Use placeholders only in Git. Configure real values in Zoho Catalyst.

| Variable | Required | Default | Purpose |
|---|---:|---|---|
| `ALLOWED_PATHS` | Yes | `/zillow/leads` | Comma-separated POST paths accepted by the service. |
| `MAX_BODY_BYTES` | Yes | `65536` | Rejects oversized webhook bodies. |
| `REQUIRE_INBOUND_SECRET` | Yes | `true` | Requires a shared secret before processing. |
| `INBOUND_SECRET_HEADER_NAME` | Yes | `x-gh-zillow-webhook-key` | Header checked for the inbound secret. |
| `INBOUND_SECRET_VALUE` | Yes | blank | Long random secret. Required when `REQUIRE_INBOUND_SECRET=true`. |
| `ALLOW_SECRET_QUERY_PARAM` | No | `false` | Allows secret in query string only if Zillow cannot send headers. |
| `INBOUND_SECRET_QUERY_PARAM` | No | `key` | Query parameter name for fallback shared secret. |
| `DRY_RUN` | Yes | `true` | Validates and plans without writing to Zoho. |
| `LIVE_MODE_ENABLED` | Yes | `false` | First live-mode circuit breaker. |
| `LIVE_MODE_CONFIRMATION` | Yes for live | blank | Must match expected value before CRM writes. |
| `EXPECTED_LIVE_MODE_CONFIRMATION` | Yes | `GH_ZILLOW_LEAD_INTAKE_LIVE_APPROVED` | Second live-mode circuit breaker value. |
| `ZOHO_CLIENT_ID` | Yes for live | blank | Zoho OAuth client ID. |
| `ZOHO_CLIENT_SECRET` | Yes for live | blank | Zoho OAuth client secret. |
| `ZOHO_REFRESH_TOKEN` | Yes for live | blank | Zoho OAuth refresh token. |
| `ZOHO_ACCOUNTS_BASE_URL` | Yes | `https://accounts.zoho.com` | Zoho Accounts base URL. |
| `ZOHO_CRM_BASE_URL` | Yes | `https://www.zohoapis.com` | Zoho CRM API base URL. |
| `ZOHO_CRM_API_VERSION` | Yes | `v8` | CRM API version. |
| `ZOHO_CRM_LEADS_MODULE` | Yes | `Leads` | CRM Leads module API name. |
| `LEAD_DUPLICATE_CHECK_FIELDS` | Yes | `Zillow_Lead_Key` | Unique lead key. Create and mark this field unique. |
| `PROPERTY_UNIT_MAP_JSON` | No | `{}` | Maps Zillow listing/address to CRM Property and Unit record IDs. |
| `ZOHO_CRM_FIELD_MAP_JSON` | No | `{}` | Overrides default API field names. |
| `ENABLE_CRM_INTAKE_EVENT_LOG` | No | `false` | Writes optional audit events to a custom CRM module. |

## Property/Unit Map Example

```json
{
  "listing:zpid test 9401 1": {
    "propertyId": "1111111111111111111",
    "unitId": "2222222222222222222",
    "propertyName": "9401 Nieman Rd",
    "unitName": "Unit 1",
    "approvedRent": 1125,
    "approvedDeposit": 1125
  }
}
```

Keys are normalized to lowercase letters/numbers/spaces. Listing IDs are safer than address matching when Zillow provides them.

## Field Map Override Example

Use this only if your Zoho CRM API names differ.

```json
{
  "lead": {
    "zillowLeadKey": "GHRE_Zillow_Lead_Key",
    "property": "GHRE_Property",
    "unit": "GHRE_Unit"
  }
}
```
