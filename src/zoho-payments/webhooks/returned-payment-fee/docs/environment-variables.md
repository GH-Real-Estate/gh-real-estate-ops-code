# Environment Variables

All secrets and deployment-specific settings for this function must be stored in the Zoho Catalyst runtime environment or another approved runtime secret/config manager.

Do not hardcode secrets in `src/index.js`, `package.json`, documentation files, `.env`, or local notes.

## Safe Production Core Mode

Use these values only after the returned-payment fee rule and item IDs are verified:

```text
REGISTRATION_ONLY=false
DRY_RUN=false
SEND_INVOICE_ON_CREATE=true
REQUIRE_LIVE_MODE_CONFIRMATION=true
LIVE_MODE_CONFIRMATION=GH_RETURNED_FEE_LIVE_APPROVED
EXPECTED_LIVE_MODE_CONFIRMATION=GH_RETURNED_FEE_LIVE_APPROVED
```

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

## Test And Debug Routes

Production default:

```text
ENABLE_OAUTH_DIAGNOSTIC=false
ENABLE_MOCK_PROCESSING=false
ENABLE_ADMIN_PROCESS_PAYMENT=false
DEBUG_PAYLOAD_LOGGING=false
DEBUG_SAFE_ZOHO_BODIES=false
ENABLE_HEALTH=false
```

## Zoho OAuth Variables

These must exist in the runtime environment:

```text
ZOHO_CLIENT_ID
ZOHO_CLIENT_SECRET
ZOHO_REFRESH_TOKEN
```

These values are secrets. Do not commit their real values.

## Zoho API URLs

```text
ZOHO_ACCOUNTS_BASE_URL=https://accounts.zoho.com
ZOHO_BOOKS_BASE_URL=https://www.zohoapis.com/books/v3
ZOHO_PAYMENTS_BASE_URL=https://payments.zoho.com
ACCOUNTS_ALLOWED_HOST_SUFFIXES=accounts.zoho.com
BOOKS_ALLOWED_HOST_SUFFIXES=zohoapis.com
PAYMENTS_ALLOWED_HOST_SUFFIXES=payments.zoho.com
```

## Business Configuration

The current GHRE lease template states a returned-payment fee of **$30.00 or the maximum amount allowed by law, whichever is less**. Therefore the runtime value should be explicit rather than relying on a default.

```text
ZOHO_BOOKS_ORG_ID=<runtime value>
ZOHO_PAYMENTS_ACCOUNT_ID=<runtime value>
RETURNED_FEE_ITEM_ID=<Zoho Books item ID for returned-payment fee>
RETURNED_FEE_AMOUNT=30.00
RETURNED_FEE_INVOICE_PREFIX=RF
RETURNED_FEE_LEDGER_FIELD_API_NAME=cf_returned_payment_fee_events
OPTIONAL_LATEST_RF_INVOICE_FIELD_API_NAME=cf_returned_fee_invoice_number
UPDATE_OPTIONAL_LATEST_RF_INVOICE_FIELD=false
MAX_LEDGER_LENGTH=32000
BOOKS_PAYMENT_OPTIONS_ENABLED=true
BOOKS_PAYMENT_GATEWAYS_CSV=
```

Do not wrap values in quotes when entering them into Catalyst unless the runtime explicitly requires it.

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

To test without creating invoices:

```text
DRY_RUN=true
SEND_INVOICE_ON_CREATE=true
```

The function should verify the event and return what it would do, but it should not create or send an invoice.
