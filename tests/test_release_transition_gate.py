import copy
import json
import sys
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from release_transition_gate import evaluate_release_state, promotion_blockers  # noqa: E402


class ReleaseTransitionGateContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.release = json.loads((ROOT / "sources" / "release_state.json").read_text(encoding="utf-8"))

    def by_id(self, result):
        return {x["transition_id"]: x for x in result["transitions"]}

    def test_checkpoint_holds_pending_releases(self):
        result = evaluate_release_state(self.release, date(2026, 9, 29))
        rows = self.by_id(result)
        self.assertEqual(rows["ORKS_CODEX_2026"]["state"], "CURRENT_STABLE_NO_PENDING_TRANSITION")
        self.assertEqual(rows["SPACE_MARINES_CODEX_2026"]["state"], "HOLD_CURRENT_PRE_RELEASE")
        self.assertEqual(rows["ADEPTUS_CUSTODES_CODEX_2026"]["state"], "HOLD_CURRENT_RELEASE_DATE_UNKNOWN")
        self.assertEqual(result["official_rechecks_due"], 0)
        self.assertFalse(result["auto_promote"])
        self.assertIn("space_marines", result["blocked_factions"])
        self.assertIn("adeptus_custodes", result["blocked_factions"])

    def test_release_date_triggers_recheck_not_authorization(self):
        result = evaluate_release_state(self.release, date(2026, 10, 3))
        rows = self.by_id(result)
        sm = rows["SPACE_MARINES_CODEX_2026"]
        self.assertEqual(sm["state"], "OFFICIAL_RECHECK_REQUIRED")
        self.assertFalse(sm["candidate_authorization"])
        self.assertEqual(result["official_rechecks_due"], 1)
        self.assertIn("space_marines", result["blocked_factions"])

    def test_pending_transition_blocks_affected_candidate(self):
        blockers = promotion_blockers(
            self.release,
            {"space_marines", "orks", "adeptus_custodes"},
            date(2026, 9, 29),
        )
        ids = {x["transition_id"] for x in blockers}
        self.assertEqual(ids, {"SPACE_MARINES_CODEX_2026", "ADEPTUS_CUSTODES_CODEX_2026"})
        self.assertTrue(all(x["affected_factions"] for x in blockers))

    def test_unrelated_current_faction_is_not_blocked(self):
        blockers = promotion_blockers(self.release, {"orks"}, date(2026, 9, 29))
        self.assertEqual(blockers, [])

    def test_explicit_authorization_is_required_and_sufficient_for_gate(self):
        release = copy.deepcopy(self.release)
        sm = next(x for x in release["transitions"] if x["id"] == "SPACE_MARINES_CODEX_2026")
        sm["ingestion_gate"]["candidate_authorization"] = True
        sm["ingestion_gate"]["state"] = "AUTHORIZED_AFTER_OFFICIAL_RECHECK"
        blockers = promotion_blockers(release, {"space_marines"}, date(2026, 10, 3))
        self.assertEqual(blockers, [])
        result = evaluate_release_state(release, date(2026, 10, 3))
        rows = self.by_id(result)
        self.assertEqual(rows["SPACE_MARINES_CODEX_2026"]["state"], "CANDIDATE_AUTHORIZED_BY_OFFICIAL_RECHECK")


if __name__ == "__main__":
    unittest.main()
