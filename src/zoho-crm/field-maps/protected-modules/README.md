# Protected Zoho CRM Module Baselines

These files are the sanitized production metadata baselines for CRM modules
that must not be changed by reconciliation work. They contain configuration
metadata only. No CRM records, organization or metadata IDs, users, profiles,
authentication values, or tenant/applicant data belong here.

## Protection boundary

| Display label | Live module API name | Fields | Captured sections (all modes) | Why protected |
|---|---|---:|---:|---|
| Leads | `Leads` | 82 | 10 | The Zillow/Catalyst intake depends on its existing API contract. |
| Property Assets | `Equipment` | 106 | 13 | The user confirmed this module is already configured correctly. |
| Pets | `Pets` | 44 | 7 | The user confirmed this module is already configured correctly. |
| Vehicles | `Tenant_Vehicles` | 29 | 5 | The user confirmed this module is already configured correctly. |

The label/API-name distinction is mandatory. In particular, live API
`Equipment` is the **Property Assets** module, and live API
`Tenant_Vehicles` is the **Vehicles** module. Do not infer a module API name
from its display label.

The existing
[`equipment.csv`](../crm-module-fields/equipment.csv) is retained as
historical target-design evidence. It does not authorize any live mutation:
its display label is stale relative to the verified production identity of
API `Equipment`. A later cleanup may relabel or archive that catalog only
after references are audited; it must never be used as a create, update,
delete, choice, or layout-placement manifest for Property Assets.

## Required mutation gate

Every CRM reconciliation or deployment plan must resolve the live module API
name before proposing a write. If it matches any protected API name, the
operation must fail closed:

- do not create, update, rename, retire, or delete fields;
- do not add, remove, reorder, rename, or recolor picklist values;
- do not attach or detach global picklists;
- do not change formulas, lookups, rollups, auto-number settings, required
  flags, defaults, uniqueness, history tracking, tooltips, or permissions;
- do not add, remove, rename, or reorder layouts, sections, or fields; and
- do not change module labels, visibility, capabilities, or tab placement.

This repository policy is an execution gate for Codex, scripts, and reviewed
deployment work. GitHub cannot prevent an administrator from changing Zoho
directly. Detecting live administrative drift requires a new metadata-only
audit and comparison with these baselines.

The checksums detect unreviewed drift; they do not make the files
cryptographically immutable because the snapshots, expected hashes, and
validator are versioned together. Enforce required checks and owner approval
on the protected branch for a stronger repository gate. An expressly
authorized baseline refresh remains possible by design.

The sanitized baseline intentionally omits profile identities/permissions and
does not contain full formula expressions. It therefore cannot detect every
formula-expression or field-access change. Before relying on either control,
perform a fresh authorized metadata-only formula and permission audit; never
infer unchanged access or calculations from a passing baseline hash.

## Leads integration lock

Leads remains read-only for CRM reconciliation. The baseline covers every
field returned by production metadata. The narrower
[`leads.csv`](../crm-module-fields/leads.csv) contains the reviewed runtime
fields plus explicitly blocked, superseded, and prohibited historical
proposals; it is not a list of fields to create. The active runtime contract is
the Zillow code and field map. Neither source may be used to remove an
unreferenced live Lead field.

At minimum, preserve the runtime APIs documented in
[`zillow-to-crm-to-contracts.md`](../zillow-to-crm-to-contracts.md), including
the `Zillow_Lead_Key` idempotency contract and the standard required Lead
fields. A runtime-code change and an expressly authorized baseline refresh
are both required before changing that contract.

## Authorized baseline refresh

A refresh is documentation work, not authorization to mutate Zoho:

1. Obtain explicit approval to refresh the protected baseline.
2. Verify the organization gate is exactly `GH Real Estate` / `production`.
3. Use metadata-only module, field, and layout reads. Never read records.
4. Omit IDs, users, profiles, audit actors/timestamps, and authentication data.
5. Compare the new result with the committed baseline and investigate every
   difference. Do not normalize away a real field, choice, or layout change.
6. Update the baseline, policy digest, tests, and operator documentation in
   one reviewed pull request.
7. Run:

   ```bash
   python src/zoho-crm/tools/validate-protected-module-baselines.py
   python -m unittest discover -s src/zoho-crm/tests -p 'test_*.py'
   ```

Changing a checksum only to make CI pass is prohibited.
