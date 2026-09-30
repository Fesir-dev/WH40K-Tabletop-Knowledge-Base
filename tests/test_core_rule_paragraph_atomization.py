from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))

from build_core_rule_paragraph_atoms import (  # noqa: E402
    candidate_within_spans,
    make_paragraph_key,
    paragraph_classification,
)


class CoreRuleParagraphAtomizationContracts(unittest.TestCase):
    def test_stable_key_uses_parent_occurrence_page_and_ordinal(self):
        self.assertEqual(
            make_paragraph_key("core-rule-01-02--p8--l13",8,2),
            "core-rule-01-02--p8--l13--para-p8-o2",
        )

    def test_single_occurrence_classification(self):
        self.assertEqual(
            paragraph_classification({"occurrence_count":1}),
            "SINGLE_OCCURRENCE_PARAGRAPH",
        )

    def test_repeated_occurrence_classification(self):
        self.assertEqual(
            paragraph_classification({"occurrence_count":2}),
            "REPEATED_OCCURRENCE_PARAGRAPH_VARIANT",
        )

    def test_candidate_must_be_inside_one_parent_page_span(self):
        spans=[{
            "page":8,
            "line_start":10,
            "line_end":20,
            "char_start":100,
            "char_end":500,
        }]
        good={
            "page":8,
            "line_start":12,
            "line_end":18,
            "char_start":150,
            "char_end":400,
        }
        bad_page={**good,"page":9}
        bad_range={**good,"char_end":600}
        self.assertTrue(candidate_within_spans(good,spans))
        self.assertFalse(candidate_within_spans(bad_page,spans))
        self.assertFalse(candidate_within_spans(bad_range,spans))


if __name__=="__main__":
    unittest.main()
