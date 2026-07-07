# Runtime Environment Template

Configure these values in Zoho Catalyst or another approved runtime secret/config manager. Do not commit a real `.env` file.

## Inbound Route And Safety

```text
GATEWAY_VERSION=2026-07-07.v4
ALLOWED_PATHS=/zillow/leads
MAX_BODY_BYTES=65536
INBOUND_BODY_TIMEOUT_MS=8000
REQUIRE_INBOUND_SECRET=true
INBOUND_SECRET_HEADER_NAME=x-gh-zillow-webhook-key
ZILLOW_WEBHOOK_KEY=<long random runtime secret>
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

```text
ZOHO_CLIENT_ID=<runtime OAuth client ID>
ZOHO_CLIENT_SECRET=<runtime OAuth client secret>
ZOHO_REFRESH_TOKEN=<runtime OAuth refresh token>
ZOHO_ACCOUNTS_BASE_URL=https://accounts.zoho.com
ZOHO_CRM_BASE_URL=https://www.zohoapis.com
ZOHO_CRM_API_VERSION=v8
ACCOUNTS_ALLOWED_HOST_SUFFIXES=accounts.zoho.com
CRM_ALLOWED_HOST_SUFFIXES=zohoapis.com
OUTBOUND_TIMEOUT_MS=15000
```

## CRM Modules And Triggers

```text
ZOHO_CRM_LEADS_MODULE=Leads
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
DEFAULT_LEAD_STATUS=Not Contacted
DEFAULT_ZILLOW_INTAKE_STATUS=Received
```

After the CRM Lead Status picklist includes `New Zillow Inquiry`, you can change:

```text
DEFAULT_LEAD_STATUS=New Zillow Inquiry
```

## Duplicate Prevention And Field Mapping

```text
LEAD_DUPLICATE_CHECK_FIELDS=Zillow_Lead_Key
INTAKE_EVENT_DUPLICATE_CHECK_FIELDS=External_Event_Key
PROPERTY_UNIT_MAP_JSON={}
ZOHO_CRM_FIELD_MAP_JSON={}
```

Use `ZOHO_CRM_FIELD_MAP_JSON` only when actual Zoho CRM API names differ from the defaults documented in `README.md`.
