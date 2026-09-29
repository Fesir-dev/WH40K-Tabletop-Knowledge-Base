import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from plan_upstream_reingestion import build_plan  # noqa: E402


class ReingestionPlannerContracts(unittest.TestCase):
    def load(self, name):
        return json.loads((ROOT / "tests" / "fixtures" / "reingestion" / name).read_text(encoding="utf-8"))

    def plan(self, name):
        return build_plan(self.load(name), "2026-09-30")

    def test_no_change_is_no_action(self):
        p = self.plan("no_change.json")
        self.assertEqual(p["state"], "NO_ACTION")
        self.assertEqual(p["stages"], [])
        self.assertFalse(p["promotion"]["auto_promote"])

    def test_wahapedia_change_automates_candidate_only(self):
        p = self.plan("wahapedia_change.json")
        ids = [x["id"] for x in p["stages"]]
        self.assertEqual(ids, [
            "WAHAPEDIA_INGEST",
            "WAVE_B_RECONCILE",
            "WAVE_B_ROSTER_VIEWS",
            "WAHAPEDIA_SEMANTIC_AUDIT",
        ])
        self.assertEqual(p["promotion"]["state"], "REVIEW_REQUIRED_AFTER_CANDIDATE_PASS")
        self.assertEqual(p["blockers"], [])
        self.assertFalse(p["promotion"]["auto_promote"])

    def test_source_catalog_change_adds_official_asset_audit(self):
        p = self.plan("wahapedia_source_change.json")
        ids = [x["id"] for x in p["stages"]]
        self.assertEqual(ids, [
            "WAHAPEDIA_INGEST",
            "WAVE_B_RECONCILE",
            "WAVE_B_ROSTER_VIEWS",
            "WAHAPEDIA_SEMANTIC_AUDIT",
            "OFFICIAL_ASSET_AUDIT",
        ])
        self.assertEqual(p["promotion"]["state"], "REVIEW_REQUIRED_AFTER_CANDIDATE_PASS")

    def test_bsdata_change_reconciles_and_rebuilds_fallback(self):
        p = self.plan("bsdata_change.json")
        ids = [x["id"] for x in p["stages"]]
        self.assertEqual(ids, ["WAVE_B_RECONCILE", "BSDATA_FALLBACK_REBUILD"])
        self.assertEqual(p["candidate_revisions"]["bsdata_wh40k_11e"]["candidate"], "new-bs")
        self.assertEqual(p["source_affected_roster_identities"]["bsdata_wh40k_11e"], ["orks"])
        self.assertEqual(p["promotion"]["state"], "REVIEW_REQUIRED_AFTER_CANDIDATE_PASS")

    def test_mfm_change_requires_official_authority_gate(self):
        p = self.plan("mfm_change.json")
        self.assertEqual([x["id"] for x in p["stages"]], ["MFM_NORMATIVE_REVALIDATION"])
        self.assertEqual(p["promotion"]["state"], "BLOCKED_AUTHORITY_REVALIDATION")
        self.assertEqual(p["blockers"][0]["id"], "MFM_OFFICIAL_REVALIDATION_REQUIRED")
        self.assertFalse(p["promotion"]["auto_promote"])

    def test_multi_change_preserves_blocker(self):
        p = self.plan("multi_change.json")
        ids = [x["id"] for x in p["stages"]]
        self.assertIn("WAHAPEDIA_INGEST", ids)
        self.assertIn("BSDATA_FALLBACK_REBUILD", ids)
        self.assertIn("MFM_NORMATIVE_REVALIDATION", ids)
        self.assertEqual(p["promotion"]["state"], "BLOCKED_AUTHORITY_REVALIDATION")
        self.assertEqual(set(p["changed_sources"]), {"WAHAPEDIA_11E","BSDATA_WH40K_11E","BSDATA_MFM_11E"})

    def test_plan_is_deterministic(self):
        a = self.plan("multi_change.json")
        b = self.plan("multi_change.json")
        self.assertEqual(a["plan_fingerprint"], b["plan_fingerprint"])
        self.assertEqual(a["plan_id"], b["plan_id"])


if __name__ == "__main__":
    unittest.main()
