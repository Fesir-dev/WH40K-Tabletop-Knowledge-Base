import copy
import json
import sys
import unittest
from datetime import date
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))

from evaluate_release_transitions import build_report  # noqa: E402
from watch_release_transition_activation import build_watch  # noqa: E402


class ReleaseTransitionActivationWatchContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sm=json.loads((ROOT/"ingestion/release_transitions/space_marines_codex_2026.json").read_text(encoding="utf-8"))
        cls.cust=json.loads((ROOT/"ingestion/release_transitions/adeptus_custodes_codex_2026.json").read_text(encoding="utf-8"))
        cls.watch=json.loads((ROOT/"reports/UPSTREAM_CHANGE_WATCH_CURRENT.json").read_text(encoding="utf-8"))

    def make_watch(self, manifests, as_of, watch=None):
        readiness=build_report(manifests,watch or self.watch,date.fromisoformat(as_of))
        return build_watch(readiness)

    def test_current_checkpoint_requires_no_action(self):
        r=self.make_watch([self.sm,self.cust],"2026-09-29")
        self.assertEqual(r["status"],"NO_ACTION_REQUIRED")
        self.assertEqual(r["summary"]["no_action"],2)
        self.assertEqual(r["summary"]["action_required"],0)
        self.assertEqual(r["summary"]["ready_for_candidate"],0)
        self.assertFalse(r["safety"]["auto_promote"])
        self.assertTrue(all(x["promotion_eligible"] is False for x in r["transitions"]))

    def test_space_marines_release_date_requires_currentness_check(self):
        r=self.make_watch([self.sm],"2026-10-03")
        self.assertEqual(r["status"],"ACTION_REQUIRED")
        row=r["transitions"][0]
        self.assertEqual(row["watch_state"],"ACTION_REQUIRED")
        self.assertEqual(row["next_action"],"VERIFY_AND_RECORD_OFFICIAL_CURRENT_LEGAL_EVIDENCE")
        self.assertFalse(row["candidate_eligible"])
        self.assertFalse(row["promotion_eligible"])

    def test_confirmed_currentness_without_projection_is_monitoring(self):
        sm=copy.deepcopy(self.sm)
        sm["activation_evidence"]["current_legal_confirmed"]=True
        sm["activation_evidence"]["confirmed_at"]="2026-10-03"
        r=self.make_watch([sm],"2026-10-03")
        self.assertEqual(r["status"],"MONITORING_UPSTREAM_PROJECTION")
        row=r["transitions"][0]
        self.assertEqual(row["watch_state"],"MONITORING")
        self.assertEqual(row["next_action"],"WAIT_FOR_UPSTREAM_PROJECTION_CHANGE")
        self.assertFalse(row["promotion_eligible"])

    def test_confirmed_currentness_plus_projection_is_candidate_ready_only(self):
        sm=copy.deepcopy(self.sm)
        sm["activation_evidence"]["current_legal_confirmed"]=True
        sm["activation_evidence"]["confirmed_at"]="2026-10-03"
        watch=copy.deepcopy(self.watch)
        watch["status"]="CHANGE_DETECTED"
        watch["change_summary"]["wahapedia_files_changed"]=3
        r=self.make_watch([sm],"2026-10-03",watch)
        self.assertEqual(r["status"],"READY_FOR_GUARDED_CANDIDATE")
        row=r["transitions"][0]
        self.assertEqual(row["watch_state"],"READY_FOR_CANDIDATE")
        self.assertTrue(row["candidate_eligible"])
        self.assertFalse(row["promotion_eligible"])
        self.assertEqual(row["next_action"],"BUILD_GUARDED_REINGESTION_CANDIDATE")

    def test_unknown_state_fails_to_action_required(self):
        readiness={
            "as_of":"2026-09-29",
            "milestone":"RELEASE_TRANSITION_INGESTION_READINESS",
            "watch_status":"NO_CHANGE",
            "transitions":[{
                "transition_id":"TEST",
                "title":"Test",
                "state":"UNEXPECTED_STATE",
                "scheduled_release_date":None,
                "current_legal_confirmed":False,
                "upstream_changed":False,
                "candidate_eligible":False,
            }]
        }
        r=build_watch(readiness)
        self.assertEqual(r["status"],"ACTION_REQUIRED")
        self.assertEqual(r["transitions"][0]["next_action"],"REVIEW_UNKNOWN_RELEASE_TRANSITION_STATE")
        self.assertFalse(r["transitions"][0]["promotion_eligible"])


if __name__=="__main__":
    unittest.main()
