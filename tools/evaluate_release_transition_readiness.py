#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from release_transition_gate import evaluate_release_state

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--release-state", type=Path, default=ROOT / "sources" / "release_state.json")
    ap.add_argument("--as-of", default=date.today().isoformat())
    ap.add_argument("--output", type=Path)
    ap.add_argument("--fail-on-official-recheck", action="store_true")
    args = ap.parse_args()

    release_state_path = args.release_state.resolve()
    release_state = json.loads(release_state_path.read_text(encoding="utf-8"))
    try:
        source_display = release_state_path.relative_to(ROOT).as_posix()
    except ValueError:
        source_display = str(release_state_path)
    result = evaluate_release_state(release_state, date.fromisoformat(args.as_of))
    result.update({
        "schema_version": "1.0",
        "status": "OFFICIAL_RECHECK_REQUIRED" if result["official_rechecks_due"] else "HOLD_OR_STABLE",
        "release_state_source": source_display,
        "authority_rule": "Release dates and previews are recheck signals only. Games Workshop evidence must explicitly authorize promotion.",
        "promotion_route": "GUARDED_REINGESTION_CANDIDATE_TO_REVIEWED_PROMOTION",
    })
    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")

    if args.fail_on_official_recheck and result["official_rechecks_due"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
