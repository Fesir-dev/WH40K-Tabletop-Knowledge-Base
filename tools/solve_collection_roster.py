#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MFM = ROOT / "rules" / "11e" / "snapshots" / "2026-09-29" / "mfm" / "factions" / "adeptus-custodes.json"
DEFAULT_PROFILE = ROOT / "collection" / "adeptus_custodes" / "solver_profile.json"


def norm(value: str | None) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    return " ".join(re.sub(r"[^a-z0-9]+", " ", value.casefold()).split())


def parse_copy_range(value: str) -> tuple[int, int | None]:
    value = value.strip()
    m = re.fullmatch(r"\[(\d+),(\d+)\]", value)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = re.fullmatch(r"\[(\d+),\)", value)
    if m:
        return int(m.group(1)), None
    raise ValueError(f"Unsupported MFM range: {value}")


def copy_band(unit: dict, copy_number: int) -> dict | None:
    for band in unit.get("pricing", []):
        lo, hi = parse_copy_range(band["range"])
        if copy_number >= lo and (hi is None or copy_number <= hi):
            return band
    return None


def unit_points(unit: dict, model_count: int, copy_number: int) -> int | None:
    band = copy_band(unit, copy_number)
    if not band:
        return None
    for row in band.get("costs", []):
        if int(row.get("models", -1)) == model_count:
            return int(row["points"])
    return None


class MinCostFlow:
    def __init__(self):
        self.index: dict[str, int] = {}
        self.names: list[str] = []
        self.g: list[list[dict]] = []

    def node(self, name: str) -> int:
        if name not in self.index:
            self.index[name] = len(self.names)
            self.names.append(name)
            self.g.append([])
        return self.index[name]

    def add_edge(self, a: str, b: str, cap: int, cost: int, meta: dict | None = None) -> dict:
        u, v = self.node(a), self.node(b)
        fwd = {"to": v, "rev": len(self.g[v]), "cap": int(cap), "orig": int(cap), "cost": int(cost), "meta": meta}
        rev = {"to": u, "rev": len(self.g[u]), "cap": 0, "orig": 0, "cost": -int(cost), "meta": None}
        self.g[u].append(fwd)
        self.g[v].append(rev)
        return fwd

    def solve(self, source: str, sink: str, target: int) -> tuple[int, int]:
        s, t = self.node(source), self.node(sink)
        flow = cost = 0
        n = len(self.names)
        while flow < target:
            dist = [10**18] * n
            prev: list[tuple[int, int] | None] = [None] * n
            inq = [False] * n
            dist[s] = 0
            q = [s]
            inq[s] = True
            qi = 0
            # SPFA is sufficient for this small allocation graph and handles reverse negative edges.
            while qi < len(q):
                u = q[qi]
                qi += 1
                inq[u] = False
                for ei, e in enumerate(self.g[u]):
                    if e["cap"] <= 0:
                        continue
                    nd = dist[u] + e["cost"]
                    if nd < dist[e["to"]]:
                        dist[e["to"]] = nd
                        prev[e["to"]] = (u, ei)
                        if not inq[e["to"]]:
                            q.append(e["to"])
                            inq[e["to"]] = True
            if prev[t] is None:
                break
            add = target - flow
            v = t
            while v != s:
                u, ei = prev[v]
                add = min(add, self.g[u][ei]["cap"])
                v = u
            v = t
            while v != s:
                u, ei = prev[v]
                e = self.g[u][ei]
                e["cap"] -= add
                self.g[v][e["rev"]]["cap"] += add
                cost += add * e["cost"]
                v = u
            flow += add
        return flow, cost


def resolve_unique(mapping: dict[str, list[dict]], value: str) -> dict | None:
    hits = mapping.get(norm(value), [])
    return hits[0] if len(hits) == 1 else None


def evaluate_physical(request: dict, expanded_units: list[dict], profile: dict) -> dict:
    options = request.get("options", {})
    allow_conversion = bool(options.get("allow_conversion", profile.get("policy", {}).get("allow_conversion_default", False)))

    demand = Counter()
    for row in expanded_units:
        if row.get("canonical_unit") and row.get("models"):
            demand[row["canonical_unit"]] += int(row["models"])

    modeled_units = {
        role["unit"]
        for pool in profile.get("body_pools", [])
        for role in pool.get("roles", [])
    }
    unmodeled = [
        {"unit": unit, "models": count, "reason": "NO_COLLECTION_BODY_MAPPING"}
        for unit, count in sorted(demand.items())
        if unit not in modeled_units
    ]

    graph = MinCostFlow()
    allocation_edges: list[dict] = []
    unit_sink_edges: dict[str, dict] = {}
    for pool in profile.get("body_pools", []):
        pid = pool["pool_id"]
        ready = int(pool.get("ready_bodies", 0))
        build = int(pool.get("buildable_bodies", 0))
        segments = []
        if ready:
            seg = f"segment:{pid}:ready"
            graph.add_edge("SOURCE", seg, ready, 0)
            segments.append((seg, "READY"))
        if build:
            seg = f"segment:{pid}:build"
            graph.add_edge("SOURCE", seg, build, 10)
            segments.append((seg, "BUILD_REQUIRED"))

        for role in pool.get("roles", []):
            unit = role["unit"]
            if unit not in demand:
                continue
            mode = role.get("mode", "DIRECT")
            if mode == "CONVERSION_REQUIRED" and not allow_conversion:
                continue
            gate = f"role:{pid}:{unit}"
            role_cap = int(role.get("max_from_pool", pool.get("physical_bodies", 0)))
            graph.add_edge(gate, f"unit:{unit}", role_cap, 0)
            for seg, readiness in segments:
                meta = {
                    "pool_id": pid,
                    "unit": unit,
                    "readiness": readiness,
                    "mode": mode,
                }
                edge = graph.add_edge(
                    seg,
                    gate,
                    int(pool.get("physical_bodies", 0)),
                    100 if mode == "CONVERSION_REQUIRED" else 0,
                    meta=meta,
                )
                allocation_edges.append(edge)

    total_modeled_demand = 0
    for unit, count in demand.items():
        if unit not in modeled_units:
            continue
        edge = graph.add_edge(f"unit:{unit}", "SINK", int(count), 0)
        unit_sink_edges[unit] = edge
        total_modeled_demand += int(count)

    graph.solve("SOURCE", "SINK", total_modeled_demand)

    allocations = []
    assembly_required = 0
    conversion_required = 0
    for edge in allocation_edges:
        used = edge["orig"] - edge["cap"]
        if not used:
            continue
        row = dict(edge["meta"])
        row["bodies"] = used
        allocations.append(row)
        if row["readiness"] == "BUILD_REQUIRED":
            assembly_required += used
        if row["mode"] == "CONVERSION_REQUIRED":
            conversion_required += used

    body_deficits = []
    for unit, count in demand.items():
        if unit not in modeled_units:
            continue
        edge = unit_sink_edges[unit]
        supplied = edge["orig"] - edge["cap"]
        if supplied < count:
            body_deficits.append({
                "unit": unit,
                "required": count,
                "allocated": supplied,
                "deficit": count - supplied,
            })

    component_demand = Counter()
    for row in expanded_units:
        for component_id, count in (row.get("components") or {}).items():
            component_demand[component_id] += int(count)

    component_caps = {x["component_id"]: int(x["capacity"]) for x in profile.get("component_pools", [])}
    component_rows = []
    component_deficits = []
    unknown_components = []
    for cid, required in sorted(component_demand.items()):
        cap = component_caps.get(cid)
        if cap is None:
            component_rows.append({
                "component_id": cid,
                "required": required,
                "capacity": None,
                "status": "UNKNOWN_COMPONENT",
            })
            unknown_components.append({
                "component_id": cid,
                "required": required,
                "reason": "Component is not normalized in the solver profile.",
            })
        else:
            ok = required <= cap
            component_rows.append({
                "component_id": cid,
                "required": required,
                "capacity": cap,
                "status": "PASS" if ok else "FAIL",
            })
            if not ok:
                component_deficits.append({
                    "component_id": cid,
                    "required": required,
                    "capacity": cap,
                    "deficit": required - cap,
                })

    unknown_constraints = []
    unknown_defs = {x["id"]: x for x in profile.get("unknown_constraints", [])}
    support = {
        (norm(x["unit"]), norm(x["item"])): x
        for x in profile.get("paid_wargear_physical_support", [])
    }
    for row in expanded_units:
        for wg in row.get("paid_wargear", []):
            rec = support.get((norm(row["canonical_unit"]), norm(wg.get("item"))))
            if rec and str(rec.get("status", "")).startswith("UNKNOWN"):
                unknown = unknown_defs.get(rec.get("constraint_id"), {"id": rec.get("constraint_id")})
                unknown_constraints.append({
                    "constraint_id": rec.get("constraint_id"),
                    "unit": row["canonical_unit"],
                    "item": wg.get("item"),
                    "reason": unknown.get("reason"),
                })
    for cid in component_demand:
        for unknown in profile.get("unknown_constraints", []):
            if unknown.get("trigger", {}).get("component_id") == cid:
                unknown_constraints.append({
                    "constraint_id": unknown["id"],
                    "component_id": cid,
                    "reason": unknown.get("reason"),
                })

    if unmodeled or body_deficits or component_deficits:
        state = "INFEASIBLE_FROM_SNAPSHOT"
    elif unknown_components or unknown_constraints:
        state = "UNKNOWN_COMPONENT_FEASIBILITY"
    elif assembly_required and conversion_required:
        state = "FEASIBLE_WITH_BUILD_AND_CONVERSION_PROVISIONAL"
    elif assembly_required:
        state = "FEASIBLE_WITH_BUILD_PROVISIONAL"
    elif conversion_required:
        state = "FEASIBLE_WITH_CONVERSION_PROVISIONAL"
    else:
        state = "FEASIBLE_PROVISIONAL"

    return {
        "state": state,
        "collection_status": profile.get("collection_status"),
        "allow_conversion": allow_conversion,
        "body_demand": dict(sorted(demand.items())),
        "allocations": allocations,
        "body_deficits": body_deficits,
        "unmodeled_units": unmodeled,
        "assembly_required_bodies": assembly_required,
        "conversion_required_bodies": conversion_required,
        "component_checks": component_rows,
        "component_deficits": component_deficits,
        "unknown_components": unknown_components,
        "unknown_constraints": unknown_constraints,
        "loadout_scope": "DECLARED_COMPONENTS_AND_PAID_WARGEAR_ONLY",
        "normative_promotion": False,
    }


def solve_request(request: dict, root: Path = ROOT) -> dict:
    mfm_path = root / request.get("rules_snapshot", str(DEFAULT_MFM.relative_to(ROOT)))
    profile_path = root / request.get("collection_profile", str(DEFAULT_PROFILE.relative_to(ROOT)))
    current_rules_path = root / "rules" / "11e" / "current.json"

    mfm = json.loads(mfm_path.read_text(encoding="utf-8"))
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    current_rules = json.loads(current_rules_path.read_text(encoding="utf-8")) if current_rules_path.exists() else {}

    unit_map: dict[str, list[dict]] = defaultdict(list)
    for unit in mfm.get("units", []):
        unit_map[norm(unit["name"])].append(unit)
    det_map: dict[str, list[dict]] = defaultdict(list)
    for det in mfm.get("detachments", []):
        det_map[norm(det["name"])].append(det)

    checks = []
    expanded = []
    copy_counts = Counter()
    seen_ids = set()

    detachment = resolve_unique(det_map, request.get("detachment", ""))
    if not detachment:
        checks.append({"check": "detachment_exists", "status": "FAIL", "value": request.get("detachment")})
    else:
        checks.append({
            "check": "detachment_exists",
            "status": "PASS",
            "canonical": detachment["name"],
            "detachment_points": detachment.get("dp"),
        })

    for raw in request.get("units", []):
        rid = raw.get("id")
        if not rid or rid in seen_ids:
            checks.append({"check": "unique_unit_id", "status": "FAIL", "id": rid})
            continue
        seen_ids.add(rid)
        unit = resolve_unique(unit_map, raw.get("unit", ""))
        if not unit:
            checks.append({"check": "unit_exists", "status": "FAIL", "id": rid, "unit": raw.get("unit")})
            expanded.append({**raw, "canonical_unit": None, "points": None})
            continue

        copy_counts[unit["name"]] += 1
        copy_no = copy_counts[unit["name"]]
        models = int(raw.get("models", 0))
        base = unit_points(unit, models, copy_no)
        if base is None:
            checks.append({
                "check": "unit_size_and_copy_tier",
                "status": "FAIL",
                "id": rid,
                "unit": unit["name"],
                "models": models,
                "copy_number": copy_no,
            })
        else:
            checks.append({
                "check": "unit_size_and_copy_tier",
                "status": "PASS",
                "id": rid,
                "unit": unit["name"],
                "models": models,
                "copy_number": copy_no,
                "base_points": base,
            })

        paid = 0
        paid_rows = []
        paid_catalog = {norm(x["item"]): x for x in unit.get("wargear", [])}
        for wg in raw.get("paid_wargear", []):
            item = paid_catalog.get(norm(wg.get("item")))
            qty = int(wg.get("quantity", 1))
            if not item:
                checks.append({
                    "check": "paid_wargear_cost",
                    "status": "FAIL",
                    "id": rid,
                    "unit": unit["name"],
                    "item": wg.get("item"),
                })
                paid_rows.append({
                    "item": wg.get("item"),
                    "quantity": qty,
                    "points_each": None,
                    "points": None,
                })
            else:
                cost = int(item["points"]) * qty
                paid += cost
                checks.append({
                    "check": "paid_wargear_cost",
                    "status": "PASS",
                    "id": rid,
                    "unit": unit["name"],
                    "item": item["item"],
                    "quantity": qty,
                    "points": cost,
                })
                paid_rows.append({
                    "item": item["item"],
                    "quantity": qty,
                    "points_each": int(item["points"]),
                    "points": cost,
                })

        expanded.append({
            **raw,
            "canonical_unit": unit["name"],
            "copy_number": copy_no,
            "base_points": base,
            "paid_wargear_points": paid,
            "points": None if base is None else base + paid,
            "paid_wargear": paid_rows,
        })

    enhancement_total = 0
    enhancement_rows = []
    det_enh = {norm(x["name"]): x for x in (detachment or {}).get("enhancements", [])}
    for enh in request.get("enhancements", []):
        item = det_enh.get(norm(enh.get("name")))
        if not item:
            checks.append({
                "check": "enhancement_exists_in_detachment",
                "status": "FAIL",
                "name": enh.get("name"),
            })
            enhancement_rows.append({"name": enh.get("name"), "points": None, "status": "FAIL"})
        else:
            pts = int(item.get("points", 0))
            enhancement_total += pts
            checks.append({
                "check": "enhancement_exists_in_detachment",
                "status": "PASS",
                "name": item["name"],
                "points": pts,
            })
            enhancement_rows.append({"name": item["name"], "points": pts, "status": "PASS"})

    by_id = {x.get("id"): x for x in expanded if x.get("id")}
    for att in request.get("attachments", []):
        leader = by_id.get(att.get("leader_ref"))
        body = by_id.get(att.get("bodyguard_ref"))
        if not leader or not body or not leader.get("canonical_unit") or not body.get("canonical_unit"):
            checks.append({"check": "leader_relation", "status": "FAIL", **att, "reason": "UNKNOWN_REF"})
            continue
        leader_obj = resolve_unique(unit_map, leader["canonical_unit"])
        allowed = {norm(x) for x in leader_obj.get("leaderTo", [])}
        ok = norm(body["canonical_unit"]) in allowed
        checks.append({
            "check": "leader_relation",
            "status": "PASS" if ok else "FAIL",
            **att,
            "leader": leader["canonical_unit"],
            "bodyguard": body["canonical_unit"],
        })

    unit_points_total = sum(int(x["points"]) for x in expanded if x.get("points") is not None)
    total_points = unit_points_total + enhancement_total
    points_limit = request.get("points_limit")
    if points_limit is not None:
        checks.append({
            "check": "points_limit",
            "status": "PASS" if total_points <= int(points_limit) else "FAIL",
            "points": total_points,
            "limit": int(points_limit),
        })

    scoped_fail = [x for x in checks if x["status"] == "FAIL"]
    scoped_state = "PASS" if not scoped_fail else "FAIL"

    physical = evaluate_physical(request, expanded, profile)

    if scoped_state == "FAIL":
        overall = "INVALID_SCOPED_RULES"
    elif physical["state"] == "INFEASIBLE_FROM_SNAPSHOT":
        overall = "SCOPED_RULES_PASS_PHYSICAL_INFEASIBLE"
    elif physical["state"] == "UNKNOWN_COMPONENT_FEASIBILITY":
        overall = "SCOPED_RULES_PASS_PHYSICAL_UNKNOWN"
    else:
        overall = "SCOPED_RULES_PASS_PHYSICAL_FEASIBLE"

    return {
        "schema_version": "1.0",
        "roster_id": request.get("roster_id"),
        "status": overall,
        "rules": {
            "edition": mfm.get("edition"),
            "mfm_version": mfm.get("mfm_version"),
            "official_last_updated": mfm.get("official_last_updated"),
            "detachment": detachment["name"] if detachment else request.get("detachment"),
            "detachment_points": detachment.get("dp") if detachment else None,
            "scoped_legality": scoped_state,
            "scoped_checks": checks,
            "full_normative_legality": "UNKNOWN_PENDING_NORMATIVE_APP",
            "full_normative_reason": "Repository current state intentionally does not claim full official/app semantic normalization.",
            "repository_rules_status": current_rules.get("status"),
        },
        "points": {
            "units": unit_points_total,
            "enhancements": enhancement_total,
            "total": total_points,
            "limit": int(points_limit) if points_limit is not None else None,
        },
        "enhancements": enhancement_rows,
        "units": expanded,
        "physical": physical,
        "provenance": {
            "rules_snapshot": str(mfm_path.relative_to(root)),
            "mfm_extraction": mfm.get("provenance"),
            "collection_profile": str(profile_path.relative_to(root)),
            "collection_source": profile.get("source", {}).get("canonical_inventory"),
            "collection_checkpoint": profile.get("collection_checkpoint"),
            "collection_status": profile.get("collection_status"),
        },
        "authority_boundary": {
            "points_unit_sizes_detachment_costs": "GW_MFM",
            "physical_collection": "PERSONAL_COLLECTION_SNAPSHOT",
            "full_rules_legality": "NOT_CLAIMED",
            "runtime_or_bsdata_values_do_not_rewrite_normative_data": True,
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Evaluate scoped 11E roster legality and physical feasibility against the personal collection."
    )
    ap.add_argument("--input", required=True, type=Path)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()

    request = json.loads(args.input.read_text(encoding="utf-8"))
    result = solve_request(request)
    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")

    if result["rules"]["scoped_legality"] == "FAIL":
        return 2
    if result["physical"]["state"] == "INFEASIBLE_FROM_SNAPSHOT":
        return 3
    if result["physical"]["state"] == "UNKNOWN_COMPONENT_FEASIBILITY":
        return 4
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
