#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate_transition(manifest: dict, watch: dict, as_of: date) -> dict:
    activation = manifest.get("activation_evidence", {})
    confirmed = activation.get("current_legal_confirmed") is True
    release_raw = manifest.get("scheduled_release_date")
    release_date = date.fromisoformat(release_raw) if release_raw else None

    summary = watch.get("change_summary", {})
    upstream_changed = bool(
        summary.get("github_sources_changed")
        or summary.get("wahapedia_files_changed")
        or summary.get("wahapedia_last_update_changed")
    )

    if confirmed:
        if upstream_changed:
            state = "READY_FOR_GUARDED_REINGESTION"
            action = "BUILD_ISOLATED_CANDIDATE"
        else:
            state = "CURRENT_LEGAL_CONFIRMED_WAITING_UPSTREAM_PROJECTION"
            action = "WAIT_FOR_UPSTREAM_CHANGE"
    elif release_date is None:
        state = "UPCOMING_HOLD_NO_RELEASE_DATE"
        action = "WAIT_FOR_OFFICIAL_CURRENT_LEGAL_EVIDENCE"
    elif as_of < release_date:
        state = "PRE_RELEASE_HOLD"
        action = "WAIT_UNTIL_RELEASE_DATE_THEN_RECHECK_OFFICIAL_CURRENTNESS"
    else:
        state = "RELEASE_DATE_REACHED_AWAITING_OFFICIAL_CURRENTNESS"
        action = "REQUIRE_OFFICIAL_CURRENT_LEGAL_CONFIRMATION"

    promotion_eligible = state == "READY_FOR_GUARDED_REINGESTION"
    return {
        "transition_id": manifest["transition_id"],
        "title": manifest["title"],
        "factions": manifest["factions"],
        "as_of": as_of.isoformat(),
        "baseline_current_state": manifest["baseline_current_state"],
        "upcoming_state": manifest["upcoming_state"],
        "scheduled_release_date": release_raw,
        "date_confidence": manifest.get("date_confidence"),
        "current_legal_confirmed": confirmed,
        "upstream_changed": upstream_changed,
        "state": state,
        "next_action": action,
        "candidate_eligible": promotion_eligible,
        "promotion_eligible": False,
        "authority_boundary": {
            "date_alone_never_promotes": True,
            "preview_never_promotes": True,
            "requires_official_current_legal_evidence": True,
            "requires_upstream_change_before_candidate": True,
            "candidate_route": "GUARDED_REINGESTION_CANDIDATE_REVIEWED_PROMOTION",
            "direct_current_mutation": False,
        },
    }


def build_report(manifests: list[dict], watch: dict, as_of: date) -> dict:
    rows = [evaluate_transition(m, watch, as_of) for m in manifests]
    return {
        "schema_version": "1.0",
        "status": "PASS",
        "as_of": as_of.isoformat(),
        "milestone": "RELEASE_TRANSITION_INGESTION_READINESS",
        "watch_status": watch.get("status"),
        "transitions": rows,
        "summary": {
            "transition_count": len(rows),
            "pre_release_hold": sum(x["state"] == "PRE_RELEASE_HOLD" for x in rows),
            "no_release_date_hold": sum(x["state"] == "UPCOMING_HOLD_NO_RELEASE_DATE" for x in rows),
            "awaiting_official_currentness": sum(
                x["state"] == "RELEASE_DATE_REACHED_AWAITING_OFFICIAL_CURRENTNESS" for x in rows
            ),
            "candidate_ready": sum(x["state"] == "READY_FOR_GUARDED_REINGESTION" for x in rows),
        },
        "global_policy": {
            "calendar_date_is_not_currentness_evidence": True,
            "preview_or_preorder_is_not_currentness_evidence": True,
            "official_current_legal_confirmation_required": True,
            "upstream_projection_change_required_for_candidate": True,
            "auto_promote": False,
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--as-of", required=True)
    ap.add_argument(
        "--manifest",
        action="append",
        type=Path,
        default=[],
        help="Release transition manifest; repeatable. Defaults to all JSON manifests.",
    )
    ap.add_argument(
        "--watch-report",
        type=Path,
        default=ROOT / "reports" / "UPSTREAM_CHANGE_WATCH_CURRENT.json",
    )
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()

    as_of = date.fromisoformat(args.as_of)
    paths = args.manifest or sorted((ROOT / "ingestion" / "release_transitions").glob("*.json"))
    manifests = [load(p if p.is_absolute() else ROOT / p) for p in paths]
    watch = load(args.watch_report if args.watch_report.is_absolute() else ROOT / args.watch_report)
    report = build_report(manifests, watch, as_of)
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
