# Authority refresh runbook

## Purpose and trust boundary

This runbook operates the discovery and review controls around the approved legal and accounting libraries. The system finds potential changes and preserves evidence; it does not determine legal effect, GAAP applicability, tax treatment, contract interpretation, or compliance.

The approved July 12, 2026 legal and accounting libraries remain unchanged until a separate, complete, human-reviewed dated-release pull request is approved. Candidate branches, workflow artifacts, issues, and discovery snapshots are never production authority inputs.

## Automation schedule

GitHub cron schedules use UTC and therefore shift relative to Central Time when daylight-saving time changes.

| Workflow | Schedule | Purpose | Write boundary |
|---|---:|---|---|
| `Authority Discovery` | Daily, `11:17 UTC`; manual dispatch | Poll 13 legal and 9 accounting official-source indexes for candidate publications or metadata changes | Read-only scan; publisher may update only `authority/candidates/<domain>/`, a draft PR, and a degraded-source issue |
| `Legal Source Monitor` | Monday, `12:27 UTC`; manual dispatch | Compare known approved legal payloads and semantic fingerprints | Report artifact and bounded legal-review issue only |
| `Accounting Authority Review Calendar` | Day 1 monthly, `13:41 UTC`; manual dispatch | Check stored FASB/accounting review dates | Report artifact and bounded accounting-review issue only |
| `Authority Release Promotion` | Manual only | Validate structured review and archive immutable evidence plus the reviewed discovery snapshot | Protected draft PR affecting only `authority/releases/` and one `authority/snapshots/<domain>.json` |

No workflow auto-approves, auto-promotes, auto-merges, edits operational code, changes Zoho, posts a journal entry, changes tenant treatment, or updates the approved legal/accounting libraries.

## Required GitHub controls

Before relying on the automation:

1. Protect `main`; require pull requests, resolved conversations, required checks, and branches to be up to date before merge.
2. Require the `Validate authority refresh controls` check. The authority-check workflow runs on every pull request so this globally required check is never skipped by a path filter; its `main` push trigger remains path-limited.
3. Enable code-owner review and confirm `@GHRealEstate` in `.github/CODEOWNERS` resolves to a repository user or team.
4. Allow GitHub Actions to create pull requests. Workflows still cannot approve or merge their own pull requests, and repository auto-merge remains off.
5. Create the protected `authority-production` environment with a required human reviewer, prevent self-review when available, and restrict deployment to `main`.
6. Optionally add the repository Actions secret `CONGRESS_API_KEY`. Without it, the noncritical Library of Congress metadata source reports `configuration_required`; GovInfo and the other critical sources continue to provide enacted-law discovery coverage.

Candidate and promotion publishers explicitly dispatch `Authority Refresh Checks` and `Repo Checks` against the generated branch, which preserves branch-head evidence without a PAT. GitHub also creates `pull_request` runs for a PR opened or updated with `GITHUB_TOKEN`, but those runs may wait for a repository writer to select **Approve workflows to run**. A branch-head dispatch may not satisfy a pending PR-event check on GitHub's test-merge commit, so approve that banner and wait for the required PR checks before merging. If zero-click bot checks become necessary, use a narrowly scoped GitHub App installation token; do not introduce a long-lived PAT.

GitHub code-owner and environment approvals enforce repository control; they do not establish counsel, CPA, tax, or licensing qualifications. Enforced non-self review requires a second trusted GitHub operator. When staffing does not permit that separation, record the limitation and retain the structured professional evidence rather than describing a solo repository approval as independent review.

Do not put FASB credentials, licensed source exports, tenant information, legal client material, tax records, or production credentials in GitHub secrets or workflow artifacts.

## Local validation and discovery

Run from the repository root:

```powershell
python tools/authority_refresh/validate_system.py
python -m unittest discover -s tools/authority_refresh/tests -p "test_*.py" -v
python tools/authority_refresh/refresh.py --domain all --output-dir authority-refresh-output --run-id "manual-$(Get-Date -Format yyyyMMdd-HHmmss)"
```

Use `--domain legal` or `--domain accounting` to isolate a domain. Discovery exit codes are:

- `0`: `current`
- `2`: `review_required`
- `3`: `degraded` or a runner error

The output directory is ignored by Git. Do not copy it into an approved library. Local network policy may prevent a live scan; in that case use the default-branch GitHub workflow and inspect its artifact.

Start the default-branch workflow with the GitHub CLI when available:

```powershell
gh workflow run authority-discovery.yml --ref main
```

The same operation is available in GitHub under Actions -> Authority Discovery -> Run workflow. Run it from `main`; only the default-branch publisher is allowed to create candidate PRs or issues.

## Interpret a discovery result

### `current`

No new, modified, or comparison-eligible missing observation was detected against the reviewed discovery snapshot. No source returned `error`, and no critical source returned `configuration_required`. A noncritical configuration gap such as an absent `CONGRESS_API_KEY` may still appear, so inspect `source_results` and counts before relying on the signal.

`current` does not advance either dated release, prove source completeness, or certify legal, GAAP, tax, or operational compliance.

### `review_required`

At least one candidate change was detected. The publisher creates or updates a draft PR on `automation/authority-<domain>-candidate` containing only:

```text
authority/candidates/<domain>/latest/candidate.json
authority/candidates/<domain>/latest/README.md
authority/candidates/<domain>/latest/issue-summary.md
authority/candidates/<domain>/runs/<workflow-run-id>-<run-attempt>/candidate.json
authority/candidates/<domain>/runs/<workflow-run-id>-<run-attempt>/README.md
authority/candidates/<domain>/runs/<workflow-run-id>-<run-attempt>/issue-summary.md
```

The candidate PR records unapproved evidence; merging that evidence does not approve or update legal/accounting authority. Promotion must use the immutable per-run `candidate.json`, never the mutable `latest/candidate.json` convenience copy.

### `degraded`

At least one source returned `error`, a critical source returned `configuration_required`, or a runner/report control failed. A source `error` degrades the run even when that source is marked noncritical. The approved baseline remains in place; the publisher creates a draft candidate PR and a bounded issue when evidence is available. A degraded candidate cannot be promoted.

Treat the affected domain as not automatically verified. Inspect the artifact, rerun once if the failure appears transient, and then verify the live source manually or repair the adapter/configuration. Never translate a retrieval failure into “no change.”

### `configuration_required`

This is a per-source state. Today it is expected when `CONGRESS_API_KEY` is absent. The Congress source is noncritical, so its absence alone does not make the whole legal run degraded. Record the limitation; add the secret only if the additional legislation metadata justifies operating it.

## Important comparison semantics

- Sources marked `complete-index` may report an approved snapshot item as `missing` only after satisfying an explicit bootstrap item floor and at least 80% of that source's prior approved item count. That is still a review signal, not proof of repeal or withdrawal; a larger drop fails closed as degraded discovery.
- Sources marked `rolling-window` are limited recent-item feeds or pages. They report new and modified observations, but an old item leaving the window is not reported as missing, repealed, revoked, withdrawn, or superseded. An empty current window is healthy unless that source declares an explicit `minimum_items` floor.
- The Kansas Secretary of State page links to `rules.ks.gov`. The current adapter records official portal/index metadata; substantive rule text, adoption, amendment, effective date, and applicability remain a manual review gap.
- `codes.opkansas.org` is the City-linked electronic municipal-code copy. The Overland Park City Clerk's master copy controls, and every municipal discovery remains manual-review evidence.
- FASB sources are metadata-only. Never commit Codification text, screenshots, print exports, copied paragraphs, or scraped licensed content.

## Initial snapshot bootstrap

If `authority/snapshots/<domain>.json` does not yet exist, the first scan compares the official indexes with an empty baseline. Every successfully discovered item is therefore reported as `new`. This is expected bootstrap behavior, not a claim that every law, standard, or tax publication just changed.

The system does not auto-approve that initial inventory. A qualified reviewer must resolve every candidate change and every conservative impact route before the first reviewed discovery snapshot can be promoted. If any source errors during bootstrap, the run is `degraded` and cannot establish the snapshot. Until that first snapshot is merged, later daily runs will continue to compare against an empty baseline and may produce another all-new candidate; keep the selected per-run evidence immutable and reconcile any newer run before promotion.

## Candidate-to-promotion sequence

Use this sequence so the protected workflow can read immutable evidence from `main`:

1. Open the generated draft candidate PR and select its per-run path under `authority/candidates/<domain>/runs/<workflow-run-id>-<run-attempt>/`. Verify the candidate hash, source results, report, and candidate-only file scope.
2. If GitHub shows **Approve workflows to run**, approve it and wait for the PR-event authority and repository checks as well as the explicitly dispatched branch-head checks. Then mark the evidence PR ready and merge it to `main`. This preserves unapproved discovery evidence only; it does not modify the approved legal/accounting library, current status, policy, or runtime code.
3. Perform the qualified review below. On a separate human-authored branch from the updated `main`, add one structured approval JSON under `authority/reviews/<domain>/` that targets the immutable per-run candidate hash. Do not add the approval record to the automation candidate branch; that branch is intentionally candidate-only.
4. Validate the candidate/approval pair locally, open a focused approval-record PR, obtain code-owner and applicable professional review, and merge the approval JSON to `main`.
5. Check the newest discovery run before dispatch. The selected immutable run must exactly equal the merged `latest/candidate.json`, be no more than seven days old, and have no newer same-repository candidate PR pending. If a later run is degraded or contains additional/unresolved changes, stop and review the newer evidence.
6. Dispatch `Authority Release Promotion` from `main` with the immutable per-run candidate path and merged approval path. The `authority-production` reviewer must confirm those exact inputs before approving the environment gate.
7. If GitHub shows **Approve workflows to run**, approve it. Review and intentionally merge the resulting evidence-promotion PR only after its PR-event checks, explicitly dispatched branch-head checks, up-to-date branch check, and code-owner approval pass. If the reviewed observation changes authority content or operations, handle that work in a separate complete dated-release or implementation PR.

Both input JSON files must exist on `main` before promotion starts because the workflow accepts dispatches only from the default branch and checks out `main`. Approval and workflow input still use the immutable per-run path, while promotion requires that file to exactly match the merged `latest/` candidate as a stale-run guard.

## Review a candidate

For each `new`, `modified`, or `missing` entry:

1. Open the official HTTPS evidence URL and preserve the publisher identifier, publication/status date, retrieval context, and source weight.
2. Determine whether the observation is final, proposed, withdrawn, superseded, future-effective, historical, or merely an index/display change.
3. Verify effective date, transition, scope, applicability facts, later history, and whether another source controls.
4. Check storage and redistribution rights independently from authority weight. Default uncertain rights to link/hash/metadata-only.
5. Use `authority/impact_crosswalk.json` to identify code, policy, document, configuration, and test surfaces. Record an explicit no-change conclusion when no implementation change is needed.
6. Record exactly one structured resolution for every candidate change and every conservative `potential_impacts` mapping, with at least one HTTPS evidence URL for each reviewer determination and resolution. Potential impacts are review routes, not claims that every listed artifact must change.

Required reviewers:

- Legal baseline: an approved `qualified-legal-reviewer` determination. Applicable mappings may also require `kansas-counsel` for Kansas legal effect and applicability.
- Accounting baseline: an approved `cpa-or-qualified-accounting-reviewer` determination using authorized FASB access.
- Tax: an approved `tax-professional` determination whenever a canonical impact route requires it for the applicable tax year.
- Operations: applicable mappings may require `finance-operator` and `system-owner` determinations.
- Licensing and records: applicable mappings may require `records-and-licensing-reviewer`.

The exact required set is the union of the baseline role and every `potential_impacts[].review_gate.required_roles` value in the canonical candidate. Promotion rejects a missing required role; do not substitute an old underscored role name.

A conflicting rejection from a required reviewer blocks promotion. A GitHub PR approval alone is not structured authority approval.

Create the review record under `authority/reviews/<domain>/` on a separate human-authored branch and conform it to `authority/schemas/review-approval.schema.json`. Its `candidate_sha256` must match the immutable per-run candidate exactly; reviewer values must be GitHub-style logins; timestamps must include a UTC offset; and each change key must match the candidate's `item_id` plus `change_type`. Use only these bounded resolutions:

- `no_material_change`
- `not_applicable`
- `superseded`
- `approved_release_updated`

`approved_release_updated` requires existing reviewed paths under the applicable domain or `authority/`. Do not select it until the complete dated legal/accounting release update exists and has received its separate review.

`future_effective` is intentionally not a promotable resolution. If an observation has not taken effect, leave the candidate unpromoted, retain the evidence and review issue, and run a new discovery/review cycle when its effective-state treatment can be resolved.

For every `potential_impacts[].mapping_id`, add one `impact_resolutions` entry using one of:

- `no_change_required`
- `not_applicable`
- `approved_paths_updated`

Every impact-resolution object must include `reviewed_paths`; use an empty array when no repository path was reviewed or changed. `approved_paths_updated` requires a nonempty array, and every path must be one of that mapping's crosswalk paths and already exist in the repository. Every impact resolution also requires at least one HTTPS evidence URL. The promotion tool rejects missing, duplicate, unexpected, or out-of-crosswalk impact resolutions.

`blocked_pending_implementation` is intentionally not promotable. Keep the candidate and its review issue open until the required implementation is complete and reviewed; otherwise advancing the discovery baseline could hide an unresolved operational obligation on the next scan.

Validate without writing:

```powershell
python tools/authority_refresh/promotion.py `
  --candidate authority/candidates/legal/runs/123456789-1/candidate.json `
  --approval authority/reviews/legal/2026-07-13-123456789-1.json `
  --release-date 2026-07-13 `
  --source-revision (git rev-parse HEAD)
```

Replace the example workflow run ID, review filename, and dates with the selected merged evidence. Omitting `--confirm` is intentional. The source revision must be the clean checked-out commit containing the candidate, approval, catalog, crosswalk, and any reviewed paths. Do not run protected promotion locally. The release date cannot be in the future or precede the candidate date, prior snapshot approval, or latest structured-review date; the candidate must match merged `latest/` and be no more than seven days old.

## Protected evidence promotion

Only use promotion after every candidate change is resolved, all required professional determinations are approved, source/licensing evidence is recorded, and the candidate is not degraded.

Start it from GitHub Actions or, when available, the GitHub CLI:

```powershell
gh workflow run authority-release-promotion.yml --ref main `
  -f domain=legal `
  -f candidate_path=authority/candidates/legal/runs/123456789-1/candidate.json `
  -f approval_path=authority/reviews/legal/2026-07-13-123456789-1.json `
  -f release_date=2026-07-13 `
  -f confirmation=PROMOTE_REVIEWED_AUTHORITY_RELEASE
```

Replace the example run ID and dates with the merged evidence. For accounting, change all domain paths and `domain=accounting`. The exact confirmation is case-sensitive. The job pauses at the `authority-production` environment for its required human approval, requires a clean default-branch checkout, revalidates path scope and the structured evidence, reconstructs the candidate from each source's `observed_item_ids`, the current baseline, the canonical source catalog, and the impact crosswalk, and then opens a draft PR. It writes only:

- an immutable `authority/releases/<date>-<domain>-<hash>/` evidence set, including `validation-context.json` with the exact source revision, catalog, crosswalk, and reviewed-path hash/size manifest; and
- `authority/snapshots/<domain>.json`, the baseline for later discovery comparisons.

`release.json` binds that context by SHA-256. Required offline validation replays the same promotion rules against the archived context and historical predecessor snapshot; it does not use today's catalog, crosswalk, or reviewed-path existence. In a Git checkout, it also verifies that the archived candidate, approval, catalog, crosswalk, and reviewed-path hashes match the recorded source commit. That source commit must be the commit immediately preceding the release's unique introduction on first-parent history, not merely any older ancestor. All four immutable release files must enter together and remain present, so a stale source revision, partial introduction, deletion/re-addition, or later mutation fails closed. The validator also proves that releases form a single baseline-hash chain per domain, that child approval dates never precede their parents, and that the checked-in snapshot equals its unique tip. A missing or altered context, invalid approval, unavailable or mismatched source revision, fork, backdated child, unknown predecessor, second bootstrap root, or manually reconciled snapshot fails CI.

The workflow never merges. It blocks while a newer same-repository candidate PR is open and allows only one open automation promotion PR per domain; reconcile the candidate first, and review, merge, or close an existing promotion PR before another dispatch. It explicitly dispatches authority and repository checks for the generated commit. If GitHub shows **Approve workflows to run**, approve it and wait for the PR-event checks too. Require `Validate authority refresh controls`, require the branch to be up to date with `main`, require code-owner approval, resolve all conversations, and merge intentionally only if the evidence archive is correct. Promotion still does not change `legal/`, `accounting/`, or production systems. A substantive currentness change needs a separate complete dated-release PR with its own counsel/CPA/tax review and applicable tests.

## Triage checklist

When a discovery or legacy monitor fails:

- [ ] Open the run and identify whether scan, artifact preservation, or publishing failed.
- [ ] Download and retain the JSON and Markdown artifacts; do not rely only on the issue summary.
- [ ] Check `source_results`, `observed_item_ids`, final URLs, HTTP/content-type errors, parser errors, item counts, and critical flags.
- [ ] Distinguish transient transport failure from publisher redesign, changed source data, missing secret, or invalid baseline.
- [ ] For `rolling-window` sources, do not infer withdrawal from absence.
- [ ] For Kansas rules and Overland Park code, perform the documented manual official-source check.
- [ ] For FASB, use authorized access and retain only permissible metadata/evidence links.
- [ ] Rerun after a transient failure; repair and test an adapter change through a normal PR when the publisher contract changed.
- [ ] Keep the affected domain `degraded` until a later nondegraded run replaces it. Manual qualified review may support a specific decision, but it does not make a degraded candidate promotable.
- [ ] Do not close the review issue merely because the old dated baseline still exists.

## Rollback

Discovery and promotion are designed to be reversible without erasing evidence:

1. **Unmerged candidate:** close the draft PR and delete the candidate branch. Approved libraries and snapshots are unchanged.
2. **Unmerged promotion:** reject the `authority-production` job or close its draft PR. No reviewed snapshot reaches `main`.
3. **Defective merged evidence promotion:** do not edit or restore the snapshot directly. Produce and review a corrected candidate that references the defective tip, promote a new corrective release (using the prior reviewed items when the evidence supports that result), mark the defective release superseded or rejected in audit documentation, and preserve its evidence. Do not delete or silently rewrite history.
4. **Defective approved legal/accounting release:** pin consumers back to the last approved tag or commit, preserve the defective dated release for audit, and complete a qualified corrective release PR.
5. **Downstream operational change:** use that system's deployment and rollback runbooks. Authority automation itself never deploys or mutates live records.

After rollback, rerun system validation and the applicable discovery/legacy monitor, then record the incident and corrective evidence in the pull request and changelog.
