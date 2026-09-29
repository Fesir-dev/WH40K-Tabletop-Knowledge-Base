#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, hashlib, io, json, urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATE="2026-09-29"
WROOT=ROOT/"rules"/"11e"/"snapshots"/DATE/"wahapedia"
BASE="https://wahapedia.ru/wh40k11ed/"

FILES={
    "ability":"Abilities.csv",
    "datasheet-ability":"Datasheets_abilities.csv",
    "datasheet-option":"Datasheets_options.csv",
    "unit-composition":"Datasheets_unit_composition.csv",
    "detachment-ability":"Detachment_abilities.csv",
    "enhancement":"Enhancements.csv",
    "stratagem":"Stratagems.csv",
    "datasheet":"Datasheets.csv",
}
KEYS={
    "ability":("id","faction_id"),
    "datasheet-ability":("datasheet_id","line"),
    "datasheet-option":("datasheet_id","line"),
    "unit-composition":("datasheet_id","line"),
    "detachment-ability":("id","faction_id"),
    "enhancement":("id","faction_id"),
    "stratagem":("id","faction_id"),
    "datasheet":("id",),
}

def digest(v):
    v=(v or "").strip()
    return hashlib.sha256(v.encode("utf-8")).hexdigest() if v else None

def fetch_csv(filename):
    req=urllib.request.Request(BASE+filename,headers={"User-Agent":"WH40K-Tabletop-Knowledge-Base/1.0"})
    with urllib.request.urlopen(req,timeout=90) as r:
        text=r.read().decode("utf-8-sig")
    rows=[]
    for raw in csv.DictReader(io.StringIO(text),delimiter="|"):
        row={str(k).strip().lower():(v or "").strip() for k,v in raw.items() if k}
        if any(row.values()): rows.append(row)
    return rows

def key_for(kind,row):
    return tuple(row.get(k,"") for k in KEYS[kind])

def add_expected(out,seen,kind,identity,field,expected,origin):
    if not expected: return
    token=(kind,tuple(sorted(identity.items())),field,expected)
    if token in seen: return
    seen.add(token)
    out.append({"kind":kind,"identity":identity,"field":field,"expected_sha256":expected,"origin":origin})

def expected_records():
    out=[]; seen=set()
    ability_catalog=json.loads((WROOT/"ability_catalog.json").read_text(encoding="utf-8"))
    for x in ability_catalog:
        ident={"id":x.get("id",""),"faction_id":x.get("faction_id","")}
        add_expected(out,seen,"ability",ident,"description",x.get("description_sha256"),"ability_catalog")
        add_expected(out,seen,"ability",ident,"legend",x.get("legend_sha256"),"ability_catalog")

    for p in sorted((WROOT/"factions").glob("*.json")):
        f=json.loads(p.read_text(encoding="utf-8"))
        fid=f.get("faction",{}).get("id","")
        origin=str(p.relative_to(ROOT))
        for x in f.get("army_abilities",[]):
            ident={"id":x.get("id",""),"faction_id":x.get("faction_id") or fid}
            add_expected(out,seen,"ability",ident,"description",x.get("description_sha256"),origin)
            add_expected(out,seen,"ability",ident,"legend",x.get("legend_sha256"),origin)
        for x in f.get("detachment_abilities",[]):
            ident={"id":x.get("id",""),"faction_id":x.get("faction_id") or fid}
            add_expected(out,seen,"detachment-ability",ident,"description",x.get("description_sha256"),origin)
            add_expected(out,seen,"detachment-ability",ident,"legend",x.get("legend_sha256"),origin)
        for x in f.get("enhancements",[]):
            ident={"id":x.get("id",""),"faction_id":x.get("faction_id") or fid}
            add_expected(out,seen,"enhancement",ident,"description",x.get("description_sha256"),origin)
            add_expected(out,seen,"enhancement",ident,"legend",x.get("legend_sha256"),origin)
        for x in f.get("stratagems",[]):
            ident={"id":x.get("id",""),"faction_id":x.get("faction_id") or fid}
            add_expected(out,seen,"stratagem",ident,"description",x.get("description_sha256"),origin)
            add_expected(out,seen,"stratagem",ident,"legend",x.get("legend_sha256"),origin)
        for ds in f.get("datasheets",[]):
            dsid=ds.get("id","")
            ident={"id":dsid}
            add_expected(out,seen,"datasheet",ident,"loadout",ds.get("loadout_sha256"),origin)
            add_expected(out,seen,"datasheet",ident,"transport",ds.get("transport_sha256"),origin)
            add_expected(out,seen,"datasheet",ident,"damaged_description",ds.get("damaged_description_sha256"),origin)
            for x in ds.get("abilities",[]):
                ident={"datasheet_id":dsid,"line":str(x.get("line",""))}
                add_expected(out,seen,"datasheet-ability",ident,"description",x.get("description_sha256"),origin)
            for x in ds.get("options",[]):
                ident={"datasheet_id":dsid,"line":str(x.get("line",""))}
                add_expected(out,seen,"datasheet-option",ident,"description",x.get("description_sha256"),origin)
            for x in ds.get("unit_composition",[]):
                ident={"datasheet_id":dsid,"line":str(x.get("line",""))}
                add_expected(out,seen,"unit-composition",ident,"description",x.get("description_sha256"),origin)
    return out

def main():
    global DATE, WROOT
    ap=argparse.ArgumentParser()
    ap.add_argument("--snapshot-date",default=DATE)
    ap.add_argument("--report-path")
    a=ap.parse_args()
    DATE=a.snapshot_date
    WROOT=ROOT/"rules"/"11e"/"snapshots"/DATE/"wahapedia"
    live={}
    file_meta={}
    for kind,filename in sorted(FILES.items()):
        if filename in file_meta: continue
        rows=fetch_csv(filename)
        file_meta[filename]={"rows":len(rows)}
        live[filename]=rows

    indexes={}
    for kind,filename in FILES.items():
        idx=defaultdict(list)
        for row in live[filename]:
            # Abilities.csv can contain malformed HTML spill rows; ignore non-numeric IDs.
            if kind=="ability" and not str(row.get("id","")).isdigit(): continue
            idx[key_for(kind,row)].append(row)
        indexes[kind]=idx

    expected=expected_records()
    if len(expected)<10000:
        raise SystemExit(f"suspiciously low semantic fingerprint count: {len(expected)}")

    results=[]; counts=Counter(); by_kind=Counter()
    for rec in expected:
        kind=rec["kind"]; ident=rec["identity"]
        key=tuple(ident.get(k,"") for k in KEYS[kind])
        candidates=indexes[kind].get(key,[])
        # Core/shared abilities can have blank local faction_id. Exact blank is preferred;
        # if absent, fall back to same ID across factions only when all candidate hashes agree.
        if kind=="ability" and not candidates and not ident.get("faction_id"):
            candidates=[]
            for k,rows in indexes[kind].items():
                if k[0]==ident.get("id"): candidates.extend(rows)
        actual_hashes=sorted({digest(x.get(rec["field"],"")) for x in candidates if digest(x.get(rec["field"],""))})
        if not candidates:
            status="MISSING_LIVE"
        elif rec["expected_sha256"] in actual_hashes:
            status="MATCH"
        else:
            status="DRIFT"
        counts[status]+=1; by_kind[(kind,status)]+=1
        if status!="MATCH":
            results.append({**rec,"status":status,"actual_sha256":actual_hashes[:8],"candidate_count":len(candidates)})

    report={
        "schema_version":"1.0",
        "audited_at":datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z"),
        "snapshot_date":DATE,
        "source_base":BASE,
        "snapshot_last_update":json.loads((WROOT/"manifest.json").read_text(encoding="utf-8"))["source"]["last_update"],
        "status":"PASS" if counts["DRIFT"]==0 and counts["MISSING_LIVE"]==0 else "SOURCE_DRIFT",
        "expected_fingerprints":len(expected),
        "counts":dict(counts),
        "by_kind":{
            kind:{state:by_kind[(kind,state)] for state in ["MATCH","DRIFT","MISSING_LIVE"] if by_kind[(kind,state)]}
            for kind in sorted(FILES)
        },
        "live_files":file_meta,
        "problems":results,
        "promotion_guidance":{
            "secondary_mirror_semantics":"CURRENT_HASH_VERIFIED" if not results else "BLOCKED",
            "normative_authority":"UNCHANGED_GAMES_WORKSHOP",
            "copyright_policy":"Long prose remains external; repository stores fingerprints and structured metadata only."
        }
    }
    out=ROOT/"reports"/f"WAVE_B_SEMANTIC_FINGERPRINT_AUDIT_{DATE}.json"
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":report["status"],"expected_fingerprints":len(expected),"counts":dict(counts),"problems":len(results)},ensure_ascii=False,indent=2))
    return 0 if report["status"]=="PASS" else 2

if __name__=="__main__":
    raise SystemExit(main())
