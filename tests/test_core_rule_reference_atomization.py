from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))

from build_core_rule_reference_atoms import (  # noqa: E402
    classify_heading_evidence,
    ref_rx,
)


class CoreRuleReferenceAtomizationContracts(unittest.TestCase):
    def test_reference_regex_is_exact_numbered_identity(self):
        rx=ref_rx("09.05")
        self.assertTrue(rx.search("RULE 09.05"))
        self.assertTrue(rx.search("09.05: ADVANCE"))
        self.assertFalse(rx.search("109.05"))
        self.assertFalse(rx.search("09.050"))

    def test_unique_heading_classification(self):
        self.assertEqual(
            classify_heading_evidence({33:["ADVANCE MOVES 09.05"]}),
            "UNIQUE_IN_FAMILY_HEADING",
        )

    def test_repeated_heading_classification(self):
        self.assertEqual(
            classify_heading_evidence({
                54:["USING STRATAGEMS 15.01"],
                56:["USING STRATAGEMS 15.01"],
            }),
            "REPEATED_IN_FAMILY_HEADING",
        )

    def test_same_page_multiple_labels_is_ambiguous(self):
        self.assertEqual(
            classify_heading_evidence({
                55:["RAPID INGRESS 15.07","15.07 RAPID INGRESS"]
            }),
            "MULTIPLE_LABELS_SAME_PAGE",
        )

    def test_missing_heading_fails_closed(self):
        self.assertEqual(
            classify_heading_evidence({}),
            "HEADING_RECOVERY_GAP",
        )


if __name__=="__main__":
    unittest.main()
