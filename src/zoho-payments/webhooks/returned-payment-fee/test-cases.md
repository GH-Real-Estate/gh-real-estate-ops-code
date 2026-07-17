# Returned Payment Webhook Test Cases

Use sanitized records only. These cases apply to the Zoho Payments returned/failed-payment event that runs in Zoho Catalyst and writes any approved returned-payment fee to Zoho Books.

## Automated Source-Contract Checks

The package-level automated checks live under `test/` and run with:

```text
npm run ci
```

They verify the webhook keeps safe defaults, replay/lock controls, live-mode circuit breaker requirements, the documented Zoho Payments -> Catalyst -> Zoho Books ownership model, the lease-aligned default returned-fee amount, and source-invoice partial-payment preservation.

## Manual / Runtime Cases

| Case | Setup | Expected result |
|---|---|---|
| Valid returned payment | Valid sanitized `payment.failed` event for `PAYMENT_TEST_001` | Event accepted and fee logic runs |
| Invalid signature | Same event with bad `X-Zoho-Webhook-Signature` | Event rejected before any Zoho API action |
| Replay event | Same event ID submitted twice within replay window | Second event ignored |
| Payment lock | Same payment ID submitted twice at the same time | One processing path continues; the other is ignored while lock is active |
| Missing invoice reference | Payload and Zoho Payments record lack invoice ID/number | `needs_review`; no fee created |
| Invoice not found | Payment resolves to missing Books invoice | `needs_review`; no fee created |
| Customer canceled / abandoned | Failure reason is a customer-canceled or abandoned checkout | Event ignored; no fee created |
| Payment session still active | Failed event has an active payment session | Event deferred; no fee created yet |
| Already charged fee | Ledger already contains `ZPAY_PAYMENT_TEST_001` | No duplicate fee |
| Duplicate fee invoice exists | RF invoice exists but source ledger was not updated | Existing RF invoice is detected and ledger is repaired |
| Dry run | `DRY_RUN=true` | Returns would-create result; no invoice created or emailed |
| Live circuit breaker | `DRY_RUN=false` without live confirmation | Startup/config validation fails safely |
| Lease fee amount | `RETURNED_FEE_AMOUNT=30.00` | Created/would-create RF invoice uses `$30.00`, unless law requires lower amount |
| Partial payments enabled | Source invoice has top-level `allow_partial_payments=true` | RF invoice inherits `true`; source-ledger update writes custom fields only |
| Partial payments disabled | Source invoice has top-level `allow_partial_payments=false` | RF invoice inherits `false`; source-ledger update writes custom fields only |
| Partial-payment field absent | Source response omits `allow_partial_payments` | RF creation payload omits the field and the source-ledger update leaves payment behavior untouched |
| Email disabled | `SEND_INVOICE_ON_CREATE=false` | Fee invoice may be created; email send is skipped intentionally |
| Logs check | Event processed with diagnostics off | No bank data, tenant PII, tokens, or secrets in logs |
