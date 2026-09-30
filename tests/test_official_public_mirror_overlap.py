from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

spec = importlib.util.spec_from_file_location(
    "audit_official_public_mirror_overlap",
    TOOLS / "audit_official_public_mirror_overlap.py",
)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)


class OverlapContractTests(unittest.TestCase):
    def test_overlap_normalization_collapses_html_unicode_and_punctuation(self):
        left = mod.overlap_normalize("<b>Rapid—Fire</b> 2 &amp; TEST")
        right = mod.overlap_normalize("rapid-fire 2 & TEST")
        self.assertEqual(left, right)
        self.assertEqual(left, "rapid fire 2 test")

    def test_short_units_are_not_anchor_eligible(self):
        row = mod.unit_record(
            "ability",
            "ability:x:_",
            {"id": "x"},
            "Very short text",
        )
        self.assertIsNotNone(row)
        self.assertIsNone(row["_anchor"])

    def test_direct_source_scope_wins(self):
        unit = {"source_id": "000000024", "faction_id": "AC"}
        hits = [
            {
                "document_id": "GW_11E_FACTION_PACK_000000024",
                "document_type": "FACTION_PACK",
            },
            {
                "document_id": "GW_11E_CORE_RULES_PUBLIC",
                "document_type": "CORE_RULES",
            },
        ]
        scope, scoped = mod.classify_provenance(
            unit,
            hits,
            {"000000024": "GW_11E_FACTION_PACK_000000024"},
            {"AC": "000000024"},
        )
        self.assertEqual(scope, "DIRECT_SOURCE_SCOPED")
        self.assertEqual(len(scoped), 1)
        self.assertEqual(scoped[0]["document_id"], "GW_11E_FACTION_PACK_000000024")

    def test_core_only_match_is_not_promotable(self):
        unit = {"source_id": None, "faction_id": None}
        hits = [
            {
                "document_id": "GW_11E_CORE_RULES_PUBLIC",
                "document_type": "CORE_RULES",
            }
        ]
        scope, _ = mod.classify_provenance(unit, hits, {}, {})
        self.assertEqual(scope, "CORE_PUBLIC_TEXT_ONLY")
        self.assertNotIn(scope, mod.PROMOTABLE_SCOPES)

    def test_multi_document_classification(self):
        hits = [
            {"document_id": "a"},
            {"document_id": "b"},
        ]
        self.assertEqual(
            mod.public_match_classification(hits),
            "EXACT_NORMALIZED_TEXT_MATCH_MULTI_OFFICIAL",
        )


if __name__ == "__main__":
    unittest.main()
