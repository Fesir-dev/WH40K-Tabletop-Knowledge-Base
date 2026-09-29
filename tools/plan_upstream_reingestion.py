#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

STAGE_DEFS = {
    "WAHAPEDIA_INGEST": {
        "source": "WAHAPEDIA_11E",
        "automation": "AUTOMATED_CANDIDATE",
        "description": "Download current Wahapedia 11E CSV export into an isolated candidate snapshot.",
    },
    "WAVE_B_RECONCILE": {
        "source": "MULTI_SOURCE",
        "automation": "AUTOMATED_CANDIDATE",
        "description": "Reconcile candidate/current Wahapedia structure against current MFM and candidate/current BSData.",
    },
    "WAVE_B_ROSTER_VIEWS": {
        "source": "WAHAPEDIA_11E",
        "automation": "AUTOMATED_CANDIDATE",
        "description": "Build candidate roster-specific structural views.",
    },
    "WAHAPEDIA_SEMANTIC_AUDIT": {
        "source": "WAHAPEDIA_11E",
        "automation": "AUTOMATED_CANDIDATE",
        "description": "Verify candidate semantic fingerprints against the live Wahapedia export.",
    },
    "OFFICIAL_ASSET_AUDIT": {
        "source": "GW_40K_DOWNLOADS",
        "automation": "AUTOMATED_CANDIDATE",
        "description": "When the mirror source catalog changes, verify its referenced official Games Workshop PDF assets before promotion.",
    },
    "BSDATA_FALLBACK_REBUILD": {
        "source": "BSDATA_WH40K_11E",
        "automation": "AUTOMATED_CANDIDATE",
        "description": "Rebuild structured-implementation fallback views at the candidate BSData revision.",
    },
    "MFM_NORMATIVE_REVALIDATION": {
        "source": "GW_MFM",
        "automation": "MANUAL_AUTHORITY_GATE",
        "description": "Revalidate the official MFM revision before any normative promotion from a changed derived extraction.",
    },
}

def bsdata_affected_rosters(bs: dict) -> list[str]:
    files = [x.get("filename") for x in bs.get("files", []) if x.get("filename")]
    if not files:
        return []
    catalog = json.loads((ROOT / "factions" / "catalog.json").read_text(encoding="utf-8"))
    by_path = {x.get("bsdata_path"): x.get("slug") for x in catalog.get("factions", []) if x.get("bsdata_path")}
    all_slugs = sorted(x.get("slug") for x in catalog.get("factions", []) if x.get("slug"))
    affected = set()
    for path in files:
        if path in by_path:
            affected.add(by_path[path])
            continue
        # Shared libraries can affect many catalogues. Unknown data JSON is also
        # treated conservatively rather than guessed.
        if path.startswith("Library") or path.endswith(".json"):
            return all_slugs
    return sorted(affected)


def stable_fingerprint(payload: dict) -> str:
    body = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(body).hexdigest()

def build_plan(watch: dict, candidate_snapshot_date: str) -> dict:
    if watch.get("status") == "NO_CHANGE":
        base = {
            "schema_version": "1.0",
            "state": "NO_ACTION",
            "baseline_snapshot": watch.get("baseline_snapshot"),
            "candidate_snapshot_date": candidate_snapshot_date,
            "changed_sources": [],
            "stages": [],
            "blockers": [],
            "promotion": {
                "auto_promote": False,
                "state": "NOT_APPLICABLE",
            },
        }
        base["plan_fingerprint"] = stable_fingerprint(base)
        base["plan_id"] = "REINGEST_" + base["plan_fingerprint"][:12]
        return base

    github = {x.get("source_id"): x for x in watch.get("github_sources", [])}
    bs = github.get("BSDATA_WH40K_11E", {})
    mfm = github.get("BSDATA_MFM_11E", {})
    waha = watch.get("wahapedia", {})
    waha_changed_files = {x.get("file") for x in waha.get("changed_files", []) if x.get("file")}
    waha_changed = bool(waha_changed_files or watch.get("change_summary", {}).get("wahapedia_last_update_changed"))
    source_catalog_changed = "Source.csv" in waha_changed_files
    bs_changed = bool(bs.get("changed"))
    mfm_changed = bool(mfm.get("changed"))

    changed_sources = []
    if waha_changed:
        changed_sources.append("WAHAPEDIA_11E")
    if bs_changed:
        changed_sources.append("BSDATA_WH40K_11E")
    if mfm_changed:
        changed_sources.append("BSDATA_MFM_11E")

    stage_ids = []
    if waha_changed:
        stage_ids.extend(["WAHAPEDIA_INGEST", "WAVE_B_RECONCILE", "WAVE_B_ROSTER_VIEWS", "WAHAPEDIA_SEMANTIC_AUDIT"])
        if source_catalog_changed:
            stage_ids.append("OFFICIAL_ASSET_AUDIT")
    elif bs_changed:
        stage_ids.append("WAVE_B_RECONCILE")
    if bs_changed:
        stage_ids.append("BSDATA_FALLBACK_REBUILD")
    if mfm_changed:
        stage_ids.append("MFM_NORMATIVE_REVALIDATION")

    # Stable de-dup preserving order.
    stage_ids = list(dict.fromkeys(stage_ids))
    stages = [{"id": sid, **STAGE_DEFS[sid]} for sid in stage_ids]

    blockers = []
    if mfm_changed:
        blockers.append({
            "id": "MFM_OFFICIAL_REVALIDATION_REQUIRED",
            "source": "BSDATA_MFM_11E",
            "severity": "BLOCKING",
            "reason": "A changed derived MFM extraction cannot update normative MFM facts until the official GW MFM revision is revalidated.",
        })

    if not changed_sources:
        blockers.append({
            "id": "UNCLASSIFIED_WATCH_CHANGE",
            "severity": "BLOCKING",
            "reason": "Watcher reported change but no supported source class was resolved.",
        })

    candidate_revisions = {
        "wahapedia": {
            "baseline_last_update": waha.get("snapshot_last_update"),
            "candidate_last_update": waha.get("live_last_update"),
            "changed_files": len(waha.get("changed_files", [])),
            "changed_files_detail": waha.get("changed_files", []),
        },
        "bsdata_wh40k_11e": {
            "pinned": bs.get("pinned"),
            "candidate": bs.get("live"),
            "changed": bs_changed,
            "changed_files_detail": bs.get("files", []),
        },
        "bsdata_mfm_11e": {
            "pinned": mfm.get("pinned"),
            "candidate": mfm.get("live"),
            "changed": mfm_changed,
        },
    }

    promotion_state = "BLOCKED_AUTHORITY_REVALIDATION" if blockers else "REVIEW_REQUIRED_AFTER_CANDIDATE_PASS"
    base = {
        "schema_version": "1.0",
        "state": "CANDIDATE_REQUIRED",
        "baseline_snapshot": watch.get("baseline_snapshot"),
        "candidate_snapshot_date": candidate_snapshot_date,
        "changed_sources": changed_sources,
        "candidate_revisions": candidate_revisions,
        "source_affected_roster_identities": {
            "bsdata_wh40k_11e": bsdata_affected_rosters(bs) if bs_changed else [],
            "wahapedia_11e": [],
        },
        "stages": stages,
        "blockers": blockers,
        "promotion": {
            "auto_promote": False,
            "state": promotion_state,
            "required_review": True,
            "rule": "Candidate generation and reconciliation may be automatic; promotion to current/normative state is never automatic.",
        },
    }
    base["plan_fingerprint"] = stable_fingerprint(base)
    base["plan_id"] = "REINGEST_" + base["plan_fingerprint"][:12]
    return base

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--watch-report", type=Path, default=ROOT / "reports" / "UPSTREAM_CHANGE_WATCH_CURRENT.json")
    ap.add_argument("--candidate-snapshot-date", required=True)
    ap.add_argument("--output", type=Path, default=ROOT / "reports" / "UPSTREAM_REINGESTION_PLAN_CURRENT.json")
    args = ap.parse_args()
    watch = json.loads(args.watch_report.read_text(encoding="utf-8"))
    plan = build_plan(watch, args.candidate_snapshot_date)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"plan_id": plan["plan_id"], "state": plan["state"], "promotion": plan["promotion"]["state"]}, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
