#!/usr/bin/env python3
"""Validate the governed GH Real Estate Zoho CRM per-module field catalogs."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HEX_COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")
API_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
VERIFIED_FIELD_STATUSES = {
    "verified_repo_runtime",
    "verified_repo_live_integration",
}
VERIFIED_MODULE_STATUSES = {
    "verified_standard_zoho",
    "verified_standard_zoho_and_repo_runtime",
    "verified_repo_live_integration",
}
REQUIRED_CURRENT_MODULES = {
    "Leads",
    "Zillow Intake Events",
    "Properties",
    "Contacts",
    "Rental Applications",
    "Units",
    "Leases",
    "Maintenance Requests",
    "Inspections",
    "Notices",
    "Vendors",
    "Tasks",
    "Equipment",
    "Lease Documents / Addenda",
}
KNOWN_SOURCE_IDS = {
    "REPO_ZILLOW_FIELD_MAP",
    "REPO_ZILLOW_RUNTIME_DEFAULTS",
    "REPO_UNIT_ROUTING",
    "MATRIX_2026-07-08",
    "SETUP_SPEC",
}
REQUIRED_COLUMNS = {
    "module_display_label",
    "module_type",
    "module_api_name",
    "module_api_name_status",
    "field_label",
    "field_type",
    "api_name",
    "api_name_status",
    "proposed_api_name",
    "disposition",
    "required",
    "help_text",
    "picklist_scope",
    "picklist_values_and_colors",
    "phase",
    "section",
    "notes",
    "source_ids",
}


def parse_args() -> argparse.Namespace:
    default_path = (
        Path(__file__).resolve().parents[1]
        / "field-maps"
        / "crm-module-fields"
    )
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "catalog_dir",
        nargs="?",
        type=Path,
        default=default_path,
        help=f"Directory containing per-module CSV files (default: {default_path})",
    )
    return parser.parse_args()


def validate_api_name(value: str, path: str, errors: list[str]) -> None:
    if value and not API_NAME_RE.fullmatch(value):
        errors.append(f"{path}: invalid Zoho API-name format: {value!r}")


def parse_choices(value: str, path: str, errors: list[str]) -> list[tuple[str, str]]:
    if not value.strip():
        return []
    choices: list[tuple[str, str]] = []
    seen: set[str] = set()
    for index, raw in enumerate(value.split(" | "), start=1):
        item = raw.strip()
        if "=" not in item:
            errors.append(f"{path}: choice {index} must use Label=#RRGGBB")
            continue
        label, color = item.rsplit("=", 1)
        label = label.strip()
        color = color.strip()
        if not label:
            errors.append(f"{path}: choice {index} has an empty label")
        folded = label.casefold()
        if folded in seen:
            errors.append(f"{path}: duplicate choice label {label!r}")
        seen.add(folded)
        if not HEX_COLOR_RE.fullmatch(color):
            errors.append(f"{path}: choice {label!r} has invalid color {color!r}")
        choices.append((label, color.upper()))
    return choices


def load_catalog_dir(path: Path) -> list[tuple[Path, dict[str, str]]]:
    if not path.is_dir():
        raise ValueError(f"catalog directory not found: {path}")
    csv_paths = sorted(path.glob("*.csv"))
    if not csv_paths:
        raise ValueError(f"no module CSV files found in: {path}")

    loaded: list[tuple[Path, dict[str, str]]] = []
    for csv_path in csv_paths:
        try:
            with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle)
                headers = reader.fieldnames or []
                missing = sorted(REQUIRED_COLUMNS.difference(headers))
                if missing:
                    raise ValueError(
                        f"{csv_path}: missing required columns: {', '.join(missing)}"
                    )
                rows = [
                    {key: (value or "").strip() for key, value in row.items()}
                    for row in reader
                ]
        except csv.Error as exc:
            raise ValueError(f"{csv_path}: invalid CSV: {exc}") from exc
        if not rows:
            raise ValueError(f"{csv_path}: must contain at least one field row")
        labels = {row["module_display_label"] for row in rows}
        if len(labels) != 1:
            raise ValueError(
                f"{csv_path}: expected exactly one module label, found {sorted(labels)}"
            )
        loaded.extend((csv_path, row) for row in rows)
    return loaded


def validate_rows(rows_with_paths: list[tuple[Path, dict[str, str]]]) -> list[str]:
    errors: list[str] = []
    module_facts: dict[str, tuple[str, str, str]] = {}
    module_display_names: set[str] = set()
    field_labels: dict[str, set[str]] = defaultdict(set)
    verified_api_names: dict[str, set[str]] = defaultdict(set)
    row_numbers: dict[Path, int] = defaultdict(lambda: 1)

    for csv_path, row in rows_with_paths:
        row_numbers[csv_path] += 1
        path = f"{csv_path.name}:row {row_numbers[csv_path]}"
        module_label = row["module_display_label"]
        module_type = row["module_type"]
        module_api_name = row["module_api_name"]
        module_api_status = row["module_api_name_status"]
        field_label = row["field_label"]
        field_type = row["field_type"]
        api_name = row["api_name"]
        api_status = row["api_name_status"]
        proposed_api_name = row["proposed_api_name"]
        disposition = row["disposition"]
        help_text = row["help_text"]
        source_ids = [item for item in row["source_ids"].split(",") if item]

        for column, value in (
            ("module_display_label", module_label),
            ("module_type", module_type),
            ("module_api_name_status", module_api_status),
            ("field_label", field_label),
            ("field_type", field_type),
            ("api_name_status", api_status),
            ("disposition", disposition),
            ("help_text", help_text),
        ):
            if not value:
                errors.append(f"{path}.{column}: required value is blank")

        if not source_ids:
            errors.append(f"{path}.source_ids: at least one source ID is required")
        for source_id in source_ids:
            if source_id not in KNOWN_SOURCE_IDS:
                errors.append(f"{path}.source_ids: unknown source ID {source_id!r}")

        if len(help_text) > 255:
            errors.append(
                f"{path}.help_text: {len(help_text)} characters exceeds GH maximum 255"
            )

        validate_api_name(module_api_name, f"{path}.module_api_name", errors)
        validate_api_name(api_name, f"{path}.api_name", errors)
        validate_api_name(proposed_api_name, f"{path}.proposed_api_name", errors)

        if module_api_status in VERIFIED_MODULE_STATUSES and not module_api_name:
            errors.append(f"{path}: verified module status requires module_api_name")
        if api_status in VERIFIED_FIELD_STATUSES and not api_name:
            errors.append(f"{path}: verified field status requires api_name")
        if api_status == "proposed_unverified" and not proposed_api_name:
            errors.append(f"{path}: proposed_unverified requires proposed_api_name")
        if api_status == "not_proposed_unverified" and api_name:
            errors.append(f"{path}: not_proposed_unverified must not claim api_name")

        module_key = module_label.casefold()
        module_display_names.add(module_label)
        module_fact = (module_type, module_api_name, module_api_status)
        previous_fact = module_facts.setdefault(module_key, module_fact)
        if previous_fact != module_fact:
            errors.append(f"{path}: module metadata conflicts with earlier rows")

        folded_label = field_label.casefold()
        if folded_label in field_labels[module_key]:
            errors.append(f"{path}.field_label: duplicate {field_label!r} in module")
        field_labels[module_key].add(folded_label)

        if api_status in VERIFIED_FIELD_STATUSES and api_name:
            folded_api = api_name.casefold()
            if folded_api in verified_api_names[module_key]:
                errors.append(
                    f"{path}.api_name: duplicate verified API name {api_name!r} in module"
                )
            verified_api_names[module_key].add(folded_api)

        choices = parse_choices(
            row["picklist_values_and_colors"],
            f"{path}.picklist_values_and_colors",
            errors,
        )
        is_choice_type = "pick" in field_type.casefold() or "multi-select" in field_type.casefold()
        if is_choice_type and not choices:
            errors.append(f"{path}: choice field is missing choices and #RRGGBB colors")
        if choices and not row["picklist_scope"]:
            errors.append(f"{path}: choice field is missing picklist_scope")

        if row["required"].casefold() not in {"true", "false"}:
            errors.append(f"{path}.required: expected true or false")

    missing_modules = sorted(REQUIRED_CURRENT_MODULES.difference(module_display_names))
    if missing_modules:
        errors.append(f"catalog is missing current modules: {', '.join(missing_modules)}")
    return errors


def main() -> int:
    args = parse_args()
    try:
        rows_with_paths = load_catalog_dir(args.catalog_dir)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    errors = validate_rows(rows_with_paths)
    if errors:
        print(
            f"CRM field catalog validation failed with {len(errors)} error(s):",
            file=sys.stderr,
        )
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    rows = [row for _, row in rows_with_paths]
    module_count = len({row["module_display_label"].casefold() for row in rows})
    picklist_count = sum(bool(row["picklist_values_and_colors"]) for row in rows)
    api_status_counts = Counter(row["api_name_status"] for row in rows)
    print(
        "CRM field catalog valid: "
        f"{module_count} modules, {len(rows)} fields, {picklist_count} choice fields."
    )
    print("Field API-name statuses:")
    for status, count in sorted(api_status_counts.items()):
        print(f"- {status}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
