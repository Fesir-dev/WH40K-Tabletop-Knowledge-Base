#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "NEW_RECRUIT_RUNTIME_VALIDATION_CURRENT.json"
REGISTRY = ROOT / "sources" / "runtime_drift_registry.json"
PROFILE = ROOT / "sources" / "profiles" / "new_recruit_bsdata_11e.json"
CURRENT = ROOT / "rules" / "11e" / "current.json"
SOURCE_REGISTRY = ROOT / "sources" / "registry.json"
WATCH = ROOT / "reports" / "UPSTREAM_CHANGE_WATCH_CURRENT.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def source_by_id(registry, source_id):
    return next(x for x in registry["sources"] if x["id"] == source_id)


def prepare_registry() -> None:
    report = load(REPORT)
    points = report.get("representative_points", {})
    surfaces = report.get("representative_surfaces", {})
    new = points.get("new_drifts", [])
    assert report.get("status") == "NEW_RUNTIME_PROJECTION_DRIFT", report.get("status")
    assert len(new) == 1 and int(points.get("new_drift_count", -1)) == 1, new
    assert int(surfaces.get("new_drift_count", -1)) == 0, surfaces
    drift = new[0]
    expected = {
        "slug": "adeptus_custodes",
        "unit": "Trajann Valoris",
        "classification": "RUNTIME_PROJECTION_DRIFT",
        "gw_mfm_value": 265,
        "wahapedia_value": 265,
        "pinned_bsdata_value": 265,
        "live_bsdata_value": 265,
        "new_recruit_runtime_value": 135,
    }
    for key, value in expected.items():
        assert drift.get(key) == value, (key, drift.get(key), value)
    assert drift.get("normative_kb_change_required") is False

    registry = load(REGISTRY)
    prior_active = registry.get("active", [])
    resolved = registry.setdefault("resolved", [])
    resolved_ids = {x.get("id") for x in resolved}
    for old in prior_active:
        if old.get("id") in resolved_ids:
            continue
        copy = dict(old)
        copy["state"] = "RESOLVED"
        copy["resolved_at"] = "2026-10-20"
        copy["resolution"] = "Runtime now matches the refreshed current MFM/Wahapedia/BSData projection; preserved as historical drift evidence."
        resolved.append(copy)

    registry["schema_version"] = "2.1"
    registry["as_of"] = "2026-10-20"
    registry["active"] = [{
        "id": "NR_ADEPTUS_CUSTODES_TRAJANN_POINTS_2026_10_20",
        "surface": "points",
        "parent_state": "RUNTIME_PROJECTION_DRIFT",
        "classification": "RUNTIME_PROJECTION_DRIFT",
        "roster_slug": "adeptus_custodes",
        "unit": "Trajann Valoris",
        "normative": {
            "source_id": "GW_MFM",
            "mfm_version": "1.6",
            "official_last_updated": "2026-10-14",
            "points": 265,
            "repository_snapshot": "rules/11e/snapshots/2026-10-20/mfm/factions/adeptus-custodes.json"
        },
        "current_mirror_crosscheck": {
            "source_id": "WAHAPEDIA_11E",
            "last_update": "2026-10-19 03:47:32",
            "points": 265,
            "repository_snapshot": "rules/11e/snapshots/2026-10-20/wahapedia/factions/adeptus_custodes.json"
        },
        "structured_upstream": {
            "source_id": "BSDATA_WH40K_11E",
            "repository": "BSData/wh40k-11e",
            "pinned_revision": "a56674583d9f656a191e4210268c276f133b47d1",
            "pinned_points": 265,
            "live_revision": "a56674583d9f656a191e4210268c276f133b47d1",
            "live_points": 265,
            "file": "Imperium - Adeptus Custodes.json"
        },
        "runtime": {
            "source_id": "NEW_RECRUIT_WIKI",
            "observed_at": "2026-10-20",
            "points": 135,
            "url": drift.get("url"),
            "exact_sync_cadence": "UNKNOWN_NOT_INFERRED"
        },
        "recommended_action": "Investigate New Recruit runtime projection/cache synchronization. Do not modify normative MFM data.",
        "normative_kb_change_required": False,
        "state": "ACTIVE"
    }]
    write(REGISTRY, registry)


def sync_profile_and_current() -> None:
    report = load(REPORT)
    assert report.get("status") in {"PASS", "PASS_WITH_KNOWN_RUNTIME_DRIFT"}, report.get("status")
    points = report["representative_points"]
    surfaces = report["representative_surfaces"]
    assert points.get("new_drift_count") == 0 and surfaces.get("new_drift_count") == 0

    registry = load(SOURCE_REGISTRY)
    bs = source_by_id(registry, "BSDATA_WH40K_11E")["observed_revision"]
    drift_registry = load(REGISTRY)
    active = [x for x in drift_registry.get("active", []) if x.get("state") == "ACTIVE"]
    active_ids = [x["id"] for x in active]

    profile = load(PROFILE)
    profile["schema_version"] = "1.3"
    profile["as_of"] = "2026-10-20"
    profile["status"] = report["status"]
    profile["upstream"]["observed_head"] = {
        "sha": bs["commit_sha"],
        "date": bs.get("commit_date", "2026-10-20"),
        "message": bs.get("message", "Current reviewed BSData revision")
    }
    validation = profile["runtime"]["validation"]
    validation["state"] = report["status"]
    validation["roster_identities_resolved"] = report["universe"]["resolved_runtime_identities"]
    validation["point_samples"] = {
        "checks": points["checks"],
        "matched": points["matched"],
        "known_drifts": points["known_drift_count"],
        "new_drifts": points["new_drift_count"]
    }
    validation["surface_samples"] = {
        "checks": surfaces["checks"],
        "matched": surfaces["matched"],
        "known_drifts": surfaces["known_drift_count"],
        "new_drifts": surfaces["new_drift_count"]
    }
    validation["known_runtime_drifts"] = len(active)
    profile["runtime"]["known_drifts"] = [{
        "id": x["id"],
        "summary": f"{x.get('unit', x.get('object_name'))}: current GW/MFM + mirror + BSData {x.get('normative', {}).get('points', 'present')} vs New Recruit {x.get('runtime', {}).get('points', 'missing')}.",
        "classification": x["classification"],
        "normative_resolution": "Do not change normative KB data.",
        "monitoring": "Daily; exact registered drift is reported, while new/changed drift fails validation."
    } for x in active]
    write(PROFILE, profile)

    current = load(CURRENT)
    nr = current["automation"]["new_recruit_runtime"]
    nr.update({
        "state": report["status"],
        "roster_identities_resolved": report["universe"]["resolved_runtime_identities"],
        "representative_point_checks": points["checks"],
        "representative_point_matches": points["matched"],
        "known_runtime_drifts": len(active),
        "new_runtime_drifts": points["new_drift_count"] + surfaces["new_drift_count"],
        "active_known_drift_ids": active_ids,
        "known_point_drifts": points["known_drift_count"],
        "representative_surface_checks": surfaces["checks"],
        "representative_surface_matches": surfaces["matched"],
        "known_surface_drifts": surfaces["known_drift_count"],
        "exact_sync_cadence": "UNKNOWN_NOT_INFERRED"
    })

    watch = load(WATCH)
    watch_map = {x["source_id"]: x for x in watch.get("github_sources", [])}
    uw = current["automation"]["upstream_change_watch"]
    uw["state"] = "ACTIVE_CHANGE_DETECTED" if watch["status"] == "CHANGE_DETECTED" else "ACTIVE_NO_CHANGE"
    for source_id, key in (("BSDATA_WH40K_11E", "bsdata_wh40k_11e"), ("BSDATA_MFM_11E", "bsdata_mfm_11e")):
        row = watch_map[source_id]
        uw[key] = {
            "pinned": row.get("pinned"),
            "live": row.get("live"),
            "changed": bool(row.get("changed")),
            "relation": row.get("relation_from_pinned_to_live")
        }
    waha = watch.get("wahapedia", {})
    uw["wahapedia"] = {
        "manifest_files_checked": waha.get("manifest_files_checked"),
        "changed_files": len(waha.get("changed_files", [])),
        "last_update_changed": waha.get("live_last_update") != waha.get("snapshot_last_update")
    }
    official = {x["source_id"]: x for x in watch.get("official_sources", [])}
    if "GW_MFM" in official:
        uw["gw_mfm"] = official["GW_MFM"]
    write(CURRENT, current)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["prepare-registry", "sync-current"])
    args = ap.parse_args()
    if args.mode == "prepare-registry":
        prepare_registry()
    else:
        sync_profile_and_current()
