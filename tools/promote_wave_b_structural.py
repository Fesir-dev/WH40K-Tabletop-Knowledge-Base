#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATE="2026-09-29"
VIEW_INDEX=ROOT/"rules"/"11e"/"snapshots"/DATE/"wahapedia"/"roster_views"/"index.json"
COVERAGE=ROOT/"coverage"/"current.json"
CURRENT=ROOT/"rules"/"11e"/"current.json"
REGISTRY=ROOT/"sources"/"registry.json"
RECON=ROOT/"reports"/f"WAVE_B_RECONCILIATION_{DATE}.json"
CONFLICTS=ROOT/"sources"/"snapshots"/f"{DATE}_wave_b_conflicts.json"
CLOSURE=ROOT/"reports"/f"WAVE_B_STRUCTURAL_CLOSURE_{DATE}.md"

STRUCTURAL_DIMS=[
    "roster_view",
    "datasheet_index",
    "model_profiles",
    "weapon_profiles",
    "keyword_index",
    "ability_index",
    "options_index",
    "unit_composition_index",
    "leader_graph",
    "detachment_index",
    "enhancement_index",
    "stratagem_index",
]

def main():
    idx=json.loads(VIEW_INDEX.read_text(encoding="utf-8"))
    expected={"roster_identities":37,"structural_complete":35,"structural_partial":0,"unavailable":2}
    if idx.get("counts")!=expected:
        raise SystemExit(f"Wave B view contract not satisfied: {idx.get('counts')} != {expected}")
    unavailable={x["slug"] for x in idx["views"] if str(x.get("status","")).startswith("UNAVAILABLE")}
    if unavailable!={"titanicus_traitoris","unaligned_forces"}:
        raise SystemExit(f"Unexpected unavailable roster views: {sorted(unavailable)}")
    by_slug={x["slug"]:x for x in idx["views"]}

    recon=json.loads(RECON.read_text(encoding="utf-8"))
    if recon.get("status") not in {"PASS","PASS_WITH_CONFLICTS"}:
        raise SystemExit("Wave B reconciliation has not passed")

    cov=json.loads(COVERAGE.read_text(encoding="utf-8"))
    cov["schema_version"]="1.2"
    cov["status"]="WAVE_B_STRUCTURAL_COMPLETE"
    cov["structural_dimensions"]=STRUCTURAL_DIMS
    cov["global"].update({
        "wave_b_wahapedia_last_update":idx["wahapedia_last_update"],
        "wave_b_structural_roster_identities_complete":35,
        "wave_b_structural_roster_identities_unavailable":2,
        "wave_b_reconciliation_conflicts":recon.get("conflict_count",0),
        "full_semantic_current_factions":0,
    })
    for row in cov["factions"]:
        slug=row["slug"]
        view=by_slug[slug]
        complete=view.get("status")=="STRUCTURAL_COMPLETE"
        row["structural_current"]=complete
        if complete:
            row["wave_b_structural"]={
                "state":"COMPLETE",
                "source_id":"WAHAPEDIA_11E",
                "source_last_update":idx["wahapedia_last_update"],
                "view":view["file"],
                "dimensions":{k:100 for k in STRUCTURAL_DIMS},
                "semantic_rule_text_current_verified":False,
                "faq_errata_current_verified":False,
            }
        else:
            row["wave_b_structural"]={
                "state":"UNAVAILABLE",
                "source_id":"WAHAPEDIA_11E",
                "reason":view.get("reason","no mapped structural roster view"),
                "dimensions":{k:0 for k in STRUCTURAL_DIMS},
                "semantic_rule_text_current_verified":False,
                "faq_errata_current_verified":False,
            }
    COVERAGE.write_text(json.dumps(cov,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

    cur=json.loads(CURRENT.read_text(encoding="utf-8"))
    cur["schema_version"]="2.2"
    cur["status"]="CURRENT_STRUCTURAL_READY_SEMANTIC_PENDING"
    cur["source_currentness"]["faction_rules_content"]={
        "state":"STRUCTURAL_PASS_SEMANTIC_PENDING",
        "verified_at":DATE,
        "secondary_mirror_last_update":idx["wahapedia_last_update"],
    }
    cur["wave_b_structural"]={
        "state":"CURRENT_SECONDARY_MIRROR_STRUCTURAL",
        "snapshot":"rules/11e/snapshots/2026-09-29/wahapedia/roster_views/index.json",
        "wahapedia_last_update":idx["wahapedia_last_update"],
        "roster_identities_complete":35,
        "roster_identities_unavailable":["titanicus_traitoris","unaligned_forces"],
        "reconciliation_report":"reports/WAVE_B_RECONCILIATION_2026-09-29.json",
        "source_conflicts":recon.get("conflict_count",0),
        "authority_rule":"GW MFM remains normative for points, detachment points and enhancement costs when Wahapedia differs.",
        "semantic_rule_text":"PENDING",
        "faq_errata":"PENDING",
    }
    cur["next_milestone"]="WAVE_B_SEMANTIC_AND_FAQ_CURRENTNESS"
    CURRENT.write_text(json.dumps(cur,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

    reg=json.loads(REGISTRY.read_text(encoding="utf-8"))
    for src in reg.get("sources",[]):
        if src.get("id")=="WAHAPEDIA_11E":
            src["repository_coverage_state"]="STRUCTURAL_INGESTED"
            src["observed_revision"]={
                "last_update":idx["wahapedia_last_update"],
                "snapshot_date":DATE,
                "manifest":"rules/11e/snapshots/2026-09-29/wahapedia/manifest.json",
            }
            uses=set(src.get("use_for",[]))
            uses.update(["csv_structural_ingestion","roster_structural_views"])
            src["use_for"]=sorted(uses)
    REGISTRY.write_text(json.dumps(reg,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

    conflict_doc={
        "schema_version":"1.0",
        "snapshot_date":DATE,
        "state":"SOURCE_CONFLICT",
        "source_pair":["WAHAPEDIA_11E","GW_MFM"],
        "conflict_count":recon.get("conflict_count",0),
        "resolution_policy":{
            "points":"GW_MFM",
            "detachment_points":"GW_MFM",
            "enhancement_costs":"GW_MFM",
            "wahapedia_role":"secondary current mirror; conflicts retained as drift evidence",
        },
        "conflicts":recon.get("conflicts",[]),
        "source_report":"reports/WAVE_B_RECONCILIATION_2026-09-29.json",
    }
    CONFLICTS.parent.mkdir(parents=True,exist_ok=True)
    CONFLICTS.write_text(json.dumps(conflict_doc,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

    t=recon["totals"]
    md=f"""# Wave B structural closure — 2026-09-29

## Status

**STRUCTURAL COMPLETE: 35 / 37 roster identities.**

Unavailable in the Wahapedia 11E roster projection:

- `titanicus_traitoris`
- `unaligned_forces`

No roster view remains partially resolved.

## Source snapshot

- Wahapedia 11E CSV last update: `{idx["wahapedia_last_update"]}`
- MFM normative version: `1.4`
- BSData diagnostic commit: `{recon.get("bsdata_commit")}`

The public repository stores structured characteristics, names, IDs, links and fingerprints. Long copyrighted rules prose is not vendored verbatim.

## Reconciliation

- roster/faction views compared: {t.get("factions_compared")}
- MFM unit names: {t.get("mfm_unit_names")}
- Wahapedia unit names in compared views: {t.get("wahapedia_unit_names")}
- matching unit names: {t.get("unit_name_matches")}
- point signatures compared: {t.get("points_compared")}
- point conflicts retained: {t.get("point_mismatches")}
- detachment matches: {t.get("detachment_matches")}
- detachment-point conflicts retained: {t.get("dp_mismatches")}
- enhancement matches: {t.get("enhancement_matches")}
- enhancement-cost conflicts retained: {t.get("enhancement_cost_mismatches")}

Total retained source conflicts: **{recon.get("conflict_count",0)}**.

For cost-bearing conflicts, Games Workshop MFM remains normative.

## Meaning of closure

Wave B **structural** coverage is production-ready for the 35 mapped roster identities:

- roster membership;
- datasheet index;
- model characteristics;
- weapon profiles;
- keyword index;
- ability linkage/index;
- wargear/options linkage;
- unit composition linkage;
- leader graph;
- detachment index;
- enhancement index;
- stratagem index.

This closure does **not** claim complete current semantic rules text or complete FAQ/errata normalization. Those remain the next milestone and therefore `current_normalized_factions` intentionally remains 0.
"""
    CLOSURE.write_text(md,encoding="utf-8")
    print("Wave B structural promotion: PASS")

if __name__=="__main__":
    main()
