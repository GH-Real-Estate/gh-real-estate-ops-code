# Environment Variables

Use placeholders only in Git. Configure real values in Zoho Catalyst or another approved runtime configuration manager.

Do not store a Zoho `access_token` as an environment variable. Access tokens are short-lived. Store the refresh token only; the function exchanges it for fresh access tokens at runtime.

## Catalyst Environment Rule

Configure variables in the same Catalyst environment that is serving the endpoint you are testing.

- Development should stay dry-run by default.
- Production should be live only after dry-run and routing tests pass.
- Runtime variables in Catalyst are the source of truth for secrets and mode switches.
- After editing variables, redeploy or otherwise force the function runtime to reload before testing again.

## Complete Development Variable Block

Use this for Catalyst **Development**.

```text
GATEWAY_VERSION=dev-2026-07-08
ALLOWED_PATHS=/zillow/leads
MAX_BODY_BYTES=65536
INBOUND_BODY_TIMEOUT_MS=8000
REQUIRE_INBOUND_SECRET=true
INBOUND_SECRET_HEADER_NAME=x-gh-zillow-webhook-key
ZILLOW_WEBHOOK_KEY=<set in Catalyst, do not commit>
INBOUND_SECRET_VALUE=
ALLOW_SECRET_QUERY_PARAM=false
INBOUND_SECRET_QUERY_PARAM=key
ENFORCE_IP_ALLOWLIST=false
ALLOWED_IPS=
ZILLOW_WEBHOOK_DRY_RUN=true
DRY_RUN=true
LIVE_MODE_ENABLED=false
LIVE_MODE_CONFIRMATION=
EXPECTED_LIVE_MODE_CONFIRMATION=GH_ZILLOW_LEAD_INTAKE_LIVE_APPROVED
ALLOW_JSON_PAYLOADS=false
GENERIC_PUBLIC_ERRORS=true
ENABLE_HEALTH=true
HEALTH_HEADER_NAME=x-gh-health-token
HEALTH_CHECK_TOKEN=<set in Catalyst, do not commit>
ENABLE_CACHE_REPLAY_DEFENSE=false
STRICT_REPLAY_FAILURE=false
REPLAY_CACHE_SEGMENT_ID=
REPLAY_WINDOW_SECONDS=300
ZOHO_CLIENT_ID=<set in Catalyst, do not commit>
ZOHO_CLIENT_SECRET=<set in Catalyst, do not commit>
ZOHO_REFRESH_TOKEN=<set in Catalyst, do not commit>
ZOHO_ACCOUNTS_BASE_URL=https://accounts.zoho.com
ZOHO_CRM_BASE_URL=https://www.zohoapis.com
ZOHO_CRM_API_VERSION=v8
ACCOUNTS_ALLOWED_HOST_SUFFIXES=accounts.zoho.com
CRM_ALLOWED_HOST_SUFFIXES=zohoapis.com
OUTBOUND_TIMEOUT_MS=15000
ZOHO_CRM_LEADS_MODULE=Leads
ZOHO_CRM_UNITS_MODULE=Units
ENABLE_DYNAMIC_UNIT_ROUTING=true
DYNAMIC_UNIT_ROUTING_REQUIRED=false
UNIT_PROPERTY_LOOKUP_FIELD=Property
PROPERTY_UNIT_MAP_JSON={}
ZOHO_CRM_FIELD_MAP_JSON={}
ZOHO_CRM_INTAKE_EVENTS_MODULE=Zillow_Intake_Events
ENABLE_CRM_INTAKE_EVENT_LOG=false
ENABLE_DRY_RUN_CRM_AUDIT_LOG=false
INTAKE_EVENT_DUPLICATE_CHECK_FIELDS=External_Event_Key
CRM_TRIGGER_WORKFLOWS=false
CRM_TRIGGER_APPROVALS=false
CRM_TRIGGER_BLUEPRINTS=false
SKIP_CADENCES_ON_INSERT=false
SKIP_CADENCES_ON_UPDATE=false
DEFAULT_LEAD_SOURCE=Zillow
DEFAULT_LEAD_STATUS=New Zillow Inquiry
LEAD_DUPLICATE_CHECK_FIELDS=Zillow_Lead_Key
DEBUG_ERRORS=true
```

## Complete Production Variable Block

Use this for Catalyst **Production**.

```text
GATEWAY_VERSION=prod-token-refresh-2026-07-08-01
ALLOWED_PATHS=/zillow/leads
MAX_BODY_BYTES=65536
INBOUND_BODY_TIMEOUT_MS=8000
REQUIRE_INBOUND_SECRET=true
INBOUND_SECRET_HEADER_NAME=x-gh-zillow-webhook-key
ZILLOW_WEBHOOK_KEY=<set in Catalyst, do not commit>
INBOUND_SECRET_VALUE=
ALLOW_SECRET_QUERY_PARAM=false
INBOUND_SECRET_QUERY_PARAM=key
ENFORCE_IP_ALLOWLIST=false
ALLOWED_IPS=
ZILLOW_WEBHOOK_DRY_RUN=false
DRY_RUN=false
LIVE_MODE_ENABLED=true
LIVE_MODE_CONFIRMATION=GH_ZILLOW_LEAD_INTAKE_LIVE_APPROVED
EXPECTED_LIVE_MODE_CONFIRMATION=GH_ZILLOW_LEAD_INTAKE_LIVE_APPROVED
ALLOW_JSON_PAYLOADS=false
GENERIC_PUBLIC_ERRORS=false
ENABLE_HEALTH=true
HEALTH_HEADER_NAME=x-gh-health-token
HEALTH_CHECK_TOKEN=<set in Catalyst, do not commit>
ENABLE_CACHE_REPLAY_DEFENSE=false
STRICT_REPLAY_FAILURE=false
REPLAY_CACHE_SEGMENT_ID=
REPLAY_WINDOW_SECONDS=300
ZOHO_CLIENT_ID=<set in Catalyst, do not commit>
ZOHO_CLIENT_SECRET=<set in Catalyst, do not commit>
ZOHO_REFRESH_TOKEN=<set in Catalyst, do not commit>
ZOHO_ACCOUNTS_BASE_URL=https://accounts.zoho.com
ZOHO_CRM_BASE_URL=https://www.zohoapis.com
ZOHO_CRM_API_VERSION=v8
ACCOUNTS_ALLOWED_HOST_SUFFIXES=accounts.zoho.com
CRM_ALLOWED_HOST_SUFFIXES=zohoapis.com
OUTBOUND_TIMEOUT_MS=15000
ZOHO_CRM_LEADS_MODULE=Leads
ZOHO_CRM_UNITS_MODULE=Units
ENABLE_DYNAMIC_UNIT_ROUTING=true
DYNAMIC_UNIT_ROUTING_REQUIRED=false
UNIT_PROPERTY_LOOKUP_FIELD=Property
PROPERTY_UNIT_MAP_JSON={}
ZOHO_CRM_FIELD_MAP_JSON={}
ZOHO_CRM_INTAKE_EVENTS_MODULE=Zillow_Intake_Events
ENABLE_CRM_INTAKE_EVENT_LOG=false
ENABLE_DRY_RUN_CRM_AUDIT_LOG=false
INTAKE_EVENT_DUPLICATE_CHECK_FIELDS=External_Event_Key
CRM_TRIGGER_WORKFLOWS=false
CRM_TRIGGER_APPROVALS=false
CRM_TRIGGER_BLUEPRINTS=false
SKIP_CADENCES_ON_INSERT=false
SKIP_CADENCES_ON_UPDATE=false
DEFAULT_LEAD_SOURCE=Zillow
DEFAULT_LEAD_STATUS=New Zillow Inquiry
LEAD_DUPLICATE_CHECK_FIELDS=Zillow_Lead_Key
DEBUG_ERRORS=true
```

`ENABLE_HEALTH`, `HEALTH_HEADER_NAME`, `HEALTH_CHECK_TOKEN`, `GENERIC_PUBLIC_ERRORS=false`, and `DEBUG_ERRORS=true` are temporary diagnostics. After the live smoke test passes, either set `ENABLE_HEALTH=false` or rotate the health token, and return `GENERIC_PUBLIC_ERRORS=true`.

## Important Cadence Skip Note

Keep both cadence skip variables off for this Zillow intake function:

```text
SKIP_CADENCES_ON_INSERT=false
SKIP_CADENCES_ON_UPDATE=false
```

Manual Zoho CRM upsert diagnostics pass without the `skip_feature_execution` payload. A live webhook failure after token, Units search, full upsert, and lookup upsert all pass is strongly consistent with Zoho rejecting `skip_feature_execution`. The root entrypoint also forces both variables to `false` before loading the implementation as a hard safety guard.

## Live/Dry-Run Mode Matrix

| Catalyst environment | `ZILLOW_WEBHOOK_DRY_RUN` | `DRY_RUN` | `LIVE_MODE_ENABLED` | `LIVE_MODE_CONFIRMATION` | Use |
|---|---:|---:|---:|---|---|
| Development | `true` | `true` | `false` | blank | Safe testing with no CRM Lead writes. |
| Production | `false` | `false` | `true` | `GH_ZILLOW_LEAD_INTAKE_LIVE_APPROVED` | Live CRM Lead upsert after approval. |

## Variable Reference

| Variable | Required | Default | Purpose |
|---|---:|---|---|
| `GATEWAY_VERSION` | Yes | `2026-07-07.v7` | Runtime version label surfaced in health checks. |
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
| `ENABLE_HEALTH` | Diagnostic | `false` | Enables protected `/health`. |
| `HEALTH_HEADER_NAME` | Diagnostic | `x-gh-health-token` | Header checked on health route. |
| `HEALTH_CHECK_TOKEN` | Diagnostic if health enabled | blank | Required token for health route. |
| `ENABLE_CACHE_REPLAY_DEFENSE` | No | `false` | Optional Catalyst Cache duplicate/replay guard. CRM upsert remains the main duplicate control. |
| `STRICT_REPLAY_FAILURE` | No | `false` | If true, cache failure rejects webhook with 503. |
| `REPLAY_CACHE_SEGMENT_ID` | No | blank | Optional Catalyst Cache segment ID. |
| `REPLAY_WINDOW_SECONDS` | No | `300` | Recent duplicate cache window. |
| `ZOHO_CLIENT_ID` | Yes for live and dynamic routing | blank | Zoho OAuth client ID. |
| `ZOHO_CLIENT_SECRET` | Yes for live and dynamic routing | blank | Zoho OAuth client credential. |
| `ZOHO_REFRESH_TOKEN` | Yes for live and dynamic routing | blank | Zoho OAuth refresh token for CRM Leads and Units lookup. |
| `ZOHO_ACCOUNTS_BASE_URL` | Yes | `https://accounts.zoho.com` | Zoho Accounts base URL. |
| `ZOHO_CRM_BASE_URL` | Yes | `https://www.zohoapis.com` | Zoho CRM API base URL. |
| `ZOHO_CRM_API_VERSION` | Yes | `v8` | CRM API version. |
| `ACCOUNTS_ALLOWED_HOST_SUFFIXES` | Yes | `accounts.zoho.com` | Outbound host allowlist for Zoho Accounts. |
| `CRM_ALLOWED_HOST_SUFFIXES` | Yes | `zohoapis.com` | Outbound host allowlist for Zoho CRM. |
| `OUTBOUND_TIMEOUT_MS` | Yes | `15000` | Zoho API request timeout. |
| `ZOHO_CRM_LEADS_MODULE` | Yes | `Leads` | CRM Leads module API name. |
| `ZOHO_CRM_UNITS_MODULE` | Yes | `Units` | CRM Units module API name. GH Real Estate verified `Units`. |
| `ENABLE_DYNAMIC_UNIT_ROUTING` | Yes | `true` | Searches CRM Units using the Zillow routing fields on each Unit record. |
| `DYNAMIC_UNIT_ROUTING_REQUIRED` | No | `false` | If true, a CRM Unit search failure rejects the callback instead of accepting the lead as unmatched. |
| `UNIT_PROPERTY_LOOKUP_FIELD` | No | `Property` | API name of the lookup from Units back to Properties/Accounts. |
| `LEAD_DUPLICATE_CHECK_FIELDS` | Yes | `Zillow_Lead_Key` | Unique lead key. Create and mark this field unique. |
| `PROPERTY_UNIT_MAP_JSON` | No | `{}` | Legacy/fallback static routing map. Leave `{}` when using Unit-based routing. |
| `ZOHO_CRM_FIELD_MAP_JSON` | No | `{}` | Overrides default API field names. Leave `{}` if verified CRM API names match the README. |
| `ENABLE_CRM_INTAKE_EVENT_LOG` | No | `false` | Writes optional audit events to a custom CRM module. |
| `ENABLE_DRY_RUN_CRM_AUDIT_LOG` | No | `false` | Allows dry-run audit-event writes without creating Leads. |
| `ZOHO_CRM_INTAKE_EVENTS_MODULE` | No | `Zillow_Intake_Events` | Optional audit module API name. |
| `INTAKE_EVENT_DUPLICATE_CHECK_FIELDS` | No | `External_Event_Key` | Optional audit module duplicate key. |
| `CRM_TRIGGER_WORKFLOWS` | No | `false` | Enables Zoho CRM workflow triggers on upsert. |
| `CRM_TRIGGER_APPROVALS` | No | `false` | Enables Zoho CRM approval triggers on upsert. |
| `CRM_TRIGGER_BLUEPRINTS` | No | `false` | Enables Zoho CRM blueprint triggers on upsert. |
| `SKIP_CADENCES_ON_INSERT` | No | `false` | Keep off. Avoids sending `skip_feature_execution` until verified for this org/API version. |
| `SKIP_CADENCES_ON_UPDATE` | No | `false` | Keep off. Avoids sending `skip_feature_execution` until verified for this org/API version. |
| `DEFAULT_LEAD_SOURCE` | Yes | `Zillow` | Default Lead Source. |
| `DEFAULT_LEAD_STATUS` | Yes | `New Zillow Inquiry` | Default Lead Status. |
| `DEBUG_ERRORS` | No | `false` | Adds sanitized error detail to server logs only. |

## Preferred Unit-Based Routing

The long-term routing source is the CRM Units module. Populate these Unit fields as Zillow data becomes available:

| Unit field | API name | Use |
|---|---|---|
| Zillow Listing ID | `Zillow_Listing_ID` | Strongest key when Zillow provides the real listing ID. |
| Zillow Provider Model ID | `Zillow_Provider_Model_ID` | Useful for multifamily model/floorplan routing when meaningful. |
| Zillow Listing Contact Prefix | `Zillow_Listing_Contact_Prefix` | Prefix before `@` in the listing contact email. Useful if Zillow triggers by email domain. |
| Zillow Routing Unit Key | `Zillow_Routing_Unit_Key` | Fallback key built from `listingStreet|listingUnit|listingCity|listingState|listingPostalCode`. |

Example `Zillow_Routing_Unit_Key`:

```text
1000 example avenue|unit 3|sample city|ks|00000
```

## Legacy Static Map Fallback

Use this only for temporary testing or one-off exceptions:

```json
{
  "listing:synthetic id 005": {
    "propertyId": "SYNTHETIC-ID-001",
    "unitId": "SYNTHETIC-ID-006",
    "propertyName": "1000 Example Avenue",
    "unitName": "Unit 3"
  }
}
```

Replace `propertyId` and `unitId` with private Zoho record IDs in runtime configuration. Never commit those production IDs.

Do not put approved rent or deposit in routing configuration. Rent and deposit belong to GH Real Estate property/unit/lease records and Zoho Books setup, not Zillow prospect intake.

## Field Map Override Example

Use this only if your Zoho CRM API names differ.

```json
{
  "unit": {
    "zillowRoutingUnitKey": "Custom_Zillow_Routing_Key"
  },
  "lead": {
    "zillowLeadKey": "GHRE_Zillow_Lead_Key"
  }
}
```
