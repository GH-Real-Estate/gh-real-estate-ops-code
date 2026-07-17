#!/usr/bin/env python3
"""Validate GH Real Estate's Zoho Contracts and Zoho Sign authoring policies.

The module intentionally uses only Python's standard library so the same fail-closed
checks run locally and in GitHub Actions without dependency installation.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse


CLAUSE_TYPES = [
    "Agreement Structure",
    "Parties, Premises and Term",
    "Rent, Fees and Payment",
    "Deposits and Prepaid Amounts",
    "Utilities and Services",
    "Use, Occupancy and Conduct",
    "Maintenance, Repairs and Condition",
    "Access and Inspection",
    "Animals and Accommodations",
    "Ancillary Storage",
    "Insurance, Risk and Liability",
    "Default, Remedies and Termination",
    "Personal Property and Abandonment",
    "Notices and Communications",
    "Compliance and Disclosures",
    "General Provisions",
]

CLAUSE_STYLES = [
    "Heading 1",
    "Heading 2",
    "Heading 3",
    "Heading 4",
    "Heading 5",
    "Normal",
]

CLAUSE_LANGUAGE_STYLES = ["Heading 3", "Heading 4", "Heading 5", "Normal"]

EXPECTED_SEMANTIC_STYLE_MAP = [
    {
        "semantic_role": "main_document_title",
        "zoho_writer_style": "Title",
        "clause_language_block_allowed": False,
        "notes": "Apply only in the contract template outside clause-library records.",
    },
    {
        "semantic_role": "article_heading",
        "zoho_writer_style": "Heading 1",
        "clause_language_block_allowed": False,
        "notes": "Top-level article or major section heading managed in the contract template, outside clause language.",
    },
    {
        "semantic_role": "clause_title",
        "zoho_writer_style": "Heading 2",
        "clause_language_block_allowed": False,
        "notes": "Stored as clause_title metadata for each standard or alternate language variant and rendered separately from substantive language blocks.",
    },
    {
        "semantic_role": "subsection_heading",
        "zoho_writer_style": "Heading 3",
        "clause_language_block_allowed": True,
        "notes": "First-level subsection within a clause.",
    },
    {
        "semantic_role": "nested_heading_level_1",
        "zoho_writer_style": "Heading 4",
        "clause_language_block_allowed": True,
        "notes": "Nested heading below a subsection.",
    },
    {
        "semantic_role": "nested_heading_level_2",
        "zoho_writer_style": "Heading 5",
        "clause_language_block_allowed": True,
        "notes": "Deepest permitted heading; do not create Heading 6.",
    },
    {
        "semantic_role": "body_text",
        "zoho_writer_style": "Normal",
        "clause_language_block_allowed": True,
        "notes": "Paragraphs, list text, and other substantive clause language.",
    },
]

EXPECTED_TYPOGRAPHY = {
    "scope": "Zoho Contracts templates and clause content only",
    "body_text": {
        "font_family": "Inter",
        "font_size_pt": 11,
        "font_weight": "Regular",
        "color_hex": "#000000",
        "alignment": "Left",
    },
    "main_title": {
        "font_family": "Inter",
        "font_size_pt": 18,
        "font_weight": "Bold",
        "color_hex": "#000000",
        "alignment": "Center",
        "zoho_writer_style": "Title",
    },
    "article_heading": {
        "font_family": "Inter",
        "font_size_pt": 12,
        "font_weight": "Bold",
        "color_hex": "#1F4E79",
        "alignment": "Left",
        "zoho_writer_style": "Heading 1",
    },
    "subheadings": {
        "styles": ["Heading 2", "Heading 3", "Heading 4", "Heading 5"],
        "font_family": "Inter",
        "font_size_pt": 11,
        "font_weight": "Bold",
        "color_hex": "#000000",
        "alignment": "Left",
    },
    "tables_and_forms": {
        "font_family": "Inter",
        "font_size_pt": 10,
        "font_weight": "Regular",
        "color_hex": "#000000",
        "alignment": "Left",
    },
    "header_and_footer": {
        "font_family": "Inter",
        "font_size_pt": 8.5,
        "allowed_font_size_pt": {"minimum": 8, "maximum": 8.5},
        "font_weight": "Regular",
        "color_hex": "#666666",
    },
    "line_spacing": 1.15,
    "paragraph_spacing_after_pt": 6,
    "allowed_paragraph_spacing_after_pt": {"minimum": 4, "maximum": 6},
    "page": {
        "size": "US Letter",
        "width_in": 8.5,
        "height_in": 11,
        "margins_in": {"top": 0.75, "right": 0.75, "bottom": 0.75, "left": 0.75},
    },
    "paragraph_alignment": {
        "allowed": ["Left"],
        "fully_justified_allowed": False,
    },
}

SIMPLE_TAG_CODES = [
    "S",
    "I",
    "D",
    "N",
    "FN",
    "LN",
    "E",
    "CO",
    "JT",
    "TF",
    "A",
    "ST",
]

CANONICAL_SIGN_DATE_FORMAT = "MM/dd/yyyy hh:mm a z"
CANONICAL_SIGN_DATE_R1 = (
    '{{SD:R1:(dateformat="MM/dd/yyyy hh:mm a z")}}'
)

PRODUCTION_TAG_LOCKS = [
    ("S", "Signature", "{{S:R1}}", "compatibility_only"),
    ("I", "Initial", "{{I:R1}}", "compatibility_only"),
    ("SD", "Sign Date", CANONICAL_SIGN_DATE_R1, "forbidden"),
    ("D", "Date", "{{D:R1}}", "forbidden"),
    ("N", "Full Name", "{{N:R1}}", "forbidden"),
    ("FN", "First Name", "{{FN:R1}}", "forbidden"),
    ("LN", "Last Name", "{{LN:R1}}", "forbidden"),
    ("E", "Email", "{{E:R1}}", "forbidden"),
    ("CO", "Company", "{{CO:R1}}", "forbidden"),
    ("JT", "Job Title", "{{JT:R1}}", "forbidden"),
    ("TF", "Text", "{{TF:R1*}}", "meaningful_optional"),
    ("[]", "Checkbox", "{{[]}}", "editor_or_smoke_test_for_required"),
    ("A", "Attachment", "{{A:R1}}", "forbidden"),
    ("ST", "Stamp", "{{ST:R1}}", "forbidden"),
]

OFFICIAL_SIGN_FIELDS = [
    "Signature",
    "Initial",
    "Stamp",
    "Image",
    "Company",
    "Full Name",
    "Email",
    "Sign Date",
    "Date",
    "Text",
    "Job Title",
    "Checkbox",
    "Dropdown",
    "Radio",
    "Payment",
    "Attachment",
    "Formula",
    "Checkbox Group",
    "Split Text",
]

UNVERIFIED_COMPLEX_FIELDS = [
    "Dropdown",
    "Radio",
    "Checkbox Group",
]

NO_PUBLISHED_TAG_FIELDS = {"Image", "Payment", "Formula", "Split Text"}
INVENTED_TAG_NAMES = {"Phone", "Image", "Payment", "Formula", "SplitText"}
OFFICIAL_FIELD_SYNTAX = {
    "Signature": "{{S:R1}}",
    "Initial": "{{I:R1}}",
    "Stamp": "{{ST:R1}}",
    "Image": None,
    "Company": "{{CO:R1}}",
    "Full Name": "{{N:R1}}",
    "Email": "{{E:R1}}",
    "Sign Date": CANONICAL_SIGN_DATE_R1,
    "Date": "{{D:R1}}",
    "Text": "{{TF:R1*}}",
    "Job Title": "{{JT:R1}}",
    "Checkbox": "{{[]}}",
    "Dropdown": '{{DD:R1:Text(options="option 1, option 2, option 3")}}',
    "Radio": "{{(Radio1):Recipient1:RadioA}}",
    "Payment": None,
    "Attachment": "{{A:R1}}",
    "Formula": None,
    "Checkbox Group": "{{CBG:Recipient1:checkboxgroup-1[checkbox1]}}",
    "Split Text": None,
}
PUBLISHED_LONG_SHORT_EXAMPLES = [
    "{{Signature}}",
    "{{S}}",
    "{{Company:Recipient2}}",
    "{{CO:R2}}",
    "{{Textfield:Recipient1*}}",
    "{{TF:R1*}}",
    "{{Jobtitle}}",
    "{{JT}}",
    "{{Initial}}",
    "{{I}}",
    "{{Signdate}}",
    "{{SD}}",
    "{{Checkbox}}",
    "{{[]}}",
    "{{Fullname}}",
    "{{N}}",
    "{{Customdate:Recipient1}}",
    "{{D:R1}}",
    "{{Firstname}}",
    "{{FN}}",
    "{{Lastname}}",
    "{{LN}}",
    "{{Attachment}}",
    "{{A}}",
    "{{Stamp}}",
    "{{ST}}",
    "{{Email}}",
    "{{E}}",
]
ROLE_RE = re.compile(r"^R(?:[1-9]|1[0-9]|2[0-5])$")
SIMPLE_TAG_RE = re.compile(
    r"^\{\{(?P<code>[A-Za-z]+):(?P<role>R\d{1,2})(?P<star>\*)?\}\}$"
)
FORMATTED_SD_RE = re.compile(
    r'^\{\{SD:(?P<role>R\d{1,2}):\(dateformat="(?P<format>[^"\r\n]+)"\)\}\}$'
)
DROPDOWN_RE = re.compile(
    r'^\{\{DD:(?P<role>R\d{1,2}):Text\(options="(?P<options>[^"\r\n]+)"\)\}\}$'
)
RADIO_RE = re.compile(
    r"^\{\{\((?P<option>[^():{}\r\n]+)\):Recipient(?P<number>\d{1,2}):(?P<group>[^:{}\r\n]+)\}\}$"
)
CHECKBOX_GROUP_RE = re.compile(
    r"^\{\{CBG:Recipient(?P<number>\d{1,2}):(?P<group>[^\[\]{}:\r\n]+)\[(?P<option>[^\[\]{}\r\n]+)\]\}\}$"
)
TAG_RE = re.compile(r"\{\{.*?\}\}", re.DOTALL)
NON_ASCII_DELIMITERS = set("“”‘’｛｝")


def repository_root() -> Path:
    """Return the repository root relative to this checked-in script."""

    return Path(__file__).resolve().parents[3]


def _paths(root: Path) -> dict[str, Path]:
    return {
        "standard": root
        / "src/zoho-contracts/standards/contract-authoring-standard.json",
        "standard_markdown": root
        / "src/zoho-contracts/standards/contract-authoring-standard.md",
        "clause_schema": root / "src/zoho-contracts/schemas/clause-definition.schema.json",
        "clause_template": root
        / "src/zoho-contracts/templates/clause-definition.template.json",
        "sign_registry": root
        / "src/zoho-sign/field-tags/zoho-contracts-text-tag-registry.json",
        "sign_markdown": root
        / "src/zoho-sign/field-tags/zoho-contracts-text-tag-registry.md",
    }


def load_json(path: Path) -> dict[str, Any]:
    """Load a JSON object and produce a useful error for non-object roots."""

    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _question(value: Any) -> bool:
    return _non_empty_string(value) and value.rstrip().endswith("?")


def _is_official_zoho_url(value: Any) -> bool:
    if not _non_empty_string(value):
        return False
    parsed = urlparse(value)
    host = (parsed.hostname or "").lower()
    return parsed.scheme == "https" and (host == "zoho.com" or host.endswith(".zoho.com"))


def _validate_sources(sources: Any, path: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(sources, list) or not sources:
        return [f"{path} must be a non-empty list"]
    for index, source in enumerate(sources):
        prefix = f"{path}[{index}]"
        if not isinstance(source, dict):
            errors.append(f"{prefix} must be an object")
            continue
        errors.extend(_exact_keys(source, {"title", "url"}, prefix))
        if not _non_empty_string(source.get("title")):
            errors.append(f"{prefix}.title must be non-empty")
        if not _is_official_zoho_url(source.get("url")):
            errors.append(f"{prefix}.url must be an official HTTPS Zoho URL")
    return errors


def _exact_keys(value: Any, expected: set[str], path: str) -> list[str]:
    if not isinstance(value, dict):
        return [f"{path} must be an object"]
    actual = set(value)
    errors: list[str] = []
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if missing:
        errors.append(f"{path} is missing keys: {', '.join(missing)}")
    if extra:
        errors.append(f"{path} has unexpected keys: {', '.join(extra)}")
    return errors


def _result(
    tag: str,
    classification: str,
    *,
    code: str | None = None,
    recipient_role: str | None = None,
    reason: str = "",
    warnings: Iterable[str] = (),
) -> dict[str, Any]:
    return {
        "tag": tag,
        "classification": classification,
        "code": code,
        "recipient_role": recipient_role,
        "reason": reason,
        "warnings": list(warnings),
    }


def _looks_like_multi_recipient_sign_date(tag: str) -> bool:
    """Return true when a Sign Date tag's recipient slot contains 2+ indexes.

    Zoho may permissively create a field from some of these strings while
    assigning it only to the first parsed recipient. Treat that conversion as
    a false positive and reject the source with an actionable message.
    """

    lowered = tag.lower()
    if not (lowered.startswith("{{sd:") or lowered.startswith("{{signdate:")):
        return False
    parts = tag.split(":", 2)
    return len(parts) >= 2 and len(re.findall(r"\d{1,2}", parts[1])) > 1


def classify_tag(tag: str, registry: dict[str, Any] | None = None) -> dict[str, Any]:
    """Classify one exact Zoho Sign tag using the fail-closed Contracts policy.

    ``production_safe`` means the governed tag can pass the Contracts pipeline.
    ``official_pipeline_unverified`` means Zoho publishes the grammar, but GH Real
    Estate still blocks it pending an isolated Contracts-to-Sign smoke test.
    Everything else is ``invalid``.
    """

    if not isinstance(tag, str) or not tag:
        return _result(str(tag), "invalid", reason="tag must be a non-empty string")
    if "\r" in tag or "\n" in tag:
        return _result(tag, "invalid", reason="tag must remain on one physical line")
    if any(character in NON_ASCII_DELIMITERS for character in tag) or any(
        ord(character) > 127 for character in tag
    ):
        return _result(
            tag,
            "invalid",
            reason="tag must use ASCII braces, straight quotes, and ASCII content",
        )

    if _looks_like_multi_recipient_sign_date(tag):
        return _result(
            tag,
            "invalid",
            code="SD",
            reason=(
                "multi-recipient Sign Date fields are invalid: observed Zoho "
                "conversion may create a field but assigns it only to the first "
                "parsed recipient; use one separate canonical tag per recipient"
            ),
        )

    if tag == "{{[]}}":
        return _result(
            tag,
            "production_safe",
            code="[]",
            reason="exact published checkbox shorthand; requires an explicit sole R1 recipient manifest",
            warnings=(
                "checkbox shorthand has no recipient token and is permitted only for an explicitly manifested single R1 signer",
            ),
        )

    match = FORMATTED_SD_RE.fullmatch(tag)
    if match:
        role = match.group("role")
        if not ROLE_RE.fullmatch(role):
            return _result(
                tag,
                "invalid",
                code="SD",
                recipient_role=role,
                reason="recipient role must be R1 through R25",
            )
        if match.group("format") != CANONICAL_SIGN_DATE_FORMAT:
            return _result(
                tag,
                "invalid",
                code="SD",
                recipient_role=role,
                reason=(
                    "GHRE permits only the canonical Sign Date format "
                    f"{CANONICAL_SIGN_DATE_FORMAT!r}"
                ),
            )
        return _result(
            tag,
            "production_safe",
            code="SD",
            recipient_role=role,
            reason="user-confirmed canonical GHRE formatted Sign Date tag",
            warnings=(
                "verify the populated timestamp after completing the signing flow before publishing a live template",
            ),
        )

    match = DROPDOWN_RE.fullmatch(tag)
    if match:
        role = match.group("role")
        if not ROLE_RE.fullmatch(role):
            return _result(
                tag,
                "invalid",
                code="DD",
                recipient_role=role,
                reason="recipient role must be R1 through R25",
            )
        options = [item.strip() for item in match.group("options").split(",")]
        if len(options) < 2 or any(not option for option in options):
            return _result(
                tag,
                "invalid",
                code="DD",
                recipient_role=role,
                reason="dropdown tag must declare at least two non-empty options",
            )
        return _result(
            tag,
            "official_pipeline_unverified",
            code="DD",
            recipient_role=role,
            reason="Dropdown grammar is official but blocked pending a Contracts pipeline smoke test",
        )

    match = RADIO_RE.fullmatch(tag)
    if match:
        role = f"R{match.group('number')}"
        if not ROLE_RE.fullmatch(role):
            return _result(
                tag,
                "invalid",
                code="Radio",
                recipient_role=role,
                reason="recipient role must be Recipient1 through Recipient25",
            )
        return _result(
            tag,
            "official_pipeline_unverified",
            code="Radio",
            recipient_role=role,
            reason="Radio grammar is official but blocked pending a Contracts pipeline smoke test",
        )

    match = CHECKBOX_GROUP_RE.fullmatch(tag)
    if match:
        role = f"R{match.group('number')}"
        if not ROLE_RE.fullmatch(role):
            return _result(
                tag,
                "invalid",
                code="CBG",
                recipient_role=role,
                reason="recipient role must be Recipient1 through Recipient25",
            )
        return _result(
            tag,
            "official_pipeline_unverified",
            code="CBG",
            recipient_role=role,
            reason="Checkbox Group grammar is official but blocked pending a Contracts pipeline smoke test",
        )

    match = SIMPLE_TAG_RE.fullmatch(tag)
    if match:
        code = match.group("code")
        role = match.group("role")
        star = bool(match.group("star"))
        if not ROLE_RE.fullmatch(role):
            return _result(
                tag,
                "invalid",
                code=code,
                recipient_role=role,
                reason="recipient role must be R1 through R25",
            )
        if code not in SIMPLE_TAG_CODES:
            if code == "SD":
                reason = (
                    "GHRE requires the canonical formatted Sign Date tag "
                    '{{SD:Rn:(dateformat="MM/dd/yyyy hh:mm a z")}}'
                )
            elif code in INVENTED_TAG_NAMES:
                reason = f"{code} has no published dedicated Zoho Sign text-tag grammar"
            else:
                reason = f"unknown or unapproved Zoho Sign text-tag code: {code}"
            return _result(
                tag,
                "invalid",
                code=code,
                recipient_role=role,
                reason=reason,
            )
        warnings: list[str] = []
        if star and code in {"S", "I"}:
            warnings.append(
                "redundant asterisk accepted for compatibility; mandatory semantics apply only to text and checkbox fields"
            )
        elif star and code != "TF":
            return _result(
                tag,
                "invalid",
                code=code,
                recipient_role=role,
                reason="asterisk is permitted on TF, with S/I accepted for compatibility; the exact checkbox shorthand has no role-specific starred form",
            )
        return _result(
            tag,
            "production_safe",
            code=code,
            recipient_role=role,
            reason="approved simple short tag",
            warnings=warnings,
        )

    return _result(
        tag,
        "invalid",
        reason="tag does not match an approved simple tag or documented quarantined grammar",
    )


def _manifest_roles(recipient_manifest: Any) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    roles: list[str] = []
    if not isinstance(recipient_manifest, list) or not recipient_manifest:
        return [], ["recipient-role manifest is required and must be non-empty"]
    for index, item in enumerate(recipient_manifest):
        role = item.get("role") if isinstance(item, dict) else item
        if not isinstance(role, str) or not ROLE_RE.fullmatch(role):
            errors.append(f"recipient manifest item {index} must declare role R1 through R25")
            continue
        if role in roles:
            errors.append(f"recipient manifest contains duplicate role {role}")
        roles.append(role)
    return roles, errors


def scan_text_tags(
    text: str,
    recipient_manifest: list[Any] | None,
    *,
    page_count: int | None = None,
    production: bool = True,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Scan contract text and enforce tag syntax, roles, and production gates."""

    errors: list[str] = []
    warnings: list[str] = []
    classified: list[dict[str, Any]] = []
    if not isinstance(text, str):
        return {"errors": ["text must be a string"], "warnings": [], "tags": []}
    if page_count is not None and (
        isinstance(page_count, bool) or not isinstance(page_count, int) or page_count < 1
    ):
        errors.append("page_count must be a positive integer when supplied")
    elif page_count is not None and page_count > 74:
        errors.append("text tags are limited to documents of 74 pages or fewer")

    raw_tags = TAG_RE.findall(text)
    if text.count("{{") != len(raw_tags) or text.count("}}") != len(raw_tags):
        errors.append("unbalanced or malformed text-tag braces detected")

    roles, manifest_errors = _manifest_roles(recipient_manifest)
    if raw_tags:
        errors.extend(manifest_errors)
    referenced_roles: set[str] = set()
    for raw_tag in raw_tags:
        result = classify_tag(raw_tag, registry)
        if raw_tag == "{{[]}}":
            if roles == ["R1"]:
                result = dict(result)
                result["recipient_role"] = "R1"
            else:
                errors.append(
                    "{{[]}}: exact checkbox shorthand is allowed only when the explicit recipient-role manifest contains sole signer R1"
                )
        classified.append(result)
        role = result.get("recipient_role")
        if isinstance(role, str) and ROLE_RE.fullmatch(role):
            referenced_roles.add(role)
        warnings.extend(result.get("warnings", []))
        if result["classification"] == "invalid":
            errors.append(f"{raw_tag}: {result['reason']}")
        elif result["classification"] == "official_pipeline_unverified":
            message = f"{raw_tag}: {result['reason']}"
            if production:
                errors.append(message)
            else:
                warnings.append(message)

    for role in sorted(referenced_roles - set(roles)):
        errors.append(f"tag recipient {role} is absent from the recipient-role manifest")
    for role in roles:
        if role not in referenced_roles:
            errors.append(f"recipient-role manifest signer {role} has no assigned field")

    return {"errors": errors, "warnings": warnings, "tags": classified}


def validate_clause_definition(
    clause: Any,
    standard: dict[str, Any] | None = None,
) -> list[str]:
    """Validate one clause definition beyond what JSON Schema can express."""

    errors: list[str] = []
    if not isinstance(clause, dict):
        return ["clause definition must be an object"]
    allowed_keys = {
        "$schema",
        "schema_version",
        "clause_type",
        "clause_name",
        "zoho_api_name",
        "zoho_api_name_status",
        "library_question",
        "contract_type_question_overrides",
        "sign_recipient_manifest",
        "language_variants",
    }
    required_keys = {
        "schema_version",
        "clause_type",
        "clause_name",
        "zoho_api_name",
        "zoho_api_name_status",
        "library_question",
        "contract_type_question_overrides",
        "language_variants",
    }
    for key in sorted(required_keys - clause.keys()):
        errors.append(f"missing required clause property: {key}")
    for key in sorted(clause.keys() - allowed_keys):
        errors.append(f"unknown clause property: {key}")
    if clause.get("schema_version") != "1.0.0":
        errors.append("schema_version must be 1.0.0")
    types = (
        standard.get("clause_type_master_list", CLAUSE_TYPES)
        if isinstance(standard, dict)
        else CLAUSE_TYPES
    )
    if clause.get("clause_type") not in types:
        errors.append("clause_type must be selected from the governed master list")
    if not _non_empty_string(clause.get("clause_name")):
        errors.append("clause_name must be a non-empty string")

    api_name = clause.get("zoho_api_name")
    api_status = clause.get("zoho_api_name_status")
    if api_name is None:
        if api_status != "tenant_verification_required":
            errors.append(
                "null zoho_api_name requires tenant_verification_required status"
            )
    elif _non_empty_string(api_name):
        if api_status != "tenant_verified":
            errors.append("non-null zoho_api_name requires tenant_verified status")
    else:
        errors.append("zoho_api_name must be null or a non-empty string")

    if not _question(clause.get("library_question")):
        errors.append("library_question must be non-empty and end with a question mark")
    overrides = clause.get("contract_type_question_overrides")
    if not isinstance(overrides, list):
        errors.append("contract_type_question_overrides must be a list")
    else:
        seen_contract_types: set[str] = set()
        for index, override in enumerate(overrides):
            prefix = f"contract_type_question_overrides[{index}]"
            if not isinstance(override, dict):
                errors.append(f"{prefix} must be an object")
                continue
            if set(override) != {"contract_type", "question"}:
                errors.append(f"{prefix} must contain only contract_type and question")
            contract_type = override.get("contract_type")
            if not _non_empty_string(contract_type):
                errors.append(f"{prefix}.contract_type must be non-empty")
            elif contract_type in seen_contract_types:
                errors.append(f"duplicate contract type question override: {contract_type}")
            else:
                seen_contract_types.add(contract_type)
            if not _question(override.get("question")):
                errors.append(f"{prefix}.question must be non-empty and end with ?")

    variants = clause.get("language_variants")
    if not isinstance(variants, list) or not variants:
        errors.append("language_variants must contain at least one variant")
        return errors
    standard_count = 0
    variant_ids: set[str] = set()
    combined_text: list[str] = []
    for index, variant in enumerate(variants):
        prefix = f"language_variants[{index}]"
        if not isinstance(variant, dict):
            errors.append(f"{prefix} must be an object")
            continue
        expected_variant_keys = {
            "variant_id",
            "variant_kind",
            "clause_title",
            "clause_title_style",
            "blocks",
        }
        if set(variant) != expected_variant_keys:
            errors.append(f"{prefix} must contain exactly {sorted(expected_variant_keys)}")
        variant_id = variant.get("variant_id")
        if not _non_empty_string(variant_id) or not re.fullmatch(
            r"[a-z0-9]+(?:-[a-z0-9]+)*", str(variant_id)
        ):
            errors.append(f"{prefix}.variant_id must be lower kebab-case")
        elif variant_id in variant_ids:
            errors.append(f"duplicate variant_id: {variant_id}")
        else:
            variant_ids.add(variant_id)
        kind = variant.get("variant_kind")
        if kind == "standard":
            standard_count += 1
        elif kind != "alternate":
            errors.append(f"{prefix}.variant_kind must be standard or alternate")
        title = variant.get("clause_title")
        if not _non_empty_string(title):
            errors.append(f"{prefix}.clause_title must be non-empty")
        if variant.get("clause_title_style") != "Heading 2":
            errors.append(f"{prefix}.clause_title_style must be Heading 2")
        blocks = variant.get("blocks")
        if not isinstance(blocks, list) or not blocks:
            errors.append(f"{prefix}.blocks must contain substantive clause language")
            continue
        heading_depth = 2
        for block_index, block in enumerate(blocks):
            block_prefix = f"{prefix}.blocks[{block_index}]"
            if not isinstance(block, dict):
                errors.append(f"{block_prefix} must be an object")
                continue
            if set(block) != {"style", "text"}:
                errors.append(f"{block_prefix} must contain only style and text")
            style = block.get("style")
            if style not in CLAUSE_LANGUAGE_STYLES:
                errors.append(
                    f"{block_prefix}.style must be Heading 3-5 or Normal; article Heading 1 and clause-title Heading 2 are stored outside substantive language blocks"
                )
            elif style.startswith("Heading "):
                new_depth = int(style.removeprefix("Heading "))
                if new_depth > heading_depth + 1:
                    errors.append(
                        f"{block_prefix}.style skips heading depth from Heading {heading_depth} to Heading {new_depth}"
                    )
                heading_depth = new_depth
            if not _non_empty_string(block.get("text")):
                errors.append(f"{block_prefix}.text must be non-empty")
            else:
                if _non_empty_string(title) and block["text"].strip() == title.strip():
                    errors.append(
                        f"{block_prefix}.text duplicates clause_title; render title metadata separately"
                    )
                combined_text.append(block["text"])
    if standard_count != 1:
        errors.append("language_variants must contain exactly one standard variant")

    text = "\n".join(combined_text)
    if "{{" in text or "}}" in text:
        scan = scan_text_tags(text, clause.get("sign_recipient_manifest"))
        errors.extend(f"sign tag: {message}" for message in scan["errors"])
    return errors


def validate_sign_registry(registry: Any) -> list[str]:
    """Validate the canonical Zoho Sign field and text-tag registry."""

    errors: list[str] = []
    if not isinstance(registry, dict):
        return ["Sign registry must be an object"]
    errors.extend(
        _exact_keys(
            registry,
            {
                "schema_version",
                "registry_id",
                "title",
                "effective_date",
                "scope",
                "governance_status",
                "official_sources",
                "recipient_role_policy",
                "document_safety_policy",
                "mandatory_marker_policy",
                "canonical_sign_date_policy",
                "evidence_policy",
                "observed_pipeline_constraints",
                "compatibility_aliases",
                "production_safe_simple_tags",
                "official_but_contracts_pipeline_unverified",
                "official_but_ghre_blocked_features",
                "official_document_field_catalog",
                "unsupported_or_invented_text_tags",
            },
            "Sign registry",
        )
    )
    if registry.get("schema_version") != "1.2.0":
        errors.append("Sign registry schema_version must be 1.2.0")
    if registry.get("effective_date") != "2026-07-17":
        errors.append("Sign registry effective_date must be 2026-07-17")
    errors.extend(_validate_sources(registry.get("official_sources"), "official_sources"))
    source_urls = {
        source.get("url")
        for source in registry.get("official_sources", [])
        if isinstance(source, dict)
    }
    if (
        "https://help.zoho.com/portal/en/kb/zoho-sign/user-guide/sending-a-document/articles/send-for-signatures"
        not in source_urls
    ):
        errors.append("official sources must include Zoho Sign Send Documents for Signatures")
    roles = registry.get("recipient_role_policy", {})
    errors.extend(
        _exact_keys(
            roles,
            {
                "canonical_pattern",
                "minimum",
                "maximum",
                "manifest_required",
                "manifest_rule",
                "implicit_first_recipient_allowed",
            },
            "recipient_role_policy",
        )
    )
    if roles.get("minimum") != 1 or roles.get("maximum") != 25:
        errors.append("recipient roles must be limited to R1 through R25")
    if roles.get("manifest_required") is not True:
        errors.append("recipient-role manifest must be required")
    if roles.get("implicit_first_recipient_allowed") is not False:
        errors.append("implicit first-recipient assignment must be disabled")
    safety = registry.get("document_safety_policy", {})
    errors.extend(
        _exact_keys(
            safety,
            {
                "official_limit",
                "maximum_pages",
                "single_physical_line_required",
                "ascii_braces_and_quotes_required",
                "trailing_width_spaces_allowed",
                "rule",
            },
            "document_safety_policy",
        )
    )
    if safety.get("maximum_pages") != 74:
        errors.append("document text-tag safety maximum must be 74 pages")
    if safety.get("single_physical_line_required") is not True:
        errors.append("single physical line policy must be enabled")
    if safety.get("ascii_braces_and_quotes_required") is not True:
        errors.append("ASCII delimiter policy must be enabled")
    marker = registry.get("mandatory_marker_policy", {})
    errors.extend(
        _exact_keys(
            marker,
            {"marker", "meaningful_for", "compatibility_accepted_for", "rule"},
            "mandatory_marker_policy",
        )
    )
    if marker.get("meaningful_for") != ["TF", "checkbox"]:
        errors.append("asterisk must be meaningful only for TF and checkbox")
    if marker.get("compatibility_accepted_for") != ["S", "I"]:
        errors.append("redundant asterisk compatibility must be limited to S and I")
    sign_date_policy = registry.get("canonical_sign_date_policy", {})
    errors.extend(
        _exact_keys(
            sign_date_policy,
            {
                "format",
                "syntax_pattern",
                "r1_example",
                "output_example",
                "recipient_rule",
                "mandatory_marker_rule",
                "verification_rule",
            },
            "canonical_sign_date_policy",
        )
    )
    if sign_date_policy.get("format") != CANONICAL_SIGN_DATE_FORMAT:
        errors.append("canonical Sign Date format changed")
    if sign_date_policy.get("r1_example") != CANONICAL_SIGN_DATE_R1:
        errors.append("canonical R1 Sign Date syntax changed")
    if "Do not add *" not in str(sign_date_policy.get("mandatory_marker_rule", "")):
        errors.append("canonical Sign Date policy must explicitly forbid the asterisk")
    if "one" not in str(sign_date_policy.get("recipient_rule", "")).lower():
        errors.append("canonical Sign Date policy must require one recipient per tag")
    evidence = registry.get("evidence_policy", {})
    errors.extend(
        _exact_keys(
            evidence,
            {
                "officially_documented_grammar",
                "user_confirmed_contracts_handoff",
                "tenant_smoke_test_evidence_recorded",
                "rule",
            },
            "evidence_policy",
        )
    )
    if evidence.get("user_confirmed_contracts_handoff") != [
        "{{I:R1*}}",
        CANONICAL_SIGN_DATE_R1,
    ]:
        errors.append(
            "user-confirmed Contracts handoff evidence must record the Initial alias and canonical formatted Sign Date"
        )
    expected_smoke_evidence = [
        {
            "date": "2026-07-17",
            "syntax": CANONICAL_SIGN_DATE_R1,
            "stage": "preview_field_conversion",
            "result": "passed",
            "source": "user-confirmed Zoho Contracts-to-Zoho Sign test",
            "post_signature_value_population": "pending",
        }
    ]
    if evidence.get("tenant_smoke_test_evidence_recorded") != expected_smoke_evidence:
        errors.append("tenant smoke-test evidence must record the exact 2026-07-17 preview result")

    constraints = registry.get("observed_pipeline_constraints", {})
    errors.extend(
        _exact_keys(
            constraints,
            {"multiple_recipient_field_ownership", "table_cell_sign_date"},
            "observed_pipeline_constraints",
        )
    )
    multiple = constraints.get("multiple_recipient_field_ownership", {})
    errors.extend(
        _exact_keys(
            multiple,
            {"status", "evidence_date", "tested_families", "observation", "rule"},
            "observed_pipeline_constraints.multiple_recipient_field_ownership",
        )
    )
    if multiple.get("status") != "invalid":
        errors.append("combined-recipient field ownership must remain invalid")
    if "first parsed recipient" not in str(multiple.get("observation", "")):
        errors.append("combined-recipient evidence must record first-recipient-only assignment")
    if "one recipient owner" not in str(multiple.get("rule", "")).lower():
        errors.append("combined-recipient rule must require one recipient owner per field")

    table = constraints.get("table_cell_sign_date", {})
    errors.extend(
        _exact_keys(
            table,
            {
                "status",
                "evidence_date",
                "observation",
                "official_rule",
                "production_rule",
                "diagnostic_matrix",
            },
            "observed_pipeline_constraints.table_cell_sign_date",
        )
    )
    if table.get("status") != "open_layout_smoke_test":
        errors.append("table-cell Sign Date constraint must remain an open layout smoke test")
    if "one physical line" not in str(table.get("official_rule", "")):
        errors.append("table-cell official rule must preserve Zoho's one-line requirement")
    if CANONICAL_SIGN_DATE_FORMAT not in str(table.get("production_rule", "")):
        errors.append("table-cell production rule must preserve the canonical Sign Date format")
    matrix = table.get("diagnostic_matrix")
    if not isinstance(matrix, list) or len(matrix) != 10:
        errors.append("table-cell Sign Date diagnostic matrix must contain exactly 10 tests")
    else:
        if [entry.get("order") for entry in matrix if isinstance(entry, dict)] != list(
            range(1, 11)
        ):
            errors.append("table-cell Sign Date diagnostics must be ordered 1 through 10")
        for index, entry in enumerate(matrix):
            prefix = f"observed_pipeline_constraints.table_cell_sign_date.diagnostic_matrix[{index}]"
            if not isinstance(entry, dict):
                errors.append(f"{prefix} must be an object")
                continue
            errors.extend(
                _exact_keys(
                    entry,
                    {"order", "classification", "tag", "placement", "purpose"},
                    prefix,
                )
            )
            for key in ("classification", "tag", "placement", "purpose"):
                if not _non_empty_string(entry.get(key)):
                    errors.append(f"{prefix}.{key} must be non-empty")
        first = matrix[0] if isinstance(matrix[0], dict) else {}
        last = matrix[-1] if isinstance(matrix[-1], dict) else {}
        if first.get("tag") != CANONICAL_SIGN_DATE_R1:
            errors.append("table-cell diagnostic 1 must use the exact canonical Sign Date")
        if first.get("classification") != "production_control":
            errors.append("table-cell diagnostic 1 must be the production control")
        if last.get("tag") != "{{SD:R1}}":
            errors.append("table-cell diagnostic 10 must retain the short-tag fallback")
    aliases = registry.get("compatibility_aliases")
    expected_alias = {
        "field": "Initial",
        "canonical_syntax": "{{I:R1}}",
        "alias_syntax": "{{I:R1*}}",
        "evidence_status": "user_confirmed_contracts_handoff",
        "notes": "Accepted for existing Contracts content. The asterisk is redundant for Initial and is not the canonical published syntax.",
    }
    if aliases != [expected_alias]:
        errors.append("compatibility aliases must record only user-confirmed {{I:R1*}} against canonical {{I:R1}}")

    simple_tags = registry.get("production_safe_simple_tags")
    if not isinstance(simple_tags, list):
        errors.append("production_safe_simple_tags must be a list")
    else:
        actual_locks = [
            (
                entry.get("code"),
                entry.get("field"),
                entry.get("syntax"),
                entry.get("asterisk_policy"),
            )
            for entry in simple_tags
            if isinstance(entry, dict)
        ]
        if actual_locks != PRODUCTION_TAG_LOCKS:
            errors.append("production tag code/field/syntax/asterisk locks changed")
        for index, entry in enumerate(simple_tags):
            if not isinstance(entry, dict):
                errors.append(f"production_safe_simple_tags[{index}] must be an object")
                continue
            errors.extend(
                _exact_keys(
                    entry,
                    {"code", "field", "syntax", "asterisk_policy", "behavior"},
                    f"production_safe_simple_tags[{index}]",
                )
            )
            result = classify_tag(entry.get("syntax", ""), registry)
            if result["classification"] != "production_safe":
                errors.append(
                    f"production_safe_simple_tags[{index}].syntax is not production safe: {result['reason']}"
                )
            if result.get("code") != entry.get("code"):
                errors.append(
                    f"production_safe_simple_tags[{index}] parsed code does not match declared code"
                )
        sign_date = next(
            (entry for entry in simple_tags if isinstance(entry, dict) and entry.get("code") == "SD"),
            {},
        )
        if "only after" not in str(sign_date.get("behavior", "")).lower():
            errors.append("Sign Date behavior must state that it fills only after signing")

    complex_tags = registry.get("official_but_contracts_pipeline_unverified")
    if not isinstance(complex_tags, list):
        errors.append("official_but_contracts_pipeline_unverified must be a list")
    else:
        fields = [entry.get("field") for entry in complex_tags if isinstance(entry, dict)]
        if fields != UNVERIFIED_COMPLEX_FIELDS:
            errors.append("unverified complex field catalog or order changed")
        for index, entry in enumerate(complex_tags):
            if not isinstance(entry, dict):
                errors.append(f"unverified tag {index} must be an object")
                continue
            if entry.get("pipeline_status") != "contracts_pipeline_unverified":
                errors.append(f"unverified tag {index} has unsafe pipeline status")
            if entry.get("production_policy") != "blocked_until_smoke_tested":
                errors.append(f"unverified tag {index} must remain blocked")
            expected_keys = {
                "field",
                "syntax",
                "official_status",
                "pipeline_status",
                "production_policy",
                "notes",
            }
            errors.extend(_exact_keys(entry, expected_keys, f"unverified tag {index}"))
            result = classify_tag(entry.get("syntax", ""), registry)
            if result["classification"] != "official_pipeline_unverified":
                errors.append(
                    f"unverified tag {index} does not match documented quarantined grammar"
                )

    blocked = registry.get("official_but_ghre_blocked_features")
    if not isinstance(blocked, list):
        errors.append("official_but_ghre_blocked_features must be a list")
    else:
        expected_features = [
            "published_longhand_and_shorthand_examples",
            "omitted_recipient_defaults_to_first",
            "general_field_name_grammar",
            "font_parameters",
            "trailing_width_padding",
        ]
        if [entry.get("feature") for entry in blocked if isinstance(entry, dict)] != expected_features:
            errors.append("official-but-blocked feature list or order changed")
        for index, entry in enumerate(blocked):
            if not isinstance(entry, dict):
                errors.append(f"official_but_ghre_blocked_features[{index}] must be an object")
                continue
            errors.extend(
                _exact_keys(
                    entry,
                    {"feature", "official_examples", "ghre_policy", "notes"},
                    f"official_but_ghre_blocked_features[{index}]",
                )
            )
        if blocked and isinstance(blocked[0], dict) and blocked[0].get("official_examples") != PUBLISHED_LONG_SHORT_EXAMPLES:
            errors.append("published longhand/shorthand example pairs changed")
        font_feature = next(
            (entry for entry in blocked if isinstance(entry, dict) and entry.get("feature") == "font_parameters"),
            {},
        )
        if "inconsistent" not in str(font_feature.get("notes", "")).lower():
            errors.append("font-parameter policy must record the official separator inconsistency")

    catalog = registry.get("official_document_field_catalog")
    if not isinstance(catalog, list):
        errors.append("official_document_field_catalog must be a list")
    else:
        fields = [entry.get("field") for entry in catalog if isinstance(entry, dict)]
        if fields != OFFICIAL_SIGN_FIELDS:
            errors.append("official Zoho Sign document field catalog is incomplete or reordered")
        for index, entry in enumerate(catalog):
            if not isinstance(entry, dict):
                errors.append(f"official_document_field_catalog[{index}] must be an object")
                continue
            errors.extend(
                _exact_keys(
                    entry,
                    {"field", "text_tag_syntax", "placement"},
                    f"official_document_field_catalog[{index}]",
                )
            )
            field = entry.get("field")
            syntax = entry.get("text_tag_syntax")
            if OFFICIAL_FIELD_SYNTAX.get(field, object()) != syntax:
                errors.append(f"{field} published text-tag syntax changed")
            if field in NO_PUBLISHED_TAG_FIELDS and syntax is not None:
                errors.append(f"{field} must not claim published text-tag syntax")
            if field not in NO_PUBLISHED_TAG_FIELDS and syntax is None:
                errors.append(f"{field} must record its published text-tag syntax")
            if not _non_empty_string(entry.get("placement")):
                errors.append(f"official_document_field_catalog[{index}].placement is required")

    rejected = registry.get("unsupported_or_invented_text_tags")
    names = [entry.get("name") for entry in rejected if isinstance(entry, dict)] if isinstance(rejected, list) else []
    if names != ["Phone", "Image", "Payment", "Formula", "SplitText"]:
        errors.append("unsupported/invented tag list must fail closed for Phone, Image, Payment, Formula, and SplitText")
    if isinstance(rejected, list):
        for index, entry in enumerate(rejected):
            errors.extend(
                _exact_keys(entry, {"name", "reason"}, f"unsupported_or_invented_text_tags[{index}]")
            )
    return errors


def validate_authoring_standard(standard: Any) -> list[str]:
    """Validate the canonical Contracts authoring and typography standard."""

    errors: list[str] = []
    if not isinstance(standard, dict):
        return ["Contracts authoring standard must be an object"]
    errors.extend(
        _exact_keys(
            standard,
            {
                "schema_version",
                "standard_id",
                "title",
                "effective_date",
                "scope",
                "governance_status",
                "official_sources",
                "clause_type_master_list",
                "clause_requirements",
                "allowed_clause_language_block_styles",
                "semantic_style_map",
                "typography",
                "tenant_verification_gates",
                "zoho_sign_text_tag_registry",
            },
            "authoring standard",
        )
    )
    if standard.get("schema_version") != "1.0.0":
        errors.append("authoring standard schema_version must be 1.0.0")
    if standard.get("effective_date") != "2026-07-15":
        errors.append("authoring standard effective_date must be 2026-07-15")
    errors.extend(_validate_sources(standard.get("official_sources"), "official_sources"))
    source_urls = {
        source.get("url")
        for source in standard.get("official_sources", [])
        if isinstance(source, dict)
    }
    if (
        "https://help.zoho.com/portal/en/kb/contracts/getting-started/articles/tailor-the-settings-as-per-your-needs"
        not in source_urls
    ):
        errors.append("official sources must include Zoho Contracts Tailor Settings")
    if standard.get("clause_type_master_list") != CLAUSE_TYPES:
        errors.append("clause type master list must contain the exact 16 governed values in order")
    if standard.get("allowed_clause_language_block_styles") != CLAUSE_LANGUAGE_STYLES:
        errors.append("clause language block styles must be exactly Heading 3-5 and Normal")
    requirements = standard.get("clause_requirements", {})
    errors.extend(
        _exact_keys(
            requirements,
            {
                "required_metadata",
                "zoho_api_name_policy",
                "library_question_policy",
                "contract_type_override_policy",
                "language_variant_policy",
                "legal_review_policy",
            },
            "clause_requirements",
        )
    )
    required_metadata = requirements.get("required_metadata")
    if required_metadata != [
        "clause_type",
        "clause_name",
        "zoho_api_name",
        "zoho_api_name_status",
        "library_question",
        "language_variants",
    ]:
        errors.append("clause required metadata policy changed")

    if standard.get("semantic_style_map") != EXPECTED_SEMANTIC_STYLE_MAP:
        errors.append("semantic style map changed from Title/H1/H2/H3/H4/H5/Normal policy")
    if standard.get("typography") != EXPECTED_TYPOGRAPHY:
        errors.append("typography must exactly match the governed Zoho Contracts profile")
    gates = standard.get("tenant_verification_gates", {})
    errors.extend(
        _exact_keys(
            gates,
            {"inter_font_availability", "live_template_republish"},
            "tenant_verification_gates",
        )
    )
    for gate_name in ("inter_font_availability", "live_template_republish"):
        errors.extend(
            _exact_keys(gates.get(gate_name), {"status", "instruction"}, f"tenant_verification_gates.{gate_name}")
        )
    if gates.get("inter_font_availability", {}).get("status") != "tenant_verification_required":
        errors.append("Inter availability must remain tenant-verification required")
    inter_instruction = str(gates.get("inter_font_availability", {}).get("instruction", "")).lower()
    if "install" not in inter_instruction or "if installation is impossible" not in inter_instruction:
        errors.append("Inter gate must require organization-wide installation before considering amendment")
    if gates.get("live_template_republish", {}).get("status") != "manual_controlled_change_required":
        errors.append("live template republishing must remain a controlled manual change")
    if standard.get("zoho_sign_text_tag_registry") != (
        "src/zoho-sign/field-tags/zoho-contracts-text-tag-registry.json"
    ):
        errors.append("Contracts standard must reference the canonical Zoho Sign registry")
    return errors


def validate_schema_consistency(
    schema: Any,
    template: Any,
    standard: dict[str, Any],
) -> list[str]:
    """Ensure the checked-in schema enums and starter template match policy."""

    errors: list[str] = []
    if not isinstance(schema, dict):
        return ["clause schema must be an object"]
    properties = schema.get("properties", {})
    if properties.get("clause_type", {}).get("enum") != CLAUSE_TYPES:
        errors.append("clause schema type enum differs from the master list")
    try:
        style_enum = properties["language_variants"]["items"]["properties"]["blocks"][
            "items"
        ]["properties"]["style"]["enum"]
    except (KeyError, TypeError):
        style_enum = None
    if style_enum != CLAUSE_LANGUAGE_STYLES:
        errors.append("clause schema language style enum differs from Heading 3-5 and Normal")
    variant_properties = properties.get("language_variants", {}).get("items", {}).get("properties", {})
    if variant_properties.get("clause_title_style", {}).get("const") != "Heading 2":
        errors.append("clause schema must lock clause_title_style to Heading 2")
    if variant_properties.get("blocks", {}).get("minItems") != 1:
        errors.append("clause schema must require at least one substantive language block")
    variant_required = set(
        properties.get("language_variants", {}).get("items", {}).get("required", [])
    )
    if variant_required != {
        "variant_id",
        "variant_kind",
        "clause_title",
        "clause_title_style",
        "blocks",
    }:
        errors.append("clause schema variant requirements differ from policy")
    schema_required = set(schema.get("required", []))
    expected_required = {
        "schema_version",
        "clause_type",
        "clause_name",
        "zoho_api_name",
        "zoho_api_name_status",
        "library_question",
        "contract_type_question_overrides",
        "language_variants",
    }
    if schema_required != expected_required:
        errors.append("clause schema required properties differ from policy")
    if not isinstance(template, dict):
        errors.append("clause template must be an object")
    else:
        if template.get("$schema") != "../schemas/clause-definition.schema.json":
            errors.append("clause template must reference the checked-in schema")
        errors.extend(
            f"clause template: {error}"
            for error in validate_clause_definition(template, standard)
        )
    return errors


def _markdown_escape(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_authoring_markdown(standard: dict[str, Any]) -> str:
    """Render the human-readable Contracts standard from canonical JSON."""

    lines = [
        "<!-- Generated by validate_contract_authoring_standard.py; edit the JSON source. -->",
        "# GH Real Estate Zoho Contracts Authoring Standard",
        "",
        f"**Scope:** {standard['scope']}",
        f"**Effective date:** {standard['effective_date']}",
        "",
        "This standard governs contract structure, clause metadata, editor styles, and typography. It does not by itself alter or republish a live Zoho Contracts template.",
        "",
        "## Clause Type Master List",
        "",
    ]
    lines.extend(
        f"{index}. {clause_type}"
        for index, clause_type in enumerate(standard["clause_type_master_list"], start=1)
    )
    requirements = standard["clause_requirements"]
    lines.extend(
        [
            "",
            "## Clause authoring requirements",
            "",
            "Every clause definition must include a governed clause type, clause name, library selection question, nullable tenant-verified Zoho API name, and language variants. Exactly one variant is standard; approved alternates are optional. Every variant stores its clause title separately with `clause_title_style: Heading 2`.",
            "",
            f"- **Library question:** {requirements['library_question_policy']}",
            f"- **Contract-type overrides:** {requirements['contract_type_override_policy']}",
            f"- **Zoho API name:** {requirements['zoho_api_name_policy']}",
            f"- **Legal review:** {requirements['legal_review_policy']}",
            "",
            "Use `../templates/clause-definition.template.json` and validate before committing. Language `blocks` contain substantive language only and must use Heading 3-5 or Normal. Heading depth starts at the virtual Heading 2 clause title, may deepen by only one level at a time, may return shallower, and is unchanged by Normal paragraphs.",
            "",
            "## Editor semantic styles",
            "",
            "| Semantic role | Zoho Writer style | Allowed in clause language block |",
            "|---|---|---:|",
        ]
    )
    for item in standard["semantic_style_map"]:
        lines.append(
            f"| {_markdown_escape(item['semantic_role'])} | {_markdown_escape(item['zoho_writer_style'])} | {'Yes' if item['clause_language_block_allowed'] else 'No'} |"
        )
    typography = standard["typography"]
    lines.extend(
        [
            "",
            "The main document title uses the Writer **Title** style and article headings use Heading 1 in the contract template, outside clause language. Clause titles render from variant metadata as Heading 2. Substantive clause blocks use Heading 3, Heading 4/5, or Normal. Heading 6 is prohibited.",
            "",
            "## Typography",
            "",
            "| Element | Governed setting |",
            "|---|---|",
            "| Body text | Inter, 11 pt, regular, black `#000000`, left aligned |",
            "| Main title | Inter Bold, 18 pt, black, centered, Writer Title style |",
            "| Article headings | Inter Bold, 12 pt, dark navy `#1F4E79`, Heading 1 |",
            "| Subheadings | Inter Bold, 11 pt, Heading 2-5 |",
            "| Tables/forms | Inter, 10 pt |",
            "| Header/footer | Inter, 8-8.5 pt; canonical 8.5 pt; gray `#666666` |",
            f"| Line spacing | {typography['line_spacing']} |",
            f"| Paragraph spacing | 4-6 pt after; canonical {typography['paragraph_spacing_after_pt']} pt |",
            "| Page | US Letter; 0.75-inch margins on every side |",
            "| Alignment | Left aligned; never fully justified |",
            "",
            "## Publication gates",
            "",
            f"- **Inter availability:** {standard['tenant_verification_gates']['inter_font_availability']['instruction']}",
            f"- **Existing live templates:** {standard['tenant_verification_gates']['live_template_republish']['instruction']}",
            f"- **Zoho Sign fields:** Follow `{standard['zoho_sign_text_tag_registry']}`. Only production-safe governed tags pass the default scanner.",
            "",
            "## Official Zoho sources",
            "",
        ]
    )
    for source in standard["official_sources"]:
        lines.append(f"- [{source['title']}]({source['url']})")
    return "\n".join(lines) + "\n"


def render_sign_markdown(registry: dict[str, Any]) -> str:
    """Render the human-readable Sign registry from canonical JSON."""

    lines = [
        "<!-- Generated by validate_contract_authoring_standard.py; edit the JSON source. -->",
        "# Zoho Contracts to Zoho Sign Text Tag Registry",
        "",
        "This registry is fail-closed: a field visible in the Zoho Sign editor is not assumed to have text-tag syntax. Only the governed tags below are approved for production Contracts content.",
        "",
        f"**Effective date:** {registry['effective_date']}",
        "",
        "## Evidence levels",
        "",
        "- **Official grammar:** Recorded from Zoho's current automatic-field-addition documentation.",
        "- **User-confirmed Contracts handoff:** `{{I:R1*}}` and the canonical formatted Sign Date have been observed converting successfully.",
        "- **Tenant smoke-test evidence:** The canonical formatted Sign Date passed preview field conversion in ordinary body text on 2026-07-17. Combined-recipient probes and narrow-table placement exposed separate ownership and wrapping constraints; table-placement and completed-signature checks remain required before live-template publication.",
        "",
        "## Production-safe tags",
        "",
        "| Field | Code | Exact example | Operational behavior |",
        "|---|---|---|---|",
    ]
    for entry in registry["production_safe_simple_tags"]:
        lines.append(
            f"| {_markdown_escape(entry['field'])} | `{entry['code']}` | `{_markdown_escape(entry['syntax'])}` | {_markdown_escape(entry['behavior'])} |"
        )
    lines.extend(
        [
            "",
            "Zoho documents `*` as meaningful only for Text and Checkbox fields. The exact published checkbox shorthand `{{[]}}` is approved here only for an explicitly manifested single R1 signer and does not encode mandatory behavior; configure a required checkbox in the Sign editor unless a separate smoke test proves a role-specific tagged form. A redundant `*` on Signature (`S`) or Initial (`I`) is accepted for compatibility, including the user-confirmed `{{I:R1*}}`; do not infer additional semantics from it. Do not add `*` to Sign Date (`SD`): it is system-populated after the assigned recipient signs.",
            "",
            "## Canonical GHRE Sign Date standard",
            "",
            f"- Exact R1 syntax: `{_markdown_escape(registry['canonical_sign_date_policy']['r1_example'])}`",
            f"- Output example: `{registry['canonical_sign_date_policy']['output_example']}`",
            f"- Recipient rule: {registry['canonical_sign_date_policy']['recipient_rule']}",
            f"- Required-marker rule: {registry['canonical_sign_date_policy']['mandatory_marker_rule']}",
            f"- Verification: {registry['canonical_sign_date_policy']['verification_rule']}",
            "",
            "## Observed Contracts-to-Sign constraints",
            "",
            "### One field, one recipient",
            "",
            f"- Status: `{registry['observed_pipeline_constraints']['multiple_recipient_field_ownership']['status']}`",
            f"- Observed result: {registry['observed_pipeline_constraints']['multiple_recipient_field_ownership']['observation']}",
            f"- Production rule: {registry['observed_pipeline_constraints']['multiple_recipient_field_ownership']['rule']}",
            "",
            "A field appearing in preview does not prove that a combined-recipient expression worked. Inspect its assigned recipient. Use separate R1, R2, R3, and later tags.",
            "",
            "### Sign Date inside table cells",
            "",
            f"- Status: `{registry['observed_pipeline_constraints']['table_cell_sign_date']['status']}`",
            f"- Observed result: {registry['observed_pipeline_constraints']['table_cell_sign_date']['observation']}",
            f"- Official rule and syntax conclusion: {registry['observed_pipeline_constraints']['table_cell_sign_date']['official_rule']}",
            f"- Production rule: {registry['observed_pipeline_constraints']['table_cell_sign_date']['production_rule']}",
            "",
            "There is no documented table-specific text-tag syntax. The ranked tests below isolate rendered wrapping and provide a governed fallback. Run them only in a synthetic document with controlled recipients; do not promote a diagnostic tag into live content.",
            "",
            "| Test | Classification | Exact tag | Placement | Purpose |",
            "|---:|---|---|---|---|",
            *[
                "| "
                + " | ".join(
                    [
                        str(entry["order"]),
                        f"`{_markdown_escape(entry['classification'])}`",
                        f"`{_markdown_escape(entry['tag'])}`",
                        _markdown_escape(entry["placement"]),
                        _markdown_escape(entry["purpose"]),
                    ]
                )
                + " |"
                for entry in registry["observed_pipeline_constraints"][
                    "table_cell_sign_date"
                ]["diagnostic_matrix"]
            ],
            "",
            "Only tests 1 and 3 preserve the canonical GHRE syntax. Tests 2 and 4-9 are diagnostics; test 10 is a governed fallback that requires setting the final format in Zoho Sign or using a native signer field.",
            "",
            "## Official syntax blocked pending Contracts-pipeline testing",
            "",
            "| Field | Exact official syntax example | Status |",
            "|---|---|---|",
        ]
    )
    for entry in registry["official_but_contracts_pipeline_unverified"]:
        lines.append(
            f"| {_markdown_escape(entry['field'])} | `{_markdown_escape(entry['syntax'])}` | `{entry['production_policy']}` |"
        )
    lines.extend(
        [
            "",
            "Dropdown, radio, and checkbox-group tags remain blocked until their exact Contracts-to-Sign paths pass isolated smoke tests.",
            "",
            "## Other published features blocked by GHRE",
            "",
            "Zoho also publishes longhand and recipient-omitting examples, broad named-field grammar, font parameters, and trailing-space width padding. They are reference material, not production allowlist entries:",
            "",
        ]
    )
    for entry in registry["official_but_ghre_blocked_features"]:
        examples = ", ".join(
            f"`{_markdown_escape(example)}`" for example in entry["official_examples"]
        )
        lines.append(
            f"- **{_markdown_escape(entry['feature'])}** — {examples}. Policy: `{entry['ghre_policy']}`. {_markdown_escape(entry['notes'])}"
        )
    lines.extend(
        [
            "",
            "## Complete current Zoho Sign document field catalog",
            "",
            "| Document field | Published text-tag syntax | Placement policy |",
            "|---|---|---|",
        ]
    )
    for entry in registry["official_document_field_catalog"]:
        syntax = (
            f"`{_markdown_escape(entry['text_tag_syntax'])}`"
            if entry["text_tag_syntax"] is not None
            else "None published"
        )
        lines.append(
            f"| {_markdown_escape(entry['field'])} | {syntax} | {_markdown_escape(entry['placement'])} |"
        )
    lines.extend(
        [
            "",
            "No dedicated official text tag is published for Image, Payment, Formula, or Split Text. Zoho's current text-tag table also does not publish a dedicated Phone tag. Place those fields through the Sign editor, a governed Sign template, or the API as described above; tags such as `{{Phone:R1}}`, `{{Image:R1}}`, `{{Payment:R1}}`, `{{Formula:R1}}`, and `{{SplitText:R1}}` are rejected.",
            "",
            "## Safety rules",
            "",
            f"- Maximum document length: **{registry['document_safety_policy']['maximum_pages']} pages** (Zoho documents the feature for documents less than 75 pages).",
            "- Maximum recipient manifest: **25 recipients**, matching Zoho Sign's sending limit.",
            "- Keep every tag on one physical line and use ASCII braces and straight double quotes.",
            "- Declare recipients explicitly as R1-R25; implicit first-recipient assignment is not allowed in governed content.",
            "- Every signer in the recipient-role manifest must have at least one assigned field, and every tag recipient must appear in the manifest.",
            "- Noncanonical formatted, multi-recipient, unknown, or invented tags fail the production scanner.",
            "",
            "## Official Zoho sources",
            "",
        ]
    )
    for source in registry["official_sources"]:
        lines.append(f"- [{source['title']}]({source['url']})")
    return "\n".join(lines) + "\n"


def markdown_drift_errors(
    standard: dict[str, Any],
    sign_registry: dict[str, Any],
    actual_standard_markdown: str,
    actual_sign_markdown: str,
) -> list[str]:
    """Return deterministic errors when generated references differ from JSON."""

    errors: list[str] = []
    if actual_standard_markdown != render_authoring_markdown(standard):
        errors.append("contract authoring Markdown is stale")
    if actual_sign_markdown != render_sign_markdown(sign_registry):
        errors.append("Zoho Sign text-tag Markdown is stale")
    return errors


def validate_clause_records(
    records: Iterable[tuple[str, Any]], standard: dict[str, Any]
) -> list[str]:
    """Validate named clause records; useful for recursive CI scans and tests."""

    errors: list[str] = []
    for name, record in records:
        errors.extend(
            f"{name}: {error}"
            for error in validate_clause_definition(record, standard)
        )
    return errors


def validate_clause_directory(root: Path, standard: dict[str, Any]) -> list[str]:
    """Recursively validate every checked-in ``*.clause.json`` record."""

    clause_root = root / "src/zoho-contracts/clauses"
    records: list[tuple[str, Any]] = []
    errors: list[str] = []
    if not clause_root.is_dir():
        return ["src/zoho-contracts/clauses directory is required"]
    if not (clause_root / "README.md").is_file():
        errors.append("src/zoho-contracts/clauses/README.md is required")
    for path in sorted(clause_root.rglob("*.clause.json")):
        relative = path.relative_to(root).as_posix()
        try:
            records.append((relative, load_json(path)))
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"{relative}: {exc}")
    errors.extend(validate_clause_records(records, standard))
    return errors


def validate_global_style_profile(root: Path, standard: dict[str, Any]) -> list[str]:
    """Check the optional global profile mirror when the global file is present."""

    path = root / "docs/standards/document-style-profile.json"
    if not path.exists():
        return []
    try:
        global_profile = load_json(path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [f"{path.relative_to(root).as_posix()}: {exc}"]
    platform_profiles = global_profile.get("platform_profiles")
    if not isinstance(platform_profiles, dict):
        return ["document-style-profile.json must contain platform_profiles"]
    profile = platform_profiles.get("zoho_contracts")
    if not isinstance(profile, dict):
        return ["document-style-profile.json must contain platform_profiles.zoho_contracts"]
    errors = _exact_keys(
        profile,
        {"governed_by", "scope", "typography", "semantic_style_map"},
        "platform_profiles.zoho_contracts",
    )
    if profile.get("governed_by") != (
        "src/zoho-contracts/standards/contract-authoring-standard.json"
    ):
        errors.append("platform_profiles.zoho_contracts.governed_by is incorrect")
    if profile.get("scope") != standard.get("scope"):
        errors.append("platform_profiles.zoho_contracts.scope drifted from Contracts standard")
    if profile.get("typography") != standard.get("typography"):
        errors.append("platform_profiles.zoho_contracts.typography drifted from Contracts standard")
    if profile.get("semantic_style_map") != standard.get("semantic_style_map"):
        errors.append("platform_profiles.zoho_contracts.semantic_style_map drifted from Contracts standard")
    return errors


def validate_repository(root: Path, *, check_markdown: bool = True) -> list[str]:
    """Validate all canonical files and optionally detect generated-doc drift."""

    paths = _paths(root)
    errors: list[str] = []
    loaded: dict[str, dict[str, Any]] = {}
    for key in ("standard", "clause_schema", "clause_template", "sign_registry"):
        try:
            loaded[key] = load_json(paths[key])
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"{paths[key]}: {exc}")
    if errors:
        return errors
    errors.extend(
        f"contract-authoring-standard.json: {error}"
        for error in validate_authoring_standard(loaded["standard"])
    )
    errors.extend(
        f"zoho-contracts-text-tag-registry.json: {error}"
        for error in validate_sign_registry(loaded["sign_registry"])
    )
    errors.extend(
        f"schema/template: {error}"
        for error in validate_schema_consistency(
            loaded["clause_schema"], loaded["clause_template"], loaded["standard"]
        )
    )
    errors.extend(validate_clause_directory(root, loaded["standard"]))
    errors.extend(validate_global_style_profile(root, loaded["standard"]))
    if check_markdown and not errors:
        actual: dict[str, str] = {}
        for key in ("standard_markdown", "sign_markdown"):
            try:
                actual[key] = paths[key].read_text(encoding="utf-8")
            except OSError as exc:
                errors.append(f"{paths[key]}: {exc}")
        if len(actual) == 2:
            for error in markdown_drift_errors(
                loaded["standard"],
                loaded["sign_registry"],
                actual["standard_markdown"],
                actual["sign_markdown"],
            ):
                errors.append(
                    f"{error}; run validate_contract_authoring_standard.py --write-markdown"
                )
    return errors


def write_markdown(root: Path) -> None:
    """Regenerate both Markdown references from their canonical JSON sources."""

    paths = _paths(root)
    standard = load_json(paths["standard"])
    sign_registry = load_json(paths["sign_registry"])
    paths["standard_markdown"].write_text(
        render_authoring_markdown(standard), encoding="utf-8", newline="\n"
    )
    paths["sign_markdown"].write_text(
        render_sign_markdown(sign_registry), encoding="utf-8", newline="\n"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=repository_root(),
        help="repository root (defaults to the script's repository)",
    )
    parser.add_argument(
        "--write-markdown",
        action="store_true",
        help="regenerate Markdown from validated canonical JSON",
    )
    args = parser.parse_args(argv)
    root = args.root.resolve()
    errors = validate_repository(root, check_markdown=not args.write_markdown)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    if args.write_markdown:
        write_markdown(root)
    print(
        f"Validated {len(CLAUSE_TYPES)} clause types, {len(PRODUCTION_TAG_LOCKS)} production-safe Sign mappings, typography, schema/template, recursive clause records, and generated documentation."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
