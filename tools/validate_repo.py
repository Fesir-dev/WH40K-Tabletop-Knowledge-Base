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
        (ROOT / "reports" / "NORMATIVE_APP_EQUIVALENCE_GAP_AUDIT_CURRENT.json").read_text(encoding="utf-8")
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
    if cov.get("status") != "WAVE_B_SEMANTIC_FAQ_OPERATIONAL_COMPLETE":
        errors.append("coverage/current.json must retain WAVE_B_SEMANTIC_FAQ_OPERATIONAL_COMPLETE")
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
    if current_rules.get("next_milestone") != "NORMATIVE_APP_EQUIVALENCE_GAP_AUDIT":
        errors.append("Current milestone must be NORMATIVE_APP_EQUIVALENCE_GAP_AUDIT")
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
    "semantic-core index, external/analytics source contracts, roster evidence model, painting KB, current MFM Wave A, Wave B structural coverage, and historical repricing invariants validated."
)
