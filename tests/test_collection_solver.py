import copy
import json
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from solve_collection_roster import solve_request  # noqa: E402


class CollectionSolverContracts(unittest.TestCase):
    def load(self, name):
        return json.loads((ROOT / "rosters" / "examples" / name).read_text(encoding="utf-8"))

    def test_ready_roster(self):
        result = solve_request(self.load("custodes_feasible_ready.json"), ROOT)
        self.assertEqual(result["rules"]["scoped_legality"], "PASS")
        self.assertEqual(result["physical"]["state"], "FEASIBLE_PROVISIONAL")
        self.assertEqual(result["points"]["total"], 740)
        self.assertEqual(result["rules"]["full_normative_legality"], "UNKNOWN_PENDING_NORMATIVE_APP")

    def test_build_required(self):
        result = solve_request(self.load("custodes_build_required.json"), ROOT)
        self.assertEqual(result["physical"]["state"], "FEASIBLE_WITH_BUILD_PROVISIONAL")
        self.assertEqual(result["physical"]["assembly_required_bodies"], 11)

    def test_shared_bike_pool_conflict(self):
        result = solve_request(self.load("custodes_body_conflict.json"), ROOT)
        self.assertEqual(result["physical"]["state"], "INFEASIBLE_FROM_SNAPSHOT")
        self.assertEqual(sum(x["deficit"] for x in result["physical"]["body_deficits"]), 1)

    def test_component_stock_conflict(self):
        result = solve_request(self.load("custodes_component_conflict.json"), ROOT)
        self.assertEqual(result["physical"]["state"], "INFEASIBLE_FROM_SNAPSHOT")
        deficit = result["physical"]["component_deficits"][0]
        self.assertEqual(deficit["component_id"], "CUSTODES_TELEMON_ARACHNUS_STORM_CANNON")
        self.assertEqual(deficit["deficit"], 2)

    def test_conversion_gate(self):
        request = self.load("custodes_conversion.json")
        allowed = solve_request(request, ROOT)
        self.assertEqual(allowed["physical"]["state"], "FEASIBLE_WITH_CONVERSION_PROVISIONAL")
        denied_request = copy.deepcopy(request)
        denied_request["options"] = {"allow_conversion": False}
        denied = solve_request(denied_request, ROOT)
        self.assertEqual(denied["physical"]["state"], "INFEASIBLE_FROM_SNAPSHOT")

    def test_unknown_shared_component_fails_closed(self):
        result = solve_request(self.load("custodes_unknown_venatari_lance.json"), ROOT)
        self.assertEqual(result["physical"]["state"], "UNKNOWN_COMPONENT_FEASIBILITY")
        self.assertEqual(result["physical"]["unknown_constraints"][0]["constraint_id"], "CUSTODES_VENATARI_GUARD_SPEAR_SHARING")


if __name__ == "__main__":
    unittest.main()
