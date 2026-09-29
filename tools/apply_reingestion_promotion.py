#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from datetime import date
from pathlib import Path

from release_transition_gate import promotion_blockers

ROOT = Path(__file__).resolve().parents[1]


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def safe_key(value: str) -> str:
    if not value or "/" in value or "\\" in value or ".." in value:
        raise SystemExit(f"Unsafe candidate key: {value!r}")
    return value


def copy_tree(src: Path, dst: Path) -> list[str]:
    copied = []
    if not src.exists():
        return copied
    for p in src.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(src)
        out = dst / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, out)
        copied.append(out.as_posix())
    return copied


def source(registry: dict, sid: str) -> dict:
    hits = [x for x in registry.get("sources", []) if x.get("id") == sid]
    if len(hits) != 1:
        raise SystemExit(f"Expected one source registry entry for {sid}, got {len(hits)}")
    return hits[0]


def check(
    plan: dict,
    report: dict,
    artifact_dir: Path,
    release_state: dict | None = None,
    as_of: date | None = None,
) -> dict:
    if plan.get("state") != "CANDIDATE_REQUIRED":
        raise SystemExit("Promotion requires a CANDIDATE_REQUIRED plan")
    if report.get("plan_id") != plan.get("plan_id"):
        raise SystemExit("Candidate report plan_id does not match reingestion plan")
    if report.get("plan_fingerprint") != plan.get("plan_fingerprint"):
        raise SystemExit("Candidate report fingerprint does not match reingestion plan")
    if report.get("status") != "PASS":
        raise SystemExit(f"Candidate is not promotable: status={report.get('status')}")
    if report.get("promotion_gate") != "ELIGIBLE_FOR_REVIEWED_PROMOTION":
        raise SystemExit(f"Candidate promotion gate is {report.get('promotion_gate')}")
    if report.get("auto_promote") is not False or plan.get("promotion", {}).get("auto_promote") is not False:
        raise SystemExit("auto_promote must remain false")
    if plan.get("blockers"):
        raise SystemExit(f"Promotion has blockers: {plan.get('blockers')}")
    if report.get("forbidden_current_authority_mutations"):
        raise SystemExit("Candidate mutated forbidden current-authority files")
    if "BSDATA_MFM_11E" in plan.get("changed_sources", []):
        raise SystemExit("MFM-derived extraction changes require the separate official authority gate")
    if "affected_roster_identities" not in report:
        raise SystemExit("Candidate lacks affected_roster_identities; regenerate it with the current candidate pipeline")

    if release_state is None:
        release_path = ROOT / "sources" / "release_state.json"
        release_state = load(release_path) if release_path.exists() else {"transitions": []}
    transition_blockers = promotion_blockers(
        release_state,
        report.get("affected_roster_identities", []),
        as_of or date.today(),
    )
    if transition_blockers:
        raise SystemExit(
            "Release transition promotion blocked: "
            + json.dumps(transition_blockers, ensure_ascii=False, sort_keys=True)
        )

    plan_id = safe_key(plan["plan_id"])
    candidate_key = safe_key(plan["candidate_snapshot_date"])
    candidate_root = artifact_dir / "candidate"
    snapshot_root = candidate_root / "rules" / "11e" / "snapshots" / candidate_key
    evidence_root = candidate_root / "ingestion" / "candidates" / plan_id

    changed = set(plan.get("changed_sources", []))
    evidence = {
        "plan_id": plan_id,
        "candidate_key": candidate_key,
        "changed_sources": sorted(changed),
        "snapshot_root": snapshot_root,
        "evidence_root": evidence_root,
        "affected_roster_identities": sorted(report.get("affected_roster_identities", [])),
        "release_transition_blockers": [],
    }

    if "WAHAPEDIA_11E" in changed:
        manifest = load(snapshot_root / "wahapedia" / "manifest.json")
        views = load(snapshot_root / "wahapedia" / "roster_views" / "index.json")
        recon = load(evidence_root / "reconciliation.json")
        sem = load(evidence_root / "semantic_fingerprint_audit.json")
        counts = views.get("counts", {})
        if counts.get("roster_identities") != 37:
            raise SystemExit("Candidate roster-view universe is not 37")
        if counts.get("structural_partial") != 0:
            raise SystemExit("Candidate roster views contain structural partials")
        if recon.get("status") not in {"PASS", "PASS_WITH_CONFLICTS"}:
            raise SystemExit("Candidate reconciliation did not pass")
        if sem.get("status") != "PASS" or sem.get("problems"):
            raise SystemExit("Candidate semantic fingerprint audit did not pass")
        if sem.get("counts", {}).get("MATCH") != sem.get("expected_fingerprints"):
            raise SystemExit("Candidate semantic fingerprint count is incomplete")
        if sem.get("snapshot_last_update") != manifest.get("source", {}).get("last_update"):
            raise SystemExit("Semantic audit and candidate manifest disagree on Wahapedia revision")
        evidence.update({"manifest": manifest, "views": views, "reconciliation": recon, "semantic": sem})

        waha_changed_files = {
            x.get("file") for x in plan.get("candidate_revisions", {}).get("wahapedia", {}).get("changed_files_detail", [])
            if x.get("file")
        }
        official_path = evidence_root / "official_assets.json"
        if "Source.csv" in waha_changed_files and not official_path.exists():
            raise SystemExit("Source.csv changed but candidate has no official asset audit")
        if official_path.exists():
            official = load(official_path)
            if official.get("status") != "PASS":
                raise SystemExit("Candidate official asset audit did not pass")
            if official.get("live_source_csv", {}).get("catalog_drift_count") != 0:
                raise SystemExit("Candidate official Source.csv still drifts from candidate source catalog")
            evidence["official_assets"] = official

    if "BSDATA_WH40K_11E" in changed:
        fallback = load(snapshot_root / "bsdata_fallback" / "index.json")
        expected = plan.get("candidate_revisions", {}).get("bsdata_wh40k_11e", {}).get("candidate")
        if fallback.get("commit_sha") != expected:
            raise SystemExit("Candidate BSData fallback revision does not match plan")
        evidence["fallback"] = fallback

    return evidence


def apply_promotion(repo_root: Path, artifact_dir: Path, promoted_at: str) -> dict:
    plan = load(artifact_dir / "reingestion_plan.json")
    report = load(artifact_dir / "candidate_report.json")
    release_state = load(repo_root / "sources" / "release_state.json")
    ev = check(plan, report, artifact_dir, release_state, date.fromisoformat(promoted_at))

    plan_id = ev["plan_id"]
    candidate_key = ev["candidate_key"]
    changed = set(ev["changed_sources"])
    promotion_root = repo_root / "ingestion" / "promotions" / plan_id
    promotion_root.mkdir(parents=True, exist_ok=True)

    copied = []
    snapshot_src = ev["snapshot_root"]
    snapshot_dst = repo_root / "rules" / "11e" / "snapshots" / candidate_key
    copied += copy_tree(snapshot_src, snapshot_dst)
    copied += copy_tree(ev["evidence_root"], promotion_root / "candidate_evidence")
    shutil.copy2(artifact_dir / "reingestion_plan.json", promotion_root / "reingestion_plan.json")
    shutil.copy2(artifact_dir / "candidate_report.json", promotion_root / "candidate_report.json")

    current_path = repo_root / "rules" / "11e" / "current.json"
    coverage_path = repo_root / "coverage" / "current.json"
    registry_path = repo_root / "sources" / "registry.json"
    gate_path = repo_root / "sources" / "currentness_gate.json"

    current = load(current_path)
    coverage = load(coverage_path)
    registry = load(registry_path)
    gate = load(gate_path)

    current.setdefault("automation", {})["upstream_reingestion"] = {
        "state": "REVIEWED_PROMOTION_APPLIED_PENDING_POST_PROMOTION_WATCH",
        "plan_id": plan_id,
        "candidate_snapshot": candidate_key,
        "promoted_at": promoted_at,
        "auto_promote": False,
        "authority_rule": "Promotion was explicitly dispatched from a PASS candidate; normative GW/MFM authority was not changed.",
    }

    promotion_meta = {
        "schema_version": "1.0",
        "plan_id": plan_id,
        "plan_fingerprint": plan["plan_fingerprint"],
        "candidate_snapshot": candidate_key,
        "promoted_at": promoted_at,
        "changed_sources": sorted(changed),
        "auto_promote": False,
        "normative_mfm_changed": False,
        "copied_files": sorted(str(Path(x).relative_to(repo_root)) for x in copied),
        "pointer_updates": [],
    }

    by_gate = {x.get("id"): x for x in gate.get("required_checks", [])}

    if "WAHAPEDIA_11E" in changed:
        manifest = ev["manifest"]
        views = ev["views"]
        recon = ev["reconciliation"]
        sem = ev["semantic"]
        last_update = manifest["source"]["last_update"]
        view_path = f"rules/11e/snapshots/{candidate_key}/wahapedia/roster_views/index.json"
        recon_path = f"ingestion/promotions/{plan_id}/candidate_evidence/reconciliation.json"
        sem_path = f"ingestion/promotions/{plan_id}/candidate_evidence/semantic_fingerprint_audit.json"

        unavailable = [
            x.get("slug") for x in views.get("views", [])
            if str(x.get("status", "")).startswith("UNAVAILABLE")
        ]
        complete = int(views["counts"]["structural_complete"])

        conflict_doc = {
            "schema_version": "1.0",
            "state": "SOURCE_CONFLICT",
            "source_pair": ["WAHAPEDIA_11E", "GW_MFM"],
            "candidate_snapshot": candidate_key,
            "conflict_count": int(recon.get("conflict_count", 0)),
            "conflicts": recon.get("conflicts", []),
            "resolution_policy": {
                "points": "GW_MFM",
                "detachment_points": "GW_MFM",
                "enhancement_costs": "GW_MFM",
                "wahapedia_role": "secondary current mirror; conflicts retained as drift evidence",
            },
            "source_report": recon_path,
        }
        conflict_path = f"ingestion/promotions/{plan_id}/wave_b_conflicts.json"
        dump(repo_root / conflict_path, conflict_doc)

        wb = current["wave_b_structural"]
        wb.update({
            "snapshot": view_path,
            "wahapedia_last_update": last_update,
            "roster_identities_complete": complete,
            "roster_identities_unavailable": unavailable,
            "reconciliation_report": recon_path,
            "conflict_snapshot": conflict_path,
            "source_conflicts": int(recon.get("conflict_count", 0)),
            "current_mirror_roster_identities_complete": complete,
            "semantic_current_mirror_roster_identities": complete,
            "semantic_rule_text": "CURRENT_SECONDARY_MIRROR_FULL_HASH_VERIFIED",
            "normative_semantic_equivalence": "NOT_CLAIMED",
        })

        current["source_currentness"]["faction_rules_content"].update({
            "state": "SECONDARY_MIRROR_SEMANTICS_FULL_HASH_MATCH",
            "verified_at": promoted_at,
            "secondary_mirror_last_update": last_update,
            "fingerprint_audit": sem_path,
            "expected_fingerprints": sem["expected_fingerprints"],
            "matched_fingerprints": sem["counts"]["MATCH"],
            "problems": len(sem.get("problems", [])),
            "normative_equivalence": "NOT_CLAIMED",
        })
        current["semantic_resolver"]["full_audit"].update({
            "report": sem_path,
            "expected_fingerprints": sem["expected_fingerprints"],
            "matched_fingerprints": sem["counts"]["MATCH"],
            "problems": len(sem.get("problems", [])),
        })

        gc = coverage["global"]
        gc.update({
            "wave_b_wahapedia_last_update": last_update,
            "wave_b_structural_roster_identities_complete": complete,
            "wave_b_structural_roster_identities_unavailable": len(unavailable),
            "wave_b_reconciliation_conflicts": int(recon.get("conflict_count", 0)),
            "wave_b_current_mirror_structural_complete": complete,
            "wave_b_semantic_fingerprint_audit_status": sem["status"],
            "wave_b_semantic_fingerprints_expected": sem["expected_fingerprints"],
            "wave_b_semantic_fingerprints_matched": sem["counts"]["MATCH"],
            "wave_b_semantic_fingerprint_problems": len(sem.get("problems", [])),
            "wave_b_current_mirror_semantic_roster_identities": complete,
        })
        coverage["as_of"] = promoted_at

        view_by_slug = {x.get("slug"): x for x in views.get("views", [])}
        for row in coverage.get("factions", []):
            slug = row.get("slug")
            v = view_by_slug.get(slug)
            if not v or v.get("status") != "STRUCTURAL_COMPLETE":
                continue
            row["structural_current"] = True
            row["structural_source_available"] = True
            row.setdefault("wave_b_structural", {}).update({
                "state": "COMPLETE",
                "source_id": "WAHAPEDIA_11E",
                "source_last_update": last_update,
                "view": v["file"],
                "semantic_rule_text_current_verified": False,
                "faq_errata_current_verified": False,
            })
            row["semantic_current_mirror"] = {
                "state": "FULL_FINGERPRINT_MATCH",
                "source_id": "WAHAPEDIA_11E",
                "source_last_update": last_update,
                "audit_report": sem_path,
                "full_rule_text_embedded": False,
                "on_demand_resolver": "tools/query_current_semantics.py",
                "normative_equivalence_verified": False,
            }

        waha = source(registry, "WAHAPEDIA_11E")
        waha["checked_at"] = promoted_at
        waha["source_health"] = "PASS"
        waha["observed_revision"] = {
            "last_update": last_update,
            "snapshot_date": candidate_key,
            "manifest": f"rules/11e/snapshots/{candidate_key}/wahapedia/manifest.json",
        }

        wg = by_gate["WAHAPEDIA_11E"]
        wg["state"] = "PASS"
        wg["checked_at"] = promoted_at
        wg["semantic_fingerprint_audit"] = {
            "state": "PASS",
            "checked_at": promoted_at,
            "report": sem_path,
            "expected": sem["expected_fingerprints"],
            "matched": sem["counts"]["MATCH"],
            "problems": len(sem.get("problems", [])),
        }
        gate["scope_profiles"]["semantic_mirror_current"]["report"] = sem_path
        gate["scope_profiles"]["semantic_mirror_current"]["content_state"] = "PASS"

        if "official_assets" in ev:
            official = ev["official_assets"]
            official_path = f"ingestion/promotions/{plan_id}/candidate_evidence/official_assets.json"
            off = official["official_assets"]
            current["source_currentness"]["faq_errata_assets"].update({
                "state": "OFFICIAL_ASSETS_VERIFIED",
                "verified_at": promoted_at,
                "report": official_path,
                "edition_11_sources": off["edition_11_sources"],
                "verified_pdf_assets": off["verified_pdf_assets"],
                "failures": off["failures"],
                "source_catalog_drift": official["live_source_csv"]["catalog_drift_count"],
            })
            current["wave_b_structural"]["faq_errata"] = "SOURCE_CATALOG_CURRENT_OFFICIAL_ASSETS_VERIFIED"
            coverage["global"].update({
                "wave_b_official_edition11_sources": off["edition_11_sources"],
                "wave_b_official_pdf_assets_verified": off["verified_pdf_assets"],
                "wave_b_official_pdf_asset_failures": off["failures"],
                "wave_b_source_catalog_drift": official["live_source_csv"]["catalog_drift_count"],
            })
            gate["scope_profiles"]["faq_errata_assets"]["report"] = official_path
            gate["scope_profiles"]["faq_errata_assets"]["content_state"] = "PASS"

        promotion_meta["pointer_updates"].extend([
            "rules/11e/current.json:wave_b_structural",
            "rules/11e/current.json:semantic_resolver",
            "coverage/current.json:wave_b_current_mirror",
            "sources/registry.json:WAHAPEDIA_11E",
            "sources/currentness_gate.json:WAHAPEDIA_11E",
        ])

    if "BSDATA_WH40K_11E" in changed:
        fallback = ev["fallback"]
        commit = fallback["commit_sha"]
        fallback_path = f"rules/11e/snapshots/{candidate_key}/bsdata_fallback/index.json"
        wb = current["wave_b_structural"]
        wb["implementation_fallback_snapshot"] = fallback_path
        wb["implementation_fallback_roster_identities_complete"] = len(fallback.get("views", []))
        wb["total_structural_source_available"] = wb.get("current_mirror_roster_identities_complete", 0) + len(fallback.get("views", []))

        rows = {x.get("slug"): x for x in coverage.get("factions", [])}
        for fv in fallback.get("views", []):
            slug = fv["slug"]
            row = rows.get(slug)
            if not row:
                continue
            row["structural_source_available"] = True
            row["structural_current"] = False
            old = row.setdefault("wave_b_structural", {})
            old.update({
                "state": "IMPLEMENTATION_FALLBACK_COMPLETE",
                "source_id": "BSDATA_WH40K_11E",
                "source_role": "structured_implementation",
                "pinned_commit": commit,
                "view": fv["file"],
                "current_mirror_verified": False,
                "normative_rules_verified": False,
                "semantic_rule_text_current_verified": False,
                "faq_errata_current_verified": False,
            })

        coverage["global"]["wave_b_structured_implementation_fallback_complete"] = len(fallback.get("views", []))
        coverage["global"]["wave_b_total_structural_source_available"] = current["wave_b_structural"]["total_structural_source_available"]

        bs = source(registry, "BSDATA_WH40K_11E")
        bs["checked_at"] = promoted_at
        bs["source_health"] = "PASS"
        bs["observed_revision"] = {
            "commit_sha": commit,
            "promoted_at": promoted_at,
            "observed_via": "AUTOMATED_REINGESTION_REVIEWED_PROMOTION",
        }
        bg = by_gate["BSDATA_WH40K_11E"]
        bg["state"] = "PASS"
        bg["checked_at"] = promoted_at
        bg["observed_commit"] = commit

        promotion_meta["pointer_updates"].extend([
            "rules/11e/current.json:implementation_fallback_snapshot",
            "coverage/current.json:implementation_fallback",
            "sources/registry.json:BSDATA_WH40K_11E",
            "sources/currentness_gate.json:BSDATA_WH40K_11E",
        ])

    auto = current["automation"]["upstream_change_watch"]
    revs = plan.get("candidate_revisions", {})
    if "BSDATA_WH40K_11E" in changed:
        commit = revs["bsdata_wh40k_11e"]["candidate"]
        auto["bsdata_wh40k_11e"] = {"pinned": commit, "live": commit, "changed": False}
    if "WAHAPEDIA_11E" in changed:
        auto["wahapedia"] = {
            "manifest_files_checked": len(ev["manifest"].get("files", [])),
            "changed_files": 0,
            "last_update_changed": False,
        }
    auto["state"] = "ACTIVE_NO_CHANGE"
    auto["auto_promote"] = False

    dump(current_path, current)
    dump(coverage_path, coverage)
    dump(registry_path, registry)
    dump(gate_path, gate)
    dump(promotion_root / "promotion.json", promotion_meta)
    return promotion_meta


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Apply an explicitly reviewed upstream candidate to repository current pointers. Never auto-promotes."
    )
    ap.add_argument("--artifact-dir", type=Path, required=True)
    ap.add_argument("--repo-root", type=Path, default=ROOT)
    ap.add_argument("--promoted-at", required=True)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--proposal-out", type=Path)
    args = ap.parse_args()

    artifact_dir = args.artifact_dir.resolve()
    plan = load(artifact_dir / "reingestion_plan.json")
    report = load(artifact_dir / "candidate_report.json")
    release_state = load(ROOT / "sources" / "release_state.json")
    ev = check(plan, report, artifact_dir, release_state, date.fromisoformat(args.promoted_at))
    proposal = {
        "schema_version": "1.0",
        "plan_id": ev["plan_id"],
        "plan_fingerprint": plan["plan_fingerprint"],
        "candidate_snapshot": ev["candidate_key"],
        "changed_sources": ev["changed_sources"],
        "affected_roster_identities": ev["affected_roster_identities"],
        "release_transition_blockers": ev["release_transition_blockers"],
        "promotion_gate": "ELIGIBLE_FOR_REVIEWED_PROMOTION",
        "auto_promote": False,
        "requires_explicit_apply": True,
    }
    if args.proposal_out:
        dump(args.proposal_out, proposal)
    if not args.apply:
        print(json.dumps(proposal, ensure_ascii=False, indent=2))
        return 0

    meta = apply_promotion(args.repo_root.resolve(), artifact_dir, args.promoted_at)
    print(json.dumps({
        "status": "APPLIED_TO_WORKTREE",
        "plan_id": meta["plan_id"],
        "candidate_snapshot": meta["candidate_snapshot"],
        "auto_promote": False,
        "pointer_updates": meta["pointer_updates"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
