#!/usr/bin/env python3
"""Validate the governed GH Real Estate Zoho CRM per-module field catalogs."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HEX_COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")
API_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
VERIFIED_FIELD_STATUSES = {
    "verified_live_mcp",
    "verified_repo_runtime",
    "verified_repo_live_integration",
}
VERIFIED_MODULE_STATUSES = {
    "verified_live_mcp",
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
    "LIVE_CRM_MCP_2026-07-24",
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
GOVERNED_LIVE_SNAPSHOT_COUNT = 75
GOVERNED_LIVE_SNAPSHOT_SHA256 = (
    "72a2c456f71665d10a7d5dcdc0d50a76afebefecde2ea5b5c2c77bf7dca0f91a"
)

# Immutable production readback captured on 2026-07-24. These entries are
# intentionally explicit: plausible API-name edits must not silently rewrite
# the repository's record of fields already created or reused in live CRM.
DEALS_CREATED_LIVE_MANIFEST = (
    ("Co-Applicant 1", "Co_Applicant_1", "Rental Application Information"),
    ("Co-Applicant 2", "Co_Applicant_2", "Rental Application Information"),
    ("Source Lead", "Source_Lead", "Rental Application Information"),
    ("Unit", "Unit", "Rental Application Information"),
    (
        "Application Received At",
        "Application_Received_At",
        "Rental Application Information",
    ),
    ("Addenda Required", "Addenda_Required", "Rental Application Information"),
    (
        "Approved Lease Commencement Date",
        "Approved_Lease_Commencement_Date",
        "Rental Application Information",
    ),
    (
        "Approved Lease Term End Date",
        "Approved_Lease_Term_End_Date",
        "Rental Application Information",
    ),
    (
        "Approved Possession Date",
        "Approved_Possession_Date",
        "Rental Application Information",
    ),
    (
        "Approved Security Deposit",
        "Approved_Security_Deposit",
        "Rental Application Information",
    ),
    (
        "Attorney Review Required?",
        "Attorney_Review_Required",
        "Rental Application Information",
    ),
    ("Decision", "Decision", "Rental Application Information"),
    ("Decision Date", "Decision_Date", "Rental Application Information"),
    (
        "Nonstandard Terms?",
        "Nonstandard_Terms",
        "Rental Application Information",
    ),
    (
        "Nonstandard Terms Notes",
        "Nonstandard_Terms_Notes",
        "Rental Application Information",
    ),
)

LEASE_CREATED_LIVE_MANIFEST = (
    ("Agreement Date", "Agreement_Date", "Lease Dates"),
    (
        "Attorney Review Required?",
        "Attorney_Review_Required",
        "Contract Controls",
    ),
    ("Nonstandard Terms Notes", "Nonstandard_Terms_Notes", "Contract Controls"),
    ("Nonstandard Terms?", "Nonstandard_Terms", "Contract Controls"),
    ("Addenda Required", "Addenda_Required", "Contract Controls"),
    (
        "Total Monthly Pet Rent Amount",
        "Total_Monthly_Pet_Rent_Amount",
        "Monthly Charges",
    ),
    (
        "Next Total Monthly Rent Due Date",
        "Next_Total_Monthly_Rent_Due_Date",
        "Monthly Charges",
    ),
    (
        "Base Storage Unit Rent Amount",
        "Base_Storage_Unit_Rent_Amount",
        "Monthly Charges",
    ),
    (
        "Total Monthly Storage Rent Amount",
        "Total_Monthly_Storage_Rent_Amount",
        "Monthly Charges",
    ),
    (
        "Total Due Before Possession",
        "Total_Due_Before_Possession",
        "Initial Amounts",
    ),
    (
        "Prorated Rent Start Date",
        "Prorated_Rent_Start_Date",
        "Initial Amounts",
    ),
    (
        "Prorated Rent End Date",
        "Prorated_Rent_End_Date",
        "Initial Amounts",
    ),
    (
        "Prorated Pet Rent Amount",
        "Prorated_Pet_Rent_Amount",
        "Initial Amounts",
    ),
    (
        "Prorated Storage Unit Rent Amount",
        "Prorated_Storage_Unit_Rent_Amount",
        "Initial Amounts",
    ),
    (
        "Holding Deposit Credit Applied",
        "Holding_Deposit_Credit_Applied",
        "Initial Amounts",
    ),
    (
        "Tenant 2 Email Snapshot",
        "Tenant_2_Email_Snapshot",
        "Additional Tenants",
    ),
    (
        "Tenant 2 Legal Name Snapshot",
        "Tenant_2_Legal_Name_Snapshot",
        "Additional Tenants",
    ),
    (
        "Tenant 3 Email Snapshot",
        "Tenant_3_Email_Snapshot",
        "Additional Tenants",
    ),
    (
        "Tenant 3 Legal Name Snapshot",
        "Tenant_3_Legal_Name_Snapshot",
        "Additional Tenants",
    ),
    (
        "Pet Security Deposit Amount",
        "Pet_Security_Deposit_Amount",
        "Initial Amounts",
    ),
    (
        "Premises Apartment Number",
        "Premises_Apartment_Number",
        "Premises Snapshot",
    ),
    ("Premises City", "Premises_City", "Premises Snapshot"),
    ("Premises State", "Premises_State", "Premises Snapshot"),
    (
        "Premises Street Line 1",
        "Premises_Street_Line_1",
        "Premises Snapshot",
    ),
    ("Premises ZIP Code", "Premises_ZIP_Code", "Premises Snapshot"),
    ("Property", "Property", "Relationships"),
    ("Rental Application", "Rental_Application", "Relationships"),
    ("Tenant 2", "Tenant_2", "Relationships"),
    ("Tenant 3", "Tenant_3", "Relationships"),
    ("Unit", "Unit", "Relationships"),
    ("Lease Type", "Lease_Type", "Lease Identity and Status"),
    ("Previous Lease", "Previous_Lease", "Relationships"),
    ("Guarantor", "Guarantor", "Relationships"),
)

LEASE_REUSED_LIVE_MANIFEST = (
    ("Move-In Date", "Move_In_Date", "Lease Dates"),
    ("Lease Name", "Name", "Lease Identity and Status"),
    ("Lease Status", "Lease_Status", "Lease Identity and Status"),
    ("Security Deposit", "Security_Deposit", "Initial Amounts"),
    ("Tenant", "Tenant", "Relationships"),
    ("Lease End Date", "Lease_End_Date", "Lease Dates"),
    ("Lease Start Date", "Lease_Start_Date", "Lease Dates"),
)

LEASE_PLACED_LIVE_MANIFEST = (
    LEASE_CREATED_LIVE_MANIFEST + LEASE_REUSED_LIVE_MANIFEST
)
GOVERNED_LIVE_MANIFEST = (
    ("Rental Applications", "Deals", DEALS_CREATED_LIVE_MANIFEST),
    ("Leases", "Leases", LEASE_PLACED_LIVE_MANIFEST),
)

GOVERNED_LIVE_FIELD_TYPE_GROUPS = {
    "Rental Applications": {
        "Lookup": ("Co-Applicant 1", "Co-Applicant 2", "Source Lead", "Unit"),
        "Date/Time": ("Application Received At",),
        "Multi-Select Pick List": ("Addenda Required",),
        "Date": (
            "Approved Lease Commencement Date",
            "Approved Lease Term End Date",
            "Approved Possession Date",
            "Decision Date",
        ),
        "Currency": ("Approved Security Deposit",),
        "Checkbox": ("Attorney Review Required?", "Nonstandard Terms?"),
        "Pick List": ("Decision",),
        "Multi-Line": ("Nonstandard Terms Notes",),
    },
    "Leases": {
        "Date": (
            "Agreement Date",
            "Next Total Monthly Rent Due Date",
            "Prorated Rent Start Date",
            "Prorated Rent End Date",
            "Move-In Date",
            "Lease End Date",
            "Lease Start Date",
        ),
        "Checkbox": ("Attorney Review Required?", "Nonstandard Terms?"),
        "Multi-Line": ("Nonstandard Terms Notes",),
        "Multi-Select Pick List": ("Addenda Required",),
        "Currency": (
            "Total Monthly Pet Rent Amount",
            "Base Storage Unit Rent Amount",
            "Total Monthly Storage Rent Amount",
            "Total Due Before Possession",
            "Prorated Pet Rent Amount",
            "Prorated Storage Unit Rent Amount",
            "Holding Deposit Credit Applied",
            "Pet Security Deposit Amount",
            "Security Deposit",
        ),
        "Email": ("Tenant 2 Email Snapshot", "Tenant 3 Email Snapshot"),
        "Single Line": (
            "Tenant 2 Legal Name Snapshot",
            "Tenant 3 Legal Name Snapshot",
            "Premises Apartment Number",
            "Premises City",
            "Premises State",
            "Premises Street Line 1",
            "Premises ZIP Code",
        ),
        "Lookup": (
            "Property",
            "Rental Application",
            "Tenant 2",
            "Tenant 3",
            "Unit",
            "Previous Lease",
            "Guarantor",
            "Tenant",
        ),
        "Pick List": ("Lease Type", "Lease Status"),
        "Single Line / Module Name": ("Lease Name",),
    },
}
GOVERNED_LIVE_FIELD_TYPES = {
    (module_label, field_label): field_type
    for module_label, type_groups in GOVERNED_LIVE_FIELD_TYPE_GROUPS.items()
    for field_type, field_labels in type_groups.items()
    for field_label in field_labels
}

GOVERNED_LIVE_LOOKUP_TARGETS = {
    ("Rental Applications", "Co-Applicant 1"): "Contacts",
    ("Rental Applications", "Co-Applicant 2"): "Contacts",
    ("Rental Applications", "Source Lead"): "Leads",
    ("Rental Applications", "Unit"): "Units",
    ("Leases", "Property"): "Accounts",
    ("Leases", "Rental Application"): "Deals",
    ("Leases", "Tenant 2"): "Contacts",
    ("Leases", "Tenant 3"): "Contacts",
    ("Leases", "Unit"): "Units",
    ("Leases", "Previous Lease"): "Leases",
    ("Leases", "Guarantor"): "Contacts",
    ("Leases", "Tenant"): "Contacts",
}

ADDENDA_REQUIRED_CHOICES = (
    "Lead-Based Paint=#DB2777 | Ordinary Pet=#0F766E | Storage=#7C3AED | "
    "Guaranty/Cosigner=#0891B2 | Roommate=#4F46E5 | HOA/Handbook=#65A30D | "
    "Other=#EA580C"
)
GOVERNED_LIVE_CHOICES = {
    ("Rental Applications", "Decision"): (
        "Pending=#D97706 | Approved=#16A34A | "
        "Approved with Conditions=#EA580C | Denied=#DC2626 | "
        "Withdrawn=#6B7280 | Duplicate=#6B7280 | No Response=#6B7280"
    ),
    ("Rental Applications", "Addenda Required"): ADDENDA_REQUIRED_CHOICES,
    ("Leases", "Lease Type"): "Original=#2563EB | Renewal=#16A34A",
    ("Leases", "Addenda Required"): ADDENDA_REQUIRED_CHOICES,
    ("Leases", "Lease Status"): (
        "Contract in Progress=#7C3AED | Draft Lease Data=#AF38FA | "
        "Ready For Contract=#7C3AED | Signed - Future=#16A34A | "
        "Active=#16A34A | Contract Requested=#F8E199 | "
        "Contract Drafting=#90A9FD | Month-to-Month=#2563EB | "
        "Non-Renewing=#EA580C | Sent For Signature=#F5C72F | "
        "Signed - Pending Move-In=#F5C72F | Terminated=#DC2626 | "
        "Expired=#92400E | Lease Active=#67C480 | Moved Out=#6B7280 | "
        "Renewal Pending=#D97706 | Archived=#6B7280 | Notice Given=#EB4D4D | "
        "Ended=#666666 | Cancelled=#666666 | Draft=#2563EB"
    ),
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


def parse_choices(
    value: str,
    path: str,
    errors: list[str],
    *,
    allow_uncolored: bool = False,
) -> list[tuple[str, str]]:
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
        if color == "UNCOLORED" and allow_uncolored:
            pass
        elif not HEX_COLOR_RE.fullmatch(color):
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
                rows = []
                for row_number, row in enumerate(reader, start=2):
                    if None in row:
                        raise ValueError(
                            f"{csv_path}: row {row_number} has extra CSV columns"
                        )
                    if any(value is None for value in row.values()):
                        raise ValueError(
                            f"{csv_path}: row {row_number} has missing CSV columns"
                        )
                    rows.append(
                        {key: (value or "").strip() for key, value in row.items()}
                    )
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


def governed_live_snapshot_digest(
    rows_with_paths: list[tuple[Path, dict[str, str]]],
) -> tuple[int, str]:
    """Return a deterministic digest of every governed live-readback CSV fact."""

    columns = sorted(REQUIRED_COLUMNS)
    rows = [
        {column: row[column] for column in columns}
        for _, row in rows_with_paths
        if row["api_name_status"] == "verified_live_mcp"
    ]
    rows.sort(
        key=lambda row: (
            row["module_display_label"].casefold(),
            row["field_label"].casefold(),
            row["api_name"],
        )
    )
    payload = json.dumps(
        rows,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return len(rows), hashlib.sha256(payload).hexdigest()


def validate_governed_live_snapshot(
    rows_with_paths: list[tuple[Path, dict[str, str]]],
    errors: list[str],
) -> None:
    """Fail on any drift in the complete sanitized 2026-07-24 live snapshot."""

    count, digest = governed_live_snapshot_digest(rows_with_paths)
    if count != GOVERNED_LIVE_SNAPSHOT_COUNT:
        errors.append(
            "2026-07-24 governed live snapshot: expected "
            f"{GOVERNED_LIVE_SNAPSHOT_COUNT} verified_live_mcp rows, found {count}"
        )
    if digest != GOVERNED_LIVE_SNAPSHOT_SHA256:
        errors.append(
            "2026-07-24 governed live snapshot: canonical CSV facts drifted "
            f"(expected {GOVERNED_LIVE_SNAPSHOT_SHA256}, found {digest})"
        )


def validate_governed_live_manifest(
    rows_with_paths: list[tuple[Path, dict[str, str]]],
    errors: list[str],
) -> None:
    """Protect the exact 2026-07-24 production field identities and placements."""

    manifest_keys = {
        (module_label, field_label)
        for module_label, _, manifest in GOVERNED_LIVE_MANIFEST
        for field_label, _, _ in manifest
    }
    if set(GOVERNED_LIVE_FIELD_TYPES) != manifest_keys:
        errors.append(
            "validator invariant: governed live field-type coverage does not "
            "exactly match the 2026-07-24 manifest"
        )
    lookup_keys = {
        key
        for key, field_type in GOVERNED_LIVE_FIELD_TYPES.items()
        if field_type == "Lookup"
    }
    if set(GOVERNED_LIVE_LOOKUP_TARGETS) != lookup_keys:
        errors.append(
            "validator invariant: governed live lookup-target coverage does not "
            "exactly match the 2026-07-24 lookup fields"
        )
    choice_keys = {
        key
        for key, field_type in GOVERNED_LIVE_FIELD_TYPES.items()
        if field_type in {"Pick List", "Multi-Select Pick List"}
    }
    if set(GOVERNED_LIVE_CHOICES) != choice_keys:
        errors.append(
            "validator invariant: governed live choice coverage does not exactly "
            "match the 2026-07-24 choice fields"
        )

    rows_by_field: dict[
        tuple[str, str], list[tuple[Path, dict[str, str]]]
    ] = defaultdict(list)
    for csv_path, row in rows_with_paths:
        key = (
            row["module_display_label"].casefold(),
            row["field_label"].casefold(),
        )
        rows_by_field[key].append((csv_path, row))

    for module_label, module_api_name, manifest in GOVERNED_LIVE_MANIFEST:
        for field_label, api_name, section in manifest:
            key = (module_label.casefold(), field_label.casefold())
            matches = rows_by_field.get(key, [])
            manifest_path = (
                f"2026-07-24 live manifest: {module_label}.{field_label}"
            )
            if not matches:
                errors.append(f"{manifest_path}: required catalog row is missing")
                continue
            if len(matches) != 1:
                errors.append(
                    f"{manifest_path}: expected exactly one catalog row, "
                    f"found {len(matches)}"
                )
                continue

            csv_path, row = matches[0]
            expected_values = {
                "module_display_label": module_label,
                "module_api_name": module_api_name,
                "field_label": field_label,
                "field_type": GOVERNED_LIVE_FIELD_TYPES[
                    (module_label, field_label)
                ],
                "api_name": api_name,
                "api_name_status": "verified_live_mcp",
                "disposition": "governed_current",
                "section": section,
            }
            for column, expected in expected_values.items():
                actual = row[column]
                if actual != expected:
                    errors.append(
                        f"{csv_path.name}: {manifest_path}.{column}: "
                        f"expected {expected!r}, found {actual!r}"
                    )

            source_ids = {
                item.strip()
                for item in row["source_ids"].split(",")
                if item.strip()
            }
            if "LIVE_CRM_MCP_2026-07-24" not in source_ids:
                errors.append(
                    f"{csv_path.name}: {manifest_path}.source_ids: "
                    "expected LIVE_CRM_MCP_2026-07-24"
                )

            lookup_target = GOVERNED_LIVE_LOOKUP_TARGETS.get(
                (module_label, field_label)
            )
            if lookup_target is not None:
                lookup_pattern = (
                    rf"\blookup (?:target |to ){re.escape(lookup_target)}\b"
                )
                if not re.search(lookup_pattern, row["notes"], re.IGNORECASE):
                    errors.append(
                        f"{csv_path.name}: {manifest_path}.notes: expected "
                        f"readback evidence for lookup target {lookup_target!r}"
                    )

            expected_choices = GOVERNED_LIVE_CHOICES.get(
                (module_label, field_label)
            )
            if (
                expected_choices is not None
                and row["picklist_values_and_colors"] != expected_choices
            ):
                errors.append(
                    f"{csv_path.name}: {manifest_path}."
                    "picklist_values_and_colors: exact live choices/order/colors "
                    "drifted"
                )


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
        if (
            api_status == "verified_live_mcp"
            and "LIVE_CRM_MCP_2026-07-24" not in source_ids
        ):
            errors.append(
                f"{path}: verified_live_mcp requires "
                "LIVE_CRM_MCP_2026-07-24 in source_ids"
            )
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
            allow_uncolored=(
                api_status == "verified_live_mcp"
                and row["picklist_scope"]
                in {"module_local_live_uncolored", "standard_module_live_uncolored"}
            ),
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
    validate_governed_live_snapshot(rows_with_paths, errors)
    validate_governed_live_manifest(rows_with_paths, errors)
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
