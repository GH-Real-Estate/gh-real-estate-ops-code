# Environment Variables

## Purpose

All secrets and deployment-specific settings for this function must be stored in Zoho Catalyst Environment Variables.

Do not hardcode secrets in `index.js`, `package.json`, documentation files, or local `.env` files that could be uploaded or shared.

## Production Core Mode

Use these values in Catalyst Production when the automation is fully live:

```text
REGISTRATION_ONLY=false
DRY_RUN=false
SEND_INVOICE_ON_CREATE=true
REQUIRE_LIVE_MODE_CONFIRMATION=true
LIVE_MODE_CONFIRMATION=GH_RETURNED_FEE_LIVE_APPROVED
EXPECTED_LIVE_MODE_CONFIRMATION=GH_RETURNED_FEE_LIVE_APPROVED
```

Meaning:

| Variable | Purpose |
|---|---|
| `REGISTRATION_ONLY=false` | Allows the function to process events instead of only acknowledging registration tests. |
| `DRY_RUN=false` | Allows real returned-fee invoice creation. |
| `SEND_INVOICE_ON_CREATE=true` | Sends newly created returned-fee invoices automatically. |
| `REQUIRE_LIVE_MODE_CONFIRMATION=true` | Requires an explicit live-mode confirmation before invoice creation. |
| `LIVE_MODE_CONFIRMATION` | Circuit-breaker value proving live mode was intentionally enabled. |
| `EXPECTED_LIVE_MODE_CONFIRMATION` | Expected confirmation phrase. |

## Inbound Security

```text
REQUIRE_SIGNATURE=true
REQUIRE_JSON=true
ENABLE_REPLAY_DEFENSE=true
STRICT_REPLAY_FAILURE=true
GENERIC_PUBLIC_ERRORS=true
ALLOWED_PATHS=/zpayments/payment-failed
MAX_BODY_BYTES=262144
INBOUND_BODY_TIMEOUT_MS=8000
SIGNATURE_TOLERANCE_SECONDS=900
REPLAY_KEY_PREFIX=zpr:
REPLAY_WINDOW_SECONDS=86400
PAYMENT_LOCK_SECONDS=300
```

Meaning:

| Variable | Purpose |
|---|---|
| `REQUIRE_SIGNATURE` | Requires Zoho Payments HMAC webhook signature verification. |
| `REQUIRE_JSON` | Rejects non-JSON webhook requests. |
| `ENABLE_REPLAY_DEFENSE` | Prevents repeated processing of the same event/payment attempt. |
| `STRICT_REPLAY_FAILURE` | Fails closed if replay defense cannot be evaluated. |
| `GENERIC_PUBLIC_ERRORS` | Avoids exposing sensitive internals in public webhook responses. |
| `ALLOWED_PATHS` | Restricts processing to the real webhook route. |
| `MAX_BODY_BYTES` | Prevents oversized request bodies. |
| `INBOUND_BODY_TIMEOUT_MS` | Prevents slow body reads from hanging the function. |
| `SIGNATURE_TOLERANCE_SECONDS` | Limits accepted age of signed webhook events. |
| `REPLAY_KEY_PREFIX` | Prefix for replay-defense cache keys. |
| `REPLAY_WINDOW_SECONDS` | Time window for event replay protection. |
| `PAYMENT_LOCK_SECONDS` | Short lock to prevent concurrent processing of the same payment. |

## Test And Debug Routes

In Production, these should remain disabled:

```text
ENABLE_OAUTH_DIAGNOSTIC=false
ENABLE_MOCK_PROCESSING=false
ENABLE_ADMIN_PROCESS_PAYMENT=false
DEBUG_PAYLOAD_LOGGING=false
DEBUG_SAFE_ZOHO_BODIES=false
ENABLE_HEALTH=false
```

Meaning:

| Variable | Purpose |
|---|---|
| `ENABLE_OAUTH_DIAGNOSTIC` | Enables OAuth diagnostic route. Should be off in Production. |
| `ENABLE_MOCK_PROCESSING` | Enables mock processing route. Should be off in Production. |
| `ENABLE_ADMIN_PROCESS_PAYMENT` | Enables admin/manual route if present. Should be off unless intentionally needed. |
| `DEBUG_PAYLOAD_LOGGING` | Logs payload details. Should be off in Production. |
| `DEBUG_SAFE_ZOHO_BODIES` | Logs sanitized Zoho API response details. Should be off in Production. |
| `ENABLE_HEALTH` | Enables health route. Optional, but off is safer unless monitoring requires it. |

## Zoho OAuth2 Variables

These must exist in Catalyst Production:

```text
ZOHO_CLIENT_ID
ZOHO_CLIENT_SECRET
ZOHO_REFRESH_TOKEN
```

These are used by Catalyst to obtain Zoho OAuth2 access tokens for outbound API calls.

Required outbound APIs:

```text
Catalyst → Zoho Payments API
Catalyst → Zoho Books API
```

OAuth2 is not used for inbound webhook authentication. Inbound webhook authentication uses HMAC.

## Zoho API URLs

```text
ZOHO_ACCOUNTS_BASE_URL=https://accounts.zoho.com
ZOHO_BOOKS_BASE_URL=https://www.zohoapis.com/books/v3
ZOHO_PAYMENTS_BASE_URL=https://payments.zoho.com
ACCOUNTS_ALLOWED_HOST_SUFFIXES=accounts.zoho.com
BOOKS_ALLOWED_HOST_SUFFIXES=zohoapis.com
PAYMENTS_ALLOWED_HOST_SUFFIXES=payments.zoho.com
```

The host allowlists prevent misconfigured environment variables from redirecting API calls to unapproved domains.

## Business Configuration

```text
ZOHO_BOOKS_ORG_ID=<Zoho Books organization ID>
ZOHO_PAYMENTS_ACCOUNT_ID=<Zoho Payments account ID>
RETURNED_FEE_ITEM_ID=<Zoho Books item ID for returned-payment fee>
RETURNED_FEE_AMOUNT=30
RETURNED_FEE_INVOICE_PREFIX=RF
RETURNED_FEE_LEDGER_FIELD_API_NAME=cf_returned_payment_fee_events
OPTIONAL_LATEST_RF_INVOICE_FIELD_API_NAME=cf_returned_fee_invoice_number
UPDATE_OPTIONAL_LATEST_RF_INVOICE_FIELD=false
MAX_LEDGER_LENGTH=32000
BOOKS_PAYMENT_OPTIONS_ENABLED=true
BOOKS_PAYMENT_GATEWAYS_CSV=
```

Do not wrap values in quotes when entering them into Catalyst.

## Webhook Signing Key

```text
ZPAYMENTS_WEBHOOK_SIGNING_KEY=<raw Zoho Payments webhook signing key>
```

Rules:

```text
No quotes
No angle brackets
No leading spaces
No trailing spaces
No line breaks
```

## Dry Run Safety Mode

To test safely in Production without creating invoices:

```text
DRY_RUN=true
SEND_INVOICE_ON_CREATE=true
```

The function should verify the event and return what it would do, but it should not create or send an invoice.

## Full Live Mode

To fully enable production automation:

```text
REGISTRATION_ONLY=false
DRY_RUN=false
SEND_INVOICE_ON_CREATE=true
REQUIRE_LIVE_MODE_CONFIRMATION=true
LIVE_MODE_CONFIRMATION=GH_RETURNED_FEE_LIVE_APPROVED
EXPECTED_LIVE_MODE_CONFIRMATION=GH_RETURNED_FEE_LIVE_APPROVED
```
