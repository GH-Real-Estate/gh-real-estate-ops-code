# Returned Payment Webhook Changelog

## 2026-07-01 — Repo Structure Cleanup

- Moved webhook package under `src/zoho-payments/webhooks/returned-payment-fee/`.
- Kept runtime code content unchanged.
- Restored pinned Node package metadata and lockfile under the new package location.
- Sanitized operational documentation so real production endpoints, payment IDs, invoice IDs, and returned-fee invoice IDs are not stored in GitHub.

## 2026-05 — Production Hardening Record

High-level features documented from the prior implementation:

```text
HMAC webhook verification
Zoho Payments API verification through OAuth2
Zoho Books invoice lookup and fee invoice creation through OAuth2
Invoice description fallback parser for null invoice_number cases
Dry-run mode
Live-mode confirmation circuit breaker
Replay defense
Payment-level processing lock
Attempt-token idempotency
Returned-fee invoice auto-send support
Generic public errors
```

Do not store real historical payment IDs or invoice IDs in this changelog.
