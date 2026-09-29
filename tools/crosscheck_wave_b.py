#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re, unicodedata, urllib.parse, urllib.request
from collections import defaultdict
from pathlib import Path

BSDATA_COMMIT = "951d5900d1b4a952a4ba560a30c43788e622ccfc"

def norm(v):
    v = unicodedata.normalize("NFKD", v or "").replace("’", "'").replace("‘", "'")
    return " ".join(re.sub(r"[^a-z0-9]+", " ", v.casefold()).split())

def mfm_sig(unit):
    out=set()
    for tier in unit.get("pricing", []):
        for row in tier.get("costs", []):
            try: out.add((int(row["models"]), int(row["points"])))
            except Exception: pass
    return out

def waha_sig(ds):
    out=set()
    for row in ds.get("points_rows", []):
        m=re.search(r"(\d+)\s+models?\b", row.get("description",""), re.I)
        if m and row.get("cost"):
            try: out.add((int(m.group(1)), int(row["cost"])))
            except Exception: pass
    return out

def collect_units(obj, out):
    if isinstance(obj, dict):
        if str(obj.get("type","")).casefold()=="unit" and isinstance(obj.get("name"),str):
            out.add(norm(obj["name"]))
        for x in obj.values(): collect_units(x,out)
    elif isinstance(obj,list):
        for x in obj: collect_units(x,out)

def bsdata_names(path):
    q=urllib.parse.quote(path,safe="/")
    url="https://raw.githubusercontent.com/BSData/wh40k-11e/"+BSDATA_COMMIT+"/"+q
    req=urllib.request.Request(url,headers={"User-Agent":"WH40K-Tabletop-Knowledge-Base/1.0"})
    with urllib.request.urlopen(req,timeout=60) as r:
        obj=json.loads(r.read().decode("utf-8"))
    out=set(); collect_units(obj,out); return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",default=".")
    ap.add_argument("--snapshot-date",default="2026-09-29")
    ap.add_argument("--fetch-bsdata",action="store_true")
    a=ap.parse_args()
    root=Path(a.root).resolve()
    wroot=root/"rules"/"11e"/"snapshots"/a.snapshot_date/"wahapedia"
    manifest=json.loads((wroot/"manifest.json").read_text(encoding="utf-8"))
    catalog=json.loads((root/"factions"/"catalog.json").read_text(encoding="utf-8"))
    cats={x["slug"]:x for x in catalog["factions"]}
    totals=defaultdict(int); conflicts=[]; results=[]
    for ent in manifest["factions"]:
        slug=ent.get("repository_slug")
        if not slug or ent.get("datasheets",0)==0 or slug not in cats: continue
        cat=cats[slug]; ms=cat.get("mfm_source_slug")
        mp=root/"rules"/"11e"/"snapshots"/a.snapshot_date/"mfm"/"factions"/(str(ms)+".json")
        if not ms or not mp.exists(): continue
        w=json.loads((root/ent["file"]).read_text(encoding="utf-8"))
        m=json.loads(mp.read_text(encoding="utf-8"))
        wb=defaultdict(list); mb=defaultdict(list)
        for x in w["datasheets"]: wb[norm(x.get("name"))].append(x)
        for x in m["units"]: mb[norm(x.get("name"))].append(x)
        wn=set(wb); mn=set(mb); common=wn & mn
        pm=[]
        for n in common:
            if len(wb[n])!=1 or len(mb[n])!=1: continue
            ws=waha_sig(wb[n][0]); msig=mfm_sig(mb[n][0])
            if not ws or not msig: continue
            totals["points_compared"]+=1
            if ws!=msig:
                pm.append({"unit":wb[n][0].get("name"),"wahapedia":sorted(map(list,ws)),"mfm":sorted(map(list,msig))})
        wd={norm(x.get("name")):x for x in w.get("detachments",[]) if x.get("name")}
        md={norm(x.get("name")):x for x in m.get("detachments",[]) if x.get("name")}
        dc=set(wd)&set(md); dpm=[]
        for n in dc:
            if str(wd[n].get("dp"))!=str(md[n].get("dp")):
                dpm.append({"detachment":wd[n].get("name"),"wahapedia":wd[n].get("dp"),"mfm":md[n].get("dp")})
        we={(norm(x.get("detachment")),norm(x.get("name"))):x for x in w.get("enhancements",[]) if x.get("detachment") and x.get("name")}
        me={}
        for d in m.get("detachments",[]):
            for x in d.get("enhancements",[]):
                if d.get("name") and x.get("name"): me[(norm(d["name"]),norm(x["name"]))]=x
        ec=set(we)&set(me); ecm=[]
        for k in ec:
            if str(we[k].get("cost"))!=str(me[k].get("points")):
                ecm.append({"enhancement":we[k].get("name"),"wahapedia":we[k].get("cost"),"mfm":me[k].get("points")})
        bs=None
        if a.fetch_bsdata:
            try:
                bn=bsdata_names(cat["bsdata_path"])
                bs={"unit_names":len(bn),"matched_wahapedia_names":len(bn&wn),"overlap_ratio":round(len(bn&wn)/len(bn),4) if bn else None}
            except Exception as e:
                bs={"error":str(e)}
        results.append({"slug":slug,"unit_names":{"wahapedia":len(wn),"mfm":len(mn),"matched":len(common),"mfm_overlap_ratio":round(len(common)/len(mn),4) if mn else None},"points":{"mismatches":pm},"detachments":{"matched":len(dc),"dp_mismatches":dpm},"enhancements":{"matched":len(ec),"cost_mismatches":ecm},"bsdata":bs})
        totals["factions_compared"]+=1; totals["unit_name_matches"]+=len(common)
        totals["mfm_unit_names"]+=len(mn); totals["wahapedia_unit_names"]+=len(wn)
        totals["point_mismatches"]+=len(pm); totals["detachment_matches"]+=len(dc)
        totals["dp_mismatches"]+=len(dpm); totals["enhancement_matches"]+=len(ec); totals["enhancement_cost_mismatches"]+=len(ecm)
        for x in pm: conflicts.append({"type":"POINT_MISMATCH","faction":slug,**x})
        for x in dpm: conflicts.append({"type":"DETACHMENT_POINT_MISMATCH","faction":slug,**x})
        for x in ecm: conflicts.append({"type":"ENHANCEMENT_COST_MISMATCH","faction":slug,**x})
    if totals["factions_compared"]<23: raise SystemExit("insufficient faction reconciliation")
    if totals["unit_name_matches"]<900: raise SystemExit("suspicious unit-name overlap")
    if totals["points_compared"]<600: raise SystemExit("suspicious points comparison count")
    report={"schema_version":"1.0","snapshot_date":a.snapshot_date,"wahapedia_last_update":manifest["source"]["last_update"],"mfm_version":"1.4","bsdata_commit":BSDATA_COMMIT if a.fetch_bsdata else None,"status":"PASS_WITH_CONFLICTS" if conflicts else "PASS","totals":dict(totals),"conflict_count":len(conflicts),"conflicts":conflicts,"factions":results,"promotion_guidance":{"structural_snapshot":"ELIGIBLE","mfm_overrides_cost_conflicts":True,"full_rule_text_semantics":"NOT_PROMOTED","faq_errata":"NOT_PROMOTED"}}
    out=root/"reports"/("WAVE_B_RECONCILIATION_"+a.snapshot_date+".json")
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":report["status"],"totals":report["totals"],"conflict_count":len(conflicts)},ensure_ascii=False,indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
