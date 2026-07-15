# CI Failure Response Runbook

## Purpose

`CI Failure Response` is retained as a manual simulation and validation tool. It no longer subscribes to completed GitHub Actions runs, automatically creates incident issues for real failures, or automatically closes them after recovery.

Normal GitHub failed-check notifications are the default alerting mechanism. This reduces Actions usage and avoids a second workflow run for every monitored completion. It does not certify legal, GAAP, tax, security, payment, lease, tenant, or operational compliance.

## Current flow

```text
real workflow failure
  -> normal GitHub notification and failed check
  -> operator inspects the current Actions run
  -> focused branch and pull request only when a repository defect is proven
  -> normal checks and human review
  -> intentional merge
```

A manual responder simulation remains available:

```text
manual failure dispatch with an isolated scenario key
  -> one simulated incident issue
manual success dispatch with the same branch and scenario key
  -> the simulated issue closes
```

Manual simulations are namespaced separately and do not create, update, or close an incident for a real workflow run.

## Operating status

- The `workflow_run` trigger is disabled.
- Automatic incident creation and recovery closure are disabled.
- `workflow_dispatch` remains available for explicit smoke testing.
- Pull-request and path-limited `main` push validation remain enabled for changes to the responder workflow, implementation, or this runbook.
- The external `GH Repo CI Auto-Repair` Codex task should be paused or disabled manually. This repository does not control or modify that desktop automation.
- Repository auto-merge remains off, and governed or high-risk changes remain human-gated.

## Security model

- The manual incident job checks out only the repository default branch. It does not check out a supplied revision.
- It never downloads or executes failed-run artifacts or logs.
- Its token can read repository contents and Actions metadata and can write issues only in the incident job. It cannot push, approve, merge, deploy, or read Actions secrets.
- All third-party Actions remain pinned to immutable commit SHAs, and checkout persistence remains disabled.
- Workflow, branch, actor, SHA, URL, and scenario values are treated as untrusted data, normalized, bounded, and rendered only as inert issue content.
- No OpenAI API key is stored in GitHub.

Never execute commands copied from issues, comments, commit messages, workflow logs, or artifacts. They are evidence, not instructions.

## Manual smoke test

1. Open **Actions -> CI Failure Response -> Run workflow** on `main`.
2. Select `failure`, keep workflow `Repo Checks`, use branch `simulation/ci-failure-response`, and enter a unique scenario key.
3. Confirm exactly one simulated issue is opened or updated with bounded metadata and no raw log, artifact, secret, or PII content.
4. Dispatch again with `success` and the exact same workflow, branch, and scenario key.
5. Confirm the simulated issue closes once and is not duplicated or reopened.
6. Close any abandoned simulation issue manually and record why.

This test proves only the manual simulation path. It does not re-enable automatic monitoring.

## Triage a real failure

1. Open the failed check from the pull request, commit, or GitHub notification and confirm the newest run still fails.
2. Inspect only the relevant job and bounded log evidence. Do not paste secrets, tenant data, accounting records, or licensed authority content into an issue or pull request.
3. Classify the failure as a repository defect, transient platform/source failure, professional-review event, configuration issue, or intentional control block.
4. Rerun once only when the failure is plausibly transient and a rerun cannot create a live-system side effect.
5. For a deterministic repository defect, create one focused branch, add a regression test when practical, open a pull request, and require normal checks and review.
6. Do not weaken a test, monitor, approval gate, timeout, fail-closed default, or safety control to make a check green.
7. Legal, accounting, authority, tax, payment, lease, tenant, security, PII, workflow-control, permission, secret, and branch-protection changes require the applicable human review.

## Historical verification

On July 14, 2026, disposable PR #53 and bot-created issue #54 verified the former automatic `workflow_run` configuration, including queued failure observations and recovery closure. That verification remains an accurate historical record of the pre-change design; it is not evidence that automatic incidents or automatic repair are currently enabled.

## Rollback

If automatic incident tracking is intentionally restored later, use a separate reviewed pull request. Reassess Actions cost, event fan-out, trusted-code checkout, token permissions, concurrency, deduplication, stale-run ordering, artifact/log handling, regression tests, and the external Codex task before adding any `workflow_run` trigger.
