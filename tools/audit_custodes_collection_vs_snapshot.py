#!/usr/bin/env python3
from __future__ import annotations

import collections
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

INV = ROOT / "collection" / "adeptus_custodes" / "legacy" / "v0_5_provisional" / "collection_adeptus_custodes_v0_5_provisional.json"
PTS = ROOT / "legacy" / "rules_assistant_v0_9" / "factions" / "adeptus_custodes" / "mfm_v1_2_points.json"


def unit_cost(unit: dict, model_count: int, copy_number: int) -> int:
    band = next(
        b for b in unit["cost_bands"]
        if copy_number >= b["min_copy"] and (b["max_copy"] is None or copy_number <= b["max_copy"])
    )
    return int(band["sizes"][str(model_count)])


def main() -> int:
    inv = json.loads(INV.read_text(encoding="utf-8"))
    pts = json.loads(PTS.read_text(encoding="utf-8"))

    units = {u["name_en"]: u for u in pts["units"]}
    copies: collections.Counter[str] = collections.Counter()

    historical_full = 0
    historical_custodes = 0
    repriced_custodes = 0
    external = []
    deltas = []

    for row in inv["roster_snapshot"]:
        name = row["unit"]
        models = int(row["displayed_models"])
        historical = int(row["points_snapshot"])
        historical_full += historical

        if name not in units:
            external.append({"unit": name, "historical_points": historical})
            continue

        historical_custodes += historical
        copies[name] += 1
        current_for_snapshot = unit_cost(units[name], models, copies[name])
        repriced_custodes += current_for_snapshot

        if current_for_snapshot != historical:
            deltas.append({
                "unit": name,
                "models": models,
                "copy": copies[name],
                "old_points": historical,
                "mfm_v1_2_points": current_for_snapshot,
                "delta": current_for_snapshot - historical,
            })

    result = {
        "inventory_checkpoint": inv["created"],
        "points_checkpoint": pts["source"]["checked_at"],
        "historical_full_roster_points": historical_full,
        "historical_custodes_scope_points": historical_custodes,
        "repriced_custodes_scope_points_mfm_v1_2": repriced_custodes,
        "delta_custodes_scope": repriced_custodes - historical_custodes,
        "out_of_scope_historical_points": sum(x["historical_points"] for x in external),
        "out_of_scope_units": external,
        "changed_rows": deltas,
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))

    expected = {
        "historical_full_roster_points": 4485,
        "historical_custodes_scope_points": 4000,
        "repriced_custodes_scope_points_mfm_v1_2": 3970,
    }
    for key, value in expected.items():
        if result[key] != value:
            raise SystemExit(f"FAIL: {key}={result[key]} expected {value}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
