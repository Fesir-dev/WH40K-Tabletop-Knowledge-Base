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
        watch["change_summary"]["github_sources_changed"]=[]
        watch["change_summary"]["wahapedia_files_changed"]=0
        watch["change_summary"]["wahapedia_last_update_changed"]=False
        return watch

    def test_current_checkpoint_is_fail_closed(self):
        r=build_report([self.sm,self.cust],self.watch,date(2026,9,29))
        rows={x["transition_id"]:x for x in r["transitions"]}
        self.assertEqual(rows["SPACE_MARINES_CODEX_2026"]["state"],"PRE_RELEASE_HOLD")
        self.assertEqual(rows["ADEPTUS_CUSTODES_CODEX_2026"]["state"],"UPCOMING_HOLD_NO_RELEASE_DATE")
        self.assertTrue(all(x["promotion_eligible"] is False for x in rows.values()))
        self.assertTrue(r["global_policy"]["calendar_date_is_not_currentness_evidence"])
        self.assertFalse(r["global_policy"]["auto_promote"])

    def test_release_date_alone_never_promotes(self):
        row=evaluate_transition(self.sm,self.watch,date(2026,10,3))
        self.assertEqual(row["state"],"RELEASE_DATE_REACHED_AWAITING_OFFICIAL_CURRENTNESS")
        self.assertFalse(row["candidate_eligible"])
        self.assertFalse(row["promotion_eligible"])

    def test_official_currentness_without_projection_waits(self):
        sm=copy.deepcopy(self.sm)
        sm["activation_evidence"]["current_legal_confirmed"]=True
        sm["activation_evidence"]["confirmed_at"]="2026-10-03"
        row=evaluate_transition(sm,self.no_change_watch(),date(2026,10,3))
        self.assertEqual(row["state"],"CURRENT_LEGAL_CONFIRMED_WAITING_UPSTREAM_PROJECTION")
        self.assertFalse(row["candidate_eligible"])

    def test_official_currentness_plus_upstream_change_allows_candidate_only(self):
        sm=copy.deepcopy(self.sm)
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

    def test_custodes_can_activate_from_official_evidence_without_guessed_date(self):
        cust=copy.deepcopy(self.cust)
        cust["activation_evidence"]["current_legal_confirmed"]=True
        cust["activation_evidence"]["confirmed_at"]="2026-10-10"
        row=evaluate_transition(cust,self.no_change_watch(),date(2026,10,10))
        self.assertEqual(row["state"],"CURRENT_LEGAL_CONFIRMED_WAITING_UPSTREAM_PROJECTION")
        self.assertIsNone(row["scheduled_release_date"])


if __name__=="__main__":
    unittest.main()
