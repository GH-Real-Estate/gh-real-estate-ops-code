# GH Returned Payment Fee Webhook

Webhook/runtime code for returned or failed payment handling.

This automation is separate from the late-fee guard.

## Production file

```text
automations/returned-payment-webhook/src/index.js
```

Replace the placeholder with actual code only after the webhook design is finalized.

## Required safety behavior

- Verify webhook authenticity if the source supports signatures or shared secrets.
- Reject replayed events where feasible.
- Do not create duplicate returned-payment fees.
- Do not log tenant PII, bank info, or full payloads.
- Keep fee amount aligned with the final signed lease.
- Record deployment in `docs/runbooks/deployment-log.md`.
