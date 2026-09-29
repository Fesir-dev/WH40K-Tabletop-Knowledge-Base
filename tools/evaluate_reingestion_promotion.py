#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

def evaluate(plan: dict, candidate: dict, expected_plan_id: str | None = None) -> dict:
    reasons = []
    if plan.get("promotion", {}).get("auto_promote") is not False:
        reasons.append("PLAN_AUTO_PROMOTE_NOT_FALSE")
    if candidate.get("auto_promote") is not False:
        reasons.append("CANDIDATE_AUTO_PROMOTE_NOT_FALSE")
    if expected_plan_id and plan.get("plan_id") != expected_plan_id:
        reasons.append("PLAN_ID_MISMATCH")
    if candidate.get("plan_id") != plan.get("plan_id"):
        reasons.append("CANDIDATE_PLAN_ID_MISMATCH")
    if candidate.get("plan_fingerprint") != plan.get("plan_fingerprint"):
        reasons.append("PLAN_FINGERPRINT_MISMATCH")
    if plan.get("blockers"):
        reasons.append("PLAN_HAS_BLOCKERS")
    if candidate.get("forbidden_current_authority_mutations"):
        reasons.append("FORBIDDEN_CURRENT_AUTHORITY_MUTATION")
    if candidate.get("status") != "PASS":
        reasons.append("CANDIDATE_NOT_PASS")
    if candidate.get("promotion_gate") != "ELIGIBLE_FOR_REVIEWED_PROMOTION":
        reasons.append("CANDIDATE_NOT_REVIEW_ELIGIBLE")
    bad_stage = [
        x.get("id")
        for x in candidate.get("stages", [])
        if x.get("status") != "PASS"
    ]
    if bad_stage:
        reasons.append("NON_PASS_STAGES:" + ",".join(str(x) for x in bad_stage))

    state = "ELIGIBLE_FOR_PROMOTION_PR" if not reasons else "BLOCKED"
    return {
        "schema_version": "1.0",
        "plan_id": plan.get("plan_id"),
        "state": state,
        "reasons": reasons,
        "auto_merge": False,
        "auto_promote": False,
        "required_human_action": "Create/review a promotion PR; never merge automatically." if state.startswith("ELIGIBLE") else "Resolve blockers and regenerate candidate.",
    }

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", type=Path, required=True)
    ap.add_argument("--candidate-report", type=Path, required=True)
    ap.add_argument("--expected-plan-id")
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()

    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    candidate = json.loads(args.candidate_report.read_text(encoding="utf-8"))
    result = evaluate(plan, candidate, args.expected_plan_id)
    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0 if result["state"] == "ELIGIBLE_FOR_PROMOTION_PR" else 2

if __name__ == "__main__":
    raise SystemExit(main())
