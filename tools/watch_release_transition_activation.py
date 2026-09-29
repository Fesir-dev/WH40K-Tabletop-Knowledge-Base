#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from evaluate_release_transitions import ROOT, build_report, load


ACTION_MAP = {
    "PRE_RELEASE_HOLD": ("NO_ACTION", "WAIT_PRE_RELEASE"),
    "UPCOMING_HOLD_NO_RELEASE_DATE": ("NO_ACTION", "WAIT_OFFICIAL_RELEASE_SIGNAL"),
    "RELEASE_DATE_REACHED_AWAITING_OFFICIAL_CURRENTNESS": (
        "ACTION_REQUIRED",
        "VERIFY_AND_RECORD_OFFICIAL_CURRENT_LEGAL_EVIDENCE",
    ),
    "CURRENT_LEGAL_CONFIRMED_WAITING_UPSTREAM_PROJECTION": (
        "MONITORING",
        "WAIT_FOR_UPSTREAM_PROJECTION_CHANGE",
    ),
    "READY_FOR_GUARDED_REINGESTION": (
        "READY_FOR_CANDIDATE",
        "BUILD_GUARDED_REINGESTION_CANDIDATE",
    ),
}


def build_watch(readiness: dict) -> dict:
    rows = []
    for item in readiness.get("transitions", []):
        watch_state, action = ACTION_MAP.get(
            item.get("state"),
            ("ACTION_REQUIRED", "REVIEW_UNKNOWN_RELEASE_TRANSITION_STATE"),
        )
        rows.append({
            "transition_id": item.get("transition_id"),
            "title": item.get("title"),
            "readiness_state": item.get("state"),
            "watch_state": watch_state,
            "next_action": action,
            "scheduled_release_date": item.get("scheduled_release_date"),
            "current_legal_confirmed": item.get("current_legal_confirmed"),
            "upstream_changed": item.get("upstream_changed"),
            "candidate_eligible": item.get("candidate_eligible"),
            "promotion_eligible": False,
        })

    action_required = [x for x in rows if x["watch_state"] == "ACTION_REQUIRED"]
    ready = [x for x in rows if x["watch_state"] == "READY_FOR_CANDIDATE"]
    monitoring = [x for x in rows if x["watch_state"] == "MONITORING"]

    if ready:
        status = "READY_FOR_GUARDED_CANDIDATE"
    elif action_required:
        status = "ACTION_REQUIRED"
    elif monitoring:
        status = "MONITORING_UPSTREAM_PROJECTION"
    else:
        status = "NO_ACTION_REQUIRED"

    return {
        "schema_version": "1.0",
        "status": status,
        "as_of": readiness.get("as_of"),
        "readiness_milestone": readiness.get("milestone"),
        "watch_status": readiness.get("watch_status"),
        "transitions": rows,
        "summary": {
            "transition_count": len(rows),
            "no_action": sum(x["watch_state"] == "NO_ACTION" for x in rows),
            "action_required": len(action_required),
            "monitoring": len(monitoring),
            "ready_for_candidate": len(ready),
        },
        "safety": {
            "auto_promote": False,
            "direct_current_rules_mutation": False,
            "candidate_generation_only_when_ready": True,
            "promotion_requires_existing_reviewed_promotion_flow": True,
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--as-of", required=True)
    ap.add_argument("--watch-report", type=Path, default=ROOT / "reports" / "UPSTREAM_CHANGE_WATCH_CURRENT.json")
    ap.add_argument("--manifest", action="append", type=Path, default=[])
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()

    manifest_paths = args.manifest or sorted((ROOT / "ingestion" / "release_transitions").glob("*.json"))
    manifests = [load(p if p.is_absolute() else ROOT / p) for p in manifest_paths]
    watch_path = args.watch_report if args.watch_report.is_absolute() else ROOT / args.watch_report
    readiness = build_report(manifests, load(watch_path), date.fromisoformat(args.as_of))
    report = build_watch(readiness)

    payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        out = args.output if args.output.is_absolute() else ROOT / args.output
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
