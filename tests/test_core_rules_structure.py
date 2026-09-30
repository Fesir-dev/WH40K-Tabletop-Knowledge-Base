from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

spec = importlib.util.spec_from_file_location(
    "build_core_rules_structure",
    TOOLS / "build_core_rules_structure.py",
)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)


class CoreRulesStructureTests(unittest.TestCase):
    def test_heading_candidate(self):
        self.assertTrue(mod.is_heading_candidate("MOVEMENT PHASE"))
        self.assertTrue(mod.is_heading_candidate("1. Core Concepts"))
        self.assertFalse(mod.is_heading_candidate("This is a normal sentence ending with a period."))

    def test_clean_label_is_bounded(self):
        value = mod.clean_short_label("  A\b  B\ufffd  ")
        self.assertEqual(value, "A B")

    def test_assign_ranges_and_children(self):
        rows = [
            {"title":"A","depth":0,"page_start":1},
            {"title":"A1","depth":1,"page_start":2},
            {"title":"B","depth":0,"page_start":5},
        ]
        page_sha = [str(i) for i in range(1, 9)]
        sections = mod.assign_ranges(rows, 8, page_sha, {})
        self.assertEqual(sections[0]["page_end"], 4)
        self.assertEqual(sections[1]["page_end"], 4)
        self.assertEqual(sections[2]["page_end"], 8)
        self.assertEqual(sections[0]["children"], [sections[1]["section_key"]])

    def test_repeated_heading_noise_is_filtered(self):
        pages = ["HEADER\nUNIQUE ONE\n" for _ in range(5)]
        result = mod.heading_candidates(pages)
        self.assertTrue(all("HEADER" not in rows for rows in result.values()))

    def test_rule_reference_families_use_heading_refs(self):
        candidates = {
            2:["CORE 01.01"],
            4:["MOVE 01.04"],
            7:["ATTACK 02.01"],
        }
        rows = mod.build_rule_reference_families(candidates, 10, [str(i) for i in range(10)])
        self.assertEqual([x["family_id"] for x in rows], ["01","02"])
        self.assertEqual(rows[0]["page_start"], 2)
        self.assertEqual(rows[0]["page_end"], 6)
        self.assertEqual(rows[1]["page_end"], 10)

    def test_distant_cross_reference_does_not_move_family_start(self):
        candidates = {
            17:["SEE 24.07","SEE 24.11"],
            78:["ABILITIES 24.01"],
            82:["HEAVY 24.16","HOVER 24.17","LEADER 24.22"],
        }
        rows = mod.build_rule_reference_families(candidates, 88, [str(i) for i in range(88)])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["canonical_anchor_page"], 82)
        self.assertEqual(rows[0]["page_start"], 78)
        self.assertEqual(rows[0]["page_end"], 88)


if __name__ == "__main__":
    unittest.main()
