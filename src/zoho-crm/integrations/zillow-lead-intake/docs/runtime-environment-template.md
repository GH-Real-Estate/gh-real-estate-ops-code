# Runtime Environment Template

Configure these values in Zoho Catalyst or another approved runtime configuration manager. Do not commit a real `.env` file.

## Environment Safety Rule

Keep Catalyst **Development** safe by default and use Catalyst **Production** for the live Zillow endpoint.

- Development should normally remain dry-run unless you are intentionally running an internal live smoke test against non-production data.
- Production is the only environment Zillow should use after the API is approved for production delivery.
- Do not depend on code deploys to change secrets or runtime mode. Set environment variables in the target Catalyst environment, then redeploy/restart that same target environment.

## Development Dry-Run Values

```text
ZILLOW_WEBHOOK_DRY_RUN=true
DRY_RUN=true
LIVE_MODE_ENABLED=false
LIVE_MODE_CONFIRMATION=
EXPECTED_LIVE_MODE_CONFIRMATION=GH_ZILLOW_LEAD_INTAKE_LIVE_APPROVED
DEBUG_ERRORS=true
```

## Production Live Values

Use these only after dry-run payload mapping and routing have been verified.

```text
ZILLOW_WEBHOOK_DRY_RUN=false
DRY_RUN=false
LIVE_MODE_ENABLED=true
LIVE_MODE_CONFIRMATION=GH_ZILLOW_LEAD_INTAKE_LIVE_APPROVED
EXPECTED_LIVE_MODE_CONFIRMATION=GH_ZILLOW_LEAD_INTAKE_LIVE_APPROVED
DEBUG_ERRORS=true
```

Turn `DEBUG_ERRORS` back to `false` after live smoke testing is complete.

## Inbound Route And Safety

```text
GATEWAY_VERSION=2026-07-07.v7
ALLOWED_PATHS=/zillow/leads
MAX_BODY_BYTES=65536
INBOUND_BODY_TIMEOUT_MS=8000
REQUIRE_INBOUND_SECRET=true
INBOUND_SECRET_HEADER_NAME=x-gh-zillow-webhook-key
ZILLOW_WEBHOOK_KEY=<long random runtime value>
INBOUND_SECRET_VALUE=
ALLOW_SECRET_QUERY_PARAM=false
INBOUND_SECRET_QUERY_PARAM=key
ENFORCE_IP_ALLOWLIST=false
ALLOWED_IPS=
ALLOW_JSON_PAYLOADS=false
GENERIC_PUBLIC_ERRORS=true
```

## Health Check

```text
ENABLE_HEALTH=false
HEALTH_HEADER_NAME=x-gh-health-token
HEALTH_CHECK_TOKEN=<runtime health token>
```

## Optional Replay Cache

CRM upsert with `Zillow_Lead_Key` is the primary duplicate-control method. Enable this only after Catalyst Cache is confirmed for the deployed function.

```text
ENABLE_CACHE_REPLAY_DEFENSE=false
STRICT_REPLAY_FAILURE=false
REPLAY_CACHE_SEGMENT_ID=
REPLAY_WINDOW_SECONDS=300
```

## Zoho OAuth And API Roots

Add the Zoho OAuth client ID, client credential, and CRM refresh value only in the runtime configuration manager. Do not commit real values.

```text
ZOHO_CLIENT_ID=<runtime value>
ZOHO_CLIENT_SECRET=<runtime value>
ZOHO_REFRESH_TOKEN=<runtime value>
ZOHO_ACCOUNTS_BASE_URL=https://accounts.zoho.com
ZOHO_CRM_BASE_URL=https://www.zohoapis.com
ZOHO_CRM_API_VERSION=v8
ACCOUNTS_ALLOWED_HOST_SUFFIXES=accounts.zoho.com
CRM_ALLOWED_HOST_SUFFIXES=zohoapis.com
OUTBOUND_TIMEOUT_MS=15000
```

## CRM Modules And Routing

```text
ZOHO_CRM_LEADS_MODULE=Leads
ZOHO_CRM_UNITS_MODULE=Units
ENABLE_DYNAMIC_UNIT_ROUTING=true
DYNAMIC_UNIT_ROUTING_REQUIRED=false
UNIT_PROPERTY_LOOKUP_FIELD=Property
PROPERTY_UNIT_MAP_JSON={}
ZOHO_CRM_FIELD_MAP_JSON={}
```

`PROPERTY_UNIT_MAP_JSON` is now only a fallback. The preferred long-term routing source is the CRM Units module using `Zillow_Listing_ID`, `Zillow_Provider_Model_ID`, `Zillow_Listing_Contact_Prefix`, and `Zillow_Routing_Unit_Key` on each Unit record.

If the Units module has a lookup field back to the Properties/Accounts module, put that field's API name in `UNIT_PROPERTY_LOOKUP_FIELD`. For GH Real Estate, use `UNIT_PROPERTY_LOOKUP_FIELD=Property` unless Zoho CRM Developer Hub shows a different API name.

## Optional Intake Event Log And CRM Triggers

```text
ZOHO_CRM_INTAKE_EVENTS_MODULE=Zillow_Intake_Events
ENABLE_CRM_INTAKE_EVENT_LOG=false
ENABLE_DRY_RUN_CRM_AUDIT_LOG=false
CRM_TRIGGER_WORKFLOWS=false
CRM_TRIGGER_APPROVALS=false
CRM_TRIGGER_BLUEPRINTS=false
SKIP_CADENCES_ON_INSERT=true
SKIP_CADENCES_ON_UPDATE=false
```

## Business Defaults

```text
DEFAULT_LEAD_SOURCE=Zillow
DEFAULT_LEAD_STATUS=New Zillow Inquiry
```

The intake service sets `Zillow_Intake_Status` to `Routing Matched` or `Routing Unmatched` after property/unit routing is evaluated.

## Duplicate Prevention And Field Mapping

```text
LEAD_DUPLICATE_CHECK_FIELDS=Zillow_Lead_Key
INTAKE_EVENT_DUPLICATE_CHECK_FIELDS=External_Event_Key
```

Use `ZOHO_CRM_FIELD_MAP_JSON` only when actual Zoho CRM API names differ from the verified names documented in `README.md`.
