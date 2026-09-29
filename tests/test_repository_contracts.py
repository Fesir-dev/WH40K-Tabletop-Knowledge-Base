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
        cls.mfm = json.loads((ROOT/"rules/11e/snapshots/2026-09-29/mfm/index.json").read_text(encoding="utf-8"))
        cls.wave_b = json.loads((ROOT/"rules/11e/snapshots/2026-09-29/wahapedia/roster_views/index.json").read_text(encoding="utf-8"))
        cls.wave_b_manifest = json.loads((ROOT/"rules/11e/snapshots/2026-09-29/wahapedia/manifest.json").read_text(encoding="utf-8"))
        cls.wave_b_recon = json.loads((ROOT/"reports/WAVE_B_RECONCILIATION_2026-09-29.json").read_text(encoding="utf-8"))
        cls.current = json.loads((ROOT/"rules/11e/current.json").read_text(encoding="utf-8"))
        cls.bsdata_fallback = json.loads((ROOT/"rules/11e/snapshots/2026-09-29/bsdata_fallback/index.json").read_text(encoding="utf-8"))
        cls.semantic_audit = json.loads((ROOT/"reports/WAVE_B_SEMANTIC_FINGERPRINT_AUDIT_2026-09-29.json").read_text(encoding="utf-8"))
        cls.official_assets = json.loads((ROOT/"sources/snapshots/gw_11e_official_assets_2026-09-29.json").read_text(encoding="utf-8"))

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

    def test_mfm_wave_a_snapshot(self):
        self.assertEqual(self.mfm["official_source"]["version"], "1.4")
        self.assertEqual(self.mfm["official_source"]["last_updated"], "2026-09-02")
        self.assertEqual(len(self.mfm["faction_files"]), 30)
        self.assertEqual(self.mfm["totals"]["units"], 1789)
        self.assertEqual(self.mfm["totals"]["pricing_rows"], 2980)
        self.assertEqual(self.mfm["totals"]["leader_relations"], 1574)
        self.assertEqual(self.mfm["totals"]["enhancement_cost_entries"], 1193)

    def test_mfm_roster_mapping_and_coverage(self):
        rows={x["slug"]:x for x in self.catalog["factions"]}
        mapped=[x for x in rows.values() if x.get("mfm_source_slug")]
        self.assertEqual(len(mapped), 36)
        self.assertIsNone(rows["unaligned_forces"].get("mfm_source_slug"))
        self.assertEqual(rows["imperial_fists"]["mfm_source_slug"], "space-marines")
        self.assertEqual(rows["imperial_fists"]["mfm_group_title"], "Imperial Fists")
        wave_dims=set(self.mfm["coverage"]["dimensions"])
        cov={x["slug"]:x for x in self.coverage["factions"]}
        for row in mapped:
            for dim in wave_dims:
                self.assertEqual(cov[row["slug"]]["coverage"][dim], 100, (row["slug"], dim))



    def test_wave_b_structural_views(self):
        self.assertEqual(
            self.wave_b["counts"],
            {"roster_identities":37,"structural_complete":35,"structural_partial":0,"unavailable":2},
        )
        unavailable={
            x["slug"] for x in self.wave_b["views"]
            if x["status"].startswith("UNAVAILABLE")
        }
        self.assertEqual(unavailable, {"titanicus_traitoris","unaligned_forces"})
        self.assertEqual(self.wave_b_manifest["source"]["last_update"], "2026-09-28 02:38:04")
        self.assertEqual(self.wave_b_manifest["counts"]["datasheets"], 1660)
        self.assertEqual(self.wave_b_manifest["counts"]["ability_catalog"], 95)

    def test_wave_b_reconciliation_and_promotion(self):
        self.assertEqual(self.wave_b_recon["status"], "PASS_WITH_CONFLICTS")
        self.assertEqual(self.wave_b_recon["conflict_count"], 11)
        self.assertEqual(self.wave_b_recon["totals"]["points_compared"], 1202)
        self.assertEqual(self.wave_b_recon["totals"]["unit_name_matches"], 1242)
        self.assertEqual(self.coverage["status"], "WAVE_B_SEMANTIC_FAQ_OPERATIONAL_COMPLETE")
        self.assertEqual(sum(1 for x in self.coverage["factions"] if x.get("structural_current")), 35)
        self.assertEqual(self.coverage["global"]["current_normalized_factions"], 0)
        self.assertEqual(self.current["status"], "CURRENT_OPERATIONAL_RULES_LAYER_READY_NORMATIVE_APP_PENDING")
        self.assertEqual(self.current["wave_b_structural"]["roster_identities_complete"], 35)
        self.assertEqual(self.current["wave_b_structural"]["semantic_rule_text"], "CURRENT_SECONDARY_MIRROR_FULL_HASH_VERIFIED")
        self.assertEqual(self.current["wave_b_structural"]["faq_errata"], "SOURCE_CATALOG_CURRENT_OFFICIAL_ASSETS_VERIFIED")


    def test_structural_source_availability_37_of_37(self):
        g=self.coverage["global"]
        self.assertEqual(g["wave_b_current_mirror_structural_complete"], 35)
        self.assertEqual(g["wave_b_structured_implementation_fallback_complete"], 2)
        self.assertEqual(g["wave_b_total_structural_source_available"], 37)
        self.assertEqual(sum(1 for x in self.coverage["factions"] if x.get("structural_source_available")), 37)
        rows={x["slug"]:x for x in self.coverage["factions"]}
        for slug in {"titanicus_traitoris","unaligned_forces"}:
            self.assertFalse(rows[slug]["structural_current"])
            self.assertEqual(rows[slug]["wave_b_structural"]["state"], "IMPLEMENTATION_FALLBACK_COMPLETE")
            self.assertEqual(rows[slug]["wave_b_structural"]["source_role"], "structured_implementation")
            self.assertFalse(rows[slug]["wave_b_structural"]["normative_rules_verified"])

    def test_bsdata_fallback_snapshot(self):
        self.assertEqual(self.bsdata_fallback["commit_sha"], "951d5900d1b4a952a4ba560a30c43788e622ccfc")
        rows={x["slug"]:x for x in self.bsdata_fallback["views"]}
        self.assertEqual(rows["titanicus_traitoris"]["counts"]["units"], 4)
        self.assertEqual(rows["unaligned_forces"]["counts"]["units"], 22)

    def test_semantic_resolver_contract(self):
        self.assertTrue((ROOT/"tools/query_current_semantics.py").exists())
        self.assertTrue((ROOT/".github/workflows/semantic-smoke.yml").exists())
        self.assertEqual(self.current["wave_b_structural"]["total_structural_source_available"], 37)
        self.assertEqual(self.current["wave_b_structural"]["semantic_rule_text"], "CURRENT_SECONDARY_MIRROR_FULL_HASH_VERIFIED")

    def test_wave_b_semantic_and_official_asset_audits(self):
        self.assertEqual(self.semantic_audit["status"], "PASS")
        self.assertEqual(self.semantic_audit["expected_fingerprints"], 16506)
        self.assertEqual(self.semantic_audit["counts"], {"MATCH":16506})
        self.assertEqual(len(self.semantic_audit["problems"]), 0)
        self.assertEqual(self.official_assets["status"], "PASS")
        self.assertEqual(self.official_assets["live_source_csv"]["catalog_drift_count"], 0)
        self.assertEqual(self.official_assets["official_assets"]["edition_11_sources"], 29)
        self.assertEqual(self.official_assets["official_assets"]["verified_pdf_assets"], 28)
        self.assertEqual(self.official_assets["official_assets"]["failures"], 0)
        self.assertEqual(self.coverage["global"]["wave_b_current_mirror_semantic_roster_identities"], 35)
        self.assertEqual(self.coverage["global"]["current_normalized_factions"], 0)
        self.assertEqual(self.current["status"], "CURRENT_OPERATIONAL_RULES_LAYER_READY_NORMATIVE_APP_PENDING")

    def test_preview_never_replaces_current(self):
        for tr in self.release["transitions"]:
            if tr.get("upcoming_state"):
                self.assertEqual(tr.get("current_legal_state"), "CURRENT_LEGAL")

if __name__ == "__main__":
    unittest.main()
