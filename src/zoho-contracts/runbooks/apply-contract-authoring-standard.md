# Apply the Zoho Contracts Authoring Standard

This runbook applies the repository-governed authoring standard to a live Zoho Contracts contract type and verifies its Zoho Sign handoff. Repository changes do not alter live Zoho configuration.

## Controls

- Use only synthetic test parties and controlled GHRE-owned test mailboxes during validation. Never send a test envelope to an arbitrary, reserved, or real tenant address.
- Preserve the currently published template and record its version before editing.
- Do not rewrite attorney-approved or legally mandated language to satisfy typography.
- Do not publish until the rendered PDF and Zoho Sign field placement have been inspected.
- Treat recipient numbers such as `R1` as contiguous field-ownership indexes for the actual recipients added to the request. They are not permanent Party A/Party B identities and they do not determine signing order.
- GH Real Estate, LLC must be the final actual recipient and must have the final signing position in every document GH signs. Do not create placeholder recipients to force GH into a fixed R-number.

## Source Files

- `../standards/contract-authoring-standard.md`
- `../standards/contract-authoring-standard.json`
- `../../zoho-sign/field-tags/zoho-contracts-text-tag-registry.md`
- `../../zoho-sign/recipient-manifests/ghre-canonical-recipient-policy.json`
- `../../zoho-sign/recipient-manifests/README.md`
- `../templates/clause-definition.template.json`
- `../../../docs/standards/document-drafting-standard.md`

## 1. Preflight

1. Record the contract type, current template status, version, approval workflow, and last-published time.
2. Confirm that Inter Regular and Inter Bold are available organization-wide in the Zoho editor.
3. If Inter is unavailable, stop the production update and have an administrator add the approved Inter Regular and Bold TTF variants through Zoho Writer's organization font settings. Seek a governed typography amendment only if organization-wide installation is impossible. Do not upload Apple San Francisco font files.
4. Export or otherwise preserve the current attorney-approved template for forward repair. Before republishing, verify that the preserved copy can actually be imported or reconstructed as a new draft.
5. Create a draft working version. Do not edit an active agreement or executed document.
6. Select or create the document-specific recipient manifest before inserting any Sign text tags. The manifest must contain only actual recipients, use contiguous R-numbers beginning with R1, and place GH Real Estate last.

## 2. Apply Page and Paragraph Styles

Configure the template styles once, then apply semantic styles instead of formatting individual paragraphs ad hoc.

| Content | Zoho/Writer style | Required rendering |
|---|---|---|
| Main document title | Title | Inter Bold, 18 pt, black, centered |
| Article heading | Heading 1 | Inter Bold, 12 pt, `#1F4E79`, left |
| Clause title | Heading 2 | Inter Bold, 11 pt, black, left |
| First-level subsection | Heading 3 | Inter Bold, 11 pt, black, left |
| Nested subsection | Heading 4 | Inter Bold, 11 pt, black, left |
| Deep nested heading | Heading 5 | Inter Bold, 11 pt, black, left |
| Operative language | Normal | Inter, 11 pt, black, left |
| Tables and forms | Normal with override | Inter, 10 pt, black |
| Header and footer | Header/Footer region | Inter, 8.5 pt, `#666666` |

Set the page and paragraph controls:

- U.S. Letter, 8.5 by 11 inches.
- 0.75-inch top, bottom, left, and right margins.
- 1.15 line spacing.
- 6 pt after ordinary paragraphs, within the approved 4–6 pt range.
- Left alignment. Never fully justify contract text.
- Keep headings with the following paragraph and enable widow/orphan control when available.

Heading levels are semantic. Do not choose a heading solely because its visual appearance is convenient, and do not use Heading 6 in GH Real Estate contract templates.

## 3. Reconcile Clause Types and Clauses

1. Compare the live **Admin → Choice Lists → Clause Types** values with the 16-value repository master list.
2. Add or rename values only through an approved, separately reviewed live-change plan. Do not silently delete legacy values that are still referenced.
3. For every new or revised clause, prepare a validated `src/zoho-contracts/clauses/**/*.clause.json` record so CI discovers it.
4. Confirm the record includes:
   - Clause Type;
   - Clause Name;
   - library Question;
   - one standard language and any approved alternatives;
   - a Clause Title and `Heading 2` rendering instruction for every language variant; and
   - a Zoho editor style for every substantive Language block.
5. Confirm exactly one language is marked standard.
6. Enter Clause Title and Language in their separate Zoho fields. Do not repeat the title as the first Language paragraph merely to simulate the title field.
7. Preserve any contract-type-specific question override separately from the library Question.
8. Do not derive a Zoho API name from a display label. Record it only after authenticated tenant metadata verifies it.

## 4. Resolve the Recipient Manifest and Add Zoho Sign Text Tags

Use the production-safe shorthand forms in the Sign registry. Keep every tag on one physical line and use straight ASCII braces and quotation marks.

Recipient roles must be generated from the actual signer set:

| Actual signers | Recipient mapping | Default routing |
|---|---|---|
| One tenant + GH | R1 Tenant 1; R2 GH | Tenant position 1; GH position 2 |
| Two tenants + GH | R1 Tenant 1; R2 Tenant 2; R3 GH | Tenants position 1; GH position 2 |
| Three tenants + GH | R1 Tenant 1; R2 Tenant 2; R3 Tenant 3; R4 GH | Tenants position 1; GH position 2 |

A guarantor, witness, or other governed signer is inserted before GH. Renumber GH to the next contiguous recipient slot. Do not leave gaps and do not create dummy recipients.

Examples:

### One tenant

```text
Tenant 1 printed name: {{N:R1}}
Tenant 1 initials: {{I:R1}}
Tenant 1 signature: {{S:R1}}
Tenant 1 date signed: {{SD:R1}}
GH signature: {{S:R2}}
GH date signed: {{SD:R2}}
```

### Three tenants

```text
Tenant 1 signature: {{S:R1}}
Tenant 1 date signed: {{SD:R1}}
Tenant 2 signature: {{S:R2}}
Tenant 2 date signed: {{SD:R2}}
Tenant 3 signature: {{S:R3}}
Tenant 3 date signed: {{SD:R3}}
GH signature: {{S:R4}}
GH date signed: {{SD:R4}}
```

`{{I:R1*}}` may be retained as a user-confirmed compatibility alias, but the canonical published form is `{{I:R1}}` and the asterisk is redundant because Initial is already required. Use `*` as a meaningful required marker only for text fields and checkboxes.

The formatted Sign Date tag below is documented by Zoho Sign but is not production-approved for the Contracts handoff until the smoke test in this runbook passes:

```text
{{SD:R1:(dateformat="MMM dd yyyy")}}
```

A Sign Date is the date the recipient completes signing. It is expected to be blank before signing; that is different from a tag failing to convert into a field.

## 5. Synthetic Contracts-to-Sign Smoke Test

1. Create a short synthetic contract of 74 pages or fewer using one of the exact supported recipient manifests and a controlled GHRE-owned test mailbox for every actual recipient.
2. Do not include absent signers or placeholder recipients. Confirm the recipient sequence is contiguous from R1 and GH is the last actual recipient.
3. Include both `{{SD:R1}}` and the formatted Sign Date tag in clearly labeled test locations when testing formatted date support.
4. Send the synthetic contract from Zoho Contracts to Zoho Sign.
5. In the Zoho Sign preview, verify:
   - no literal supported tag remains in the document;
   - each expected field exists;
   - each field is assigned to the intended actual recipient;
   - recipient indexes are contiguous with no gaps;
   - the GH recipient is the final actual recipient;
   - signature and initial fields are required;
   - text and checkbox required markers behave as intended; and
   - fields do not overlap, wrap, or shift onto another page.
6. Configure signing order separately. All non-landlord signers must have an earlier position; GH must have the highest and final position. Multiple non-landlord signers may share a position and sign in parallel.
7. Complete the signing flow with every synthetic recipient.
8. Inspect the completed document and confirm:
   - the simple Sign Date contains the actual signing date;
   - the formatted Sign Date contains that same date in `MMM dd yyyy` format when that syntax is under test;
   - signatures and initials are present;
   - the completion certificate shows the intended signer identities and signing order;
   - no signer completed after GH; and
   - the rendered PDF follows the typography profile without font substitution.
9. Record the template version, manifest, test date, result, and reviewer. Only after a passing result may the formatted Sign Date tag move from `contracts_pipeline_unverified` to a production-safe status in the registry.

## 6. Publish and Verify

1. Submit the template and clause changes through the required approval workflow.
2. Confirm the preserved prior export/copy passed the reconstruction test, then publish the contract type template.
3. Create a new synthetic contract from the published version and repeat the visual and recipient-manifest checks.
4. Verify title, clause order, alternate-language selection questions, merge fields, headers, footers, pagination, Sign fields, recipient indexes, and signing order.
5. Record the deployment in the repository deployment log without tenant PII.

Zoho states that a republished contract type template applies to contracts created after publication. It does not retroactively restyle existing or executed contracts.

## Rollback

1. Stop creating contracts from the affected type.
2. Treat rollback after republishing as a forward repair: create a new draft from the verified preserved export/copy, review it, and republish that repaired draft.
3. Do not describe this as native version restoration. Zoho's **Revert to Published Version** applies only to an unpublished draft; after republishing, the previously published version cannot be restored through native revert.
4. Re-run the synthetic contract and Sign smoke tests before resuming contract creation.
5. Record the failed version, forward-repair version, time, cause, and affected synthetic tests.
6. Do not alter executed contracts; use the approved amendment or correction process when a real agreement requires remediation.

## Official References

- [Zoho Contracts — Creating and building contract type templates](https://help.zoho.com/portal/en/kb/contracts/admin-guide/contract-types/creation-and-management/articles/creating-contract-types-and-building-templates)
- [Zoho Contracts — Managing contract types](https://help.zoho.com/portal/en/kb/contracts/admin-guide/contract-types/creation-and-management/articles/managing-contract-types)
- [Zoho Contracts — Sending for signature](https://help.zoho.com/portal/en/kb/contracts/user-guide/signature/articles/send-for-signature)
- [Zoho Sign — Automatic field addition using text tags](https://help.zoho.com/portal/en/kb/zoho-sign/user-guide/sending-a-document/articles/automatic-field-addition-in-zoho-sign)
- [Zoho Sign — Sending documents for signatures and setting signing order](https://help.zoho.com/portal/en/kb/zoho-sign/user-guide/sending-a-document/articles/send-for-signatures)
- [Zoho Sign — Document fields and date formats](https://help.zoho.com/portal/en/kb/zoho-sign/user-guide/sending-a-document/articles/document-fields-in-zoho-sign)
- [Zoho Writer — Organization custom fonts](https://help.zoho.com/portal/en/kb/writer/how-to-customize-writer/admin-settings/articles/how-to-add-new-fonts-in-zoho-writer)
