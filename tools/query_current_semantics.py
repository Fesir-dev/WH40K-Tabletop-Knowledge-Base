#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, hashlib, io, json, urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATE="2026-09-29"
WROOT=ROOT/"rules"/"11e"/"snapshots"/DATE/"wahapedia"
BASE="https://wahapedia.ru/wh40k11ed/"

KIND_FILE={
    "ability":"Abilities.csv",
    "datasheet-ability":"Datasheets_abilities.csv",
    "datasheet-option":"Datasheets_options.csv",
    "unit-composition":"Datasheets_unit_composition.csv",
    "detachment-ability":"Detachment_abilities.csv",
    "enhancement":"Enhancements.csv",
    "stratagem":"Stratagems.csv",
    "datasheet-loadout":"Datasheets.csv",
    "datasheet-transport":"Datasheets.csv",
    "datasheet-damaged-description":"Datasheets.csv",
}
TEXT_FIELD={
    "ability":"description",
    "datasheet-ability":"description",
    "datasheet-option":"description",
    "unit-composition":"description",
    "detachment-ability":"description",
    "enhancement":"description",
    "stratagem":"description",
    "datasheet-loadout":"loadout",
    "datasheet-transport":"transport",
    "datasheet-damaged-description":"damaged_description",
}

def digest(v):
    v=(v or "").strip()
    return hashlib.sha256(v.encode("utf-8")).hexdigest() if v else None

def read_csv_live(filename):
    url=BASE+filename
    req=urllib.request.Request(url,headers={"User-Agent":"WH40K-Tabletop-Knowledge-Base/1.0"})
    with urllib.request.urlopen(req,timeout=60) as r:
        text=r.read().decode("utf-8-sig")
    reader=csv.DictReader(io.StringIO(text),delimiter="|")
    rows=[]
    for raw in reader:
        row={str(k).strip().lower():(v or "").strip() for k,v in raw.items() if k}
        if any(row.values()): rows.append(row)
    return url,rows

def faction_docs():
    for p in sorted((WROOT/"factions").glob("*.json")):
        try: yield json.loads(p.read_text(encoding="utf-8"))
        except Exception: continue

def find_datasheet(dsid):
    for f in faction_docs():
        for ds in f.get("datasheets",[]):
            if ds.get("id")==dsid: return f,ds
    return None,None

def find_top(kind, item_id, faction_id=None):
    if kind=="ability":
        arr=json.loads((WROOT/"ability_catalog.json").read_text(encoding="utf-8"))
        matches=[x for x in arr if x.get("id")==item_id and (not faction_id or x.get("faction_id")==faction_id)]
        return matches[0] if len(matches)==1 else (matches[0] if matches else None)
    key={"detachment-ability":"detachment_abilities","enhancement":"enhancements","stratagem":"stratagems"}[kind]
    matches=[]
    for f in faction_docs():
        if faction_id and f.get("faction",{}).get("id")!=faction_id: continue
        matches += [x for x in f.get(key,[]) if x.get("id")==item_id]
    return matches[0] if matches else None

def local_expected(kind,args):
    if kind in {"ability","detachment-ability","enhancement","stratagem"}:
        item=find_top(kind,args.id,args.faction_id)
        if not item: raise SystemExit("Local snapshot entity not found")
        return item.get("description_sha256"), {"id":args.id,"faction_id":args.faction_id,"name":item.get("name")}
    f,ds=find_datasheet(args.datasheet_id)
    if not ds: raise SystemExit("Local datasheet not found")
    if kind=="datasheet-ability":
        rows=[x for x in ds.get("abilities",[]) if str(x.get("line"))==str(args.line)]
        if not rows: raise SystemExit("Local datasheet ability line not found")
        return rows[0].get("description_sha256"), {"datasheet_id":args.datasheet_id,"line":str(args.line),"name":rows[0].get("name")}
    if kind=="datasheet-option":
        rows=[x for x in ds.get("options",[]) if str(x.get("line"))==str(args.line)]
        if not rows: raise SystemExit("Local datasheet option line not found")
        return rows[0].get("description_sha256"), {"datasheet_id":args.datasheet_id,"line":str(args.line)}
    if kind=="unit-composition":
        rows=[x for x in ds.get("unit_composition",[]) if str(x.get("line"))==str(args.line)]
        if not rows: raise SystemExit("Local unit composition line not found")
        return rows[0].get("description_sha256"), {"datasheet_id":args.datasheet_id,"line":str(args.line)}
    field={
        "datasheet-loadout":"loadout_sha256",
        "datasheet-transport":"transport_sha256",
        "datasheet-damaged-description":"damaged_description_sha256",
    }[kind]
    return ds.get(field), {"datasheet_id":args.datasheet_id,"name":ds.get("name")}

def live_match(kind,args,rows):
    if kind in {"ability","detachment-ability","enhancement","stratagem"}:
        hits=[x for x in rows if x.get("id")==args.id and (not args.faction_id or x.get("faction_id")==args.faction_id)]
        # Wahapedia Abilities.csv may contain malformed HTML spill rows; exact numeric-id matching ignores them.
        if not hits: raise SystemExit("Live source entity not found")
        return hits[0]
    if kind in {"datasheet-ability","datasheet-option","unit-composition"}:
        hits=[x for x in rows if x.get("datasheet_id")==args.datasheet_id and str(x.get("line"))==str(args.line)]
        if not hits: raise SystemExit("Live source row not found")
        return hits[0]
    hits=[x for x in rows if x.get("id")==args.datasheet_id]
    if not hits: raise SystemExit("Live datasheet row not found")
    return hits[0]

def smoke_targets():
    # Pick representative hash-bearing entities from the committed snapshot.
    f=json.loads((WROOT/"factions"/"adeptus_custodes.json").read_text(encoding="utf-8"))
    ds_ability=None; option=None; comp=None; loadout=None
    for ds in f["datasheets"]:
        if not loadout and ds.get("loadout_sha256"): loadout=(ds["id"],None)
        for x in ds.get("abilities",[]):
            if not ds_ability and x.get("description_sha256"): ds_ability=(ds["id"],x.get("line"))
        for x in ds.get("options",[]):
            if not option and x.get("description_sha256"): option=(ds["id"],x.get("line"))
        for x in ds.get("unit_composition",[]):
            if not comp and x.get("description_sha256"): comp=(ds["id"],x.get("line"))
    targets=[]
    if ds_ability: targets.append(("datasheet-ability",ds_ability[0],ds_ability[1],None,None))
    if option: targets.append(("datasheet-option",option[0],option[1],None,None))
    if comp: targets.append(("unit-composition",comp[0],comp[1],None,None))
    if loadout: targets.append(("datasheet-loadout",loadout[0],None,None,None))
    if f.get("detachment_abilities"):
        x=next((x for x in f["detachment_abilities"] if x.get("description_sha256")),None)
        if x: targets.append(("detachment-ability",None,None,x["id"],f["faction"]["id"]))
    if f.get("enhancements"):
        x=next((x for x in f["enhancements"] if x.get("description_sha256")),None)
        if x: targets.append(("enhancement",None,None,x["id"],f["faction"]["id"]))
    if f.get("stratagems"):
        x=next((x for x in f["stratagems"] if x.get("description_sha256")),None)
        if x: targets.append(("stratagem",None,None,x["id"],f["faction"]["id"]))
    ac=[x for x in json.loads((WROOT/"ability_catalog.json").read_text(encoding="utf-8")) if x.get("description_sha256")]
    if ac:
        x=ac[0]; targets.append(("ability",None,None,x["id"],x.get("faction_id")))
    return targets

def resolve_once(kind,datasheet_id=None,line=None,item_id=None,faction_id=None,include_text=False):
    class A: pass
    a=A(); a.datasheet_id=datasheet_id; a.line=line; a.id=item_id; a.faction_id=faction_id
    expected,identity=local_expected(kind,a)
    if not expected:
        return {"kind":kind,"identity":identity,"status":"NO_SNAPSHOT_FINGERPRINT"}
    filename=KIND_FILE[kind]
    url,rows=read_csv_live(filename)
    row=live_match(kind,a,rows)
    field=TEXT_FIELD[kind]; text=(row.get(field) or "").strip()
    actual=digest(text)
    status="SNAPSHOT_MATCH" if actual==expected else "SOURCE_DRIFT"
    out={"kind":kind,"identity":identity,"status":status,"source_url":url,"expected_sha256":expected,"actual_sha256":actual}
    if include_text and status=="SNAPSHOT_MATCH": out["text"]=text
    return out

def main():
    ap=argparse.ArgumentParser(description="Fetch current Wahapedia semantic text and verify it against committed SHA-256 fingerprints.")
    ap.add_argument("--kind",choices=sorted(KIND_FILE))
    ap.add_argument("--id")
    ap.add_argument("--faction-id")
    ap.add_argument("--datasheet-id")
    ap.add_argument("--line")
    ap.add_argument("--include-text",action="store_true")
    ap.add_argument("--smoke-test",action="store_true")
    args=ap.parse_args()
    if args.smoke_test:
        results=[]
        for kind,ds,line,item,fid in smoke_targets():
            results.append(resolve_once(kind,ds,line,item,fid,False))
        bad=[x for x in results if x["status"]!="SNAPSHOT_MATCH"]
        print(json.dumps({"status":"PASS" if not bad else "SOURCE_DRIFT","checks":results},ensure_ascii=False,indent=2))
        return 2 if bad else 0
    if not args.kind: ap.error("--kind is required unless --smoke-test is used")
    if args.kind in {"ability","detachment-ability","enhancement","stratagem"} and not args.id: ap.error("--id is required")
    if args.kind.startswith("datasheet-") or args.kind=="unit-composition":
        if not args.datasheet_id: ap.error("--datasheet-id is required")
    if args.kind in {"datasheet-ability","datasheet-option","unit-composition"} and args.line is None: ap.error("--line is required")
    out=resolve_once(args.kind,args.datasheet_id,args.line,args.id,args.faction_id,args.include_text)
    print(json.dumps(out,ensure_ascii=False,indent=2))
    return 2 if out["status"]=="SOURCE_DRIFT" else 0
if __name__=="__main__":
    raise SystemExit(main())
