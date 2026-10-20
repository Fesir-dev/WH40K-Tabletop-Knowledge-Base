import copy
import json
import sys
import unittest
from datetime import date
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from evaluate_release_transitions import build_report, evaluate_transition  # noqa: E402
from record_release_activation import is_official_https  # noqa: E402


class ReleaseTransitionReadinessContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sm=json.loads((ROOT/"ingestion/release_transitions/space_marines_codex_2026.json").read_text(encoding="utf-8"))
        cls.cust=json.loads((ROOT/"ingestion/release_transitions/adeptus_custodes_codex_2026.json").read_text(encoding="utf-8"))
        cls.watch=json.loads((ROOT/"reports/UPSTREAM_CHANGE_WATCH_CURRENT.json").read_text(encoding="utf-8"))

    def no_change_watch(self):
        watch=copy.deepcopy(self.watch)
        watch["status"]="NO_CHANGE"
        watch["change_summary"]["official_sources_changed"]=[]
        watch["change_summary"]["github_sources_changed"]=[]
        watch["change_summary"]["wahapedia_files_changed"]=0
        watch["change_summary"]["wahapedia_last_update_changed"]=False
        return watch

    def preclosure(self, manifest):
        row=copy.deepcopy(manifest)
        row["activation_evidence"]["current_legal_confirmed"]=False
        row["activation_evidence"]["scoped_current_legal_confirmed"]=False
        row["reviewed_promotion"]={"applied":False}
        return row

    def test_current_checkpoint_is_scoped_reconciled(self):
        r=build_report([self.sm,self.cust],self.watch,date(2026,10,20))
        rows={x["transition_id"]:x for x in r["transitions"]}
        self.assertTrue(all(x["state"]=="CURRENT_SCOPED_RECONCILED" for x in rows.values()))
        self.assertTrue(all(x["scoped_current_legal_confirmed"] for x in rows.values()))
        self.assertTrue(all(not x["full_codex_app_semantics_confirmed"] for x in rows.values()))
        self.assertTrue(all(x["promotion_eligible"] is False for x in rows.values()))
        self.assertEqual(r["summary"]["scoped_current_reconciled"],2)
        self.assertTrue(r["global_policy"]["scoped_currentness_does_not_claim_full_codex_app_equivalence"])
        self.assertFalse(r["global_policy"]["auto_promote"])

    def test_release_date_alone_never_promotes(self):
        sm=self.preclosure(self.sm)
        row=evaluate_transition(sm,self.watch,date(2026,10,3))
        self.assertEqual(row["state"],"RELEASE_DATE_REACHED_AWAITING_OFFICIAL_CURRENTNESS")
        self.assertFalse(row["candidate_eligible"])
        self.assertFalse(row["promotion_eligible"])

    def test_official_currentness_without_projection_waits(self):
        sm=self.preclosure(self.sm)
        sm["activation_evidence"]["current_legal_confirmed"]=True
        sm["activation_evidence"]["confirmed_at"]="2026-10-03"
        row=evaluate_transition(sm,self.no_change_watch(),date(2026,10,3))
        self.assertEqual(row["state"],"CURRENT_LEGAL_CONFIRMED_WAITING_UPSTREAM_PROJECTION")
        self.assertFalse(row["candidate_eligible"])

    def test_official_currentness_plus_upstream_change_allows_candidate_only(self):
        sm=self.preclosure(self.sm)
        sm["activation_evidence"]["current_legal_confirmed"]=True
        sm["activation_evidence"]["confirmed_at"]="2026-10-03"
        watch=self.no_change_watch()
        watch["status"]="CHANGE_DETECTED"
        watch["change_summary"]["wahapedia_files_changed"]=1
        row=evaluate_transition(sm,watch,date(2026,10,3))
        self.assertEqual(row["state"],"READY_FOR_GUARDED_REINGESTION")
        self.assertTrue(row["candidate_eligible"])
        self.assertFalse(row["promotion_eligible"])
        self.assertEqual(row["next_action"],"BUILD_ISOLATED_CANDIDATE")

    def test_activation_evidence_requires_official_https_domain(self):
        self.assertTrue(is_official_https("https://www.warhammer-community.com/en-gb/articles/example/"))
        self.assertTrue(is_official_https("https://www.warhammer.com/en-GB/example"))
        self.assertFalse(is_official_https("http://www.warhammer-community.com/example"))
        self.assertFalse(is_official_https("https://example.com/warhammer-community.com"))

    def test_custodes_can_activate_scoped_without_guessed_release_date(self):
        self.assertIsNone(self.cust["scheduled_release_date"])
        row=evaluate_transition(self.cust,self.no_change_watch(),date(2026,10,20))
        self.assertEqual(row["state"],"CURRENT_SCOPED_RECONCILED")
        self.assertTrue(row["scoped_current_legal_confirmed"])
        self.assertFalse(row["full_codex_app_semantics_confirmed"])


if __name__=="__main__":
    unittest.main()
