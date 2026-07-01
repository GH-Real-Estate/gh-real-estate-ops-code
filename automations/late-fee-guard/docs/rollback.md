# Late Fee Guard Rollback

Use this if a live late-fee deployment behaves incorrectly.

## Immediate steps

1. Disable the Zoho Books schedule/function trigger.
2. Do not delete invoices blindly.
3. Identify affected test or production invoices.
4. Preserve sanitized evidence for debugging.
5. Restore the prior known-good code from GitHub history.
6. Re-enable only after smoke testing.

## Manual cleanup

Any production invoice cleanup should be handled in Zoho Books with care and documented in the deployment log. Do not store tenant-specific cleanup details in this repo.
