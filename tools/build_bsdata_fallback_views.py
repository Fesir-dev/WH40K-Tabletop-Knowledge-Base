#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, re, urllib.parse, urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATE="2026-09-29"
DEFAULT_BSDATA_COMMIT="951d5900d1b4a952a4ba560a30c43788e622ccfc"
BSDATA_COMMIT=DEFAULT_BSDATA_COMMIT
FILES={
    "titanicus_catalogue":{
        "path":"Chaos - Titanicus Traitoris.json",
        "blob_sha":"46a76e2c0bd42e0b98d737ce91c10601534a62a6",
    },
    "titans_library":{
        "path":"Library - Titans.json",
        "blob_sha":"c1928f1d3cd9c6caa31d6a1889cc6f73157e888c",
    },
    "unaligned":{
        "path":"Unaligned Forces.json",
        "blob_sha":"65eac5beaaa050ceacdfdcd9668d953444187229",
    },
}
OUT=ROOT/"rules"/"11e"/"snapshots"/DATE/"bsdata_fallback"

def fetch(path):
    q=urllib.parse.quote(path,safe="/")
    url=f"https://raw.githubusercontent.com/BSData/wh40k-11e/{BSDATA_COMMIT}/{q}"
    req=urllib.request.Request(url,headers={"User-Agent":"WH40K-Tabletop-Knowledge-Base/1.0"})
    with urllib.request.urlopen(req,timeout=60) as r:
        raw=r.read()
    return raw,json.loads(raw.decode("utf-8")),url

def sha(v):
    if not v: return None
    return hashlib.sha256(str(v).encode("utf-8")).hexdigest()

def chars(profile):
    return {
        x.get("name"):x.get("$text")
        for x in profile.get("characteristics",[])
        if x.get("name") and x.get("$text") is not None
    }

def walk_profiles(node,out):
    if isinstance(node,dict):
        for p in node.get("profiles",[]) or []:
            t=p.get("typeName")
            c=chars(p)
            if t=="Unit":
                out["unit_profiles"].append({"name":p.get("name"),"characteristics":c})
            elif t in {"Ranged Weapons","Melee Weapons"}:
                out["weapon_profiles"].append({"name":p.get("name"),"type":t,"characteristics":c})
            elif t in {"Abilities","Transport"}:
                desc=c.get("Description") or c.get("Capacity")
                out["semantic_refs"].append({
                    "name":p.get("name"),"type":t,
                    "text_sha256":sha(desc),"text_present":bool(desc),
                })
        for k,v in node.items():
            if k!="profiles": walk_profiles(v,out)
    elif isinstance(node,list):
        for x in node: walk_profiles(x,out)

def entry_summary(entry):
    out={
        "id":entry.get("id"),
        "name":entry.get("name"),
        "type":entry.get("type"),
        "categories":[x.get("name") for x in entry.get("categoryLinks",[]) if x.get("name")],
        "implementation_costs":[
            {"name":x.get("name"),"value":x.get("value")}
            for x in entry.get("costs",[]) if x.get("name")
        ],
        "constraints":[
            {k:x.get(k) for k in ("field","scope","type","value") if x.get(k) is not None}
            for x in entry.get("constraints",[])
        ],
        "unit_profiles":[],
        "weapon_profiles":[],
        "semantic_refs":[],
    }
    walk_profiles(entry,out)
    # stable de-duplication because recursive structures can expose the same profile more than once
    for key in ("unit_profiles","weapon_profiles","semantic_refs"):
        seen=set(); dedup=[]
        for row in out[key]:
            sig=json.dumps(row,sort_keys=True,ensure_ascii=False)
            if sig not in seen:
                seen.add(sig); dedup.append(row)
        out[key]=dedup
    return out

def main():
    global DATE, BSDATA_COMMIT, OUT
    ap=argparse.ArgumentParser()
    ap.add_argument("--snapshot-date",default=DATE)
    ap.add_argument("--mfm-snapshot-date")
    ap.add_argument("--bsdata-commit",default=DEFAULT_BSDATA_COMMIT)
    a=ap.parse_args()
    DATE=a.snapshot_date
    BSDATA_COMMIT=a.bsdata_commit
    OUT=ROOT/"rules"/"11e"/"snapshots"/DATE/"bsdata_fallback"
    mfm_date=a.mfm_snapshot_date or DATE
    OUT.mkdir(parents=True,exist_ok=True)
    loaded={}; provenance=[]
    for key,meta in FILES.items():
        raw,obj,url=fetch(meta["path"])
        loaded[key]=obj["catalogue"]
        provenance.append({
            "role":key,"path":meta["path"],"github_blob_sha":meta["blob_sha"] if BSDATA_COMMIT==DEFAULT_BSDATA_COMMIT else None,
            "sha256":hashlib.sha256(raw).hexdigest(),"bytes":len(raw),"url":url,
        })

    mfm=json.loads((ROOT/"rules"/"11e"/"snapshots"/mfm_date/"mfm"/"factions"/"chaos-titan-legions.json").read_text(encoding="utf-8"))
    mfm_points={}
    for u in mfm.get("units",[]):
        pts=[]
        for band in u.get("pricing",[]):
            for row in band.get("costs",[]):
                if row.get("models")==1 and row.get("points") is not None: pts.append(row["points"])
        mfm_points[re.sub(r"^Chaos\s+","",u["name"])]=pts

    titan_cat=loaded["titanicus_catalogue"]
    titan_lib=loaded["titans_library"]
    lib_entries={x.get("id"):x for x in titan_lib.get("sharedSelectionEntries",[]) if x.get("id")}
    titan_links=[
        x for x in titan_cat.get("entryLinks",[])
        if x.get("type")=="selectionEntry" and x.get("targetId") in lib_entries
    ]
    titans=[]
    for link in titan_links:
        e=entry_summary(lib_entries[link["targetId"]])
        e["roster_name"]=link.get("name")
        e["normative_points_source"]="GW_MFM_1_4"
        e["normative_points"]=mfm_points.get(link.get("name"),[])
        e["implementation_points_non_normative"]=e.pop("implementation_costs")
        titans.append(e)
    titan_rules=[
        {"name":x.get("name"),"description_sha256":sha(x.get("description")),"description_present":bool(x.get("description"))}
        for x in titan_cat.get("rules",[])
    ]
    titan_view={
        "schema_version":"1.0","snapshot_date":DATE,"roster_slug":"titanicus_traitoris",
        "state":"IMPLEMENTATION_FALLBACK_COMPLETE",
        "authority":{
            "structure":"BSDATA_WH40K_11E_STRUCTURED_IMPLEMENTATION",
            "points":"GW_MFM_1_4",
            "semantic_rule_text":"HASH_ONLY_NOT_NORMATIVE",
        },
        "bsdata_commit":BSDATA_COMMIT,
        "units":titans,"army_rule_refs":titan_rules,
        "counts":{"units":len(titans),"unit_profiles":sum(len(x["unit_profiles"]) for x in titans),"weapon_profiles":sum(len(x["weapon_profiles"]) for x in titans)},
    }

    un=loaded["unaligned"]
    un_entries=[entry_summary(x) for x in un.get("sharedSelectionEntries",[]) if x.get("type")=="model"]
    un_view={
        "schema_version":"1.0","snapshot_date":DATE,"roster_slug":"unaligned_forces",
        "state":"IMPLEMENTATION_FALLBACK_COMPLETE",
        "authority":{
            "structure":"BSDATA_WH40K_11E_STRUCTURED_IMPLEMENTATION",
            "points":"BSDATA_IMPLEMENTATION_ONLY_NO_MFM_PROJECTION",
            "semantic_rule_text":"HASH_ONLY_NOT_NORMATIVE",
        },
        "bsdata_commit":BSDATA_COMMIT,
        "units":un_entries,
        "counts":{
            "units":len(un_entries),
            "legends_named_units":sum(1 for x in un_entries if "[Legends]" in (x.get("name") or "")),
            "unit_profiles":sum(len(x["unit_profiles"]) for x in un_entries),
            "weapon_profiles":sum(len(x["weapon_profiles"]) for x in un_entries),
        },
    }
    (OUT/"titanicus_traitoris.json").write_text(json.dumps(titan_view,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (OUT/"unaligned_forces.json").write_text(json.dumps(un_view,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    index={
        "schema_version":"1.0","snapshot_date":DATE,
        "source_id":"BSDATA_WH40K_11E","source_role":"structured_implementation",
        "commit_sha":BSDATA_COMMIT,
        "provenance":provenance,
        "views":[
            {"slug":"titanicus_traitoris","file":str((OUT/"titanicus_traitoris.json").relative_to(ROOT)).replace("\\","/"),"state":titan_view["state"],"counts":titan_view["counts"]},
            {"slug":"unaligned_forces","file":str((OUT/"unaligned_forces.json").relative_to(ROOT)).replace("\\","/"),"state":un_view["state"],"counts":un_view["counts"]},
        ],
        "policy":"Fallback closes structural source availability only. It does not promote BSData to normative authority or CURRENT_VERIFIED rules truth.",
    }
    (OUT/"index.json").write_text(json.dumps(index,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    if len(titans)!=4: raise SystemExit(f"Expected 4 Titanicus Traitoris units, got {len(titans)}")
    if len(un_entries)<20: raise SystemExit(f"Suspicious Unaligned unit count: {len(un_entries)}")
    print(json.dumps({"titanicus_traitoris":titan_view["counts"],"unaligned_forces":un_view["counts"]},ensure_ascii=False))
if __name__=="__main__":
    main()
