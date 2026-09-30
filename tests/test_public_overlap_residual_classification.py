from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

spec = importlib.util.spec_from_file_location(
    "classify_public_overlap_residuals",
    TOOLS / "classify_public_overlap_residuals.py",
)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)


class ResidualClassificationTests(unittest.TestCase):
    def test_core_public_global_is_not_promoted(self):
        row={"provenance_scope":"CORE_PUBLIC_TEXT_ONLY","mirror_source_id":None,"mirror_faction_id":None}
        self.assertEqual(mod.classify_unscoped(row, {}), "CORE_PUBLIC_GLOBAL")

    def test_non_11_source_is_explicit(self):
        sources={"x":{"edition":"0","name":"Example Legends"}}
        row={"provenance_scope":"GLOBAL_PUBLIC_TEXT_ONLY","mirror_source_id":"x","mirror_faction_id":"F"}
        self.assertEqual(mod.classify_unscoped(row, sources), "NON_11_OR_LEGENDS_SOURCE")

    def test_short_no_exact_is_extraction_limited(self):
        unit={"comparison_char_count":20,"token_count":4,"source_id":"x","faction_id":"F"}
        self.assertEqual(mod.classify_no_exact(unit, {}), "TOO_SHORT_FOR_SAFE_AUTO_MATCH")

    def test_edition_11_no_exact_remains_unresolved(self):
        sources={"x":{"edition":"11","name":"Current Pack"}}
        unit={"comparison_char_count":100,"token_count":20,"source_id":"x","faction_id":"F"}
        self.assertEqual(mod.classify_no_exact(unit, sources), "EDITION_11_SOURCE_NO_EXACT_PUBLIC_OVERLAP")


if __name__ == "__main__":
    unittest.main()
