#!/usr/bin/env python3
from __future__ import annotations
import json, re, unicodedata
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATE="2026-09-29"
WROOT=ROOT/"rules"/"11e"/"snapshots"/DATE/"wahapedia"
MROOT=ROOT/"rules"/"11e"/"snapshots"/DATE/"mfm"
OUT=WROOT/"roster_views"

SPACE_MARINE_CHILDREN={
    "black_templars","blood_angels","dark_angels","deathwatch",
    "imperial_fists","iron_hands","raven_guard","salamanders",
    "space_wolves","ultramarines","white_scars",
}
UNAVAILABLE={"titanicus_traitoris","unaligned_forces"}

def norm(v):
    v=unicodedata.normalize("NFKD",v or "")
    v=v.replace("’","'").replace("‘","'").replace("–","-").replace("—","-")
    return " ".join(re.sub(r"[^a-z0-9]+"," ",v.casefold()).split())

def choose_ds(candidates, mfm_unit):
    if len(candidates)==1:
        return candidates[0]
    legends=bool(mfm_unit.get("legends"))
    def score(ds):
        src=(ds.get("source_name") or "").casefold()
        edition=str(ds.get("source_edition") or "")
        s=0
        if legends:
            if "legends" in src: s+=20
            if edition in {"0","10"}: s+=5
        else:
            if edition=="11": s+=20
            if "legends" not in src: s+=5
        return s
    return sorted(candidates,key=score,reverse=True)[0]

def main():
    catalog=json.loads((ROOT/"factions"/"catalog.json").read_text(encoding="utf-8"))
    manifest=json.loads((WROOT/"manifest.json").read_text(encoding="utf-8"))
    w_entries={x.get("repository_slug"):x for x in manifest["factions"] if x.get("repository_slug")}
    OUT.mkdir(parents=True,exist_ok=True)
    index=[]
    for cat in catalog["factions"]:
        slug=cat["slug"]
        if slug in UNAVAILABLE:
            index.append({"slug":slug,"status":"UNAVAILABLE_IN_WAHAPEDIA_11E_ROSTER_PROJECTION","reason":"no mapped Wahapedia 11E roster view"})
            continue

        wslug="space_marines" if slug in SPACE_MARINE_CHILDREN else slug
        wentry=w_entries.get(wslug)
        mslug=cat.get("mfm_source_slug")
        mpath=MROOT/"factions"/f"{mslug}.json" if mslug else None
        if not wentry or not mpath or not mpath.exists():
            index.append({"slug":slug,"status":"UNAVAILABLE","wahapedia_source_slug":wslug,"mfm_source_slug":mslug})
            continue

        w=json.loads((ROOT/wentry["file"]).read_text(encoding="utf-8"))
        m=json.loads(mpath.read_text(encoding="utf-8"))
        m_units=m.get("units",[])
        if cat.get("mfm_view_mode")=="base_plus_group":
            group=cat.get("mfm_group_title")
            m_units=[u for u in m_units if not u.get("groupTitle") or u.get("groupTitle")==group]

        wb=defaultdict(list)
        for ds in w.get("datasheets",[]):
            wb[norm(ds.get("name"))].append(ds)

        selected=[]; unresolved=[]
        for u in m_units:
            candidates=wb.get(norm(u.get("name")),[])
            if not candidates:
                unresolved.append(u.get("name"))
                continue
            ds=choose_ds(candidates,u)
            selected.append({
                "datasheet_id":ds.get("id"),
                "name":ds.get("name"),
                "mfm_name":u.get("name"),
                "legends":bool(u.get("legends")),
                "source_id":ds.get("source_id"),
                "source_name":ds.get("source_name"),
                "source_edition":ds.get("source_edition"),
                "source_version":ds.get("source_version"),
            })

        m_det_names={norm(x.get("name")) for x in m.get("detachments",[]) if x.get("name")}
        w_det=[x for x in w.get("detachments",[]) if norm(x.get("name")) in m_det_names]
        det_ids={x.get("id") for x in w_det if x.get("id")}
        det_names={norm(x.get("name")) for x in w_det if x.get("name")}

        enh=[x for x in w.get("enhancements",[]) if (x.get("detachment_id") in det_ids) or (norm(x.get("detachment")) in det_names)]
        strat=[x for x in w.get("stratagems",[]) if (x.get("detachment_id") in det_ids) or (norm(x.get("detachment")) in det_names)]

        selected_ids={x["datasheet_id"] for x in selected if x.get("datasheet_id")}
        ds_by_id={x.get("id"):x for x in w.get("datasheets",[])}
        structural_counts={
            "datasheets":len(selected),
            "mfm_units":len(m_units),
            "unresolved_mfm_units":len(unresolved),
            "current_edition_11_datasheets":sum(1 for x in selected if str(x.get("source_edition"))=="11"),
            "legends_datasheets":sum(1 for x in selected if x.get("legends")),
            "model_profiles":sum(len(ds_by_id.get(i,{}).get("models",[])) for i in selected_ids),
            "weapon_profiles":sum(len(ds_by_id.get(i,{}).get("weapons",[])) for i in selected_ids),
            "keyword_rows":sum(len(ds_by_id.get(i,{}).get("keywords",[])) for i in selected_ids),
            "datasheet_ability_rows":sum(len(ds_by_id.get(i,{}).get("abilities",[])) for i in selected_ids),
            "option_rows":sum(len(ds_by_id.get(i,{}).get("options",[])) for i in selected_ids),
            "unit_composition_rows":sum(len(ds_by_id.get(i,{}).get("unit_composition",[])) for i in selected_ids),
            "leader_links":sum(len(ds_by_id.get(i,{}).get("leader_links",[])) for i in selected_ids),
            "detachments":len(w_det),
            "enhancements":len(enh),
            "stratagems":len(strat),
        }
        payload={
            "schema_version":"1.0",
            "snapshot_date":DATE,
            "roster_slug":slug,
            "wahapedia_source_slug":wslug,
            "wahapedia_last_update":manifest["source"]["last_update"],
            "mfm_source_slug":mslug,
            "mfm_version":m.get("mfm_version"),
            "mfm_view_mode":cat.get("mfm_view_mode"),
            "mfm_group_title":cat.get("mfm_group_title"),
            "status":"STRUCTURAL_COMPLETE" if not unresolved else "STRUCTURAL_PARTIAL",
            "authority":{
                "points_and_costs":"GW_MFM",
                "rules_structure":"WAHAPEDIA_11E_CSV_SECONDARY_MIRROR",
                "bsdata":"DIAGNOSTIC_IMPLEMENTATION_ONLY",
            },
            "datasheets":selected,
            "detachment_ids":[x.get("id") for x in w_det if x.get("id")],
            "enhancement_ids":[x.get("id") for x in enh if x.get("id")],
            "stratagem_ids":[x.get("id") for x in strat if x.get("id")],
            "unresolved_mfm_units":unresolved,
            "counts":structural_counts,
            "semantic_policy":{
                "full_rule_text_embedded":False,
                "description_fingerprints_available":True,
                "semantic_rule_text_current_verified":False,
                "faq_errata_current_verified":False,
            },
        }
        path=OUT/f"{slug}.json"
        path.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        index.append({
            "slug":slug,
            "status":payload["status"],
            "file":str(path.relative_to(ROOT)).replace("\\","/"),
            "wahapedia_source_slug":wslug,
            "mfm_source_slug":mslug,
            "counts":structural_counts,
            "unresolved_mfm_units":unresolved,
        })
    complete=sum(1 for x in index if x.get("status")=="STRUCTURAL_COMPLETE")
    partial=sum(1 for x in index if x.get("status")=="STRUCTURAL_PARTIAL")
    unavailable=sum(1 for x in index if str(x.get("status","")).startswith("UNAVAILABLE"))
    out={
        "schema_version":"1.0",
        "snapshot_date":DATE,
        "wahapedia_last_update":manifest["source"]["last_update"],
        "counts":{"roster_identities":len(index),"structural_complete":complete,"structural_partial":partial,"unavailable":unavailable},
        "views":index,
    }
    (OUT/"index.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(out["counts"],ensure_ascii=False))
if __name__=="__main__":
    main()
