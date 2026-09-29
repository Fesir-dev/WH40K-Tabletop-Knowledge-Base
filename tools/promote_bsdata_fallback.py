#!/usr/bin/env python3
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATE="2026-09-29"
COV=ROOT/"coverage"/"current.json"
CUR=ROOT/"rules"/"11e"/"current.json"
IDX=ROOT/"rules"/"11e"/"snapshots"/DATE/"bsdata_fallback"/"index.json"

def main():
    idx=json.loads(IDX.read_text(encoding="utf-8"))
    if idx.get("commit_sha")!="951d5900d1b4a952a4ba560a30c43788e622ccfc":
        raise SystemExit("Unexpected BSData fallback commit")
    views={x["slug"]:x for x in idx.get("views",[])}
    if set(views)!={"titanicus_traitoris","unaligned_forces"}:
        raise SystemExit("Unexpected fallback roster identities")

    cov=json.loads(COV.read_text(encoding="utf-8"))
    cov["schema_version"]="1.3"
    cov["global"].update({
        "wave_b_current_mirror_structural_complete":35,
        "wave_b_structured_implementation_fallback_complete":2,
        "wave_b_total_structural_source_available":37,
    })
    for row in cov["factions"]:
        slug=row["slug"]
        row["structural_source_available"]=bool(row.get("structural_current"))
        if slug not in views:
            continue
        view=views[slug]
        row["structural_source_available"]=True
        row["wave_b_structural"]={
            "state":"IMPLEMENTATION_FALLBACK_COMPLETE",
            "source_id":"BSDATA_WH40K_11E",
            "source_role":"structured_implementation",
            "pinned_commit":idx["commit_sha"],
            "view":view["file"],
            "current_mirror_verified":False,
            "normative_rules_verified":False,
            "semantic_rule_text_current_verified":False,
            "faq_errata_current_verified":False,
        }
        if slug=="titanicus_traitoris":
            row["wave_b_structural"]["points_authority"]="GW_MFM"
            row["wave_b_structural"]["points_source_slug"]="chaos-titan-legions"
        else:
            row["wave_b_structural"]["points_authority"]="BSDATA_IMPLEMENTATION_ONLY_NO_MFM_PROJECTION"
    COV.write_text(json.dumps(cov,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

    cur=json.loads(CUR.read_text(encoding="utf-8"))
    wb=cur["wave_b_structural"]
    wb["current_mirror_roster_identities_complete"]=35
    wb["implementation_fallback_roster_identities_complete"]=2
    wb["total_structural_source_available"]=37
    wb["implementation_fallback_snapshot"]="rules/11e/snapshots/2026-09-29/bsdata_fallback/index.json"
    wb["implementation_fallback_policy"]="Fallback provides structured implementation evidence only; it does not promote BSData to normative or current-mirror authority."
    CUR.write_text(json.dumps(cur,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("BSData fallback promotion: PASS")
if __name__=="__main__":
    main()
