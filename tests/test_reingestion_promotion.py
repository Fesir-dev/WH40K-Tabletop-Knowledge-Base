import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from apply_reingestion_promotion import apply_promotion, check  # noqa: E402
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
            "affected_roster_identities":[],
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
        views=json.loads(paths["views"].read_text(encoding="utf-8"))
        views["snapshot_date"]="candidate-test"
        for row in views.get("views",[]):
            if row.get("file"):
                row["file"]=row["file"].replace("/2026-09-29/","/candidate-test/")
        (snap/"roster_views"/"index.json").write_text(json.dumps(views,indent=2)+"\n",encoding="utf-8")
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
            "affected_roster_identities":[],
            "promotion_gate":"ELIGIBLE_FOR_REVIEWED_PROMOTION",
            "auto_promote":False,
            "forbidden_current_authority_mutations":[],
        }
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(SystemExit):
                check(plan,report,Path(td))

    def test_apply_wahapedia_promotion_updates_only_mirror_currentness(self):
        td,artifact,plan,report=self.make_artifact("wahapedia_change.json")
        try:
            with tempfile.TemporaryDirectory() as repo_td:
                repo=Path(repo_td)
                for rel in [
                    "rules/11e/current.json",
                    "coverage/current.json",
                    "sources/registry.json",
                    "sources/currentness_gate.json",
                    "sources/release_state.json",
                ]:
                    src=ROOT/rel
                    dst=repo/rel
                    dst.parent.mkdir(parents=True,exist_ok=True)
                    shutil.copy2(src,dst)
                before=json.loads((repo/"rules/11e/current.json").read_text(encoding="utf-8"))
                mfm_before=before["wave_a_mfm"]["snapshot"]

                meta=apply_promotion(repo,artifact,"2026-09-30")

                current=json.loads((repo/"rules/11e/current.json").read_text(encoding="utf-8"))
                coverage=json.loads((repo/"coverage/current.json").read_text(encoding="utf-8"))
                self.assertEqual(current["wave_b_structural"]["snapshot"],"rules/11e/snapshots/candidate-test/wahapedia/roster_views/index.json")
                self.assertEqual(current["wave_a_mfm"]["snapshot"],mfm_before)
                self.assertEqual(coverage["global"]["current_normalized_factions"],0)
                self.assertFalse(meta["auto_promote"])
                self.assertFalse(meta["normative_mfm_changed"])
                self.assertTrue((repo/"ingestion"/"promotions"/plan["plan_id"]/"promotion.json").exists())
                self.assertTrue((repo/"ingestion"/"promotions"/plan["plan_id"]/"wave_b_conflicts.json").exists())
        finally:
            td.cleanup()

    def test_active_release_transition_blocks_affected_candidate(self):
        td,root,plan,report=self.make_artifact("wahapedia_change.json")
        try:
            report["affected_roster_identities"]=["space_marines"]
            release=json.loads((ROOT/"sources/release_state.json").read_text(encoding="utf-8"))
            with self.assertRaises(SystemExit):
                check(plan,report,root,release)
        finally:
            td.cleanup()

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
