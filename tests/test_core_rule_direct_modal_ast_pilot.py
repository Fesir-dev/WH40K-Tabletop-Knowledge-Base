from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))

from build_core_rule_direct_modal_ast_pilot import split_direct_can, token_count  # noqa: E402


class DirectModalAstPilotContracts(unittest.TestCase):
    def test_direct_modal_split(self):
        raw="A selected model can perform one action."
        parts=split_direct_can(raw,100)
        self.assertEqual(parts["modal_operator"]["operator"],"PERMISSION")
        self.assertEqual(parts["modal_operator"]["lexical_signal"],"PERMISSION_CAN")
        self.assertEqual(parts["subject_span"]["token_count"],3)
        self.assertEqual(parts["modal_operator"]["token_count"],1)
        self.assertEqual(parts["action_predicate_span"]["token_count"],3)
        self.assertEqual(
            parts["subject_span"]["token_count"]+
            parts["modal_operator"]["token_count"]+
            parts["action_predicate_span"]["token_count"],
            token_count(raw),
        )
        self.assertEqual(parts["subject_span"]["absolute_char_start"],100)
        self.assertGreater(parts["action_predicate_span"]["absolute_char_start"],100)

    def test_split_rejects_missing_modal(self):
        with self.assertRaises(RuntimeError):
            split_direct_can("A selected model performs one action.",0)

    def test_split_rejects_multiple_modal_tokens(self):
        with self.assertRaises(RuntimeError):
            split_direct_can("A model can move and can shoot.",0)

    def test_cannot_is_not_standalone_can(self):
        with self.assertRaises(RuntimeError):
            split_direct_can("A model cannot move.",0)

    def test_subject_must_be_nonempty(self):
        with self.assertRaises(RuntimeError):
            split_direct_can("can perform one action.",0)

    def test_predicate_must_be_nonempty(self):
        with self.assertRaises(RuntimeError):
            split_direct_can("A model can",0)


if __name__=="__main__":
    unittest.main()
