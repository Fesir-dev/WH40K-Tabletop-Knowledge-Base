from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))

from validate_core_rule_direct_modal_ast_semantics import (  # noqa: E402
    action_head,
    canonical_tokens,
    classify_predicate,
    classify_subject,
)


class CoreRuleDirectModalSemanticValidationContracts(unittest.TestCase):
    def test_subject_closed_lexicon(self):
        row=classify_subject("Units",{})
        self.assertTrue(row["resolved"])
        self.assertEqual(row["semantic_type"],"UNIT")

    def test_unknown_subject_stays_opaque(self):
        row=classify_subject("Something",{})
        self.assertFalse(row["resolved"])
        self.assertEqual(row["semantic_type"],"OPAQUE_SUBJECT_SPAN")

    def test_action_head_closed_lexicon(self):
        self.assertEqual(action_head(["fall","back","up","to","6"]),( "FALL_BACK",2))
        self.assertEqual(action_head(["move","up","to","6"]),( "MOVE",1))

    def test_simple_predicate_can_decompose(self):
        row=classify_predicate("move up to 6 inches.",{})
        self.assertTrue(row["decomposable"])
        self.assertEqual(row["action_type"],"MOVE")
        self.assertEqual(row["blockers"],[])

    def test_coordination_blocks_predicate_decomposition(self):
        row=classify_predicate("move and shoot.",{})
        self.assertFalse(row["decomposable"])
        self.assertIn("COORDINATION_CUE",row["blockers"])

    def test_second_modal_blocks_predicate_decomposition(self):
        row=classify_predicate("move if it can see the target.",{})
        self.assertFalse(row["decomposable"])
        self.assertIn("ADDITIONAL_MODAL_CUE",row["blockers"])
        self.assertIn("CONDITION_CUE",row["blockers"])


if __name__=="__main__":
    unittest.main()
