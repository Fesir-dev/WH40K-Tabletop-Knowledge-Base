import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))

from audit_normative_equivalence_gaps import build_audit  # noqa: E402


class NormativeEquivalenceGapAuditContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.generated=build_audit(ROOT)
        cls.committed=json.loads((ROOT/"reports/NORMATIVE_APP_EQUIVALENCE_GAP_AUDIT_CURRENT.json").read_text(encoding="utf-8"))

    def test_report_is_reproducible(self):
        self.assertEqual(self.generated,self.committed)

    def test_authority_boundary(self):
        a=self.generated["authority_boundary"]
        self.assertEqual(a["normative_authority"],"GAMES_WORKSHOP")
        self.assertFalse(a["mirror_hash_match_is_normative_equivalence"])
        self.assertFalse(a["faction_pack_is_full_codex_replacement"])
        self.assertFalse(a["app_wording_inference_allowed"])

    def test_current_zero_is_intentional_normative_threshold(self):
        c=self.generated["coverage_summary"]
        self.assertEqual(c["roster_universe"],37)
        self.assertEqual(c["current_normalized_factions"],0)
        self.assertEqual(c["full_normative_semantic_factions"],0)
        self.assertEqual(c["secondary_semantic_current_roster_identities"],35)
        self.assertTrue(all(v==0 for v in c["normative_semantic_complete_by_dimension"].values()))
        self.assertTrue(all(v==37 for v in c["normative_semantic_zero_by_dimension"].values()))

    def test_mfm_normative_dimensions_are_closed(self):
        closed={x["id"]:x for x in self.generated["closed_layers"]}
        mfm=closed["MFM_NORMATIVE_DIMENSIONS"]
        self.assertEqual(mfm["state"],"CLOSED_CURRENT_NORMATIVE")
        complete=mfm["evidence"]["complete_roster_identities_by_dimension"]
        self.assertTrue(all(v==36 for v in complete.values()))

    def test_public_core_rules_fingerprint_and_section_structure_are_closed(self):
        gaps={x["id"]:x for x in self.generated["gaps"]}
        core=gaps["OFFICIAL_CORE_RULES_SEMANTIC_INGESTION"]
        self.assertEqual(core["state"],"SEMANTIC_AST_READINESS_CLOSED_DIRECT_MODAL_PILOT_PENDING")
        self.assertEqual(core["evidence"]["official_fingerprint_state"],"PASS")
        self.assertEqual(core["evidence"]["section_structure_state"],"PASS_RULE_REFERENCE_FAMILIES_01_24")
        self.assertEqual(core["evidence"]["rule_reference_families"],24)
        self.assertEqual(core["evidence"]["rule_reference_count"],141)
        self.assertFalse(core["evidence"]["paragraph_level_rules_ast_complete"])
        self.assertEqual(core["evidence"]["rule_atomization_state"],"PASS_141_RULE_ATOMS")
        self.assertEqual(core["evidence"]["rule_atoms"],141)
        self.assertEqual(core["evidence"]["rule_atom_classification_counts"],{
            "REPEATED_IN_FAMILY_HEADING":5,
            "UNIQUE_IN_FAMILY_HEADING":136,
        })
        self.assertEqual(core["evidence"]["atoms_with_cross_references"],40)
        self.assertEqual(core["evidence"]["paragraph_boundary_state"],"PASS_141_RULE_BOUNDARIES")
        self.assertEqual(core["evidence"]["boundary_occurrences"],146)
        self.assertEqual(core["evidence"]["paragraph_candidates"],310)
        self.assertEqual(core["evidence"]["paragraph_atomization_state"],"PASS_310_PARAGRAPH_ATOMS")
        self.assertEqual(core["evidence"]["paragraph_atoms"],310)
        self.assertEqual(core["evidence"]["paragraph_atom_classification_counts"],{
            "REPEATED_OCCURRENCE_PARAGRAPH_VARIANT":10,
            "SINGLE_OCCURRENCE_PARAGRAPH":300,
        })
        self.assertEqual(core["evidence"]["paragraph_range_validation_failures"],0)
        self.assertEqual(core["evidence"]["paragraph_semantic_classification_state"],"PASS_310_PARAGRAPHS_CLASSIFIED")
        self.assertEqual(core["evidence"]["paragraph_semantic_role_counts"],{
            "CONDITION_OR_TRIGGER":31,
            "MIXED":134,
            "MODIFICATION_OR_REPLACEMENT":1,
            "OBLIGATION":1,
            "PERMISSION":20,
            "PROCEDURE_OR_SEQUENCE":7,
            "PROHIBITION":4,
            "UNCLASSIFIED":112,
        })
        self.assertEqual(core["evidence"]["paragraph_semantic_confidence_counts"],{
            "HIGH":64,
            "MIXED":134,
            "NONE":112,
        })
        self.assertEqual(core["evidence"]["paragraphs_with_semantic_signals"],200)
        self.assertEqual(core["evidence"]["paragraphs_without_semantic_signals"],110)
        self.assertEqual(core["evidence"]["paragraph_semantic_hashes_reproduced"],310)
        self.assertEqual(core["evidence"]["paragraph_semantic_review_state"],"PASS_310_PARAGRAPH_SEMANTIC_PROFILES_REVIEWED")
        self.assertEqual(core["evidence"]["paragraph_semantic_review_state_counts"],{
            "AXIS_PROFILE_READY":156,
            "MULTI_MODAL_REVIEW_REQUIRED":42,
            "NO_STRONG_SIGNAL_REVIEW_REQUIRED":112,
        })
        self.assertEqual(core["evidence"]["paragraph_semantic_modal_axis_counts"],{
            "MULTI_MODAL":42,
            "NONE":173,
            "OBLIGATION":17,
            "PERMISSION":67,
            "PROHIBITION":11,
        })
        self.assertEqual(core["evidence"]["paragraph_semantic_axis_profile_ready"],156)
        self.assertEqual(core["evidence"]["paragraph_semantic_review_required"],154)
        self.assertEqual(core["evidence"]["paragraph_semantic_mixed_decomposition"],{
            "axis_profile_ready":92,
            "multi_modal_review_required":42,
            "no_strong_signal_review_required":0,
        })
        self.assertEqual(core["evidence"]["paragraph_semantic_unclassified_decomposition"],{
            "signal_free":110,
            "weak_only":2,
            "review_required":112,
        })
        self.assertEqual(core["evidence"]["paragraph_semantic_repeated_review_states"],{
            "AXIS_PROFILE_READY":4,
            "MULTI_MODAL_REVIEW_REQUIRED":6,
        })
        self.assertEqual(core["evidence"]["semantic_ast_readiness_state"],"PASS_1_DIRECT_MODAL_PILOT_READY")
        self.assertEqual(core["evidence"]["semantic_ast_readiness_pre_shape_blockers"],{
            "BLOCKED_PARENT_REVIEW":154,
            "BLOCKED_NO_NORMATIVE_MODAL":61,
            "BLOCKED_MODAL_MULTIPLICITY":27,
            "BLOCKED_COMPLEX_SEMANTIC_AXES":26,
            "BLOCKED_MULTIPLE_CONDITION_CUES":6,
            "BLOCKED_REPEATED_VARIANT":2,
        })
        self.assertEqual(core["evidence"]["semantic_ast_source_shape_candidates"],34)
        self.assertEqual(core["evidence"]["semantic_ast_source_hashes_reproduced"],34)
        self.assertEqual(core["evidence"]["semantic_ast_shape_state_counts"],{
            "BLOCKED_COMPLEX_DELIMITERS":4,
            "BLOCKED_PARENTHETICAL_SCOPE":1,
            "BLOCKED_SENTENCE_SHAPE":28,
            "PILOT_READY_DIRECT_MODAL":1,
        })
        self.assertEqual(core["evidence"]["semantic_ast_pilot_ready"],1)
        self.assertEqual(core["evidence"]["semantic_ast_pilot_ready_direct_modal"],1)
        self.assertEqual(core["evidence"]["semantic_ast_pilot_ready_conditional_modal"],0)
        self.assertEqual(core["evidence"]["semantic_ast_nodes_created"],0)
        self.assertEqual(core["evidence"]["repeated_boundary_variants"],5)
        self.assertEqual(core["evidence"]["paragraph_atomization_state"],"PASS_310_PARAGRAPH_ATOMS")
        self.assertEqual(core["evidence"]["paragraph_atoms"],310)
        self.assertEqual(core["evidence"]["paragraph_atom_classification_counts"],{
            "REPEATED_OCCURRENCE_PARAGRAPH_VARIANT":10,
            "SINGLE_OCCURRENCE_PARAGRAPH":300,
        })
        self.assertEqual(core["evidence"]["paragraph_range_validation_failures"],0)
        self.assertEqual(len(core["evidence"]["core_rules_binary_sha256"]),64)
        self.assertEqual(len(core["evidence"]["core_rules_semantic_sha256"]),64)
        self.assertTrue(core["evidence"]["official_public_source"]["asset_url"].startswith("https://assets.warhammer-community.com/"))

    def test_public_faction_packs_are_fingerprinted_and_still_supplemental(self):
        gaps={x["id"]:x for x in self.generated["gaps"]}
        public=gaps["PUBLIC_FACTION_SUPPLEMENT_SEMANTIC_INGESTION"]
        self.assertEqual(public["state"],"EXACT_PUBLIC_OVERLAP_AND_RESIDUAL_CLASSIFICATION_CLOSED_DEEP_EXTRACTION_PENDING")
        self.assertEqual(public["evidence"]["verified_public_faction_pack_pdfs"],28)
        self.assertEqual(public["evidence"]["official_fingerprint_state"],"PASS")
        self.assertEqual(public["evidence"]["official_fingerprint_documents"],29)
        self.assertEqual(public["evidence"]["promotable_scoped_units"],4070)
        self.assertEqual(public["evidence"]["unscoped_exact_units"],1566)
        self.assertEqual(public["evidence"]["no_exact_public_overlap_units"],7936)
        self.assertEqual(public["evidence"]["residual_promoted_units"],0)
        self.assertEqual(public["evidence"]["residual_semantic_conflicts_created"],0)
        full=gaps["FULL_FACTION_CODEX_APP_SEMANTICS"]
        self.assertEqual(full["evidence"]["public_faction_pack_scope"],"SUPPLEMENTS_CODEX_NOT_FULL_CODEX")
        self.assertIn("AUTHORIZED_CODEX_APP_EVIDENCE",full["state"])

    def test_app_gap_stays_blocked(self):
        gaps={x["id"]:x for x in self.generated["gaps"]}
        app=gaps["GW_APP_WORDING_AND_LOCKED_DATASHEET_CROSSCHECK"]
        self.assertEqual(app["state"],"BLOCKED_ON_AUTHORIZED_APP_EVIDENCE")
        self.assertEqual(app["evidence"]["repository_coverage_state"],"NOT_INGESTED")
        self.assertEqual(app["evidence"]["gate_state"],"PENDING")

    def test_source_mapping_is_candidate_only(self):
        m=self.generated["roster_source_mapping"]
        self.assertEqual(m["counts"],{
            "DIRECT_NAME_MATCH":25,
            "NAMING_ALIAS_CANDIDATE":3,
            "NO_PUBLIC_FACTION_PACK_MAPPING":2,
            "PARENT_SOURCE_CANDIDATE":7,
        })
        self.assertIn("candidates only",m["policy"])
        unresolved={x["slug"] for x in m["rows"] if x["mapping_state"]=="NO_PUBLIC_FACTION_PACK_MAPPING"}
        self.assertEqual(unresolved,{"titanicus_traitoris","unaligned_forces"})

    def test_next_pipeline_does_not_promise_full_normalization(self):
        conclusion=self.generated["conclusion"]
        self.assertEqual(conclusion["recommended_next_milestone"],"CORE_RULE_DIRECT_MODAL_AST_PILOT_V1")
        self.assertIn("exactly one direct-modal parser pilot candidate",conclusion["expected_effect"])


if __name__=="__main__":
    unittest.main()
