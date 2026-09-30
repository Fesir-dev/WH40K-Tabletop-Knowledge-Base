from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))

from review_core_rule_paragraph_semantics import review_profile  # noqa: E402


def row(families:dict, signals=None, role="MIXED", confidence="MIXED"):
    return {
        "paragraph_key":"p",
        "rule_ref":"01.01",
        "rule_key":"core-rule-01-01",
        "family_id":"01",
        "occurrence_key":"o",
        "occurrence_ordinal":1,
        "paragraph_ordinal_in_occurrence":1,
        "parent_paragraph_classification":"SINGLE_OCCURRENCE_PARAGRAPH",
        "primary_role":role,
        "classification_confidence":confidence,
        "semantic_sha256":"0"*64,
        "signal_family_counts":families,
        "signals":signals or [],
    }


class CoreParagraphSemanticReviewContracts(unittest.TestCase):
    def test_condition_plus_permission_is_axis_profile_ready(self):
        r=review_profile(row({"CONDITION_OR_TRIGGER":1,"PERMISSION":1}))
        self.assertEqual(r["modal_axis"],"PERMISSION")
        self.assertTrue(r["condition_trigger_present"])
        self.assertEqual(r["review_state"],"AXIS_PROFILE_READY")

    def test_permission_plus_prohibition_is_multi_modal(self):
        r=review_profile(row({"PERMISSION":1,"PROHIBITION":1}))
        self.assertEqual(r["modal_axis"],"MULTI_MODAL")
        self.assertEqual(r["review_state"],"MULTI_MODAL_REVIEW_REQUIRED")

    def test_definition_plus_modification_is_axis_profile_ready(self):
        r=review_profile(row({"DEFINITION":1,"MODIFICATION_OR_REPLACEMENT":1}))
        self.assertEqual(r["modal_axis"],"NONE")
        self.assertTrue(r["definition_present"])
        self.assertTrue(r["modification_replacement_present"])
        self.assertEqual(r["review_state"],"AXIS_PROFILE_READY")

    def test_bullet_only_is_no_strong_signal(self):
        r=review_profile(row({},signals=[{"id":"BULLET_LIKE","count":3}],role="UNCLASSIFIED",confidence="NONE"))
        self.assertTrue(r["structural_list_present"])
        self.assertEqual(r["review_state"],"NO_STRONG_SIGNAL_REVIEW_REQUIRED")

    def test_reference_only_is_no_strong_signal(self):
        r=review_profile(row({"REFERENCE_OR_CROSS_REFERENCE":1},role="REFERENCE_OR_CROSS_REFERENCE",confidence="HIGH"))
        self.assertTrue(r["reference_present"])
        self.assertEqual(r["review_state"],"NO_STRONG_SIGNAL_REVIEW_REQUIRED")

    def test_single_obligation_is_axis_profile_ready(self):
        r=review_profile(row({"OBLIGATION":1},role="OBLIGATION",confidence="HIGH"))
        self.assertEqual(r["modal_axis"],"OBLIGATION")
        self.assertEqual(r["review_state"],"AXIS_PROFILE_READY")


if __name__=="__main__":
    unittest.main()
