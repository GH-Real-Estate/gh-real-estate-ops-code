#!/usr/bin/env python3
"""Validate GH Real Estate Zoho Sign recipient manifests.

This validator is intentionally dependency-free. It enforces Zoho's positional
recipient indexing, contiguous R-numbers, and GH Real Estate's final-signer gate.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse

ROLE_RE = re.compile(r"^R([1-9]|1[0-9]|2[0-5])$")
SIMPLE_SIGNATURE_RE = re.compile(r"^\{\{S:(R(?:[1-9]|1[0-9]|2[0-5]))\}\}$")
SIMPLE_SIGN_DATE_RE = re.compile(r"^\{\{SD:(R(?:[1-9]|1[0-9]|2[0-5]))\}\}$")
LANDLORD_ROLE = "GH Real Estate, LLC Authorized Representative"
POLICY_FILE = "ghre-canonical-recipient-policy.json"
MANIFEST_GLOB = "*.recipient-manifest.json"
ZOHO_TAG_URL = (
    "https://help.zoho.com/portal/en/kb/zoho-sign/user-guide/sending-a-document/"
    "articles/automatic-field-addition-in-zoho-sign"
)
ZOHO_SEND_URL = (
    "https://help.zoho.com/portal/en/kb/zoho-sign/user-guide/sending-a-document/"
    "articles/send-for-signatures"
)


def repository_root() -> Path:
    return Path(__file__).resolve().parents[3]


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _non_empty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _role_number(role: Any) -> int | None:
    if not isinstance(role, str):
        return None
    match = ROLE_RE.fullmatch(role)
    return int(match.group(1)) if match else None


def _is_official_zoho_url(value: Any) -> bool:
    if not _non_empty(value):
        return False
    parsed = urlparse(value)
    host = (parsed.hostname or "").lower()
    return parsed.scheme == "https" and (host == "zoho.com" or host.endswith(".zoho.com"))


def _validate_recipient_sequence(
    recipients: Any,
    *,
    path: str,
    require_landlord: bool = True,
) -> tuple[list[str], list[dict[str, Any]]]:
    errors: list[str] = []
    if not isinstance(recipients, list) or not recipients:
        return [f"{path} must be a non-empty list"], []

    normalized: list[dict[str, Any]] = []
    for index, recipient in enumerate(recipients):
        prefix = f"{path}[{index}]"
        if not isinstance(recipient, dict):
            errors.append(f"{prefix} must be an object")
            continue
        expected = {"role", "business_role", "signing_position"}
        missing = expected - set(recipient)
        extra = set(recipient) - expected
        if missing:
            errors.append(f"{prefix} is missing keys: {', '.join(sorted(missing))}")
        if extra:
            errors.append(f"{prefix} has unexpected keys: {', '.join(sorted(extra))}")

        role = recipient.get("role")
        number = _role_number(role)
        if number is None:
            errors.append(f"{prefix}.role must be R1 through R25")
        business_role = recipient.get("business_role")
        if not _non_empty(business_role):
            errors.append(f"{prefix}.business_role must be non-empty")
        signing_position = recipient.get("signing_position")
        if (
            isinstance(signing_position, bool)
            or not isinstance(signing_position, int)
            or signing_position < 1
        ):
            errors.append(f"{prefix}.signing_position must be a positive integer")
        normalized.append(recipient)

    valid_roles = [item.get("role") for item in normalized if _role_number(item.get("role"))]
    expected_roles = [f"R{number}" for number in range(1, len(normalized) + 1)]
    if valid_roles != expected_roles:
        errors.append(
            f"{path} roles must be contiguous and ordered as {expected_roles}; found {valid_roles}"
        )

    landlords = [
        item for item in normalized if item.get("business_role") == LANDLORD_ROLE
    ]
    if require_landlord and len(landlords) != 1:
        errors.append(f"{path} must contain exactly one GH Real Estate landlord recipient")
    if landlords:
        landlord = landlords[0]
        if normalized[-1] is not landlord:
            errors.append(f"{path} must place GH Real Estate as the final actual recipient")
        landlord_position = landlord.get("signing_position")
        other_positions = [
            item.get("signing_position")
            for item in normalized
            if item is not landlord and isinstance(item.get("signing_position"), int)
        ]
        if isinstance(landlord_position, int) and other_positions:
            if landlord_position <= max(other_positions):
                errors.append(
                    f"{path} must give GH Real Estate a signing position after every other signer"
                )
    return errors, normalized


def _validate_canonical_tags(
    tags: Any,
    recipients: list[dict[str, Any]],
    *,
    path: str,
) -> list[str]:
    errors: list[str] = []
    if not isinstance(tags, dict) or not tags:
        return [f"{path} must be a non-empty object"]

    roles = {item["role"] for item in recipients if _role_number(item.get("role"))}
    landlord_role = recipients[-1].get("role") if recipients else None
    signature_roles: set[str] = set()
    sign_date_roles: set[str] = set()

    for key, value in tags.items():
        prefix = f"{path}.{key}"
        if not _non_empty(key) or not _non_empty(value):
            errors.append(f"{prefix} must contain a non-empty simple tag")
            continue
        signature_match = SIMPLE_SIGNATURE_RE.fullmatch(value)
        date_match = SIMPLE_SIGN_DATE_RE.fullmatch(value)
        if not signature_match and not date_match:
            errors.append(
                f"{prefix} must use an unpadded production-safe {{S:Rn}} or {{SD:Rn}} tag"
            )
            continue
        role = (signature_match or date_match).group(1)
        if role not in roles:
            errors.append(f"{prefix} references {role}, which is absent from the recipient manifest")
        if signature_match:
            signature_roles.add(role)
        else:
            sign_date_roles.add(role)

    if signature_roles != roles:
        errors.append(f"{path} must provide exactly one signature mapping for every recipient")
    if sign_date_roles != roles:
        errors.append(f"{path} must provide exactly one Sign Date mapping for every recipient")

    if landlord_role:
        if tags.get("landlord_signature") != f"{{{{S:{landlord_role}}}}}":
            errors.append(f"{path}.landlord_signature must target final recipient {landlord_role}")
        if tags.get("landlord_sign_date") != f"{{{{SD:{landlord_role}}}}}":
            errors.append(f"{path}.landlord_sign_date must target final recipient {landlord_role}")
    return errors


def validate_policy(policy: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(policy, dict):
        return ["recipient policy must be an object"]

    required = {
        "schema_version",
        "policy_id",
        "title",
        "effective_date",
        "governance_status",
        "scope",
        "source_of_truth",
        "official_sources",
        "recipient_index_policy",
        "landlord_final_signer_policy",
        "base_residential_manifests",
        "additional_signer_policy",
        "signing_order_policy",
        "optional_signer_policy",
        "validation_rules",
        "exceptions",
    }
    missing = required - set(policy)
    extra = set(policy) - required
    if missing:
        errors.append(f"recipient policy is missing keys: {', '.join(sorted(missing))}")
    if extra:
        errors.append(f"recipient policy has unexpected keys: {', '.join(sorted(extra))}")
    if policy.get("schema_version") != "1.1.0":
        errors.append("recipient policy schema_version must be 1.1.0")
    if policy.get("policy_id") != "ghre-canonical-recipient-policy":
        errors.append("recipient policy_id changed")
    if policy.get("governance_status") != "active":
        errors.append("recipient policy must remain active")
    if policy.get("source_of_truth") is not True:
        errors.append("recipient policy must remain the source of truth")

    sources = policy.get("official_sources")
    if not isinstance(sources, list) or not sources:
        errors.append("official_sources must be a non-empty list")
    else:
        urls: set[str] = set()
        for index, source in enumerate(sources):
            prefix = f"official_sources[{index}]"
            if not isinstance(source, dict) or set(source) != {"title", "url"}:
                errors.append(f"{prefix} must contain only title and url")
                continue
            if not _non_empty(source.get("title")):
                errors.append(f"{prefix}.title must be non-empty")
            url = source.get("url")
            if not _is_official_zoho_url(url):
                errors.append(f"{prefix}.url must be an official HTTPS Zoho URL")
            elif isinstance(url, str):
                urls.add(url)
        for required_url in (ZOHO_TAG_URL, ZOHO_SEND_URL):
            if required_url not in urls:
                errors.append(f"official_sources must include {required_url}")

    index_policy = policy.get("recipient_index_policy", {})
    if index_policy.get("contiguous_required") is not True:
        errors.append("recipient indexes must be contiguous")
    if index_policy.get("gaps_allowed") is not False:
        errors.append("recipient index gaps must be forbidden")
    if index_policy.get("placeholder_recipients_allowed") is not False:
        errors.append("placeholder recipients must be forbidden")
    if index_policy.get("every_signer_requires_at_least_one_field") is not True:
        errors.append("every signer must require at least one assigned field")
    if index_policy.get("business_roles_are_not_fixed_to_recipient_numbers") is not True:
        errors.append("business roles must not be fixed to recipient numbers")

    landlord_policy = policy.get("landlord_final_signer_policy", {})
    if landlord_policy.get("business_role") != LANDLORD_ROLE:
        errors.append("landlord business role changed")
    if landlord_policy.get("recipient_formula") != (
        "R{number_of_actual_non_landlord_recipients + 1}"
    ):
        errors.append("landlord recipient formula changed")
    for key in (
        "must_be_last_actual_recipient",
        "must_have_final_signing_position",
        "no_signer_after_landlord",
    ):
        if landlord_policy.get(key) is not True:
            errors.append(f"landlord_final_signer_policy.{key} must be true")
    if "only when exactly three" not in str(landlord_policy.get("fixed_R4_rule", "")):
        errors.append("fixed_R4_rule must limit R4 to three preceding actual recipients")

    scenarios = policy.get("base_residential_manifests")
    expected_counts = {"one_tenant": 1, "two_tenants": 2, "three_tenants": 3}
    if not isinstance(scenarios, dict) or set(scenarios) != set(expected_counts):
        errors.append("base_residential_manifests must define one, two, and three-tenant scenarios")
    else:
        for scenario_name, tenant_count in expected_counts.items():
            scenario = scenarios[scenario_name]
            prefix = f"base_residential_manifests.{scenario_name}"
            if not isinstance(scenario, dict) or set(scenario) != {
                "recipients",
                "landlord_role",
                "canonical_tags",
            }:
                errors.append(
                    f"{prefix} must contain recipients, landlord_role, and canonical_tags"
                )
                continue
            sequence_errors, recipients = _validate_recipient_sequence(
                scenario.get("recipients"), path=f"{prefix}.recipients"
            )
            errors.extend(sequence_errors)
            if len(recipients) != tenant_count + 1:
                errors.append(f"{prefix} must contain {tenant_count} tenants plus GH")
            for index in range(min(tenant_count, len(recipients))):
                if recipients[index].get("business_role") != f"Tenant {index + 1}":
                    errors.append(f"{prefix}.recipients[{index}] must be Tenant {index + 1}")
                if recipients[index].get("signing_position") != 1:
                    errors.append(f"{prefix}.recipients[{index}] must use signing position 1")
            if recipients and recipients[-1].get("signing_position") != 2:
                errors.append(f"{prefix} GH recipient must use signing position 2")
            expected_landlord_role = f"R{tenant_count + 1}"
            if scenario.get("landlord_role") != expected_landlord_role:
                errors.append(f"{prefix}.landlord_role must be {expected_landlord_role}")
            errors.extend(
                _validate_canonical_tags(
                    scenario.get("canonical_tags"),
                    recipients,
                    path=f"{prefix}.canonical_tags",
                )
            )

    additional = policy.get("additional_signer_policy", {})
    for key in (
        "renumber_landlord_when_additional_signers_exist",
        "dummy_or_placeholder_recipients_forbidden",
        "additional_signers_after_landlord_forbidden",
        "document_specific_manifest_required",
    ):
        if additional.get(key) is not True:
            errors.append(f"additional_signer_policy.{key} must be true")

    signing = policy.get("signing_order_policy", {})
    if signing.get("parallel_non_landlord_signing_allowed") is not True:
        errors.append("parallel non-landlord signing must remain allowed")
    if "highest signing position" not in str(signing.get("landlord_last_gate", "")):
        errors.append("landlord_last_gate must require the highest signing position")

    optional = policy.get("optional_signer_policy", {})
    if optional.get("actual_signer_signature_required") is not True:
        errors.append("actual named signer signatures must remain required")
    absent_action = str(optional.get("absent_signer_action", "")).lower()
    if "contiguous" not in absent_action or "remove" not in absent_action:
        errors.append("absent signer policy must remove the signer and regenerate contiguous roles")

    rules = policy.get("validation_rules")
    if not isinstance(rules, list) or not all(_non_empty(rule) for rule in rules):
        errors.append("validation_rules must be a non-empty list of strings")
    return errors


def validate_document_manifest(manifest: Any, *, name: str = "manifest") -> list[str]:
    errors: list[str] = []
    if not isinstance(manifest, dict):
        return [f"{name} must be an object"]
    required = {
        "schema_version",
        "manifest_id",
        "document_type",
        "gh_signs",
        "recipients",
        "landlord_role",
    }
    missing = required - set(manifest)
    extra = set(manifest) - required
    if missing:
        errors.append(f"{name} is missing keys: {', '.join(sorted(missing))}")
    if extra:
        errors.append(f"{name} has unexpected keys: {', '.join(sorted(extra))}")
    if manifest.get("schema_version") != "1.0.0":
        errors.append(f"{name}.schema_version must be 1.0.0")
    for key in ("manifest_id", "document_type"):
        if not _non_empty(manifest.get(key)):
            errors.append(f"{name}.{key} must be non-empty")
    gh_signs = manifest.get("gh_signs")
    if not isinstance(gh_signs, bool):
        errors.append(f"{name}.gh_signs must be boolean")
        gh_signs = True
    sequence_errors, recipients = _validate_recipient_sequence(
        manifest.get("recipients"), path=f"{name}.recipients", require_landlord=gh_signs
    )
    errors.extend(sequence_errors)
    if gh_signs and recipients:
        expected = recipients[-1].get("role")
        if manifest.get("landlord_role") != expected:
            errors.append(f"{name}.landlord_role must identify final recipient {expected}")
    elif not gh_signs and manifest.get("landlord_role") is not None:
        errors.append(f"{name}.landlord_role must be null when GH does not sign")
    return errors


def validate_repository(root: Path) -> list[str]:
    manifest_dir = root / "src/zoho-sign/recipient-manifests"
    errors: list[str] = []
    policy_path = manifest_dir / POLICY_FILE
    try:
        policy = load_json(policy_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [f"{policy_path}: {exc}"]
    errors.extend(f"{POLICY_FILE}: {error}" for error in validate_policy(policy))

    for path in sorted(manifest_dir.glob(MANIFEST_GLOB)):
        relative = path.relative_to(root).as_posix()
        try:
            manifest = load_json(path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"{relative}: {exc}")
            continue
        errors.extend(
            f"{relative}: {error}"
            for error in validate_document_manifest(manifest, name=relative)
        )
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=repository_root(),
        help="repository root (defaults to the script's repository)",
    )
    args = parser.parse_args(argv)
    errors = validate_repository(args.root.resolve())
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(
        "Validated contiguous Zoho Sign recipient manifests and GH Real Estate final-signer routing."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
