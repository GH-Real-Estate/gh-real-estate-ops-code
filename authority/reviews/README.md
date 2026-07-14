# Authority review records

Place structured candidate-review records here only after a qualified reviewer has
verified the official source, effective date, applicability, supersession, and licensing
status. Review records must conform to `authority/schemas/review-approval.schema.json`.

Use the immutable candidate under `authority/candidates/<domain>/runs/<workflow-run-id>-<run-attempt>/`, not the mutable `latest` copy. First merge the evidence-only candidate PR to `main`; then add this review record through a separate human-authored PR. Both files must be present on `main` before the default-branch-only promotion workflow can validate them.

The promotion tool requires every detected change and every conservative potential-impact
mapping to have a documented resolution and HTTPS evidence URL. `impact_resolutions`
must match the candidate's `potential_impacts[].mapping_id` values exactly. A generic
GitHub approval is not a substitute for this record.

Every impact-resolution object includes `reviewed_paths`; use an empty array when no repository path was reviewed or changed. A promotable impact determination may be `no_change_required`, `not_applicable`, or `approved_paths_updated`. The last option requires existing `reviewed_paths` drawn only from that mapping's `affected_paths` list. `blocked_pending_implementation` is not promotable: retain the candidate and issue until implementation and review are complete. This gate prevents an authority observation from silently changing code, policy, or production.
