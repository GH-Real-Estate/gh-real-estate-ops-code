# ChatGPT and Codex legal-source instructions

Use these rules whenever the repository is consulted for a Kansas, federal, HUD, or Overland Park real-estate question involving GH Real Estate.

1. Start with `legal/CURRENT_AUTHORITY_INDEX.md` and `legal/manifests/authority_registry.json`.
2. Identify the event date, jurisdiction, property, activity, and applicability triggers before stating a rule.
3. Search `legal/text/current/authorities/` for the relevant language, then confirm it against the corresponding approved PDF and official source URL. Official source text controls.
4. State the exact citation, authority type, applicability condition, and release/verification date. Distinguish binding law from conditional law, guidance, proposals, withdrawn material, and internal GH policy.
5. Apply an effective but not-yet-integrated session-law addendum only to the provisions it actually changes. Never silently mix current and historical versions.
6. Never infer HCV participation, HUD assistance, a federally backed mortgage, pre-1978 status, zoning, owner occupancy, licensing, or another legal trigger from silence.
7. Never treat a GH policy, fee schedule, lifecycle document, lease clause, or project summary as law. Flag a conflict instead of reconciling it silently.
8. Do not use candidate material from an unmerged branch, pull request, monitoring report, proposal, or withdrawn source as current authority.
9. For a historical question, use the law effective on the event date and clearly label any uncertainty. Do not apply the current release retroactively without checking history.
10. For eviction, accommodation, screening denial, security-deposit withholding, consumer-report adverse action, lead disclosure, fair-housing advertising, filing, or another high-risk action, recheck the live official source and recommend review by qualified Kansas counsel.

## Citation format

Include:

- Exact legal citation and section.
- Repository path or PDF bundle and page range.
- Official source URL.
- Status: binding, conditional, guidance, proposed, or withdrawn.
- “Verified through July 12, 2026” unless a later approved verification is recorded.

## Baseline prompt for a ChatGPT Project

> Use the uploaded GH Master Authority Index and current legal PDF bundles as the approved baseline. When currentness could affect an answer, search the connected `GH-Real-Estate/gh-real-estate-ops-code` repository and review `legal/CURRENT_AUTHORITY_INDEX.md`, `legal/CHANGELOG.md`, `legal/SOURCE_GAPS.md`, `legal/manifests/authority_registry.json`, and the applicable file under `legal/text/current/authorities/`. If the repository reports a change after the PDF release, flag the need for verification and do not silently blend versions. Never use superseded, proposed, withdrawn, monitoring, or archived material as current authority. Internal GH policy and property context are facts, not law.
