#!/usr/bin/env python3
"""Export sanitized Zoho CRM module and field metadata without reading records.

Required environment variable:
    ZOHO_CRM_ACCESS_TOKEN

Optional environment variable:
    ZOHO_CRM_API_DOMAIN (default: https://www.zohoapis.com)

The OAuth token needs settings metadata read scope, for example:
    ZohoCRM.settings.modules.READ
    ZohoCRM.settings.fields.READ
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

DEFAULT_API_DOMAIN = "https://www.zohoapis.com"
API_VERSION = "v8"


class MetadataExportError(RuntimeError):
    """Raised when a fail-closed metadata export cannot complete."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        help="Output JSON path. Defaults to ./zoho-crm-metadata-YYYYMMDDTHHMMSSZ.json",
    )
    parser.add_argument(
        "--module",
        action="append",
        dest="modules",
        help="Restrict export to a module API name. Repeat for multiple modules.",
    )
    parser.add_argument(
        "--visible-only",
        action="store_true",
        help="Request only modules whose status is visible.",
    )
    parser.add_argument(
        "--include-non-api-modules",
        action="store_true",
        help="Retain module metadata even when api_supported is false. Fields are not fetched.",
    )
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Record per-module field errors and continue. Default is fail closed.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite the output path when it already exists.",
    )
    return parser.parse_args()


def require_access_token() -> str:
    token = os.environ.get("ZOHO_CRM_ACCESS_TOKEN", "").strip()
    if not token:
        raise MetadataExportError(
            "ZOHO_CRM_ACCESS_TOKEN is required. Do not pass the token on the command line "
            "or store it in the repository."
        )
    return token


def validate_api_domain(raw: str) -> str:
    value = raw.strip().rstrip("/")
    parsed = urlparse(value)
    host = (parsed.hostname or "").lower()
    if parsed.scheme != "https":
        raise MetadataExportError("ZOHO_CRM_API_DOMAIN must use HTTPS")
    if not host or ".zohoapis." not in host:
        raise MetadataExportError(
            "ZOHO_CRM_API_DOMAIN must be an official Zoho API data-center domain"
        )
    if parsed.path not in {"", "/"} or parsed.params or parsed.query or parsed.fragment:
        raise MetadataExportError("ZOHO_CRM_API_DOMAIN must not contain a path or query")
    return value


def request_json(url: str, access_token: str) -> dict[str, Any]:
    request = Request(
        url,
        method="GET",
        headers={
            "Authorization": f"Zoho-oauthtoken {access_token}",
            "Accept": "application/json",
            "User-Agent": "GH-Real-Estate-Zoho-CRM-Metadata-Exporter/1.0",
        },
    )
    try:
        with urlopen(request, timeout=30) as response:
            payload = response.read()
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:1000]
        raise MetadataExportError(
            f"Zoho request failed with HTTP {exc.code} for {url}: {body}"
        ) from exc
    except URLError as exc:
        raise MetadataExportError(f"Zoho request failed for {url}: {exc.reason}") from exc

    try:
        data = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MetadataExportError(f"Zoho returned invalid JSON for {url}") from exc
    if not isinstance(data, dict):
        raise MetadataExportError(f"Zoho returned an unexpected JSON shape for {url}")
    return data


def compact_tooltip(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, dict):
        return {
            key: value.get(key)
            for key in ("name", "value")
            if value.get(key) is not None
        } or None
    return value


def sanitize_module(module: dict[str, Any]) -> dict[str, Any]:
    return {
        key: module.get(key)
        for key in (
            "plural_label",
            "singular_label",
            "actual_plural_label",
            "actual_singular_label",
            "module_name",
            "api_name",
            "generated_type",
            "api_supported",
            "status",
            "visible",
            "show_as_tab",
            "lookupable",
            "creatable",
            "editable",
            "viewable",
        )
        if module.get(key) is not None
    }


def sanitize_lookup(value: Any) -> Any:
    if not isinstance(value, dict) or not value:
        return None
    module = value.get("module")
    if isinstance(module, dict):
        module = {
            key: module.get(key)
            for key in ("api_name", "module_name")
            if module.get(key) is not None
        }
    return {
        key: item
        for key, item in {
            "module": module,
            "display_label": value.get("display_label"),
            "api_name": value.get("api_name"),
        }.items()
        if item not in (None, {}, "")
    } or None


def sanitize_formula(value: Any) -> Any:
    if not isinstance(value, dict) or not value:
        return None
    allowed = (
        "return_type",
        "expression",
        "data_type",
        "decimal_place",
    )
    return {key: value.get(key) for key in allowed if value.get(key) is not None} or None


def sanitize_auto_number(value: Any) -> Any:
    if not isinstance(value, dict) or not value:
        return None
    allowed = (
        "prefix",
        "suffix",
        "start_number",
    )
    return {key: value.get(key) for key in allowed if value.get(key) is not None} or None


def sanitize_rollup(value: Any) -> Any:
    if not isinstance(value, dict) or not value:
        return None
    allowed = (
        "return_type",
        "rollup_based_on",
        "related_list",
        "aggregation_function",
    )
    return {key: value.get(key) for key in allowed if value.get(key) is not None} or None


def sanitize_global_picklist(value: Any) -> Any:
    if not isinstance(value, dict) or not value:
        return None
    return {
        key: value.get(key)
        for key in ("name", "api_name", "display_label")
        if value.get(key) is not None
    } or None


def sanitize_picklist_values(values: Any) -> list[dict[str, Any]]:
    if not isinstance(values, list):
        return []
    output: list[dict[str, Any]] = []
    for item in values:
        if not isinstance(item, dict):
            continue
        output.append(
            {
                key: item.get(key)
                for key in (
                    "display_value",
                    "actual_value",
                    "reference_value",
                    "sequence_number",
                    "colour_code",
                    "type",
                )
                if item.get(key) is not None
            }
        )
    return output


def sanitize_field(field: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {
        key: field.get(key)
        for key in (
            "field_label",
            "display_label",
            "api_name",
            "data_type",
            "json_type",
            "custom_field",
            "system_mandatory",
            "read_only",
            "field_read_only",
            "visible",
            "length",
            "decimal_place",
            "enable_colour_code",
            "colour_code_enabled_by_system",
            "history_tracking_enabled",
            "pick_list_values_sorted_lexically",
            "created_source",
            "type",
        )
        if field.get(key) is not None
    }
    optional = {
        "tooltip": compact_tooltip(field.get("tooltip")),
        "textarea": field.get("textarea") if isinstance(field.get("textarea"), dict) else None,
        "lookup": sanitize_lookup(field.get("lookup")),
        "formula": sanitize_formula(field.get("formula")),
        "auto_number": sanitize_auto_number(field.get("auto_number")),
        "rollup_summary": sanitize_rollup(field.get("rollup_summary")),
        "global_picklist": sanitize_global_picklist(field.get("global_picklist")),
    }
    for key, value in optional.items():
        if value not in (None, {}, []):
            result[key] = value

    picklist_values = sanitize_picklist_values(field.get("pick_list_values"))
    if picklist_values:
        result["pick_list_values"] = picklist_values
    return result


def fetch_modules(api_domain: str, token: str, visible_only: bool) -> list[dict[str, Any]]:
    query = "?status=visible" if visible_only else ""
    data = request_json(
        f"{api_domain}/crm/{API_VERSION}/settings/modules{query}",
        token,
    )
    modules = data.get("modules")
    if not isinstance(modules, list):
        raise MetadataExportError("Modules Metadata response did not contain a modules list")
    return [item for item in modules if isinstance(item, dict)]


def fetch_fields(api_domain: str, token: str, module_api_name: str) -> list[dict[str, Any]]:
    query = urlencode({"module": module_api_name, "type": "all"})
    data = request_json(
        f"{api_domain}/crm/{API_VERSION}/settings/fields?{query}",
        token,
    )
    fields = data.get("fields")
    if not isinstance(fields, list):
        raise MetadataExportError(
            f"Fields Metadata response for {module_api_name!r} did not contain a fields list"
        )
    return [item for item in fields if isinstance(item, dict)]


def main() -> int:
    args = parse_args()
    try:
        token = require_access_token()
        api_domain = validate_api_domain(
            os.environ.get("ZOHO_CRM_API_DOMAIN", DEFAULT_API_DOMAIN)
        )

        now = datetime.now(timezone.utc)
        output_path = args.output or Path(
            f"zoho-crm-metadata-{now.strftime('%Y%m%dT%H%M%SZ')}.json"
        )
        output_path = output_path.expanduser().resolve()
        if output_path.exists() and not args.force:
            raise MetadataExportError(
                f"output already exists: {output_path}; pass --force to overwrite"
            )

        all_modules = fetch_modules(api_domain, token, args.visible_only)
        requested = set(args.modules or [])
        if requested:
            available = {
                str(module.get("api_name"))
                for module in all_modules
                if module.get("api_name")
            }
            missing = sorted(requested - available)
            if missing:
                raise MetadataExportError(
                    "requested module API name(s) not found: " + ", ".join(missing)
                )

        export_modules: list[dict[str, Any]] = []
        errors: list[dict[str, str]] = []

        for module in all_modules:
            api_name = str(module.get("api_name") or "").strip()
            if not api_name:
                continue
            if requested and api_name not in requested:
                continue

            api_supported = bool(module.get("api_supported"))
            if not api_supported and not args.include_non_api_modules:
                continue

            item = sanitize_module(module)
            if api_supported:
                try:
                    fields = fetch_fields(api_domain, token, api_name)
                    item["fields"] = [sanitize_field(field) for field in fields]
                except MetadataExportError as exc:
                    if not args.continue_on_error:
                        raise
                    item["fields"] = []
                    item["field_export_error"] = str(exc)
                    errors.append({"module_api_name": api_name, "error": str(exc)})
                time.sleep(0.05)
            else:
                item["fields"] = []

            export_modules.append(item)

        if requested:
            exported_names = {module.get("api_name") for module in export_modules}
            not_exported = sorted(requested - exported_names)
            if not_exported:
                raise MetadataExportError(
                    "requested module(s) were not exported: " + ", ".join(not_exported)
                )

        output = {
            "export_id": "GH-ZOHO-CRM-METADATA",
            "export_version": "1.0.0",
            "exported_at_utc": now.isoformat(),
            "api_version": API_VERSION,
            "api_domain": api_domain,
            "record_data_included": False,
            "ids_included": False,
            "required_scopes": [
                "ZohoCRM.settings.modules.READ",
                "ZohoCRM.settings.fields.READ",
            ],
            "module_count": len(export_modules),
            "field_count": sum(len(module.get("fields", [])) for module in export_modules),
            "errors": errors,
            "modules": export_modules,
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(output, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(
            f"Exported {output['module_count']} modules and {output['field_count']} fields "
            f"to {output_path}"
        )
        if errors:
            print(f"Completed with {len(errors)} module error(s).", file=sys.stderr)
            return 2
        return 0
    except MetadataExportError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
