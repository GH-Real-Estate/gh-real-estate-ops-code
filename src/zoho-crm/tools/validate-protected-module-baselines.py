#!/usr/bin/env python3
"""Validate checksum-controlled, sanitized baselines for protected CRM modules."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


CRM_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASELINE_DIR = CRM_ROOT / "field-maps" / "protected-modules"
CATALOG_DIR = CRM_ROOT / "field-maps" / "crm-module-fields"
POLICY_FILENAME = "protected-module-policy.json"
EXPECTED_POLICY_SHA256 = (
    "75989b3ebeaa8d019b877d2c24a61a3415e03f9dac08ae8c3d72b818f70d420f"
)
API_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
EQUIPMENT_HISTORICAL_STATUS = "historical_target_only_non_deployable"
EQUIPMENT_HISTORICAL_PHASE = "Historical Reference Only"
LEADS_BLOCKED_PHASE = "Protected / Blocked"
LEADS_NONDEPLOYABLE_API_STATUSES = {
    "blocked_protected_module",
    "prohibited_current_design",
    "superseded_by_verified_repo_field",
}

# These digests cover normalized JSON content, not formatting or line endings.
# Updating one requires an expressly authorized protected-baseline refresh.
EXPECTED_BASELINES = {
    "leads.json": {
        "display_label": "Leads",
        "api_name": "Leads",
        "field_count": 82,
        "layout_count": 1,
        "section_count": 10,
        "sha256": "7ab966c12f7598661073f1b849daace2fb183a39956acb500a5ff298d1fd1ad5",
    },
    "property-assets.json": {
        "display_label": "Property Assets",
        "api_name": "Equipment",
        "field_count": 106,
        "layout_count": 1,
        "section_count": 13,
        "sha256": "a31d330538bfde3a15b2d9f3e4b91db946bcf5f452e1e6c008f4f6dbaf12d90e",
    },
    "pets.json": {
        "display_label": "Pets",
        "api_name": "Pets",
        "field_count": 44,
        "layout_count": 1,
        "section_count": 7,
        "sha256": "987ea1c89b1c491fefef6786fba411713a2a8dbb0e5860d852f8521ec0a55cbc",
    },
    "vehicles.json": {
        "display_label": "Vehicles",
        "api_name": "Tenant_Vehicles",
        "field_count": 29,
        "layout_count": 1,
        "section_count": 5,
        "sha256": "c05838f11577039ac39522b7a0098ee1674d60ca423b1a62a4fc886116b58873",
    },
}

FORBIDDEN_METADATA_KEYS = {
    "id",
    "profiles",
    "created_by",
    "modified_by",
    "created_time",
    "modified_time",
    "section_id",
    "layout_associations",
    "access_token",
    "refresh_token",
    "password",
    "secret",
    "records",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "baseline_dir",
        nargs="?",
        type=Path,
        default=DEFAULT_BASELINE_DIR,
        help=f"Protected baseline directory (default: {DEFAULT_BASELINE_DIR})",
    )
    return parser.parse_args()


def canonical_sha256(document: Any) -> str:
    """Return a stable digest that ignores JSON formatting and line endings."""

    payload = json.dumps(
        document,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def load_json_object(path: Path) -> dict[str, Any]:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"required file is missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path}: invalid JSON: {exc}") from exc
    if not isinstance(document, dict):
        raise ValueError(f"{path}: top-level JSON value must be an object")
    return document


def load_catalog_rows(filename: str) -> list[dict[str, str]]:
    """Load a governed module CSV with the columns needed by protection gates."""

    path = CATALOG_DIR / filename
    required_columns = {
        "module_display_label",
        "module_type",
        "module_api_name",
        "module_api_name_status",
        "field_label",
        "api_name",
        "api_name_status",
        "proposed_api_name",
        "disposition",
        "phase",
        "notes",
        "source_ids",
    }
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            headers = set(reader.fieldnames or [])
            missing = sorted(required_columns.difference(headers))
            if missing:
                raise ValueError(
                    f"{filename}: missing required columns: {', '.join(missing)}"
                )
            rows: list[dict[str, str]] = []
            for row_number, row in enumerate(reader, start=2):
                if None in row or any(value is None for value in row.values()):
                    raise ValueError(
                        f"{filename}: row {row_number} has malformed CSV columns"
                    )
                rows.append(
                    {key: (value or "").strip() for key, value in row.items()}
                )
    except (OSError, csv.Error) as exc:
        raise ValueError(f"{filename}: catalog could not be read: {exc}") from exc
    if not rows:
        raise ValueError(f"{filename}: catalog must contain at least one row")
    return rows


def walk_keys(value: Any, path: str = "$") -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            found.append((child_path, key))
            found.extend(walk_keys(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(walk_keys(child, f"{path}[{index}]"))
    return found


def validate_sanitization(
    snapshot: dict[str, Any],
    filename: str,
    errors: list[str],
) -> None:
    allowed_governance_ids = {"$.baseline_id", "$.evidence.source_id"}
    for path, key in walk_keys(snapshot):
        folded = key.casefold()
        if (
            folded in FORBIDDEN_METADATA_KEYS
            or (folded.endswith("_id") and path not in allowed_governance_ids)
        ):
            errors.append(
                f"{filename}: forbidden identifier, actor, record, or secret key at {path}"
            )


def section_count(snapshot: dict[str, Any]) -> int:
    layouts = snapshot.get("layouts")
    if not isinstance(layouts, list):
        return 0
    return sum(
        len(layout.get("sections", []))
        for layout in layouts
        if isinstance(layout, dict) and isinstance(layout.get("sections"), list)
    )


def validate_snapshot(
    filename: str,
    snapshot: dict[str, Any],
    expected: dict[str, Any],
    errors: list[str],
) -> None:
    path = f"protected baseline {filename}"
    organization = snapshot.get("organization_gate")
    if organization != {
        "company_name": "GH Real Estate",
        "environment_type": "production",
    }:
        errors.append(f"{path}: organization gate must be GH Real Estate / production")

    evidence = snapshot.get("evidence")
    if not isinstance(evidence, dict):
        errors.append(f"{path}: evidence object is missing")
    else:
        expected_evidence = {
            "connector": "gh_zoho_crm_audit",
            "source_id": "LIVE_CRM_MCP_2026-07-24",
            "record_data_included": False,
            "metadata_ids_included": False,
        }
        for key, value in expected_evidence.items():
            if evidence.get(key) != value:
                errors.append(f"{path}: evidence.{key} must be {value!r}")

    protection = snapshot.get("protection")
    if not isinstance(protection, dict):
        errors.append(f"{path}: protection object is missing")
    else:
        if protection.get("mutation_policy") != "deny":
            errors.append(f"{path}: mutation_policy must be deny")
        if protection.get("authorized_baseline_refresh_required") is not True:
            errors.append(f"{path}: authorized baseline refresh must be required")

    module = snapshot.get("module")
    if not isinstance(module, dict):
        errors.append(f"{path}: module object is missing")
    else:
        if module.get("plural_label") != expected["display_label"]:
            errors.append(
                f"{path}: expected display label {expected['display_label']!r}"
            )
        if module.get("api_name") != expected["api_name"]:
            errors.append(f"{path}: expected API name {expected['api_name']!r}")

    fields = snapshot.get("fields")
    if not isinstance(fields, list):
        errors.append(f"{path}: fields must be an array")
        fields = []
    if snapshot.get("field_count") != expected["field_count"]:
        errors.append(
            f"{path}: expected field_count {expected['field_count']}, "
            f"found {snapshot.get('field_count')!r}"
        )
    if len(fields) != expected["field_count"]:
        errors.append(
            f"{path}: expected {expected['field_count']} field objects, "
            f"found {len(fields)}"
        )

    api_names: list[str] = []
    labels: list[str] = []
    for index, field in enumerate(fields):
        field_path = f"{path}.fields[{index}]"
        if not isinstance(field, dict):
            errors.append(f"{field_path}: expected an object")
            continue
        api_name = field.get("api_name")
        field_label = field.get("field_label")
        data_type = field.get("data_type")
        if not isinstance(api_name, str) or not API_NAME_RE.fullmatch(api_name):
            errors.append(f"{field_path}.api_name: invalid or missing API name")
        else:
            api_names.append(api_name.casefold())
        if not isinstance(field_label, str) or not field_label.strip():
            errors.append(f"{field_path}.field_label: required value is blank")
        else:
            labels.append(field_label.casefold())
        if not isinstance(data_type, str) or not data_type.strip():
            errors.append(f"{field_path}.data_type: required value is blank")

    duplicate_apis = sorted(
        name for name, count in Counter(api_names).items() if count > 1
    )
    duplicate_labels = sorted(
        label for label, count in Counter(labels).items() if count > 1
    )
    if duplicate_apis:
        errors.append(f"{path}: duplicate field API names: {', '.join(duplicate_apis)}")
    if duplicate_labels:
        errors.append(f"{path}: duplicate field labels: {', '.join(duplicate_labels)}")

    layouts = snapshot.get("layouts")
    if not isinstance(layouts, list):
        errors.append(f"{path}: layouts must be an array")
        layouts = []
    if snapshot.get("layout_count") != expected["layout_count"]:
        errors.append(
            f"{path}: expected layout_count {expected['layout_count']}, "
            f"found {snapshot.get('layout_count')!r}"
        )
    if len(layouts) != expected["layout_count"]:
        errors.append(
            f"{path}: expected {expected['layout_count']} layout objects, "
            f"found {len(layouts)}"
        )

    actual_section_count = section_count(snapshot)
    if actual_section_count != expected["section_count"]:
        errors.append(
            f"{path}: expected {expected['section_count']} layout sections, "
            f"found {actual_section_count}"
        )

    known_api_names = set(api_names)
    for layout_index, layout in enumerate(layouts):
        if not isinstance(layout, dict):
            errors.append(f"{path}.layouts[{layout_index}]: expected an object")
            continue
        sections = layout.get("sections")
        if not isinstance(sections, list):
            errors.append(
                f"{path}.layouts[{layout_index}].sections: expected an array"
            )
            continue
        for section_index, section in enumerate(sections):
            if not isinstance(section, dict):
                errors.append(
                    f"{path}.layouts[{layout_index}].sections[{section_index}]: "
                    "expected an object"
                )
                continue
            placements = section.get("fields")
            if not isinstance(placements, list):
                errors.append(
                    f"{path}.layouts[{layout_index}].sections[{section_index}]."
                    "fields: expected an array"
                )
                continue
            for placement in placements:
                if not isinstance(placement, dict):
                    errors.append(
                        f"{path}.layouts[{layout_index}].sections[{section_index}]."
                        "fields: every placement must be an object"
                    )
                    continue
                api_name = placement.get("api_name")
                if not isinstance(api_name, str) or not API_NAME_RE.fullmatch(api_name):
                    errors.append(
                        f"{path}: layout placement has an invalid or missing API name"
                    )
                elif api_name.casefold() not in known_api_names:
                    errors.append(
                        f"{path}: layout placement references unknown field "
                        f"{api_name!r}"
                    )

    validate_sanitization(snapshot, filename, errors)
    digest = canonical_sha256(snapshot)
    if digest != expected["sha256"]:
        errors.append(
            f"{path}: canonical metadata drifted "
            f"(expected {expected['sha256']}, found {digest})"
        )


def validate_leads_catalog_rows(
    live_api_names: set[str],
    rows: list[dict[str, str]],
    errors: list[str],
) -> None:
    missing = sorted(
        {
            row.get("api_name", "").strip()
            for row in rows
            if row.get("api_name", "").strip()
        }.difference(live_api_names)
    )
    if missing:
        errors.append(
            "Leads protected baseline is missing repository/runtime API names: "
            + ", ".join(missing)
        )

    for row_number, row in enumerate(rows, start=2):
        proposed_api_name = row.get("proposed_api_name", "").strip()
        if not proposed_api_name or proposed_api_name in live_api_names:
            continue

        path = (
            f"leads.csv:row {row_number} protected absent-live proposal "
            f"{proposed_api_name!r}"
        )
        if row.get("api_name_status") not in LEADS_NONDEPLOYABLE_API_STATUSES:
            errors.append(
                f"{path}: api_name_status must be a protected "
                "nondeployable classification"
            )
        if row.get("disposition") != "do_not_create":
            errors.append(f"{path}: disposition must be 'do_not_create'")
        if row.get("phase") != LEADS_BLOCKED_PHASE:
            errors.append(f"{path}: phase must be {LEADS_BLOCKED_PHASE!r}")
        notes = row.get("notes", "")
        if (
            "Protected Leads no-write boundary" not in notes
            or "do not create or deploy" not in notes.casefold()
        ):
            errors.append(
                f"{path}: notes must state the protected no-write and "
                "do-not-create/deploy boundary"
            )
        source_ids = {
            item.strip()
            for item in row.get("source_ids", "").split(",")
            if item.strip()
        }
        if "LIVE_CRM_MCP_2026-07-24" not in source_ids:
            errors.append(
                f"{path}: source_ids must include LIVE_CRM_MCP_2026-07-24"
            )


def validate_leads_catalog_contract(
    snapshots: dict[str, dict[str, Any]],
    errors: list[str],
) -> None:
    leads = snapshots.get("leads.json", {})
    live_api_names = {
        field.get("api_name")
        for field in leads.get("fields", [])
        if isinstance(field, dict) and isinstance(field.get("api_name"), str)
    }
    try:
        rows = load_catalog_rows("leads.csv")
    except ValueError as exc:
        errors.append(f"Leads runtime catalog could not be read: {exc}")
        return
    validate_leads_catalog_rows(live_api_names, rows, errors)


def validate_equipment_catalog_rows(
    rows: list[dict[str, str]],
    errors: list[str],
) -> None:
    """Prevent the historical Equipment target from authorizing live writes."""

    expected_values = {
        "module_display_label": "Equipment",
        "module_type": "custom",
        "module_api_name_status": EQUIPMENT_HISTORICAL_STATUS,
        "api_name_status": EQUIPMENT_HISTORICAL_STATUS,
        "disposition": "do_not_create",
        "phase": EQUIPMENT_HISTORICAL_PHASE,
    }
    for row_number, row in enumerate(rows, start=2):
        path = f"equipment.csv:row {row_number} historical-only guard"
        for column, expected in expected_values.items():
            if row.get(column) != expected:
                errors.append(
                    f"{path}.{column}: expected {expected!r}, "
                    f"found {row.get(column)!r}"
                )
        if row.get("module_api_name"):
            errors.append(
                f"{path}.module_api_name: historical catalog must not bind "
                "to live API Equipment"
            )
        if row.get("api_name"):
            errors.append(
                f"{path}.api_name: historical catalog must not claim a live "
                "field API"
            )
        if not row.get("proposed_api_name"):
            errors.append(
                f"{path}.proposed_api_name: historical target identifier is "
                "required for audit context"
            )
        notes = row.get("notes", "")
        if (
            "Historical target-design evidence only" not in notes
            or "this row never authorizes a live write" not in notes
        ):
            errors.append(
                f"{path}.notes: expected explicit historical non-write boundary"
            )


def validate_equipment_catalog_contract(errors: list[str]) -> None:
    try:
        rows = load_catalog_rows("equipment.csv")
    except ValueError as exc:
        errors.append(f"Historical Equipment catalog could not be read: {exc}")
        return
    validate_equipment_catalog_rows(rows, errors)


def validate_documents(
    policy: dict[str, Any],
    snapshots: dict[str, dict[str, Any]],
) -> list[str]:
    errors: list[str] = []

    if canonical_sha256(policy) != EXPECTED_POLICY_SHA256:
        errors.append("protected-module policy drifted from its reviewed checksum")
    if policy.get("organization_gate") != {
        "company_name": "GH Real Estate",
        "environment_type": "production",
    }:
        errors.append("protected-module policy has the wrong organization gate")
    if policy.get("default_mutation_policy") != "deny":
        errors.append("protected-module policy must default to deny")
    if policy.get("authorized_baseline_refresh_required") is not True:
        errors.append("protected-module policy must require an authorized refresh")

    baseline_rows = policy.get("baselines")
    if not isinstance(baseline_rows, list):
        errors.append("protected-module policy baselines must be an array")
        baseline_rows = []
    rows_by_filename = {
        row.get("filename"): row
        for row in baseline_rows
        if isinstance(row, dict) and isinstance(row.get("filename"), str)
    }
    if set(rows_by_filename) != set(EXPECTED_BASELINES):
        errors.append("protected-module policy does not list the exact baseline files")
    if set(snapshots) != set(EXPECTED_BASELINES):
        errors.append("protected-module baseline directory has a missing or extra JSON file")

    for filename, expected in EXPECTED_BASELINES.items():
        row = rows_by_filename.get(filename)
        if row is None:
            continue
        expected_policy_values = {
            "display_label": expected["display_label"],
            "module_api_name": expected["api_name"],
            "field_count": expected["field_count"],
            "layout_count": expected["layout_count"],
            "section_count": expected["section_count"],
            "canonical_sha256": expected["sha256"],
        }
        for key, value in expected_policy_values.items():
            if row.get(key) != value:
                errors.append(
                    f"protected-module policy {filename}.{key}: "
                    f"expected {value!r}, found {row.get(key)!r}"
                )

        snapshot = snapshots.get(filename)
        if snapshot is not None:
            validate_snapshot(filename, snapshot, expected, errors)

    guards = policy.get("historical_catalog_guards")
    equipment_guard = (
        guards[0]
        if isinstance(guards, list) and len(guards) == 1 and isinstance(guards[0], dict)
        else {}
    )
    expected_equipment_guard = {
        "path": "src/zoho-crm/field-maps/crm-module-fields/equipment.csv",
        "live_module_api_name": "Equipment",
        "live_display_label": "Property Assets",
        "catalog_role": "historical_target_design_only",
        "authorizes_live_writes": False,
    }
    if any(
        equipment_guard.get(key) != value
        for key, value in expected_equipment_guard.items()
    ):
        errors.append(
            "historical equipment catalog must not authorize Property Assets writes"
        )

    validate_leads_catalog_contract(snapshots, errors)
    validate_equipment_catalog_contract(errors)
    return errors


def load_repository_documents(
    baseline_dir: Path,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    if not baseline_dir.is_dir():
        raise ValueError(f"protected baseline directory not found: {baseline_dir}")
    policy = load_json_object(baseline_dir / POLICY_FILENAME)
    snapshot_paths = sorted(
        path
        for path in baseline_dir.glob("*.json")
        if path.name != POLICY_FILENAME
    )
    snapshots = {path.name: load_json_object(path) for path in snapshot_paths}
    return policy, snapshots


def main() -> int:
    args = parse_args()
    try:
        policy, snapshots = load_repository_documents(args.baseline_dir)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    errors = validate_documents(policy, snapshots)
    if errors:
        print(
            f"Protected CRM baseline validation failed with {len(errors)} error(s):",
            file=sys.stderr,
        )
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        "Protected CRM baselines valid: "
        f"{len(snapshots)} modules, "
        f"{sum(snapshot['field_count'] for snapshot in snapshots.values())} fields, "
        f"{sum(section_count(snapshot) for snapshot in snapshots.values())} sections."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
