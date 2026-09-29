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
    if by_source_id.get("GOONHAMMER_40K", {}).get("source_role") != "analysis":
        errors.append("Goonhammer must remain in the analysis source role")
    for analytics_id in {"STAT_CHECK_40K", "BCP_40K"}:
        if by_source_id.get(analytics_id, {}).get("source_role") != "analytics":
            errors.append(f"{analytics_id} must remain in the analytics source role")
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
    "semantic-core index, external source contracts, and historical repricing invariants validated."
)
