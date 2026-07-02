# Runtime Environment Template

Configure these values in Zoho Catalyst or another approved runtime secret/config manager. Do not commit a real `.env` file.

## Inbound Route And Safety

```text
GATEWAY_VERSION=2026-07-02.v2
ALLOWED_PATHS=/zillow/leads
MAX_BODY_BYTES=65536
REQUIRE_INBOUND_SECRET=true
INBOUND_SECRET_HEADER_NAME=x-gh-zillow-webhook-key
INBOUND_SECRET_VALUE=<long random runtime secret>
ALLOW_SECRET_QUERY_PARAM=false
INBOUND_SECRET_QUERY_PARAM=key
DRY_RUN=true
LIVE_MODE_ENABLED=false
LIVE_MODE_CONFIRMATION=
EXPECTED_LIVE_MODE_CONFIRMATION=GH_ZILLOW_LEAD_INTAKE_LIVE_APPROVED
```

## Health Check

```text
ENABLE_HEALTH=true
HEALTH_HEADER_NAME=x-gh-health-token
HEALTH_CHECK_TOKEN=<runtime health token>
```

## Zoho OAuth And API Roots

```text
ZOHO_CLIENT_ID=<runtime OAuth client ID>
ZOHO_CLIENT_SECRET=<runtime OAuth client secret>
ZOHO_REFRESH_TOKEN=<runtime OAuth refresh token>
ZOHO_ACCOUNTS_BASE_URL=https://accounts.zoho.com
ZOHO_CRM_BASE_URL=https://www.zohoapis.com
ZOHO_CRM_API_VERSION=v8
```

## CRM Modules And Triggers

```text
ZOHO_CRM_LEADS_MODULE=Leads
ZOHO_CRM_INTAKE_EVENTS_MODULE=Zillow_Intake_Events
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
```

## Duplicate Prevention And Field Mapping

```text
LEAD_DUPLICATE_CHECK_FIELDS=Zillow_Lead_Key
INTAKE_EVENT_DUPLICATE_CHECK_FIELDS=External_Event_Key
PROPERTY_UNIT_MAP_JSON={}
ZOHO_CRM_FIELD_MAP_JSON={}
ENABLE_CRM_INTAKE_EVENT_LOG=false
```
