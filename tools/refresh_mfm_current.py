#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

import yaml

import import_mfm_snapshot as lib

ROOT = Path(__file__).resolve().parents[1]


def current_mfm_index() -> str:
    current = lib.json_load(ROOT / "rules" / "11e" / "current.json")
    pointer = current.get("wave_a_mfm", {}).get("snapshot")
    if not pointer or not (ROOT / pointer).exists():
        raise RuntimeError(f"Invalid current MFM pointer: {pointer!r}")
    return pointer


def update_handoff(*, checked_at: str, version: str, official_date: str, extraction_commit: str, totals: dict, diff_summary: dict, previous: str) -> None:
    path = ROOT / "reports" / "CURRENT_HANDOFF.md"
    text = path.read_text(encoding="utf-8")
    import re
    text = re.sub(r"Updated: \*\*\d{4}-\d{2}-\d{2}\*\*", f"Updated: **{checked_at}**", text, count=1)
    marker = f"## Current rules refresh — MFM v{version}"
    if marker not in text:
        section = (
            f"{marker}\n\n"
            f"- official MFM: **v{version}**, updated **{official_date}**, revalidated **{checked_at}**;\n"
            f"- extraction pin: `BSData/wh40k-11e-mfm@{extraction_commit}`;\n"
            f"- immutable snapshot: `rules/11e/snapshots/{checked_at}/mfm/index.json`;\n"
            f"- previous current snapshot preserved: `{previous}`;\n"
            f"- normalized faction pages: **30**;\n"
            f"- units / pricing rows / detachments: **{totals['units']} / {totals['pricing_rows']} / {totals['detachments']}**;\n"
            f"- stable-key point changes vs previous current snapshot: **{diff_summary['point_changes']}** "
            f"(▲{diff_summary['point_increases']} / ▼{diff_summary['point_decreases']});\n"
            "- MFM authority gate: **SATISFIED**; secondary Wahapedia/BSData reconciliation must use this current MFM pointer;\n"
            "- no historical MFM snapshot was modified.\n\n"
        )
        text = text.replace("## Recovery authority", section + "## Recovery authority", 1)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot-date", required=True)
    ap.add_argument("--version", required=True)
    ap.add_argument("--official-last-updated", required=True)
    ap.add_argument("--verified-at", required=True)
    ap.add_argument("--extraction-commit", required=True)
    ap.add_argument("--previous-index")
    args = ap.parse_args()

    if args.snapshot_date != args.verified_at:
        raise SystemExit("snapshot-date and verified-at must match")
    previous_path = args.previous_index or current_mfm_index()
    previous_index = lib.json_load(ROOT / previous_path)
    if previous_index["official_source"]["version"] == args.version:
        raise RuntimeError(f"MFM v{args.version} is already current at {previous_path}")

    snapshot_root = ROOT / "rules" / "11e" / "snapshots" / args.snapshot_date / "mfm"
    if snapshot_root.exists():
        raise RuntimeError(f"Refusing to overwrite immutable snapshot path: {snapshot_root}")

    official_evidence = lib.fetch_official_mfm_evidence(args.official_last_updated)
    official_evidence["checked_at"] = args.verified_at

    previous_by_slug = {}
    for rel in previous_index.get("faction_files", []):
        old = lib.json_load(ROOT / rel)
        previous_by_slug[old["faction"]["slug"]] = old

    with tempfile.TemporaryDirectory(prefix="wh40k-mfm-current-") as td:
        extraction_repo = Path(td) / "mfm"
        lib.clone_extraction(args.extraction_commit, extraction_repo)
        meta = lib.clean_yaml(yaml.safe_load((extraction_repo / "data" / "meta.yaml").read_text(encoding="utf-8")))
        if str(meta.get("version")) != args.version:
            raise RuntimeError(f"Extraction meta version mismatch: expected {args.version}, got {meta.get('version')}")
        if str(meta.get("lastUpdated")) != args.official_last_updated:
            raise RuntimeError(f"Extraction meta date mismatch: expected {args.official_last_updated}, got {meta.get('lastUpdated')}")

        source_files = sorted(p for p in (extraction_repo / "data").glob("*.yaml") if p.name != "meta.yaml")
        expected_factions = list(meta.get("factions") or [])
        if len(source_files) != len(expected_factions) or len(source_files) != 30:
            raise RuntimeError(f"MFM faction-set mismatch: files={len(source_files)} meta={len(expected_factions)} expected=30")

        snapshots = []
        faction_files = []
        faction_diffs = []
        for source in source_files:
            raw = lib.clean_yaml(yaml.safe_load(source.read_text(encoding="utf-8")))
            if str(raw.get("version")) != args.version:
                raise RuntimeError(f"{source.name}: expected version {args.version}, got {raw.get('version')}")
            snap = lib.make_faction_snapshot(
                raw,
                extraction_repo=extraction_repo,
                extraction_commit=args.extraction_commit,
                source_path=f"data/{source.name}",
                official_date=args.official_last_updated,
                normalized_at=args.verified_at,
            )
            out = snapshot_root / "factions" / f"{raw['slug']}.json"
            lib.json_write(out, snap)
            faction_files.append(out.relative_to(ROOT).as_posix())
            snapshots.append(snap)
            faction_diffs.append(lib.diff_faction(previous_by_slug.get(raw["slug"]), snap))

    keys = ("units", "detachments", "pricing_rows", "leader_relations", "support_relations", "wargear_cost_entries", "enhancement_cost_entries", "legends_units")
    totals = {key: sum(s["summary"][key] for s in snapshots) for key in keys}
    coverage = dict(previous_index["coverage"])
    index = {
        "schema_version": "1.1",
        "snapshot_id": f"MFM_{args.version.replace('.', '_')}_{args.official_last_updated}",
        "edition": "11e",
        "status": "CURRENT_VERIFIED_MFM_DIMENSIONS",
        "official_source": {
            "source_id": lib.MFM_SOURCE_ID,
            "version": args.version,
            "last_updated": args.official_last_updated,
            "verified_at": args.verified_at,
            "evidence_url": lib.GW_DOWNLOADS,
            "evidence_page_sha256": official_evidence["page_sha256"],
        },
        "extraction_source": {
            "source_id": lib.MFM_EXTRACTION_SOURCE_ID,
            "repository": "BSData/wh40k-11e-mfm",
            "commit_sha": args.extraction_commit,
            "normalized_at": args.verified_at,
            "upstream_state": "PINNED_REVIEWED_EXTRACTION_COMMIT",
        },
        "coverage": coverage,
        "totals": totals,
        "faction_files": faction_files,
    }
    lib.json_write(snapshot_root / "index.json", index)

    diff_summary = {
        "factions_compared": len(faction_diffs),
        "factions_with_point_changes": sum(1 for x in faction_diffs if x["point_changes"]),
        "point_changes": sum(x["point_changes"] for x in faction_diffs),
        "point_increases": sum(x["point_increases"] for x in faction_diffs),
        "point_decreases": sum(x["point_decreases"] for x in faction_diffs),
        "pricing_rows_added": sum(x["pricing_rows_added"] for x in faction_diffs),
        "pricing_rows_removed": sum(x["pricing_rows_removed"] for x in faction_diffs),
        "units_added": sum(len(x["units_added"]) for x in faction_diffs),
        "units_removed": sum(len(x["units_removed"]) for x in faction_diffs),
        "detachments_added": sum(len(x["detachments_added"]) for x in faction_diffs),
        "detachments_removed": sum(len(x["detachments_removed"]) for x in faction_diffs),
    }
    tag = args.version.replace(".", "_")
    report = {
        "schema_version": "1.1",
        "status": "PASS",
        "milestone": f"MFM_V{tag}_NORMATIVE_REFRESH",
        "as_of": args.verified_at,
        "previous_snapshot": previous_path,
        "current_snapshot": f"rules/11e/snapshots/{args.snapshot_date}/mfm/index.json",
        "official_evidence": official_evidence,
        "extraction": {"repository": "BSData/wh40k-11e-mfm", "commit": args.extraction_commit, "version": args.version, "meta_last_updated": args.official_last_updated},
        "totals": totals,
        "diff_summary": diff_summary,
        "factions": faction_diffs,
        "authority_boundary": "Official GW MFM currentness establishes normative scope. The pinned BSData MFM extraction is used only as reproducible structured extraction.",
    }
    lib.json_write(ROOT / "reports" / f"MFM_{tag}_REFRESH_CURRENT.json", report)
    lib.json_write(ROOT / "ingestion" / "runs" / f"{args.verified_at}_mfm_v{tag}_refresh.json", {
        "schema_version": "1.0",
        "run_id": f"INGEST_{args.verified_at}_MFM_V{tag}_REFRESH",
        "status": "PASS",
        "started_at": args.verified_at,
        "completed_at": args.verified_at,
        "source_ids": [lib.MFM_SOURCE_ID, lib.MFM_EXTRACTION_SOURCE_ID],
        "official_revision": {"version": args.version, "updated_at": args.official_last_updated},
        "extraction_commit": args.extraction_commit,
        "previous_snapshot": previous_path,
        "output_snapshot": f"rules/11e/snapshots/{args.snapshot_date}/mfm/index.json",
        "promotion": "MFM_DIMENSIONS_CURRENT_VERIFIED",
        "auto_promote": False,
    })

    closure = (
        f"# MFM v{args.version} normative refresh — {args.verified_at}\n\n"
        f"- Official update: **{args.official_last_updated}**.\n"
        f"- Official currentness revalidated: **{args.verified_at}**.\n"
        f"- Structured extraction pin: `{args.extraction_commit}`.\n"
        f"- Snapshot: `rules/11e/snapshots/{args.snapshot_date}/mfm/index.json`.\n"
        f"- Previous current snapshot preserved: `{previous_path}`.\n"
        f"- Factions: **{len(snapshots)}**.\n"
        f"- Units / pricing rows / detachments: **{totals['units']} / {totals['pricing_rows']} / {totals['detachments']}**.\n"
        f"- Stable-key point changes vs previous current snapshot: **{diff_summary['point_changes']}** (▲{diff_summary['point_increases']} / ▼{diff_summary['point_decreases']}).\n"
        f"- Added/removed pricing rows: **{diff_summary['pricing_rows_added']} / {diff_summary['pricing_rows_removed']}**.\n"
        "- Historical snapshots were not modified.\n"
        "- Secondary Wahapedia / BSData semantics require guarded reconciliation against this new current MFM pointer.\n"
    )
    (ROOT / "reports" / f"MFM_{tag}_REFRESH_{args.verified_at}.md").write_text(closure, encoding="utf-8")

    lib.update_registry(checked_at=args.verified_at, official_date=args.official_last_updated, version=args.version, extraction_commit=args.extraction_commit)
    lib.update_currentness(checked_at=args.verified_at, official_date=args.official_last_updated, extraction_commit=args.extraction_commit)
    lib.update_rules_current(snapshot_date=args.snapshot_date, official_date=args.official_last_updated, checked_at=args.verified_at, version=args.version, index=index)
    lib.update_coverage(checked_at=args.verified_at, official_date=args.official_last_updated, version=args.version, index=index)
    update_handoff(checked_at=args.verified_at, version=args.version, official_date=args.official_last_updated, extraction_commit=args.extraction_commit, totals=totals, diff_summary=diff_summary, previous=previous_path)

    print(json.dumps({"status": "PASS", "snapshot": f"rules/11e/snapshots/{args.snapshot_date}/mfm/index.json", "totals": totals, "diff_summary": diff_summary}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
