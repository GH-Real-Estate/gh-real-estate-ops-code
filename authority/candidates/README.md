# Authority discovery candidates

This directory holds unapproved evidence produced by the weekly Sunday authority-discovery workflow. It is a review queue, not a current legal or accounting library.

## States

- `current`: no new, modified, or comparison-eligible missing item was detected and no degradation condition occurred; a noncritical `configuration_required` result may still be present.
- `review_required`: at least one new, modified, or legitimately missing observation requires human review.
- `degraded`: any source returned `error`, a critical source returned `configuration_required`, or the runner/artifact control failed. Preserve the approved baseline and verify live official sources before high-risk reliance.

Recent-item sources marked `rolling-window` do not report an old item falling out of a limited feed/API window as missing. The optional Library of Congress source reports `configuration_required` when `CONGRESS_API_KEY` is absent and, because it is noncritical, does not by itself degrade critical enacted-law discovery through GovInfo.

## Handling rules

- Workflow output is limited to `authority/candidates/<domain>/latest/` plus per-run `runs/<workflow-run-id>-<run-attempt>/` evidence on a bot branch and a draft pull request. It never edits `legal/`, `accounting/`, or runtime code and never merges itself.
- Verify every observation at the live official URL. Record legal effect, effective date, applicability facts, supersession, licensing/storage rights, and a resolution for every change and every `potential_impacts` mapping.
- Legal candidates require qualified legal review. Accounting candidates require a CPA or qualified accounting reviewer using authorized FASB access; tax items also require tax-year-specific review. Add licensing review when storage or redistribution rights are not clear.
- FASB candidates remain metadata-only. Never commit Codification text, screenshots, print exports, or scraped licensed content.
- A degraded candidate cannot be promoted. Resolve or explicitly replace the failed evidence with a new healthy run.
- Promotion archives reviewed discovery evidence and a comparison snapshot only. A legal/accounting currentness change still requires a separate, complete dated-release pull request.

For a promotable candidate, verify and merge the evidence-only candidate PR to `main`, then add the structured approval JSON through a separate human-authored PR and merge it to `main`. Reconcile any newer discovery run, then dispatch protected promotion from `main` using the immutable `runs/<workflow-run-id>-<run-attempt>/candidate.json` path, never `latest/candidate.json`. Merging candidate evidence records what was observed; it does not approve or change authority.

If no reviewed snapshot exists, the first scan reports every discovered item as `new`. That is baseline bootstrap, not evidence that every source just changed; every item and conservative impact route still requires a structured resolution.

Follow [`../../docs/runbooks/authority-refresh.md`](../../docs/runbooks/authority-refresh.md) for triage, review, promotion, and rollback.
