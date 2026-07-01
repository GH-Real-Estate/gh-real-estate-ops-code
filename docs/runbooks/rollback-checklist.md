# Rollback Checklist

Use when a code or Zoho automation deployment creates bad behavior.

## Immediate Control

- [ ] Disable schedule/webhook/workflow trigger.
- [ ] Stop rerunning the automation.
- [ ] Preserve sanitized notes about what happened.
- [ ] Identify the last known-good commit.
- [ ] Restore previous code/configuration.

## Cleanup

- [ ] Review affected records in Zoho directly.
- [ ] Do not store tenant-specific details in GitHub.
- [ ] Correct records manually only after confirming accounting impact.
- [ ] Record sanitized outcome in deployment log.

## Prevention

- [ ] Add a test case.
- [ ] Update `AGENTS.md`/review checklist if needed.
- [ ] Update field maps/business rules if the issue was caused by stale documentation.
