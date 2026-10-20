#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-10-20"
MFM_VERSION = "1.6"
MFM_UPDATED = "2026-10-14"
MFM_URL = "https://mfm.warhammer-community.com/en/"
WAHA_LAST_UPDATE = "2026-10-19 03:47:32"
BSDATA_SHA = "a56674583d9f656a191e4210268c276f133b47d1"
PROMOTION_ID = "REINGEST_49496d868bd7"
PROMOTION_ROOT = ROOT / "ingestion" / "promotions" / PROMOTION_ID
MANIFESTS = [
    ROOT / "ingestion" / "release_transitions" / "space_marines_codex_2026.json",
    ROOT / "ingestion" / "release_transitions" / "adeptus_custodes_codex_2026.json",
]
SCOPED_DIMENSIONS = [
    "points",
    "unit_sizes",
    "detachment_catalog",
    "detachment_points",
    "force_dispositions",
    "current_roster_structure",
]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def verify_current_evidence():
    current = load(ROOT / "rules" / "11e" / "current.json")
    mfm = current["wave_a_mfm"]
    assert mfm["version"] == MFM_VERSION, mfm
    assert mfm["last_updated"] == MFM_UPDATED, mfm
    assert mfm["snapshot"] == "rules/11e/snapshots/2026-10-20/mfm/index.json", mfm
    wave_b = current["wave_b_structural"]
    assert wave_b["wahapedia_last_update"] == WAHA_LAST_UPDATE, wave_b
    assert wave_b["bsdata_commit"] == BSDATA_SHA, wave_b
    assert PROMOTION_ROOT.exists(), PROMOTION_ROOT
    report = load(ROOT / "reports" / "UPSTREAM_CHANGE_WATCH_CURRENT.json")
    assert report["status"] == "NO_CHANGE", report["status"]
    return current


def patch_manifest(path: Path):
    data = load(path)
    activation = data.setdefault("activation_evidence", {})
    # Deliberately keep the legacy full-current boolean false: public evidence here
    # establishes current MFM/roster dimensions, not complete Codex/app wording.
    activation["current_legal_confirmed"] = False
    activation["scoped_current_legal_confirmed"] = True
    activation["confirmed_at"] = DATE
    activation["scope"] = SCOPED_DIMENSIONS
    activation["full_codex_app_semantics_confirmed"] = False
    activation["full_codex_app_semantics_state"] = "PENDING_AUTHORIZED_APP_EVIDENCE"
    activation["evidence"] = [
        {
            "authority": "GAMES_WORKSHOP_OFFICIAL",
            "source_id": "GW_MFM",
            "url": MFM_URL,
            "version": MFM_VERSION,
            "published_or_updated_at": MFM_UPDATED,
            "confirmed_at": DATE,
            "scope": ["points", "unit_sizes", "detachment_catalog", "detachment_points", "force_dispositions"],
            "note": "Official current MFM v1.6 establishes the scoped current-legal MFM dimensions for this transition. It does not establish complete Codex/app wording equivalence."
        }
    ]
    data["transition_state"] = "CURRENT_SCOPED_RECONCILED"
    data["reviewed_promotion"] = {
        "applied": True,
        "promotion_id": PROMOTION_ID,
        "promoted_at": DATE,
        "wahapedia_last_update": WAHA_LAST_UPDATE,
        "bsdata_commit": BSDATA_SHA,
        "scope": "SECONDARY_MIRROR_AND_STRUCTURED_PROJECTION",
        "normative_authority": False,
    }
    data["closure"] = {
        "state": "CURRENT_SCOPED_RECONCILED",
        "closed_at": DATE,
        "points_and_roster_dimensions_current": True,
        "full_codex_app_semantics_current_verified": False,
        "remaining_gap": "AUTHORIZED_GW_APP_OR_CODEX_WORDING",
        "auto_promote": False,
    }
    write(path, data)
    return data


def patch_release_state(manifests):
    path = ROOT / "sources" / "release_state.json"
    state = load(path)
    state["schema_version"] = "1.3"
    state["as_of"] = DATE
    by_id = {m["transition_id"]: m for m in manifests}
    for row in state["transitions"]:
        if row["id"] not in by_id:
            continue
        m = by_id[row["id"]]
        row["checked_at"] = DATE
        row["readiness_state"] = "CURRENT_SCOPED_RECONCILED"
        row["current_legal_confirmation"] = False
        row["scoped_current_legal_confirmation"] = True
        row["scoped_current_legal_dimensions"] = SCOPED_DIMENSIONS
        row["reviewed_promotion_id"] = PROMOTION_ID
        row["full_codex_app_semantics"] = "PENDING_AUTHORIZED_APP_EVIDENCE"
        row["upcoming_state"] = None
    state["transition_policy"]["state"] = "OPERATIONAL_READINESS_V1_SCOPED_RELEASES_RECONCILED"
    state["transition_policy"]["current_scope_rule"] = "Scoped official MFM currentness plus completed reviewed upstream promotion may close a transition for declared MFM/roster dimensions without claiming full Codex/app semantic equivalence."
    state["activation_watch"]["current_status"] = "NO_ACTION_REQUIRED"
    state["activation_watch"]["latest_scoped_closure"] = DATE
    write(path, state)


def write_closure(manifests):
    payload = {
        "schema_version": "1.0",
        "status": "PASS_SCOPED_RELEASE_TRANSITIONS_RECONCILED",
        "as_of": DATE,
        "mfm": {"version": MFM_VERSION, "official_last_updated": MFM_UPDATED, "source": MFM_URL},
        "secondary_projection": {"wahapedia_last_update": WAHA_LAST_UPDATE, "bsdata_commit": BSDATA_SHA, "reviewed_promotion_id": PROMOTION_ID},
        "transitions": [
            {
                "transition_id": m["transition_id"],
                "state": m["transition_state"],
                "scheduled_release_date": m.get("scheduled_release_date"),
                "scoped_current_legal_confirmed": m["activation_evidence"]["scoped_current_legal_confirmed"],
                "full_codex_app_semantics_confirmed": False,
            }
            for m in manifests
        ],
        "scope": SCOPED_DIMENSIONS,
        "authority_boundary": {
            "official_mfm_is_normative_within_scope": True,
            "wahapedia_and_bsdata_are_projection_evidence_only": True,
            "full_codex_app_equivalence_claimed": False,
            "preview_or_preorder_promoted_directly": False,
            "auto_promote": False,
        },
    }
    write(ROOT / "reports" / "RELEASE_TRANSITION_SCOPED_CLOSURE_CURRENT.json", payload)
    md = (
        "# Release transition scoped closure — 2026-10-20\n\n"
        "Space Marines 2026 and Adeptus Custodes 2026 release transitions are closed for declared MFM/roster dimensions only.\n\n"
        f"- Official MFM: **v{MFM_VERSION}**, updated **{MFM_UPDATED}**.\n"
        f"- Wahapedia current mirror: **{WAHA_LAST_UPDATE}**.\n"
        f"- BSData reviewed structured revision: `{BSDATA_SHA}`.\n"
        f"- Reviewed promotion: `{PROMOTION_ID}`.\n"
        "- Full Codex/App wording equivalence: **NOT CLAIMED / pending authorized app evidence**.\n"
        "- Preview/preorder material was not promoted directly.\n"
        "- Auto-promotion remains disabled.\n"
    )
    (ROOT / "reports" / "RELEASE_TRANSITION_SCOPED_CLOSURE_2026-10-20.md").write_text(md, encoding="utf-8")


def main():
    verify_current_evidence()
    manifests = [patch_manifest(p) for p in MANIFESTS]
    patch_release_state(manifests)
    write_closure(manifests)
    print(json.dumps({"status":"PASS","transitions":[m["transition_id"] for m in manifests],"scope":SCOPED_DIMENSIONS}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
