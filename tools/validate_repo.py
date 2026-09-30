#!/usr/bin/env python3
from __future__ import annotations

import collections
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
errors: list[str] = []

VALID_STATUSES = {
    "CURRENT_VERIFIED",
    "CURRENT_PENDING_RECHECK",
    "HISTORICAL_VERIFIED",
    "PROVISIONAL",
    "UNKNOWN",
}

VALID_AUTHORITIES = {
    "official_primary",
    "official_secondary",
    "secondary_reference",
    "structured_implementation",
    "runtime_projection",
    "tooling_reference",
    "empirical_dataset",
    "analytical_model",
    "derived_extraction",
    "expert_analysis",
    "event_overlay",
    "community_intelligence",
    "personal_observation",
    "legacy_project",
}

VALID_SOURCE_ROLES = {
    "normative",
    "current_mirror",
    "structured_implementation",
    "runtime_projection",
    "validation_tooling",
    "analytics",
    "analysis",
    "tournament_raw",
    "meta_aggregator",
    "list_meta",
    "mathhammer",
    "expert_analysis",
    "architecture_reference",
    "official_source_extraction",
    "event_overlay",
    "community_intelligence",
    "historical_baseline",
    "personal_collection",
}

# 1. Every tracked JSON file must parse.
for path in ROOT.rglob("*.json"):
    if ".git" in path.parts:
        continue
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"JSON parse failure: {path.relative_to(ROOT)}: {exc}")

# 2. Bootstrap baseline registry invariants.
baseline_path = ROOT / "sources" / "baselines" / "legacy_baselines.json"
try:
    baselines = json.loads(baseline_path.read_text(encoding="utf-8"))["baselines"]
    ids = {x["id"] for x in baselines}
    required = {"RULES_ASSISTANT_V0_9_20260815", "CUSTODES_COLLECTION_V0_5_20260711"}
    missing = required - ids
    if missing:
        errors.append("Missing baseline IDs: " + ", ".join(sorted(missing)))
except Exception as exc:
    errors.append(f"Baseline registry failure: {exc}")

# 3. Source registry status vocabulary.
registry_path = ROOT / "sources" / "registry.json"
try:
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    if registry.get("status") not in VALID_STATUSES:
        errors.append(f"Invalid source registry status: {registry.get('status')}")
    source_rows = registry.get("sources", [])
    source_ids = [src.get("id") for src in source_rows]
    if len(source_ids) != len(set(source_ids)):
        errors.append("Duplicate source IDs in registry")
    required_source_ids = {
        "GW_40K_DOWNLOADS",
        "GW_MFM",
        "GW_40K_APP",
        "WAHAPEDIA_11E",
        "BSDATA_WH40K_11E",
        "NEW_RECRUIT_RUNTIME",
        "NEW_RECRUIT_WIKI",
        "GOONHAMMER_40K",
        "STAT_CHECK_40K",
        "BCP_40K",
        "TABLETOP_HERALD_40K",
        "LISTHAMMER_40K",
        "INFINITE_ARCHIVE_40K",
        "META_MERGE_40K",
        "TACTICAL_REROLL_40K",
        "HUTBER_STATS_40K",
        "UNITCRUNCH_40K",
        "ART_OF_WAR_40K",
        "FORTY_K_FIRESIDE",
        "BSDATA_MFM_11E",
    }
    missing_sources = required_source_ids - set(source_ids)
    if missing_sources:
        errors.append("Missing required external source IDs: " + ", ".join(sorted(missing_sources)))

    by_source_id = {src["id"]: src for src in source_rows if src.get("id")}
    for src in source_rows:
        if src.get("status") not in VALID_STATUSES:
            errors.append(f"Invalid source status {src.get('id')}: {src.get('status')}")
        if src.get("authority") not in VALID_AUTHORITIES:
            errors.append(f"Invalid source authority {src.get('id')}: {src.get('authority')}")
        if src.get("source_role") not in VALID_SOURCE_ROLES:
            errors.append(f"Invalid source role {src.get('id')}: {src.get('source_role')}")

    if by_source_id.get("BSDATA_WH40K_11E", {}).get("source_role") != "structured_implementation":
        errors.append("BSData 11E must remain a structured_implementation source")
    if by_source_id.get("NEW_RECRUIT_RUNTIME", {}).get("upstream_source_id") != "BSDATA_WH40K_11E":
        errors.append("New Recruit runtime must declare BSData WH40K 11E as its upstream source")
    if by_source_id.get("NEW_RECRUIT_WIKI", {}).get("upstream_source_id") != "BSDATA_WH40K_11E":
        errors.append("New Recruit Wiki must declare BSData WH40K 11E as its upstream source")
    expected_roles = {
        "BCP_40K": "tournament_raw",
        "TABLETOP_HERALD_40K": "tournament_raw",
        "STAT_CHECK_40K": "meta_aggregator",
        "INFINITE_ARCHIVE_40K": "meta_aggregator",
        "HUTBER_STATS_40K": "meta_aggregator",
        "LISTHAMMER_40K": "list_meta",
        "META_MERGE_40K": "list_meta",
        "TACTICAL_REROLL_40K": "mathhammer",
        "UNITCRUNCH_40K": "mathhammer",
        "GOONHAMMER_40K": "expert_analysis",
        "ART_OF_WAR_40K": "expert_analysis",
        "FORTY_K_FIRESIDE": "expert_analysis",
        "FORTYKDC_DATA": "architecture_reference",
        "BSDATA_MFM_11E": "official_source_extraction",
    }
    for source_id, expected_role in expected_roles.items():
        if by_source_id.get(source_id, {}).get("source_role") != expected_role:
            errors.append(f"{source_id} must remain in source role {expected_role}")

    for source in source_rows:
        for dependency in source.get("depends_on", []):
            if dependency not in by_source_id:
                errors.append(f"Unknown source dependency {source.get('id')} -> {dependency}")
        if source.get("source_role") in {"meta_aggregator", "list_meta"} and not source.get("independence_groups"):
            errors.append(f"Analytics source lacks independence_groups: {source.get('id')}")
except Exception as exc:
    errors.append(f"Source registry failure: {exc}")

# 3b. External-source currentness/conflict contracts.
try:
    gate = json.loads((ROOT / "sources" / "currentness_gate.json").read_text(encoding="utf-8"))
    gate_rows = gate.get("required_checks", [])
    gate_by_id = {x["id"]: x for x in gate_rows}
    for official_id in {"GW_40K_DOWNLOADS", "GW_MFM", "GW_40K_APP"}:
        row = gate_by_id.get(official_id)
        if not row:
            errors.append(f"Missing official currentness gate: {official_id}")
        elif row.get("blocking") is not True:
            errors.append(f"Official currentness gate must be blocking: {official_id}")
    for secondary_id in {"WAHAPEDIA_11E", "BSDATA_WH40K_11E", "NEW_RECRUIT_RUNTIME"}:
        row = gate_by_id.get(secondary_id)
        if not row:
            errors.append(f"Missing cross-check currentness gate: {secondary_id}")
        elif row.get("blocking") is not False:
            errors.append(f"Secondary/runtime currentness gate must be non-blocking: {secondary_id}")

    conflict = json.loads((ROOT / "sources" / "conflict_policy.json").read_text(encoding="utf-8"))
    required_conflict_states = {
        "SOURCE_CONFLICT",
        "IMPLEMENTATION_DRIFT",
        "RUNTIME_PROJECTION_DRIFT",
        "EVENT_SCOPE_DIFFERENCE",
    }
    missing_states = required_conflict_states - set(conflict.get("states", []))
    if missing_states:
        errors.append("Missing conflict states: " + ", ".join(sorted(missing_states)))

    nr_profile = json.loads(
        (ROOT / "sources" / "profiles" / "new_recruit_bsdata_11e.json").read_text(encoding="utf-8")
    )
    if nr_profile.get("upstream", {}).get("source_id") != "BSDATA_WH40K_11E":
        errors.append("New Recruit profile upstream must be BSDATA_WH40K_11E")
    registry_bs_sha = by_source_id.get("BSDATA_WH40K_11E", {}).get("observed_revision", {}).get("commit_sha")
    profile_bs_sha = nr_profile.get("upstream", {}).get("observed_head", {}).get("sha")
    if registry_bs_sha != profile_bs_sha:
        errors.append("BSData observed commit SHA differs between registry and New Recruit profile")
except Exception as exc:
    errors.append(f"External source contract validation failure: {exc}")

# 3b2. Release-transition readiness contracts.
try:
    release = json.loads((ROOT / "sources" / "release_state.json").read_text(encoding="utf-8"))
    readiness = json.loads((ROOT / "reports" / "RELEASE_TRANSITION_READINESS_CURRENT.json").read_text(encoding="utf-8"))
    manifests = {
        "SPACE_MARINES_CODEX_2026": json.loads(
            (ROOT / "ingestion" / "release_transitions" / "space_marines_codex_2026.json").read_text(encoding="utf-8")
        ),
        "ADEPTUS_CUSTODES_CODEX_2026": json.loads(
            (ROOT / "ingestion" / "release_transitions" / "adeptus_custodes_codex_2026.json").read_text(encoding="utf-8")
        ),
    }
    catalog = json.loads((ROOT / "factions" / "catalog.json").read_text(encoding="utf-8"))
    catalog_slugs = {x.get("slug") for x in catalog.get("factions", [])}

    if release.get("schema_version") != "1.2":
        errors.append("release_state.json must be schema 1.2 with activation watch v1")
    transition_policy = release.get("transition_policy", {})
    if transition_policy.get("state") != "OPERATIONAL_READINESS_V1":
        errors.append("Release transition policy must be OPERATIONAL_READINESS_V1")
    if transition_policy.get("auto_promote") is not False:
        errors.append("Release transition policy must keep auto_promote=false")
    if transition_policy.get("report") != "reports/RELEASE_TRANSITION_READINESS_CURRENT.json":
        errors.append("Release transition policy report pointer drifted")

    if readiness.get("status") != "PASS":
        errors.append("Release transition readiness report must PASS")
    if readiness.get("milestone") != "RELEASE_TRANSITION_INGESTION_READINESS":
        errors.append("Release transition readiness milestone id drifted")
    if readiness.get("as_of") != "2026-09-29":
        errors.append("Committed release transition readiness checkpoint must remain 2026-09-29")
    if readiness.get("global_policy", {}).get("auto_promote") is not False:
        errors.append("Release transition readiness must never auto-promote")
    if readiness.get("global_policy", {}).get("calendar_date_is_not_currentness_evidence") is not True:
        errors.append("Release date alone must not become currentness evidence")

    readiness_rows = {x.get("transition_id"): x for x in readiness.get("transitions", [])}
    if set(readiness_rows) != set(manifests):
        errors.append("Release transition readiness rows differ from tracked manifests")
    if readiness_rows.get("SPACE_MARINES_CODEX_2026", {}).get("state") != "PRE_RELEASE_HOLD":
        errors.append("Space Marines transition must remain PRE_RELEASE_HOLD at 2026-09-29 checkpoint")
    if readiness_rows.get("ADEPTUS_CUSTODES_CODEX_2026", {}).get("state") != "UPCOMING_HOLD_NO_RELEASE_DATE":
        errors.append("Custodes transition must remain UPCOMING_HOLD_NO_RELEASE_DATE at 2026-09-29 checkpoint")
    if any(x.get("promotion_eligible") is not False for x in readiness_rows.values()):
        errors.append("No release transition may be directly promotion-eligible")

    transition_rows = {x.get("id"): x for x in release.get("transitions", [])}
    for tid, manifest in manifests.items():
        if manifest.get("transition_id") != tid:
            errors.append(f"Release manifest id mismatch: {tid}")
        if not set(manifest.get("factions", [])) <= catalog_slugs:
            errors.append(f"Release manifest references unknown factions: {tid}")
        if manifest.get("baseline_current_state") != "CURRENT_LEGAL":
            errors.append(f"Release manifest baseline must remain CURRENT_LEGAL: {tid}")
        activation = manifest.get("activation_evidence", {})
        if activation.get("current_legal_confirmed") is not False:
            errors.append(f"Pre-release manifest prematurely confirmed current legality: {tid}")
        policy = manifest.get("policy", {})
        if policy.get("preview_never_promotes") is not True:
            errors.append(f"Release manifest lost preview fail-closed policy: {tid}")
        if policy.get("date_alone_never_promotes") is not True:
            errors.append(f"Release manifest lost date fail-closed policy: {tid}")
        if policy.get("require_official_current_legal_evidence") is not True:
            errors.append(f"Release manifest must require official current-legal evidence: {tid}")
        if policy.get("require_upstream_change") is not True:
            errors.append(f"Release manifest must require upstream projection change: {tid}")
        if policy.get("promotion_route") != "GUARDED_REINGESTION_CANDIDATE_REVIEWED_PROMOTION":
            errors.append(f"Release manifest promotion route drifted: {tid}")

        row = transition_rows.get(tid, {})
        expected_manifest = {
            "SPACE_MARINES_CODEX_2026": "ingestion/release_transitions/space_marines_codex_2026.json",
            "ADEPTUS_CUSTODES_CODEX_2026": "ingestion/release_transitions/adeptus_custodes_codex_2026.json",
        }[tid]
        if row.get("manifest") != expected_manifest:
            errors.append(f"release_state manifest pointer drifted: {tid}")
        if row.get("current_legal_state") != "CURRENT_LEGAL":
            errors.append(f"Preview/release-pending transition replaced current legal state: {tid}")
        if row.get("current_legal_confirmation") is not False:
            errors.append(f"release_state prematurely confirmed future current legality: {tid}")

    if manifests["SPACE_MARINES_CODEX_2026"].get("scheduled_release_date") != "2026-10-03":
        errors.append("Space Marines release-readiness date drifted")
    if manifests["ADEPTUS_CUSTODES_CODEX_2026"].get("scheduled_release_date") is not None:
        errors.append("Custodes retail release date must remain UNKNOWN until official evidence exists")

    required_release_files = [
        ROOT / "schemas" / "release_transition_manifest.schema.json",
        ROOT / "tools" / "evaluate_release_transitions.py",
        ROOT / "tools" / "record_release_activation.py",
        ROOT / ".github" / "workflows" / "release-transition-readiness.yml",
        ROOT / "tests" / "test_release_transition_readiness.py",
    ]
    for path in required_release_files:
        if not path.exists():
            errors.append(f"Missing release-transition readiness artifact: {path.relative_to(ROOT)}")

    recorder = (ROOT / "tools" / "record_release_activation.py").read_text(encoding="utf-8")
    if 'ROOT/"rules"/"11e"/"current.json"' in recorder:
        errors.append("Release activation recorder must not directly mutate rules/11e/current.json")
    readiness_workflow = (ROOT / ".github" / "workflows" / "release-transition-readiness.yml").read_text(encoding="utf-8")
    if "contents: read" not in readiness_workflow:
        errors.append("Release-transition readiness workflow must remain repository read-only")
    if "release-transition auto-promotion: DISABLED" not in readiness_workflow:
        errors.append("Release-transition readiness workflow lost explicit no-auto-promotion assertion")
    activation_report = json.loads(
        (ROOT / "reports" / "RELEASE_TRANSITION_ACTIVATION_WATCH_CURRENT.json").read_text(encoding="utf-8")
    )
    activation_cfg = release.get("activation_watch", {})
    if activation_cfg.get("state") != "OPERATIONAL_V1":
        errors.append("Release transition activation watch must be OPERATIONAL_V1")
    if activation_cfg.get("current_status") != "NO_ACTION_REQUIRED":
        errors.append("Release transition activation watch checkpoint status drifted")
    if activation_cfg.get("auto_promote") is not False:
        errors.append("Release transition activation watch must keep auto_promote=false")
    if activation_cfg.get("direct_current_rules_mutation") is not False:
        errors.append("Release transition activation watch must remain read-only")
    if activation_cfg.get("cadence") != "every 6 hours":
        errors.append("Release transition activation watch cadence drifted")
    if activation_cfg.get("report") != "reports/RELEASE_TRANSITION_ACTIVATION_WATCH_CURRENT.json":
        errors.append("Release transition activation watch report pointer drifted")

    if activation_report.get("status") != "NO_ACTION_REQUIRED":
        errors.append("Committed activation watch checkpoint must be NO_ACTION_REQUIRED")
    if activation_report.get("as_of") != "2026-09-29":
        errors.append("Committed activation watch checkpoint must remain 2026-09-29")
    if activation_report.get("summary", {}).get("transition_count") != 2:
        errors.append("Activation watch must track exactly two pending transitions")
    if activation_report.get("summary", {}).get("no_action") != 2:
        errors.append("Activation watch checkpoint should have two NO_ACTION transitions")
    if any(x.get("promotion_eligible") is not False for x in activation_report.get("transitions", [])):
        errors.append("Activation watch must never mark direct promotion eligibility")
    safety = activation_report.get("safety", {})
    if safety.get("auto_promote") is not False or safety.get("direct_current_rules_mutation") is not False:
        errors.append("Activation watch safety contract drifted")

    activation_workflow = ROOT / ".github" / "workflows" / "release-transition-activation-watch.yml"
    activation_tool = ROOT / "tools" / "watch_release_transition_activation.py"
    activation_test = ROOT / "tests" / "test_release_transition_activation_watch.py"
    for path in [activation_workflow, activation_tool, activation_test]:
        if not path.exists():
            errors.append(f"Missing release activation watch artifact: {path.relative_to(ROOT)}")
    if activation_workflow.exists():
        activation_text = activation_workflow.read_text(encoding="utf-8")
        if "contents: read" not in activation_text:
            errors.append("Activation watch workflow must remain repository read-only")
        if "contents: write" in activation_text or "pull-requests: write" in activation_text:
            errors.append("Activation watch workflow acquired mutation permissions")
        if "23 */6 * * *" not in activation_text:
            errors.append("Activation watch workflow cadence no longer matches six-hour schedule")
except Exception as exc:
    errors.append(f"Release-transition readiness validation failure: {exc}")

# 3b3. Normative/app equivalence gap audit contracts.
try:
    audit = json.loads(
        (ROOT / "reports" / "NORMATIVE_APP_EQUIVALENCE_GAP_AUDIT_CURRENT.json").read_text(encoding="utf-8")
    )
    public_rules = json.loads(
        (ROOT / "sources" / "discoveries" / "gw_public_rules_surface_2026-09-29.json").read_text(encoding="utf-8")
    )
    if audit.get("status") != "PASS":
        errors.append("Normative/app equivalence gap audit must PASS")
    if audit.get("milestone") != "NORMATIVE_APP_EQUIVALENCE_GAP_AUDIT":
        errors.append("Normative/app equivalence gap audit milestone id drifted")

    boundary = audit.get("authority_boundary", {})
    if boundary.get("normative_authority") != "GAMES_WORKSHOP":
        errors.append("Normative gap audit lost Games Workshop authority")
    if boundary.get("mirror_hash_match_is_normative_equivalence") is not False:
        errors.append("Normative gap audit must not equate mirror hashes with normative equivalence")
    if boundary.get("faction_pack_is_full_codex_replacement") is not False:
        errors.append("Faction packs must not be treated as full Codex replacements")
    if boundary.get("app_wording_inference_allowed") is not False:
        errors.append("App-only wording inference must remain prohibited")

    summary = audit.get("coverage_summary", {})
    if summary.get("roster_universe") != 37:
        errors.append("Normative gap audit roster universe drifted")
    if summary.get("current_normalized_factions") != 0:
        errors.append("Normative gap audit must preserve current_normalized_factions=0 at this checkpoint")
    if summary.get("full_normative_semantic_factions") != 0:
        errors.append("Normative gap audit must preserve full_normative_semantic_factions=0")
    if summary.get("secondary_semantic_current_roster_identities") != 35:
        errors.append("Normative gap audit secondary semantic roster count drifted")
    if any(v != 0 for v in summary.get("normative_semantic_complete_by_dimension", {}).values()):
        errors.append("Normative semantic dimensions must remain unpromoted at audit checkpoint")
    if any(v != 37 for v in summary.get("normative_semantic_zero_by_dimension", {}).values()):
        errors.append("Normative semantic zero-count accounting drifted")

    mapping = audit.get("roster_source_mapping", {}).get("counts", {})
    expected_mapping = {
        "DIRECT_NAME_MATCH": 25,
        "NAMING_ALIAS_CANDIDATE": 3,
        "NO_PUBLIC_FACTION_PACK_MAPPING": 2,
        "PARENT_SOURCE_CANDIDATE": 7,
    }
    if mapping != expected_mapping:
        errors.append(f"Normative source-to-roster mapping baseline drifted: {mapping}")

    gaps = {x.get("id"): x for x in audit.get("gaps", [])}
    expected_states = {
        "OFFICIAL_CORE_RULES_SEMANTIC_INGESTION": "PARAGRAPH_SEMANTIC_REVIEW_CLOSED_AST_READINESS_PENDING",
        "PUBLIC_FACTION_SUPPLEMENT_SEMANTIC_INGESTION": "EXACT_PUBLIC_OVERLAP_AND_RESIDUAL_CLASSIFICATION_CLOSED_DEEP_EXTRACTION_PENDING",
        "FULL_FACTION_CODEX_APP_SEMANTICS": "BLOCKED_OR_CONDITIONAL_ON_AUTHORIZED_CODEX_APP_EVIDENCE",
        "MIRROR_TO_OFFICIAL_SEMANTIC_EQUIVALENCE": "PUBLIC_EXACT_OVERLAP_SCOPED_RESIDUALS_CLASSIFIED_FULL_EQUIVALENCE_PENDING",
        "GW_APP_WORDING_AND_LOCKED_DATASHEET_CROSSCHECK": "BLOCKED_ON_AUTHORIZED_APP_EVIDENCE",
        "OFFICIAL_SOURCE_TO_ROSTER_IDENTITY_MAPPING": "CLOSABLE_WITH_METADATA_AND_CONTENT_REVIEW",
        "NORMATIVE_COVERAGE_ACCOUNTING": "INTENTIONAL_ZERO_NOT_MIRROR_DATA_LOSS",
    }
    for gap_id, state in expected_states.items():
        if gaps.get(gap_id, {}).get("state") != state:
            errors.append(f"Normative gap state drifted: {gap_id}")

    findings = {x.get("id"): x for x in public_rules.get("findings", [])}
    core = findings.get("GW_11E_CORE_RULES_PUBLIC", {})
    if core.get("state") != "PUBLIC_OFFICIAL_SOURCE_DISCOVERED_NOT_INGESTED":
        errors.append("Official public Core Rules discovery state drifted")
    if not str(core.get("asset_url", "")).startswith("https://assets.warhammer-community.com/"):
        errors.append("Official public Core Rules asset URL is not an official asset URL")
    if public_rules.get("policy", {}).get("no_full_faction_equivalence_from_faction_packs_alone") is not True:
        errors.append("Public-rules discovery lost faction-pack scope boundary")

    if audit.get("conclusion", {}).get("recommended_next_milestone") != "CORE_RULE_SEMANTIC_AST_READINESS_V1":
        errors.append("Normative gap audit recommended next milestone drifted")
    if audit.get("official_public_surface", {}).get("official_public_semantic_fingerprints") != "PASS":
        errors.append("Normative gap audit must record official public fingerprint evidence as PASS")

    for required in [
        ROOT / "tools" / "audit_normative_equivalence_gaps.py",
        ROOT / "tests" / "test_normative_equivalence_gap_audit.py",
        ROOT / "schemas" / "normative_equivalence_gap_audit.schema.json",
        ROOT / ".github" / "workflows" / "normative-equivalence-gap-audit.yml",
    ]:
        if not required.exists():
            errors.append(f"Missing normative gap audit artifact: {required.relative_to(ROOT)}")
except Exception as exc:
    errors.append(f"Normative/app equivalence gap audit validation failure: {exc}")

# 3b4. Official public Games Workshop semantic fingerprint evidence.
try:
    official_fp = json.loads(
        (ROOT / "reports" / "OFFICIAL_PUBLIC_RULES_SEMANTIC_FINGERPRINT_CURRENT.json").read_text(encoding="utf-8")
    )
    core_asset = json.loads(
        (ROOT / "sources" / "snapshots" / "gw_11e_core_rules_asset_2026-09-29.json").read_text(encoding="utf-8")
    )
    current_rules = json.loads((ROOT / "rules" / "11e" / "current.json").read_text(encoding="utf-8"))
    cov = json.loads((ROOT / "coverage" / "current.json").read_text(encoding="utf-8"))
    gate = json.loads((ROOT / "sources" / "currentness_gate.json").read_text(encoding="utf-8"))
    registry_now = json.loads((ROOT / "sources" / "registry.json").read_text(encoding="utf-8"))

    if official_fp.get("status") != "PASS":
        errors.append("Official public semantic fingerprint corpus must PASS")
    if official_fp.get("authority") != "GAMES_WORKSHOP_OFFICIAL":
        errors.append("Official public fingerprint corpus lost Games Workshop authority")

    fp_summary = official_fp.get("summary", {})
    expected_fp_summary = {
        "documents": 29,
        "core_rules": 1,
        "faction_packs": 28,
        "verified": 29,
        "failures": 0,
        "pages": 1430,
        "text_chars": 1915296,
    }
    for key, value in expected_fp_summary.items():
        if fp_summary.get(key) != value:
            errors.append(f"Official public fingerprint summary {key} drifted: {fp_summary.get(key)} != {value}")

    extraction = official_fp.get("extraction_contract", {})
    if extraction.get("engine") != "pypdf 5.9.0":
        errors.append("Official public fingerprint extractor version drifted")
    if extraction.get("normalization_version") != "OFFICIAL_TEXT_NFKC_WS_V1":
        errors.append("Official public fingerprint normalization version drifted")
    if "do not vendor long" not in str(extraction.get("copyright_policy", "")).lower():
        errors.append("Official public fingerprint copyright boundary drifted")

    documents = official_fp.get("documents", [])
    if len(documents) != 29:
        errors.append("Official public fingerprint document list must contain 29 documents")
    core_docs = [x for x in documents if x.get("document_type") == "CORE_RULES"]
    pack_docs = [x for x in documents if x.get("document_type") == "FACTION_PACK"]
    if len(core_docs) != 1 or len(pack_docs) != 28:
        errors.append("Official public fingerprint corpus must contain 1 Core Rules + 28 Faction Packs")
    if any(x.get("verification") != "PASS" for x in documents):
        errors.append("Official public fingerprint corpus contains a failed document")
    if any("text" in page for doc in documents for page in doc.get("pages", [])):
        errors.append("Official public fingerprint report must not vendor extracted rules prose")
    if any(x.get("expected_binary_sha256") != x.get("binary_sha256") for x in pack_docs):
        errors.append("Official Faction Pack binary SHA differs from previously verified asset SHA")

    if core_docs:
        core = core_docs[0]
        expected_core_binary = "f6a2443a44627ac5f0ef08407d29aa5ec7e97339998f05bc35f3ae37bf276833"
        expected_core_semantic = "c8b98076bb0577878fe20f33f743f429ef838cf1df9b3eda2f42e1bba6107fe7"
        if core.get("binary_sha256") != expected_core_binary:
            errors.append("Official 11E Core Rules binary SHA drifted")
        if core.get("semantic_sha256") != expected_core_semantic:
            errors.append("Official 11E Core Rules semantic SHA drifted")
        if core.get("page_count") != 88:
            errors.append("Official 11E Core Rules page count drifted")
        if core_asset.get("binary_sha256") != core.get("binary_sha256"):
            errors.append("Core Rules asset snapshot binary SHA differs from fingerprint report")
        if core_asset.get("semantic_sha256") != core.get("semantic_sha256"):
            errors.append("Core Rules asset snapshot semantic SHA differs from fingerprint report")
        if core_asset.get("fingerprint_report") != "reports/OFFICIAL_PUBLIC_RULES_SEMANTIC_FINGERPRINT_CURRENT.json":
            errors.append("Core Rules asset snapshot fingerprint report pointer drifted")

    fp_layer = current_rules.get("official_public_semantic_fingerprints", {})
    if fp_layer.get("state") != "PASS_FULL_PUBLIC_CORPUS":
        errors.append("Current rules must record official public fingerprint corpus as PASS_FULL_PUBLIC_CORPUS")
    if fp_layer.get("documents") != 29 or fp_layer.get("faction_packs") != 28:
        errors.append("Current rules official public fingerprint corpus counts drifted")
    if fp_layer.get("normative_promotion") is not False:
        errors.append("Official public fingerprints must not directly promote normative faction completeness")
    if fp_layer.get("app_codex_equivalence") != "PENDING":
        errors.append("Official public fingerprints must preserve app/Codex equivalence as PENDING")
    if fp_layer.get("core_rules_binary_sha256") != "f6a2443a44627ac5f0ef08407d29aa5ec7e97339998f05bc35f3ae37bf276833":
        errors.append("Current rules Core Rules binary SHA pointer drifted")

    core_current = current_rules.get("source_currentness", {}).get("core_rules_content", {})
    if core_current.get("state") != "OFFICIAL_PUBLIC_PARAGRAPH_SEMANTIC_REVIEW_V1":
        errors.append("Core Rules currentness must record section structure v1 after preserving fingerprint evidence")
    if core_current.get("normative_structured_normalization") != "PARAGRAPH_SEMANTIC_REVIEW_COMPLETE_AST_READINESS_PENDING":
        errors.append("Core Rules structured normalization boundary must remain section-level complete / paragraph AST pending")

    supplements = current_rules.get("source_currentness", {}).get("faction_rules_content", {}).get("official_public_supplements", {})
    if supplements.get("state") != "OFFICIAL_PUBLIC_SUPPLEMENTS_FINGERPRINTED":
        errors.append("Official public faction supplements fingerprint state drifted")
    if supplements.get("faction_pack_pdfs") != 28:
        errors.append("Official public faction supplement count drifted")
    if supplements.get("scope") != "SUPPLEMENTAL_NOT_FULL_CODEX":
        errors.append("Faction Pack scope must remain supplemental, not full Codex")
    if supplements.get("full_codex_equivalence") != "NOT_CLAIMED":
        errors.append("Faction Pack fingerprints must not claim full Codex equivalence")

    gcov = cov.get("global", {})
    if gcov.get("official_public_documents_fingerprinted") != 29:
        errors.append("Coverage official public fingerprint document count drifted")
    if gcov.get("official_public_pages_fingerprinted") != 1430:
        errors.append("Coverage official public fingerprint page count drifted")
    if gcov.get("official_public_text_chars_fingerprinted") != 1915296:
        errors.append("Coverage official public fingerprint text-char count drifted")
    if gcov.get("official_public_fingerprint_failures") != 0:
        errors.append("Coverage official public fingerprint failures must remain zero")
    if gcov.get("current_normalized_factions") != 0 or gcov.get("full_normative_semantic_factions") != 0:
        errors.append("Official public fingerprints must not change strict full-normative faction counters")

    profiles = gate.get("scope_profiles", {})
    if profiles.get("official_public_semantic_fingerprints", {}).get("content_state") != "PASS":
        errors.append("Currentness gate official public fingerprint profile must PASS")
    if profiles.get("core_rules", {}).get("content_state") != "OFFICIAL_PUBLIC_PARAGRAPH_SEMANTIC_REVIEW_V1":
        errors.append("Currentness gate Core Rules state drifted")
    if profiles.get("faction_rules", {}).get("content_state") != "OFFICIAL_PUBLIC_SUPPLEMENTS_FINGERPRINTED_FULL_CODEX_PENDING":
        errors.append("Currentness gate faction-rules public supplement state drifted")
    if profiles.get("app_wording", {}).get("content_state") != "PENDING":
        errors.append("App wording gate must remain PENDING")

    registry_rows = {x.get("id"): x for x in registry_now.get("sources", [])}
    gw_downloads = registry_rows.get("GW_40K_DOWNLOADS", {})
    if gw_downloads.get("repository_coverage_state") != "PUBLIC_OFFICIAL_SEMANTIC_FINGERPRINTED_PARTIAL":
        errors.append("GW downloads registry coverage state drifted")
    fp_obs = gw_downloads.get("observed_revision", {}).get("official_public_semantic_fingerprints", {})
    if fp_obs.get("documents") != 29 or fp_obs.get("pages") != 1430:
        errors.append("GW downloads registry fingerprint observation drifted")

    for required in [
        ROOT / "tools" / "build_official_public_semantic_fingerprints.py",
        ROOT / "tests" / "test_official_public_semantic_fingerprints.py",
        ROOT / "schemas" / "official_public_semantic_fingerprint.schema.json",
        ROOT / ".github" / "workflows" / "official-public-semantic-fingerprints.yml",
    ]:
        if not required.exists():
            errors.append(f"Missing official public fingerprint artifact: {required.relative_to(ROOT)}")
except Exception as exc:
    errors.append(f"Official public semantic fingerprint validation failure: {exc}")

# 3c. Competitive analytics / roster recommendation contracts.
try:
    matrix = json.loads(
        (ROOT / "analytics" / "ANALYTICS_SOURCE_MATRIX.json").read_text(encoding="utf-8")
    )
    matrix_rows = matrix.get("sources", [])
    matrix_ids = [row.get("id") for row in matrix_rows]
    if len(matrix_ids) != len(set(matrix_ids)):
        errors.append("Duplicate source IDs in analytics source matrix")
    for source_id in matrix_ids:
        if source_id not in by_source_id:
            errors.append(f"Analytics matrix source missing from registry: {source_id}")

    required_matrix_ids = {
        "BCP_40K",
        "TABLETOP_HERALD_40K",
        "STAT_CHECK_40K",
        "INFINITE_ARCHIVE_40K",
        "LISTHAMMER_40K",
        "META_MERGE_40K",
        "TACTICAL_REROLL_40K",
        "UNITCRUNCH_40K",
        "GOONHAMMER_40K",
        "ART_OF_WAR_40K",
        "FORTY_K_FIRESIDE",
    }
    missing_matrix = required_matrix_ids - set(matrix_ids)
    if missing_matrix:
        errors.append("Missing required analytics matrix IDs: " + ", ".join(sorted(missing_matrix)))

    evidence_model = json.loads(
        (ROOT / "analytics" / "roster_recommendation_evidence_model.json").read_text(encoding="utf-8")
    )
    competitive_weights = evidence_model.get("competitive_support_weights", {})
    personal_weights = evidence_model.get("personal_fit_weights", {})
    if sum(competitive_weights.values()) != 100:
        errors.append("Competitive support weights must sum to 100")
    if sum(personal_weights.values()) != 100:
        errors.append("Personal fit weights must sum to 100")

    required_states = {
        "CORE_SUPPORTED",
        "STRONG_OPTION",
        "CONTEXTUAL_OPTION",
        "TECH_CHOICE",
        "EXPERIMENTAL",
        "CONFLICTED_EVIDENCE",
        "INSUFFICIENT_DATA",
        "ILLEGAL_OR_UNVERIFIED",
        "NOT_CURRENTLY_BUILDABLE",
    }
    missing_rec_states = required_states - set(evidence_model.get("recommendation_states", []))
    if missing_rec_states:
        errors.append("Missing roster recommendation states: " + ", ".join(sorted(missing_rec_states)))

    if not (ROOT / "schemas" / "roster_recommendation_evidence.schema.json").exists():
        errors.append("Missing roster recommendation evidence schema")

    # Derived analytics must expose their shared upstream lineage.
    for source_id in {"INFINITE_ARCHIVE_40K", "LISTHAMMER_40K", "META_MERGE_40K", "HUTBER_STATS_40K"}:
        src = by_source_id.get(source_id, {})
        if not src.get("independence_groups"):
            errors.append(f"Derived analytics source missing lineage groups: {source_id}")

    if "LISTHAMMER_40K" not in by_source_id.get("META_MERGE_40K", {}).get("depends_on", []):
        errors.append("Meta Merge must declare Listhammer as an upstream dependency")
    if "BCP_40K" not in by_source_id.get("INFINITE_ARCHIVE_40K", {}).get("depends_on", []):
        errors.append("Infinite Archive performance layer must retain BCP dependency")
except Exception as exc:
    errors.append(f"Analytics evidence contract validation failure: {exc}")

# 3d. Painting knowledge-base invariants.
try:
    paint_manifest = json.loads(
        (ROOT / "hobby" / "painting" / "source_manifest_v25.json").read_text(encoding="utf-8")
    )
    paint_inv = json.loads(
        (ROOT / "hobby" / "painting" / "inventory" / "snapshots" / "2026-09-29_v25.json").read_text(encoding="utf-8")
    )
    paint_recipes = json.loads(
        (ROOT / "hobby" / "painting" / "recipes" / "catalog_v25.json").read_text(encoding="utf-8")
    )
    paint_project = json.loads(
        (ROOT / "hobby" / "painting" / "projects" / "daemon_prince" / "project_v25.json").read_text(encoding="utf-8")
    )
    paint_cost = json.loads(
        (ROOT / "hobby" / "painting" / "economics" / "replacement_cost_2026-09-29.json").read_text(encoding="utf-8")
    )

    artifact = ROOT / "hobby" / "painting" / "artifacts" / "original" / "Ревизия_красок_база_техник_v25.xlsx"
    if not artifact.exists():
        errors.append("Missing painting v25 source artifact")
    else:
        raw = artifact.read_bytes()
        if len(raw) != 497616:
            errors.append(f"Painting v25 artifact size mismatch: {len(raw)} != 497616")
        got = hashlib.sha256(raw).hexdigest()
        expected = "1679f1a20dd1e4bc064fb96c577fa9d8c3f54f04a634756febef4abfe2cd7941"
        if got != expected:
            errors.append(f"Painting v25 artifact SHA-256 mismatch: {got} != {expected}")

    summary = paint_inv.get("summary", {})
    if summary.get("total_containers_and_materials") != 217:
        errors.append("Painting inventory must contain 217 containers/materials in v25")
    if summary.get("unique_products_by_identity") != 212:
        errors.append("Painting inventory must contain 212 unique product identities in v25")
    if summary.get("brand_count") != 5:
        errors.append("Painting inventory must contain 5 brands in v25")

    recipes = paint_recipes.get("recipes", [])
    recipe_ids = [int(x["recipe_id"]) for x in recipes]
    if len(recipes) != 540 or recipe_ids != list(range(1, 541)):
        errors.append("Painting recipe catalogue must contain contiguous IDs 1..540")

    if paint_project.get("stage_count") != 20 or len(paint_project.get("stages", [])) != 20:
        errors.append("Demon Prince v25 project must contain 20 stages")
    if paint_project.get("session_count") != 12 or len(paint_project.get("sessions", [])) != 12:
        errors.append("Demon Prince v25 project must contain 12 sessions")
    if paint_cost.get("base_replacement_cost_rub") != 143088:
        errors.append("Painting v25 replacement-cost baseline must remain 143088 RUB")

    if paint_manifest.get("invariants", {}).get("recipe_count") != 540:
        errors.append("Painting manifest recipe invariant drifted")
except Exception as exc:
    errors.append(f"Painting knowledge-base validation failure: {exc}")

# 3e. Current MFM Wave A contracts.
try:
    mfm_index = json.loads(
        (ROOT / "rules" / "11e" / "snapshots" / "2026-09-29" / "mfm" / "index.json").read_text(encoding="utf-8")
    )
    if mfm_index.get("official_source", {}).get("version") != "1.4":
        errors.append("Current MFM snapshot must remain version 1.4 for 2026-09-29")
    if mfm_index.get("official_source", {}).get("last_updated") != "2026-09-02":
        errors.append("Current MFM snapshot update date drifted")
    expected_totals = {
        "units": 1789,
        "detachments": 348,
        "pricing_rows": 2980,
        "leader_relations": 1574,
        "support_relations": 571,
        "wargear_cost_entries": 107,
        "enhancement_cost_entries": 1193,
        "legends_units": 326,
    }
    for key, value in expected_totals.items():
        if mfm_index.get("totals", {}).get(key) != value:
            errors.append(f"MFM aggregate {key} drifted: {mfm_index.get('totals', {}).get(key)} != {value}")
    faction_files = mfm_index.get("faction_files", [])
    if len(faction_files) != 30:
        errors.append(f"Expected 30 normalized MFM faction pages, got {len(faction_files)}")
    for rel in faction_files:
        path = ROOT / rel
        if not path.exists():
            errors.append(f"Missing normalized MFM faction snapshot: {rel}")
            continue
        snap = json.loads(path.read_text(encoding="utf-8"))
        if snap.get("mfm_version") != "1.4":
            errors.append(f"MFM version drift in {rel}")
        if snap.get("provenance", {}).get("extraction_commit") != "61a687e858c00a4ad205d564959c622a5605ef3d":
            errors.append(f"MFM extraction commit drift in {rel}")

    cov = json.loads((ROOT / "coverage" / "current.json").read_text(encoding="utf-8"))
    wave_dims = set(mfm_index.get("coverage", {}).get("dimensions", []))
    mapped = 0
    for row in cov.get("factions", []):
        if row.get("mfm_applicable"):
            mapped += 1
            for dim in wave_dims:
                if row.get("coverage", {}).get(dim) != 100:
                    errors.append(f"Incomplete MFM Wave A coverage {row.get('slug')}.{dim}")
    if mapped != 36:
        errors.append(f"Expected 36 MFM-mapped roster identities, got {mapped}")
except Exception as exc:
    errors.append(f"MFM Wave A validation failure: {exc}")

# 3f. Wave B structural ingestion contracts.
try:
    current_rules = json.loads((ROOT / "rules" / "11e" / "current.json").read_text(encoding="utf-8"))
    cov = json.loads((ROOT / "coverage" / "current.json").read_text(encoding="utf-8"))
    wb_current = current_rules.get("wave_b_structural", {})

    view_index_path = ROOT / wb_current["snapshot"]
    waha_root = view_index_path.parent.parent
    waha_manifest = json.loads((waha_root / "manifest.json").read_text(encoding="utf-8"))
    view_index = json.loads(view_index_path.read_text(encoding="utf-8"))
    ability_catalog = json.loads((waha_root / "ability_catalog.json").read_text(encoding="utf-8"))
    reconciliation = json.loads((ROOT / wb_current["reconciliation_report"]).read_text(encoding="utf-8"))

    conflict_pointer = wb_current.get("conflict_snapshot")
    wave_b_conflicts = None
    if conflict_pointer:
        wave_b_conflicts = json.loads((ROOT / conflict_pointer).read_text(encoding="utf-8"))
    elif (ROOT / "sources" / "snapshots" / "2026-09-29_wave_b_conflicts.json").exists():
        wave_b_conflicts = json.loads(
            (ROOT / "sources" / "snapshots" / "2026-09-29_wave_b_conflicts.json").read_text(encoding="utf-8")
        )

    counts = view_index.get("counts", {})
    if counts.get("roster_identities") != 37:
        errors.append(f"Wave B roster-view universe must remain 37, got {counts.get('roster_identities')}")
    if counts.get("structural_partial") != 0:
        errors.append(f"Wave B roster views must not contain structural partials: {counts}")
    if counts.get("structural_complete", 0) + counts.get("unavailable", 0) != 37:
        errors.append(f"Wave B roster-view completeness does not cover 37 identities: {counts}")
    if len(view_index.get("views", [])) != 37:
        errors.append(f"Wave B roster-view index must contain 37 rows, got {len(view_index.get('views', []))}")

    unavailable = {
        x.get("slug")
        for x in view_index.get("views", [])
        if str(x.get("status", "")).startswith("UNAVAILABLE")
    }
    if len(unavailable) != counts.get("unavailable"):
        errors.append("Wave B unavailable roster-view count disagrees with index rows")

    is_bootstrap_wave_b = waha_root.parent.name == "2026-09-29"
    if is_bootstrap_wave_b:
        expected_view_counts = {
            "roster_identities": 37,
            "structural_complete": 35,
            "structural_partial": 0,
            "unavailable": 2,
        }
        if counts != expected_view_counts:
            errors.append(f"Bootstrap Wave B roster-view counts drifted: {counts} != {expected_view_counts}")
        if unavailable != {"titanicus_traitoris", "unaligned_forces"}:
            errors.append(f"Bootstrap Wave B unavailable roster views drifted: {sorted(unavailable)}")
        if waha_manifest.get("source", {}).get("last_update") != "2026-09-28 02:38:04":
            errors.append("Bootstrap Wave B Wahapedia source timestamp drifted")
        expected_wave_b_counts = {
            "factions": 25,
            "ability_catalog": 95,
            "datasheets": 1660,
            "models": 1763,
            "weapons": 8972,
            "keywords": 16188,
            "abilities": 6934,
            "options": 2745,
            "composition_rows": 2103,
            "leader_rows": 1595,
            "army_abilities": 81,
            "detachments": 329,
            "detachment_abilities": 350,
            "enhancements": 1024,
            "stratagems": 1570,
        }
        for key, value in expected_wave_b_counts.items():
            if waha_manifest.get("counts", {}).get(key) != value:
                errors.append(
                    f"Bootstrap Wave B Wahapedia aggregate {key} drifted: "
                    f"{waha_manifest.get('counts', {}).get(key)} != {value}"
                )

    bad_ability_ids = [x.get("id") for x in ability_catalog if not str(x.get("id", "")).isdigit()]
    if bad_ability_ids:
        errors.append(f"Wave B ability catalogue contains malformed IDs: {bad_ability_ids[:5]}")

    if reconciliation.get("status") not in {"PASS", "PASS_WITH_CONFLICTS"}:
        errors.append(f"Unexpected Wave B reconciliation state: {reconciliation.get('status')}")
    if reconciliation.get("conflict_count") != wb_current.get("source_conflicts"):
        errors.append("Current Wave B conflict count differs from current reconciliation report")
    if is_bootstrap_wave_b:
        if reconciliation.get("conflict_count") != 11:
            errors.append(f"Bootstrap expected 11 retained Wave B source conflicts, got {reconciliation.get('conflict_count')}")
        if reconciliation.get("totals", {}).get("points_compared") != 1202:
            errors.append("Bootstrap Wave B reconciliation point-comparison baseline drifted")
        if reconciliation.get("totals", {}).get("unit_name_matches") != 1242:
            errors.append("Bootstrap Wave B reconciliation unit-name overlap baseline drifted")

    if wave_b_conflicts is not None:
        if wave_b_conflicts.get("state") != "SOURCE_CONFLICT":
            errors.append("Wave B conflict snapshot must remain SOURCE_CONFLICT")
        if wave_b_conflicts.get("conflict_count") != reconciliation.get("conflict_count"):
            errors.append("Wave B conflict snapshot count differs from reconciliation report")

    global_cov = cov.get("global", {})
    if cov.get("status") != "CORE_RULE_PARAGRAPH_SEMANTIC_REVIEW_V1_COMPLETE":
        errors.append("coverage/current.json must record structured normalization expansion v1 after overlap closure")
    if global_cov.get("wave_b_structural_roster_identities_complete") != counts.get("structural_complete"):
        errors.append("Coverage structural-complete count differs from current roster-view index")
    if global_cov.get("wave_b_structural_roster_identities_unavailable") != counts.get("unavailable"):
        errors.append("Coverage structural-unavailable count differs from current roster-view index")
    if global_cov.get("current_normalized_factions") != 0:
        errors.append("Full normative current_normalized_factions must remain 0 until normative/app equivalence is established")

    structural_rows = [x for x in cov.get("factions", []) if x.get("structural_current")]
    if len(structural_rows) != counts.get("structural_complete"):
        errors.append(
            f"structural_current rows ({len(structural_rows)}) differ from current mirror complete count "
            f"({counts.get('structural_complete')})"
        )
    structural_dims = set(cov.get("structural_dimensions", []))
    for row in structural_rows:
        dims = row.get("wave_b_structural", {}).get("dimensions", {})
        if row.get("wave_b_structural", {}).get("state") != "COMPLETE":
            errors.append(f"Wave B structural state not COMPLETE: {row.get('slug')}")
        for dim in structural_dims:
            if dims.get(dim) != 100:
                errors.append(f"Incomplete Wave B structural dimension {row.get('slug')}.{dim}")

    if current_rules.get("status") != "CURRENT_OPERATIONAL_RULES_LAYER_READY_NORMATIVE_APP_PENDING":
        errors.append("rules/11e/current.json operational-currentness status drifted")
    if wb_current.get("roster_identities_complete") != counts.get("structural_complete"):
        errors.append("rules/11e/current.json Wave B complete count differs from current index")
    if set(wb_current.get("roster_identities_unavailable", [])) != unavailable:
        errors.append("rules/11e/current.json unavailable identities differ from current index")
    if wb_current.get("semantic_rule_text") != "CURRENT_SECONDARY_MIRROR_FULL_HASH_VERIFIED":
        errors.append("Wave B semantic mirror promotion drifted")
    if wb_current.get("faq_errata") != "SOURCE_CATALOG_CURRENT_OFFICIAL_ASSETS_VERIFIED":
        errors.append("Wave B FAQ/errata source promotion drifted")
    if wb_current.get("normative_semantic_equivalence") != "NOT_CLAIMED":
        errors.append("Wave B must not claim normative semantic equivalence")

    waha_registry = by_source_id.get("WAHAPEDIA_11E", {})
    if waha_registry.get("repository_coverage_state") != "STRUCTURAL_INGESTED":
        errors.append("WAHAPEDIA_11E repository coverage state must be STRUCTURAL_INGESTED")
    if waha_registry.get("observed_revision", {}).get("last_update") != waha_manifest.get("source", {}).get("last_update"):
        errors.append("WAHAPEDIA_11E registry revision differs from ingested manifest")
    if (ROOT / waha_registry.get("observed_revision", {}).get("manifest", "")).resolve() != (waha_root / "manifest.json").resolve():
        errors.append("WAHAPEDIA_11E registry manifest pointer differs from current snapshot")
except Exception as exc:
    errors.append(f"Wave B structural validation failure: {exc}")

# 3g. BSData fallback and semantic resolver contracts.
try:
    current_rules = json.loads((ROOT / "rules" / "11e" / "current.json").read_text(encoding="utf-8"))
    wb_current = current_rules.get("wave_b_structural", {})
    fallback_path = ROOT / wb_current["implementation_fallback_snapshot"]
    fallback = json.loads(fallback_path.read_text(encoding="utf-8"))
    registry_now = json.loads((ROOT / "sources" / "registry.json").read_text(encoding="utf-8"))
    registry_by_id = {x.get("id"): x for x in registry_now.get("sources", [])}
    bs_registry = registry_by_id.get("BSDATA_WH40K_11E", {})

    if fallback.get("commit_sha") != bs_registry.get("observed_revision", {}).get("commit_sha"):
        errors.append("BSData fallback revision differs from current registry revision")
    fallback_views = {x.get("slug"): x for x in fallback.get("views", [])}
    if set(fallback_views) != {"titanicus_traitoris", "unaligned_forces"}:
        errors.append("BSData fallback roster identity set drifted")
    if fallback.get("commit_sha") == "951d5900d1b4a952a4ba560a30c43788e622ccfc":
        if fallback_views.get("titanicus_traitoris", {}).get("counts", {}).get("units") != 4:
            errors.append("Bootstrap Titanicus Traitoris fallback must contain 4 units")
        if fallback_views.get("unaligned_forces", {}).get("counts", {}).get("units") != 22:
            errors.append("Bootstrap Unaligned Forces fallback must contain 22 implementation units")
    else:
        if any(int(x.get("counts", {}).get("units", 0)) <= 0 for x in fallback_views.values()):
            errors.append("Promoted BSData fallback contains an empty roster view")

    cov = json.loads((ROOT / "coverage" / "current.json").read_text(encoding="utf-8"))
    gcov = cov.get("global", {})
    current_mirror_complete = int(gcov.get("wave_b_current_mirror_structural_complete", 0))
    fallback_complete = int(gcov.get("wave_b_structured_implementation_fallback_complete", 0))
    if fallback_complete != len(fallback_views):
        errors.append("Wave B implementation fallback count differs from current fallback index")
    if gcov.get("wave_b_total_structural_source_available") != 37:
        errors.append("Wave B total structural source availability must remain 37")
    rows = {x.get("slug"): x for x in cov.get("factions", [])}
    if sum(bool(x.get("structural_source_available")) for x in rows.values()) != 37:
        errors.append("All 37 roster identities must have a structural source available")
    for slug in fallback_views:
        row = rows.get(slug, {})
        if row.get("structural_current") is True:
            continue
        wb = row.get("wave_b_structural", {})
        if wb.get("state") != "IMPLEMENTATION_FALLBACK_COMPLETE":
            errors.append(f"{slug} fallback state drifted")
        if wb.get("source_role") != "structured_implementation":
            errors.append(f"{slug} fallback source role must remain structured_implementation")
        if wb.get("normative_rules_verified") is not False:
            errors.append(f"{slug} fallback must not claim normative rules verification")
        if wb.get("pinned_commit") != fallback.get("commit_sha"):
            errors.append(f"{slug} fallback pointer revision differs from fallback index")

    if wb_current.get("total_structural_source_available") != 37:
        errors.append("rules/11e/current.json structural source availability drifted")
    if wb_current.get("implementation_fallback_roster_identities_complete") != len(fallback_views):
        errors.append("rules/11e/current.json fallback count differs from fallback index")

    semantic_tool = ROOT / "tools" / "query_current_semantics.py"
    semantic_workflow = ROOT / ".github" / "workflows" / "semantic-smoke.yml"
    if not semantic_tool.exists():
        errors.append("Missing hash-verified semantic resolver")
    if not semantic_workflow.exists():
        errors.append("Missing semantic resolver smoke workflow")
except Exception as exc:
    errors.append(f"BSData fallback / semantic resolver validation failure: {exc}")

# 3g2. Wave B semantic and official-asset currentness.
try:
    current_rules = json.loads((ROOT / "rules" / "11e" / "current.json").read_text(encoding="utf-8"))
    cov = json.loads((ROOT / "coverage" / "current.json").read_text(encoding="utf-8"))

    sem_ptr = current_rules.get("semantic_resolver", {}).get("full_audit", {}).get("report")
    semantic_audit = json.loads((ROOT / sem_ptr).read_text(encoding="utf-8"))
    off_ptr = current_rules.get("source_currentness", {}).get("faq_errata_assets", {}).get("report")
    official_assets = json.loads((ROOT / off_ptr).read_text(encoding="utf-8"))

    if semantic_audit.get("status") != "PASS":
        errors.append("Wave B full semantic fingerprint audit is not PASS")
    expected = int(semantic_audit.get("expected_fingerprints", 0))
    matched = int(semantic_audit.get("counts", {}).get("MATCH", 0))
    if expected <= 0 or matched != expected:
        errors.append(f"Wave B semantic fingerprint matches are incomplete: {matched}/{expected}")
    if semantic_audit.get("problems"):
        errors.append("Wave B semantic audit contains unresolved problems")

    if official_assets.get("status") != "PASS":
        errors.append("Official 11E asset audit is not PASS")
    if official_assets.get("live_source_csv", {}).get("catalog_drift_count") != 0:
        errors.append("Live Source.csv differs from committed current 11E source catalog")
    off = official_assets.get("official_assets", {})
    if off.get("failures") != 0:
        errors.append("Official faction-pack PDF asset verification contains failures")
    if off.get("verified_pdf_assets") != off.get("pdf_assets"):
        errors.append("Not all referenced official faction-pack PDFs are verified")

    gcov = cov.get("global", {})
    complete = int(current_rules.get("wave_b_structural", {}).get("roster_identities_complete", 0))
    if gcov.get("wave_b_current_mirror_semantic_roster_identities") != complete:
        errors.append("Current-mirror semantic roster identity count differs from structural current mirror")
    if gcov.get("wave_b_semantic_fingerprints_expected") != expected:
        errors.append("Coverage semantic expected-fingerprint count differs from current audit")
    if gcov.get("wave_b_semantic_fingerprints_matched") != matched:
        errors.append("Coverage semantic matched-fingerprint count differs from current audit")
    if gcov.get("wave_b_official_edition11_sources") != off.get("edition_11_sources"):
        errors.append("Coverage official edition-11 source count differs from current asset audit")
    if gcov.get("wave_b_official_pdf_assets_verified") != off.get("verified_pdf_assets"):
        errors.append("Coverage official PDF verification count differs from current asset audit")
    if gcov.get("current_normalized_factions") != 0:
        errors.append("Full normative faction normalization must remain 0 until normative/app equivalence is established")
    if current_rules.get("wave_b_structural", {}).get("semantic_rule_text") != "CURRENT_SECONDARY_MIRROR_FULL_HASH_VERIFIED":
        errors.append("Current rules semantic mirror status drifted")
    if current_rules.get("wave_b_structural", {}).get("faq_errata") != "SOURCE_CATALOG_CURRENT_OFFICIAL_ASSETS_VERIFIED":
        errors.append("Current rules FAQ/errata asset status drifted")
except Exception as exc:
    errors.append(f"Wave B semantic/asset validation failure: {exc}")

# 3h. Automated upstream/runtime monitoring contracts.
try:
    upstream_watch = json.loads((ROOT / "reports" / "UPSTREAM_CHANGE_WATCH_CURRENT.json").read_text(encoding="utf-8"))
    nr_runtime = json.loads((ROOT / "reports" / "NEW_RECRUIT_RUNTIME_VALIDATION_CURRENT.json").read_text(encoding="utf-8"))
    runtime_drifts = json.loads((ROOT / "sources" / "runtime_drift_registry.json").read_text(encoding="utf-8"))
    current_rules = json.loads((ROOT / "rules" / "11e" / "current.json").read_text(encoding="utf-8"))

    if upstream_watch.get("status") != "NO_CHANGE":
        errors.append("Pinned upstream baseline currently has unresolved change")
    summary = upstream_watch.get("change_summary", {})
    if summary.get("github_sources_changed") != []:
        errors.append("Pinned GitHub upstream source head changed")
    if summary.get("wahapedia_files_changed") != 0 or summary.get("wahapedia_last_update_changed") is not False:
        errors.append("Wahapedia baseline changed without re-ingestion")

    if nr_runtime.get("schema_version") != "2.0":
        errors.append("New Recruit runtime report schema must be 2.0")
    if nr_runtime.get("status") not in {"PASS", "PASS_WITH_KNOWN_RUNTIME_DRIFT"}:
        errors.append(f"New Recruit runtime has unresolved drift: {nr_runtime.get('status')}")
    universe = nr_runtime.get("universe", {})
    if universe.get("resolved_runtime_identities") != 37 or universe.get("missing"):
        errors.append("New Recruit runtime universe must resolve all 37 identities")
    if any(x.get("status") != "PASS" for x in universe.get("page_checks", [])):
        errors.append("New Recruit runtime page check failed")
    if nr_runtime.get("lineage", {}).get("exact_sync_cadence") != "UNKNOWN_NOT_INFERRED":
        errors.append("New Recruit synchronization cadence must remain UNKNOWN_NOT_INFERRED")

    points = nr_runtime.get("representative_points", {})
    surfaces = nr_runtime.get("representative_surfaces", {})
    if points.get("checks") != 15:
        errors.append("New Recruit representative point sample size drifted")
    if surfaces.get("checks") != 5:
        errors.append("New Recruit representative surface sample size drifted")
    if points.get("new_drift_count") != 0 or surfaces.get("new_drift_count") != 0:
        errors.append("New Recruit contains unclassified point/surface runtime drift")

    known_points = points.get("known_drifts", [])
    known_surfaces = surfaces.get("known_drifts", [])
    allowed_classifications = {
        "NORMATIVE_MATCH",
        "IMPLEMENTATION_DRIFT",
        "RUNTIME_PROJECTION_DRIFT",
        "UPSTREAM_REVISION_DRIFT",
        "UNKNOWN_RUNTIME_DRIFT",
    }
    for row in known_points + known_surfaces:
        if row.get("classification") not in allowed_classifications:
            errors.append(f"Invalid runtime drift classification: {row.get('classification')}")
        if row.get("normative_kb_change_required") is not False:
            errors.append("Runtime drift must never require automatic normative KB change")

    active = [x for x in runtime_drifts.get("active", []) if x.get("state") == "ACTIVE"]
    if any(x.get("classification") not in allowed_classifications - {"NORMATIVE_MATCH"} for x in active):
        errors.append("Runtime drift registry contains an invalid active classification")
    if any(x.get("normative_kb_change_required") is not False for x in active):
        errors.append("Runtime drift registry must never request automatic normative KB change")

    automation = current_rules.get("automation", {})
    nr_auto = automation.get("new_recruit_runtime", {})
    if automation.get("upstream_change_watch", {}).get("state") != "ACTIVE_NO_CHANGE":
        errors.append("Current rules upstream watcher status must be ACTIVE_NO_CHANGE after promotion/rebaseline")
    if nr_auto.get("state") != nr_runtime.get("status"):
        errors.append("Current rules New Recruit runtime state differs from runtime report")
    if nr_auto.get("representative_point_checks") != points.get("checks"):
        errors.append("Current rules point-sample count differs from runtime report")
    if nr_auto.get("representative_point_matches") != points.get("matched"):
        errors.append("Current rules point-match count differs from runtime report")
    known_total = int(points.get("known_drift_count", 0)) + int(surfaces.get("known_drift_count", 0))
    if nr_auto.get("known_runtime_drifts") != known_total:
        errors.append("Current rules known runtime drift count differs from runtime report")
    new_total = int(points.get("new_drift_count", 0)) + int(surfaces.get("new_drift_count", 0))
    if nr_auto.get("new_runtime_drifts") != new_total:
        errors.append("Current rules new runtime drift count differs from runtime report")
    if nr_auto.get("exact_sync_cadence") != "UNKNOWN_NOT_INFERRED":
        errors.append("Current rules invented a New Recruit synchronization cadence")
    if current_rules.get("next_milestone") != "CORE_RULE_SEMANTIC_AST_READINESS_V1":
        errors.append("Current milestone must advance to CORE_RULE_PARAGRAPH_SEMANTIC_CLASSIFICATION_V1")
    readiness_layer = current_rules.get("release_transition_readiness", {})
    if readiness_layer.get("state") != "OPERATIONAL_V1":
        errors.append("Current rules must record release transition readiness v1 as operational")
    if readiness_layer.get("policy", {}).get("auto_promote") is not False:
        errors.append("Current release transition layer must keep auto_promote=false")
    tracked = {x.get("id"): x for x in readiness_layer.get("tracked_transitions", [])}
    if tracked.get("SPACE_MARINES_CODEX_2026", {}).get("state") != "PRE_RELEASE_HOLD":
        errors.append("Current Space Marines transition state drifted")
    if tracked.get("ADEPTUS_CUSTODES_CODEX_2026", {}).get("state") != "UPCOMING_HOLD_NO_RELEASE_DATE":
        errors.append("Current Custodes transition state drifted")
    activation_layer = current_rules.get("release_transition_activation_watch", {})
    if activation_layer.get("state") != "OPERATIONAL_V1":
        errors.append("Current rules must record release activation watch v1 as operational")
    if activation_layer.get("checkpoint_status") != "NO_ACTION_REQUIRED":
        errors.append("Current release activation checkpoint status drifted")
    if activation_layer.get("safety", {}).get("auto_promote") is not False:
        errors.append("Current release activation watch must keep auto_promote=false")
    if activation_layer.get("safety", {}).get("direct_current_rules_mutation") is not False:
        errors.append("Current release activation watch must remain read-only")
    gap_layer = current_rules.get("normative_equivalence_gap_audit", {})
    if gap_layer.get("state") != "PASS_GAPS_CLASSIFIED":
        errors.append("Current rules must record normative equivalence gap audit as PASS_GAPS_CLASSIFIED")
    if gap_layer.get("current_normalized_factions") != 0:
        errors.append("Normative gap audit layer must preserve current_normalized_factions=0")
    if gap_layer.get("public_core_rules_source_discovered") is not True:
        errors.append("Normative gap audit layer lost public Core Rules discovery")
    if gap_layer.get("verified_public_faction_pack_pdfs") != 28:
        errors.append("Normative gap audit layer official faction-pack verification count drifted")
    if gap_layer.get("public_faction_pack_scope") != "SUPPLEMENTAL_NOT_FULL_CODEX":
        errors.append("Normative gap audit layer faction-pack scope drifted")
    if gap_layer.get("gw_app_wording") != "BLOCKED_ON_AUTHORIZED_APP_EVIDENCE":
        errors.append("Normative gap audit layer GW App blocker drifted")
except Exception as exc:
    errors.append(f"Automated upstream/runtime monitoring validation failure: {exc}")

# 3i. Collection-aware Custodes roster solver contracts.
try:
    solver_report = json.loads((ROOT / "reports" / "COLLECTION_AWARE_ROSTER_SOLVER_CURRENT.json").read_text(encoding="utf-8"))
    solver_profile = json.loads((ROOT / "collection" / "adeptus_custodes" / "solver_profile.json").read_text(encoding="utf-8"))
    current_collection = json.loads((ROOT / "collection" / "adeptus_custodes" / "current.json").read_text(encoding="utf-8"))

    if solver_report.get("status") != "PASS":
        errors.append("Collection-aware roster solver validation report must PASS")
    if solver_report.get("milestone") != "COLLECTION_AWARE_ROSTER_SOLVER":
        errors.append("Collection-aware roster solver milestone id drifted")
    if len(solver_report.get("cases", [])) != 7:
        errors.append("Collection-aware roster solver smoke matrix must contain seven cases")

    boundary = solver_report.get("authority_boundary", {})
    if boundary.get("full_normative_legality") != "UNKNOWN_PENDING_NORMATIVE_APP":
        errors.append("Collection solver must not claim full normative legality")
    if boundary.get("collection_status") != "PROVISIONAL":
        errors.append("Custodes collection solver must preserve PROVISIONAL inventory status")
    if boundary.get("normative_promotion") is not False:
        errors.append("Collection solver must never promote physical/runtime evidence into normative rules")

    pools = solver_profile.get("body_pools", [])
    if len(pools) != 15 or sum(int(x.get("physical_bodies", 0)) for x in pools) != 70:
        errors.append("Custodes solver profile must model exactly 70 Custodes/Sisters bodies across 15 pools")
    if len(solver_profile.get("component_pools", [])) != 12:
        errors.append("Custodes solver component pool coverage drifted")
    if not any(
        role.get("mode") == "CONVERSION_REQUIRED"
        for pool in pools
        for role in pool.get("roles", [])
    ):
        errors.append("Custodes solver lost conversion-required role modeling")
    if not any(
        x.get("id") == "CUSTODES_VENATARI_GUARD_SPEAR_SHARING"
        for x in solver_profile.get("unknown_constraints", [])
    ):
        errors.append("Custodes solver lost fail-closed Venatari shared-spear constraint")

    solver_ptr = current_collection.get("solver", {})
    if solver_ptr.get("state") != "OPERATIONAL_PROVISIONAL":
        errors.append("Custodes current collection solver state must remain OPERATIONAL_PROVISIONAL")
    rules_solver = current_rules.get("collection_aware_roster_solver", {})
    if rules_solver.get("state") != "OPERATIONAL_V1_CUSTODES":
        errors.append("Current rules must record collection solver v1 as operational")
    if rules_solver.get("full_normative_legality") != "UNKNOWN_PENDING_NORMATIVE_APP":
        errors.append("Collection solver must preserve the normative/app legality boundary")
    for required in [
        ROOT / "tools" / "solve_collection_roster.py",
        ROOT / "tools" / "validate_collection_solver.py",
        ROOT / ".github" / "workflows" / "collection-roster-solver.yml",
        ROOT / "schemas" / "collection_solver_profile.schema.json",
        ROOT / "schemas" / "roster_request.schema.json",
        ROOT / "schemas" / "roster_solver_result.schema.json",
    ]:
        if not required.exists():
            errors.append(f"Missing collection solver artifact: {required.relative_to(ROOT)}")
except Exception as exc:
    errors.append(f"Collection-aware roster solver validation failure: {exc}")

# 3j. Official public ↔ current-mirror exact overlap contracts.
try:
    overlap = json.loads(
        (ROOT / "reports" / "OFFICIAL_PUBLIC_MIRROR_OVERLAP_CURRENT.json").read_text(encoding="utf-8")
    )
    overlap_summary = json.loads(
        (ROOT / "reports" / "OFFICIAL_PUBLIC_MIRROR_OVERLAP_SUMMARY_CURRENT.json").read_text(encoding="utf-8")
    )
    overlap_snapshot = json.loads(
        (ROOT / "rules" / "11e" / "snapshots" / "2026-09-30" / "official_public_overlap" / "index.json").read_text(encoding="utf-8")
    )
    overlap_current = json.loads((ROOT / "rules" / "11e" / "current.json").read_text(encoding="utf-8"))
    overlap_gate = json.loads((ROOT / "sources" / "currentness_gate.json").read_text(encoding="utf-8"))
    overlap_cov = json.loads((ROOT / "coverage" / "current.json").read_text(encoding="utf-8"))

    if overlap.get("status") != "PASS" or overlap_summary.get("status") != "PASS":
        errors.append("Official-public mirror overlap audit and compact summary must PASS")
    if overlap.get("milestone") != "OFFICIAL_PUBLIC_RULES_MIRROR_OVERLAP_AUDIT":
        errors.append("Official-public mirror overlap milestone id drifted")
    if overlap.get("as_of") != "2026-09-30":
        errors.append("Official-public mirror overlap checkpoint must remain 2026-09-30")

    expected_overlap = {
        "official_documents": 29,
        "core_rules": 1,
        "faction_packs": 28,
        "mirror_units": 13572,
        "exact_public_overlap_units": 5636,
        "promotable_scoped_units": 4070,
        "unscoped_exact_units": 1566,
        "no_exact_overlap_units": 7936,
        "official_pages": 1430,
        "official_pages_with_overlap": 1268,
    }
    osum = overlap.get("summary", {})
    ssum = overlap_summary.get("summary", {})
    for key, value in expected_overlap.items():
        if osum.get(key) != value:
            errors.append(f"Official-public overlap summary {key} drifted: {osum.get(key)} != {value}")
        if ssum.get(key) != value:
            errors.append(f"Compact official-public overlap summary {key} drifted: {ssum.get(key)} != {value}")

    expected_classifications = {
        "EXACT_NORMALIZED_TEXT_MATCH": 4145,
        "EXACT_NORMALIZED_TEXT_MATCH_MULTI_OFFICIAL": 1491,
    }
    if osum.get("classification_counts") != expected_classifications:
        errors.append("Official-public overlap classification counts drifted")
    expected_provenance = {
        "CORE_PUBLIC_TEXT_ONLY": 21,
        "DIRECT_FACTION_SCOPED": 2747,
        "DIRECT_SOURCE_SCOPED": 1323,
        "GLOBAL_PUBLIC_TEXT_ONLY": 1545,
    }
    if osum.get("provenance_scope_counts") != expected_provenance:
        errors.append("Official-public overlap provenance-scope counts drifted")

    boundary = overlap.get("authority_boundary", {})
    if boundary.get("normative_authority") != "GAMES_WORKSHOP":
        errors.append("Official-public overlap lost Games Workshop normative authority")
    if boundary.get("current_mirror") != "WAHAPEDIA_11E":
        errors.append("Official-public overlap current mirror must remain Wahapedia 11E")
    if boundary.get("full_codex_app_equivalence_claimed") is not False:
        errors.append("Official-public overlap must not claim full Codex/app equivalence")
    if boundary.get("faction_pack_is_full_codex_replacement") is not False:
        errors.append("Official-public overlap must not treat Faction Packs as full Codex replacements")
    if boundary.get("app_only_wording_inferred") is not False:
        errors.append("Official-public overlap must not infer app-only wording")
    if boundary.get("current_normalized_factions_promoted_by_this_audit") is not False:
        errors.append("Official-public overlap must not promote whole factions")

    if overlap_snapshot.get("status") != "PASS":
        errors.append("Structured official-public overlap snapshot must PASS")
    if overlap_snapshot.get("authority") != "GAMES_WORKSHOP_OFFICIAL_PUBLIC_OVERLAP":
        errors.append("Structured official-public overlap snapshot authority drifted")
    if overlap_snapshot.get("scope") != "EXACT_PUBLIC_OVERLAP_ONLY":
        errors.append("Structured official-public overlap snapshot scope drifted")
    if overlap_snapshot.get("summary", {}).get("units") != 4070:
        errors.append("Structured official-public overlap snapshot must contain 4070 units")
    snap_boundary = overlap_snapshot.get("authority_boundary", {})
    if snap_boundary.get("full_faction_current_verified") is not False:
        errors.append("Structured overlap snapshot must not verify a whole faction")
    if snap_boundary.get("current_normalized_factions_change") != 0:
        errors.append("Structured overlap snapshot must keep current_normalized_factions change at zero")
    if snap_boundary.get("full_codex_app_equivalence") != "NOT_CLAIMED":
        errors.append("Structured overlap snapshot must preserve Codex/app equivalence boundary")

    layer = overlap_current.get("official_public_mirror_overlap", {})
    if layer.get("state") != "PASS_EXACT_PUBLIC_OVERLAP_V1":
        errors.append("Current rules official-public overlap layer state drifted")
    if layer.get("snapshot") != "rules/11e/snapshots/2026-09-30/official_public_overlap/index.json":
        errors.append("Current rules official-public overlap snapshot pointer drifted")
    if layer.get("promotable_scoped_units") != 4070:
        errors.append("Current rules official-public overlap promoted unit count drifted")
    if layer.get("current_normalized_factions_change") != 0:
        errors.append("Current rules overlap layer must not change full-faction coverage")
    if overlap_current.get("next_milestone") != "CORE_RULE_SEMANTIC_AST_READINESS_V1":
        errors.append("Current rules next milestone did not advance after structured normalization expansion")

    profile = overlap_gate.get("scope_profiles", {}).get("official_public_mirror_overlap", {})
    if profile.get("content_state") != "PASS_EXACT_PUBLIC_OVERLAP_V1":
        errors.append("Currentness gate official-public overlap profile must PASS")
    if profile.get("promotable_scoped_units") != 4070:
        errors.append("Currentness gate official-public overlap unit count drifted")

    gcov = overlap_cov.get("global", {})
    if overlap_cov.get("status") != "CORE_RULE_PARAGRAPH_SEMANTIC_REVIEW_V1_COMPLETE":
        errors.append("Coverage status did not advance through structured normalization expansion v1")
    if gcov.get("official_public_overlap_promotable_scoped_units") != 4070:
        errors.append("Coverage official-public overlap promoted count drifted")
    if gcov.get("current_normalized_factions") != 0:
        errors.append("Official-public overlap must preserve current_normalized_factions=0")
    if gcov.get("full_normative_semantic_factions") != 0:
        errors.append("Official-public overlap must preserve full_normative_semantic_factions=0")
    if gcov.get("official_public_overlap_current_normalized_factions_change") != 0:
        errors.append("Coverage overlap delta must remain zero for full factions")

    forbidden_long_text_keys = {"text", "description", "rules_text", "official_text", "mirror_text"}
    def _check_overlap_no_long_text(value, path="root"):
        if isinstance(value, dict):
            for key, child in value.items():
                if key in forbidden_long_text_keys:
                    errors.append(f"Official-public overlap vendored forbidden long-text field: {path}.{key}")
                    continue
                _check_overlap_no_long_text(child, f"{path}.{key}")
        elif isinstance(value, list):
            for idx, child in enumerate(value):
                _check_overlap_no_long_text(child, f"{path}[{idx}]")
    _check_overlap_no_long_text(overlap)
    _check_overlap_no_long_text(overlap_snapshot)

    required_overlap_files = [
        ROOT / "docs" / "OFFICIAL_PUBLIC_MIRROR_OVERLAP_MODEL.md",
        ROOT / "schemas" / "official_public_mirror_overlap.schema.json",
        ROOT / "schemas" / "official_public_overlap_snapshot.schema.json",
        ROOT / "tools" / "audit_official_public_mirror_overlap.py",
        ROOT / "tests" / "test_official_public_mirror_overlap.py",
        ROOT / ".github" / "workflows" / "official-public-mirror-overlap.yml",
        ROOT / "reports" / "OFFICIAL_PUBLIC_MIRROR_OVERLAP_CLOSURE_2026-09-30.md",
    ]
    for path in required_overlap_files:
        if not path.exists():
            errors.append(f"Missing official-public overlap artifact: {path.relative_to(ROOT)}")
except Exception as exc:
    errors.append(f"Official-public mirror overlap validation failure: {exc}")

# 3j2. Core Rules numbered reference atomization contracts.
try:
    atom_report = json.loads(
        (ROOT / "reports" / "CORE_RULE_REFERENCE_ATOMIZATION_CURRENT.json").read_text(encoding="utf-8")
    )
    atom_snapshot = json.loads(
        (ROOT / "rules" / "11e" / "snapshots" / "2026-09-30" / "core_rule_atoms" / "index.json").read_text(encoding="utf-8")
    )
    atom_current = json.loads((ROOT / "rules" / "11e" / "current.json").read_text(encoding="utf-8"))
    atom_gate = json.loads((ROOT / "sources" / "currentness_gate.json").read_text(encoding="utf-8"))
    atom_cov = json.loads((ROOT / "coverage" / "current.json").read_text(encoding="utf-8"))

    if atom_report.get("status") != "PASS" or atom_snapshot.get("status") != "PASS":
        errors.append("Core rule-reference atomization evidence must PASS")
    if atom_report.get("authority") != "GAMES_WORKSHOP_OFFICIAL":
        errors.append("Core rule-reference atomization lost Games Workshop authority")
    if atom_report.get("atomization_version") != "CORE_RULE_REFERENCE_ATOMIZATION_V1":
        errors.append("Core rule-reference atomization version drifted")

    atom_summary = atom_report.get("summary", {})
    expected_atom_classes = {
        "REPEATED_IN_FAMILY_HEADING": 5,
        "UNIQUE_IN_FAMILY_HEADING": 136,
    }
    if atom_summary.get("atoms") != 141:
        errors.append("Core rule-reference atom count must remain 141")
    if atom_summary.get("unique_rule_refs") != 141 or atom_summary.get("unique_rule_keys") != 141:
        errors.append("Core rule-reference stable identities must remain 141/141 unique")
    if atom_summary.get("families") != 24:
        errors.append("Core rule-reference atom family count drifted")
    if atom_summary.get("family_ids") != [f"{i:02d}" for i in range(1,25)]:
        errors.append("Core rule-reference atom families must remain canonical 01-24")
    if atom_summary.get("classification_counts") != expected_atom_classes:
        errors.append("Core rule-reference atom classification counts drifted")
    if atom_summary.get("heading_recovery_gaps") != 0 or atom_summary.get("heading_recovery_gap_refs") != []:
        errors.append("Core rule-reference atomization contains heading recovery gaps")
    if atom_summary.get("atoms_with_cross_references") != 40:
        errors.append("Core rule-reference cross-reference atom count drifted")
    if atom_summary.get("all_atoms_have_in_family_heading") is not True:
        errors.append("Every Core rule atom must have in-family heading evidence")

    if atom_snapshot.get("summary") != atom_summary:
        errors.append("Core rule atom report summary differs from full snapshot")
    atoms = atom_snapshot.get("atoms", [])
    if len(atoms) != 141:
        errors.append("Core rule atom snapshot must contain exactly 141 atoms")
    if len({x.get("rule_ref") for x in atoms}) != 141:
        errors.append("Core rule atom rule_ref identities are not unique")
    if len({x.get("rule_key") for x in atoms}) != 141:
        errors.append("Core rule atom rule_key identities are not unique")
    if any(len(x.get("heading_labels", [])) == 0 for x in atoms):
        errors.append("Core rule atom missing heading labels")
    if any(
        len(label.get("label", "")) > 160
        for atom in atoms
        for label in atom.get("heading_labels", [])
    ):
        errors.append("Core rule atom heading label exceeded 160 characters")
    repeated_refs = {
        x.get("rule_ref")
        for x in atoms
        if x.get("classification") == "REPEATED_IN_FAMILY_HEADING"
    }
    if repeated_refs != {"15.07","15.08","15.09","15.10","15.11"}:
        errors.append(f"Repeated Core rule-reference set drifted: {sorted(repeated_refs)}")

    source_verification = atom_report.get("source_verification", {})
    if source_verification.get("binary_sha256_match") is not True:
        errors.append("Core rule atom source binary verification failed")
    if source_verification.get("page_semantic_fingerprints_match") != 88:
        errors.append("Core rule atom source page fingerprint count drifted")
    if source_verification.get("document_semantic_sha256_match") is not True:
        errors.append("Core rule atom source document semantic verification failed")

    atom_boundary = atom_report.get("authority_boundary", {})
    if atom_boundary.get("numbered_reference_identity_complete") is not True:
        errors.append("Core rule numbered-reference identity must be complete")
    if atom_boundary.get("definition_evidence_heading_only") is not True:
        errors.append("Core rule definition evidence must remain heading-only at atomization v1")
    if atom_boundary.get("paragraph_level_rules_ast_complete") is not False:
        errors.append("Core rule atomization must not claim paragraph AST completeness")
    if atom_boundary.get("rule_interaction_graph_complete") is not False:
        errors.append("Core rule atomization must not claim interaction graph completeness")
    if atom_boundary.get("full_faction_promotion") is not False:
        errors.append("Core rule atomization must not promote full factions")
    if atom_boundary.get("current_normalized_factions_change") != 0:
        errors.append("Core rule atomization must not change normalized faction count")

    current_layer = atom_current.get("core_rule_reference_atomization", {})
    if current_layer.get("state") != "PASS_141_RULE_ATOMS":
        errors.append("Current rules Core atomization state drifted")
    if current_layer.get("atoms") != 141 or current_layer.get("heading_recovery_gaps") != 0:
        errors.append("Current rules Core atomization counts drifted")
    if atom_current.get("next_milestone") != "CORE_RULE_SEMANTIC_AST_READINESS_V1":
        errors.append("Current rules did not advance to Core paragraph-boundary extraction")
    current_core = atom_current.get("source_currentness", {}).get("core_rules_content", {})
    if current_core.get("state") != "OFFICIAL_PUBLIC_PARAGRAPH_SEMANTIC_REVIEW_V1":
        errors.append("Core Rules currentness did not advance to reference atomization v1")
    if current_core.get("normative_structured_normalization") != "PARAGRAPH_SEMANTIC_REVIEW_COMPLETE_AST_READINESS_PENDING":
        errors.append("Core Rules structured normalization boundary did not advance after atomization")

    atom_profile = atom_gate.get("scope_profiles", {}).get("core_rule_reference_atoms", {})
    if atom_profile.get("content_state") != "PASS_141_RULE_ATOMS":
        errors.append("Currentness gate Core atomization profile must PASS")
    if atom_profile.get("atoms") != 141 or atom_profile.get("heading_recovery_gaps") != 0:
        errors.append("Currentness gate Core atomization metrics drifted")

    atom_global = atom_cov.get("global", {})
    if atom_cov.get("status") != "CORE_RULE_PARAGRAPH_SEMANTIC_REVIEW_V1_COMPLETE":
        errors.append("Coverage status did not advance after Core rule atomization")
    if atom_global.get("official_public_core_rule_atoms") != 141:
        errors.append("Coverage Core rule atom count drifted")
    if atom_global.get("official_public_core_rule_atoms_unique_heading") != 136:
        errors.append("Coverage unique-heading Core atom count drifted")
    if atom_global.get("official_public_core_rule_atoms_repeated_heading") != 5:
        errors.append("Coverage repeated-heading Core atom count drifted")
    if atom_global.get("official_public_core_rule_atom_heading_recovery_gaps") != 0:
        errors.append("Coverage Core atom heading recovery gaps must remain zero")
    if atom_global.get("official_public_core_rule_atoms_with_cross_references") != 40:
        errors.append("Coverage Core atom cross-reference count drifted")
    if atom_global.get("official_public_core_rule_paragraph_boundaries_complete") is not False:
        errors.append("Coverage must preserve Core paragraph boundaries as pending")
    if atom_global.get("official_public_core_rule_paragraph_ast_complete") is not False:
        errors.append("Coverage must preserve Core paragraph AST as pending")
    if atom_global.get("current_normalized_factions") != 0:
        errors.append("Core rule atomization must preserve current_normalized_factions=0")
    if atom_global.get("full_normative_semantic_factions") != 0:
        errors.append("Core rule atomization must preserve full_normative_semantic_factions=0")

    forbidden_atom_text_keys = {"text","description","rules_text","official_text","mirror_text","page_text","prose","paragraph"}
    def _check_atom_no_long_text(value, path="root"):
        if isinstance(value, dict):
            for key, child in value.items():
                if key in forbidden_atom_text_keys:
                    errors.append(f"Core rule atomization vendored forbidden long-text field: {path}.{key}")
                    continue
                _check_atom_no_long_text(child, f"{path}.{key}")
        elif isinstance(value, list):
            for idx, child in enumerate(value):
                _check_atom_no_long_text(child, f"{path}[{idx}]")
    _check_atom_no_long_text(atom_snapshot)

    for required in [
        ROOT / "docs" / "CORE_RULE_REFERENCE_ATOMIZATION_MODEL.md",
        ROOT / "schemas" / "core_rule_reference_index.schema.json",
        ROOT / "tools" / "build_core_rule_reference_atoms.py",
        ROOT / "tests" / "test_core_rule_reference_atomization.py",
        ROOT / ".github" / "workflows" / "core-rule-reference-atomization.yml",
    ]:
        if not required.exists():
            errors.append(f"Missing Core rule atomization artifact: {required.relative_to(ROOT)}")
except Exception as exc:
    errors.append(f"Core rule-reference atomization validation failure: {exc}")

# 3j3. Core Rules paragraph/rule-body boundary extraction contracts.
try:
    boundary_report = json.loads(
        (ROOT / "reports" / "CORE_RULE_PARAGRAPH_BOUNDARIES_CURRENT.json").read_text(encoding="utf-8")
    )
    boundary_snapshot = json.loads(
        (ROOT / "rules" / "11e" / "snapshots" / "2026-09-30" / "core_rule_boundaries" / "index.json").read_text(encoding="utf-8")
    )
    boundary_current = json.loads((ROOT / "rules" / "11e" / "current.json").read_text(encoding="utf-8"))
    boundary_gate = json.loads((ROOT / "sources" / "currentness_gate.json").read_text(encoding="utf-8"))
    boundary_cov = json.loads((ROOT / "coverage" / "current.json").read_text(encoding="utf-8"))

    if boundary_report.get("status") != "PASS" or boundary_snapshot.get("status") != "PASS":
        errors.append("Core rule paragraph-boundary evidence must PASS")
    if boundary_report.get("authority") != "GAMES_WORKSHOP_OFFICIAL":
        errors.append("Core rule paragraph-boundary evidence lost Games Workshop authority")
    if boundary_report.get("boundary_version") != "CORE_RULE_PARAGRAPH_BOUNDARY_EXTRACTION_V1":
        errors.append("Core rule paragraph-boundary version drifted")

    bsum = boundary_report.get("summary", {})
    expected_boundary_classes = {
        "REPEATED_OCCURRENCE_BOUNDARIES_VARIANT_HASH": 5,
        "SINGLE_OCCURRENCE_BOUNDARY": 136,
    }
    expected_boundary_summary = {
        "rules": 141,
        "occurrences": 146,
        "families": 24,
        "heading_line_recovery_gaps": 0,
        "empty_body_boundaries": 0,
        "paragraph_candidates": 310,
        "rules_with_multiple_occurrences": 5,
    }
    for key, value in expected_boundary_summary.items():
        if bsum.get(key) != value:
            errors.append(f"Core rule paragraph-boundary summary {key} drifted: {bsum.get(key)} != {value}")
    if bsum.get("classification_counts") != expected_boundary_classes:
        errors.append("Core rule paragraph-boundary classification counts drifted")
    if bsum.get("heading_line_recovery_gap_refs") != []:
        errors.append("Core rule paragraph-boundary heading recovery refs must remain empty")
    if bsum.get("empty_body_boundary_refs") != []:
        errors.append("Core rule paragraph-boundary empty-body refs must remain empty")
    if bsum.get("all_rules_have_nonempty_boundaries") is not True:
        errors.append("Every Core rule must retain a non-empty boundary")

    if boundary_snapshot.get("summary") != bsum:
        errors.append("Core rule paragraph-boundary report summary differs from full snapshot")
    rules = boundary_snapshot.get("rules", [])
    if len(rules) != 141:
        errors.append("Core rule paragraph-boundary snapshot must contain exactly 141 rules")
    if len({x.get("rule_ref") for x in rules}) != 141:
        errors.append("Core rule paragraph-boundary rule_ref identities are not unique")
    if len({x.get("rule_key") for x in rules}) != 141:
        errors.append("Core rule paragraph-boundary rule_key identities are not unique")

    occurrence_count = sum(len(x.get("occurrences", [])) for x in rules)
    paragraph_count = sum(
        len(occ.get("paragraph_candidates", []))
        for rule in rules
        for occ in rule.get("occurrences", [])
    )
    if occurrence_count != 146:
        errors.append(f"Core rule paragraph-boundary occurrence count drifted: {occurrence_count}")
    if paragraph_count != 310:
        errors.append(f"Core rule paragraph candidate count drifted: {paragraph_count}")

    repeated = {
        x.get("rule_ref"): x
        for x in rules
        if x.get("classification") == "REPEATED_OCCURRENCE_BOUNDARIES_VARIANT_HASH"
    }
    expected_repeated = {"15.07","15.08","15.09","15.10","15.11"}
    if set(repeated) != expected_repeated:
        errors.append(f"Repeated Core boundary variant refs drifted: {sorted(repeated)}")
    for ref, rule in repeated.items():
        occ = rule.get("occurrences", [])
        hashes = [x.get("body_semantic_sha256") for x in occ]
        if len(occ) != 2 or len(set(hashes)) != 2:
            errors.append(f"Repeated Core boundary {ref} must preserve two distinct occurrence hashes")

    for rule in rules:
        if not rule.get("occurrences"):
            errors.append(f"Core rule boundary has no occurrences: {rule.get('rule_ref')}")
            continue
        for occ in rule.get("occurrences", []):
            if occ.get("state") != "BOUNDARY_RESOLVED":
                errors.append(f"Unresolved Core boundary occurrence: {rule.get('rule_ref')} {occ.get('state')}")
                continue
            if len(str(occ.get("body_raw_sha256") or "")) != 64:
                errors.append(f"Core boundary raw hash missing: {rule.get('rule_ref')}")
            if len(str(occ.get("body_semantic_sha256") or "")) != 64:
                errors.append(f"Core boundary semantic hash missing: {rule.get('rule_ref')}")
            if int(occ.get("body_line_count", 0)) <= 0 or int(occ.get("body_char_count", 0)) <= 0:
                errors.append(f"Core boundary body count invalid: {rule.get('rule_ref')}")
            if not occ.get("body_spans"):
                errors.append(f"Core boundary page spans missing: {rule.get('rule_ref')}")
            for span in occ.get("body_spans", []):
                if int(span.get("line_start", 0)) > int(span.get("line_end", -1)):
                    errors.append(f"Core boundary span line range inverted: {rule.get('rule_ref')}")
                if int(span.get("char_start", 0)) > int(span.get("char_end", -1)):
                    errors.append(f"Core boundary span char range inverted: {rule.get('rule_ref')}")
                if len(str(span.get("raw_sha256") or "")) != 64:
                    errors.append(f"Core boundary span raw hash missing: {rule.get('rule_ref')}")
                if len(str(span.get("semantic_sha256") or "")) != 64:
                    errors.append(f"Core boundary span semantic hash missing: {rule.get('rule_ref')}")
                if len(str(span.get("page_semantic_sha256") or "")) != 64:
                    errors.append(f"Core boundary span page hash missing: {rule.get('rule_ref')}")
            for para in occ.get("paragraph_candidates", []):
                if int(para.get("line_start", 0)) > int(para.get("line_end", -1)):
                    errors.append(f"Core paragraph candidate line range inverted: {rule.get('rule_ref')}")
                if int(para.get("char_start", 0)) > int(para.get("char_end", -1)):
                    errors.append(f"Core paragraph candidate char range inverted: {rule.get('rule_ref')}")
                if len(str(para.get("semantic_sha256") or "")) != 64:
                    errors.append(f"Core paragraph candidate hash missing: {rule.get('rule_ref')}")

    source_verification = boundary_report.get("source_verification", {})
    if source_verification.get("binary_sha256_match") is not True:
        errors.append("Core boundary source binary verification failed")
    if source_verification.get("page_semantic_fingerprints_match") != 88:
        errors.append("Core boundary source page verification count drifted")
    if source_verification.get("document_semantic_sha256_match") is not True:
        errors.append("Core boundary source document semantic verification failed")

    boundary_auth = boundary_report.get("authority_boundary", {})
    if boundary_auth.get("rule_body_boundary_complete") is not True:
        errors.append("Core rule-body boundary completeness must be true")
    if boundary_auth.get("paragraph_boundaries_are_extraction_candidates") is not True:
        errors.append("Core paragraph boundaries must remain extraction candidates")
    if boundary_auth.get("paragraph_level_rules_ast_complete") is not False:
        errors.append("Core paragraph-boundary layer must not claim paragraph AST completeness")
    if boundary_auth.get("rule_interaction_graph_complete") is not False:
        errors.append("Core paragraph-boundary layer must not claim interaction graph completeness")
    if boundary_auth.get("repeated_occurrence_hash_equality_is_semantic_equivalence") is not False:
        errors.append("Repeated Core occurrence hash equality must not imply semantic equivalence")
    if boundary_auth.get("full_faction_promotion") is not False:
        errors.append("Core paragraph-boundary layer must not promote full factions")
    if boundary_auth.get("current_normalized_factions_change") != 0:
        errors.append("Core paragraph-boundary layer must not change normalized faction count")

    current_layer = boundary_current.get("core_rule_paragraph_boundaries", {})
    if current_layer.get("state") != "PASS_141_RULE_BOUNDARIES":
        errors.append("Current rules Core paragraph-boundary state drifted")
    if current_layer.get("rules") != 141 or current_layer.get("occurrences") != 146:
        errors.append("Current rules Core paragraph-boundary rule/occurrence counts drifted")
    if current_layer.get("paragraph_candidates") != 310:
        errors.append("Current rules Core paragraph candidate count drifted")
    if boundary_current.get("next_milestone") != "CORE_RULE_SEMANTIC_AST_READINESS_V1":
        errors.append("Current rules did not advance to Core paragraph semantic classification")
    current_core = boundary_current.get("source_currentness", {}).get("core_rules_content", {})
    if current_core.get("state") != "OFFICIAL_PUBLIC_PARAGRAPH_SEMANTIC_REVIEW_V1":
        errors.append("Core Rules currentness did not advance to paragraph atomization v1")
    if current_core.get("normative_structured_normalization") != "PARAGRAPH_SEMANTIC_REVIEW_COMPLETE_AST_READINESS_PENDING":
        errors.append("Core Rules normalization boundary did not advance after paragraph atomization")

    profile = boundary_gate.get("scope_profiles", {}).get("core_rule_paragraph_boundaries", {})
    if profile.get("content_state") != "PASS_141_RULE_BOUNDARIES":
        errors.append("Currentness gate Core paragraph-boundary profile must PASS")
    if profile.get("rules") != 141 or profile.get("occurrences") != 146 or profile.get("paragraph_candidates") != 310:
        errors.append("Currentness gate Core paragraph-boundary metrics drifted")
    if profile.get("heading_line_recovery_gaps") != 0 or profile.get("empty_body_boundaries") != 0:
        errors.append("Currentness gate Core paragraph-boundary failure counts must remain zero")

    bg = boundary_cov.get("global", {})
    if boundary_cov.get("status") != "CORE_RULE_PARAGRAPH_SEMANTIC_REVIEW_V1_COMPLETE":
        errors.append("Coverage status did not advance after Core paragraph atomization")
    if bg.get("official_public_core_rule_boundary_rules") != 141:
        errors.append("Coverage Core paragraph-boundary rule count drifted")
    if bg.get("official_public_core_rule_boundary_occurrences") != 146:
        errors.append("Coverage Core paragraph-boundary occurrence count drifted")
    if bg.get("official_public_core_rule_paragraph_candidates") != 310:
        errors.append("Coverage Core paragraph candidate count drifted")
    if bg.get("official_public_core_rule_heading_line_recovery_gaps") != 0:
        errors.append("Coverage Core boundary heading gaps must remain zero")
    if bg.get("official_public_core_rule_empty_body_boundaries") != 0:
        errors.append("Coverage Core empty body boundaries must remain zero")
    if bg.get("current_normalized_factions") != 0 or bg.get("full_normative_semantic_factions") != 0:
        errors.append("Core paragraph-boundary extraction must preserve strict normative faction counters")

    forbidden_boundary_text_keys = {
        "text","description","rules_text","official_text","mirror_text","page_text","prose","paragraph_body","body_text"
    }
    def _check_boundary_no_long_text(value, path="root"):
        if isinstance(value, dict):
            for key, child in value.items():
                if key in forbidden_boundary_text_keys:
                    errors.append(f"Core paragraph-boundary layer vendored forbidden long-text field: {path}.{key}")
                    continue
                _check_boundary_no_long_text(child, f"{path}.{key}")
        elif isinstance(value, list):
            for idx, child in enumerate(value):
                _check_boundary_no_long_text(child, f"{path}[{idx}]")
    _check_boundary_no_long_text(boundary_snapshot)

    for required in [
        ROOT / "docs" / "CORE_RULE_PARAGRAPH_BOUNDARY_MODEL.md",
        ROOT / "schemas" / "core_rule_paragraph_boundaries.schema.json",
        ROOT / "tools" / "build_core_rule_paragraph_boundaries.py",
        ROOT / "tests" / "test_core_rule_paragraph_boundaries.py",
        ROOT / ".github" / "workflows" / "core-rule-paragraph-boundaries.yml",
    ]:
        if not required.exists():
            errors.append(f"Missing Core paragraph-boundary artifact: {required.relative_to(ROOT)}")
except Exception as exc:
    errors.append(f"Core rule paragraph-boundary validation failure: {exc}")

# 3j4. Core Rules stable paragraph atomization contracts.
try:
    paragraph_report = json.loads(
        (ROOT / "reports" / "CORE_RULE_PARAGRAPH_ATOMIZATION_CURRENT.json").read_text(encoding="utf-8")
    )
    paragraph_snapshot = json.loads(
        (ROOT / "rules" / "11e" / "snapshots" / "2026-09-30" / "core_rule_paragraph_atoms" / "index.json").read_text(encoding="utf-8")
    )
    paragraph_current = json.loads((ROOT / "rules" / "11e" / "current.json").read_text(encoding="utf-8"))
    paragraph_gate = json.loads((ROOT / "sources" / "currentness_gate.json").read_text(encoding="utf-8"))
    paragraph_cov = json.loads((ROOT / "coverage" / "current.json").read_text(encoding="utf-8"))

    if paragraph_report.get("status") != "PASS" or paragraph_snapshot.get("status") != "PASS":
        errors.append("Core paragraph atomization evidence must PASS")
    if paragraph_report.get("authority") != "GAMES_WORKSHOP_OFFICIAL":
        errors.append("Core paragraph atomization lost Games Workshop authority")
    if paragraph_report.get("atomization_version") != "CORE_RULE_PARAGRAPH_ATOMIZATION_V1":
        errors.append("Core paragraph atomization version drifted")

    psum = paragraph_report.get("summary", {})
    expected_paragraph_classes = {
        "REPEATED_OCCURRENCE_PARAGRAPH_VARIANT": 10,
        "SINGLE_OCCURRENCE_PARAGRAPH": 300,
    }
    expected_paragraph_summary = {
        "paragraph_atoms": 310,
        "unique_paragraph_keys": 310,
        "parent_paragraph_candidates": 310,
        "rules_represented": 141,
        "occurrences_represented": 146,
        "families_represented": 24,
        "range_validation_failures": 0,
        "paragraph_hashes_reproduced_from_verified_pdf": 310,
    }
    for key, value in expected_paragraph_summary.items():
        if psum.get(key) != value:
            errors.append(f"Core paragraph atomization summary {key} drifted: {psum.get(key)} != {value}")
    if psum.get("classification_counts") != expected_paragraph_classes:
        errors.append("Core paragraph atomization classification counts drifted")
    if psum.get("repeated_occurrence_rule_refs") != ["15.07","15.08","15.09","15.10","15.11"]:
        errors.append("Core paragraph repeated-occurrence rule refs drifted")
    if psum.get("range_validation_failure_samples") != []:
        errors.append("Core paragraph atomization must have zero range failure samples")
    if psum.get("all_parent_candidates_atomized") is not True:
        errors.append("All 310 parent paragraph candidates must remain atomized")

    atoms = paragraph_snapshot.get("paragraph_atoms", [])
    if len(atoms) != 310:
        errors.append("Core paragraph atom snapshot must contain exactly 310 atoms")
    if len({x.get("paragraph_key") for x in atoms}) != 310:
        errors.append("Core paragraph atom keys are not unique")
    if len({x.get("rule_ref") for x in atoms}) != 141:
        errors.append("Core paragraph atoms must represent exactly 141 parent rules")
    if len({x.get("occurrence_key") for x in atoms}) != 146:
        errors.append("Core paragraph atoms must represent exactly 146 parent occurrences")
    if len({x.get("family_id") for x in atoms}) != 24:
        errors.append("Core paragraph atoms must represent exactly 24 families")
    for atom in atoms:
        if int(atom.get("line_start", 0)) > int(atom.get("line_end", -1)):
            errors.append(f"Core paragraph atom line range inverted: {atom.get('paragraph_key')}")
        if int(atom.get("char_start", 0)) > int(atom.get("char_end", -1)):
            errors.append(f"Core paragraph atom char range inverted: {atom.get('paragraph_key')}")
        for key in ("semantic_sha256","page_semantic_sha256","parent_body_semantic_sha256"):
            if len(str(atom.get(key) or "")) != 64:
                errors.append(f"Core paragraph atom missing 64-char {key}: {atom.get('paragraph_key')}")

    pverify = paragraph_report.get("source_verification", {})
    if pverify.get("binary_sha256_match") is not True:
        errors.append("Core paragraph atomization source binary verification failed")
    if pverify.get("page_semantic_fingerprints_match") != 88:
        errors.append("Core paragraph atomization source page verification count drifted")
    if pverify.get("document_semantic_sha256_match") is not True:
        errors.append("Core paragraph atomization document semantic verification failed")

    pauth = paragraph_report.get("authority_boundary", {})
    if pauth.get("stable_paragraph_identity_complete") is not True:
        errors.append("Core stable paragraph identity completeness must be true")
    if pauth.get("paragraph_semantic_ast_complete") is not False:
        errors.append("Core paragraph atomization must not claim semantic AST completeness")
    if pauth.get("condition_effect_parsing_complete") is not False:
        errors.append("Core paragraph atomization must not claim condition/effect parsing completeness")
    if pauth.get("rule_interaction_graph_complete") is not False:
        errors.append("Core paragraph atomization must not claim interaction graph completeness")
    if pauth.get("repeated_paragraph_variant_is_semantic_conflict") is not False:
        errors.append("Repeated Core paragraph variants must not become semantic conflicts automatically")
    if pauth.get("current_normalized_factions_change") != 0:
        errors.append("Core paragraph atomization must not change normalized faction count")

    current_layer = paragraph_current.get("core_rule_paragraph_atomization", {})
    if current_layer.get("state") != "PASS_310_PARAGRAPH_ATOMS":
        errors.append("Current rules Core paragraph atomization state drifted")
    if current_layer.get("paragraph_atoms") != 310 or current_layer.get("unique_paragraph_keys") != 310:
        errors.append("Current rules Core paragraph atom counts drifted")
    if paragraph_current.get("next_milestone") != "CORE_RULE_SEMANTIC_AST_READINESS_V1":
        errors.append("Current rules did not advance to Core paragraph semantic classification")
    current_core = paragraph_current.get("source_currentness", {}).get("core_rules_content", {})
    if current_core.get("state") != "OFFICIAL_PUBLIC_PARAGRAPH_SEMANTIC_REVIEW_V1":
        errors.append("Core Rules currentness did not advance to paragraph atomization v1")
    if current_core.get("normative_structured_normalization") != "PARAGRAPH_SEMANTIC_REVIEW_COMPLETE_AST_READINESS_PENDING":
        errors.append("Core Rules normalization boundary did not advance after paragraph atomization")

    profile = paragraph_gate.get("scope_profiles", {}).get("core_rule_paragraph_atoms", {})
    if profile.get("content_state") != "PASS_310_PARAGRAPH_ATOMS":
        errors.append("Currentness gate Core paragraph atom profile must PASS")
    if profile.get("paragraph_atoms") != 310 or profile.get("rules_represented") != 141 or profile.get("occurrences_represented") != 146:
        errors.append("Currentness gate Core paragraph atom metrics drifted")
    if profile.get("range_validation_failures") != 0:
        errors.append("Currentness gate Core paragraph atom range failures must remain zero")

    pg = paragraph_cov.get("global", {})
    if paragraph_cov.get("status") != "CORE_RULE_PARAGRAPH_SEMANTIC_REVIEW_V1_COMPLETE":
        errors.append("Coverage status did not advance after Core paragraph atomization")
    if pg.get("official_public_core_paragraph_atoms") != 310:
        errors.append("Coverage Core paragraph atom count drifted")
    if pg.get("official_public_core_paragraph_unique_keys") != 310:
        errors.append("Coverage Core paragraph unique-key count drifted")
    if pg.get("official_public_core_paragraph_rules_represented") != 141:
        errors.append("Coverage Core paragraph rule count drifted")
    if pg.get("official_public_core_paragraph_occurrences_represented") != 146:
        errors.append("Coverage Core paragraph occurrence count drifted")
    if pg.get("official_public_core_single_occurrence_paragraph_atoms") != 300:
        errors.append("Coverage single-occurrence paragraph count drifted")
    if pg.get("official_public_core_repeated_occurrence_paragraph_variants") != 10:
        errors.append("Coverage repeated paragraph variant count drifted")
    if pg.get("official_public_core_paragraph_range_validation_failures") != 0:
        errors.append("Coverage paragraph range validation failures must remain zero")
    if pg.get("current_normalized_factions") != 0 or pg.get("full_normative_semantic_factions") != 0:
        errors.append("Core paragraph atomization must preserve strict normative faction counters")

    forbidden_paragraph_text_keys = {
        "text","description","rules_text","official_text","mirror_text","page_text","prose",
        "paragraph_text","paragraph_body","body_text",
    }
    def _check_paragraph_atoms_no_long_text(value, path="root"):
        if isinstance(value, dict):
            for key, child in value.items():
                if key in forbidden_paragraph_text_keys:
                    errors.append(f"Core paragraph atomization vendored forbidden long-text field: {path}.{key}")
                    continue
                _check_paragraph_atoms_no_long_text(child, f"{path}.{key}")
        elif isinstance(value, list):
            for idx, child in enumerate(value):
                _check_paragraph_atoms_no_long_text(child, f"{path}[{idx}]")
    _check_paragraph_atoms_no_long_text(paragraph_snapshot)

    for required in [
        ROOT / "docs" / "CORE_RULE_PARAGRAPH_ATOMIZATION_MODEL.md",
        ROOT / "schemas" / "core_rule_paragraph_atoms.schema.json",
        ROOT / "tools" / "build_core_rule_paragraph_atoms.py",
        ROOT / "tests" / "test_core_rule_paragraph_atomization.py",
        ROOT / ".github" / "workflows" / "core-rule-paragraph-atomization.yml",
    ]:
        if not required.exists():
            errors.append(f"Missing Core paragraph atomization artifact: {required.relative_to(ROOT)}")
except Exception as exc:
    errors.append(f"Core rule paragraph atomization validation failure: {exc}")

# 3j5. Core Rules paragraph semantic classification contracts.
try:
    semantic_report = json.loads(
        (ROOT / "reports" / "CORE_RULE_PARAGRAPH_SEMANTIC_CLASSIFICATION_CURRENT.json").read_text(encoding="utf-8")
    )
    semantic_snapshot = json.loads(
        (ROOT / "rules" / "11e" / "snapshots" / "2026-09-30" / "core_rule_paragraph_semantics" / "index.json").read_text(encoding="utf-8")
    )
    semantic_current = json.loads((ROOT / "rules" / "11e" / "current.json").read_text(encoding="utf-8"))
    semantic_gate = json.loads((ROOT / "sources" / "currentness_gate.json").read_text(encoding="utf-8"))
    semantic_cov = json.loads((ROOT / "coverage" / "current.json").read_text(encoding="utf-8"))

    if semantic_report.get("status") != "PASS" or semantic_snapshot.get("status") != "PASS":
        errors.append("Core paragraph semantic classification evidence must PASS")
    if semantic_report.get("authority") != "GAMES_WORKSHOP_OFFICIAL":
        errors.append("Core paragraph semantic classification lost Games Workshop authority")
    if semantic_report.get("classifier_version") != "CORE_RULE_PARAGRAPH_SEMANTIC_CLASSIFICATION_V1":
        errors.append("Core paragraph semantic classifier version drifted")

    expected_roles = {
        "CONDITION_OR_TRIGGER": 31,
        "MIXED": 134,
        "MODIFICATION_OR_REPLACEMENT": 1,
        "OBLIGATION": 1,
        "PERMISSION": 20,
        "PROCEDURE_OR_SEQUENCE": 7,
        "PROHIBITION": 4,
        "UNCLASSIFIED": 112,
    }
    expected_confidence = {"HIGH": 64, "MIXED": 134, "NONE": 112}
    ss = semantic_report.get("summary", {})
    if ss.get("paragraphs") != 310 or ss.get("unique_paragraph_keys") != 310:
        errors.append("Core paragraph semantic classification must cover 310 unique paragraphs")
    if ss.get("role_counts") != expected_roles:
        errors.append("Core paragraph semantic role distribution drifted")
    if ss.get("confidence_counts") != expected_confidence:
        errors.append("Core paragraph semantic confidence distribution drifted")
    if ss.get("paragraphs_with_signals") != 200 or ss.get("paragraphs_without_signals") != 110:
        errors.append("Core paragraph semantic signal coverage drifted")
    if ss.get("mixed_paragraphs") != 134 or ss.get("unclassified_paragraphs") != 112:
        errors.append("Core paragraph fail-closed MIXED/UNCLASSIFIED counts drifted")
    if ss.get("repeated_variant_paragraphs") != 10:
        errors.append("Core paragraph repeated-variant semantic count drifted")
    if ss.get("repeated_variant_role_counts") != {"CONDITION_OR_TRIGGER": 2, "MIXED": 8}:
        errors.append("Core paragraph repeated-variant role distribution drifted")
    if ss.get("paragraph_hashes_reproduced_from_verified_pdf") != 310:
        errors.append("Core paragraph semantic hash reproduction count drifted")
    if semantic_snapshot.get("summary") != ss:
        errors.append("Core paragraph semantic compact/full summary mismatch")

    rows = semantic_snapshot.get("classifications", [])
    if len(rows) != 310 or len({x.get("paragraph_key") for x in rows}) != 310:
        errors.append("Core paragraph semantic snapshot must contain 310 unique classifications")
    valid_roles = {
        "PROHIBITION","OBLIGATION","PERMISSION","DEFINITION",
        "MODIFICATION_OR_REPLACEMENT","PROCEDURE_OR_SEQUENCE",
        "CONDITION_OR_TRIGGER","REFERENCE_OR_CROSS_REFERENCE",
        "MIXED","UNCLASSIFIED",
    }
    if not {x.get("primary_role") for x in rows} <= valid_roles:
        errors.append("Core paragraph semantic snapshot contains unknown primary role")
    if not {x.get("classification_confidence") for x in rows} <= {"HIGH","MIXED","NONE"}:
        errors.append("Core paragraph semantic snapshot contains unknown confidence state")
    if any(len(str(x.get("semantic_sha256") or "")) != 64 for x in rows):
        errors.append("Core paragraph semantic row missing 64-char semantic SHA")
    if len({x.get("rule_ref") for x in rows}) != 141:
        errors.append("Core paragraph semantic rows must represent 141 parent rules")
    if len({x.get("occurrence_key") for x in rows}) != 146:
        errors.append("Core paragraph semantic rows must represent 146 parent occurrences")

    verify = semantic_report.get("source_verification", {})
    if verify.get("binary_sha256_match") is not True:
        errors.append("Core paragraph semantic source binary verification failed")
    if verify.get("page_semantic_fingerprints_match") != 88:
        errors.append("Core paragraph semantic source page verification count drifted")
    if verify.get("document_semantic_sha256_match") is not True:
        errors.append("Core paragraph semantic source document verification failed")

    auth = semantic_report.get("authority_boundary", {})
    if auth.get("semantic_role_classification_complete") is not True:
        errors.append("Core paragraph semantic classification completeness must be true")
    if auth.get("classification_is_lexical_structural_not_full_semantic_ast") is not True:
        errors.append("Core paragraph semantic layer must remain lexical/structural")
    if auth.get("mixed_and_unclassified_are_valid_fail_closed_states") is not True:
        errors.append("Core paragraph semantic layer lost fail-closed MIXED/UNCLASSIFIED policy")
    if auth.get("paragraph_prose_committed") is not False:
        errors.append("Core paragraph semantic layer must not commit paragraph prose")
    if auth.get("condition_effect_ast_complete") is not False:
        errors.append("Core paragraph semantic layer must not claim condition/effect AST completeness")
    if auth.get("rule_interaction_graph_complete") is not False:
        errors.append("Core paragraph semantic layer must not claim interaction graph completeness")
    if auth.get("repeated_variant_semantic_equivalence_claimed") is not False:
        errors.append("Core paragraph semantic layer must not claim repeated-variant equivalence")
    if auth.get("current_normalized_factions_change") != 0:
        errors.append("Core paragraph semantic classification must not change normalized faction count")

    layer = semantic_current.get("core_rule_paragraph_semantic_classification", {})
    if layer.get("state") != "PASS_310_PARAGRAPHS_CLASSIFIED":
        errors.append("Current rules Core paragraph semantic classification state drifted")
    if layer.get("role_counts") != expected_roles or layer.get("confidence_counts") != expected_confidence:
        errors.append("Current rules Core paragraph semantic distribution drifted")
    if layer.get("semantic_review_pending") is not False:
        errors.append("Core paragraph semantic classification review-pending flag must be false after review closure")
    if layer.get("semantic_review_complete") is not True:
        errors.append("Core paragraph semantic review completeness must be true after review closure")
    if layer.get("ast_readiness_pending") is not True:
        errors.append("Core paragraph AST readiness must remain pending after v1 classification")
    if semantic_current.get("next_milestone") != "CORE_RULE_SEMANTIC_AST_READINESS_V1":
        errors.append("Current rules did not advance to Core paragraph semantic review")
    current_core = semantic_current.get("source_currentness", {}).get("core_rules_content", {})
    if current_core.get("state") != "OFFICIAL_PUBLIC_PARAGRAPH_SEMANTIC_REVIEW_V1":
        errors.append("Core Rules currentness did not advance to semantic classification v1")
    if current_core.get("normative_structured_normalization") != "PARAGRAPH_SEMANTIC_REVIEW_COMPLETE_AST_READINESS_PENDING":
        errors.append("Core Rules normalization boundary did not advance to semantic review")

    profile = semantic_gate.get("scope_profiles", {}).get("core_rule_paragraph_semantics", {})
    if profile.get("content_state") != "PASS_310_PARAGRAPHS_CLASSIFIED":
        errors.append("Currentness gate Core paragraph semantic profile must PASS")
    if profile.get("role_counts") != expected_roles or profile.get("confidence_counts") != expected_confidence:
        errors.append("Currentness gate Core paragraph semantic distribution drifted")

    sg = semantic_cov.get("global", {})
    if semantic_cov.get("status") != "CORE_RULE_PARAGRAPH_SEMANTIC_REVIEW_V1_COMPLETE":
        errors.append("Coverage status did not advance after Core paragraph semantic classification")
    if sg.get("official_public_core_paragraph_semantic_classification_complete") is not True:
        errors.append("Coverage Core paragraph semantic classification completeness drifted")
    if sg.get("official_public_core_paragraph_semantic_ast_complete") is not False:
        errors.append("Coverage Core paragraph semantic AST must remain pending")
    if sg.get("official_public_core_paragraph_semantic_classified") != 310:
        errors.append("Coverage Core paragraph semantic classified count drifted")
    if sg.get("official_public_core_paragraph_high_confidence") != 64:
        errors.append("Coverage Core paragraph HIGH count drifted")
    if sg.get("official_public_core_paragraph_mixed") != 134:
        errors.append("Coverage Core paragraph MIXED count drifted")
    if sg.get("official_public_core_paragraph_unclassified") != 112:
        errors.append("Coverage Core paragraph UNCLASSIFIED count drifted")
    if sg.get("official_public_core_paragraph_role_counts") != expected_roles:
        errors.append("Coverage Core paragraph role distribution drifted")
    if sg.get("official_public_core_paragraph_confidence_counts") != expected_confidence:
        errors.append("Coverage Core paragraph confidence distribution drifted")
    if sg.get("official_public_core_paragraph_semantic_hashes_reproduced") != 310:
        errors.append("Coverage Core paragraph semantic hash reproduction count drifted")
    if sg.get("current_normalized_factions") != 0 or sg.get("full_normative_semantic_factions") != 0:
        errors.append("Core paragraph semantic classification must preserve strict normative faction counters")

    forbidden_semantic_text_keys = {
        "text","description","rules_text","official_text","mirror_text","page_text",
        "prose","paragraph_text","body_text","matched_phrase",
    }
    def _check_semantic_no_long_text(value, path="root"):
        if isinstance(value, dict):
            for key, child in value.items():
                if key in forbidden_semantic_text_keys:
                    errors.append(f"Core paragraph semantic classification vendored forbidden text field: {path}.{key}")
                    continue
                _check_semantic_no_long_text(child, f"{path}.{key}")
        elif isinstance(value, list):
            for idx, child in enumerate(value):
                _check_semantic_no_long_text(child, f"{path}[{idx}]")
    _check_semantic_no_long_text(semantic_snapshot)

    for required in [
        ROOT / "docs" / "CORE_RULE_PARAGRAPH_SEMANTIC_CLASSIFICATION_MODEL.md",
        ROOT / "schemas" / "core_rule_paragraph_semantic_classification.schema.json",
        ROOT / "tools" / "classify_core_rule_paragraph_semantics.py",
        ROOT / "tests" / "test_core_rule_paragraph_semantic_classification.py",
        ROOT / ".github" / "workflows" / "core-rule-paragraph-semantic-classification.yml",
    ]:
        if not required.exists():
            errors.append(f"Missing Core paragraph semantic classification artifact: {required.relative_to(ROOT)}")
except Exception as exc:
    errors.append(f"Core paragraph semantic classification validation failure: {exc}")

# 3j6. Core Rules paragraph semantic review contracts.
try:
    review_report = json.loads(
        (ROOT / "reports" / "CORE_RULE_PARAGRAPH_SEMANTIC_REVIEW_CURRENT.json").read_text(encoding="utf-8")
    )
    review_snapshot = json.loads(
        (ROOT / "rules" / "11e" / "snapshots" / "2026-09-30" / "core_rule_paragraph_semantic_review" / "index.json").read_text(encoding="utf-8")
    )
    review_current = json.loads((ROOT / "rules" / "11e" / "current.json").read_text(encoding="utf-8"))
    review_gate = json.loads((ROOT / "sources" / "currentness_gate.json").read_text(encoding="utf-8"))
    review_cov = json.loads((ROOT / "coverage" / "current.json").read_text(encoding="utf-8"))

    if review_report.get("status") != "PASS" or review_snapshot.get("status") != "PASS":
        errors.append("Core paragraph semantic review evidence must PASS")
    if review_report.get("authority") != "GAMES_WORKSHOP_OFFICIAL":
        errors.append("Core paragraph semantic review lost Games Workshop authority")
    if review_report.get("review_version") != "CORE_RULE_PARAGRAPH_SEMANTIC_REVIEW_V1":
        errors.append("Core paragraph semantic review version drifted")

    expected_review_states = {
        "AXIS_PROFILE_READY": 156,
        "MULTI_MODAL_REVIEW_REQUIRED": 42,
        "NO_STRONG_SIGNAL_REVIEW_REQUIRED": 112,
    }
    expected_modal_axes = {
        "MULTI_MODAL": 42,
        "NONE": 173,
        "OBLIGATION": 17,
        "PERMISSION": 67,
        "PROHIBITION": 11,
    }
    expected_mixed_decomposition = {
        "axis_profile_ready": 92,
        "multi_modal_review_required": 42,
        "no_strong_signal_review_required": 0,
    }
    expected_unclassified_decomposition = {
        "signal_free": 110,
        "weak_only": 2,
        "review_required": 112,
    }
    expected_repeated_review = {
        "AXIS_PROFILE_READY": 4,
        "MULTI_MODAL_REVIEW_REQUIRED": 6,
    }

    rs = review_report.get("summary", {})
    if rs.get("profiles") != 310 or rs.get("unique_paragraph_keys") != 310:
        errors.append("Core paragraph semantic review must cover 310 unique profiles")
    if rs.get("review_state_counts") != expected_review_states:
        errors.append("Core paragraph semantic review-state distribution drifted")
    if rs.get("modal_axis_counts") != expected_modal_axes:
        errors.append("Core paragraph semantic modal-axis distribution drifted")
    if rs.get("axis_profile_ready") != 156 or rs.get("review_required") != 154:
        errors.append("Core paragraph semantic review ready/blocked counts drifted")
    if rs.get("mixed_decomposition") != expected_mixed_decomposition:
        errors.append("Core paragraph MIXED decomposition drifted")
    if rs.get("unclassified_decomposition") != expected_unclassified_decomposition:
        errors.append("Core paragraph UNCLASSIFIED decomposition drifted")
    if rs.get("repeated_variant_review_state_counts") != expected_repeated_review:
        errors.append("Core paragraph repeated-variant review distribution drifted")
    if rs.get("parent_hashes_verified") != 310:
        errors.append("Core paragraph semantic review parent-hash verification count drifted")
    if review_snapshot.get("summary") != rs:
        errors.append("Core paragraph semantic review compact/full summary mismatch")

    profiles = review_snapshot.get("profiles", [])
    if len(profiles) != 310 or len({x.get("paragraph_key") for x in profiles}) != 310:
        errors.append("Core paragraph semantic review snapshot must contain 310 unique profiles")
    valid_modal = {"NONE","PERMISSION","OBLIGATION","PROHIBITION","MULTI_MODAL"}
    valid_review_states = {
        "AXIS_PROFILE_READY",
        "MULTI_MODAL_REVIEW_REQUIRED",
        "NO_STRONG_SIGNAL_REVIEW_REQUIRED",
    }
    if not {x.get("modal_axis") for x in profiles} <= valid_modal:
        errors.append("Core paragraph semantic review contains unknown modal-axis value")
    if not {x.get("review_state") for x in profiles} <= valid_review_states:
        errors.append("Core paragraph semantic review contains unknown review state")
    if any(len(str(x.get("semantic_sha256") or "")) != 64 for x in profiles):
        errors.append("Core paragraph semantic review profile missing 64-char semantic SHA")
    if any(x.get("ast_readiness_claimed") is not False for x in profiles):
        errors.append("Core paragraph semantic review must not claim AST readiness per profile")
    for row in profiles:
        for key in (
            "condition_trigger_present",
            "procedure_sequence_present",
            "definition_present",
            "modification_replacement_present",
            "reference_present",
            "structural_list_present",
        ):
            if not isinstance(row.get(key), bool):
                errors.append(f"Core paragraph semantic review axis is not boolean: {row.get('paragraph_key')} {key}")

    rauth = review_report.get("authority_boundary", {})
    if rauth.get("semantic_review_complete") is not True:
        errors.append("Core paragraph semantic review completeness must be true")
    if rauth.get("multi_axis_profile_is_not_condition_effect_ast") is not True:
        errors.append("Core paragraph semantic review must not equate axis profiles with AST")
    if rauth.get("axis_profile_ready_is_not_ast_readiness_claim") is not True:
        errors.append("AXIS_PROFILE_READY must not be treated as AST readiness")
    if rauth.get("multi_modal_rows_remain_unresolved") is not True:
        errors.append("Multi-modal Core paragraphs must remain unresolved")
    if rauth.get("no_strong_signal_rows_remain_unresolved") is not True:
        errors.append("No-strong-signal Core paragraphs must remain unresolved")
    if rauth.get("paragraph_prose_committed") is not False:
        errors.append("Core paragraph semantic review must not commit paragraph prose")
    if rauth.get("condition_effect_ast_complete") is not False:
        errors.append("Core paragraph semantic review must not claim condition/effect AST completeness")
    if rauth.get("rule_interaction_graph_complete") is not False:
        errors.append("Core paragraph semantic review must not claim interaction graph completeness")
    if rauth.get("repeated_variant_semantic_equivalence_claimed") is not False:
        errors.append("Core paragraph semantic review must not claim repeated-variant equivalence")
    if rauth.get("current_normalized_factions_change") != 0:
        errors.append("Core paragraph semantic review must not change normalized faction count")
    if rauth.get("next_milestone") != "CORE_RULE_SEMANTIC_AST_READINESS_V1":
        errors.append("Core paragraph semantic review next milestone drifted")

    current_layer = review_current.get("core_rule_paragraph_semantic_review", {})
    if current_layer.get("state") != "PASS_310_PARAGRAPH_SEMANTIC_PROFILES_REVIEWED":
        errors.append("Current rules Core paragraph semantic review state drifted")
    if current_layer.get("profiles") != 310:
        errors.append("Current rules Core paragraph semantic review profile count drifted")
    if current_layer.get("review_state_counts") != expected_review_states:
        errors.append("Current rules Core paragraph semantic review-state distribution drifted")
    if current_layer.get("modal_axis_counts") != expected_modal_axes:
        errors.append("Current rules Core paragraph modal-axis distribution drifted")
    if current_layer.get("axis_profile_ready") != 156 or current_layer.get("review_required") != 154:
        errors.append("Current rules Core paragraph review ready/blocked counts drifted")
    if current_layer.get("axis_profile_ready_is_ast_ready") is not False:
        errors.append("Current rules must not equate AXIS_PROFILE_READY with AST readiness")
    if current_layer.get("ast_readiness_pending") is not True:
        errors.append("Core paragraph AST readiness must remain pending after semantic review")
    if current_layer.get("condition_effect_ast_complete") is not False:
        errors.append("Current rules Core paragraph condition/effect AST must remain incomplete")
    if review_current.get("next_milestone") != "CORE_RULE_SEMANTIC_AST_READINESS_V1":
        errors.append("Current rules did not advance to Core semantic AST-readiness audit")
    current_core = review_current.get("source_currentness", {}).get("core_rules_content", {})
    if current_core.get("state") != "OFFICIAL_PUBLIC_PARAGRAPH_SEMANTIC_REVIEW_V1":
        errors.append("Core Rules currentness did not advance to semantic review v1")
    if current_core.get("normative_structured_normalization") != "PARAGRAPH_SEMANTIC_REVIEW_COMPLETE_AST_READINESS_PENDING":
        errors.append("Core Rules normalization boundary did not advance to AST-readiness pending")

    profile = review_gate.get("scope_profiles", {}).get("core_rule_paragraph_semantic_review", {})
    if profile.get("content_state") != "PASS_310_PARAGRAPH_SEMANTIC_PROFILES_REVIEWED":
        errors.append("Currentness gate Core paragraph semantic review profile must PASS")
    if profile.get("profiles") != 310 or profile.get("axis_profile_ready") != 156 or profile.get("review_required") != 154:
        errors.append("Currentness gate Core paragraph semantic review metrics drifted")
    if profile.get("review_state_counts") != expected_review_states:
        errors.append("Currentness gate Core paragraph review-state distribution drifted")

    rg = review_cov.get("global", {})
    if review_cov.get("status") != "CORE_RULE_PARAGRAPH_SEMANTIC_REVIEW_V1_COMPLETE":
        errors.append("Coverage status did not advance after Core paragraph semantic review")
    expected_cov = {
        "official_public_core_paragraph_semantic_review_profiles": 310,
        "official_public_core_paragraph_axis_profile_ready": 156,
        "official_public_core_paragraph_semantic_review_required": 154,
        "official_public_core_paragraph_multi_modal_review_required": 42,
        "official_public_core_paragraph_no_strong_signal_review_required": 112,
        "official_public_core_paragraph_mixed_axis_profile_ready": 92,
        "official_public_core_paragraph_unclassified_signal_free": 110,
        "official_public_core_paragraph_unclassified_weak_only": 2,
        "official_public_core_repeated_axis_profile_ready": 4,
        "official_public_core_repeated_multi_modal_review_required": 6,
    }
    for key, value in expected_cov.items():
        if rg.get(key) != value:
            errors.append(f"Coverage Core paragraph semantic review metric drifted: {key}")
    if rg.get("official_public_core_semantic_ast_readiness_complete") is not False:
        errors.append("Coverage Core semantic AST readiness must remain incomplete")
    if rg.get("official_public_core_condition_effect_ast_complete") is not False:
        errors.append("Coverage Core condition/effect AST must remain incomplete")
    if rg.get("official_public_core_rule_interaction_graph_complete") is not False:
        errors.append("Coverage Core interaction graph must remain incomplete")
    if rg.get("current_normalized_factions") != 0 or rg.get("full_normative_semantic_factions") != 0:
        errors.append("Core paragraph semantic review must preserve strict normative faction counters")

    forbidden_review_text_keys = {
        "text","description","rules_text","official_text","mirror_text","page_text",
        "prose","paragraph_text","body_text","matched_phrase",
    }
    def _check_review_no_long_text(value, path="root"):
        if isinstance(value, dict):
            for key, child in value.items():
                if key in forbidden_review_text_keys:
                    errors.append(f"Core paragraph semantic review vendored forbidden text field: {path}.{key}")
                    continue
                _check_review_no_long_text(child, f"{path}.{key}")
        elif isinstance(value, list):
            for idx, child in enumerate(value):
                _check_review_no_long_text(child, f"{path}[{idx}]")
    _check_review_no_long_text(review_snapshot)

    for required in [
        ROOT / "reports" / "CORE_RULE_PARAGRAPH_SEMANTIC_REVIEW_CURRENT.json",
        ROOT / "rules" / "11e" / "snapshots" / "2026-09-30" / "core_rule_paragraph_semantic_review" / "index.json",
        ROOT / "docs" / "CORE_RULE_PARAGRAPH_SEMANTIC_REVIEW_MODEL.md",
        ROOT / "schemas" / "core_rule_paragraph_semantic_review.schema.json",
        ROOT / "tools" / "review_core_rule_paragraph_semantics.py",
        ROOT / "tests" / "test_core_rule_paragraph_semantic_review.py",
        ROOT / ".github" / "workflows" / "core-rule-paragraph-semantic-review.yml",
    ]:
        if not required.exists():
            errors.append(f"Missing Core paragraph semantic review artifact: {required.relative_to(ROOT)}")
except Exception as exc:
    errors.append(f"Core paragraph semantic review validation failure: {exc}")

# 3k. Official public structured normalization expansion contracts.
try:
    core_structure = json.loads(
        (ROOT / "reports" / "CORE_RULES_STRUCTURE_CURRENT.json").read_text(encoding="utf-8")
    )
    core_structure_snapshot = json.loads(
        (ROOT / "rules" / "11e" / "snapshots" / "2026-09-30" / "core_rules_structure" / "index.json").read_text(encoding="utf-8")
    )
    residual = json.loads(
        (ROOT / "reports" / "OFFICIAL_PUBLIC_OVERLAP_RESIDUAL_CLASSIFICATION_CURRENT.json").read_text(encoding="utf-8")
    )
    residual_snapshot = json.loads(
        (ROOT / "rules" / "11e" / "snapshots" / "2026-09-30" / "official_public_overlap" / "residual_classification.json").read_text(encoding="utf-8")
    )
    expansion_current = json.loads((ROOT / "rules" / "11e" / "current.json").read_text(encoding="utf-8"))
    expansion_gate = json.loads((ROOT / "sources" / "currentness_gate.json").read_text(encoding="utf-8"))
    expansion_cov = json.loads((ROOT / "coverage" / "current.json").read_text(encoding="utf-8"))

    if core_structure.get("status") != "PASS" or core_structure_snapshot.get("status") != "PASS":
        errors.append("Core Rules structured normalization evidence must PASS")
    if core_structure.get("authority") != "GAMES_WORKSHOP_OFFICIAL":
        errors.append("Core Rules structured normalization lost Games Workshop authority")
    core_summary = core_structure.get("summary", {})
    expected_family_ids = [f"{i:02d}" for i in range(1, 25)]
    if core_summary.get("rule_reference_family_ids") != expected_family_ids:
        errors.append("Core Rules rule-reference families must remain canonical 01-24")
    if core_summary.get("rule_reference_families") != 24:
        errors.append("Core Rules rule-reference family count drifted")
    if core_summary.get("rule_reference_count") != 141:
        errors.append("Core Rules detected rule-reference count drifted")
    if core_summary.get("pages_represented") != 88:
        errors.append("Core Rules structured normalization must represent all 88 pages")
    if core_summary.get("sections") != 80:
        errors.append("Core Rules flat heading section count drifted")
    core_boundary = core_structure.get("authority_boundary", {})
    if core_boundary.get("section_level_structure_complete_for_public_pdf") is not True:
        errors.append("Core Rules section-level family structure must be complete")
    if core_boundary.get("hierarchical_structure_complete") is not False:
        errors.append("Core Rules nested hierarchy must not be overclaimed")
    if core_boundary.get("paragraph_level_rules_ast_complete") is not False:
        errors.append("Core Rules paragraph AST must remain pending")
    if core_boundary.get("current_normalized_factions_change") != 0:
        errors.append("Core Rules structure must not change full-faction coverage")

    expected_unscoped = {
        "CORE_PUBLIC_GLOBAL": 21,
        "EDITION_11_SOURCE_MATCH_OUTSIDE_OWN_PACK": 426,
        "FACTION_ONLY_MATCH_OUTSIDE_OWN_PACK": 124,
        "NON_11_OR_LEGENDS_SOURCE": 995,
    }
    expected_no_exact = {
        "EDITION_11_SOURCE_NO_EXACT_PUBLIC_OVERLAP": 3467,
        "FACTION_ONLY_NO_EXACT_PUBLIC_OVERLAP": 1868,
        "NON_11_OR_LEGENDS_SOURCE_NO_EXACT": 227,
        "NO_SOURCE_OR_FACTION_NO_EXACT": 61,
        "TOO_SHORT_FOR_SAFE_AUTO_MATCH": 2313,
    }
    if residual.get("status") != "PASS" or residual_snapshot.get("status") != "PASS":
        errors.append("Official-public residual classification must PASS")
    if residual.get("unscoped_exact", {}).get("total") != 1566:
        errors.append("Residual unscoped exact total drifted")
    if residual.get("unscoped_exact", {}).get("classes") != expected_unscoped:
        errors.append("Residual unscoped exact classes drifted")
    if residual.get("no_exact_public_overlap", {}).get("total") != 7936:
        errors.append("Residual no-exact total drifted")
    if residual.get("no_exact_public_overlap", {}).get("classes") != expected_no_exact:
        errors.append("Residual no-exact classes drifted")
    residual_boundary = residual.get("authority_boundary", {})
    if residual_boundary.get("no_exact_is_conflict") is not False:
        errors.append("No-exact public overlap must not become SOURCE_CONFLICT automatically")
    if residual_boundary.get("unscoped_exact_is_promotable") is not False:
        errors.append("Unscoped exact overlap must remain non-promotable")
    if residual_boundary.get("legends_or_non_11_reuse_promotes_current_rules") is not False:
        errors.append("Legends/non-11 exact reuse must not promote current rules")
    if residual_boundary.get("app_codex_inference_allowed") is not False:
        errors.append("Residual classification must not infer app/Codex wording")
    if residual.get("summary", {}).get("promoted_units") != 0:
        errors.append("Residual classification must promote zero units")
    if residual.get("summary", {}).get("semantic_conflicts_created") != 0:
        errors.append("Residual classification must create zero semantic conflicts")

    current_layer = expansion_current.get("official_public_structured_normalization_expansion", {})
    if current_layer.get("state") != "PASS_SCOPED_EXPANSION_V1":
        errors.append("Current rules structured normalization expansion state drifted")
    if current_layer.get("core_rules_structure", {}).get("rule_reference_families") != 24:
        errors.append("Current rules Core structure family count drifted")
    if current_layer.get("residual_classification", {}).get("no_exact_total") != 7936:
        errors.append("Current rules residual no-exact count drifted")
    if current_layer.get("current_normalized_factions_change") != 0:
        errors.append("Structured normalization expansion must not change faction coverage")
    core_current = expansion_current.get("source_currentness", {}).get("core_rules_content", {})
    if core_current.get("state") != "OFFICIAL_PUBLIC_PARAGRAPH_SEMANTIC_REVIEW_V1":
        errors.append("Core Rules currentness state did not advance to section structure v1")
    if core_current.get("normative_structured_normalization") != "PARAGRAPH_SEMANTIC_REVIEW_COMPLETE_AST_READINESS_PENDING":
        errors.append("Core Rules structured normalization boundary drifted")

    expansion_profile = expansion_gate.get("scope_profiles", {}).get("official_public_structured_normalization_expansion", {})
    if expansion_profile.get("content_state") != "PASS_SCOPED_EXPANSION_V1":
        errors.append("Currentness gate structured expansion profile must PASS")
    if expansion_profile.get("core_rule_reference_families") != 24:
        errors.append("Currentness gate Core family count drifted")
    if expansion_profile.get("promoted_units") != 0 or expansion_profile.get("semantic_conflicts_created") != 0:
        errors.append("Currentness gate residual classification must remain non-promoting/non-conflicting")

    expansion_global = expansion_cov.get("global", {})
    if expansion_cov.get("status") != "CORE_RULE_PARAGRAPH_SEMANTIC_REVIEW_V1_COMPLETE":
        errors.append("Coverage status did not advance after structured normalization expansion")
    if expansion_global.get("official_public_core_rule_reference_families") != 24:
        errors.append("Coverage Core family count drifted")
    if expansion_global.get("official_public_core_rule_reference_count") != 141:
        errors.append("Coverage Core rule-reference count drifted")
    if expansion_global.get("official_public_unscoped_exact_total") != 1566:
        errors.append("Coverage unscoped exact total drifted")
    if expansion_global.get("official_public_no_exact_total") != 7936:
        errors.append("Coverage no-exact total drifted")
    if expansion_global.get("official_public_residual_promoted_units") != 0:
        errors.append("Coverage residual promotion count must remain zero")
    if expansion_global.get("official_public_residual_semantic_conflicts_created") != 0:
        errors.append("Coverage residual semantic conflicts must remain zero")
    if expansion_global.get("current_normalized_factions") != 0:
        errors.append("Structured normalization expansion must preserve current_normalized_factions=0")
    if expansion_global.get("full_normative_semantic_factions") != 0:
        errors.append("Structured normalization expansion must preserve full_normative_semantic_factions=0")

    forbidden_structured_text_keys = {"text", "description", "rules_text", "official_text", "mirror_text", "page_text", "prose"}
    def _check_structured_no_long_text(value, path="root"):
        if isinstance(value, dict):
            for key, child in value.items():
                if key in forbidden_structured_text_keys:
                    errors.append(f"Structured normalization vendored forbidden long-text field: {path}.{key}")
                    continue
                _check_structured_no_long_text(child, f"{path}.{key}")
        elif isinstance(value, list):
            for idx, child in enumerate(value):
                _check_structured_no_long_text(child, f"{path}[{idx}]")
    _check_structured_no_long_text(core_structure_snapshot)
    _check_structured_no_long_text(residual_snapshot)

    required_expansion_files = [
        ROOT / "docs" / "OFFICIAL_CORE_RULES_STRUCTURE_MODEL.md",
        ROOT / "docs" / "OFFICIAL_PUBLIC_OVERLAP_RESIDUAL_MODEL.md",
        ROOT / "schemas" / "core_rules_structure_snapshot.schema.json",
        ROOT / "schemas" / "public_overlap_residual_classification.schema.json",
        ROOT / "tools" / "build_core_rules_structure.py",
        ROOT / "tools" / "classify_public_overlap_residuals.py",
        ROOT / "tests" / "test_core_rules_structure.py",
        ROOT / "tests" / "test_public_overlap_residual_classification.py",
        ROOT / ".github" / "workflows" / "core-rules-structured-normalization.yml",
        ROOT / ".github" / "workflows" / "public-overlap-residual-classification.yml",
    ]
    for path in required_expansion_files:
        if not path.exists():
            errors.append(f"Missing structured normalization expansion artifact: {path.relative_to(ROOT)}")
except Exception as exc:
    errors.append(f"Official-public structured normalization expansion validation failure: {exc}")


# 4. Custodes legacy normalized inventory invariants.
custodes_path = (
    ROOT
    / "collection"
    / "adeptus_custodes"
    / "legacy"
    / "v0_5_provisional"
    / "collection_adeptus_custodes_v0_5_provisional.json"
)
try:
    inv = json.loads(custodes_path.read_text(encoding="utf-8"))
    scope = inv["scope"]
    if scope["confirmed_physical_models_including_shared_agents"] != 75:
        errors.append("Custodes total including shared agents must remain 75 in v0.5 baseline")
    if scope["custodes_and_sisters_physical_models_excluding_shared_agents"] != 70:
        errors.append("Custodes/Sisters total excluding shared agents must remain 70 in v0.5 baseline")
    if scope["shared_imperial_agents"] != 5:
        errors.append("Shared Imperial Agents total must remain 5 in v0.5 baseline")
    pool_ids = {x["pool_id"] for x in inv.get("physical_pools", [])}
    for pool in {"CUSTODES_SISTERS_01", "CUSTODES_TELEMON_01", "CUSTODES_WARDENS_01"}:
        if pool not in pool_ids:
            errors.append(f"Missing critical Custodes physical pool: {pool}")
    sisters = next(x for x in inv["physical_pools"] if x["pool_id"] == "CUSTODES_SISTERS_01")
    if sisters.get("current_body_states") != {"built_models": 0, "on_sprue_bodies": 10}:
        errors.append("Custodes v0.5 Sisters body-state correction was lost")
except Exception as exc:
    errors.append(f"Custodes baseline validation failure: {exc}")

# 5. Legacy semantic-core index and Custodes historical rules snapshot.
try:
    semantic_index = json.loads(
        (ROOT / "legacy" / "rules_assistant_v0_9" / "SEMANTIC_CORE_FILE_INDEX.json").read_text(encoding="utf-8")
    )
    if semantic_index.get("selected_semantic_core_files") != 69:
        errors.append("Expected 69 indexed legacy semantic-core files")
    if semantic_index.get("total_uncompressed_bytes") != 959003:
        errors.append("Unexpected legacy semantic-core byte count")

    points = json.loads(
        (ROOT / "legacy" / "rules_assistant_v0_9" / "factions" / "adeptus_custodes" / "mfm_v1_2_points.json").read_text(encoding="utf-8")
    )
    detachments = json.loads(
        (ROOT / "legacy" / "rules_assistant_v0_9" / "factions" / "adeptus_custodes" / "mfm_v1_2_detachments.json").read_text(encoding="utf-8")
    )
    leader_graph = json.loads(
        (ROOT / "legacy" / "rules_assistant_v0_9" / "factions" / "adeptus_custodes" / "leader_support_graph_v1_2.json").read_text(encoding="utf-8")
    )
    if len(points.get("units", [])) != 31:
        errors.append(f"Expected 31 Custodes historical point entries, got {len(points.get('units', []))}")
    if len(detachments.get("detachments", [])) != 9:
        errors.append(f"Expected 9 Custodes historical detachments, got {len(detachments.get('detachments', []))}")
    if len(leader_graph.get("links", [])) != 8:
        errors.append(f"Expected 8 Custodes historical Leader links, got {len(leader_graph.get('links', []))}")
except Exception as exc:
    errors.append(f"Custodes historical rules snapshot failure: {exc}")

# 6. Historical collection repricing regression:
# v0.5 roster Custodes rows = 4000 old points; MFM 1.2 repricing = 3970.
try:
    points_by_name = {u["name_en"]: u for u in points["units"]}
    copies: collections.Counter[str] = collections.Counter()
    historical_custodes = 0
    repriced_custodes = 0
    for row in inv["roster_snapshot"]:
        name = row["unit"]
        if name not in points_by_name:
            continue
        historical_custodes += int(row["points_snapshot"])
        copies[name] += 1
        unit = points_by_name[name]
        band = next(
            b
            for b in unit["cost_bands"]
            if copies[name] >= b["min_copy"] and (b["max_copy"] is None or copies[name] <= b["max_copy"])
        )
        repriced_custodes += int(band["sizes"][str(row["displayed_models"])])
    if historical_custodes != 4000:
        errors.append(f"Expected historical Custodes roster subtotal 4000, got {historical_custodes}")
    if repriced_custodes != 3970:
        errors.append(f"Expected MFM v1.2 repriced Custodes subtotal 3970, got {repriced_custodes}")
except Exception as exc:
    errors.append(f"Custodes historical repricing regression failure: {exc}")


# 7. Exact preserved bootstrap artifact integrity.
artifact_expectations = {
    "legacy/artifacts/original/W40K_11E_RULES_ASSISTANT_v0_9_FULL_FACTION_SEMANTICS_20260815.zip": (
        883437,
        "98bbc892879e9211fadaff158efbd98321b704e0c56e6dd84df2ef69e9b00947",
    ),
    "legacy/artifacts/original/W40K_COLLECTION_INVENTORY_v0_5_ADEPTUS_CUSTODES_PROVISIONAL.zip": (
        32347,
        "6aee2f7bf491f4fe6f254aeecf79dffe84a5579e24a3022aafcea422b9e97f20",
    ),
}
for rel, (expected_size, expected_sha256) in artifact_expectations.items():
    path = ROOT / rel
    if not path.exists():
        errors.append(f"Missing preserved artifact: {rel}")
        continue
    raw = path.read_bytes()
    if len(raw) != expected_size:
        errors.append(f"Preserved artifact size mismatch {rel}: {len(raw)} != {expected_size}")
    got = hashlib.sha256(raw).hexdigest()
    if got != expected_sha256:
        errors.append(f"Preserved artifact SHA-256 mismatch {rel}: {got} != {expected_sha256}")

if errors:
    print("FAIL")
    for error in errors:
        print("-", error)
    sys.exit(1)

print(
    "PASS: repository JSON, baselines, source statuses, Custodes collection, "
    "semantic-core index, external/analytics source contracts, roster evidence model, painting KB, current MFM Wave A, Wave B structural coverage, official-public exact overlap, and historical repricing invariants validated."
)
