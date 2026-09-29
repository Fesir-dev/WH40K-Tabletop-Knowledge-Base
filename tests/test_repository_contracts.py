import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class RepositoryContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads((ROOT/"factions/catalog.json").read_text(encoding="utf-8"))
        cls.coverage = json.loads((ROOT/"coverage/current.json").read_text(encoding="utf-8"))
        cls.gate = json.loads((ROOT/"sources/currentness_gate.json").read_text(encoding="utf-8"))
        cls.release = json.loads((ROOT/"sources/release_state.json").read_text(encoding="utf-8"))
        cls.bsdata = json.loads((ROOT/"ingestion/source_snapshots/bsdata_wh40k_11e_2026-09-29.json").read_text(encoding="utf-8"))

    def test_catalog_unique(self):
        slugs=[x["slug"] for x in self.catalog["factions"]]
        paths=[x["bsdata_path"] for x in self.catalog["factions"]]
        self.assertEqual(len(slugs), len(set(slugs)))
        self.assertEqual(len(paths), len(set(paths)))
        self.assertEqual(len(slugs), 37)

    def test_bsdata_roster_catalogues_mapped(self):
        roster={x["path"] for x in self.bsdata["files"] if x["role"]=="roster_catalogue"}
        mapped={x["bsdata_path"] for x in self.catalog["factions"]}
        self.assertEqual(roster, mapped)

    def test_coverage_matches_catalog(self):
        self.assertEqual(
            {x["slug"] for x in self.catalog["factions"]},
            {x["slug"] for x in self.coverage["factions"]},
        )
        self.assertEqual(self.coverage["global"]["current_normalized_factions"], 0)
        self.assertTrue(all(not x["current_normalized"] for x in self.coverage["factions"]))

    def test_scope_profiles_reference_known_sources(self):
        source_ids={x["id"] for x in self.gate["required_checks"]}
        profiles=self.gate["scope_profiles"]
        for name,p in profiles.items():
            self.assertTrue(set(p.get("required_sources", [])) <= source_ids, name)
            self.assertTrue(set(p.get("required_profiles", [])) <= set(profiles), name)

    def test_release_transitions_reference_catalog(self):
        slugs={x["slug"] for x in self.catalog["factions"]}
        for tr in self.release["transitions"]:
            self.assertTrue(set(tr["factions"]) <= slugs, tr["id"])

    def test_preview_never_replaces_current(self):
        for tr in self.release["transitions"]:
            if tr.get("upcoming_state"):
                self.assertEqual(tr.get("current_legal_state"), "CURRENT_LEGAL")

if __name__ == "__main__":
    unittest.main()
