from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))

from build_core_rule_paragraph_boundaries import (  # noqa: E402
    build_line_records,
    occurrence_classification,
    paragraph_candidates,
    trim_selected,
)


class CoreRuleParagraphBoundaryContracts(unittest.TestCase):
    def test_line_records_keep_exact_offsets(self):
        text="HEAD\n\nalpha beta\nomega"
        rows=build_line_records(text)
        self.assertEqual([x["line"] for x in rows],[1,2,3,4])
        self.assertEqual(rows[0]["char_start"],0)
        self.assertEqual(text[rows[2]["char_start"]:rows[2]["char_end"]],"alpha beta")
        self.assertEqual(text[rows[3]["char_start"]:rows[3]["char_end"]],"omega")

    def test_trim_selected_removes_only_outer_blank_lines(self):
        rows=build_line_records("\nalpha\n\nbeta\n")
        selected=[(1,row) for row in rows]
        trimmed=trim_selected(selected)
        self.assertEqual(trimmed[0][1]["clean"],"alpha")
        self.assertEqual(trimmed[-1][1]["clean"],"beta")
        self.assertTrue(any(not x[1]["clean"] for x in trimmed))

    def test_paragraph_candidates_are_page_local_blank_line_groups(self):
        text="alpha\nbeta\n\ngamma\n"
        rows=build_line_records(text)
        selected=[(1,row) for row in rows]
        out=paragraph_candidates(selected,[text])
        self.assertEqual(len(out),2)
        self.assertEqual(out[0]["line_start"],1)
        self.assertEqual(out[0]["line_end"],2)
        self.assertEqual(out[1]["line_start"],4)
        self.assertEqual(out[1]["line_end"],4)
        self.assertTrue(all(len(x["semantic_sha256"])==64 for x in out))

    def test_single_occurrence_classification(self):
        self.assertEqual(
            occurrence_classification([{"state":"BOUNDARY_RESOLVED","body_semantic_sha256":"a"*64}]),
            "SINGLE_OCCURRENCE_BOUNDARY",
        )

    def test_repeated_identical_hash_classification(self):
        occ=[
            {"state":"BOUNDARY_RESOLVED","body_semantic_sha256":"a"*64},
            {"state":"BOUNDARY_RESOLVED","body_semantic_sha256":"a"*64},
        ]
        self.assertEqual(
            occurrence_classification(occ),
            "REPEATED_OCCURRENCE_BOUNDARIES_IDENTICAL_HASH",
        )

    def test_repeated_variant_hash_classification(self):
        occ=[
            {"state":"BOUNDARY_RESOLVED","body_semantic_sha256":"a"*64},
            {"state":"BOUNDARY_RESOLVED","body_semantic_sha256":"b"*64},
        ]
        self.assertEqual(
            occurrence_classification(occ),
            "REPEATED_OCCURRENCE_BOUNDARIES_VARIANT_HASH",
        )

    def test_gap_and_empty_fail_closed(self):
        self.assertEqual(
            occurrence_classification([{"state":"HEADING_LINE_RECOVERY_GAP"}]),
            "HEADING_LINE_RECOVERY_GAP",
        )
        self.assertEqual(
            occurrence_classification([{"state":"EMPTY_BODY_BOUNDARY"}]),
            "EMPTY_BODY_BOUNDARY",
        )


if __name__=="__main__":
    unittest.main()
