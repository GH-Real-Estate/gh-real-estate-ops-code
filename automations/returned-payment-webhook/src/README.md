# GH Real Estate — Zoho Payments Returned-Payment Fee Webhook

## Purpose

This Zoho Catalyst Advanced I/O function receives `payment.failed` webhook events from Zoho Payments and creates a returned-payment fee invoice in Zoho Books when a tenant payment fails or returns.

The function is built for GH Real Estate’s rent/payment workflow. It is designed to prevent duplicate fee invoices, reject unauthenticated webhook traffic, and verify each failed payment directly with Zoho before taking any financial action.

## Current Production Status

Status: **Live Production**

Current production endpoint:

```text
https://gh-returned-payment-fee-webhook-924161115.catalystserverless.com/server/gh_zpayments_returned_fee_webhook/zpayments/payment-failed
```

Production behavior:

```text
REGISTRATION_ONLY=false
DRY_RUN=false
SEND_INVOICE_ON_CREATE=true
```

This means future verified failed-payment events should create and send returned-payment fee invoices automatically.

## What This Function Does

1. Receives a Zoho Payments `payment.failed` webhook.
2. Requires a valid `X-Zoho-Webhook-Signature` HMAC signature.
3. Validates method, path, content type, body size, timestamp, and replay safety.
4. Extracts the Zoho Payments `payment_id`.
5. Calls Zoho Payments by OAuth2 to verify the payment really failed.
6. Resolves the related Zoho Books invoice.
7. Uses fallback parsing when Zoho Payments has `invoice_number=null` but the invoice number exists in the payment description.
8. Checks the source invoice ledger/idempotency fields to prevent duplicate returned-fee invoices.
9. Creates a returned-payment fee invoice in Zoho Books.
10. Optionally sends the invoice on creation when `SEND_INVOICE_ON_CREATE=true`.
11. Records the failed-payment attempt token so future retries/replays are ignored.

## Known Successful Historical Production Test

Historical failed payment processed successfully:

```text
Payment ID: 7854000000325005
Source Invoice: INV-000142
Returned Fee Invoice: RF-INV-000142-00325005
Returned Fee Invoice ID: 5858793000003082001
```

Do not replay that historical payment again in live mode.

## Runtime Files

Only these files affect runtime behavior:

```text
index.js
package.json
package-lock.json
catalyst-config.json
node_modules/
```

Documentation files do not control runtime behavior.

## Operational Warning

Do not set `DRY_RUN=false` unless all live-mode safety variables are intentionally configured.

Do not store OAuth secrets, webhook signing keys, or refresh tokens in source files. All secrets belong in Zoho Catalyst Environment Variables.

## Owner Notes

This function intentionally does not route through Zoho Creator. Catalyst owns the transaction because this is a financial automation. It must verify the payment, resolve the invoice, enforce idempotency, and create the Books fee invoice in one controlled backend flow.
