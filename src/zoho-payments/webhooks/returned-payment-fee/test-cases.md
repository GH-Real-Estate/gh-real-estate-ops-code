# Returned Payment Webhook Test Cases

Use sanitized records only.

| Case | Setup | Expected result |
|---|---|---|
| Valid returned payment | Valid sample event | Event accepted and fee logic runs |
| Invalid signature | Bad signature/shared secret | Event rejected |
| Replay event | Same event ID submitted twice | Second event ignored |
| Missing invoice ID | Payload lacks invoice reference | Fail safely; no fee created |
| Already charged fee | Returned-payment fee already exists | No duplicate fee |
| Logs check | Event processed | No PII/bank data/secrets in logs |
