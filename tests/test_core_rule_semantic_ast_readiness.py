from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))

from audit_core_rule_semantic_ast_readiness import pre_shape_gate, range_shape, shape_gate  # noqa: E402


def semantic(signals):
    return {"signals":[{"id":k,"count":v} for k,v in signals.items()]}


def profile(**kw):
    base={
        "review_state":"AXIS_PROFILE_READY",
        "modal_axis":"PERMISSION",
        "procedure_sequence_present":False,
        "definition_present":False,
        "modification_replacement_present":False,
        "reference_present":False,
        "structural_list_present":False,
        "parent_paragraph_classification":"SINGLE_OCCURRENCE_PARAGRAPH",
    }
    base.update(kw)
    return base


class CoreSemanticAstReadinessContracts(unittest.TestCase):
    def test_parent_review_blocked_first(self):
        state,_=pre_shape_gate(profile(review_state="MULTI_MODAL_REVIEW_REQUIRED",modal_axis="MULTI_MODAL"),semantic({}))
        self.assertEqual(state,"BLOCKED_PARENT_REVIEW")

    def test_no_modal_is_blocked(self):
        state,_=pre_shape_gate(profile(modal_axis="NONE"),semantic({"CONDITION_IF":1}))
        self.assertEqual(state,"BLOCKED_NO_NORMATIVE_MODAL")

    def test_modal_multiplicity_is_blocked(self):
        state,_=pre_shape_gate(profile(),semantic({"PERMISSION_CAN":2}))
        self.assertEqual(state,"BLOCKED_MODAL_MULTIPLICITY")

    def test_complex_axis_is_blocked(self):
        state,_=pre_shape_gate(profile(definition_present=True),semantic({"PERMISSION_CAN":1,"DEFINITION_MEANS":1}))
        self.assertEqual(state,"BLOCKED_COMPLEX_SEMANTIC_AXES")

    def test_multiple_conditions_are_blocked(self):
        state,e=pre_shape_gate(profile(),semantic({"PERMISSION_CAN":1,"CONDITION_IF":1,"TRIGGER_WHEN":1}))
        self.assertEqual(e["condition_cues"],2)
        self.assertEqual(state,"BLOCKED_MULTIPLE_CONDITION_CUES")

    def test_repeated_variant_is_blocked(self):
        state,_=pre_shape_gate(
            profile(parent_paragraph_classification="REPEATED_OCCURRENCE_PARAGRAPH_VARIANT"),
            semantic({"PERMISSION_CAN":1}),
        )
        self.assertEqual(state,"BLOCKED_REPEATED_VARIANT")

    def test_simple_modal_reaches_shape_gate(self):
        state,e=pre_shape_gate(profile(),semantic({"PERMISSION_CAN":1}))
        self.assertIsNone(state)
        self.assertEqual(e["modal_occurrences"],1)
        self.assertEqual(e["condition_cues"],0)

    def test_shape_direct_modal(self):
        shape=range_shape("A unit can act.")
        self.assertEqual(shape_gate(shape,0),"PILOT_READY_DIRECT_MODAL")

    def test_shape_conditional_modal(self):
        shape=range_shape("If this happens, a unit can act.")
        self.assertEqual(shape_gate(shape,1),"PILOT_READY_CONDITIONAL_MODAL")

    def test_shape_blocks_multi_sentence(self):
        shape=range_shape("A unit can act. It moves.")
        self.assertEqual(shape_gate(shape,0),"BLOCKED_SENTENCE_SHAPE")

    def test_shape_blocks_semicolon(self):
        shape=range_shape("A unit can act; it moves.")
        self.assertEqual(shape_gate(shape,0),"BLOCKED_COMPLEX_DELIMITERS")

    def test_shape_blocks_parenthetical(self):
        shape=range_shape("A unit can act (once).")
        self.assertEqual(shape_gate(shape,0),"BLOCKED_PARENTHETICAL_SCOPE")


if __name__=="__main__":
    unittest.main()
