# Returned Payment Webhook Install Checklist

## Pre-install

- [ ] Confirm the source system and exact webhook event type.
- [ ] Confirm webhook authentication method.
- [ ] Confirm replay-prevention method.
- [ ] Confirm returned-payment fee rule against final signed lease.
- [ ] Confirm Zoho Books item/custom field IDs.
- [ ] Confirm no tenant PII is logged.

## Test

- [ ] Valid event accepted.
- [ ] Invalid signature rejected.
- [ ] Duplicate event ignored.
- [ ] Returned-payment fee created only once.
- [ ] Related invoice/customer matched correctly.
- [ ] Logs do not contain bank data or tenant PII.

## Deployment

- [ ] Deploy to approved runtime.
- [ ] Configure webhook URL in source system.
- [ ] Run smoke test.
- [ ] Record deployment in `docs/runbooks/deployment-log.md`.
