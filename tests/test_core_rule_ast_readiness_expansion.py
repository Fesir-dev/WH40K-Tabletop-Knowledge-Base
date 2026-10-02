from __future__ import annotations

import unittest
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))

from audit_core_rule_ast_readiness_expansion import (  # noqa: E402
    analyze_row,
    sentence_ranges,
)


class CoreRuleAstReadinessExpansionContracts(unittest.TestCase):
    def parent(self, **overrides):
        row={
            "readiness_state":"BLOCKED_SENTENCE_SHAPE",
            "modal_axis":"PERMISSION",
            "modal_occurrences":1,
            "condition_cues":0,
        }
        row.update(overrides)
        return row

    def test_sentence_ranges_preserve_two_sentences(self):
        rows=sentence_ranges("Models move. Units can shoot.")
        self.assertEqual(len(rows),2)
        self.assertTrue(all(x["terminal"] for x in rows))

    def test_single_modal_sentence_candidate(self):
        raw="Models move normally. Units can shoot."
        r=analyze_row(raw,self.parent(),0)
        self.assertEqual(r["expansion_state"],"CANDIDATE_SINGLE_MODAL_SENTENCE")
        self.assertEqual(r["modal_sentence_ordinal"],2)
        self.assertEqual(r["candidate"]["modal_occurrences"],1)
        self.assertEqual(r["candidate"]["condition_cues"],0)

    def test_condition_must_be_inside_modal_sentence(self):
        raw="If an enemy is visible, resolve this step. Units can shoot."
        r=analyze_row(raw,self.parent(condition_cues=1),0)
        self.assertEqual(r["expansion_state"],"BLOCKED_CONDITION_OUTSIDE_MODAL_SENTENCE")

    def test_condition_inside_modal_sentence_is_candidate(self):
        raw="Resolve the previous step. If an enemy is visible, units can shoot."
        r=analyze_row(raw,self.parent(condition_cues=1),0)
        self.assertEqual(r["expansion_state"],"CANDIDATE_SINGLE_MODAL_SENTENCE")
        self.assertEqual(r["candidate"]["condition_cues"],1)

    def test_modal_sentence_colon_stays_blocked(self):
        raw="Resolve the previous step. Units can shoot: resolve attacks."
        r=analyze_row(raw,self.parent(),0)
        self.assertEqual(r["expansion_state"],"BLOCKED_MODAL_SENTENCE_COMPLEX_DELIMITERS")

    def test_modal_sentence_parenthetical_stays_blocked(self):
        raw="Resolve the previous step. Units can shoot (if eligible)."
        r=analyze_row(raw,self.parent(condition_cues=1),0)
        self.assertEqual(r["expansion_state"],"BLOCKED_MODAL_SENTENCE_PARENTHETICAL_SCOPE")

    def test_original_delimiter_parent_never_promotes(self):
        raw="If eligible: units can shoot."
        r=analyze_row(raw,self.parent(
            readiness_state="BLOCKED_COMPLEX_DELIMITERS",
            condition_cues=1,
        ),0)
        self.assertEqual(r["expansion_state"],"BLOCKED_DELIMITER_SCOPE")
        self.assertIsNone(r["candidate"])

    def test_original_parenthetical_parent_never_promotes(self):
        raw="Units must move (if able)."
        r=analyze_row(raw,self.parent(
            readiness_state="BLOCKED_PARENTHETICAL_SCOPE",
            modal_axis="OBLIGATION",
        ),0)
        self.assertEqual(r["expansion_state"],"BLOCKED_PARENTHETICAL_SCOPE")
        self.assertIsNone(r["candidate"])


if __name__=="__main__":
    unittest.main()
