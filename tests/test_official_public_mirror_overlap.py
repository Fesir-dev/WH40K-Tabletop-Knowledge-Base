import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))

from audit_official_public_mirror_overlap import canonical_text, classify, shingle_coverage, tokens  # noqa: E402


class OfficialPublicMirrorOverlapContracts(unittest.TestCase):
    def test_html_and_pdf_punctuation_normalize_conservatively(self):
        a="<b>Target:</b> One Aeldari unit<br>within 12\u201d."
        b="Target: One Aeldari unit within 12\"."
        self.assertEqual(canonical_text(a),canonical_text(b))

    def test_exact_token_sequence(self):
        official="Ancient Doom When this model makes an attack re roll a Hit roll of 1"
        state,cov,anchor=classify(
            "When this model makes an attack, re-roll a Hit roll of 1.",
            "Ancient Doom",tokens(official),"EXACT_SOURCE_ID"
        )
        self.assertEqual(state,"EXACT_TOKEN_SEQUENCE_MATCH")
        self.assertEqual(cov,1.0)
        self.assertTrue(anchor)

    def test_high_overlap_is_not_called_full_equivalence(self):
        official="unit ability alpha beta gamma delta epsilon zeta eta theta"
        state,cov,anchor=classify(
            "alpha beta gamma delta epsilon zeta eta iota",
            "unit ability",tokens(official),"EXACT_SOURCE_ID"
        )
        self.assertIn(state,{"HIGH_OVERLAP_NORMALIZATION_MATCH","PARTIAL_OVERLAP_REVIEW"})
        self.assertTrue(anchor)
        self.assertGreater(cov,0)

    def test_exact_source_low_overlap_fails_to_review_not_drift_claim(self):
        official="Eldrad Ulthran unrelated public text"
        state,cov,anchor=classify(
            "Completely different semantic wording with enough tokens for comparison",
            "Eldrad Ulthran",tokens(official),"EXACT_SOURCE_ID"
        )
        self.assertEqual(state,"REVIEW_REQUIRED_POSSIBLE_DRIFT_OR_LAYOUT")
        self.assertTrue(anchor)
        self.assertLess(cov,0.4)

    def test_faction_candidate_without_anchor_is_outside_or_unmapped(self):
        state,cov,anchor=classify(
            "some codex only rule text that is not in the public pack",
            "Codex Only Rule",tokens("faction pack different content"),"FACTION_SCOPE_CANDIDATE"
        )
        self.assertEqual(state,"OUTSIDE_PUBLIC_PACK_OR_UNMAPPED")
        self.assertFalse(anchor)

    def test_shingle_coverage(self):
        candidate="a b c d e f g h".split()
        official="x a b c d e f g y".split()
        cov=shingle_coverage(candidate,official,5)
        self.assertGreater(cov,0.4)
        self.assertLess(cov,1.0)


if __name__=="__main__":
    unittest.main()
