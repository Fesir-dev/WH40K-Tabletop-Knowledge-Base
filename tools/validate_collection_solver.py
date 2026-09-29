#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
from pathlib import Path

from solve_collection_roster import ROOT, solve_request

CASES = [
    ("custodes_feasible_ready.json", "SCOPED_RULES_PASS_PHYSICAL_FEASIBLE", "FEASIBLE_PROVISIONAL"),
    ("custodes_build_required.json", "SCOPED_RULES_PASS_PHYSICAL_FEASIBLE", "FEASIBLE_WITH_BUILD_PROVISIONAL"),
    ("custodes_conversion.json", "SCOPED_RULES_PASS_PHYSICAL_FEASIBLE", "FEASIBLE_WITH_CONVERSION_PROVISIONAL"),
    ("custodes_body_conflict.json", "SCOPED_RULES_PASS_PHYSICAL_INFEASIBLE", "INFEASIBLE_FROM_SNAPSHOT"),
    ("custodes_component_conflict.json", "SCOPED_RULES_PASS_PHYSICAL_INFEASIBLE", "INFEASIBLE_FROM_SNAPSHOT"),
    ("custodes_unknown_venatari_lance.json", "SCOPED_RULES_PASS_PHYSICAL_UNKNOWN", "UNKNOWN_COMPONENT_FEASIBILITY"),
]


def main() -> int:
    rows = []
    for filename, expected_status, expected_physical in CASES:
        path = ROOT / "rosters" / "examples" / filename
        request = json.loads(path.read_text(encoding="utf-8"))
        result = solve_request(request)
        if result["status"] != expected_status:
            raise SystemExit(f"FAIL {filename}: status={result['status']} expected={expected_status}")
        if result["physical"]["state"] != expected_physical:
            raise SystemExit(f"FAIL {filename}: physical={result['physical']['state']} expected={expected_physical}")
        if result["rules"]["scoped_legality"] != "PASS":
            raise SystemExit(f"FAIL {filename}: scoped legality must PASS")
        if result["rules"]["full_normative_legality"] != "UNKNOWN_PENDING_NORMATIVE_APP":
            raise SystemExit(f"FAIL {filename}: full normative boundary changed")
        rows.append({
            "case": filename,
            "status": result["status"],
            "physical": result["physical"]["state"],
            "points": result["points"]["total"],
        })

    conversion_path = ROOT / "rosters" / "examples" / "custodes_conversion.json"
    request = json.loads(conversion_path.read_text(encoding="utf-8"))
    no_conversion = copy.deepcopy(request)
    no_conversion["roster_id"] = "custodes_conversion_disabled"
    no_conversion["options"] = {"allow_conversion": False}
    result = solve_request(no_conversion)
    if result["physical"]["state"] != "INFEASIBLE_FROM_SNAPSHOT":
        raise SystemExit("FAIL conversion-disabled: expected body deficit without Sagittarum conversion")
    rows.append({
        "case": "custodes_conversion_disabled",
        "status": result["status"],
        "physical": result["physical"]["state"],
        "points": result["points"]["total"],
    })

    report = {
        "schema_version": "1.0",
        "status": "PASS",
        "milestone": "COLLECTION_AWARE_ROSTER_SOLVER",
        "faction": "Adeptus Custodes",
        "rules_snapshot": "MFM 1.4 / 2026-09-02",
        "collection_snapshot": "v0.5-provisional-r2 / 2026-07-11",
        "cases": rows,
        "coverage": {
            "mfm_unit_existence": True,
            "mfm_unit_size_and_copy_tier_points": True,
            "mfm_detachment_existence": True,
            "mfm_enhancement_costs": True,
            "mfm_paid_wargear_costs": True,
            "mfm_leader_relations_when_declared": True,
            "physical_shared_body_allocation": True,
            "ready_vs_build_required_bodies": True,
            "conversion_gating": True,
            "declared_component_capacities": True,
            "unknown_component_fail_closed": True,
            "full_normative_army_legality": False,
            "automatic_free_wargear_wysiwyg_inference": False,
        },
        "authority_boundary": {
            "full_normative_legality": "UNKNOWN_PENDING_NORMATIVE_APP",
            "collection_status": "PROVISIONAL",
            "normative_promotion": False,
        },
    }
    out = ROOT / "reports" / "COLLECTION_AWARE_ROSTER_SOLVER_CURRENT.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "cases": len(rows)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
