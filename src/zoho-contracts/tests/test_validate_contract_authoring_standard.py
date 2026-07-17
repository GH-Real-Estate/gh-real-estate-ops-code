"""Regression tests for the Contracts authoring and Sign tag governance policy."""

from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/validate_contract_authoring_standard.py"
SPEC = importlib.util.spec_from_file_location("validate_contract_authoring_standard", SCRIPT)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class ContractAuthoringStandardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parents[3]
        cls.paths = validator._paths(cls.root)
        cls.standard = validator.load_json(cls.paths["standard"])
        cls.sign_registry = validator.load_json(cls.paths["sign_registry"])
        cls.schema = validator.load_json(cls.paths["clause_schema"])
        cls.template = validator.load_json(cls.paths["clause_template"])

    def valid_clause(self) -> dict:
        return copy.deepcopy(self.template)

    def test_exact_clause_type_master_list(self) -> None:
        self.assertEqual(self.standard["clause_type_master_list"], validator.CLAUSE_TYPES)
        self.assertEqual(len(validator.CLAUSE_TYPES), 16)

    def test_canonical_contract_standard_validates(self) -> None:
        self.assertEqual(validator.validate_authoring_standard(self.standard), [])

    def test_canonical_sign_registry_validates(self) -> None:
        self.assertEqual(validator.validate_sign_registry(self.sign_registry), [])

    def test_schema_and_template_are_consistent(self) -> None:
        self.assertEqual(
            validator.validate_schema_consistency(
                self.schema, self.template, self.standard
            ),
            [],
        )

    def test_template_is_a_valid_clause_definition(self) -> None:
        self.assertEqual(
            validator.validate_clause_definition(self.template, self.standard), []
        )

    def test_missing_clause_metadata_is_rejected_without_crashing(self) -> None:
        clause = self.valid_clause()
        del clause["clause_name"]
        errors = validator.validate_clause_definition(clause, self.standard)
        self.assertTrue(any("missing required clause property: clause_name" in error for error in errors))

    def test_bad_clause_type_is_rejected(self) -> None:
        clause = self.valid_clause()
        clause["clause_type"] = "Miscellaneous"
        errors = validator.validate_clause_definition(clause, self.standard)
        self.assertTrue(any("governed master list" in error for error in errors))

    def test_library_question_is_required_to_be_a_question(self) -> None:
        clause = self.valid_clause()
        clause["library_question"] = "Use the standard language"
        errors = validator.validate_clause_definition(clause, self.standard)
        self.assertTrue(any("library_question" in error for error in errors))

    def test_bad_contract_type_override_question_is_rejected(self) -> None:
        clause = self.valid_clause()
        clause["contract_type_question_overrides"] = [
            {"contract_type": "Residential Lease", "question": "Use this version"}
        ]
        errors = validator.validate_clause_definition(clause, self.standard)
        self.assertTrue(any("overrides[0].question" in error for error in errors))

    def test_clause_title_style_must_be_heading_2(self) -> None:
        clause = self.valid_clause()
        clause["language_variants"][0]["clause_title_style"] = "Title"
        errors = validator.validate_clause_definition(clause, self.standard)
        self.assertTrue(any("clause_title_style must be Heading 2" in error for error in errors))

    def test_heading_6_is_rejected(self) -> None:
        clause = self.valid_clause()
        clause["language_variants"][0]["blocks"][0]["style"] = "Heading 6"
        errors = validator.validate_clause_definition(clause, self.standard)
        self.assertTrue(any("Heading 3-5 or Normal" in error for error in errors))

    def test_clause_title_must_not_be_duplicated_in_language(self) -> None:
        clause = self.valid_clause()
        clause["language_variants"][0]["blocks"][0]["text"] = clause[
            "language_variants"
        ][0]["clause_title"]
        errors = validator.validate_clause_definition(clause, self.standard)
        self.assertTrue(any("duplicates clause_title" in error for error in errors))

    def test_article_and_clause_title_styles_are_rejected_in_language(self) -> None:
        for style in ("Heading 1", "Heading 2", "Title"):
            clause = self.valid_clause()
            clause["language_variants"][0]["blocks"][0]["style"] = style
            errors = validator.validate_clause_definition(clause, self.standard)
            with self.subTest(style=style):
                self.assertTrue(any("Heading 3-5 or Normal" in error for error in errors))

    def test_language_heading_depth_cannot_skip(self) -> None:
        clause = self.valid_clause()
        clause["language_variants"][0]["blocks"] = [
            {"style": "Heading 5", "text": "Skipped Heading"},
            {"style": "Normal", "text": "Substantive language."},
        ]
        errors = validator.validate_clause_definition(clause, self.standard)
        self.assertTrue(any("skips heading depth" in error for error in errors))

    def test_language_heading_depth_may_return_to_shallower_level(self) -> None:
        clause = self.valid_clause()
        clause["language_variants"][0]["blocks"] = [
            {"style": "Heading 3", "text": "First Subsection"},
            {"style": "Heading 4", "text": "Nested Subsection"},
            {"style": "Normal", "text": "Nested substantive language."},
            {"style": "Heading 3", "text": "Second Subsection"},
            {"style": "Normal", "text": "More substantive language."},
        ]
        self.assertEqual(
            validator.validate_clause_definition(clause, self.standard), []
        )

    def test_exactly_one_standard_variant_is_required(self) -> None:
        clause = self.valid_clause()
        clause["language_variants"][0]["variant_kind"] = "alternate"
        errors = validator.validate_clause_definition(clause, self.standard)
        self.assertTrue(any("exactly one standard" in error for error in errors))

    def test_multiple_standard_variants_are_rejected(self) -> None:
        clause = self.valid_clause()
        duplicate = copy.deepcopy(clause["language_variants"][0])
        duplicate["variant_id"] = "second-standard"
        clause["language_variants"].append(duplicate)
        errors = validator.validate_clause_definition(clause, self.standard)
        self.assertTrue(any("exactly one standard" in error for error in errors))

    def test_optional_alternate_variant_is_accepted(self) -> None:
        clause = self.valid_clause()
        alternate = copy.deepcopy(clause["language_variants"][0])
        alternate.update(
            {
                "variant_id": "approved-alternate",
                "variant_kind": "alternate",
                "clause_title": "Alternate Sample Clause Title",
            }
        )
        clause["language_variants"].append(alternate)
        self.assertEqual(
            validator.validate_clause_definition(clause, self.standard), []
        )

    def test_null_api_name_requires_verification_status(self) -> None:
        clause = self.valid_clause()
        clause["zoho_api_name_status"] = "tenant_verified"
        errors = validator.validate_clause_definition(clause, self.standard)
        self.assertTrue(any("null zoho_api_name" in error for error in errors))

    def test_verified_api_name_is_accepted(self) -> None:
        clause = self.valid_clause()
        clause["zoho_api_name"] = "sampleClauseDefinition"
        clause["zoho_api_name_status"] = "tenant_verified"
        self.assertEqual(
            validator.validate_clause_definition(clause, self.standard), []
        )

    def test_all_canonical_simple_tags_classify_production_safe(self) -> None:
        for entry in self.sign_registry["production_safe_simple_tags"]:
            with self.subTest(entry=entry["code"]):
                result = validator.classify_tag(entry["syntax"], self.sign_registry)
                self.assertEqual(result["classification"], "production_safe")

    def test_user_confirmed_initial_tag_is_safe_with_compatibility_warning(self) -> None:
        result = validator.classify_tag("{{I:R1*}}", self.sign_registry)
        self.assertEqual(result["classification"], "production_safe")
        self.assertTrue(any("redundant asterisk" in warning for warning in result["warnings"]))

    def test_simple_signer_tags_scan_with_manifest(self) -> None:
        result = validator.scan_text_tags(
            "Sign {{S:R1}} and initial {{I:R1*}}.",
            [{"role": "R1", "purpose": "Tenant signer"}],
        )
        self.assertEqual(result["errors"], [])
        self.assertEqual(len(result["tags"]), 2)

    def test_exact_checkbox_shorthand_requires_sole_explicit_r1(self) -> None:
        safe = validator.scan_text_tags("Accept {{[]}}", ["R1"])
        self.assertEqual(safe["errors"], [])
        unsafe = validator.scan_text_tags("Accept {{[]}}", ["R1", "R2"])
        self.assertTrue(any("sole signer R1" in error for error in unsafe["errors"]))

    def test_unpublished_lowercase_checkbox_tags_are_rejected(self) -> None:
        for tag in ("{{checkbox:R1}}", "{{checkbox:R1*}}"):
            with self.subTest(tag=tag):
                result = validator.classify_tag(tag, self.sign_registry)
                self.assertEqual(result["classification"], "invalid")

    def test_r26_is_rejected(self) -> None:
        result = validator.classify_tag("{{S:R26}}", self.sign_registry)
        self.assertEqual(result["classification"], "invalid")
        self.assertIn("R1 through R25", result["reason"])

    def test_unknown_and_invented_tags_are_rejected(self) -> None:
        for tag in ("{{ZZ:R1}}", "{{Phone:R1}}", "{{Image:R1}}", "{{Payment:R1}}"):
            with self.subTest(tag=tag):
                self.assertEqual(
                    validator.classify_tag(tag, self.sign_registry)["classification"],
                    "invalid",
                )

    def test_canonical_formatted_sign_date_is_production_safe(self) -> None:
        result = validator.classify_tag(
            '{{SD:R1:(dateformat="MM/dd/yyyy hh:mm a z")}}', self.sign_registry
        )
        self.assertEqual(result["classification"], "production_safe")

    def test_production_scan_accepts_canonical_formatted_sign_date(self) -> None:
        result = validator.scan_text_tags(
            '{{SD:R1:(dateformat="MM/dd/yyyy hh:mm a z")}}', ["R1"]
        )
        self.assertEqual(result["errors"], [])

    def test_noncanonical_and_simple_sign_date_tags_are_rejected(self) -> None:
        for tag in (
            '{{SD:R1:(dateformat="MMM dd yyyy")}}',
            "{{SD:R1}}",
            '{{SD:R1*:(dateformat="MM/dd/yyyy hh:mm a z")}}',
        ):
            with self.subTest(tag=tag):
                self.assertEqual(
                    validator.classify_tag(tag, self.sign_registry)["classification"],
                    "invalid",
                )

    def test_combined_recipient_sign_dates_fail_with_first_recipient_reason(self) -> None:
        for tag in (
            '{{SD:R1,R2:(dateformat="MM/dd/yyyy hh:mm a z")}}',
            '{{SD:R1&R2:(dateformat="MM/dd/yyyy hh:mm a z")}}',
            '{{SD:R1|R2:(dateformat="MM/dd/yyyy hh:mm a z")}}',
            '{{SD:R1;R2:(dateformat="MM/dd/yyyy hh:mm a z")}}',
            '{{SD:R1+R2:(dateformat="MM/dd/yyyy hh:mm a z")}}',
            '{{SignDate:Recipient1,Recipient2:(dateformat="MM/dd/yyyy hh:mm a z")}}',
            '{{SignDate:Recipient1&Recipient2:(dateformat="MM/dd/yyyy hh:mm a z")}}',
            '{{SignDate:Recipients[1,2,3]:(dateformat="MM/dd/yyyy hh:mm a z")}}',
        ):
            with self.subTest(tag=tag):
                result = validator.classify_tag(tag, self.sign_registry)
                self.assertEqual(result["classification"], "invalid")
                self.assertIn("first parsed recipient", result["reason"])
                self.assertIn("one separate canonical tag", result["reason"])

    def test_manifest_signer_without_field_is_rejected(self) -> None:
        result = validator.scan_text_tags("{{S:R1}}", ["R1", "R2"])
        self.assertTrue(any("R2 has no assigned field" in error for error in result["errors"]))

    def test_tag_recipient_must_be_in_manifest(self) -> None:
        result = validator.scan_text_tags("{{S:R2}}", ["R1"])
        self.assertTrue(any("R2 is absent" in error for error in result["errors"]))

    def test_page_75_is_rejected(self) -> None:
        result = validator.scan_text_tags("{{S:R1}}", ["R1"], page_count=75)
        self.assertTrue(any("74 pages or fewer" in error for error in result["errors"]))

    def test_multiline_and_smart_quote_tags_are_rejected(self) -> None:
        multiline = validator.scan_text_tags("{{S:\nR1}}", ["R1"])
        self.assertTrue(multiline["errors"])
        wrapped_sign_date = validator.classify_tag(
            '{{SD:R1:(dateformat="MM/dd/yyyy\nhh:mm a z")}}'
        )
        self.assertEqual(wrapped_sign_date["classification"], "invalid")
        self.assertIn("one physical line", wrapped_sign_date["reason"])
        smart = validator.classify_tag(
            '{{SD:R1:(dateformat=“MM/dd/yyyy hh:mm a z”)}}'
        )
        self.assertEqual(smart["classification"], "invalid")

    def test_observed_sign_date_pipeline_constraints_are_locked(self) -> None:
        constraints = self.sign_registry["observed_pipeline_constraints"]
        multiple = constraints["multiple_recipient_field_ownership"]
        self.assertEqual(multiple["status"], "invalid")
        self.assertIn("first parsed recipient", multiple["observation"])

        table = constraints["table_cell_sign_date"]
        self.assertEqual(table["status"], "open_layout_smoke_test")
        self.assertIn("one physical line", table["official_rule"])
        self.assertIn("MM/dd/yyyy hh:mm a z", table["production_rule"])
        self.assertEqual(len(table["diagnostic_matrix"]), 10)
        self.assertEqual(
            table["diagnostic_matrix"][0]["tag"],
            '{{SD:R1:(dateformat="MM/dd/yyyy hh:mm a z")}}',
        )
        self.assertEqual(table["diagnostic_matrix"][-1]["tag"], "{{SD:R1}}")

    def test_official_document_field_catalog_is_complete(self) -> None:
        fields = [
            entry["field"]
            for entry in self.sign_registry["official_document_field_catalog"]
        ]
        self.assertEqual(fields, validator.OFFICIAL_SIGN_FIELDS)

    def test_initial_catalog_uses_canonical_unstarred_syntax(self) -> None:
        catalog = {
            entry["field"]: entry["text_tag_syntax"]
            for entry in self.sign_registry["official_document_field_catalog"]
        }
        self.assertEqual(catalog["Initial"], "{{I:R1}}")
        self.assertEqual(
            self.sign_registry["compatibility_aliases"][0]["alias_syntax"],
            "{{I:R1*}}",
        )

    def test_registry_exact_mapping_and_shape_are_locked(self) -> None:
        changed_syntax = copy.deepcopy(self.sign_registry)
        changed_syntax["production_safe_simple_tags"][0]["syntax"] = "{{TF:R1}}"
        self.assertTrue(validator.validate_sign_registry(changed_syntax))

        changed_field = copy.deepcopy(self.sign_registry)
        changed_field["production_safe_simple_tags"][0]["field"] = "Made Up"
        self.assertTrue(validator.validate_sign_registry(changed_field))

        changed_catalog = copy.deepcopy(self.sign_registry)
        changed_catalog["official_document_field_catalog"][0][
            "text_tag_syntax"
        ] = "{{TF:R1}}"
        self.assertTrue(validator.validate_sign_registry(changed_catalog))

        extra_key = copy.deepcopy(self.sign_registry)
        extra_key["unguarded"] = True
        self.assertTrue(validator.validate_sign_registry(extra_key))

    def test_all_published_longhand_and_shorthand_examples_are_locked(self) -> None:
        feature = next(
            entry
            for entry in self.sign_registry["official_but_ghre_blocked_features"]
            if entry["feature"] == "published_longhand_and_shorthand_examples"
        )
        self.assertEqual(feature["official_examples"], validator.PUBLISHED_LONG_SHORT_EXAMPLES)

    def test_fields_without_published_tag_syntax_remain_null(self) -> None:
        catalog = {
            entry["field"]: entry["text_tag_syntax"]
            for entry in self.sign_registry["official_document_field_catalog"]
        }
        self.assertEqual(
            {field for field, syntax in catalog.items() if syntax is None},
            validator.NO_PUBLISHED_TAG_FIELDS,
        )

    def test_typography_exact_values(self) -> None:
        typography = self.standard["typography"]
        self.assertEqual(typography, validator.EXPECTED_TYPOGRAPHY)
        self.assertEqual(
            self.standard["semantic_style_map"], validator.EXPECTED_SEMANTIC_STYLE_MAP
        )
        self.assertEqual(typography["body_text"]["font_family"], "Inter")
        self.assertEqual(typography["body_text"]["font_size_pt"], 11)
        self.assertEqual(typography["main_title"]["font_size_pt"], 18)
        self.assertEqual(typography["article_heading"]["color_hex"], "#1F4E79")
        self.assertEqual(typography["line_spacing"], 1.15)
        self.assertEqual(typography["paragraph_spacing_after_pt"], 6)
        self.assertEqual(
            typography["page"]["margins_in"],
            {"top": 0.75, "right": 0.75, "bottom": 0.75, "left": 0.75},
        )
        self.assertFalse(
            typography["paragraph_alignment"]["fully_justified_allowed"]
        )

    def test_checked_in_markdown_matches_renderers(self) -> None:
        self.assertEqual(
            self.paths["standard_markdown"].read_text(encoding="utf-8"),
            validator.render_authoring_markdown(self.standard),
        )
        self.assertEqual(
            self.paths["sign_markdown"].read_text(encoding="utf-8"),
            validator.render_sign_markdown(self.sign_registry),
        )

    def test_generated_markdown_drift_is_detected(self) -> None:
        errors = validator.markdown_drift_errors(
            self.standard,
            self.sign_registry,
            "stale\n",
            validator.render_sign_markdown(self.sign_registry),
        )
        self.assertEqual(errors, ["contract authoring Markdown is stale"])

    def test_recursive_clause_directory_validation_catches_future_records(self) -> None:
        clause_dir = self.root / "src/zoho-contracts/clauses"
        self.assertEqual(
            validator.validate_clause_directory(self.root, self.standard), []
        )

        invalid = self.valid_clause()
        invalid["clause_type"] = "Miscellaneous"
        invalid_path = clause_dir / ".validator-test-invalid.clause.json"
        try:
            invalid_path.write_text(json.dumps(invalid), encoding="utf-8")
            errors = validator.validate_clause_directory(self.root, self.standard)
            self.assertTrue(
                any(".validator-test-invalid.clause.json" in error for error in errors)
            )
        finally:
            invalid_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
