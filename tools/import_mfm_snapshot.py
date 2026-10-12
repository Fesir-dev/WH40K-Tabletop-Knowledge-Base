#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import subprocess
import tempfile
import urllib.request
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
MFM_REPO = "https://github.com/BSData/wh40k-11e-mfm.git"
MFM_SOURCE_ID = "GW_MFM"
MFM_EXTRACTION_SOURCE_ID = "BSDATA_MFM_11E"
GW_DOWNLOADS = "https://www.warhammer-community.com/en-gb/downloads/warhammer-40000/"
USER_AGENT = "WH40K-Tabletop-Knowledge-Base/1.0"


def json_load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def json_write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def clean_yaml(value: Any) -> Any:
    if isinstance(value, (dt.date, dt.datetime)):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_yaml(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_yaml(v) for v in value]
    return value


def run(args: list[str], cwd: Path | None = None) -> str:
    proc = subprocess.run(args, cwd=cwd, text=True, capture_output=True)
    if proc.returncode:
        raise RuntimeError(
            f"command failed ({proc.returncode}): {' '.join(args)}\n"
            f"stdout:\n{proc.stdout[-8000:]}\nstderr:\n{proc.stderr[-8000:]}"
        )
    return proc.stdout.strip()


def fetch_official_mfm_evidence(expected_date: str) -> dict[str, Any]:
    request = urllib.request.Request(GW_DOWNLOADS, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=90) as response:
        body = response.read(12 * 1024 * 1024)
    text = body.decode("utf-8", errors="replace")
    low = text.casefold()
    marker = low.find("munitorum field manual")
    if marker < 0:
        raise RuntimeError("Official GW downloads page did not expose a Munitorum Field Manual marker")
    date_obj = dt.date.fromisoformat(expected_date)
    accepted = {
        expected_date,
        date_obj.strftime("%d/%m/%Y"),
        date_obj.strftime("%d/%m/%y"),
        date_obj.strftime("%-d/%-m/%Y"),
    }
    window = text[max(0, marker - 3000): marker + 7000]
    if not any(token in window for token in accepted):
        raise RuntimeError(
            f"Official MFM marker found, but expected update date {expected_date} was not found near it"
        )
    return {
        "url": GW_DOWNLOADS,
        "checked_at": dt.date.today().isoformat(),
        "expected_updated_at": expected_date,
        "page_sha256": hashlib.sha256(body).hexdigest(),
        "marker": "Munitorum Field Manual",
        "state": "PASS",
    }


def clone_extraction(commit: str, destination: Path) -> None:
    run(["git", "init", "-q", str(destination)])
    run(["git", "remote", "add", "origin", MFM_REPO], cwd=destination)
    run(["git", "fetch", "-q", "--depth", "1", "origin", commit], cwd=destination)
    run(["git", "checkout", "-q", "--detach", "FETCH_HEAD"], cwd=destination)
    resolved = run(["git", "rev-parse", "HEAD"], cwd=destination)
    if resolved != commit:
        raise RuntimeError(f"Extraction commit mismatch: expected {commit}, got {resolved}")


def blob_sha(repo: Path, commit: str, relative: str) -> str:
    return run(["git", "rev-parse", f"{commit}:{relative}"], cwd=repo)


def summarize(raw: dict[str, Any]) -> dict[str, int]:
    units = raw.get("units") or []
    detachments = raw.get("detachments") or []
    pricing_rows = sum(
        len(tier.get("costs") or [])
        for unit in units
        for tier in (unit.get("pricing") or [])
    )
    return {
        "units": len(units),
        "detachments": len(detachments),
        "pricing_rows": pricing_rows,
        "leader_relations": sum(len(unit.get("leaderTo") or []) for unit in units),
        "support_relations": sum(len(unit.get("supportTo") or []) for unit in units),
        "wargear_cost_entries": sum(len(unit.get("wargear") or []) for unit in units),
        "enhancement_cost_entries": sum(
            len(detachment.get("enhancements") or []) for detachment in detachments
        ),
        "legends_units": sum(1 for unit in units if unit.get("legends") is True),
    }


def make_faction_snapshot(
    raw: dict[str, Any],
    *,
    extraction_repo: Path,
    extraction_commit: str,
    source_path: str,
    official_date: str,
    normalized_at: str,
) -> dict[str, Any]:
    version = str(raw.get("version"))
    slug = str(raw["slug"])
    return {
        "schema_version": "1.0",
        "snapshot_id": f"MFM_{version.replace('.', '_')}_{slug.upper().replace('-', '_')}",
        "edition": "11e",
        "mfm_version": version,
        "official_last_updated": official_date,
        "content_first_seen": raw.get("firstSeen"),
        "faction": {
            "slug": slug,
            "name": raw["name"],
            "parent": raw.get("parent"),
        },
        "provenance": {
            "normative_source_id": MFM_SOURCE_ID,
            "extraction_source_id": MFM_EXTRACTION_SOURCE_ID,
            "extraction_repository": "BSData/wh40k-11e-mfm",
            "extraction_commit": extraction_commit,
            "extraction_path": source_path,
            "extraction_blob_sha": blob_sha(extraction_repo, extraction_commit, source_path),
            "normalized_at": normalized_at,
        },
        "summary": summarize(raw),
        "detachments": raw.get("detachments") or [],
        "units": raw.get("units") or [],
    }


def pricing_map(snapshot: dict[str, Any]) -> dict[tuple[Any, ...], int]:
    out: dict[tuple[Any, ...], int] = {}
    for unit in snapshot.get("units") or []:
        for tier in unit.get("pricing") or []:
            for cost in tier.get("costs") or []:
                key = (
                    unit.get("name"),
                    tier.get("range"),
                    cost.get("models"),
                    cost.get("desc"),
                    bool(cost.get("addon")),
                )
                out[key] = int(cost["points"])
    return out


def diff_faction(old: dict[str, Any] | None, new: dict[str, Any]) -> dict[str, Any]:
    old_units = {x.get("name") for x in (old or {}).get("units", [])}
    new_units = {x.get("name") for x in new.get("units", [])}
    old_det = {x.get("name") for x in (old or {}).get("detachments", [])}
    new_det = {x.get("name") for x in new.get("detachments", [])}
    old_points = pricing_map(old or {})
    new_points = pricing_map(new)
    shared = old_points.keys() & new_points.keys()
    changes = [
        {"key": list(key), "from": old_points[key], "to": new_points[key], "delta": new_points[key] - old_points[key]}
        for key in shared
        if old_points[key] != new_points[key]
    ]
    return {
        "slug": new["faction"]["slug"],
        "name": new["faction"]["name"],
        "units_added": sorted(x for x in new_units - old_units if x),
        "units_removed": sorted(x for x in old_units - new_units if x),
        "detachments_added": sorted(x for x in new_det - old_det if x),
        "detachments_removed": sorted(x for x in old_det - new_det if x),
        "point_changes": len(changes),
        "point_increases": sum(1 for x in changes if x["delta"] > 0),
        "point_decreases": sum(1 for x in changes if x["delta"] < 0),
        "net_point_delta_across_changed_rows": sum(x["delta"] for x in changes),
        "pricing_rows_added": len(new_points.keys() - old_points.keys()),
        "pricing_rows_removed": len(old_points.keys() - new_points.keys()),
    }


def update_registry(*, checked_at: str, official_date: str, version: str, extraction_commit: str) -> None:
    path = ROOT / "sources" / "registry.json"
    data = json_load(path)
    data["as_of"] = checked_at
    by_id = {x["id"]: x for x in data["sources"]}
    gw = by_id[MFM_SOURCE_ID]
    gw["checked_at"] = checked_at
    gw["source_health"] = "PASS"
    gw["status"] = "CURRENT_VERIFIED"
    gw["observed_revision"] = {
        "updated_at": official_date,
        "verified_at": checked_at,
        "evidence_url": GW_DOWNLOADS,
    }
    ext = by_id[MFM_EXTRACTION_SOURCE_ID]
    ext["checked_at"] = checked_at
    ext["status"] = "CURRENT_VERIFIED"
    ext["observed_revision"] = {
        "commit_sha": extraction_commit,
        "mfm_version": version,
        "official_last_updated": official_date,
    }
    json_write(path, data)


def update_currentness(*, checked_at: str, official_date: str, extraction_commit: str) -> None:
    path = ROOT / "sources" / "currentness_gate.json"
    data = json_load(path)
    data["as_of"] = checked_at
    by_id = {x["id"]: x for x in data["required_checks"]}
    gw = by_id[MFM_SOURCE_ID]
    gw["state"] = "PASS"
    gw["checked_at"] = checked_at
    gw["observed_updated_at"] = official_date
    ext = by_id[MFM_EXTRACTION_SOURCE_ID]
    ext["state"] = "PASS"
    ext["checked_at"] = checked_at
    ext["observed_commit"] = extraction_commit
    json_write(path, data)


def update_rules_current(*, snapshot_date: str, official_date: str, checked_at: str, version: str, index: dict[str, Any]) -> None:
    path = ROOT / "rules" / "11e" / "current.json"
    data = json_load(path)
    data["repository_checkpoint"] = checked_at
    mfm_current = data["source_currentness"]["mfm"]
    mfm_current["state"] = "PASS"
    mfm_current["updated_at"] = official_date
    mfm_current["verified_at"] = checked_at
    wave = data["wave_a_mfm"]
    wave["state"] = "CURRENT_VERIFIED"
    wave["snapshot"] = f"rules/11e/snapshots/{snapshot_date}/mfm/index.json"
    wave["version"] = version
    wave["last_updated"] = official_date
    wave["normalized_faction_pages"] = index["coverage"]["mfm_faction_pages"]
    wave["mapped_roster_identities"] = index["coverage"]["mapped_roster_identities"]
    automation = data.get("automation", {}).get("upstream_reingestion", {})
    if automation:
        automation["mfm_authority_gate"] = "SATISFIED_CURRENT_OFFICIAL_MFM_REVALIDATION"
    json_write(path, data)


def update_coverage(*, checked_at: str, official_date: str, version: str, index: dict[str, Any]) -> None:
    path = ROOT / "coverage" / "current.json"
    data = json_load(path)
    data["as_of"] = checked_at
    glob = data["global"]
    glob["mfm_version"] = version
    glob["mfm_last_updated"] = official_date
    glob["mfm_faction_pages_normalized"] = index["coverage"]["mfm_faction_pages"]
    glob["mfm_roster_identities_complete"] = index["coverage"]["mapped_roster_identities"]
    glob["mfm_roster_identities_not_applicable"] = len(index["coverage"]["not_applicable_roster_identities"])
    json_write(path, data)


def update_handoff(*, checked_at: str, version: str, official_date: str, extraction_commit: str, totals: dict[str, int], diff_summary: dict[str, int]) -> None:
    path = ROOT / "reports" / "CURRENT_HANDOFF.md"
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"Updated: \*\*\d{4}-\d{2}-\d{2}\*\*", f"Updated: **{checked_at}**", text, count=1)
    marker = "## Current rules refresh — MFM v1.5"
    if marker not in text:
        section = (
            f"{marker}\n\n"
            f"- official MFM: **v{version}**, updated **{official_date}**, revalidated **{checked_at}**;\n"
            f"- extraction pin: `BSData/wh40k-11e-mfm@{extraction_commit}`;\n"
            f"- immutable snapshot: `rules/11e/snapshots/{checked_at}/mfm/index.json`;\n"
            f"- normalized faction pages: **30**;\n"
            f"- units / pricing rows / detachments: **{totals['units']} / {totals['pricing_rows']} / {totals['detachments']}**;\n"
            f"- changed point rows vs v1.4 on stable pricing keys: **{diff_summary['point_changes']}** "
            f"(▲{diff_summary['point_increases']} / ▼{diff_summary['point_decreases']});\n"
            "- MFM authority gate: **SATISFIED**; secondary Wahapedia/BSData reconciliation follows on the same guarded refresh branch;\n"
            "- historical MFM 1.4 snapshot remains immutable.\n\n"
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
    ap.add_argument("--previous-index", default="rules/11e/snapshots/2026-09-29/mfm/index.json")
    args = ap.parse_args()

    if args.version != "1.5":
        raise SystemExit("This refresh milestone expects MFM v1.5")
    if args.snapshot_date != args.verified_at:
        raise SystemExit("snapshot-date and verified-at must match for this immutable refresh checkpoint")

    official_evidence = fetch_official_mfm_evidence(args.official_last_updated)
    official_evidence["checked_at"] = args.verified_at

    previous_index_path = ROOT / args.previous_index
    previous_index = json_load(previous_index_path)
    previous_by_slug: dict[str, dict[str, Any]] = {}
    for rel in previous_index.get("faction_files", []):
        old = json_load(ROOT / rel)
        previous_by_slug[old["faction"]["slug"]] = old

    snapshot_root = ROOT / "rules" / "11e" / "snapshots" / args.snapshot_date / "mfm"
    if snapshot_root.exists():
        raise RuntimeError(f"Refusing to overwrite immutable snapshot path: {snapshot_root}")

    with tempfile.TemporaryDirectory(prefix="wh40k-mfm-") as td:
        extraction_repo = Path(td) / "mfm"
        clone_extraction(args.extraction_commit, extraction_repo)
        source_files = sorted(p for p in (extraction_repo / "data").glob("*.yaml") if p.name != "meta.yaml")
        if len(source_files) != 30:
            raise RuntimeError(f"Expected 30 MFM faction files, found {len(source_files)}")

        snapshots: list[dict[str, Any]] = []
        faction_files: list[str] = []
        faction_diffs: list[dict[str, Any]] = []
        for source in source_files:
            raw = clean_yaml(yaml.safe_load(source.read_text(encoding="utf-8")))
            if str(raw.get("version")) != args.version:
                raise RuntimeError(f"{source.name}: expected version {args.version}, got {raw.get('version')}")
            rel_source = f"data/{source.name}"
            snap = make_faction_snapshot(
                raw,
                extraction_repo=extraction_repo,
                extraction_commit=args.extraction_commit,
                source_path=rel_source,
                official_date=args.official_last_updated,
                normalized_at=args.verified_at,
            )
            out = snapshot_root / "factions" / f"{raw['slug']}.json"
            json_write(out, snap)
            faction_files.append(out.relative_to(ROOT).as_posix())
            snapshots.append(snap)
            faction_diffs.append(diff_faction(previous_by_slug.get(raw["slug"]), snap))

    totals = {
        key: sum(s["summary"][key] for s in snapshots)
        for key in (
            "units", "detachments", "pricing_rows", "leader_relations", "support_relations",
            "wargear_cost_entries", "enhancement_cost_entries", "legends_units",
        )
    }
    coverage = dict(previous_index["coverage"])
    index = {
        "schema_version": "1.1",
        "snapshot_id": f"MFM_{args.version.replace('.', '_')}_{args.official_last_updated}",
        "edition": "11e",
        "status": "CURRENT_VERIFIED_MFM_DIMENSIONS",
        "official_source": {
            "source_id": MFM_SOURCE_ID,
            "version": args.version,
            "last_updated": args.official_last_updated,
            "verified_at": args.verified_at,
            "evidence_url": GW_DOWNLOADS,
            "evidence_page_sha256": official_evidence["page_sha256"],
        },
        "extraction_source": {
            "source_id": MFM_EXTRACTION_SOURCE_ID,
            "repository": "BSData/wh40k-11e-mfm",
            "commit_sha": args.extraction_commit,
            "normalized_at": args.verified_at,
        },
        "coverage": coverage,
        "totals": totals,
        "faction_files": faction_files,
    }
    json_write(snapshot_root / "index.json", index)

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
    report = {
        "schema_version": "1.0",
        "status": "PASS",
        "milestone": "MFM_V1_5_NORMATIVE_REFRESH",
        "as_of": args.verified_at,
        "previous_snapshot": args.previous_index,
        "current_snapshot": f"rules/11e/snapshots/{args.snapshot_date}/mfm/index.json",
        "official_evidence": official_evidence,
        "extraction": {
            "repository": "BSData/wh40k-11e-mfm",
            "commit": args.extraction_commit,
            "version": args.version,
        },
        "totals": totals,
        "diff_summary": diff_summary,
        "factions": faction_diffs,
        "authority_boundary": (
            "Official GW MFM currentness establishes normative scope. "
            "The pinned BSData MFM extraction is used only as reproducible structured extraction."
        ),
    }
    json_write(ROOT / "reports" / "MFM_1_5_REFRESH_CURRENT.json", report)
    json_write(
        ROOT / "ingestion" / "runs" / "2026-10-13_mfm_v1_5_refresh.json",
        {
            "schema_version": "1.0",
            "run_id": "INGEST_2026-10-13_MFM_V1_5_REFRESH",
            "status": "PASS",
            "started_at": args.verified_at,
            "completed_at": args.verified_at,
            "source_ids": [MFM_SOURCE_ID, MFM_EXTRACTION_SOURCE_ID],
            "official_revision": {"version": args.version, "updated_at": args.official_last_updated},
            "extraction_commit": args.extraction_commit,
            "previous_snapshot": args.previous_index,
            "output_snapshot": f"rules/11e/snapshots/{args.snapshot_date}/mfm/index.json",
            "promotion": "MFM_DIMENSIONS_CURRENT_VERIFIED",
            "auto_promote": False,
        },
    )

    closure = (
        "# MFM v1.5 normative refresh — 2026-10-13\n\n"
        f"- Official update: **{args.official_last_updated}**.\n"
        f"- Official currentness revalidated: **{args.verified_at}**.\n"
        f"- Structured extraction pin: `{args.extraction_commit}`.\n"
        f"- Snapshot: `rules/11e/snapshots/{args.snapshot_date}/mfm/index.json`.\n"
        f"- Factions: **{len(snapshots)}**.\n"
        f"- Units / pricing rows / detachments: **{totals['units']} / {totals['pricing_rows']} / {totals['detachments']}**.\n"
        f"- Stable-key point changes vs v1.4: **{diff_summary['point_changes']}** "
        f"(▲{diff_summary['point_increases']} / ▼{diff_summary['point_decreases']}).\n"
        f"- Added/removed pricing rows: **{diff_summary['pricing_rows_added']} / {diff_summary['pricing_rows_removed']}**.\n"
        "- Historical MFM v1.4 snapshot was not modified.\n"
        "- Wahapedia / BSData roster semantics are refreshed separately through the guarded re-ingestion pipeline.\n"
    )
    (ROOT / "reports" / "MFM_1_5_REFRESH_2026-10-13.md").write_text(closure, encoding="utf-8")

    update_registry(
        checked_at=args.verified_at,
        official_date=args.official_last_updated,
        version=args.version,
        extraction_commit=args.extraction_commit,
    )
    update_currentness(
        checked_at=args.verified_at,
        official_date=args.official_last_updated,
        extraction_commit=args.extraction_commit,
    )
    update_rules_current(
        snapshot_date=args.snapshot_date,
        official_date=args.official_last_updated,
        checked_at=args.verified_at,
        version=args.version,
        index=index,
    )
    update_coverage(
        checked_at=args.verified_at,
        official_date=args.official_last_updated,
        version=args.version,
        index=index,
    )
    update_handoff(
        checked_at=args.verified_at,
        version=args.version,
        official_date=args.official_last_updated,
        extraction_commit=args.extraction_commit,
        totals=totals,
        diff_summary=diff_summary,
    )

    print(json.dumps(
        {
            "status": "PASS",
            "snapshot": f"rules/11e/snapshots/{args.snapshot_date}/mfm/index.json",
            "totals": totals,
            "diff_summary": diff_summary,
        },
        ensure_ascii=False,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
