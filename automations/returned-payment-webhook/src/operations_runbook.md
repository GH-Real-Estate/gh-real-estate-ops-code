# Operations Runbook

## Production Endpoint

```text
https://gh-returned-payment-fee-webhook-924161115.catalystserverless.com/server/gh_zpayments_returned_fee_webhook/zpayments/payment-failed
```

Use this endpoint in Zoho Payments for the `payment.failed` webhook.

## Normal Production Mode

```text
REGISTRATION_ONLY=false
DRY_RUN=false
SEND_INVOICE_ON_CREATE=true
```

Expected behavior:

```text
A verified failed payment creates a returned-payment fee invoice and sends it to the tenant.
```

## Safe Production Dry Run

To test the production endpoint without creating invoices:

```text
DRY_RUN=true
```

Expected dry-run behavior:

```text
The function verifies the payment, resolves the invoice, checks duplicates, and returns what it would do.
No invoice is created.
No email is sent.
```

After testing, return to:

```text
DRY_RUN=false
```

## Live Mode Enablement Checklist

Before enabling live invoice creation, confirm:

```text
Zoho Payments webhook URL points to the Production endpoint
Production ZPAYMENTS_WEBHOOK_SIGNING_KEY matches the Zoho Payments webhook signing key
Production OAuth2 variables are present
Production Books org ID is correct
Production Payments account ID is correct
Returned fee item ID is correct
DRY_RUN=false
SEND_INVOICE_ON_CREATE=true
LIVE_MODE_CONFIRMATION=GH_RETURNED_FEE_LIVE_APPROVED
Debug/test routes are disabled
```

## What To Check After A Returned-Fee Invoice Is Created

Search Zoho Books invoices for the new RF invoice.

Confirm:

```text
Customer matches the original invoice
Source invoice is referenced
Fee amount is correct
Returned-payment fee item is correct
Payment ID or attempt token is recorded
No duplicate RF invoice exists
Invoice was sent if SEND_INVOICE_ON_CREATE=true
```

## Historical Processed Payment

The following historical payment has already been processed:

```text
Payment ID: 7854000000325005
Source Invoice: INV-000142
Returned Fee Invoice: RF-INV-000142-00325005
```

Do not replay this payment in live mode again.

## Common Responses

### `created_returned_fee_invoice`

Meaning:

```text
The function created the returned-payment fee invoice successfully.
```

Action:

```text
Verify the invoice in Zoho Books.
```

### `dry_run_would_create_returned_fee_invoice`

Meaning:

```text
The function would create the returned-fee invoice, but DRY_RUN=true prevented creation.
```

Action:

```text
Use this only for testing. Switch DRY_RUN=false only when ready.
```

### `attempt_already_recorded_on_source_invoice`

Meaning:

```text
The failed payment was already recorded on the source invoice ledger.
```

Action:

```text
No action needed unless the ledger is incorrect.
```

### `payment_processing_lock_active`

Meaning:

```text
The same payment was processed recently and the temporary lock has not expired.
```

Action:

```text
Wait at least 5–6 minutes and retry only if there is a valid operational reason.
```

### `payment_not_failed_after_api_verification`

Meaning:

```text
The webhook said payment.failed, but Zoho Payments API says the payment is not failed.
```

Action:

```text
No returned-fee invoice should be created.
```

### `books_invoice_not_found`

Meaning:

```text
The failed payment could not be mapped to a Zoho Books invoice.
```

Action:

```text
Inspect the Zoho Payments payment description and metadata. Confirm the original payment came from a Books invoice payment flow.
```

### `invalid_signature` or `Webhook signature verification failed`

Meaning:

```text
The webhook signing key or signed body does not match.
```

Action:

```text
Confirm ZPAYMENTS_WEBHOOK_SIGNING_KEY exactly matches the Zoho Payments webhook signing key.
Remove quotes, spaces, or line breaks.
```

### `missing_oauth_env`

Meaning:

```text
The function cannot see one or more OAuth2 environment variables.
```

Action:

```text
Confirm ZOHO_CLIENT_ID, ZOHO_CLIENT_SECRET, and ZOHO_REFRESH_TOKEN exist in the active Catalyst environment.
```

## Manual Replay Policy

Manual replay should only be used for testing or recovery.

Do not manually replay a payment that already created a returned-fee invoice.

If manual replay is needed, always use a unique `event_id`.

## Emergency Stop

To stop all invoice creation immediately:

```text
DRY_RUN=true
```

For a stronger stop:

```text
REGISTRATION_ONLY=true
```

If needed, also disable the Zoho Payments webhook in Zoho Payments.

## Recovery After Accidental Duplicate

If a duplicate returned-fee invoice is created:

```text
1. Do not delete immediately unless accounting policy allows it.
2. Void or credit according to GH Real Estate accounting practice.
3. Confirm the source invoice ledger contains only the correct payment attempt.
4. Check duplicate-detection logic before re-enabling live mode.
```
