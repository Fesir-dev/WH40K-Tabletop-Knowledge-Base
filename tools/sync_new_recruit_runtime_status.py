#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "NEW_RECRUIT_RUNTIME_VALIDATION_CURRENT.json"
CURRENT = ROOT / "rules" / "11e" / "current.json"

def main() -> int:
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    if report.get("schema_version") != "2.0":
        raise SystemExit("New Recruit runtime report schema must be 2.0")
    if report.get("status") not in {"PASS", "PASS_WITH_KNOWN_RUNTIME_DRIFT"}:
        raise SystemExit(f"Cannot sync unresolved runtime state: {report.get('status')}")
    points = report.get("representative_points", {})
    surfaces = report.get("representative_surfaces", {})
    if int(points.get("new_drift_count", 0)) or int(surfaces.get("new_drift_count", 0)):
        raise SystemExit("Cannot sync runtime state with unclassified drift")

    current = json.loads(CURRENT.read_text(encoding="utf-8"))
    nr = current.setdefault("automation", {}).setdefault("new_recruit_runtime", {})
    known = points.get("known_drifts", []) + surfaces.get("known_drifts", [])
    nr.update({
        "state": report["status"],
        "report": "reports/NEW_RECRUIT_RUNTIME_VALIDATION_CURRENT.json",
        "roster_identities_resolved": report.get("universe", {}).get("resolved_runtime_identities"),
        "representative_point_checks": points.get("checks"),
        "representative_point_matches": points.get("matched"),
        "known_point_drifts": points.get("known_drift_count"),
        "representative_surface_checks": surfaces.get("checks"),
        "representative_surface_matches": surfaces.get("matched"),
        "known_surface_drifts": surfaces.get("known_drift_count"),
        "known_runtime_drifts": int(points.get("known_drift_count", 0)) + int(surfaces.get("known_drift_count", 0)),
        "new_runtime_drifts": int(points.get("new_drift_count", 0)) + int(surfaces.get("new_drift_count", 0)),
        "active_known_drift_ids": [x.get("known_drift_id") for x in known if x.get("known_drift_id")],
        "exact_sync_cadence": report.get("lineage", {}).get("exact_sync_cadence"),
        "authority_rule": "Runtime mismatch never automatically changes normative Games Workshop/MFM data.",
    })
    CURRENT.write_text(json.dumps(current, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": nr["state"], "known_runtime_drifts": nr["known_runtime_drifts"], "new_runtime_drifts": nr["new_runtime_drifts"]}))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
