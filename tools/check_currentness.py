#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
gate = json.loads((ROOT / "sources" / "currentness_gate.json").read_text(encoding="utf-8"))
coverage = json.loads((ROOT / "coverage" / "current.json").read_text(encoding="utf-8"))
release = json.loads((ROOT / "sources" / "release_state.json").read_text(encoding="utf-8"))

parser = argparse.ArgumentParser(description="Check scoped 11E currentness and repository coverage.")
parser.add_argument("--scope", default="full_normative_faction", choices=sorted(gate["scope_profiles"]))
parser.add_argument("--faction")
parser.add_argument("--require-coverage", action="store_true")
parser.add_argument("--json", action="store_true", dest="as_json")
args = parser.parse_args()

source_by_id = {x["id"]: x for x in gate["required_checks"]}
profiles = gate["scope_profiles"]

def eval_profile(name: str, seen=None):
    seen = set() if seen is None else seen
    if name in seen:
        return False, [f"profile cycle: {name}"]
    seen.add(name)
    p = profiles[name]
    reasons = []
    ok = p.get("content_state") == "PASS"
    if not ok:
        reasons.append(f"{name}.content_state={p.get('content_state')}")
    for sid in p.get("required_sources", []):
        state = source_by_id.get(sid, {}).get("state", "MISSING")
        if state != "PASS":
            ok = False
            reasons.append(f"{sid}={state}")
    for child in p.get("required_profiles", []):
        child_ok, child_reasons = eval_profile(child, seen.copy())
        if not child_ok:
            ok = False
            reasons.extend(child_reasons)
    return ok, reasons

ok, reasons = eval_profile(args.scope)
coverage_value = None
if args.faction:
    rows = {x["slug"]: x for x in coverage["factions"]}
    if args.faction not in rows:
        ok = False
        reasons.append(f"unknown faction: {args.faction}")
    else:
        dim = profiles[args.scope].get("repository_dimension")
        if dim:
            coverage_value = rows[args.faction]["coverage"].get(dim, 0)
            if args.require_coverage and coverage_value < 100:
                ok = False
                reasons.append(f"{args.faction}.{dim}.coverage={coverage_value}%")
        elif args.require_coverage and not rows[args.faction].get("current_normalized"):
            ok = False
            reasons.append(f"{args.faction}.current_normalized=false")

warnings = []
if args.faction:
    for tr in release["transitions"]:
        if args.faction in tr.get("factions", []) and tr.get("upcoming_state"):
            warnings.append(f"{tr['id']}: {tr['upcoming_state']} (current legal data remains separate)")

out = {
    "scope": args.scope,
    "faction": args.faction,
    "source_current": ok if not args.require_coverage else None,
    "result": "PASS" if ok else "PENDING",
    "reasons": reasons,
    "coverage": coverage_value,
    "warnings": warnings,
}
if args.as_json:
    print(json.dumps(out, ensure_ascii=False, indent=2))
else:
    print(out["result"])
    print(f"scope: {args.scope}")
    if args.faction:
        print(f"faction: {args.faction}")
    for reason in reasons:
        print("-", reason)
    for warning in warnings:
        print("WARNING:", warning)
raise SystemExit(0 if ok else 2)
