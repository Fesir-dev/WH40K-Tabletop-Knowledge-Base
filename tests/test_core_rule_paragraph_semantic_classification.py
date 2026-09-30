from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))

from classify_core_rule_paragraph_semantics import (  # noqa: E402
    classify_paragraph,
    count_signals,
    choose_role,
    family_counts,
)


class CoreRuleParagraphSemanticClassificationContracts(unittest.TestCase):
    def test_must_not_is_prohibition_not_obligation(self):
        result=classify_paragraph("A model must not move.")
        self.assertEqual(result["primary_role"],"PROHIBITION")
        ids={x["id"] for x in result["signals"]}
        self.assertIn("PROHIBITION_MUST_NOT",ids)
        self.assertNotIn("OBLIGATION_MUST",ids)

    def test_cannot_is_prohibition_not_permission_can(self):
        result=classify_paragraph("This unit cannot shoot.")
        self.assertEqual(result["primary_role"],"PROHIBITION")
        ids={x["id"] for x in result["signals"]}
        self.assertIn("PROHIBITION_CANNOT",ids)
        self.assertNotIn("PERMISSION_CAN",ids)

    def test_permission_is_clean_single_role(self):
        result=classify_paragraph("A unit can make this move.")
        self.assertEqual(result["primary_role"],"PERMISSION")
        self.assertEqual(result["classification_confidence"],"HIGH")

    def test_conditional_obligation_is_mixed(self):
        result=classify_paragraph("If this happens, the model must move.")
        self.assertEqual(result["primary_role"],"MIXED")
        self.assertEqual(result["classification_confidence"],"MIXED")
        self.assertEqual(set(result["signal_family_counts"]),{"CONDITION_OR_TRIGGER","OBLIGATION"})

    def test_reference_only_is_reference_role(self):
        result=classify_paragraph("See rule 12.03.")
        self.assertEqual(result["primary_role"],"REFERENCE_OR_CROSS_REFERENCE")
        self.assertEqual(result["classification_confidence"],"HIGH")

    def test_definition_is_definition(self):
        result=classify_paragraph("This means the selected model.")
        self.assertEqual(result["primary_role"],"DEFINITION")

    def test_replacement_is_modification(self):
        result=classify_paragraph("Use this value instead.")
        self.assertEqual(result["primary_role"],"MODIFICATION_OR_REPLACEMENT")

    def test_no_signal_is_unclassified(self):
        result=classify_paragraph("Models are placed on the battlefield.")
        self.assertEqual(result["primary_role"],"UNCLASSIFIED")
        self.assertEqual(result["classification_confidence"],"NONE")

    def test_reference_is_weak_beside_strong_role(self):
        signals=count_signals("A model must move; see rule 12.03.")
        role,confidence=choose_role(family_counts(signals))
        self.assertEqual(role,"OBLIGATION")
        self.assertEqual(confidence,"HIGH")


if __name__=="__main__":
    unittest.main()
