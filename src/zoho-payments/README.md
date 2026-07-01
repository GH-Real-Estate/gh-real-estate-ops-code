# Zoho Payments

Use this area for webhook handling and technical documentation driven by Zoho Payments events.

Zoho Payments is not the accounting source of truth. Zoho Books remains the accounting source of truth. Zoho Payments webhook code may still live here when the triggering event originates from Zoho Payments.

## Contents

```text
webhooks/
  returned-payment-fee/
    package.json
    src/index.js
    README.md
    install-checklist.md
    test-cases.md
```

## Rules

- Do not store ACH details, bank records, or raw payment logs here.
- Store only sanitized payload examples under `samples/zoho-payments/`.
- Returned-payment fee logic must remain separate from late-fee logic unless explicitly changed.
