#!/usr/bin/env python3
"""Validate and render the canonical Zoho Contracts field registry.

The registry contains public field definitions only. It intentionally excludes
live values, keeps Contracts API names unverified, and permits CRM API names
only where the governed production metadata readback explicitly verifies them.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
REGISTRY_PATH = ROOT / "src/zoho-contracts/field-maps/contract-field-registry.json"
MARKDOWN_PATH = ROOT / "src/zoho-contracts/field-maps/contract-field-registry.md"
SCHEMA_PATH = ROOT / "src/zoho-contracts/schemas/contract-field-registry.schema.json"

REQUIRED_CUSTOM_TYPES = [
    "Text",
    "Date",
    "Number",
    "Currency",
    "Dropdown",
    "Single Checkbox",
    "Percent",
    "Phone",
    "Email",
]

EXPECTED_SYSTEM_LABELS = [
    "Agreement Name",
    "Party A Jurisdiction",
    "Party A",
    "Party A Time Zone Name",
    "Party B Time Zone Name",
    "Party A Time Zone",
    "Party B Time Zone",
    "Party B Jurisdiction",
    "Term Period",
    "Condition / Event / Fulfilment of Order / Completion of Services",
    "Term End Date",
    "Party B",
    "Non-renewal Notice Period",
    "Renewal Notice Days",
    "Termination Notice Period",
    "Termination Fee",
    "Party A Name",
    "Party A Address",
    "Party B Address",
    "Agreement Date",
    "Renewal Term Period",
    "Renewal Notice Period",
    "Party B Name",
    "Party A Phone Number",
    "Party A Apartment/Suite/Building",
    "Party A Street Address",
    "Party A City",
    "Party A State",
    "Party A Zip Code",
    "Party A Country",
    "Party A Contact Name",
    "Party A Contact Email Address",
    "Party A Contact Phone Number",
    "Party A Contact Job Title",
    "Party B Phone Number",
    "Party B Apartment/Suite/Building",
    "Party B Street Address",
    "Party B City",
    "Party B State",
    "Party B Zip Code",
    "Party B Country",
    "Party B Contact Name",
    "Party B Contact Email Address",
    "Party B Contact Phone Number",
    "Party B Contact Job Title",
    "Contract Amount",
]

BASELINE_CUSTOM_LABELS = [
    "Lease Number",
    "Property Street Line 1",
    "Property City",
    "Property State",
    "Property Zip Code",
    "Storage Unit Number",
    "Number of Storage Unit Keys Provided",
    "Storage Term Begins",
    "Storage Unit Rent",
    "Storage Term Ends",
    "Storage Term Starts",
    "Party C Contact Name",
    "Party D Contact Name",
    "Party C Contact Phone Number",
    "Party D Contact Phone Number",
    "Party C Contact Email Address",
    "Party D Contact Email Address",
    "Lease Agreement Effective Date",
    "Property Apartment Number",
]

REQUESTED_DESTINATION_TYPES = {
    "Base Rent Amount": "Currency",
    "Security Deposit Amount": "Currency",
    "Total Monthly Pet Rent Amount": "Currency",
    "Base Storage Unit Rent Amount": "Currency",
    "Total Storage Unit Rent Amount": "Currency",
    "Total Monthly Rent Amount": "Currency",
    "Next Total Monthly Rent Due Date": "Date",
    "Prorated Rent Start Date": "Date",
    "Prorated Rent End Date": "Date",
    "Prorated Base Rent Amount": "Currency",
    "Pet Security Deposit Amount": "Currency",
    "Prorated Pet Rent Amount": "Currency",
    "Prorated Storage Unit Rent Amount": "Currency",
    "Holding Deposit Amount": "Currency",
    "First Full Month Base Rent Amount": "Currency",
    "Total Due Before Possession": "Currency",
}

VERIFIED_CRM_API_CROSSWALK = {
    "Agreement Name": "Name",
    "Agreement Date": "Agreement_Date",
    "Lease Agreement Effective Date": "Lease_Start_Date",
    "Term End Date": "Lease_End_Date",
    "Property Street Line 1": "Premises_Street_Line_1",
    "Property Apartment Number": "Premises_Apartment_Number",
    "Property City": "Premises_City",
    "Property State": "Premises_State",
    "Property Zip Code": "Premises_ZIP_Code",
    "Party C Contact Name": "Tenant_2_Legal_Name_Snapshot",
    "Party D Contact Name": "Tenant_3_Legal_Name_Snapshot",
    "Security Deposit Amount": "Security_Deposit",
    "Total Monthly Pet Rent Amount": "Total_Monthly_Pet_Rent_Amount",
    "Base Storage Unit Rent Amount": "Base_Storage_Unit_Rent_Amount",
    "Total Storage Unit Rent Amount": "Total_Monthly_Storage_Rent_Amount",
    "Next Total Monthly Rent Due Date": "Next_Total_Monthly_Rent_Due_Date",
    "Prorated Rent Start Date": "Prorated_Rent_Start_Date",
    "Prorated Rent End Date": "Prorated_Rent_End_Date",
    "Pet Security Deposit Amount": "Pet_Security_Deposit_Amount",
    "Prorated Pet Rent Amount": "Prorated_Pet_Rent_Amount",
    "Prorated Storage Unit Rent Amount": "Prorated_Storage_Unit_Rent_Amount",
    "Holding Deposit Amount": "Holding_Deposit_Credit_Applied",
    "First Full Month Base Rent Amount": "First_Full_Month_Base_Rent_Amount",
    "Total Due Before Possession": "Total_Due_Before_Possession",
}

CRM_FIELDS_WITH_UNDEFINED_SEMANTICS = {
    "Base Rent Amount",
    "Total Monthly Rent Amount",
    "Prorated Base Rent Amount",
}

REVIEW_REQUIRED_DESTINATION_LABELS = {
    "First Full Month Base Rent Amount",
    "Total Due Before Possession",
}

EXPECTED_CUSTOM_LABELS = BASELINE_CUSTOM_LABELS + list(
    REQUESTED_DESTINATION_TYPES
)

LABEL_EVIDENCE_ID = "user-confirmed-live-labels-2026-07-24"
USER_CONFIRMED_LIVE_LABELS = [
    "Base Rent Amount",
    "Security Deposit Amount",
    "Total Monthly Pet Rent Amount",
    "Base Storage Unit Rent Amount",
    "Total Storage Unit Rent Amount",
    "Total Monthly Rent Amount",
    "Next Total Monthly Rent Due Date",
    "Prorated Rent Start Date",
    "Prorated Rent End Date",
    "Prorated Base Rent Amount",
    "Pet Security Deposit Amount",
    "Prorated Pet Rent Amount",
    "Prorated Storage Unit Rent Amount",
    "Holding Deposit Amount",
    "Total Due Before Possession",
    "Agreement Effective Date",
    "Lease Agreement Effective Date",
    "Term End Date",
    "Property Street Line 1",
    "Property Apartment Number",
    "Property City",
    "Property State",
    "Property Zip Code",
    "Party C Contact Name",
    "Party D Contact Name",
    "Party A",
    "Party A Name",
    "Party A Jurisdiction",
    "Party A Address",
    "Party A Contact Name",
    "Party A Contact Phone Number",
    "Party A Contact Email Address",
    "Party B",
    "Party B Name",
    "Party B Jurisdiction",
    "Party B Address",
    "Party B Contact Name",
]

ALLOWED_NATIVE_TYPES = {
    "Boolean",
    "Number",
    "String",
    "Date",
    "Index",
    "Text",
    "Currency",
    "Term",
    "Percent",
    "Phone",
    "Email",
    "Unknown",
}
ALLOWED_STATUSES = {"active", "deprecated_alias", "review_required"}
ALLOWED_TYPE_STATUSES = {
    "official_system_semantics",
    "design_decision",
    "tenant_api_required",
    "tenant_api_verified",
}
ALLOWED_PORTABLE_TYPES = {
    "text",
    "multiline_text",
    "date",
    "integer",
    "currency",
    "phone",
    "email",
    "duration",
    "entity_reference",
    "time_zone",
    "unknown",
}
ALLOWED_CRM_TYPES = {
    "Single Line",
    "Multi Line",
    "Date",
    "Number",
    "Currency",
    "Phone",
    "Email",
    "Pick List",
    "Lookup",
    "Composite",
    "Unresolved",
}
ALLOWED_CRM_API_STATUSES = {
    "proposed_unverified",
    "tenant_api_required",
    "design_required",
    "do_not_create",
    "do_not_create_until_defined",
    "verified_live_mcp",
}
ALLOWED_SENSITIVITIES = {
    "internal_contract",
    "internal_identifier",
    "restricted_pii",
    "restricted_property",
    "confidential_financial",
}
TOP_LEVEL_KEYS = {
    "$schema",
    "registry_id",
    "version",
    "as_of_date",
    "record_counts",
    "allowed_custom_types",
    "official_sources",
    "label_evidence",
    "policies",
    "fields",
}
FIELD_KEYS = {
    "id",
    "label",
    "classification",
    "status",
    "aliases",
    "canonical_id",
    "zoho",
    "portable_type",
    "unit",
    "allowed_values",
    "crm",
    "source_of_truth",
    "sensitivity",
    "validation",
}
REQUIRED_FIELD_KEYS = {
    "id",
    "label",
    "classification",
    "status",
    "zoho",
    "portable_type",
    "crm",
    "source_of_truth",
    "sensitivity",
    "validation",
}
ZOHO_KEYS = {
    "ui_type",
    "expected_native_type",
    "api_name",
    "type_status",
    "evidence_id",
    "allow_decimals",
}
REQUIRED_ZOHO_KEYS = {
    "ui_type",
    "expected_native_type",
    "api_name",
    "type_status",
    "evidence_id",
}
CRM_KEYS = {"recommended_type", "proposed_api_name", "api_name_status"}


def load_registry(path: Path = REGISTRY_PATH) -> dict[str, Any]:
    """Load a UTF-8 registry JSON object."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("registry root must be an object")
    return payload


def _duplicates(values: list[str]) -> list[str]:
    counts = Counter(value.casefold() for value in values)
    return sorted(value for value, count in counts.items() if count > 1)


def _json_type_matches(value: object, expected: str) -> bool:
    """Match JSON types without treating booleans as Python integers."""

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
    """Compare JSON values with strict scalar typing."""

    if isinstance(left, (bool, int, float)) or isinstance(right, (bool, int, float)):
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
    """Validate the JSON-Schema subset used by this registry.

    This avoids a runtime dependency while keeping CI coupled to the actual
    checked-in schema instead of a second hand-maintained type definition.
    """

    if not isinstance(schema, dict):
        return [f"{path}: schema node must be an object"]
    if root_schema is None:
        root_schema = schema
    problems: list[str] = []

    if "$ref" in schema:
        try:
            target = _resolve_local_ref(root_schema, schema["$ref"])
        except (TypeError, ValueError) as exc:
            return [f"{path}: {exc}"]
        return validate_json_schema(
            value, target, root_schema=root_schema, path=path
        )

    any_of = schema.get("anyOf")
    if isinstance(any_of, list):
        if not any(
            not validate_json_schema(value, candidate, root_schema=root_schema, path=path)
            for candidate in any_of
        ):
            problems.append(f"{path}: value does not satisfy anyOf")

    if "const" in schema and not _json_equal(value, schema["const"]):
        problems.append(f"{path}: value does not match const")
    if isinstance(schema.get("enum"), list) and not any(
        _json_equal(value, candidate) for candidate in schema["enum"]
    ):
        problems.append(f"{path}: value is not in enum")

    expected_types = schema.get("type")
    if isinstance(expected_types, str):
        expected_types = [expected_types]
    type_matches = True
    if isinstance(expected_types, list):
        type_matches = any(
            isinstance(item, str) and _json_type_matches(value, item)
            for item in expected_types
        )
        if not type_matches:
            problems.append(
                f"{path}: expected type " + " or ".join(str(item) for item in expected_types)
            )
    if not type_matches:
        return problems

    if isinstance(value, str):
        minimum_length = schema.get("minLength")
        maximum_length = schema.get("maxLength")
        if isinstance(minimum_length, int) and len(value) < minimum_length:
            problems.append(f"{path}: string is shorter than minLength")
        if isinstance(maximum_length, int) and len(value) > maximum_length:
            problems.append(f"{path}: string is longer than maxLength")
        pattern = schema.get("pattern")
        if isinstance(pattern, str) and re.search(pattern, value) is None:
            problems.append(f"{path}: string does not match pattern")
        if schema.get("format") == "date":
            try:
                parsed = dt.date.fromisoformat(value)
            except ValueError:
                problems.append(f"{path}: invalid ISO date")
            else:
                if parsed.isoformat() != value:
                    problems.append(f"{path}: date must be canonical YYYY-MM-DD")

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        minimum = schema.get("minimum")
        if isinstance(minimum, (int, float)) and value < minimum:
            problems.append(f"{path}: number is below minimum")

    if isinstance(value, list):
        minimum_items = schema.get("minItems")
        if isinstance(minimum_items, int) and len(value) < minimum_items:
            problems.append(f"{path}: array has fewer than minItems")
        if schema.get("uniqueItems") is True:
            normalized = [
                json.dumps(item, sort_keys=True, separators=(",", ":"))
                for item in value
            ]
            if len(set(normalized)) != len(normalized):
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
        minimum_properties = schema.get("minProperties")
        if isinstance(minimum_properties, int) and len(value) < minimum_properties:
            problems.append(f"{path}: object has fewer than minProperties")
        required = schema.get("required", [])
        if isinstance(required, list):
            for key in required:
                if key not in value:
                    problems.append(f"{path}: missing required property {key}")
        properties = schema.get("properties", {})
        if not isinstance(properties, dict):
            properties = {}
        for key, child_value in value.items():
            child_path = f"{path}.{key}"
            if key in properties:
                problems.extend(
                    validate_json_schema(
                        child_value,
                        properties[key],
                        root_schema=root_schema,
                        path=child_path,
                    )
                )
                continue
            additional = schema.get("additionalProperties", True)
            if additional is False:
                problems.append(f"{path}: unknown property {key}")
            elif isinstance(additional, dict):
                problems.extend(
                    validate_json_schema(
                        child_value,
                        additional,
                        root_schema=root_schema,
                        path=child_path,
                    )
                )

    all_of = schema.get("allOf")
    if isinstance(all_of, list):
        for sub_schema in all_of:
            problems.extend(
                validate_json_schema(
                    value, sub_schema, root_schema=root_schema, path=path
                )
            )
    if_schema = schema.get("if")
    then_schema = schema.get("then")
    if isinstance(if_schema, dict) and isinstance(then_schema, dict):
        if not validate_json_schema(
            value, if_schema, root_schema=root_schema, path=path
        ):
            problems.extend(
                validate_json_schema(
                    value, then_schema, root_schema=root_schema, path=path
                )
            )
    return problems


def validate_against_checked_in_schema(registry: dict[str, Any]) -> list[str]:
    """Load the canonical schema and validate the registry against it."""

    try:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [f"could not load contract field registry schema: {exc}"]
    if not isinstance(schema, dict):
        return ["contract field registry schema root must be an object"]
    return validate_json_schema(registry, schema)


def validate_registry(registry: dict[str, Any]) -> list[str]:
    """Return deterministic validation errors for a registry object."""

    # Schema validation is a structural gate. Domain checks below intentionally
    # use required keys directly, so malformed data must never reach them.
    schema_problems = validate_against_checked_in_schema(registry)
    if schema_problems:
        return schema_problems
    problems: list[str] = []
    unknown_top_level = sorted(set(registry) - TOP_LEVEL_KEYS)
    if unknown_top_level:
        problems.append(
            "unknown top-level properties: " + ", ".join(unknown_top_level)
        )
    missing_top_level = sorted(TOP_LEVEL_KEYS - set(registry))
    if missing_top_level:
        problems.append(
            "missing top-level properties: " + ", ".join(missing_top_level)
        )
    if registry.get("registry_id") != "GHRE-ZC-FIELDS":
        problems.append("registry_id must be GHRE-ZC-FIELDS")
    if not isinstance(registry.get("version"), str) or not re.fullmatch(
        r"[0-9]+\.[0-9]+\.[0-9]+", registry.get("version", "")
    ):
        problems.append("version must use semantic version format")
    if not isinstance(registry.get("as_of_date"), str) or not re.fullmatch(
        r"[0-9]{4}-[0-9]{2}-[0-9]{2}", registry.get("as_of_date", "")
    ):
        problems.append("as_of_date must use YYYY-MM-DD")

    fields = registry.get("fields")
    if not isinstance(fields, list):
        return ["fields must be an array"]

    allowed_custom_types = registry.get("allowed_custom_types")
    if allowed_custom_types != REQUIRED_CUSTOM_TYPES:
        problems.append(
            "allowed_custom_types must exactly match the tenant UI order: "
            + ", ".join(REQUIRED_CUSTOM_TYPES)
        )

    sources = registry.get("official_sources")
    if not isinstance(sources, dict) or not sources:
        problems.append("official_sources must be a non-empty object")
        sources = {}
    for source_id, source in sources.items():
        if not isinstance(source, str) or not source.strip():
            problems.append(f"official source {source_id!r} must be non-empty")
        elif source.startswith("http://"):
            problems.append(f"official source {source_id!r} must use HTTPS")

    policies = registry.get("policies")
    if not isinstance(policies, dict) or not policies:
        problems.append("policies must be a non-empty object")
    else:
        for policy_id, policy in policies.items():
            if not isinstance(policy, str) or not policy.strip():
                problems.append(f"policy {policy_id!r} must be a non-empty string")

    label_evidence = registry.get("label_evidence")
    if not isinstance(label_evidence, list):
        problems.append("label_evidence must be an array")
        label_evidence = []
    elif len(label_evidence) != 1:
        problems.append(
            "label_evidence must contain exactly the governed 2026-07-24 snapshot"
        )
    if label_evidence:
        evidence = label_evidence[0]
        expected_metadata = {
            "id": LABEL_EVIDENCE_ID,
            "evidence_type": "user_confirmed_live_label",
            "confirmed_on": "2026-07-24",
            "scope": "label_only",
            "api_name_status": "unverified",
        }
        for key, expected in expected_metadata.items():
            if evidence.get(key) != expected:
                problems.append(
                    f"label_evidence[0].{key} must be {expected!r}"
                )
        if evidence.get("labels") != USER_CONFIRMED_LIVE_LABELS:
            problems.append(
                "label_evidence[0].labels must exactly match the governed "
                f"{len(USER_CONFIRMED_LIVE_LABELS)}-label inventory"
            )

    ids = [str(field.get("id", "")) for field in fields if isinstance(field, dict)]
    labels = [str(field.get("label", "")) for field in fields if isinstance(field, dict)]
    for duplicate in _duplicates(ids):
        problems.append(f"duplicate field id: {duplicate}")
    for duplicate in _duplicates(labels):
        problems.append(f"duplicate field label: {duplicate}")
    id_set = set(ids)

    actual_counts = Counter(
        field.get("classification") for field in fields if isinstance(field, dict)
    )
    expected_counts = registry.get("record_counts", {})
    if not isinstance(expected_counts, dict):
        problems.append("record_counts must be an object")
        expected_counts = {}
    elif set(expected_counts) != {"system", "custom", "total"}:
        problems.append("record_counts must contain only system, custom, and total")
    for classification in ("system", "custom"):
        if expected_counts.get(classification) != actual_counts[classification]:
            problems.append(
                f"record_counts.{classification} does not match field inventory"
            )
    if expected_counts.get("total") != len(fields):
        problems.append("record_counts.total does not match field inventory")

    system_labels = [
        field["label"]
        for field in fields
        if isinstance(field, dict) and field.get("classification") == "system"
    ]
    custom_labels = [
        field["label"]
        for field in fields
        if isinstance(field, dict) and field.get("classification") == "custom"
    ]
    if system_labels != EXPECTED_SYSTEM_LABELS:
        problems.append("system field labels/order drifted from the submitted inventory")
    if custom_labels != EXPECTED_CUSTOM_LABELS:
        problems.append("custom field labels/order drifted from the submitted inventory")

    alias_labels: dict[str, str] = {}
    for index, field in enumerate(fields):
        context = f"fields[{index}]"
        if not isinstance(field, dict):
            problems.append(f"{context} must be an object")
            continue

        unknown_field_keys = sorted(set(field) - FIELD_KEYS)
        if unknown_field_keys:
            problems.append(
                f"{context}: unknown properties: " + ", ".join(unknown_field_keys)
            )
        missing_field_keys = sorted(REQUIRED_FIELD_KEYS - set(field))
        if missing_field_keys:
            problems.append(
                f"{context}: missing properties: " + ", ".join(missing_field_keys)
            )

        field_id = field.get("id")
        label = field.get("label")
        classification = field.get("classification")
        status = field.get("status")
        zoho = field.get("zoho")
        crm = field.get("crm")

        if not isinstance(field_id, str) or not re.fullmatch(r"[a-z][a-z0-9_]*", field_id):
            problems.append(f"{context}.id must be lower snake_case")
        if not isinstance(label, str) or not label.strip() or len(label) > 255:
            problems.append(f"{context}.label must contain 1-255 characters")
        if classification not in {"system", "custom"}:
            problems.append(f"{context}.classification must be system or custom")
        if status not in ALLOWED_STATUSES:
            problems.append(f"{context}.status is invalid")
        if not isinstance(field.get("source_of_truth"), str) or not field["source_of_truth"].strip():
            problems.append(f"{context}.source_of_truth is required")
        if not isinstance(field.get("validation"), str) or not field["validation"].strip():
            problems.append(f"{context}.validation is required")
        if field.get("sensitivity") not in ALLOWED_SENSITIVITIES:
            problems.append(f"{context}.sensitivity is invalid")
        if field.get("portable_type") not in ALLOWED_PORTABLE_TYPES:
            problems.append(f"{context}.portable_type is invalid")

        unit = field.get("unit")
        if unit is not None and (not isinstance(unit, str) or not unit.strip()):
            problems.append(f"{context}.unit must be a non-empty string")
        allowed_values = field.get("allowed_values")
        if allowed_values is not None:
            if (
                not isinstance(allowed_values, list)
                or not allowed_values
                or any(not isinstance(value, str) or not value for value in allowed_values)
                or len(set(allowed_values)) != len(allowed_values)
            ):
                problems.append(f"{context}.allowed_values must be unique non-empty strings")

        if not isinstance(zoho, dict):
            problems.append(f"{context}.zoho must be an object")
            continue
        unknown_zoho_keys = sorted(set(zoho) - ZOHO_KEYS)
        if unknown_zoho_keys:
            problems.append(
                f"{context}.zoho: unknown properties: "
                + ", ".join(unknown_zoho_keys)
            )
        missing_zoho_keys = sorted(REQUIRED_ZOHO_KEYS - set(zoho))
        if missing_zoho_keys:
            problems.append(
                f"{context}.zoho: missing properties: "
                + ", ".join(missing_zoho_keys)
            )
        ui_type = zoho.get("ui_type")
        native_type = zoho.get("expected_native_type")
        type_status = zoho.get("type_status")
        evidence_id = zoho.get("evidence_id")
        api_name = zoho.get("api_name")

        if classification == "system" and ui_type is not None:
            problems.append(f"{context}: system fields must not use the custom-field menu")
        if classification == "custom" and ui_type not in REQUIRED_CUSTOM_TYPES:
            problems.append(f"{context}: custom field has unsupported Zoho type {ui_type!r}")
        if classification == "custom" and type_status not in {
            "design_decision",
            "tenant_api_verified",
        }:
            problems.append(
                f"{context}: custom type must be a design_decision or tenant_api_verified"
            )
        if classification == "system" and type_status == "design_decision":
            problems.append(f"{context}: system field type cannot be a design_decision")
        if native_type not in ALLOWED_NATIVE_TYPES:
            problems.append(f"{context}: unsupported expected native type {native_type!r}")
        if type_status not in ALLOWED_TYPE_STATUSES:
            problems.append(f"{context}: invalid Zoho type_status")
        if evidence_id not in sources:
            problems.append(f"{context}: unknown evidence_id {evidence_id!r}")
        if api_name is not None and type_status != "tenant_api_verified":
            problems.append(
                f"{context}: Zoho api_name cannot be populated before tenant API verification"
            )
        if type_status == "tenant_api_verified":
            if not isinstance(api_name, str) or not re.fullmatch(
                r"[A-Za-z][A-Za-z0-9_]*", api_name
            ):
                problems.append(
                    f"{context}: tenant-verified Zoho api_name must be a non-empty API identifier"
                )
            if evidence_id != "zoho-metadata-api":
                problems.append(
                    f"{context}: tenant-verified type must cite zoho-metadata-api"
                )
        if native_type == "Unknown" and type_status != "tenant_api_required":
            problems.append(f"{context}: Unknown native type must require tenant API metadata")
        if type_status == "tenant_api_required" and status != "review_required":
            problems.append(f"{context}: tenant_api_required fields must be review_required")

        if not isinstance(crm, dict):
            problems.append(f"{context}.crm must be an object")
        else:
            unknown_crm_keys = sorted(set(crm) - CRM_KEYS)
            if unknown_crm_keys:
                problems.append(
                    f"{context}.crm: unknown properties: "
                    + ", ".join(unknown_crm_keys)
                )
            missing_crm_keys = sorted(CRM_KEYS - set(crm))
            if missing_crm_keys:
                problems.append(
                    f"{context}.crm: missing properties: "
                    + ", ".join(missing_crm_keys)
                )
            proposed_name = crm.get("proposed_api_name")
            api_status = crm.get("api_name_status")
            if crm.get("recommended_type") not in ALLOWED_CRM_TYPES:
                problems.append(f"{context}: unsupported CRM recommended_type")
            if api_status not in ALLOWED_CRM_API_STATUSES:
                problems.append(f"{context}: invalid CRM api_name_status")
            if proposed_name is not None and not re.fullmatch(
                r"[A-Za-z][A-Za-z0-9_]*", str(proposed_name)
            ):
                problems.append(f"{context}: proposed CRM API name is malformed")
            if api_status == "verified_live_mcp":
                if not isinstance(proposed_name, str) or not proposed_name:
                    problems.append(
                        f"{context}: verified_live_mcp CRM API name must be non-empty"
                    )
            elif proposed_name is not None and api_status not in {
                "proposed_unverified",
                "design_required",
            }:
                problems.append(
                    f"{context}: CRM API name must be null for status {api_status}"
                )
            if (
                classification == "system"
                and isinstance(label, str)
                and re.fullmatch(r"Party [AB](?: .+)?", label)
                and (
                    proposed_name is not None
                    or api_status != "do_not_create"
                )
            ):
                problems.append(
                    f"{context}: native {label} must not have a CRM mirror proposal"
                )

        canonical_id = field.get("canonical_id")
        if status == "deprecated_alias" and not canonical_id:
            problems.append(f"{context}: deprecated alias requires canonical_id")
        if canonical_id:
            if canonical_id not in id_set:
                problems.append(f"{context}: canonical_id does not exist: {canonical_id}")
            if canonical_id == field_id:
                problems.append(f"{context}: field cannot canonicalize to itself")

        aliases = field.get("aliases", [])
        if not isinstance(aliases, list):
            problems.append(f"{context}.aliases must be an array")
        else:
            if len(set(aliases)) != len(aliases):
                problems.append(f"{context}: aliases must be unique")
            for alias in aliases:
                if not isinstance(alias, str) or not alias.strip():
                    problems.append(f"{context}: aliases must be non-empty strings")
                    continue
                folded = alias.casefold()
                if folded in alias_labels and alias_labels[folded] != field_id:
                    problems.append(f"alias used by multiple fields: {alias}")
                alias_labels[folded] = field_id

        if field_id and ("postal_code" in field_id or "zip_code" in field_id):
            if field.get("portable_type") != "text":
                problems.append(f"{context}: postal/ZIP identifiers must be portable text")
            if isinstance(crm, dict) and crm.get("recommended_type") != "Single Line":
                problems.append(f"{context}: postal/ZIP identifiers must be CRM Single Line")
            if classification == "custom" and ui_type != "Text":
                problems.append(f"{context}: custom postal/ZIP identifiers must be Zoho Text")

        if field_id in {"lease_number", "storage_unit_number", "property_unit_number_snapshot"}:
            if field.get("portable_type") != "text" or ui_type != "Text":
                problems.append(f"{context}: identifiers must remain Text")

        if ui_type == "Dropdown" and not field.get("allowed_values"):
            problems.append(f"{context}: Dropdown fields require allowed_values")
        if ui_type == "Number" and zoho.get("allow_decimals") is not False:
            problems.append(f"{context}: current Number fields must disallow decimals")
        if ui_type == "Date" and field.get("portable_type") != "date":
            problems.append(f"{context}: Zoho Date must use portable date")
        if ui_type == "Currency" and field.get("portable_type") != "currency":
            problems.append(f"{context}: Zoho Currency must use portable currency")
        if ui_type == "Phone" and field.get("portable_type") != "phone":
            problems.append(f"{context}: Zoho Phone must use portable phone")
        if ui_type == "Email" and field.get("portable_type") != "email":
            problems.append(f"{context}: Zoho Email must use portable email")

    if label_evidence:
        represented_labels = set(labels)
        represented_labels.update(
            alias
            for field in fields
            if isinstance(field, dict)
            for alias in field.get("aliases", [])
            if isinstance(alias, str)
        )
        missing_evidence_labels = [
            label
            for label in USER_CONFIRMED_LIVE_LABELS
            if label not in represented_labels
        ]
        if missing_evidence_labels:
            problems.append(
                "user-confirmed live labels are not represented by a canonical "
                "field or alias: " + ", ".join(missing_evidence_labels)
            )

    by_id = {
        field.get("id"): field for field in fields if isinstance(field, dict)
    }
    by_label = {
        field.get("label"): field for field in fields if isinstance(field, dict)
    }
    for label, expected_type in REQUESTED_DESTINATION_TYPES.items():
        field = by_label.get(label, {})
        expected_portable_type = (
            "currency" if expected_type == "Currency" else "date"
        )
        expected_crm_type = expected_type
        if field.get("classification") != "custom":
            problems.append(f"{label} must be a custom Contracts destination")
        if field.get("zoho", {}).get("ui_type") != expected_type:
            problems.append(
                f"{label} must use the requested Zoho {expected_type} type"
            )
        if field.get("zoho", {}).get("expected_native_type") != expected_type:
            problems.append(
                f"{label} must retain expected native type {expected_type}"
            )
        if field.get("portable_type") != expected_portable_type:
            problems.append(
                f"{label} must use portable type {expected_portable_type}"
            )
        if field.get("zoho", {}).get("api_name") is not None:
            problems.append(
                f"{label} Contracts api_name must remain null until metadata verification"
            )
        if field.get("zoho", {}).get("type_status") != "design_decision":
            problems.append(
                f"{label} type must remain a design decision until metadata verification"
            )
        expected_status = (
            "review_required"
            if label in REVIEW_REQUIRED_DESTINATION_LABELS
            else "active"
        )
        if field.get("status") != expected_status:
            problems.append(
                f"{label} must remain {expected_status} until its governed "
                "deployment conditions are satisfied"
            )
        crm = field.get("crm", {})
        if crm.get("recommended_type") != expected_crm_type:
            problems.append(
                f"{label} must use CRM design type {expected_crm_type}"
            )
        if (
            label not in VERIFIED_CRM_API_CROSSWALK
            and label not in CRM_FIELDS_WITH_UNDEFINED_SEMANTICS
        ):
            problems.append(f"{label} lacks an explicit CRM crosswalk decision")

    for label, expected_api_name in VERIFIED_CRM_API_CROSSWALK.items():
        crm = by_label.get(label, {}).get("crm", {})
        if (
            crm.get("proposed_api_name") != expected_api_name
            or crm.get("api_name_status") != "verified_live_mcp"
        ):
            problems.append(
                f"{label} must use verified_live_mcp CRM API name {expected_api_name}"
            )

    for label in CRM_FIELDS_WITH_UNDEFINED_SEMANTICS:
        crm = by_label.get(label, {}).get("crm", {})
        if (
            crm.get("proposed_api_name") is not None
            or crm.get("api_name_status") != "do_not_create_until_defined"
        ):
            problems.append(
                f"{label} must remain unmapped until its CRM semantics are defined"
            )

    lease_number_crm = by_label.get("Lease Number", {}).get("crm", {})
    if (
        lease_number_crm.get("proposed_api_name") is not None
        or lease_number_crm.get("api_name_status")
        != "do_not_create_until_defined"
    ):
        problems.append(
            "Lease Number must remain unmapped until an approved auto-number "
            "prefix and format are defined"
        )

    tenant_only = {
        "party_a_time_zone_name",
        "party_b_time_zone_name",
        "party_a_time_zone",
        "party_b_time_zone",
        "renewal_notice_days_tenant",
    }
    for field_id in tenant_only:
        field = by_id.get(field_id, {})
        type_status = field.get("zoho", {}).get("type_status")
        if type_status == "tenant_api_required":
            if field.get("status") != "review_required":
                problems.append(f"{field_id} must remain blocked on tenant metadata")
        elif type_status == "tenant_api_verified":
            if field.get("status") != "active":
                problems.append(f"{field_id} must be active after tenant verification")
            if field.get("zoho", {}).get("expected_native_type") == "Unknown":
                problems.append(
                    f"{field_id} must record the resolved native type after tenant verification"
                )
        else:
            problems.append(
                f"{field_id} must be tenant_api_required or tenant_api_verified"
            )

    legacy_start = by_id.get("storage_term_starts_legacy", {})
    if legacy_start.get("canonical_id") != "storage_term_start_date":
        problems.append("Storage Term Starts must alias Storage Term Begins")
    lease_effective = by_id.get("lease_agreement_effective_date_custom", {})
    if lease_effective.get("canonical_id") != "agreement_effective_date":
        problems.append("Lease Agreement Effective Date must review against Agreement Date")
    party_b_jurisdiction = by_id.get("party_b_jurisdiction", {})
    if party_b_jurisdiction.get("status") != "review_required":
        problems.append("Party B Jurisdiction must remain unresolved")

    return problems


def _escape(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ").strip()


def _crm_display(field: dict[str, Any]) -> str:
    crm = field["crm"]
    name = crm.get("proposed_api_name")
    if name:
        qualifier = (
            "verified_live_mcp"
            if crm["api_name_status"] == "verified_live_mcp"
            else "proposed"
        )
        return f"{crm['recommended_type']} / `{name}` ({qualifier})"
    return f"{crm['recommended_type']} / {crm['api_name_status']}"


def render_markdown(registry: dict[str, Any]) -> str:
    """Render the checked-in operator view from canonical JSON."""

    fields = registry["fields"]
    system_fields = [field for field in fields if field["classification"] == "system"]
    custom_fields = [field for field in fields if field["classification"] == "custom"]
    sources = registry["official_sources"]
    label_evidence = registry["label_evidence"][0]

    lines = [
        "# Zoho Contracts Field Registry",
        "",
        "> **Status:** Sanitized technical source of truth for field definitions and cross-application mapping. It contains no contract values or tenant records and does not deploy fields to Zoho.",
        "",
        f"- **Registry:** `{registry['registry_id']}` v{registry['version']}",
        f"- **As of:** {registry['as_of_date']}",
        f"- **Inventory:** {len(system_fields)} system fields + {len(custom_fields)} custom fields = {len(fields)} total",
        "",
        "## Operating Rules",
        "",
        "- `contract-field-registry.json` is canonical; this Markdown file is generated and checked for drift.",
        "- Built-in system fields are platform-managed and are not forced into the custom-field type menu.",
        "- User-confirmed live labels are label-only evidence and cannot populate a Contracts `apiName`; authenticated metadata is required.",
        "- CRM API names marked `verified_live_mcp` are bounded to the governed 2026-07-24 production metadata readback. Other names remain unverified design targets.",
        "- `Base Rent Amount`, `Total Monthly Rent Amount`, and `Prorated Base Rent Amount` stay unmapped until their CRM semantics are explicitly defined.",
        "- Native Party A fields come from Organization Info and native Party B fields from counterparty/contact configuration; do not create CRM Lease mirrors.",
        "- CRM owns approved pre-authoring party, property, unit, and lease inputs. Zoho Contracts owns lifecycle fields and the resolved agreement snapshot.",
        "- Prefer one-way CRM-to-Contracts authoring. Executed document values are immutable snapshots.",
        "- Never commit live names, addresses, phone numbers, emails, amounts, record IDs, tokens, or merged contracts.",
        "",
        "## Label-Only Tenant Evidence",
        "",
        f"- **Evidence:** `{label_evidence['id']}`",
        f"- **Type:** `{label_evidence['evidence_type']}`",
        f"- **Confirmed:** {label_evidence['confirmed_on']}",
        f"- **Scope:** `{label_evidence['scope']}`",
        f"- **Contracts API names:** `{label_evidence['api_name_status']}`",
        f"- **Confirmed labels:** {len(label_evidence['labels'])}",
        "",
        "This evidence confirms display labels only. It does not verify Contracts API names, field IDs, data types, template publication, or deployability.",
        "",
    ]
    for label in label_evidence["labels"]:
        lines.append(f"- {label}")
    lines.extend(
        [
        "",
        "## Zoho Custom Field Types",
        "",
        "The tenant UI exposes: " + ", ".join(f"`{item}`" for item in registry["allowed_custom_types"]) + ".",
        "",
        "None of the current custom fields needs `Single Checkbox` or `Percent`. `Property State` uses `Dropdown`; identifiers and postal codes stay `Text`.",
        "",
        "## System Fields",
        "",
        "System-field types below are expected native/logical types from Zoho's published semantics. The authenticated `/allfields` metadata response remains controlling for exact tenant `apiName`, `metaType`, `dataType`, and `displayType`.",
        "",
        "| Field | Registry ID | Expected Zoho type | Portable / CRM design | Status | Validation / distinction |",
        "|---|---|---|---|---|---|",
        ]
    )
    for field in system_fields:
        lines.append(
            "| "
            + " | ".join(
                [
                    _escape(field["label"]),
                    f"`{field['id']}`",
                    _escape(field["zoho"]["expected_native_type"]),
                    _escape(f"{field['portable_type']} / {_crm_display(field)}"),
                    _escape(field["status"]),
                    _escape(field["validation"]),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Custom Fields",
            "",
            "These are the approved design types to use when configuring the custom fields. Existing tenant fields must still be reconciled through metadata before automation uses them.",
            "",
            "| Field | Registry ID | Zoho Contracts type | CRM design | Status | Validation / alias rule |",
            "|---|---|---|---|---|---|",
        ]
    )
    for field in custom_fields:
        lines.append(
            "| "
            + " | ".join(
                [
                    _escape(field["label"]),
                    f"`{field['id']}`",
                    _escape(field["zoho"]["ui_type"]),
                    _escape(_crm_display(field)),
                    _escape(field["status"]),
                    _escape(field["validation"]),
                ]
            )
            + " |"
        )

    review_fields = [field for field in fields if field["status"] == "review_required"]
    lines.extend(
        [
            "",
            "## Required Reconciliation Before Live Mapping",
            "",
        ]
    )
    for field in review_fields:
        lines.append(f"- **{field['label']}:** {field['validation']}")
    lines.extend(
        [
            "- **Storage Term Starts:** deprecated alias of `storage_term_start_date`; do not create or independently populate it.",
            "- **Party C/D:** this workflow maps them only to the verified Tenant 2 and Tenant 3 legal-name snapshots; do not reuse the labels for arbitrary party roles.",
            "",
            "## Tenant Metadata Verification",
            "",
            "1. Call `GET /api/v1/admin/contracttypes/{contract-type-api-name}/allfields` with `contracts.meta.READ`.",
            "2. Match by returned stable `apiName`, not display text.",
            "3. Record `metaType` (`1` system, `3` custom), `dataType`, and `displayType`.",
            "4. Query CRM fields with `GET /crm/v8/settings/fields?module=...`; confirm every `verified_live_mcp` crosswalk name still exists in the exact module/layout before deployment.",
            "5. Run the registry validator and sanitized merge tests before activating any sync.",
            "",
            "Zoho Contracts `dataType` codes: `1` Boolean, `2` Number, `3` String, `4` Date, `5` Index, `6` Text, `7` Currency, `8` Term, `9` Percent, `10` Phone, `11` Email.",
            "",
            "## Official References",
            "",
        ]
    )
    for source_id, source in sources.items():
        if source.startswith("https://"):
            lines.append(f"- [{source_id}]({source})")
    lines.extend(
        [
            "",
            "## Validation",
            "",
            "```powershell",
            "python src/zoho-contracts/scripts/validate_contract_field_registry.py",
            "python -m unittest discover -s src/zoho-contracts/tests -p 'test_*.py' -v",
            "```",
            "",
            "Merging this registry does not create, rename, or update any live Zoho field.",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--write-markdown",
        action="store_true",
        help="Regenerate the Markdown operator view after JSON validation.",
    )
    args = parser.parse_args(argv)

    try:
        registry = load_registry()
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print(f"Could not load field registry: {exc}")
        return 1

    problems = validate_registry(registry)
    if problems:
        print("Zoho Contracts field registry validation failed:\n")
        for problem in problems:
            print(f"- {problem}")
        return 1

    expected_markdown = render_markdown(registry)
    if args.write_markdown:
        MARKDOWN_PATH.write_text(expected_markdown, encoding="utf-8")
    else:
        try:
            actual_markdown = MARKDOWN_PATH.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            print(f"Could not read generated Markdown: {exc}")
            return 1
        if actual_markdown != expected_markdown:
            print(
                "Generated Markdown is out of date. Run "
                "python src/zoho-contracts/scripts/validate_contract_field_registry.py "
                "--write-markdown"
            )
            return 1

    print(
        "Zoho Contracts field registry passed: "
        f"{registry['record_counts']['system']} system + "
        f"{registry['record_counts']['custom']} custom = "
        f"{registry['record_counts']['total']} fields."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
