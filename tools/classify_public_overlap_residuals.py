#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

from audit_official_public_mirror_overlap import (
    build_mirror_units,
    load_verified_mirror,
    resolve_current_wahapedia_root,
)

ROOT = Path(__file__).resolve().parents[1]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def classify_unscoped(match: dict, source_by_id: dict[str, dict]) -> str:
    if match.get("provenance_scope") == "CORE_PUBLIC_TEXT_ONLY":
        return "CORE_PUBLIC_GLOBAL"
    source_id = match.get("mirror_source_id")
    faction_id = match.get("mirror_faction_id")
    source = source_by_id.get(source_id) if source_id else None
    if source and str(source.get("edition")) != "11":
        return "NON_11_OR_LEGENDS_SOURCE"
    if source and str(source.get("edition")) == "11":
        return "EDITION_11_SOURCE_MATCH_OUTSIDE_OWN_PACK"
    if source_id and source is None:
        return "UNKNOWN_SOURCE_ID"
    if faction_id:
        return "FACTION_ONLY_MATCH_OUTSIDE_OWN_PACK"
    return "NO_SOURCE_OR_FACTION_SCOPE"


def classify_no_exact(unit: dict, source_by_id: dict[str, dict]) -> str:
    if unit.get("comparison_char_count", 0) < 40 or unit.get("token_count", 0) < 6:
        return "TOO_SHORT_FOR_SAFE_AUTO_MATCH"
    source_id = unit.get("source_id")
    faction_id = unit.get("faction_id")
    source = source_by_id.get(source_id) if source_id else None
    if source and str(source.get("edition")) != "11":
        return "NON_11_OR_LEGENDS_SOURCE_NO_EXACT"
    if source and str(source.get("edition")) == "11":
        return "EDITION_11_SOURCE_NO_EXACT_PUBLIC_OVERLAP"
    if source_id and source is None:
        return "UNKNOWN_SOURCE_ID_NO_EXACT"
    if faction_id:
        return "FACTION_ONLY_NO_EXACT_PUBLIC_OVERLAP"
    return "NO_SOURCE_OR_FACTION_NO_EXACT"


def build(as_of: str, root: Path = ROOT) -> dict:
    report = load(root / "reports" / "OFFICIAL_PUBLIC_MIRROR_OVERLAP_CURRENT.json")
    if report.get("status") != "PASS":
        raise RuntimeError("Official-public overlap report is not PASS")

    tables, mirror_state = load_verified_mirror(root)
    units = build_mirror_units(tables)
    wroot = resolve_current_wahapedia_root(root)
    source_catalog = load(wroot / "source_catalog.json")
    source_by_id = {x.get("id"): x for x in source_catalog if x.get("id")}

    exact_keys = {
        (x.get("unit_key"), x.get("mirror_text_sha256"))
        for x in report.get("matches", [])
    }

    unscoped_matches = [
        x for x in report.get("matches", [])
        if x.get("provenance_scope") in {"GLOBAL_PUBLIC_TEXT_ONLY", "CORE_PUBLIC_TEXT_ONLY"}
    ]
    unscoped_rows = []
    unscoped_counts = Counter()
    unscoped_by_kind = defaultdict(Counter)
    for match in unscoped_matches:
        cls = classify_unscoped(match, source_by_id)
        unscoped_counts[cls] += 1
        unscoped_by_kind[match["kind"]][cls] += 1
        source_id = match.get("mirror_source_id")
        source = source_by_id.get(source_id) if source_id else None
        unscoped_rows.append({
            "unit_key": match["unit_key"],
            "kind": match["kind"],
            "identity": match.get("identity", {}),
            "classification": cls,
            "mirror_source_id": source_id,
            "mirror_faction_id": match.get("mirror_faction_id"),
            "source_name": source.get("name") if source else None,
            "source_edition": source.get("edition") if source else None,
            "exact_official_documents": sorted({
                e["document_id"] for e in match.get("official_evidence", [])
            }),
            "promotion_eligible": False,
        })

    no_exact_rows = []
    no_exact_counts = Counter()
    no_exact_by_kind = defaultdict(Counter)
    for unit in units:
        if (unit["unit_key"], unit["mirror_text_sha256"]) in exact_keys:
            continue
        cls = classify_no_exact(unit, source_by_id)
        no_exact_counts[cls] += 1
        no_exact_by_kind[unit["kind"]][cls] += 1
        source_id = unit.get("source_id")
        source = source_by_id.get(source_id) if source_id else None
        no_exact_rows.append({
            "unit_key": unit["unit_key"],
            "kind": unit["kind"],
            "identity": unit.get("identity", {}),
            "classification": cls,
            "mirror_source_id": source_id,
            "mirror_faction_id": unit.get("faction_id"),
            "source_name": source.get("name") if source else None,
            "source_edition": source.get("edition") if source else None,
            "comparison_char_count": unit.get("comparison_char_count"),
            "token_count": unit.get("token_count"),
            "promotion_eligible": False,
            "semantic_conflict_claimed": False,
        })

    if len(unscoped_rows) != int(report["summary"]["unscoped_exact_units"]):
        raise RuntimeError("Unscoped residual count differs from overlap audit")
    if len(no_exact_rows) != int(report["summary"]["no_exact_overlap_units"]):
        raise RuntimeError("No-exact residual count differs from overlap audit")

    return {
        "schema_version": "1.0",
        "status": "PASS",
        "as_of": as_of,
        "milestone": "OFFICIAL_PUBLIC_STRUCTURED_NORMALIZATION_EXPANSION",
        "authority_boundary": {
            "normative_authority": "GAMES_WORKSHOP",
            "no_exact_is_conflict": False,
            "unscoped_exact_is_promotable": False,
            "legends_or_non_11_reuse_promotes_current_rules": False,
            "app_codex_inference_allowed": False,
            "current_normalized_factions_change": 0,
        },
        "source_state": {
            "overlap_report": "reports/OFFICIAL_PUBLIC_MIRROR_OVERLAP_CURRENT.json",
            "mirror_verification": mirror_state,
            "source_catalog": str((wroot / "source_catalog.json").relative_to(root)),
        },
        "unscoped_exact": {
            "total": len(unscoped_rows),
            "classes": dict(sorted(unscoped_counts.items())),
            "by_kind": {
                kind: dict(sorted(counter.items()))
                for kind, counter in sorted(unscoped_by_kind.items())
            },
            "rows": unscoped_rows,
        },
        "no_exact_public_overlap": {
            "total": len(no_exact_rows),
            "classes": dict(sorted(no_exact_counts.items())),
            "by_kind": {
                kind: dict(sorted(counter.items()))
                for kind, counter in sorted(no_exact_by_kind.items())
            },
            "rows": no_exact_rows,
        },
        "summary": {
            "unscoped_exact_total": len(unscoped_rows),
            "no_exact_total": len(no_exact_rows),
            "promoted_units": 0,
            "semantic_conflicts_created": 0,
            "interpretation": "Residual classes explain evidence/scope limitations only. They do not assert that unmatched mirror semantics disagree with Games Workshop.",
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--as-of", default="2026-09-30")
    ap.add_argument("--output", type=Path, default=Path("rules/11e/snapshots/2026-09-30/official_public_overlap/residual_classification.json"))
    ap.add_argument("--summary-output", type=Path, default=Path("reports/OFFICIAL_PUBLIC_OVERLAP_RESIDUAL_CLASSIFICATION_CURRENT.json"))
    args = ap.parse_args()

    payload = build(args.as_of)
    out = args.output if args.output.is_absolute() else ROOT / args.output
    summary_out = args.summary_output if args.summary_output.is_absolute() else ROOT / args.summary_output
    out.parent.mkdir(parents=True, exist_ok=True)
    summary_out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    compact = {
        "schema_version": payload["schema_version"],
        "status": payload["status"],
        "as_of": payload["as_of"],
        "milestone": payload["milestone"],
        "authority_boundary": payload["authority_boundary"],
        "source_state": payload["source_state"],
        "unscoped_exact": {
            "total": payload["unscoped_exact"]["total"],
            "classes": payload["unscoped_exact"]["classes"],
            "by_kind": payload["unscoped_exact"]["by_kind"],
        },
        "no_exact_public_overlap": {
            "total": payload["no_exact_public_overlap"]["total"],
            "classes": payload["no_exact_public_overlap"]["classes"],
            "by_kind": payload["no_exact_public_overlap"]["by_kind"],
        },
        "summary": payload["summary"],
    }
    summary_out.write_text(json.dumps(compact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(compact, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
