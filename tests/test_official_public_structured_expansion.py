from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class StructuredExpansionRepositoryTests(unittest.TestCase):
    def test_core_structure_and_residual_boundaries(self):
        core=json.loads((ROOT/"reports"/"CORE_RULES_STRUCTURE_CURRENT.json").read_text(encoding="utf-8"))
        residual=json.loads((ROOT/"reports"/"OFFICIAL_PUBLIC_OVERLAP_RESIDUAL_CLASSIFICATION_CURRENT.json").read_text(encoding="utf-8"))
        current=json.loads((ROOT/"rules"/"11e"/"current.json").read_text(encoding="utf-8"))
        coverage=json.loads((ROOT/"coverage"/"current.json").read_text(encoding="utf-8"))

        self.assertEqual(core["status"],"PASS")
        self.assertEqual(core["summary"]["rule_reference_family_ids"],[f"{i:02d}" for i in range(1,25)])
        self.assertEqual(core["summary"]["rule_reference_count"],141)
        self.assertTrue(core["authority_boundary"]["section_level_structure_complete_for_public_pdf"])
        self.assertFalse(core["authority_boundary"]["hierarchical_structure_complete"])
        self.assertFalse(core["authority_boundary"]["paragraph_level_rules_ast_complete"])

        self.assertEqual(residual["unscoped_exact"]["total"],1566)
        self.assertEqual(residual["no_exact_public_overlap"]["total"],7936)
        self.assertEqual(residual["summary"]["promoted_units"],0)
        self.assertEqual(residual["summary"]["semantic_conflicts_created"],0)
        self.assertFalse(residual["authority_boundary"]["no_exact_is_conflict"])
        self.assertFalse(residual["authority_boundary"]["unscoped_exact_is_promotable"])

        layer=current["official_public_structured_normalization_expansion"]
        self.assertEqual(layer["state"],"PASS_SCOPED_EXPANSION_V1")
        self.assertEqual(layer["current_normalized_factions_change"],0)
        self.assertEqual(current["next_milestone"],"CORE_RULE_REFERENCE_ATOMIZATION_V1")

        self.assertEqual(coverage["global"]["current_normalized_factions"],0)
        self.assertEqual(coverage["global"]["full_normative_semantic_factions"],0)
        self.assertEqual(coverage["global"]["official_public_residual_promoted_units"],0)
        self.assertEqual(coverage["global"]["official_public_residual_semantic_conflicts_created"],0)


if __name__=="__main__":
    unittest.main()
