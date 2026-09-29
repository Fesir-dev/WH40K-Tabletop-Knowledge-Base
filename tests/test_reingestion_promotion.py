import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from apply_reingestion_promotion import check  # noqa: E402
from plan_upstream_reingestion import build_plan  # noqa: E402


class ReingestionPromotionContracts(unittest.TestCase):
    def fixture(self, name):
        return json.loads((ROOT / "tests" / "fixtures" / "reingestion" / name).read_text(encoding="utf-8"))

    def current_paths(self):
        current=json.loads((ROOT/"rules/11e/current.json").read_text(encoding="utf-8"))
        widx=ROOT/current["wave_b_structural"]["snapshot"]
        return {
            "manifest": widx.parent.parent/"manifest.json",
            "views": widx,
            "recon": ROOT/current["wave_b_structural"]["reconciliation_report"],
            "semantic": ROOT/current["semantic_resolver"]["full_audit"]["report"],
            "official": ROOT/current["source_currentness"]["faq_errata_assets"]["report"],
        }

    def make_artifact(self, fixture_name, include_official=False):
        td=tempfile.TemporaryDirectory()
        root=Path(td.name)
        plan=build_plan(self.fixture(fixture_name), "candidate-test")
        (root/"reingestion_plan.json").write_text(json.dumps(plan,indent=2)+"\n",encoding="utf-8")
        report={
            "schema_version":"1.0",
            "plan_id":plan["plan_id"],
            "plan_fingerprint":plan["plan_fingerprint"],
            "status":"PASS",
            "candidate_snapshot_date":"candidate-test",
            "changed_sources":plan["changed_sources"],
            "stages":[],
            "changed_files_in_isolated_workspace":[],
            "artifact_files":[],
            "forbidden_current_authority_mutations":[],
            "promotion_gate":"ELIGIBLE_FOR_REVIEWED_PROMOTION",
            "auto_promote":False,
        }
        (root/"candidate_report.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
        paths=self.current_paths()
        snap=root/"candidate"/"rules"/"11e"/"snapshots"/"candidate-test"/"wahapedia"
        (snap/"roster_views").mkdir(parents=True)
        shutil.copy2(paths["manifest"], snap/"manifest.json")
        shutil.copy2(paths["views"], snap/"roster_views"/"index.json")
        evidence=root/"candidate"/"ingestion"/"candidates"/plan["plan_id"]
        evidence.mkdir(parents=True)
        shutil.copy2(paths["recon"], evidence/"reconciliation.json")
        shutil.copy2(paths["semantic"], evidence/"semantic_fingerprint_audit.json")
        if include_official:
            shutil.copy2(paths["official"], evidence/"official_assets.json")
        return td,root,plan,report

    def test_wahapedia_candidate_is_review_eligible(self):
        td,root,plan,report=self.make_artifact("wahapedia_change.json")
        try:
            ev=check(plan,report,root)
            self.assertEqual(ev["candidate_key"],"candidate-test")
            self.assertIn("manifest",ev)
            self.assertIn("semantic",ev)
        finally:
            td.cleanup()

    def test_fingerprint_mismatch_fails_closed(self):
        td,root,plan,report=self.make_artifact("wahapedia_change.json")
        try:
            report["plan_fingerprint"]="wrong"
            with self.assertRaises(SystemExit):
                check(plan,report,root)
        finally:
            td.cleanup()

    def test_auto_promote_true_fails_closed(self):
        td,root,plan,report=self.make_artifact("wahapedia_change.json")
        try:
            report["auto_promote"]=True
            with self.assertRaises(SystemExit):
                check(plan,report,root)
        finally:
            td.cleanup()

    def test_mfm_change_cannot_enter_reviewed_promotion(self):
        plan=build_plan(self.fixture("mfm_change.json"),"candidate-test")
        report={
            "plan_id":plan["plan_id"],
            "plan_fingerprint":plan["plan_fingerprint"],
            "status":"PASS",
            "promotion_gate":"ELIGIBLE_FOR_REVIEWED_PROMOTION",
            "auto_promote":False,
            "forbidden_current_authority_mutations":[],
        }
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(SystemExit):
                check(plan,report,Path(td))

    def test_source_catalog_change_requires_official_asset_evidence(self):
        td,root,plan,report=self.make_artifact("wahapedia_source_change.json",include_official=False)
        try:
            with self.assertRaises(SystemExit):
                check(plan,report,root)
        finally:
            td.cleanup()

        td,root,plan,report=self.make_artifact("wahapedia_source_change.json",include_official=True)
        try:
            ev=check(plan,report,root)
            self.assertIn("official_assets",ev)
        finally:
            td.cleanup()


if __name__=="__main__":
    unittest.main()
