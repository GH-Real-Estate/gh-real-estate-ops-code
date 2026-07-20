#!/usr/bin/env python3
"""Validate the governed Residential Lease Agreement implementation package.

The validator is intentionally dependency-free. It joins the source manifest,
source crosswalk, clause records, field registry, native template components,
attachment requirements, recipient manifests, Ending Text, and Addendum B
fragments into one fail-closed Draft-only release gate.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


CONTRACT_TYPE = "Residential Lease Agreement"
PACKAGE_REL = Path("src/zoho-contracts/contract-types/residential-lease-agreement")
CLAUSE_DIR_REL = Path("src/zoho-contracts/clauses/residential-lease-agreement")
READABLE_CLAUSE_LIBRARY_REL = PACKAGE_REL / "readable-clause-library.md"
FIELD_REGISTRY_REL = Path(
    "src/zoho-contracts/field-maps/contract-field-registry.json"
)
AUTHORING_STANDARD_REL = Path(
    "src/zoho-contracts/standards/contract-authoring-standard.json"
)
RECIPIENT_DIR_REL = Path("src/zoho-sign/recipient-manifests")

PACKAGE_FILES = {
    "source_manifest": "source-manifest.json",
    "crosswalk": "source-to-clause-crosswalk.json",
    "implementation": "contract-type-implementation.json",
    "field_map": "document-field-map.json",
}
ARTIFACT_FILES = {
    "template_components": "template-components.json",
    "attachment_requirements": "attachment-requirements.json",
}
SCHEMA_FILES = {
    "source_manifest": "source-manifest.schema.json",
    "crosswalk": "source-to-clause-crosswalk.schema.json",
    "implementation": "contract-type-implementation.schema.json",
    "field_map": "document-field-map.schema.json",
}
EXPECTED_SCHEMA_REFS = {
    key: f"../../schemas/{file_name}"
    for key, file_name in SCHEMA_FILES.items()
}
EXPECTED_IMPLEMENTATION_REFS = {
    "source_manifest_ref": PACKAGE_FILES["source_manifest"],
    "crosswalk_ref": PACKAGE_FILES["crosswalk"],
    "field_map_ref": PACKAGE_FILES["field_map"],
    "template_components_ref": ARTIFACT_FILES["template_components"],
    "attachment_requirements_ref": ARTIFACT_FILES["attachment_requirements"],
}
VARIANT_FILE_NAMES = {
    "one_tenant": (
        "residential-lease-one-tenant.recipient-manifest.json",
        "one-tenant.md",
        1,
    ),
    "two_tenants": (
        "residential-lease-two-tenants.recipient-manifest.json",
        "two-tenants.md",
        2,
    ),
    "three_tenants": (
        "residential-lease-three-tenants.recipient-manifest.json",
        "three-tenants.md",
        3,
    ),
}
EXPECTED_CODES = [f"RLA-{number:03d}" for number in range(10, 600, 10)]
EXPECTED_DEPLOYMENT_STATUS = {
    "state": "draft_only",
    "published": False,
    "attorney_review_required": True,
    "execution_blocked": True,
    "signature_request_sent": False,
}
EXPECTED_SOURCE_RECORDS = (
    {
        "source_id": "lead-first-docx",
        "path": "Residential Lease Agreement - Lead-First Attorney Review Draft.docx",
        "filename": "Residential Lease Agreement - Lead-First Attorney Review Draft.docx",
        "role": "controlling_tenant_facing_language",
        "format": "docx",
        "sha256": "df3dddbc58235996dcfadd0602703e7fd1c58fdc859a5c0465312422ce03a04e",
        "page_count": 20,
        "status": "controlling_tenant_facing_language",
    },
    {
        "source_id": "lead-first-pdf",
        "path": "Residential Lease Agreement - Lead-First Attorney Review Draft.pdf",
        "filename": "Residential Lease Agreement - Lead-First Attorney Review Draft.pdf",
        "role": "controlling_visual_comparison",
        "format": "pdf",
        "sha256": "16ea38596be8c1327ead3c14b43a050f0978511a4c338ee8ae02a46242db8c42",
        "page_count": 20,
        "status": "controlling_visual_comparison",
    },
    {
        "source_id": "build-matrix",
        "path": "GH_Zoho_Contracts_Build_Matrix_2026-07-12.xlsx",
        "filename": "GH_Zoho_Contracts_Build_Matrix_2026-07-12.xlsx",
        "role": "secondary_migration_reference_only",
        "format": "xlsx",
        "sha256": "50c4f508127aa84d8efa3eb7e65944741e4d47484be457b8b057e92b61277061",
        "page_count": None,
        "status": "secondary_migration_reference_only",
    },
    {
        "source_id": "excluded-older-docx",
        "path": "Residential Lease Agreement (7).docx",
        "filename": "Residential Lease Agreement (7).docx",
        "role": "excluded",
        "format": "docx",
        "sha256": "88c3d4e3ca731bdd324f01951a0a49de18b66f88bae075857098390432f8197b",
        "page_count": 22,
        "status": "excluded",
    },
)
EXPECTED_PRODUCTION_GATE_IDS = frozenset(
    {
    "monthly_rent_source_ownership",
    "security_deposit_source_ownership",
    "statutory_notice_address",
    "attorney_reviewer",
    "intake_form",
    "signature_fragment_automation",
    "formatted_sign_date_smoke_test",
    "hoa_applicability",
    "conditional_utility_values",
    "tenant_field_api_metadata",
    "legal_currentness",
    "lead_disclosure",
    "lease_commencement_field",
    "tenant_two_three_identity_fields",
    "recipient_smoke_test",
    "inter_availability",
    "dynamic_toc",
    "header_footer_placeholder",
    "draft_visual_qa",
    "parking_terms",
    "storage_terms",
    "lease_end_time",
    "initial_amounts_due",
    "pet_terms",
    "appliance_inventory",
    "landlord_authorized_representative",
    "required_contact_fields",
    "municipality_jurisdiction_applicability",
    "required_initials_design",
    }
)
# Kept as an alias for callers that use the earlier constant name.
REQUIRED_OPEN_GATES = EXPECTED_PRODUCTION_GATE_IDS
LANDLORD_BUSINESS_ROLE = "GH Real Estate, LLC Authorized Representative"

CLAUSE_NAME_RE = re.compile(
    r"^(?P<code>RLA-\d{3}) \u2014 Residential Lease \u2014 (?P<topic>.+)$"
)
CLAUSE_FILE_RE = re.compile(
    r"^(?P<code>rla-\d{3})-(?P<slug>[a-z0-9]+(?:-[a-z0-9]+)*)\.clause\.json$"
)
CODE_RE = re.compile(r"\bRLA-(?P<number>\d{3})\b", re.IGNORECASE)
ROLE_RE = re.compile(r"^R(?P<number>[1-9]|1[0-9]|2[0-5])$")
TAG_RE = re.compile(r"\{\{.*?\}\}", re.DOTALL)
APPROVED_SIMPLE_ENDING_TAG_RE = re.compile(
    r"^\{\{(?P<code>S|I):(?P<role>R(?:[1-9]|1[0-9]|2[0-5]))\}\}$"
)
CANONICAL_SIGN_DATE_RE = re.compile(
    r'^\{\{SD:(?P<role>R(?:[1-9]|1[0-9]|2[0-5])):\(dateformat="MM/dd/yyyy hh:mm a z"\)\}\}$'
)


def repository_root() -> Path:
    """Return the repository root relative to this checked-in script."""

    return Path(__file__).resolve().parents[3]


def _paths(root: Path) -> dict[str, Any]:
    package = root / PACKAGE_REL
    schema_dir = root / "src/zoho-contracts/schemas"
    return {
        "package": package,
        "data": {
            key: package / file_name for key, file_name in PACKAGE_FILES.items()
        },
        "artifacts": {
            key: package / file_name for key, file_name in ARTIFACT_FILES.items()
        },
        "schemas": {
            key: schema_dir / file_name for key, file_name in SCHEMA_FILES.items()
        },
        "clause_dir": root / CLAUSE_DIR_REL,
        "readable_clause_library": root / READABLE_CLAUSE_LIBRARY_REL,
        "field_registry": root / FIELD_REGISTRY_REL,
        "authoring_standard": root / AUTHORING_STANDARD_REL,
        "recipient_dir": root / RECIPIENT_DIR_REL,
    }


def load_json(path: Path) -> dict[str, Any]:
    """Load one UTF-8 JSON object."""

    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _non_empty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _markdown_escape(value: Any) -> str:
    """Escape one value for a Markdown table cell."""

    return str(value).replace("|", "\\|").replace("\n", " ")


def _readable_article_heading_map(
    template_components: dict[str, Any],
) -> dict[int, str]:
    """Return the governed Article number-to-title mapping."""

    components = template_components.get("components")
    if not isinstance(components, list):
        raise ValueError("template-components.components must be a list")
    article_component = next(
        (
            item
            for item in components
            if isinstance(item, dict)
            and item.get("component_id") == "article-headings"
        ),
        None,
    )
    if article_component is None:
        raise ValueError("template-components must include article-headings")
    headings = article_component.get("headings")
    if not isinstance(headings, list):
        raise ValueError("article-headings.headings must be a list")

    result: dict[int, str] = {}
    for heading in headings:
        match = re.fullmatch(
            r"(?P<number>\d{1,2})\.\s+(?P<title>.+)", str(heading)
        )
        if match is None:
            raise ValueError(f"invalid article heading: {heading}")
        result[int(match.group("number"))] = match.group("title")
    return result


def _readable_clause_items(
    root: Path,
    implementation: dict[str, Any],
) -> list[
    tuple[
        dict[str, Any],
        dict[str, Any],
        list[dict[str, Any]],
        int,
    ]
]:
    """Load ordered clause definitions for the generated readable library."""

    records = implementation.get("clause_records")
    if not isinstance(records, list):
        raise ValueError("contract-type-implementation.clause_records must be a list")

    items: list[
        tuple[
            dict[str, Any],
            dict[str, Any],
            list[dict[str, Any]],
            int,
        ]
    ] = []
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("each clause record must be an object")
        clause_path = record.get("path")
        if not _non_empty(clause_path):
            raise ValueError("each clause record must include a path")
        definition = load_json(root / clause_path)
        variants = definition.get("language_variants")
        if not isinstance(variants, list) or not variants:
            raise ValueError(f"{clause_path} must include language variants")
        first_title = variants[0].get("clause_title")
        match = re.match(r"(?P<article>\d{1,2})\.", str(first_title))
        if match is None:
            raise ValueError(
                f"{clause_path} clause title must begin with an Article number"
            )
        items.append(
            (
                record,
                definition,
                variants,
                int(match.group("article")),
            )
        )
    return items


def render_readable_clause_library(root: Path) -> str:
    """Render the professional human-readable view from canonical clause JSON."""

    root = root.resolve()
    paths = _paths(root)
    implementation = load_json(paths["data"]["implementation"])
    template_components = load_json(paths["artifacts"]["template_components"])
    article_headings = _readable_article_heading_map(template_components)
    items = _readable_clause_items(root, implementation)

    articles: dict[int, list[str]] = {}
    total_variants = 0
    total_blocks = 0
    for record, _definition, variants, article in items:
        articles.setdefault(article, []).append(str(record["code"]))
        total_variants += len(variants)
        total_blocks += sum(len(variant["blocks"]) for variant in variants)

    lines = [
        "<!-- Generated by validate_residential_lease_implementation.py; edit the canonical JSON sources. -->",
        "# Residential Lease Agreement — Readable Clause Library",
        "",
        "> **ATTORNEY REVIEW DRAFT — NOT FOR TENANT EXECUTION**",
        ">",
        "> This generated reference presents the governed Residential Lease clause records in a professional, readable format. It is not the complete lease, a signed agreement, legal approval, or proof of the live Zoho configuration.",
        "",
        f"- **Contract type:** {implementation['contract_type']}",
        f"- **Implementation:** `{implementation['implementation_id']}`",
        "- **Status:** Draft only; unpublished; execution blocked",
        "- **Canonical order:** [`contract-type-implementation.json`](contract-type-implementation.json)",
        f"- **Generated content:** {len(items)} clause records; {total_variants} language variants; {total_blocks} language blocks",
        "",
        "## Source and Scope",
        "",
        "Edit the referenced `.clause.json` files—not this generated Markdown. The ordered JSON records remain the repository source of truth for the clause library. The controlling source DOCX governs tenant-facing legal wording and order, and the matching PDF governs visual comparison.",
        "",
        "This library covers the governed clause records for Articles 1–12. It does not include the cover, tables, Articles 13–14, signatures, addenda, attachments, or tenant-specific merged values. Those items remain governed by the related package files identified below.",
        "",
        "## Article Index",
        "",
        "| Article | Title | Clause records |",
        "|---:|---|---|",
    ]
    for article, codes in articles.items():
        title = article_headings.get(article)
        if title is None:
            raise ValueError(f"missing governed heading for Article {article}")
        if len(codes) == 1:
            code_range = f"`{codes[0]}`"
        else:
            code_range = f"`{codes[0]}`–`{codes[-1]}`"
        lines.append(
            f"| {article} | {_markdown_escape(title)} | "
            f"{code_range} ({len(codes)}) |"
        )

    lines.extend(
        [
            "",
            "## Related Lease Content Outside This Library",
            "",
            "- [`template-components.json`](template-components.json) governs the cover, table of contents, article headings, Sections 1.3, 1.4, 3.2, and 5.1, and Article 13.",
            "- [`ending-text/`](ending-text/) governs Article 14 and signature text for each supported tenant count.",
            "- [`addendum-b/`](addendum-b/) governs Addendum B variants.",
            "- [`attachment-requirements.json`](attachment-requirements.json) governs separately executed Addendum A and other required attachments.",
            "- [`source-to-clause-crosswalk.json`](source-to-clause-crosswalk.json) records the complete source sequence and identifies clause and non-clause content.",
            "",
        ]
    )

    current_article: int | None = None
    for record, definition, variants, article in items:
        if article != current_article:
            current_article = article
            title = article_headings.get(article)
            if title is None:
                raise ValueError(f"missing governed heading for Article {article}")
            lines.extend([f"## Article {article} — {title}", ""])

        clause_name = str(definition["clause_name"])
        match = CLAUSE_NAME_RE.fullmatch(clause_name)
        topic = match.group("topic") if match is not None else clause_name
        source_name = Path(str(record["path"])).name
        source_sections = ", ".join(
            f"`{section}`" for section in record["source_sections"]
        )
        lines.extend(
            [
                f"### {record['code']} — {topic}",
                "",
                f"- **Clause type:** {definition['clause_type']}",
                f"- **Source sections:** {source_sections}",
                f"- **Source JSON:** [`{source_name}`](../../clauses/residential-lease-agreement/{source_name})",
                f"- **Zoho API status:** `{definition['zoho_api_name_status']}`",
                "",
                f"> **Library question:** {definition['library_question']}",
                "",
            ]
        )

        for variant in variants:
            variant_title = str(variant["clause_title"])
            if len(variants) > 1:
                if variant.get("variant_kind") == "standard":
                    label = "Standard language"
                else:
                    label = (
                        "Alternate language — "
                        f"{variant.get('variant_id', 'unnamed')}"
                    )
                variant_title = f"{variant_title} ({label})"
            lines.extend([f"#### {variant_title}", ""])

            for block in variant["blocks"]:
                style = block["style"]
                text = block["text"]
                if style == "Normal":
                    lines.extend([text, ""])
                elif style == "Heading 3":
                    lines.extend([f"##### {text}", ""])
                elif style == "Heading 4":
                    lines.extend([f"###### {text}", ""])
                elif style == "Heading 5":
                    lines.extend([f"**{text}**", ""])
                else:
                    raise ValueError(f"unsupported clause language style: {style}")
        lines.extend(["---", ""])

    return "\n".join(lines).rstrip() + "\n"


def readable_clause_library_drift_errors(
    root: Path,
    actual_markdown: str,
) -> list[str]:
    """Return an error when the generated readable clause library is stale."""

    if actual_markdown != render_readable_clause_library(root):
        return [
            f"{READABLE_CLAUSE_LIBRARY_REL.as_posix()}: generated Markdown is stale; "
            "run validate_residential_lease_implementation.py --write-markdown"
        ]
    return []


def write_readable_clause_library(root: Path) -> None:
    """Write the generated readable clause library after validation passes."""

    root = root.resolve()
    path = root / READABLE_CLAUSE_LIBRARY_REL
    path.write_text(
        render_readable_clause_library(root),
        encoding="utf-8",
        newline="\n",
    )


def _json_type_matches(value: object, expected: str) -> bool:
    matches = {
        "null": value is None,
        "boolean": isinstance(value, bool),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "number": isinstance(value, (int, float)) and not isinstance(value, bool),
        "string": isinstance(value, str),
        "array": isinstance(value, list),
        "object": isinstance(value, dict),
    }
    return matches.get(expected, False)


def _json_equal(left: object, right: object) -> bool:
    if isinstance(left, (bool, int, float)) or isinstance(
        right, (bool, int, float)
    ):
        return type(left) is type(right) and left == right
    return left == right


def _resolve_local_ref(root_schema: dict[str, Any], reference: str) -> object:
    if not reference.startswith("#/"):
        raise ValueError(f"unsupported non-local schema reference: {reference}")
    current: object = root_schema
    for raw_part in reference[2:].split("/"):
        part = raw_part.replace("~1", "/").replace("~0", "~")
        if not isinstance(current, dict) or part not in current:
            raise ValueError(f"unresolved schema reference: {reference}")
        current = current[part]
    return current


def validate_json_schema(
    value: object,
    schema: object,
    *,
    root_schema: dict[str, Any] | None = None,
    path: str = "$",
) -> list[str]:
    """Validate the JSON-Schema subset used by the RLA package."""

    if not isinstance(schema, dict):
        return [f"{path}: schema node must be an object"]
    if root_schema is None:
        root_schema = schema
    problems: list[str] = []

    reference = schema.get("$ref")
    if isinstance(reference, str):
        try:
            target = _resolve_local_ref(root_schema, reference)
        except ValueError as exc:
            return [f"{path}: {exc}"]
        return validate_json_schema(
            value, target, root_schema=root_schema, path=path
        )

    any_of = schema.get("anyOf")
    if isinstance(any_of, list):
        if not any(
            not validate_json_schema(
                value, candidate, root_schema=root_schema, path=path
            )
            for candidate in any_of
        ):
            return [f"{path}: value does not satisfy anyOf"]

    if "const" in schema and not _json_equal(value, schema["const"]):
        problems.append(f"{path}: value does not match const")
    enum = schema.get("enum")
    if isinstance(enum, list) and not any(
        _json_equal(value, candidate) for candidate in enum
    ):
        problems.append(f"{path}: value is not in enum")

    expected_types = schema.get("type")
    if isinstance(expected_types, str):
        expected_types = [expected_types]
    if isinstance(expected_types, list) and not any(
        isinstance(item, str) and _json_type_matches(value, item)
        for item in expected_types
    ):
        problems.append(
            f"{path}: expected type "
            + " or ".join(str(item) for item in expected_types)
        )
        return problems

    if isinstance(value, str):
        minimum_length = schema.get("minLength")
        if isinstance(minimum_length, int) and len(value) < minimum_length:
            problems.append(f"{path}: string is shorter than minLength")
        pattern = schema.get("pattern")
        if isinstance(pattern, str) and re.search(pattern, value) is None:
            problems.append(f"{path}: string does not match pattern")

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        minimum = schema.get("minimum")
        if isinstance(minimum, (int, float)) and value < minimum:
            problems.append(f"{path}: number is below minimum")

    if isinstance(value, list):
        minimum_items = schema.get("minItems")
        if isinstance(minimum_items, int) and len(value) < minimum_items:
            problems.append(f"{path}: array has fewer than minItems")
        if schema.get("uniqueItems") is True:
            serialized = [
                json.dumps(item, sort_keys=True, separators=(",", ":"))
                for item in value
            ]
            if len(serialized) != len(set(serialized)):
                problems.append(f"{path}: array items must be unique")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                problems.extend(
                    validate_json_schema(
                        item,
                        item_schema,
                        root_schema=root_schema,
                        path=f"{path}[{index}]",
                    )
                )

    if isinstance(value, dict):
        required = schema.get("required")
        if isinstance(required, list):
            for key in required:
                if key not in value:
                    problems.append(f"{path}: missing required property {key}")
        properties = schema.get("properties")
        if not isinstance(properties, dict):
            properties = {}
        for key, child in value.items():
            if key in properties:
                problems.extend(
                    validate_json_schema(
                        child,
                        properties[key],
                        root_schema=root_schema,
                        path=f"{path}.{key}",
                    )
                )
                continue
            additional = schema.get("additionalProperties", True)
            if additional is False:
                problems.append(f"{path}: unknown property {key}")
            elif isinstance(additional, dict):
                problems.extend(
                    validate_json_schema(
                        child,
                        additional,
                        root_schema=root_schema,
                        path=f"{path}.{key}",
                    )
                )
    return problems


def validate_deployment_status(
    value: Any, *, path: str = "deployment_status"
) -> list[str]:
    """Require the exact fail-closed Draft-only state."""

    if value != EXPECTED_DEPLOYMENT_STATUS:
        return [
            f"{path} must exactly equal the governed Draft-only state "
            f"{EXPECTED_DEPLOYMENT_STATUS}"
        ]
    return []


def validate_schema_reference(
    payload: Any, package_key: str
) -> list[str]:
    """Lock a package file to its checked-in schema path."""

    expected = EXPECTED_SCHEMA_REFS.get(package_key)
    if expected is None:
        return [f"unknown package schema key: {package_key}"]
    if not isinstance(payload, dict):
        return [f"{package_key} must be an object"]
    if payload.get("$schema") != expected:
        return [
            f"{package_key}.$schema must exactly reference {expected}"
        ]
    return []


def validate_source_manifest(manifest: Any) -> list[str]:
    """Validate source inventory identity, ordering, and Draft-only status."""

    if not isinstance(manifest, dict):
        return ["source manifest must be an object"]
    errors = validate_deployment_status(
        manifest.get("deployment_status"), path="source-manifest.deployment_status"
    )
    if manifest.get("contract_type") != CONTRACT_TYPE:
        errors.append(f"source-manifest.contract_type must be {CONTRACT_TYPE}")

    sources = manifest.get("sources")
    if not isinstance(sources, list) or not sources:
        errors.append("source-manifest.sources must be a non-empty list")
    else:
        source_ids = [
            item.get("source_id")
            for item in sources
            if isinstance(item, dict) and _non_empty(item.get("source_id"))
        ]
        duplicates = sorted(
            item for item, count in Counter(source_ids).items() if count > 1
        )
        if duplicates:
            errors.append(
                "source-manifest.sources contains duplicate source_id values: "
                + ", ".join(duplicates)
            )
        actual_ids = [
            item.get("source_id") if isinstance(item, dict) else None
            for item in sources
        ]
        expected_ids = [item["source_id"] for item in EXPECTED_SOURCE_RECORDS]
        if actual_ids != expected_ids:
            errors.append(
                "source-manifest.sources must contain the exact governed source "
                f"sequence {expected_ids}"
            )
        for index, expected in enumerate(EXPECTED_SOURCE_RECORDS):
            if index >= len(sources):
                break
            actual = sources[index]
            prefix = f"source-manifest.sources[{index}]"
            if not isinstance(actual, dict):
                errors.append(f"{prefix} must be an object")
                continue
            for key, expected_value in expected.items():
                if actual.get(key) != expected_value:
                    errors.append(
                        f"{prefix}.{key} must exactly match the governed "
                        f"{expected['source_id']} source identity"
                    )

    units = manifest.get("source_units")
    if not isinstance(units, list) or not units:
        errors.append("source-manifest.source_units must be a non-empty list")
        return errors
    refs: list[str] = []
    orders: list[int] = []
    for index, unit in enumerate(units):
        prefix = f"source-manifest.source_units[{index}]"
        if not isinstance(unit, dict):
            errors.append(f"{prefix} must be an object")
            continue
        source_ref = unit.get("source_ref")
        if not _non_empty(source_ref):
            errors.append(f"{prefix}.source_ref must be non-empty")
        else:
            refs.append(source_ref)
        if not _non_empty(unit.get("source_heading")):
            errors.append(f"{prefix}.source_heading must be non-empty")
        source_order = unit.get("source_order")
        if (
            isinstance(source_order, bool)
            or not isinstance(source_order, int)
            or source_order < 1
        ):
            errors.append(f"{prefix}.source_order must be a positive integer")
        else:
            orders.append(source_order)
    duplicate_refs = sorted(
        item for item, count in Counter(refs).items() if count > 1
    )
    if duplicate_refs:
        errors.append(
            "source-manifest.source_units contains duplicate source_ref values: "
            + ", ".join(duplicate_refs)
        )
    if orders != list(range(1, len(units) + 1)):
        errors.append(
            "source-manifest.source_units source_order values must be the exact "
            "sequential range from 1 through the source-unit count; "
            f"found {orders}"
        )
    return errors


def _code_from_target_ref(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    match = CODE_RE.search(value)
    return match.group(0).upper() if match else None


def validate_crosswalk(
    crosswalk: Any,
    source_manifest: Any,
    *,
    open_gate_ids: set[str] | None = None,
) -> list[str]:
    """Require exactly one disposition for every source heading."""

    if not isinstance(crosswalk, dict):
        return ["source-to-clause crosswalk must be an object"]
    if not isinstance(source_manifest, dict):
        return ["source manifest must be available before crosswalk validation"]
    errors: list[str] = []
    units = source_manifest.get("source_units")
    entries = crosswalk.get("entries")
    if not isinstance(units, list) or not isinstance(entries, list):
        return ["source units and crosswalk entries must both be lists"]
    entry_refs = [
        item.get("source_ref")
        for item in entries
        if isinstance(item, dict) and _non_empty(item.get("source_ref"))
    ]
    duplicate_refs = sorted(
        item for item, count in Counter(entry_refs).items() if count > 1
    )
    if duplicate_refs:
        errors.append(
            "crosswalk contains duplicate source_ref values: "
            + ", ".join(duplicate_refs)
        )
    source_outline_count = crosswalk.get("source_outline_count")
    if (
        isinstance(source_outline_count, bool)
        or not isinstance(source_outline_count, int)
        or source_outline_count < 1
    ):
        errors.append("crosswalk.source_outline_count must be a positive integer")
    elif source_outline_count != len(units):
        errors.append(
            "crosswalk.source_outline_count must exactly match the source "
            "manifest source-unit count"
        )
    if len(entries) != len(units):
        errors.append(
            "crosswalk.entries must contain exactly one record for every "
            "source-manifest source unit"
        )
    source_orders = [
        item.get("source_order")
        for item in entries
        if isinstance(item, dict)
        and isinstance(item.get("source_order"), int)
        and not isinstance(item.get("source_order"), bool)
    ]
    if isinstance(source_outline_count, int) and source_orders != list(
        range(1, source_outline_count + 1)
    ):
        errors.append(
            "crosswalk entries must cover every sequential source_order from 1 "
            "through source_outline_count"
        )

    for index, entry in enumerate(entries):
        prefix = f"source-to-clause-crosswalk.entries[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{prefix} must be an object")
            continue
        if index < len(units) and isinstance(units[index], dict):
            expected_unit = units[index]
            for key in ("source_ref", "source_heading", "source_order"):
                if entry.get(key) != expected_unit.get(key):
                    errors.append(
                        f"{prefix}.{key} must exactly match "
                        f"source-manifest.source_units[{index}].{key}"
                    )
        coverage = entry.get("coverage_status")
        target_ref = entry.get("target_ref")
        gate_id = entry.get("gate_id")
        if coverage == "mapped" and not _non_empty(target_ref):
            errors.append(f"{prefix}.target_ref is required for mapped content")
        if coverage == "mapped" and gate_id is not None:
            errors.append(f"{prefix}.gate_id must be null for mapped content")
        if coverage == "deferred":
            if not _non_empty(gate_id):
                errors.append(f"{prefix}.gate_id is required for deferred content")
            elif open_gate_ids is not None and gate_id not in open_gate_ids:
                errors.append(f"{prefix}.gate_id must reference an open production gate")
        if coverage == "not_applicable" and entry.get("target_kind") != "not_applicable":
            errors.append(
                f"{prefix}.target_kind must be not_applicable when coverage is not_applicable"
            )
        if entry.get("target_kind") == "clause" and coverage == "mapped":
            code = _code_from_target_ref(target_ref)
            if code not in EXPECTED_CODES:
                errors.append(
                    f"{prefix}.target_ref must identify an expected RLA clause code"
                )
    unmapped = crosswalk.get("unmapped_source_refs")
    if unmapped not in (None, []):
        errors.append("crosswalk.unmapped_source_refs must be empty")
    summary = crosswalk.get("coverage_summary")
    if isinstance(summary, dict):
        actual = Counter(
            entry.get("coverage_status")
            for entry in entries
            if isinstance(entry, dict)
        )
        if summary.get("mapped") != actual["mapped"]:
            errors.append("crosswalk.coverage_summary.mapped does not match entries")
        if summary.get("deferred") != actual["deferred"]:
            errors.append("crosswalk.coverage_summary.deferred does not match entries")
        if summary.get("unmapped") not in (None, 0):
            errors.append("crosswalk.coverage_summary.unmapped must be zero")
    return errors


def _slug(value: str) -> str:
    normalized = value.casefold().replace("\u2019", "")
    normalized = re.sub(r"[^a-z0-9]+", "-", normalized)
    return normalized.strip("-")


def _clause_path_entry(value: Any) -> tuple[str | None, str | None]:
    if isinstance(value, str):
        return _code_from_target_ref(value), value
    if isinstance(value, dict):
        code = value.get("code")
        path = value.get("path")
        return (
            code.upper() if isinstance(code, str) else None,
            path if isinstance(path, str) else None,
        )
    return None, None


def _resolve_reference(root: Path, base: Path, value: str) -> Path | None:
    """Resolve a repository- or manifest-relative reference inside the root."""

    normalized = value.replace("\\", "/")
    candidate = Path(*[part for part in normalized.split("/") if part])
    if candidate.is_absolute():
        return None
    start = root if normalized.startswith("src/") else base
    resolved = (start / candidate).resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError:
        return None
    return resolved


def validate_implementation_bindings(implementation: Any) -> list[str]:
    """Lock critical package and signer-variant references."""

    if not isinstance(implementation, dict):
        return ["contract type implementation must be an object"]
    errors: list[str] = []
    for key, expected in EXPECTED_IMPLEMENTATION_REFS.items():
        if implementation.get(key) != expected:
            errors.append(f"{key} must exactly reference {expected}")

    expected_variants = set(VARIANT_FILE_NAMES)
    for key in (
        "recipient_manifests",
        "ending_text_variants",
        "addendum_b_variants",
    ):
        bindings = implementation.get(key)
        if not isinstance(bindings, dict):
            errors.append(f"{key} must be an object")
            continue
        actual_variants = set(bindings)
        if actual_variants != expected_variants:
            errors.append(
                f"{key} must contain exactly the signer-count variants "
                f"{sorted(expected_variants)}"
            )
    return errors


def _block_has_substantive_content(block: Any) -> bool:
    if not isinstance(block, dict):
        return False
    text = block.get("text")
    return _non_empty(text)


def validate_mapped_clause_content(
    standard_variant: Any,
    source_headings: list[str],
    *,
    name: str,
) -> list[str]:
    """Require every mapped clause heading and at least one body block."""

    if not isinstance(standard_variant, dict):
        return [f"{name} standard variant must be an object"]
    if not source_headings:
        return [f"{name} must have at least one mapped source heading"]
    errors: list[str] = []
    clause_title = standard_variant.get("clause_title")
    blocks = standard_variant.get("blocks")
    if not isinstance(blocks, list):
        return [f"{name}.blocks must be a list"]

    represented_headings: list[str] = (
        [clause_title] if _non_empty(clause_title) else []
    )
    body_by_heading: dict[str, int] = {
        heading: 0 for heading in source_headings
    }
    current_heading = clause_title if _non_empty(clause_title) else None
    for block in blocks:
        if not isinstance(block, dict):
            continue
        style = block.get("style")
        text = block.get("text")
        if (
            isinstance(style, str)
            and style.startswith("Heading ")
            and _non_empty(text)
        ):
            represented_headings.append(text)
            current_heading = text
            continue
        if (
            current_heading in body_by_heading
            and _block_has_substantive_content(block)
        ):
            body_by_heading[current_heading] += 1

    if represented_headings != source_headings:
        errors.append(
            f"{name} mapped heading sequence must exactly match the crosswalk; "
            f"expected {source_headings}, found {represented_headings}"
        )
    for heading in source_headings:
        if body_by_heading.get(heading, 0) < 1:
            errors.append(
                f"{name} mapped source heading {heading!r} must retain "
                "substantive body content"
            )
    return errors


def validate_clause_records(
    root: Path,
    implementation: Any,
    crosswalk: Any,
    clause_types: set[str],
) -> list[str]:
    """Validate the exact 59-record RLA sequence and crosswalk binding."""

    if not isinstance(implementation, dict):
        return ["contract type implementation must be an object"]
    records = implementation.get("clause_records")
    if not isinstance(records, list):
        return ["contract-type-implementation.clause_records must be a list"]
    errors: list[str] = []
    declared: list[tuple[str | None, str | None]] = [
        _clause_path_entry(item) for item in records
    ]
    declared_codes = [code for code, _ in declared if code]
    if declared_codes != EXPECTED_CODES:
        errors.append(
            "clause_records must declare exactly 59 sequential codes "
            "RLA-010 through RLA-590"
        )
    if len(records) != len(EXPECTED_CODES):
        errors.append(
            f"clause_records must contain 59 records; found {len(records)}"
        )
    source_refs_by_code: dict[str, list[str]] = {}
    source_headings_by_code: dict[str, list[str]] = {}
    if isinstance(crosswalk, dict) and isinstance(crosswalk.get("entries"), list):
        for entry in crosswalk["entries"]:
            if (
                isinstance(entry, dict)
                and entry.get("target_kind") == "clause"
                and entry.get("coverage_status") == "mapped"
            ):
                code = _code_from_target_ref(entry.get("target_ref"))
                source_ref = entry.get("source_ref")
                if code and _non_empty(source_ref):
                    source_refs_by_code.setdefault(code, []).append(source_ref)
                    source_heading = entry.get("source_heading")
                    if _non_empty(source_heading):
                        source_headings_by_code.setdefault(code, []).append(
                            source_heading
                        )

    loaded_codes: list[str] = []
    for index, (declared_code, relative) in enumerate(declared):
        prefix = f"contract-type-implementation.clause_records[{index}]"
        if not _non_empty(relative):
            errors.append(f"{prefix} must identify a repository-relative path")
            continue
        path = _resolve_reference(root, root / PACKAGE_REL, relative)
        if path is None:
            errors.append(
                f"{prefix} must resolve within the repository from the implementation manifest"
            )
            continue
        expected_parent = (root / CLAUSE_DIR_REL).resolve()
        try:
            path.resolve().relative_to(expected_parent)
        except ValueError:
            errors.append(f"{prefix} must be under {CLAUSE_DIR_REL.as_posix()}")
            continue
        match = CLAUSE_FILE_RE.fullmatch(path.name)
        if not match:
            errors.append(
                f"{prefix} filename must be rla-NNN-topic.clause.json"
            )
        file_code = match.group("code").upper() if match else None
        if declared_code and file_code and declared_code != file_code:
            errors.append(f"{prefix} code does not match its filename")
        if not path.is_file():
            errors.append(f"{prefix} file does not exist: {relative}")
            continue
        try:
            clause = load_json(path)
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
            errors.append(f"{prefix}: {exc}")
            continue

        name_match = CLAUSE_NAME_RE.fullmatch(str(clause.get("clause_name", "")))
        if not name_match:
            errors.append(
                f"{prefix}.clause_name must use "
                "'RLA-NNN \u2014 Residential Lease \u2014 Topic'"
            )
            continue
        name_code = name_match.group("code")
        topic = name_match.group("topic").strip()
        loaded_codes.append(name_code)
        if file_code and name_code != file_code:
            errors.append(f"{prefix}.clause_name code does not match its filename")
        if declared_code and name_code != declared_code:
            errors.append(f"{prefix}.clause_name code does not match declaration")
        if clause.get("clause_type") not in clause_types:
            errors.append(f"{prefix}.clause_type is not in the governed master list")
        declaration = records[index] if index < len(records) else None
        if isinstance(declaration, dict):
            exact_metadata = {
                "clause_name": clause.get("clause_name"),
                "clause_type": clause.get("clause_type"),
                "library_question": clause.get("library_question"),
            }
            for key, expected in exact_metadata.items():
                if declaration.get(key) != expected:
                    errors.append(
                        f"{prefix}.{key} must exactly match the clause record"
                    )
            if declaration.get("source_sections") != source_refs_by_code.get(
                name_code, []
            ):
                errors.append(
                    f"{prefix}.source_sections must exactly match the ordered "
                    "crosswalk source refs for this clause"
                )

        variants = clause.get("language_variants")
        standards = (
            [
                item
                for item in variants
                if isinstance(item, dict)
                and item.get("variant_kind") == "standard"
            ]
            if isinstance(variants, list)
            else []
        )
        if len(standards) != 1:
            errors.append(f"{prefix} must contain exactly one standard variant")
        else:
            title = standards[0].get("clause_title")
            if isinstance(title, str) and CODE_RE.search(title):
                errors.append(f"{prefix} tenant-facing clause_title must not show an RLA code")
            if match and match.group("slug") != _slug(topic):
                errors.append(
                    f"{prefix} filename topic slug must match the internal Clause Name topic"
                )
            if isinstance(declaration, dict) and declaration.get(
                "clause_title"
            ) != title:
                errors.append(
                    f"{prefix}.clause_title must exactly match the standard "
                    "tenant-facing clause title"
                )
            errors.extend(
                validate_mapped_clause_content(
                    standards[0],
                    source_headings_by_code.get(name_code, []),
                    name=prefix,
                )
            )

    if loaded_codes and loaded_codes != EXPECTED_CODES:
        errors.append("loaded clause records are not the exact RLA-010 through RLA-590 sequence")

    mapped_codes = set(source_refs_by_code)
    missing_mappings = sorted(set(EXPECTED_CODES) - mapped_codes)
    unknown_mappings = sorted(mapped_codes - set(EXPECTED_CODES))
    if missing_mappings:
        errors.append(
            "crosswalk has no mapped source heading for clause codes: "
            + ", ".join(missing_mappings)
        )
    if unknown_mappings:
        errors.append(
            "crosswalk maps unknown clause codes: " + ", ".join(unknown_mappings)
        )
    return errors


def validate_production_gates(implementation: Any) -> tuple[list[str], set[str]]:
    """Return gate errors and the set of open gate IDs."""

    if not isinstance(implementation, dict):
        return ["contract type implementation must be an object"], set()
    gates = implementation.get("production_gates")
    if not isinstance(gates, list):
        return ["production_gates must be a list"], set()
    errors: list[str] = []
    gate_ids: list[str] = []
    open_ids: set[str] = set()
    for index, gate in enumerate(gates):
        prefix = f"production_gates[{index}]"
        if not isinstance(gate, dict):
            errors.append(f"{prefix} must be an object")
            continue
        gate_id = gate.get("gate_id")
        if not _non_empty(gate_id):
            errors.append(f"{prefix}.gate_id must be non-empty")
            continue
        gate_ids.append(gate_id)
        if gate.get("status") == "open":
            open_ids.add(gate_id)
        else:
            errors.append(f"{prefix}.status must remain open for Draft-only release")
        if not _non_empty(gate.get("reason")):
            errors.append(f"{prefix}.reason must explain why the gate is unresolved")
        blocks = gate.get("blocks")
        if not isinstance(blocks, list) or not blocks or not all(
            _non_empty(item) for item in blocks
        ):
            errors.append(f"{prefix}.blocks must identify blocked production actions")
    duplicates = sorted(
        item for item, count in Counter(gate_ids).items() if count > 1
    )
    if duplicates:
        errors.append("duplicate production gate IDs: " + ", ".join(duplicates))
    declared_ids = set(gate_ids)
    missing = sorted(EXPECTED_PRODUCTION_GATE_IDS - declared_ids)
    unexpected = sorted(declared_ids - EXPECTED_PRODUCTION_GATE_IDS)
    if missing:
        errors.append(
            "production_gates is missing exact governed gate IDs: "
            + ", ".join(missing)
        )
    if unexpected:
        errors.append(
            "production_gates contains unexpected gate IDs: "
            + ", ".join(unexpected)
        )
    closed = sorted(EXPECTED_PRODUCTION_GATE_IDS - open_ids)
    if closed:
        errors.append(
            "all exact governed production gates must remain open: "
            + ", ".join(closed)
        )
    return errors, open_ids


def validate_field_map(
    field_map: Any,
    field_registry: Any,
    *,
    open_gate_ids: set[str] | None = None,
) -> list[str]:
    """Validate registry references and fail closed on unverified API names."""

    if not isinstance(field_map, dict):
        return ["document field map must be an object"]
    if not isinstance(field_registry, dict):
        return ["contract field registry must be available"]
    errors: list[str] = []
    registry_fields = field_registry.get("fields")
    by_id = {
        item.get("id"): item
        for item in registry_fields
        if isinstance(item, dict) and _non_empty(item.get("id"))
    } if isinstance(registry_fields, list) else {}
    mappings = field_map.get("mappings")
    if not isinstance(mappings, list):
        return ["document-field-map.mappings must be a list"]
    variables: list[str] = []
    for index, mapping in enumerate(mappings):
        prefix = f"document-field-map.mappings[{index}]"
        if not isinstance(mapping, dict):
            errors.append(f"{prefix} must be an object")
            continue
        source_variable = mapping.get("source_variable")
        if _non_empty(source_variable):
            variables.append(source_variable)
        registry_id = mapping.get("registry_field_id")
        registry_field = by_id.get(registry_id)
        if registry_id is not None and registry_field is None:
            errors.append(
                f"{prefix}.registry_field_id references unknown field {registry_id!r}"
            )
        api_name = mapping.get("zoho_api_name")
        api_status = mapping.get("api_name_status")
        if api_name is not None and api_status != "tenant_verified":
            errors.append(
                f"{prefix}.zoho_api_name must remain null unless api_name_status "
                "is tenant_verified"
            )
        if api_status == "tenant_verified":
            if not _non_empty(api_name):
                errors.append(
                    f"{prefix}.zoho_api_name must be non-empty after tenant verification"
                )
            if isinstance(registry_field, dict):
                zoho = registry_field.get("zoho")
                if not isinstance(zoho, dict) or zoho.get(
                    "type_status"
                ) != "tenant_api_verified":
                    errors.append(
                        f"{prefix} cannot claim tenant verification before the "
                        "canonical field registry is tenant_api_verified"
                    )
                elif api_name != zoho.get("api_name"):
                    errors.append(
                        f"{prefix}.zoho_api_name must match the tenant-verified "
                        "canonical field registry"
                    )
        status = mapping.get("status")
        gate_id = mapping.get("gate_id")
        if status == "mapped" and registry_id is None:
            errors.append(f"{prefix} mapped fields require registry_field_id")
        if status == "mapped" and gate_id is not None:
            errors.append(f"{prefix}.gate_id must be null for mapped fields")
        gated_statuses = {
            "approved_pending_live_metadata",
            "approved_pending_role_and_metadata_verification",
            "deferred",
        }
        if status in gated_statuses:
            if not _non_empty(gate_id):
                errors.append(
                    f"{prefix}.gate_id is required while the field remains gated"
                )
            elif open_gate_ids is not None and gate_id not in open_gate_ids:
                errors.append(f"{prefix}.gate_id must reference an open production gate")
        if status in {
            "approved_pending_live_metadata",
            "approved_pending_role_and_metadata_verification",
        } and registry_id is None:
            errors.append(
                f"{prefix} approved-pending mappings require registry_field_id"
            )

        semantic = " ".join(
            str(mapping.get(key, ""))
            for key in ("source_variable", "business_meaning")
        ).casefold()
        is_rent_or_deposit = (
            "monthly rent" in semantic
            or "base rent" in semantic
            or "security deposit" in semantic
        )
        if registry_id == "contract_amount" and is_rent_or_deposit:
            errors.append(
                f"{prefix} must not map monthly rent or security deposit to contract_amount"
            )
    duplicates = sorted(
        item for item, count in Counter(variables).items() if count > 1
    )
    if duplicates:
        errors.append(
            "document field map contains duplicate source_variable values: "
            + ", ".join(duplicates)
        )
    return errors


def validate_recipient_manifest(
    manifest: Any, *, tenant_count: int, name: str
) -> list[str]:
    """Validate one exact one-, two-, or three-tenant recipient layout."""

    if not isinstance(manifest, dict):
        return [f"{name} must be an object"]
    errors: list[str] = []
    expected_keys = {
        "schema_version",
        "manifest_id",
        "document_type",
        "gh_signs",
        "recipients",
        "landlord_role",
    }
    missing = sorted(expected_keys - set(manifest))
    extra = sorted(set(manifest) - expected_keys)
    if missing:
        errors.append(f"{name} is missing keys: {', '.join(missing)}")
    if extra:
        errors.append(f"{name} has unexpected keys: {', '.join(extra)}")
    if manifest.get("schema_version") != "1.0.0":
        errors.append(f"{name}.schema_version must be 1.0.0")
    if manifest.get("document_type") != CONTRACT_TYPE:
        errors.append(f"{name}.document_type must be {CONTRACT_TYPE}")
    if manifest.get("gh_signs") is not True:
        errors.append(f"{name}.gh_signs must be true")
    recipients = manifest.get("recipients")
    expected_count = tenant_count + 1
    if not isinstance(recipients, list) or len(recipients) != expected_count:
        errors.append(
            f"{name}.recipients must contain {tenant_count} tenant(s) plus GH"
        )
        return errors
    expected_roles = [f"R{number}" for number in range(1, expected_count + 1)]
    actual_roles = [
        item.get("role") if isinstance(item, dict) else None for item in recipients
    ]
    if actual_roles != expected_roles:
        errors.append(f"{name}.recipients roles must be contiguous {expected_roles}")
    for index in range(tenant_count):
        recipient = recipients[index]
        if not isinstance(recipient, dict):
            errors.append(f"{name}.recipients[{index}] must be an object")
            continue
        if recipient.get("business_role") != f"Tenant {index + 1}":
            errors.append(f"{name}.recipients[{index}] must be Tenant {index + 1}")
        if recipient.get("signing_position") != 1:
            errors.append(f"{name}.recipients[{index}] must sign at position 1")
    landlord = recipients[-1]
    if not isinstance(landlord, dict):
        errors.append(f"{name} final recipient must be an object")
    else:
        if landlord.get("business_role") != LANDLORD_BUSINESS_ROLE:
            errors.append(f"{name} final recipient must be the GH landlord role")
        if landlord.get("signing_position") != 2:
            errors.append(f"{name} GH recipient must have final signing position 2")
    expected_landlord_role = f"R{expected_count}"
    if manifest.get("landlord_role") != expected_landlord_role:
        errors.append(f"{name}.landlord_role must be {expected_landlord_role}")
    return errors


def validate_sign_fragment(
    text: Any,
    recipient_manifest: Any,
    *,
    name: str,
    required_tenant_initials: int | None = None,
) -> list[str]:
    """Validate production-safe Sign tags and exact recipient ownership."""

    if not isinstance(text, str):
        return [f"{name} must contain text"]
    if not isinstance(recipient_manifest, dict):
        return [f"{name} requires a recipient manifest"]
    errors: list[str] = []
    raw_tags = TAG_RE.findall(text)
    if text.count("{{") != len(raw_tags) or text.count("}}") != len(raw_tags):
        errors.append(f"{name} contains unbalanced or malformed text-tag braces")
    recipients = recipient_manifest.get("recipients")
    roles = [
        item.get("role")
        for item in recipients
        if isinstance(item, dict) and ROLE_RE.fullmatch(str(item.get("role", "")))
    ] if isinstance(recipients, list) else []
    signatures: Counter[str] = Counter()
    dates: Counter[str] = Counter()
    initials: Counter[str] = Counter()
    for tag in raw_tags:
        simple_match = APPROVED_SIMPLE_ENDING_TAG_RE.fullmatch(tag)
        date_match = CANONICAL_SIGN_DATE_RE.fullmatch(tag)
        if not simple_match and not date_match:
            errors.append(
                f"{name}: unsupported Sign tag {tag!r}; "
                "use only {{S:Rn}}, source-required {{I:Rn}}, or the canonical one-recipient formatted Sign Date"
            )
            continue
        match = simple_match or date_match
        role = match.group("role")
        if role not in roles:
            errors.append(f"{name}: tag {tag} references absent recipient {role}")
        code = simple_match.group("code") if simple_match else "SD"
        if code == "S":
            signatures[role] += 1
        elif code == "SD":
            dates[role] += 1
        elif code == "I":
            initials[role] += 1
    for role in roles:
        if signatures[role] != 1:
            errors.append(f"{name} must contain exactly one signature tag for {role}")
        if dates[role] != 1:
            errors.append(f"{name} must contain exactly one Sign Date tag for {role}")
    if required_tenant_initials is not None:
        landlord_role = recipient_manifest.get("landlord_role")
        tenant_roles = [role for role in roles if role != landlord_role]
        for role in tenant_roles:
            if initials[role] != required_tenant_initials:
                errors.append(
                    f"{name} must contain exactly {required_tenant_initials} "
                    f"initial tag(s) for {role}"
                )
        if isinstance(landlord_role, str) and initials[landlord_role] != 0:
            errors.append(
                f"{name} must not assign tenant initials to {landlord_role}"
            )
    return errors


def validate_ending_text(
    text: Any,
    recipient_manifest: Any,
    *,
    name: str,
) -> list[str]:
    """Validate simple Sign tags and field ownership in one Ending Text fragment."""

    return validate_sign_fragment(text, recipient_manifest, name=name)


def validate_addendum_b(
    text: Any,
    recipient_manifest: Any,
    *,
    name: str,
) -> list[str]:
    """Validate Addendum B content and its two initials per tenant."""

    errors = validate_sign_fragment(
        text,
        recipient_manifest,
        name=name,
        required_tenant_initials=2,
    )
    if not isinstance(text, str):
        return errors
    required_heading = "# Addendum B. HOA and Tenant Handbook Acknowledgment"
    if required_heading not in text.splitlines():
        errors.append(f"{name} must retain the exact Addendum B heading")
    if "Do not preselect HOA applicability or delivery status" not in text:
        errors.append(f"{name} must retain the no-preselection warning")
    return errors


def _binding_path(value: Any) -> str | None:
    if isinstance(value, str):
        return value
    if isinstance(value, dict) and isinstance(value.get("path"), str):
        return value["path"]
    return None


def validate_recipient_and_ending_variants(
    root: Path, implementation: Any
) -> list[str]:
    """Validate governed recipients, Ending Text, and Addendum B variants."""

    if not isinstance(implementation, dict):
        return ["contract type implementation must be an object"]
    errors: list[str] = []
    recipient_bindings = implementation.get("recipient_manifests")
    ending_bindings = implementation.get("ending_text_variants")
    addendum_bindings = implementation.get("addendum_b_variants")
    if not isinstance(recipient_bindings, dict):
        return ["recipient_manifests must be an object"]
    if not isinstance(ending_bindings, dict):
        return ["ending_text_variants must be an object"]
    if not isinstance(addendum_bindings, dict):
        return ["addendum_b_variants must be an object"]

    for variant, (manifest_name, ending_name, tenant_count) in VARIANT_FILE_NAMES.items():
        manifest_rel = (RECIPIENT_DIR_REL / manifest_name).as_posix()
        ending_rel = (PACKAGE_REL / "ending-text" / ending_name).as_posix()
        addendum_rel = (PACKAGE_REL / "addendum-b" / ending_name).as_posix()
        recipient_path_value = _binding_path(recipient_bindings.get(variant))
        ending_path_value = _binding_path(ending_bindings.get(variant))
        addendum_path_value = _binding_path(addendum_bindings.get(variant))
        recipient_reference = (
            _resolve_reference(root, root / PACKAGE_REL, recipient_path_value)
            if isinstance(recipient_path_value, str)
            else None
        )
        ending_reference = (
            _resolve_reference(root, root / PACKAGE_REL, ending_path_value)
            if isinstance(ending_path_value, str)
            else None
        )
        addendum_reference = (
            _resolve_reference(root, root / PACKAGE_REL, addendum_path_value)
            if isinstance(addendum_path_value, str)
            else None
        )
        expected_manifest_path = (root / RECIPIENT_DIR_REL / manifest_name).resolve()
        expected_ending_path = (
            root / PACKAGE_REL / "ending-text" / ending_name
        ).resolve()
        expected_addendum_path = (
            root / PACKAGE_REL / "addendum-b" / ending_name
        ).resolve()
        if (
            recipient_reference is None
            or recipient_reference != expected_manifest_path
        ):
            errors.append(
                f"recipient_manifests.{variant} must reference {manifest_rel}"
            )
        if (
            ending_reference is None
            or ending_reference != expected_ending_path
        ):
            errors.append(
                f"ending_text_variants.{variant} must reference {ending_rel}"
            )
        if (
            addendum_reference is None
            or addendum_reference != expected_addendum_path
        ):
            errors.append(
                f"addendum_b_variants.{variant} must reference {addendum_rel}"
            )

        manifest_path = expected_manifest_path
        try:
            manifest = load_json(manifest_path)
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
            errors.append(f"{manifest_rel}: {exc}")
            continue
        errors.extend(
            validate_recipient_manifest(
                manifest, tenant_count=tenant_count, name=manifest_rel
            )
        )
        ending_path = expected_ending_path
        try:
            text = ending_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"{ending_rel}: {exc}")
        else:
            errors.extend(validate_ending_text(text, manifest, name=ending_rel))

        try:
            addendum_text = expected_addendum_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"{addendum_rel}: {exc}")
        else:
            errors.extend(
                validate_addendum_b(
                    addendum_text,
                    manifest,
                    name=addendum_rel,
                )
            )
    return errors


def _non_empty_string_leaf(value: Any) -> bool:
    if _non_empty(value):
        return True
    if isinstance(value, list):
        return any(_non_empty_string_leaf(item) for item in value)
    if isinstance(value, dict):
        return any(_non_empty_string_leaf(item) for item in value.values())
    return False


def _component_gate_ids(component: dict[str, Any]) -> list[str]:
    gate_ids: list[str] = []
    gate_id = component.get("gate_id")
    if _non_empty(gate_id):
        gate_ids.append(gate_id)
    for key in ("gate_ids", "field_gate_ids"):
        value = component.get(key)
        if isinstance(value, list):
            gate_ids.extend(item for item in value if _non_empty(item))
    return gate_ids


def validate_template_components(
    template_components: Any,
    implementation: Any,
    crosswalk: Any,
    *,
    open_gate_ids: set[str],
) -> list[str]:
    """Validate native template components referenced by the crosswalk."""

    if not isinstance(template_components, dict):
        return ["template-components must be an object"]
    if not isinstance(implementation, dict):
        return ["contract type implementation must be available"]
    if not isinstance(crosswalk, dict):
        return ["source crosswalk must be available"]
    errors = validate_deployment_status(
        template_components.get("deployment_status"),
        path="template-components.deployment_status",
    )
    components = template_components.get("components")
    entries = crosswalk.get("entries")
    if not isinstance(components, list):
        return errors + ["template-components.components must be a list"]
    if not isinstance(entries, list):
        return errors + ["crosswalk entries must be available for components"]

    component_ids: list[str] = []
    by_id: dict[str, dict[str, Any]] = {}
    for index, component in enumerate(components):
        prefix = f"template-components.components[{index}]"
        if not isinstance(component, dict):
            errors.append(f"{prefix} must be an object")
            continue
        component_id = component.get("component_id")
        if not _non_empty(component_id):
            errors.append(f"{prefix}.component_id must be non-empty")
            continue
        component_ids.append(component_id)
        by_id[component_id] = component
        if not _non_empty_string_leaf(
            {
                key: value
                for key, value in component.items()
                if key
                not in {
                    "component_id",
                    "component_type",
                    "gate_id",
                    "gate_ids",
                    "field_gate_ids",
                }
            }
        ):
            errors.append(f"{prefix} must retain substantive template content")
        for gate_id in _component_gate_ids(component):
            if gate_id not in open_gate_ids:
                errors.append(
                    f"{prefix} references production gate {gate_id!r}, "
                    "which must exist and remain open"
                )
    duplicate_ids = sorted(
        item for item, count in Counter(component_ids).items() if count > 1
    )
    if duplicate_ids:
        errors.append(
            "template-components contains duplicate component IDs: "
            + ", ".join(duplicate_ids)
        )

    for key in ("ending_text_variants", "addendum_b_variants"):
        if template_components.get(key) != implementation.get(key):
            errors.append(
                f"template-components.{key} must exactly match the "
                "contract-type implementation"
            )

    title_entries = [
        entry
        for entry in entries
        if isinstance(entry, dict)
        and entry.get("coverage_status") == "mapped"
        and entry.get("target_kind") == "template_title"
    ]
    cover_page = by_id.get("cover-page")
    if len(title_entries) != 1 or not isinstance(cover_page, dict):
        errors.append(
            "mapped template title requires exactly one source entry and "
            "the cover-page component"
        )
    else:
        title_entry = title_entries[0]
        if title_entry.get("target_ref") != "residential-lease-title":
            errors.append(
                "template title target_ref must be residential-lease-title"
            )
        if cover_page.get("title") != title_entry.get("source_heading"):
            errors.append(
                "cover-page.title must exactly match the mapped source title"
            )

    toc_entries = [
        entry
        for entry in entries
        if isinstance(entry, dict)
        and entry.get("coverage_status") == "mapped"
        and entry.get("target_kind") == "template_toc"
    ]
    for entry in toc_entries:
        target_ref = entry.get("target_ref")
        if target_ref not in by_id:
            errors.append(
                f"mapped template TOC component does not exist: {target_ref!r}"
            )

    article_entries = [
        entry
        for entry in entries
        if isinstance(entry, dict)
        and entry.get("coverage_status") == "mapped"
        and entry.get("target_kind") == "template_article_heading"
    ]
    article_component = by_id.get("article-headings")
    if not isinstance(article_component, dict):
        errors.append("article-headings component is required")
    else:
        expected_headings = [
            entry.get("source_heading")
            for entry in entries
            if isinstance(entry, dict)
            and entry.get("coverage_status") == "mapped"
            and re.fullmatch(r"article-(?:[1-9]|1[0-4])", str(entry.get("source_ref")))
        ]
        if article_component.get("headings") != expected_headings:
            errors.append(
                "article-headings.headings must exactly match mapped source "
                "article headings in source order"
            )

    for entry in entries:
        if (
            not isinstance(entry, dict)
            or entry.get("coverage_status") != "mapped"
            or entry.get("target_kind") != "template_component"
        ):
            continue
        target_ref = entry.get("target_ref")
        component = by_id.get(target_ref)
        if not isinstance(component, dict):
            errors.append(
                f"mapped template component does not exist: {target_ref!r}"
            )
            continue
        heading = component.get("heading")
        if _non_empty(heading) and heading != entry.get("source_heading"):
            errors.append(
                f"template component {target_ref!r} heading must exactly "
                "match its mapped source heading"
            )
        if target_ref == "article-13-operative-text":
            article_13 = next(
                (
                    item.get("source_heading")
                    for item in article_entries
                    if item.get("source_ref") == "article-13"
                ),
                None,
            )
            if component.get("article_heading") != article_13:
                errors.append(
                    "article-13-operative-text.article_heading must exactly "
                    "match the Article 13 source heading"
                )
            paragraphs = component.get("paragraphs")
            if not isinstance(paragraphs, list) or not any(
                _non_empty(item) for item in paragraphs
            ):
                errors.append(
                    "article-13-operative-text must retain its operative body"
                )
    return errors


def validate_attachment_requirements(
    attachment_requirements: Any,
    implementation: Any,
    crosswalk: Any,
    *,
    open_gate_ids: set[str],
) -> list[str]:
    """Validate attachment gates and mapped attachment requirement IDs."""

    if not isinstance(attachment_requirements, dict):
        return ["attachment-requirements must be an object"]
    if not isinstance(implementation, dict):
        return ["contract type implementation must be available"]
    if not isinstance(crosswalk, dict):
        return ["source crosswalk must be available"]
    errors = validate_deployment_status(
        attachment_requirements.get("deployment_status"),
        path="attachment-requirements.deployment_status",
    )
    requirements = attachment_requirements.get("requirements")
    entries = crosswalk.get("entries")
    if not isinstance(requirements, list):
        return errors + ["attachment-requirements.requirements must be a list"]
    if not isinstance(entries, list):
        return errors + ["crosswalk entries must be available for attachments"]

    requirement_ids: list[str] = []
    by_id: dict[str, dict[str, Any]] = {}
    for index, requirement in enumerate(requirements):
        prefix = f"attachment-requirements.requirements[{index}]"
        if not isinstance(requirement, dict):
            errors.append(f"{prefix} must be an object")
            continue
        requirement_id = requirement.get("requirement_id")
        if not _non_empty(requirement_id):
            errors.append(f"{prefix}.requirement_id must be non-empty")
            continue
        requirement_ids.append(requirement_id)
        by_id[requirement_id] = requirement
        gate_id = requirement.get("gate_id")
        if not _non_empty(gate_id) or gate_id not in open_gate_ids:
            errors.append(
                f"{prefix}.gate_id must reference an open production gate"
            )
    duplicate_ids = sorted(
        item for item, count in Counter(requirement_ids).items() if count > 1
    )
    if duplicate_ids:
        errors.append(
            "attachment-requirements contains duplicate requirement IDs: "
            + ", ".join(duplicate_ids)
        )

    mapped_ids = [
        entry.get("target_ref")
        for entry in entries
        if isinstance(entry, dict)
        and entry.get("coverage_status") == "mapped"
        and entry.get("target_kind") == "attachment_requirement"
    ]
    for target_ref in mapped_ids:
        if target_ref not in by_id:
            errors.append(
                f"mapped attachment requirement does not exist: {target_ref!r}"
            )

    lead = by_id.get("executed-addendum-a-lead-disclosure")
    if not isinstance(lead, dict):
        errors.append(
            "executed-addendum-a-lead-disclosure requirement is required"
        )
    else:
        if lead.get("blank_form_prohibited") is not True:
            errors.append(
                "executed Addendum A must prohibit embedding a blank form"
            )
        if lead.get("must_remain_attached_to_final_contract") is not True:
            errors.append(
                "executed Addendum A must remain attached to the final contract"
            )

    rules = attachment_requirements.get("addendum_b_rules")
    if not isinstance(rules, dict):
        errors.append("attachment-requirements.addendum_b_rules is required")
    else:
        exact_rules = {
            "default_value": "unknown",
            "preselection_forbidden": True,
            "delivery_status_preselection_forbidden": True,
            "version_and_delivery_date_required_when_delivered": True,
            "signer_count_variant_required": True,
        }
        for key, expected in exact_rules.items():
            if rules.get(key) != expected:
                errors.append(
                    f"attachment-requirements.addendum_b_rules.{key} "
                    f"must exactly equal {expected!r}"
                )

    attachments = implementation.get("attachments")
    if not isinstance(attachments, dict) or attachments.get(
        "attachment_manifest"
    ) != ARTIFACT_FILES["attachment_requirements"]:
        errors.append(
            "contract-type implementation attachments.attachment_manifest "
            "must reference attachment-requirements.json"
        )
    return errors


def validate_repository(
    root: Path,
    *,
    check_markdown: bool = True,
) -> list[str]:
    """Validate the checked-in Residential Lease implementation package."""

    root = root.resolve()
    paths = _paths(root)
    errors: list[str] = []
    loaded: dict[str, dict[str, Any]] = {}
    artifacts: dict[str, dict[str, Any]] = {}
    schemas: dict[str, dict[str, Any]] = {}

    for key, path in paths["schemas"].items():
        try:
            schemas[key] = load_json(path)
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
            errors.append(f"{path.relative_to(root).as_posix()}: {exc}")
    for key, path in paths["data"].items():
        try:
            loaded[key] = load_json(path)
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
            errors.append(f"{path.relative_to(root).as_posix()}: {exc}")
    for key, path in paths["artifacts"].items():
        try:
            artifacts[key] = load_json(path)
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
            errors.append(f"{path.relative_to(root).as_posix()}: {exc}")

    for key in PACKAGE_FILES:
        if key in loaded and key in schemas:
            errors.extend(
                f"{PACKAGE_REL.as_posix()}/{PACKAGE_FILES[key]}: {problem}"
                for problem in validate_schema_reference(loaded[key], key)
            )
            errors.extend(
                f"{PACKAGE_REL.as_posix()}/{PACKAGE_FILES[key]}: {problem}"
                for problem in validate_json_schema(loaded[key], schemas[key])
            )

    source_manifest = loaded.get("source_manifest")
    crosswalk = loaded.get("crosswalk")
    implementation = loaded.get("implementation")
    field_map = loaded.get("field_map")
    template_components = artifacts.get("template_components")
    attachment_requirements = artifacts.get("attachment_requirements")

    if source_manifest is not None:
        errors.extend(validate_source_manifest(source_manifest))
    if implementation is not None:
        errors.extend(validate_implementation_bindings(implementation))
        errors.extend(
            validate_deployment_status(
                implementation.get("deployment_status"),
                path="contract-type-implementation.deployment_status",
            )
        )
        if implementation.get("contract_type") != CONTRACT_TYPE:
            errors.append(
                f"contract-type-implementation.contract_type must be {CONTRACT_TYPE}"
            )

    gate_errors, open_gate_ids = validate_production_gates(implementation)
    errors.extend(gate_errors)
    if crosswalk is not None and source_manifest is not None:
        errors.extend(
            validate_crosswalk(
                crosswalk, source_manifest, open_gate_ids=open_gate_ids
            )
        )

    try:
        standard = load_json(paths["authoring_standard"])
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        errors.append(
            f"{AUTHORING_STANDARD_REL.as_posix()}: {exc}"
        )
        clause_types: set[str] = set()
    else:
        clause_types = set(standard.get("clause_type_master_list", []))
    if implementation is not None and crosswalk is not None:
        errors.extend(
            validate_clause_records(root, implementation, crosswalk, clause_types)
        )
        if template_components is not None:
            errors.extend(
                validate_template_components(
                    template_components,
                    implementation,
                    crosswalk,
                    open_gate_ids=open_gate_ids,
                )
            )
        if attachment_requirements is not None:
            errors.extend(
                validate_attachment_requirements(
                    attachment_requirements,
                    implementation,
                    crosswalk,
                    open_gate_ids=open_gate_ids,
                )
            )

    try:
        registry = load_json(paths["field_registry"])
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        errors.append(f"{FIELD_REGISTRY_REL.as_posix()}: {exc}")
    else:
        if field_map is not None:
            errors.extend(
                validate_field_map(
                    field_map, registry, open_gate_ids=open_gate_ids
                )
            )
    if implementation is not None:
        errors.extend(validate_recipient_and_ending_variants(root, implementation))

    if check_markdown and not errors:
        try:
            actual_markdown = paths["readable_clause_library"].read_text(
                encoding="utf-8"
            )
        except (OSError, UnicodeError) as exc:
            errors.append(
                f"{READABLE_CLAUSE_LIBRARY_REL.as_posix()}: {exc}"
            )
        else:
            errors.extend(
                readable_clause_library_drift_errors(root, actual_markdown)
            )
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=repository_root(),
        help="repository root (defaults to this script's repository)",
    )
    parser.add_argument(
        "--write-markdown",
        action="store_true",
        help="regenerate the readable clause library from validated JSON",
    )
    args = parser.parse_args(argv)
    root = args.root.resolve()
    errors = validate_repository(
        root,
        check_markdown=not args.write_markdown,
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    if args.write_markdown:
        write_readable_clause_library(root)
    print(
        "Validated the Draft-only Residential Lease package: "
        "59 sequential clauses, complete source coverage, governed fields, "
        "native components and attachments, exact open production gates, "
        "governed Ending Text/Addendum B signer variants, and the generated "
        "readable clause library."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
