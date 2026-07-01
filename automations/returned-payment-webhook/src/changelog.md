# Changelog

## 2026-05 — Production Go-Live

### Added

```text
Production HMAC webhook verification
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
Production documentation
```

### Verified

Historical failed payment successfully processed:

```text
Payment ID: 7854000000325005
Source Invoice: INV-000142
Returned Fee Invoice: RF-INV-000142-00325005
```

Production dry-run verified duplicate prevention:

```text
Reason: attempt_already_recorded_on_source_invoice
```

### Current Production Intent

```text
Future Zoho Payments payment.failed events should create and send returned-payment fee invoices automatically after signature verification, payment verification, invoice resolution, and duplicate checks.
```

## Notes

Do not store secrets in source files.

Do not leave patch, diff, or setup debris in the production function view.

Do not manually replay already-processed historical payments.
