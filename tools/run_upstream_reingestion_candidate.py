#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_MUTATIONS = {
    "coverage/current.json",
    "rules/11e/current.json",
    "sources/currentness_gate.json",
    "sources/registry.json",
    "reports/CURRENT_HANDOFF.md",
}

def run_cmd(workspace: Path, args: list[str]) -> dict:
    p = subprocess.run(args, cwd=workspace, text=True, capture_output=True)
    return {
        "command": args,
        "returncode": p.returncode,
        "stdout_tail": p.stdout[-8000:],
        "stderr_tail": p.stderr[-8000:],
        "status": "PASS" if p.returncode == 0 else "FAIL",
    }

def copy_repo(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(
        src,
        dst,
        ignore=shutil.ignore_patterns(".git", ".cache", "__pycache__", "*.pyc"),
    )

def inventory_files(root: Path) -> dict[str, tuple[int, int]]:
    out = {}
    for p in root.rglob("*"):
        if p.is_file():
            rel = p.relative_to(root).as_posix()
            st = p.stat()
            out[rel] = (st.st_size, int(st.st_mtime_ns))
    return out

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", type=Path, required=True)
    ap.add_argument("--workspace", type=Path, required=True)
    ap.add_argument("--artifact-dir", type=Path, required=True)
    args = ap.parse_args()

    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    artifact_dir = args.artifact_dir.resolve()
    artifact_dir.mkdir(parents=True, exist_ok=True)

    if plan.get("state") == "NO_ACTION":
        report = {
            "schema_version": "1.0",
            "plan_id": plan["plan_id"],
            "status": "NO_ACTION",
            "stages": [],
            "promotion_gate": "NOT_APPLICABLE",
            "auto_promote": False,
        }
        (artifact_dir / "candidate_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        return 0

    workspace = args.workspace.resolve()
    copy_repo(ROOT, workspace)
    before = inventory_files(workspace)

    baseline = plan["baseline_snapshot"]
    candidate_date = plan["candidate_snapshot_date"]
    revisions = plan.get("candidate_revisions", {})
    bs_rev = revisions.get("bsdata_wh40k_11e", {}).get("candidate") or revisions.get("bsdata_wh40k_11e", {}).get("pinned")
    waha_changed = "WAHAPEDIA_11E" in plan.get("changed_sources", [])
    waha_snapshot = candidate_date if waha_changed else baseline

    stage_results = []
    hard_fail = False
    for stage in plan.get("stages", []):
        sid = stage["id"]
        if sid == "MFM_NORMATIVE_REVALIDATION":
            stage_results.append({
                "id": sid,
                "status": "BLOCKED_MANUAL_AUTHORITY_GATE",
                "reason": "Derived MFM extraction changed; official GW MFM revalidation is required before normative ingestion.",
            })
            continue

        commands: list[list[str]] = []
        if sid == "WAHAPEDIA_INGEST":
            commands = [[
                sys.executable, "tools/import_wahapedia_wave_b.py",
                "--download", "--snapshot-date", candidate_date,
            ]]
        elif sid == "WAVE_B_RECONCILE":
            commands = [[
                sys.executable, "tools/crosscheck_wave_b.py",
                "--snapshot-date", candidate_date,
                "--wahapedia-snapshot-date", waha_snapshot,
                "--mfm-snapshot-date", baseline,
                "--fetch-bsdata",
                "--bsdata-commit", bs_rev,
                "--report-path", f"ingestion/candidates/{plan['plan_id']}/reconciliation.json",
            ]]
        elif sid == "WAVE_B_ROSTER_VIEWS":
            commands = [
                [
                    sys.executable, "tools/build_wave_b_roster_views.py",
                    "--snapshot-date", candidate_date,
                    "--mfm-snapshot-date", baseline,
                ],
                [
                    sys.executable, "tools/audit_wave_b_views.py",
                    "--snapshot-date", candidate_date,
                    "--report-path", f"ingestion/candidates/{plan['plan_id']}/view_diagnostics.json",
                ],
            ]
        elif sid == "WAHAPEDIA_SEMANTIC_AUDIT":
            commands = [[
                sys.executable, "tools/audit_semantic_fingerprints.py",
                "--snapshot-date", candidate_date,
                "--report-path", f"ingestion/candidates/{plan['plan_id']}/semantic_fingerprint_audit.json",
            ]]
        elif sid == "BSDATA_FALLBACK_REBUILD":
            commands = [[
                sys.executable, "tools/build_bsdata_fallback_views.py",
                "--snapshot-date", candidate_date,
                "--mfm-snapshot-date", baseline,
                "--bsdata-commit", bs_rev,
            ]]
        elif sid == "OFFICIAL_ASSET_AUDIT":
            commands = [[
                sys.executable, "tools/audit_official_11e_assets.py",
                "--snapshot-date", candidate_date,
                "--report-path", f"ingestion/candidates/{plan['plan_id']}/official_assets.json",
            ]]
        else:
            stage_results.append({"id": sid, "status": "FAIL", "reason": "Unsupported stage id"})
            hard_fail = True
            continue

        command_results = []
        for command in commands:
            result = run_cmd(workspace, command)
            command_results.append(result)
            if result["returncode"] != 0:
                hard_fail = True
                break
        stage_results.append({
            "id": sid,
            "status": "PASS" if command_results and all(x["returncode"] == 0 for x in command_results) else "FAIL",
            "commands": command_results,
        })
        if hard_fail:
            break

    after = inventory_files(workspace)
    changed = sorted(
        path for path, sig in after.items()
        if path not in before or before[path] != sig
    )
    forbidden = sorted(set(changed) & FORBIDDEN_MUTATIONS)
    if forbidden:
        hard_fail = True

    candidate_root = artifact_dir / "candidate"
    candidate_root.mkdir(parents=True, exist_ok=True)
    wanted_prefixes = [
        f"rules/11e/snapshots/{candidate_date}/",
        f"ingestion/candidates/{plan['plan_id']}/",
        f"ingestion/runs/{candidate_date}_",
        ".cache/wahapedia11e/",
    ]
    copied = []
    for rel in changed:
        if any(rel.startswith(prefix) for prefix in wanted_prefixes):
            src = workspace / rel
            dst = candidate_root / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            copied.append(rel)

    blocked = bool(plan.get("blockers")) or any(x.get("status") == "BLOCKED_MANUAL_AUTHORITY_GATE" for x in stage_results)
    if hard_fail:
        promotion_gate = "CANDIDATE_FAILED"
        status = "FAIL"
    elif blocked:
        promotion_gate = "BLOCKED_AUTHORITY_REVALIDATION"
        status = "PASS_WITH_BLOCKER"
    else:
        promotion_gate = "ELIGIBLE_FOR_REVIEWED_PROMOTION"
        status = "PASS"

    report = {
        "schema_version": "1.0",
        "plan_id": plan["plan_id"],
        "plan_fingerprint": plan["plan_fingerprint"],
        "status": status,
        "candidate_snapshot_date": candidate_date,
        "changed_sources": plan.get("changed_sources", []),
        "stages": stage_results,
        "changed_files_in_isolated_workspace": changed,
        "artifact_files": copied,
        "forbidden_current_authority_mutations": forbidden,
        "promotion_gate": promotion_gate,
        "auto_promote": False,
        "authority_rule": "This run produces candidate evidence only. It never mutates or promotes repository current/normative state.",
    }
    (artifact_dir / "candidate_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    shutil.copy2(args.plan, artifact_dir / "reingestion_plan.json")
    print(json.dumps({"status": status, "promotion_gate": promotion_gate, "artifact_files": len(copied)}, ensure_ascii=False))
    return 2 if hard_fail else 0

if __name__ == "__main__":
    raise SystemExit(main())
