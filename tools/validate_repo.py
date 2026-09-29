#!/usr/bin/env python3
from __future__ import annotations

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
    for src in registry.get("sources", []):
        if src.get("status") not in VALID_STATUSES:
            errors.append(f"Invalid source status {src.get('id')}: {src.get('status')}")
except Exception as exc:
    errors.append(f"Source registry failure: {exc}")

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

if errors:
    print("FAIL")
    for error in errors:
        print("-", error)
    sys.exit(1)

print("PASS: repository JSON, baseline registry, source statuses and Custodes bootstrap invariants validated.")
