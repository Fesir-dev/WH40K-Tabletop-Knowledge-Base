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
        cls.release_readiness = json.loads((ROOT/"reports/RELEASE_TRANSITION_READINESS_CURRENT.json").read_text(encoding="utf-8"))
        cls.release_activation_watch = json.loads((ROOT/"reports/RELEASE_TRANSITION_ACTIVATION_WATCH_CURRENT.json").read_text(encoding="utf-8"))
        cls.space_marines_transition = json.loads((ROOT/"ingestion/release_transitions/space_marines_codex_2026.json").read_text(encoding="utf-8"))
        cls.custodes_transition = json.loads((ROOT/"ingestion/release_transitions/adeptus_custodes_codex_2026.json").read_text(encoding="utf-8"))
        cls.registry = json.loads((ROOT/"sources/registry.json").read_text(encoding="utf-8"))
        cls.bsdata = json.loads((ROOT/"ingestion/source_snapshots/bsdata_wh40k_11e_2026-09-29.json").read_text(encoding="utf-8"))
        cls.current = json.loads((ROOT/"rules/11e/current.json").read_text(encoding="utf-8"))

        mfm_index_path = ROOT / cls.current["wave_a_mfm"]["snapshot"]
        cls.mfm = json.loads(mfm_index_path.read_text(encoding="utf-8"))

        wave_b_index_path = ROOT / cls.current["wave_b_structural"]["snapshot"]
        cls.wave_b = json.loads(wave_b_index_path.read_text(encoding="utf-8"))
        cls.wave_b_manifest = json.loads((wave_b_index_path.parent.parent/"manifest.json").read_text(encoding="utf-8"))
        cls.wave_b_recon = json.loads((ROOT/cls.current["wave_b_structural"]["reconciliation_report"]).read_text(encoding="utf-8"))

        fallback_path = ROOT / cls.current["wave_b_structural"]["implementation_fallback_snapshot"]
        cls.bsdata_fallback = json.loads(fallback_path.read_text(encoding="utf-8"))

        sem_path = ROOT / cls.current["semantic_resolver"]["full_audit"]["report"]
        cls.semantic_audit = json.loads(sem_path.read_text(encoding="utf-8"))
        official_path = ROOT / cls.current["source_currentness"]["faq_errata_assets"]["report"]
        cls.official_assets = json.loads(official_path.read_text(encoding="utf-8"))

        cls.upstream_watch = json.loads((ROOT/"reports/UPSTREAM_CHANGE_WATCH_CURRENT.json").read_text(encoding="utf-8"))
        cls.nr_runtime = json.loads((ROOT/"reports/NEW_RECRUIT_RUNTIME_VALIDATION_CURRENT.json").read_text(encoding="utf-8"))
        cls.runtime_drifts = json.loads((ROOT/"sources/runtime_drift_registry.json").read_text(encoding="utf-8"))
        cls.collection_solver = json.loads((ROOT/"reports/COLLECTION_AWARE_ROSTER_SOLVER_CURRENT.json").read_text(encoding="utf-8"))
        cls.custodes_solver_profile = json.loads((ROOT/"collection/adeptus_custodes/solver_profile.json").read_text(encoding="utf-8"))
        cls.custodes_current_collection = json.loads((ROOT/"collection/adeptus_custodes/current.json").read_text(encoding="utf-8"))
        cls.normative_gap_audit = json.loads((ROOT/"reports/NORMATIVE_APP_EQUIVALENCE_GAP_AUDIT_CURRENT.json").read_text(encoding="utf-8"))
        cls.public_rules_discovery = json.loads((ROOT/"sources/discoveries/gw_public_rules_surface_2026-09-29.json").read_text(encoding="utf-8"))
        cls.official_public_fingerprints = json.loads((ROOT/"reports/OFFICIAL_PUBLIC_RULES_SEMANTIC_FINGERPRINT_CURRENT.json").read_text(encoding="utf-8"))
        cls.official_core_snapshot = json.loads((ROOT/"sources/snapshots/gw_11e_core_rules_asset_2026-09-29.json").read_text(encoding="utf-8"))
        cls.core_rule_atoms = json.loads((ROOT/"reports/CORE_RULE_REFERENCE_ATOMIZATION_CURRENT.json").read_text(encoding="utf-8"))
        cls.core_rule_boundaries = json.loads((ROOT/"reports/CORE_RULE_PARAGRAPH_BOUNDARIES_CURRENT.json").read_text(encoding="utf-8"))
        cls.core_rule_paragraph_atoms = json.loads((ROOT/"reports/CORE_RULE_PARAGRAPH_ATOMIZATION_CURRENT.json").read_text(encoding="utf-8"))
        cls.core_rule_paragraph_semantics = json.loads((ROOT/"reports/CORE_RULE_PARAGRAPH_SEMANTIC_CLASSIFICATION_CURRENT.json").read_text(encoding="utf-8"))

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

    def test_release_transition_readiness_control_plane(self):
        self.assertEqual(self.release["schema_version"], "1.2")
        policy=self.release["transition_policy"]
        self.assertEqual(policy["state"], "OPERATIONAL_READINESS_V1")
        self.assertFalse(policy["auto_promote"])
        self.assertEqual(policy["report"], "reports/RELEASE_TRANSITION_READINESS_CURRENT.json")
        self.assertTrue((ROOT/policy["evaluator"]).exists())
        self.assertTrue((ROOT/policy["workflow"]).exists())
        self.assertTrue((ROOT/"tools/record_release_activation.py").exists())
        self.assertTrue((ROOT/"schemas/release_transition_manifest.schema.json").exists())

        report=self.release_readiness
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["milestone"], "RELEASE_TRANSITION_INGESTION_READINESS")
        self.assertEqual(report["as_of"], "2026-09-29")
        self.assertFalse(report["global_policy"]["auto_promote"])
        rows={x["transition_id"]:x for x in report["transitions"]}
        self.assertEqual(set(rows), {"SPACE_MARINES_CODEX_2026","ADEPTUS_CUSTODES_CODEX_2026"})
        self.assertEqual(rows["SPACE_MARINES_CODEX_2026"]["state"], "PRE_RELEASE_HOLD")
        self.assertEqual(rows["ADEPTUS_CUSTODES_CODEX_2026"]["state"], "UPCOMING_HOLD_NO_RELEASE_DATE")
        self.assertTrue(all(x["promotion_eligible"] is False for x in rows.values()))

        manifests={
            "SPACE_MARINES_CODEX_2026": self.space_marines_transition,
            "ADEPTUS_CUSTODES_CODEX_2026": self.custodes_transition,
        }
        catalog_slugs={x["slug"] for x in self.catalog["factions"]}
        for tid,manifest in manifests.items():
            self.assertEqual(manifest["transition_id"], tid)
            self.assertTrue(set(manifest["factions"]) <= catalog_slugs)
            self.assertEqual(manifest["baseline_current_state"], "CURRENT_LEGAL")
            self.assertFalse(manifest["activation_evidence"]["current_legal_confirmed"])
            self.assertTrue(manifest["policy"]["preview_never_promotes"])
            self.assertTrue(manifest["policy"]["date_alone_never_promotes"])
            self.assertTrue(manifest["policy"]["require_official_current_legal_evidence"])
            self.assertEqual(manifest["policy"]["promotion_route"], "GUARDED_REINGESTION_CANDIDATE_REVIEWED_PROMOTION")

        self.assertEqual(self.space_marines_transition["scheduled_release_date"], "2026-10-03")
        self.assertIsNone(self.custodes_transition["scheduled_release_date"])

        recorder=(ROOT/"tools/record_release_activation.py").read_text(encoding="utf-8")
        self.assertNotIn('ROOT/"rules"/"11e"/"current.json"', recorder)
        workflow=(ROOT/".github/workflows/release-transition-readiness.yml").read_text(encoding="utf-8")
        self.assertIn("contents: read", workflow)
        self.assertIn("release-transition auto-promotion: DISABLED", workflow)

    def test_release_transition_activation_watch_control_plane(self):
        watch=self.release["activation_watch"]
        self.assertEqual(watch["state"], "OPERATIONAL_V1")
        self.assertEqual(watch["current_status"], "NO_ACTION_REQUIRED")
        self.assertFalse(watch["auto_promote"])
        self.assertFalse(watch["direct_current_rules_mutation"])
        self.assertEqual(watch["cadence"], "every 6 hours")
        self.assertTrue((ROOT/watch["tool"]).exists())
        self.assertTrue((ROOT/watch["workflow"]).exists())
        self.assertEqual(watch["report"], "reports/RELEASE_TRANSITION_ACTIVATION_WATCH_CURRENT.json")

        report=self.release_activation_watch
        self.assertEqual(report["status"], "NO_ACTION_REQUIRED")
        self.assertEqual(report["as_of"], "2026-09-29")
        self.assertEqual(report["summary"]["transition_count"], 2)
        self.assertEqual(report["summary"]["no_action"], 2)
        self.assertEqual(report["summary"]["action_required"], 0)
        self.assertEqual(report["summary"]["monitoring"], 0)
        self.assertEqual(report["summary"]["ready_for_candidate"], 0)
        self.assertFalse(report["safety"]["auto_promote"])
        self.assertFalse(report["safety"]["direct_current_rules_mutation"])
        self.assertTrue(all(x["promotion_eligible"] is False for x in report["transitions"]))

        rows={x["transition_id"]:x for x in report["transitions"]}
        self.assertEqual(rows["SPACE_MARINES_CODEX_2026"]["watch_state"], "NO_ACTION")
        self.assertEqual(rows["SPACE_MARINES_CODEX_2026"]["next_action"], "WAIT_PRE_RELEASE")
        self.assertEqual(rows["ADEPTUS_CUSTODES_CODEX_2026"]["watch_state"], "NO_ACTION")
        self.assertEqual(rows["ADEPTUS_CUSTODES_CODEX_2026"]["next_action"], "WAIT_OFFICIAL_RELEASE_SIGNAL")

        workflow=(ROOT/".github/workflows/release-transition-activation-watch.yml").read_text(encoding="utf-8")
        self.assertIn("contents: read", workflow)
        self.assertIn("23 */6 * * *", workflow)
        self.assertNotIn("contents: write", workflow)
        self.assertNotIn("pull-requests: write", workflow)

    def test_normative_app_equivalence_gap_audit(self):
        audit=self.normative_gap_audit
        self.assertEqual(audit["status"], "PASS")
        self.assertEqual(audit["milestone"], "NORMATIVE_APP_EQUIVALENCE_GAP_AUDIT")
        self.assertEqual(audit["coverage_summary"]["current_normalized_factions"], 0)
        self.assertEqual(audit["coverage_summary"]["full_normative_semantic_factions"], 0)
        self.assertEqual(audit["coverage_summary"]["secondary_semantic_current_roster_identities"], 35)
        self.assertFalse(audit["authority_boundary"]["mirror_hash_match_is_normative_equivalence"])
        self.assertFalse(audit["authority_boundary"]["faction_pack_is_full_codex_replacement"])
        self.assertFalse(audit["authority_boundary"]["app_wording_inference_allowed"])

        mapping=audit["roster_source_mapping"]["counts"]
        self.assertEqual(mapping["DIRECT_NAME_MATCH"], 25)
        self.assertEqual(mapping["NAMING_ALIAS_CANDIDATE"], 3)
        self.assertEqual(mapping["PARENT_SOURCE_CANDIDATE"], 7)
        self.assertEqual(mapping["NO_PUBLIC_FACTION_PACK_MAPPING"], 2)

        gaps={x["id"]:x for x in audit["gaps"]}
        self.assertEqual(gaps["OFFICIAL_CORE_RULES_SEMANTIC_INGESTION"]["state"], "PARAGRAPH_SEMANTIC_CLASSIFICATION_CLOSED_SEMANTIC_REVIEW_PENDING")
        self.assertEqual(gaps["PUBLIC_FACTION_SUPPLEMENT_SEMANTIC_INGESTION"]["state"], "EXACT_PUBLIC_OVERLAP_AND_RESIDUAL_CLASSIFICATION_CLOSED_DEEP_EXTRACTION_PENDING")
        self.assertEqual(gaps["GW_APP_WORDING_AND_LOCKED_DATASHEET_CROSSCHECK"]["state"], "BLOCKED_ON_AUTHORIZED_APP_EVIDENCE")
        self.assertEqual(gaps["NORMATIVE_COVERAGE_ACCOUNTING"]["state"], "INTENTIONAL_ZERO_NOT_MIRROR_DATA_LOSS")
        self.assertEqual(audit["conclusion"]["recommended_next_milestone"], "CORE_RULE_PARAGRAPH_SEMANTIC_REVIEW_V1")

        findings={x["id"]:x for x in self.public_rules_discovery["findings"]}
        self.assertEqual(findings["GW_11E_CORE_RULES_PUBLIC"]["state"], "PUBLIC_OFFICIAL_SOURCE_DISCOVERED_NOT_INGESTED")
        self.assertTrue(findings["GW_11E_CORE_RULES_PUBLIC"]["asset_url"].startswith("https://assets.warhammer-community.com/"))
        self.assertTrue(self.public_rules_discovery["policy"]["no_full_faction_equivalence_from_faction_packs_alone"])

        self.assertTrue((ROOT/"tools/audit_normative_equivalence_gaps.py").exists())
        self.assertTrue((ROOT/".github/workflows/normative-equivalence-gap-audit.yml").exists())
        self.assertTrue((ROOT/"schemas/normative_equivalence_gap_audit.schema.json").exists())

    def test_official_public_semantic_fingerprint_layer(self):
        r=self.official_public_fingerprints
        self.assertEqual(r["status"], "PASS")
        self.assertEqual(r["authority"], "GAMES_WORKSHOP_OFFICIAL")
        self.assertEqual(r["summary"]["documents"], 29)
        self.assertEqual(r["summary"]["core_rules"], 1)
        self.assertEqual(r["summary"]["faction_packs"], 28)
        self.assertEqual(r["summary"]["verified"], 29)
        self.assertEqual(r["summary"]["failures"], 0)
        self.assertEqual(r["summary"]["pages"], 1430)
        self.assertEqual(r["summary"]["text_chars"], 1915296)
        self.assertEqual(r["extraction_contract"]["engine"], "pypdf 5.9.0")
        self.assertIn("do not vendor long", r["extraction_contract"]["copyright_policy"].lower())
        self.assertTrue(all("text" not in p for d in r["documents"] for p in d["pages"]))

        core=next(x for x in r["documents"] if x["document_type"]=="CORE_RULES")
        self.assertEqual(core["binary_sha256"], "f6a2443a44627ac5f0ef08407d29aa5ec7e97339998f05bc35f3ae37bf276833")
        self.assertEqual(core["semantic_sha256"], "c8b98076bb0577878fe20f33f743f429ef838cf1df9b3eda2f42e1bba6107fe7")
        self.assertEqual(core["page_count"], 88)
        packs=[x for x in r["documents"] if x["document_type"]=="FACTION_PACK"]
        self.assertEqual(len(packs), 28)
        self.assertTrue(all(x["expected_binary_sha256"]==x["binary_sha256"] for x in packs))

        snap=self.official_core_snapshot
        self.assertEqual(snap["binary_sha256"], core["binary_sha256"])
        self.assertEqual(snap["semantic_sha256"], core["semantic_sha256"])
        self.assertEqual(snap["fingerprint_report"], "reports/OFFICIAL_PUBLIC_RULES_SEMANTIC_FINGERPRINT_CURRENT.json")

        layer=self.current["official_public_semantic_fingerprints"]
        self.assertEqual(layer["state"], "PASS_FULL_PUBLIC_CORPUS")
        self.assertFalse(layer["normative_promotion"])
        self.assertEqual(layer["app_codex_equivalence"], "PENDING")
        self.assertEqual(self.coverage["global"]["current_normalized_factions"], 0)
        self.assertEqual(self.coverage["global"]["full_normative_semantic_factions"], 0)
        self.assertEqual(self.coverage["global"]["official_public_documents_fingerprinted"], 29)

        profiles=self.gate["scope_profiles"]
        self.assertEqual(profiles["official_public_semantic_fingerprints"]["content_state"], "PASS")
        self.assertEqual(profiles["core_rules"]["content_state"], "OFFICIAL_PUBLIC_PARAGRAPH_SEMANTIC_CLASSIFICATION_V1")
        self.assertEqual(profiles["faction_rules"]["content_state"], "OFFICIAL_PUBLIC_SUPPLEMENTS_FINGERPRINTED_FULL_CODEX_PENDING")
        self.assertEqual(profiles["app_wording"]["content_state"], "PENDING")

        workflow=(ROOT/".github/workflows/official-public-semantic-fingerprints.yml").read_text(encoding="utf-8")
        self.assertIn('31 3 * * *', workflow)
        self.assertIn("Assert committed fingerprint reproducibility", workflow)

    def test_core_rule_reference_atomization_layer(self):
        r=self.core_rule_atoms
        self.assertEqual(r["status"], "PASS")
        self.assertEqual(r["authority"], "GAMES_WORKSHOP_OFFICIAL")
        self.assertEqual(r["atomization_version"], "CORE_RULE_REFERENCE_ATOMIZATION_V1")
        s=r["summary"]
        self.assertEqual(s["atoms"], 141)
        self.assertEqual(s["unique_rule_refs"], 141)
        self.assertEqual(s["unique_rule_keys"], 141)
        self.assertEqual(s["families"], 24)
        self.assertEqual(s["family_ids"], [f"{i:02d}" for i in range(1,25)])
        self.assertEqual(s["classification_counts"], {
            "REPEATED_IN_FAMILY_HEADING": 5,
            "UNIQUE_IN_FAMILY_HEADING": 136,
        })
        self.assertEqual(s["heading_recovery_gaps"], 0)
        self.assertEqual(s["heading_recovery_gap_refs"], [])
        self.assertEqual(s["atoms_with_cross_references"], 40)
        self.assertTrue(s["all_atoms_have_in_family_heading"])
        self.assertTrue(r["source_verification"]["binary_sha256_match"])
        self.assertEqual(r["source_verification"]["page_semantic_fingerprints_match"], 88)
        self.assertTrue(r["source_verification"]["document_semantic_sha256_match"])
        self.assertTrue(r["authority_boundary"]["numbered_reference_identity_complete"])
        self.assertFalse(r["authority_boundary"]["paragraph_level_rules_ast_complete"])
        self.assertFalse(r["authority_boundary"]["rule_interaction_graph_complete"])
        self.assertEqual(r["authority_boundary"]["current_normalized_factions_change"], 0)

        layer=self.current["core_rule_reference_atomization"]
        self.assertEqual(layer["state"], "PASS_141_RULE_ATOMS")
        self.assertEqual(layer["atoms"], 141)
        self.assertEqual(layer["heading_recovery_gaps"], 0)
        self.assertEqual(layer["current_normalized_factions_change"], 0)
        self.assertEqual(
            self.current["source_currentness"]["core_rules_content"]["state"],
            "OFFICIAL_PUBLIC_PARAGRAPH_SEMANTIC_CLASSIFICATION_V1",
        )
        self.assertEqual(
            self.current["source_currentness"]["core_rules_content"]["normative_structured_normalization"],
            "PARAGRAPH_SEMANTIC_ROLES_CLASSIFIED_SEMANTIC_REVIEW_PENDING",
        )

        profile=self.gate["scope_profiles"]["core_rule_reference_atoms"]
        self.assertEqual(profile["content_state"], "PASS_141_RULE_ATOMS")
        self.assertEqual(profile["atoms"], 141)
        self.assertEqual(self.coverage["global"]["official_public_core_rule_atoms"], 141)
        self.assertEqual(self.coverage["global"]["official_public_core_rule_atom_heading_recovery_gaps"], 0)
        self.assertFalse(self.coverage["global"]["official_public_core_rule_paragraph_boundaries_complete"])
        self.assertFalse(self.coverage["global"]["official_public_core_rule_paragraph_ast_complete"])
        self.assertEqual(self.coverage["global"]["current_normalized_factions"], 0)
        self.assertEqual(self.coverage["global"]["full_normative_semantic_factions"], 0)

        for required in [
            "tools/build_core_rule_reference_atoms.py",
            "tests/test_core_rule_reference_atomization.py",
            "schemas/core_rule_reference_index.schema.json",
            "docs/CORE_RULE_REFERENCE_ATOMIZATION_MODEL.md",
            ".github/workflows/core-rule-reference-atomization.yml",
            "rules/11e/snapshots/2026-09-30/core_rule_atoms/index.json",
        ]:
            self.assertTrue((ROOT/required).exists(), required)

    def test_core_rule_paragraph_boundary_layer(self):
        r=self.core_rule_boundaries
        self.assertEqual(r["status"],"PASS")
        self.assertEqual(r["authority"],"GAMES_WORKSHOP_OFFICIAL")
        self.assertEqual(r["boundary_version"],"CORE_RULE_PARAGRAPH_BOUNDARY_EXTRACTION_V1")
        s=r["summary"]
        self.assertEqual(s["rules"],141)
        self.assertEqual(s["occurrences"],146)
        self.assertEqual(s["families"],24)
        self.assertEqual(s["classification_counts"],{
            "REPEATED_OCCURRENCE_BOUNDARIES_VARIANT_HASH":5,
            "SINGLE_OCCURRENCE_BOUNDARY":136,
        })
        self.assertEqual(s["heading_line_recovery_gaps"],0)
        self.assertEqual(s["heading_line_recovery_gap_refs"],[])
        self.assertEqual(s["empty_body_boundaries"],0)
        self.assertEqual(s["empty_body_boundary_refs"],[])
        self.assertEqual(s["paragraph_candidates"],310)
        self.assertEqual(s["rules_with_multiple_occurrences"],5)
        self.assertTrue(s["all_rules_have_nonempty_boundaries"])

        special={x["rule_ref"]:x for x in r["special_rules"]}
        self.assertEqual(set(special),{"15.07","15.08","15.09","15.10","15.11"})
        self.assertTrue(all(x["classification"]=="REPEATED_OCCURRENCE_BOUNDARIES_VARIANT_HASH" for x in special.values()))
        self.assertTrue(all(len(x["occurrence_hashes"])==2 for x in special.values()))

        self.assertTrue(r["source_verification"]["binary_sha256_match"])
        self.assertEqual(r["source_verification"]["page_semantic_fingerprints_match"],88)
        self.assertTrue(r["source_verification"]["document_semantic_sha256_match"])
        self.assertTrue(r["authority_boundary"]["rule_body_boundary_complete"])
        self.assertTrue(r["authority_boundary"]["paragraph_boundaries_are_extraction_candidates"])
        self.assertFalse(r["authority_boundary"]["paragraph_level_rules_ast_complete"])
        self.assertFalse(r["authority_boundary"]["rule_interaction_graph_complete"])
        self.assertFalse(r["authority_boundary"]["repeated_occurrence_hash_equality_is_semantic_equivalence"])
        self.assertEqual(r["authority_boundary"]["current_normalized_factions_change"],0)

        layer=self.current["core_rule_paragraph_boundaries"]
        self.assertEqual(layer["state"],"PASS_141_RULE_BOUNDARIES")
        self.assertEqual(layer["rules"],141)
        self.assertEqual(layer["occurrences"],146)
        self.assertEqual(layer["paragraph_candidates"],310)
        self.assertEqual(layer["heading_line_recovery_gaps"],0)
        self.assertEqual(layer["empty_body_boundaries"],0)
        self.assertEqual(self.current["next_milestone"],"CORE_RULE_PARAGRAPH_SEMANTIC_REVIEW_V1")
        self.assertEqual(
            self.current["source_currentness"]["core_rules_content"]["state"],
            "OFFICIAL_PUBLIC_PARAGRAPH_SEMANTIC_CLASSIFICATION_V1",
        )
        self.assertEqual(
            self.current["source_currentness"]["core_rules_content"]["normative_structured_normalization"],
            "PARAGRAPH_SEMANTIC_ROLES_CLASSIFIED_SEMANTIC_REVIEW_PENDING",
        )

        profile=self.gate["scope_profiles"]["core_rule_paragraph_boundaries"]
        self.assertEqual(profile["content_state"],"PASS_141_RULE_BOUNDARIES")
        self.assertEqual(profile["rules"],141)
        self.assertEqual(profile["paragraph_candidates"],310)
        self.assertEqual(profile["heading_line_recovery_gaps"],0)
        self.assertEqual(profile["empty_body_boundaries"],0)

        self.assertEqual(self.coverage["status"],"CORE_RULE_PARAGRAPH_SEMANTIC_CLASSIFICATION_V1_COMPLETE")
        self.assertEqual(self.coverage["global"]["official_public_core_rule_boundary_rules"],141)
        self.assertEqual(self.coverage["global"]["official_public_core_rule_boundary_occurrences"],146)
        self.assertEqual(self.coverage["global"]["official_public_core_rule_paragraph_candidates"],310)
        self.assertEqual(self.coverage["global"]["official_public_core_rule_heading_line_recovery_gaps"],0)
        self.assertEqual(self.coverage["global"]["official_public_core_rule_empty_body_boundaries"],0)
        self.assertEqual(self.coverage["global"]["current_normalized_factions"],0)
        self.assertEqual(self.coverage["global"]["full_normative_semantic_factions"],0)

        for required in [
            "tools/build_core_rule_paragraph_boundaries.py",
            "tests/test_core_rule_paragraph_boundaries.py",
            "schemas/core_rule_paragraph_boundaries.schema.json",
            "docs/CORE_RULE_PARAGRAPH_BOUNDARY_MODEL.md",
            ".github/workflows/core-rule-paragraph-boundaries.yml",
            "rules/11e/snapshots/2026-09-30/core_rule_boundaries/index.json",
        ]:
            self.assertTrue((ROOT/required).exists(),required)

    def test_core_rule_paragraph_atomization_layer(self):
        r=self.core_rule_paragraph_atoms
        self.assertEqual(r["status"],"PASS")
        self.assertEqual(r["authority"],"GAMES_WORKSHOP_OFFICIAL")
        self.assertEqual(r["atomization_version"],"CORE_RULE_PARAGRAPH_ATOMIZATION_V1")
        s=r["summary"]
        self.assertEqual(s["paragraph_atoms"],310)
        self.assertEqual(s["unique_paragraph_keys"],310)
        self.assertEqual(s["parent_paragraph_candidates"],310)
        self.assertEqual(s["rules_represented"],141)
        self.assertEqual(s["occurrences_represented"],146)
        self.assertEqual(s["families_represented"],24)
        self.assertEqual(s["classification_counts"],{
            "REPEATED_OCCURRENCE_PARAGRAPH_VARIANT":10,
            "SINGLE_OCCURRENCE_PARAGRAPH":300,
        })
        self.assertEqual(s["repeated_occurrence_rule_refs"],["15.07","15.08","15.09","15.10","15.11"])
        self.assertEqual(s["range_validation_failures"],0)
        self.assertEqual(s["range_validation_failure_samples"],[])
        self.assertTrue(s["all_parent_candidates_atomized"])
        self.assertEqual(s["paragraph_hashes_reproduced_from_verified_pdf"],310)

        self.assertTrue(r["source_verification"]["binary_sha256_match"])
        self.assertEqual(r["source_verification"]["page_semantic_fingerprints_match"],88)
        self.assertTrue(r["source_verification"]["document_semantic_sha256_match"])
        b=r["authority_boundary"]
        self.assertTrue(b["stable_paragraph_identity_complete"])
        self.assertTrue(b["paragraph_boundaries_are_extraction_candidates"])
        self.assertFalse(b["paragraph_semantic_ast_complete"])
        self.assertFalse(b["condition_effect_parsing_complete"])
        self.assertFalse(b["rule_interaction_graph_complete"])
        self.assertFalse(b["repeated_paragraph_variant_is_semantic_conflict"])
        self.assertEqual(b["current_normalized_factions_change"],0)

        layer=self.current["core_rule_paragraph_atomization"]
        self.assertEqual(layer["state"],"PASS_310_PARAGRAPH_ATOMS")
        self.assertEqual(layer["paragraph_atoms"],310)
        self.assertEqual(layer["unique_paragraph_keys"],310)
        self.assertEqual(layer["range_validation_failures"],0)
        self.assertEqual(self.current["next_milestone"],"CORE_RULE_PARAGRAPH_SEMANTIC_REVIEW_V1")
        self.assertEqual(
            self.current["source_currentness"]["core_rules_content"]["state"],
            "OFFICIAL_PUBLIC_PARAGRAPH_SEMANTIC_CLASSIFICATION_V1",
        )
        self.assertEqual(
            self.current["source_currentness"]["core_rules_content"]["normative_structured_normalization"],
            "PARAGRAPH_SEMANTIC_ROLES_CLASSIFIED_SEMANTIC_REVIEW_PENDING",
        )

        profile=self.gate["scope_profiles"]["core_rule_paragraph_atoms"]
        self.assertEqual(profile["content_state"],"PASS_310_PARAGRAPH_ATOMS")
        self.assertEqual(profile["paragraph_atoms"],310)
        self.assertEqual(profile["rules_represented"],141)
        self.assertEqual(profile["occurrences_represented"],146)
        self.assertEqual(profile["repeated_occurrence_paragraph_variants"],10)
        self.assertEqual(profile["range_validation_failures"],0)

        self.assertEqual(self.coverage["status"],"CORE_RULE_PARAGRAPH_SEMANTIC_CLASSIFICATION_V1_COMPLETE")
        g=self.coverage["global"]
        self.assertEqual(g["official_public_core_paragraph_atoms"],310)
        self.assertEqual(g["official_public_core_paragraph_unique_keys"],310)
        self.assertEqual(g["official_public_core_paragraph_rules_represented"],141)
        self.assertEqual(g["official_public_core_paragraph_occurrences_represented"],146)
        self.assertEqual(g["official_public_core_single_occurrence_paragraph_atoms"],300)
        self.assertEqual(g["official_public_core_repeated_occurrence_paragraph_variants"],10)
        self.assertEqual(g["official_public_core_paragraph_range_validation_failures"],0)
        self.assertFalse(g["official_public_core_paragraph_semantic_classification_complete"])
        self.assertFalse(g["official_public_core_paragraph_semantic_ast_complete"])
        self.assertEqual(g["current_normalized_factions"],0)
        self.assertEqual(g["full_normative_semantic_factions"],0)

        for required in [
            "tools/build_core_rule_paragraph_atoms.py",
            "tests/test_core_rule_paragraph_atomization.py",
            "schemas/core_rule_paragraph_atoms.schema.json",
            "docs/CORE_RULE_PARAGRAPH_ATOMIZATION_MODEL.md",
            ".github/workflows/core-rule-paragraph-atomization.yml",
            "rules/11e/snapshots/2026-09-30/core_rule_paragraph_atoms/index.json",
        ]:
            self.assertTrue((ROOT/required).exists(),required)

    def test_core_rule_paragraph_semantic_classification_layer(self):
        r=self.core_rule_paragraph_semantics
        self.assertEqual(r["status"],"PASS")
        self.assertEqual(r["authority"],"GAMES_WORKSHOP_OFFICIAL")
        self.assertEqual(r["classifier_version"],"CORE_RULE_PARAGRAPH_SEMANTIC_CLASSIFICATION_V1")
        s=r["summary"]
        self.assertEqual(s["paragraphs"],310)
        self.assertEqual(s["unique_paragraph_keys"],310)
        self.assertEqual(s["role_counts"],{
            "CONDITION_OR_TRIGGER":31,
            "MIXED":134,
            "MODIFICATION_OR_REPLACEMENT":1,
            "OBLIGATION":1,
            "PERMISSION":20,
            "PROCEDURE_OR_SEQUENCE":7,
            "PROHIBITION":4,
            "UNCLASSIFIED":112,
        })
        self.assertEqual(s["confidence_counts"],{"HIGH":64,"MIXED":134,"NONE":112})
        self.assertEqual(s["paragraphs_with_signals"],200)
        self.assertEqual(s["paragraphs_without_signals"],110)
        self.assertEqual(s["mixed_paragraphs"],134)
        self.assertEqual(s["unclassified_paragraphs"],112)
        self.assertEqual(s["repeated_variant_paragraphs"],10)
        self.assertEqual(s["repeated_variant_role_counts"],{"CONDITION_OR_TRIGGER":2,"MIXED":8})
        self.assertEqual(s["paragraph_hashes_reproduced_from_verified_pdf"],310)

        self.assertTrue(r["source_verification"]["binary_sha256_match"])
        self.assertEqual(r["source_verification"]["page_semantic_fingerprints_match"],88)
        self.assertTrue(r["source_verification"]["document_semantic_sha256_match"])
        b=r["authority_boundary"]
        self.assertTrue(b["semantic_role_classification_complete"])
        self.assertTrue(b["classification_is_lexical_structural_not_full_semantic_ast"])
        self.assertTrue(b["mixed_and_unclassified_are_valid_fail_closed_states"])
        self.assertFalse(b["paragraph_prose_committed"])
        self.assertFalse(b["condition_effect_ast_complete"])
        self.assertFalse(b["rule_interaction_graph_complete"])
        self.assertFalse(b["repeated_variant_semantic_equivalence_claimed"])
        self.assertEqual(b["current_normalized_factions_change"],0)

        layer=self.current["core_rule_paragraph_semantic_classification"]
        self.assertEqual(layer["state"],"PASS_310_PARAGRAPHS_CLASSIFIED")
        self.assertEqual(layer["paragraphs"],310)
        self.assertEqual(layer["role_counts"],s["role_counts"])
        self.assertEqual(layer["confidence_counts"],s["confidence_counts"])
        self.assertTrue(layer["semantic_review_pending"])
        self.assertTrue(layer["ast_readiness_pending"])
        self.assertFalse(layer["condition_effect_ast_complete"])
        self.assertEqual(self.current["next_milestone"],"CORE_RULE_PARAGRAPH_SEMANTIC_REVIEW_V1")
        core=self.current["source_currentness"]["core_rules_content"]
        self.assertEqual(core["state"],"OFFICIAL_PUBLIC_PARAGRAPH_SEMANTIC_CLASSIFICATION_V1")
        self.assertEqual(core["normative_structured_normalization"],"PARAGRAPH_SEMANTIC_ROLES_CLASSIFIED_SEMANTIC_REVIEW_PENDING")

        profile=self.gate["scope_profiles"]["core_rule_paragraph_semantics"]
        self.assertEqual(profile["content_state"],"PASS_310_PARAGRAPHS_CLASSIFIED")
        self.assertEqual(profile["paragraphs"],310)
        self.assertEqual(profile["role_counts"],s["role_counts"])
        self.assertEqual(profile["confidence_counts"],s["confidence_counts"])

        self.assertEqual(self.coverage["status"],"CORE_RULE_PARAGRAPH_SEMANTIC_CLASSIFICATION_V1_COMPLETE")
        g=self.coverage["global"]
        self.assertTrue(g["official_public_core_paragraph_semantic_classification_complete"])
        self.assertFalse(g["official_public_core_paragraph_semantic_ast_complete"])
        self.assertEqual(g["official_public_core_paragraph_semantic_classified"],310)
        self.assertEqual(g["official_public_core_paragraph_high_confidence"],64)
        self.assertEqual(g["official_public_core_paragraph_mixed"],134)
        self.assertEqual(g["official_public_core_paragraph_unclassified"],112)
        self.assertEqual(g["official_public_core_paragraph_role_counts"],s["role_counts"])
        self.assertEqual(g["official_public_core_paragraph_confidence_counts"],s["confidence_counts"])
        self.assertEqual(g["official_public_core_paragraph_semantic_hashes_reproduced"],310)
        self.assertEqual(g["current_normalized_factions"],0)
        self.assertEqual(g["full_normative_semantic_factions"],0)

        for required in [
            "tools/classify_core_rule_paragraph_semantics.py",
            "tests/test_core_rule_paragraph_semantic_classification.py",
            "schemas/core_rule_paragraph_semantic_classification.schema.json",
            "docs/CORE_RULE_PARAGRAPH_SEMANTIC_CLASSIFICATION_MODEL.md",
            ".github/workflows/core-rule-paragraph-semantic-classification.yml",
            "rules/11e/snapshots/2026-09-30/core_rule_paragraph_semantics/index.json",
        ]:
            self.assertTrue((ROOT/required).exists(),required)

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
        counts=self.wave_b["counts"]
        self.assertEqual(counts["roster_identities"], 37)
        self.assertEqual(counts["structural_partial"], 0)
        self.assertEqual(counts["structural_complete"] + counts["unavailable"], 37)
        self.assertEqual(len(self.wave_b["views"]), 37)
        unavailable={
            x["slug"] for x in self.wave_b["views"]
            if x["status"].startswith("UNAVAILABLE")
        }
        self.assertEqual(len(unavailable), counts["unavailable"])
        self.assertEqual(self.wave_b_manifest["source"]["last_update"], self.current["wave_b_structural"]["wahapedia_last_update"])
        self.assertEqual(self.coverage["global"]["wave_b_wahapedia_last_update"], self.wave_b_manifest["source"]["last_update"])
        if self.current["wave_b_structural"]["snapshot"].startswith("rules/11e/snapshots/2026-09-29/"):
            self.assertEqual(counts, {"roster_identities":37,"structural_complete":35,"structural_partial":0,"unavailable":2})
            self.assertEqual(unavailable, {"titanicus_traitoris","unaligned_forces"})
            self.assertEqual(self.wave_b_manifest["source"]["last_update"], "2026-09-28 02:38:04")
            self.assertEqual(self.wave_b_manifest["counts"]["datasheets"], 1660)
            self.assertEqual(self.wave_b_manifest["counts"]["ability_catalog"], 95)

    def test_wave_b_reconciliation_and_promotion(self):
        self.assertIn(self.wave_b_recon["status"], {"PASS","PASS_WITH_CONFLICTS"})
        self.assertEqual(self.wave_b_recon["conflict_count"], self.current["wave_b_structural"]["source_conflicts"])
        self.assertEqual(self.coverage["status"], "CORE_RULE_PARAGRAPH_SEMANTIC_CLASSIFICATION_V1_COMPLETE")
        complete=self.wave_b["counts"]["structural_complete"]
        self.assertEqual(sum(1 for x in self.coverage["factions"] if x.get("structural_current")), complete)
        self.assertEqual(self.coverage["global"]["current_normalized_factions"], 0)
        self.assertEqual(self.current["status"], "CURRENT_OPERATIONAL_RULES_LAYER_READY_NORMATIVE_APP_PENDING")
        self.assertEqual(self.current["wave_b_structural"]["roster_identities_complete"], complete)
        self.assertEqual(self.current["wave_b_structural"]["semantic_rule_text"], "CURRENT_SECONDARY_MIRROR_FULL_HASH_VERIFIED")
        self.assertEqual(self.current["wave_b_structural"]["faq_errata"], "SOURCE_CATALOG_CURRENT_OFFICIAL_ASSETS_VERIFIED")
        if self.current["wave_b_structural"]["snapshot"].startswith("rules/11e/snapshots/2026-09-29/"):
            self.assertEqual(self.wave_b_recon["conflict_count"], 11)
            self.assertEqual(self.wave_b_recon["totals"]["points_compared"], 1202)
            self.assertEqual(self.wave_b_recon["totals"]["unit_name_matches"], 1242)

    def test_structural_source_availability_37_of_37(self):
        g=self.coverage["global"]
        complete=self.wave_b["counts"]["structural_complete"]
        fallback_count=len(self.bsdata_fallback["views"])
        self.assertEqual(g["wave_b_current_mirror_structural_complete"], complete)
        self.assertEqual(g["wave_b_structured_implementation_fallback_complete"], fallback_count)
        self.assertEqual(g["wave_b_total_structural_source_available"], 37)
        self.assertEqual(sum(1 for x in self.coverage["factions"] if x.get("structural_source_available")), 37)
        rows={x["slug"]:x for x in self.coverage["factions"]}
        for slug in {x["slug"] for x in self.bsdata_fallback["views"]}:
            if rows[slug]["structural_current"]:
                continue
            self.assertEqual(rows[slug]["wave_b_structural"]["state"], "IMPLEMENTATION_FALLBACK_COMPLETE")
            self.assertEqual(rows[slug]["wave_b_structural"]["source_role"], "structured_implementation")
            self.assertFalse(rows[slug]["wave_b_structural"]["normative_rules_verified"])

    def test_bsdata_fallback_snapshot(self):
        registry={x["id"]:x for x in self.registry["sources"]}
        current_commit=registry["BSDATA_WH40K_11E"]["observed_revision"]["commit_sha"]
        self.assertEqual(self.bsdata_fallback["commit_sha"], current_commit)
        rows={x["slug"]:x for x in self.bsdata_fallback["views"]}
        self.assertEqual(set(rows), {"titanicus_traitoris","unaligned_forces"})
        if current_commit=="951d5900d1b4a952a4ba560a30c43788e622ccfc":
            self.assertEqual(rows["titanicus_traitoris"]["counts"]["units"], 4)
            self.assertEqual(rows["unaligned_forces"]["counts"]["units"], 22)
        else:
            self.assertTrue(all(x["counts"]["units"] > 0 for x in rows.values()))

    def test_semantic_resolver_contract(self):
        self.assertTrue((ROOT/"tools/query_current_semantics.py").exists())
        self.assertTrue((ROOT/".github/workflows/semantic-smoke.yml").exists())
        self.assertEqual(self.current["wave_b_structural"]["total_structural_source_available"], 37)
        self.assertEqual(self.current["wave_b_structural"]["semantic_rule_text"], "CURRENT_SECONDARY_MIRROR_FULL_HASH_VERIFIED")

    def test_wave_b_semantic_and_official_asset_audits(self):
        self.assertEqual(self.semantic_audit["status"], "PASS")
        expected=self.semantic_audit["expected_fingerprints"]
        matched=self.semantic_audit["counts"]["MATCH"]
        self.assertGreater(expected, 0)
        self.assertEqual(matched, expected)
        self.assertEqual(len(self.semantic_audit["problems"]), 0)
        self.assertEqual(self.official_assets["status"], "PASS")
        self.assertEqual(self.official_assets["live_source_csv"]["catalog_drift_count"], 0)
        off=self.official_assets["official_assets"]
        self.assertEqual(off["verified_pdf_assets"], off["pdf_assets"])
        self.assertEqual(off["failures"], 0)
        complete=self.current["wave_b_structural"]["roster_identities_complete"]
        g=self.coverage["global"]
        self.assertEqual(g["wave_b_current_mirror_semantic_roster_identities"], complete)
        self.assertEqual(g["wave_b_semantic_fingerprints_expected"], expected)
        self.assertEqual(g["wave_b_semantic_fingerprints_matched"], matched)
        self.assertEqual(g["wave_b_official_edition11_sources"], off["edition_11_sources"])
        self.assertEqual(g["wave_b_official_pdf_assets_verified"], off["verified_pdf_assets"])
        self.assertEqual(g["current_normalized_factions"], 0)
        self.assertEqual(self.current["status"], "CURRENT_OPERATIONAL_RULES_LAYER_READY_NORMATIVE_APP_PENDING")

    def test_upstream_watch_and_new_recruit_runtime(self):
        self.assertEqual(self.upstream_watch["status"], "NO_CHANGE")
        self.assertEqual(self.upstream_watch["change_summary"]["github_sources_changed"], [])
        self.assertEqual(self.upstream_watch["change_summary"]["wahapedia_files_changed"], 0)
        self.assertFalse(self.upstream_watch["change_summary"]["wahapedia_last_update_changed"])

        self.assertEqual(self.nr_runtime["schema_version"], "2.0")
        self.assertIn(self.nr_runtime["status"], {"PASS","PASS_WITH_KNOWN_RUNTIME_DRIFT"})
        self.assertEqual(self.nr_runtime["universe"]["resolved_runtime_identities"], 37)
        self.assertEqual(self.nr_runtime["universe"]["missing"], [])
        self.assertTrue(all(x["status"] == "PASS" for x in self.nr_runtime["universe"]["page_checks"]))
        self.assertEqual(self.nr_runtime["lineage"]["exact_sync_cadence"], "UNKNOWN_NOT_INFERRED")

        points=self.nr_runtime["representative_points"]
        surfaces=self.nr_runtime["representative_surfaces"]
        self.assertEqual(points["checks"], 15)
        self.assertEqual(surfaces["checks"], 5)
        self.assertEqual(points["new_drift_count"], 0)
        self.assertEqual(surfaces["new_drift_count"], 0)

        allowed={"NORMATIVE_MATCH","IMPLEMENTATION_DRIFT","RUNTIME_PROJECTION_DRIFT","UPSTREAM_REVISION_DRIFT","UNKNOWN_RUNTIME_DRIFT"}
        known=points["known_drifts"]+surfaces["known_drifts"]
        self.assertTrue(all(x["classification"] in allowed for x in known))
        self.assertTrue(all(x["normative_kb_change_required"] is False for x in known))

        active=[x for x in self.runtime_drifts["active"] if x["state"]=="ACTIVE"]
        self.assertTrue(all(x["classification"] in allowed-{"NORMATIVE_MATCH"} for x in active))
        self.assertTrue(all(x["normative_kb_change_required"] is False for x in active))

        automation=self.current["automation"]
        nr=automation["new_recruit_runtime"]
        self.assertEqual(automation["upstream_change_watch"]["state"], "ACTIVE_NO_CHANGE")
        self.assertEqual(nr["state"], self.nr_runtime["status"])
        self.assertEqual(nr["representative_point_checks"], points["checks"])
        self.assertEqual(nr["representative_point_matches"], points["matched"])
        self.assertEqual(nr["known_runtime_drifts"], points["known_drift_count"]+surfaces["known_drift_count"])
        self.assertEqual(nr["new_runtime_drifts"], 0)
        self.assertEqual(nr["exact_sync_cadence"], "UNKNOWN_NOT_INFERRED")
        self.assertEqual(self.current["next_milestone"], "CORE_RULE_PARAGRAPH_SEMANTIC_REVIEW_V1")
        layer=self.current["release_transition_readiness"]
        self.assertEqual(layer["state"], "OPERATIONAL_V1")
        self.assertFalse(layer["policy"]["auto_promote"])
        tracked={x["id"]:x for x in layer["tracked_transitions"]}
        self.assertEqual(tracked["SPACE_MARINES_CODEX_2026"]["state"], "PRE_RELEASE_HOLD")
        self.assertEqual(tracked["ADEPTUS_CUSTODES_CODEX_2026"]["state"], "UPCOMING_HOLD_NO_RELEASE_DATE")
        activation=self.current["release_transition_activation_watch"]
        self.assertEqual(activation["state"], "OPERATIONAL_V1")
        self.assertEqual(activation["checkpoint_status"], "NO_ACTION_REQUIRED")
        self.assertFalse(activation["safety"]["auto_promote"])
        self.assertFalse(activation["safety"]["direct_current_rules_mutation"])
        gap_layer=self.current["normative_equivalence_gap_audit"]
        self.assertEqual(gap_layer["state"], "PASS_GAPS_CLASSIFIED")
        self.assertEqual(gap_layer["current_normalized_factions"], 0)
        self.assertTrue(gap_layer["public_core_rules_source_discovered"])
        self.assertEqual(gap_layer["verified_public_faction_pack_pdfs"], 28)
        self.assertEqual(gap_layer["public_faction_pack_scope"], "SUPPLEMENTAL_NOT_FULL_CODEX")
        self.assertEqual(gap_layer["gw_app_wording"], "BLOCKED_ON_AUTHORIZED_APP_EVIDENCE")

    def test_guarded_reingestion_control_plane(self):
        required=[
            "tools/plan_upstream_reingestion.py",
            "tools/run_upstream_reingestion_candidate.py",
            "tools/apply_reingestion_promotion.py",
            "tools/sync_new_recruit_runtime_status.py",
            ".github/workflows/upstream-reingestion-candidate.yml",
            ".github/workflows/upstream-reingestion-promote.yml",
            "schemas/upstream_reingestion_plan.schema.json",
            "schemas/upstream_reingestion_candidate.schema.json",
            "schemas/upstream_reingestion_promotion.schema.json",
        ]
        for rel in required:
            self.assertTrue((ROOT/rel).exists(), rel)
        for rel in [
            "schemas/upstream_reingestion_plan.schema.json",
            "schemas/upstream_reingestion_candidate.schema.json",
            "schemas/upstream_reingestion_promotion.schema.json",
        ]:
            json.loads((ROOT/rel).read_text(encoding="utf-8"))
        promote=(ROOT/".github/workflows/upstream-reingestion-promote.yml").read_text(encoding="utf-8")
        self.assertIn("PROMOTE_REVIEWED_CANDIDATE", promote)
        self.assertIn("pull-requests: write", promote)
        self.assertIn("git switch -c", promote)
        self.assertNotIn("git push origin main", promote)

    def test_collection_aware_roster_solver(self):
        self.assertEqual(self.collection_solver["status"], "PASS")
        self.assertEqual(self.collection_solver["milestone"], "COLLECTION_AWARE_ROSTER_SOLVER")
        self.assertEqual(len(self.collection_solver["cases"]), 7)
        self.assertEqual(self.collection_solver["authority_boundary"]["full_normative_legality"], "UNKNOWN_PENDING_NORMATIVE_APP")
        self.assertEqual(self.collection_solver["authority_boundary"]["collection_status"], "PROVISIONAL")
        self.assertFalse(self.collection_solver["authority_boundary"]["normative_promotion"])

        profile = self.custodes_solver_profile
        self.assertEqual(profile["collection_status"], "PROVISIONAL")
        self.assertEqual(sum(x["physical_bodies"] for x in profile["body_pools"]), 70)
        self.assertEqual(len(profile["body_pools"]), 15)
        self.assertEqual(len(profile["component_pools"]), 12)
        self.assertTrue(any(x["mode"] == "CONVERSION_REQUIRED" for p in profile["body_pools"] for x in p["roles"]))
        self.assertTrue(any(x["id"] == "CUSTODES_VENATARI_GUARD_SPEAR_SHARING" for x in profile["unknown_constraints"]))

        solver = self.custodes_current_collection["solver"]
        self.assertEqual(solver["state"], "OPERATIONAL_PROVISIONAL")
        self.assertEqual(solver["profile"], "collection/adeptus_custodes/solver_profile.json")
        self.assertEqual(self.current["collection_aware_roster_solver"]["state"], "OPERATIONAL_V1_CUSTODES")
        self.assertEqual(self.current["collection_aware_roster_solver"]["full_normative_legality"], "UNKNOWN_PENDING_NORMATIVE_APP")
        self.assertTrue((ROOT/"tools/solve_collection_roster.py").exists())
        self.assertTrue((ROOT/".github/workflows/collection-roster-solver.yml").exists())

    def test_preview_never_replaces_current(self):
        for tr in self.release["transitions"]:
            if tr.get("upcoming_state"):
                self.assertEqual(tr.get("current_legal_state"), "CURRENT_LEGAL")

if __name__ == "__main__":
    unittest.main()
