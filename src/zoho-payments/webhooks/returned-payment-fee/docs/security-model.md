# Security Model

## Summary

This function uses layered security.

Inbound webhook authentication uses HMAC signature verification. Outbound Zoho API access uses OAuth2.

Do not replace the inbound HMAC model with OAuth2 unless Zoho Payments supports sending OAuth bearer tokens or custom authentication headers on webhook delivery.

## Security Flow

```text
Zoho Payments webhook
→ Catalyst function
→ HMAC verification
→ replay/timestamp/body/path validation
→ Zoho Payments API verification by OAuth2
→ Zoho Books API action by OAuth2
→ returned-fee invoice creation
```

## Inbound Security: Zoho Payments To Catalyst

The webhook request must satisfy all of the following:

```text
POST method
Allowed path: /zpayments/payment-failed
Content-Type: application/json
Body size under limit
Valid X-Zoho-Webhook-Signature
Signature timestamp within tolerance
Replay check passes
Payment-level lock is not active
```

The webhook body alone is not trusted.

## Outbound Security: Catalyst To Zoho

Catalyst uses OAuth2 to access:

```text
Zoho Payments API
Zoho Books API
```

OAuth2 credentials must be stored in runtime environment variables:

```text
ZOHO_CLIENT_ID
ZOHO_CLIENT_SECRET
ZOHO_REFRESH_TOKEN
```

The function obtains access tokens at runtime and uses them for Zoho API calls.

## Source-Of-Truth Verification

The function does not blindly trust the webhook event type.

For every failed-payment event, it calls Zoho Payments using OAuth2 and verifies the actual payment status.

If Zoho Payments says the payment is not failed/returned, the function ignores the event.

## Invoice Resolution

The function resolves the related Zoho Books invoice using available payment data.

Known behavior: Zoho Payments may return `invoice_number=null` for failed ACH payments even when the payment description contains the invoice number.

Use sanitized examples only in this repo:

```text
Zoho :: GH Real Estate :: INV-TEST-001
```

## Duplicate Protection

The function prevents duplicate returned-fee invoices using several controls:

```text
Replay defense cache
Payment-level processing lock
Attempt token
Source invoice ledger/custom field
Existing returned-fee invoice checks
```

Known attempt token format:

```text
ZPAY_<payment_id>
```

Sanitized example:

```text
ZPAY_PAYMENT_TEST_001
```

## Live Mode Circuit Breaker

Invoice creation requires more than `DRY_RUN=false`.

Live mode should also require:

```text
REQUIRE_LIVE_MODE_CONFIRMATION=true
LIVE_MODE_CONFIRMATION=GH_RETURNED_FEE_LIVE_APPROVED
EXPECTED_LIVE_MODE_CONFIRMATION=GH_RETURNED_FEE_LIVE_APPROVED
```

This protects against accidental live invoice creation caused by a single environment variable mistake.

## Public Error Handling

Production should use:

```text
GENERIC_PUBLIC_ERRORS=true
```

This prevents public webhook responses from exposing detailed internals.

Internal detail should be obtained from Catalyst logs using the request ID.

## Debug Routes

Diagnostic, mock, and admin routes must be disabled in Production unless there is a controlled operational reason.

Production default:

```text
ENABLE_OAUTH_DIAGNOSTIC=false
ENABLE_MOCK_PROCESSING=false
ENABLE_ADMIN_PROCESS_PAYMENT=false
DEBUG_PAYLOAD_LOGGING=false
DEBUG_SAFE_ZOHO_BODIES=false
ENABLE_HEALTH=false
```

## Security Position

This function is hardened only when the following controls are enabled:

```text
HTTPS
HMAC webhook verification
Timestamp tolerance
Replay defense
Payment-level lock
OAuth2 outbound API access
Host allowlists
Source-of-truth payment verification
Dry-run mode
Live-mode circuit breaker
Idempotency ledger
Generic public errors
No hardcoded secrets
```
