# Animal Addendum Business Rules

> **Status:** Operational draft for attorney and implementation review. This file is not the lease, an accommodation decision, or legal advice. The actual Pet and Assistance Animal Addendum remains an attorney-review draft outside this repository. The final approved template and signed documents belong in Zoho Contracts, Zoho Sign, and Zoho WorkDrive.
>
> **Authority baseline:** GH legal release verified through July 12, 2026. Official source text and the final signed lease control over this summary.

## Purpose

These rules define the intended business behavior for one consolidated **Pet and Assistance Animal Addendum**. The design replaces separate ordinary-pet and assistance-animal addenda while preserving the different legal and financial treatment required for each animal.

This page may be used to review the template, configure merge fields, design validation, and test the Zoho Contracts workflow. It does not authorize tenant execution, a production template replacement, an accommodation denial, a charge, an animal-removal demand, or enforcement action.

## Source-of-Truth Order

Apply the following order when a conflict appears:

1. Nonwaivable federal, Kansas, and applicable local law.
2. A final individualized written accommodation decision for the animal.
3. The attorney-approved, executed Pet and Assistance Animal Addendum.
4. The executed Residential Lease.
5. Approved written property rules and GH operating policy.
6. This operational summary and the related merge-field map.

Do not silently resolve a conflict. Stop generation or enforcement and escalate it for legal or business review.

## Single-Document Architecture

Use one addendum for the household, with a separate classification for every listed animal.

| Classification | Meaning | Ordinary-pet charges | Ordinary-pet eligibility rules | Accommodation review |
|---|---|---|---|---|
| `Ordinary Pet` | An animal specifically approved under the Lease | May apply only when completed in the addendum | Apply only to the identified animal | Not applicable unless a later accommodation request is made |
| `Approved Assistance Animal` | An identified animal covered by a completed individualized accommodation decision | Must be `$0.00` / not applicable | Do not apply automatically | Completed; keep private support records outside the Lease packet |
| `Interim Assistance Animal` | An identified animal covered by an express temporary written arrangement while review is pending | Must be `$0.00` / not applicable while interim status applies | Do not apply automatically | Pending; interim terms and expiration must be stated |

The classification, effective date, and identifying description are required for each animal. Approval does not automatically transfer to a replacement or additional animal.

## Generation and Execution Gate

The document must not be released for signature until all of the following are true:

- The final form has been approved by qualified Kansas landlord-tenant/fair-housing counsel.
- The final form has been compared with the complete current lease, not only the payment-automation summary in this repository.
- Lease number, lease date, addendum effective date, premises/unit, affected tenant names, and landlord name are populated.
- Every listed animal has exactly one classification, name or other identifying label, species/type, identifying description, and classification effective date.
- Household-status checkboxes are derived from the animal schedule and agree with it.
- Every ordinary-pet charge is populated with a numeric amount or an explicit not-applicable selection; no financial field is blank.
- Approved and interim assistance animals are excluded from pet-deposit, pet-rent, pet-fee, and animal-specific insurance calculations.
- Any interim arrangement states its operational terms and expiration date.
- No diagnosis, medical record, disability details, accommodation support document, live signature image, or tenant-specific test payload is placed in this repository or merged into the lease packet.
- The signer workflow does not make a tenant signature a condition of an accommodation that applicable law otherwise requires.

## Ordinary-Pet Approval Rules

- Approval is exact-animal approval. It does not cover an additional, replacement, temporary, visiting, foster, boarding, pet-sitting, or stray animal.
- Record breed/mix, age, approximate adult weight, and photo-received status only for an Ordinary Pet, unless counsel approves another lawful operational need.
- Do not infer a universal breed, weight, species, number, age, or spay/neuter policy from this page. Those standards remain an unresolved business, insurance, and counsel decision.
- No breeding, sale, boarding, kennel, training business, or other commercial animal activity is allowed.
- Do not approve an animal as an Ordinary Pet when it is prohibited by law or has been lawfully designated dangerous. A disability-related request involving an animal must be routed to the individualized accommodation workflow.
- A guest's service or other animal that applicable law requires GH to admit is not an unauthorized guest pet.

## Ordinary-Pet Charges

| Rule | Required behavior |
|---|---|
| Additional pet security deposit | One aggregate refundable deposit for all approved Ordinary Pets; never a separate deposit per animal |
| Kansas cap | Aggregate additional pet deposit must not exceed one-half of one month's periodic rent under K.S.A. 58-2550 |
| Deposit accounting | Treat as part of the Kansas security-deposit regime; account for, itemize, apply, and return it with the general security deposit as required by the lease and law |
| Monthly pet rent | Classify as an `Other Charge`, not `Base Rent` |
| Blank fields | Generation must fail; the template fallback is `$0.00`, but production must require `$0.00` or an explicit not-applicable choice |
| Nonrefundable administration fee | Not authorized by the current GH fee policy; do not merge, invoice, or collect it |
| Late fee, interest, and payment allocation | Do not create a separate formula in the animal addendum; the final lease and approved automation rules control |
| Approved or interim assistance animal | No pet fee, pet rent, pet deposit, or animal-specific insurance requirement as a condition of the accommodation |

The actual pet-deposit amount, monthly pet-rent rate, chargeable Ordinary-Pet count, first due date, and any approved proration method remain required business inputs. Do not deploy placeholder or blank values.

## Assistance-Animal Workflow Rules

- A reasonable-accommodation request may be made orally or in writing by the individual or a representative. The addendum is not a mandatory request form.
- Route the request to a separate, confidential accommodation workflow. Only the final operational decision and conditions needed to implement it belong in the signed packet.
- A commercial registry, certificate, card, vest, or internet letter is neither required nor independently conclusive.
- Do not request a diagnosis, medical records, or disability details beyond information lawfully permitted and reasonably necessary for the individualized review.
- Do not use an ordinary-pet approval, breed, size, species, number, photograph, charge, insurance, or revocation rule automatically against an approved or interim assistance animal.
- Apply the Fair Housing Act, 24 C.F.R. section 100.204, Kansas law, and any applicable conditional program rule through an individualized analysis. Consider necessity, reasonableness, undue financial or administrative burden, fundamental alteration, direct threat, substantial property damage, and effective mitigation only as applicable to the facts.
- A direct-threat or substantial-damage decision must rely on reliable, objective evidence about the specific animal, current conduct or recent overt acts, the nature/duration/severity/probability of the risk, and whether reasonable measures would sufficiently reduce it. Do not rely on generalized fear, stereotype, breed, size, or species alone.
- A pending request is not automatically approved or denied. Animal presence during review must follow applicable law and any express interim written arrangement.
- Approval continues through renewal, extension, or holdover unless lawfully modified after an individualized review. Do not require routine reapplication solely because the lease renewed.
- A replacement or additional animal requires an updated individualized review; removal of one animal does not waive the right to request another reasonable accommodation.

### 2026 federal-guidance caution

HUD withdrew the 2013 and 2020 animal notices effective September 17, 2025. HUD's May 22, 2026 FHEO memorandum describes a training-centered federal enforcement posture, but it is nonbinding, does not amend the Fair Housing Act or 24 C.F.R. section 100.204, and expressly does not eliminate private claims. Do not implement a categorical trained-animal-only rule or a categorical entitlement for every untrained emotional-support-animal request. Counsel must approve the decision tree used for training, nexus, documentation, fees, and untrained-animal requests.

## Neutral Rules for All Animals

Subject to a required accommodation, the final addendum should require:

- Humane care, adequate food, water, shelter, sanitation, supervision, and appropriate veterinary care.
- All licenses, permits, tags, rabies vaccinations, other vaccinations, and quarantine steps required by law.
- Reasonable control and lawful restraint in common areas, without unnecessarily interfering with disability-related work or assistance.
- Prompt waste removal and proper disposal; no animal waste or litter in plumbing.
- No roaming, unattended animal in common/shared areas or vehicles, persistent odor, infestation, unsanitary condition, repeated excessive noise, property damage, threatening conduct, bite, attack, or unreasonable neighbor disturbance.
- Prior written consent for an animal door, cage, run, enclosure, fence, attached habitat, or other permanent alteration, subject to any reasonable-modification right.
- Prompt notice of an escape, bite, attack, injury, substantial damage, quarantine, dangerous-animal designation, animal-control contact, or lapse of a legally required license or vaccination.

The applicable Overland Park animal-control, licensing, rabies, waste, control, quarantine, and dangerous-animal requirements remain controlling and may change. Do not copy a fixed ordinance rule into automation without a current legal check.

## Damage, Access, Emergency, and Enforcement

- Charge only reasonable, actual, documented amounts lawfully caused by the tenant or an animal. Do not assess an automatic cleaning, deodorizing, pest, damage, or incident fee merely because an animal was present.
- Do not recover twice for the same loss or add prohibited indemnity, exculpation, attorney-fee, confession-of-judgment, or jury-waiver language.
- Coordinate lawful unit access and animal control reasonably. For an approved or interim assistance animal, use an access method consistent with the accommodation.
- The tenant remains responsible for animal care during an absence. GH may contact the stated emergency caregiver or appropriate authorities for an imminent safety concern but assumes no continuing animal-care duty.
- Do not implement automatic 24-hour removal, seizure, surrender, disposal, lockout, eviction, or other self-help language.
- Ordinary-pet permission may be withdrawn for a material violation only through the notice, cure, and remedy process required by the lease and law. An approved or interim assistance animal requires an individualized reassessment and mitigation review, except for immediate lawful action needed for an imminent threat.

## Required Human Decisions Before Production

1. Attorney approval of the final consolidated form and the post-May-2026 assistance-animal decision process.
2. Full-lease reconciliation for definitions of Rent, Base Rent, Other Charges, security deposit, payment application, access, default, notice, renewal, and rules.
3. Confirmed pet-deposit and monthly-pet-rent pricing, due dates, proration, accounting, and invoicing ownership.
4. Decision on ordinary-pet eligibility standards, supported by consistent administration and insurance review.
5. Decision on the standard interim-arrangement duration and escalation path.
6. Applicability check for HCV, Section 504, HUD-insured/assisted housing, federally backed financing, or another program-specific overlay.
7. Final Zoho field/API names, source-system ownership, signature routing, privacy permissions, and validation tests.

## Authority and Internal-Policy Crosswalk

| Topic | Status | Repository reference |
|---|---|---|
| Kansas pet-deposit cap and security-deposit treatment, K.S.A. 58-2550 | Binding Kansas law; verify live before use | `legal/text/current/authorities/kansas/core-article25/k-s-a-58-2550-2d8cc759c5.md` |
| Prohibited lease terms, K.S.A. 58-2547 | Binding Kansas law; verify live before use | `legal/CURRENT_AUTHORITY_INDEX.md` and the matching approved authority file |
| Tenant duties, rules, and remedies, K.S.A. 58-2555, 58-2556, and 58-2564 | Binding Kansas law; verify live before use | `legal/CURRENT_AUTHORITY_INDEX.md` and matching `legal/text/current/authorities/kansas/` files |
| Kansas fair-housing accommodation law, K.S.A. 44-1016 | Binding Kansas law; fact-specific | `legal/text/current/authorities/kansas/fair-housing/k-s-a-44-1016-8c156bd9ba.md` |
| Fair Housing Act and 24 C.F.R. sections 100.202 and 100.204 | Binding federal law/regulation; applicability and facts control | `legal/text/current/authorities/federal/federal-official/24-c-f-r-part-100-10d5e95fc1.md` and `legal/CURRENT_AUTHORITY_INDEX.md` |
| HUD FHEO memorandum dated May 22, 2026 | Nonbinding enforcement guidance | `legal/text/current/authorities/federal/federal-official/hud-fheo-memorandum-may-22-2026-d1bcc85d6f.md` |
| HUD/DOJ Joint Statement dated May 17, 2004 | Nonbinding guidance; use only with current binding law | `legal/text/current/authorities/federal/federal-official/hud-doj-joint-statement-may-17-2004-aa52e64623.md` |
| Overland Park Municipal Code Title 6 | Binding local ordinance; current text controls | `legal/text/current/authorities/overland-park/overland-park-code/opmc-toc-006-3b5562294e.md` |
| Lease payment automation summary | Internal operational summary, not the lease | `docs/business-rules/lease-automation-rules.md` |
| Addendum merge fields | Proposed technical map; not a legal source | `src/zoho-contracts/field-maps/animal-addendum-merge-fields.md` |

Start legal review with `legal/CURRENT_AUTHORITY_INDEX.md`, `legal/PROJECT_INSTRUCTIONS.md`, and `legal/SOURCE_GAPS.md`. Official source text and qualified counsel control over this file.

## Implementation and Rollback

- Keep both legacy templates active until counsel approves the consolidated form and the complete merge/signature path passes sanitized tests.
- After approval, replace the two legacy tenant-facing templates with one consolidated template in Zoho Contracts/WorkDrive and archive the superseded versions with clear effective dates.
- Do not interpret merging this Markdown file as deploying or approving a lease document.
- Rollback is documentation-only: revert this file and the related merge-field map. A template or signed-document rollback must occur in Zoho Contracts/WorkDrive under the approved document-control process.

