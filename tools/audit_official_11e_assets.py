#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, io, json, urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATE="2026-09-29"
WROOT=ROOT/"rules"/"11e"/"snapshots"/DATE/"wahapedia"
LIVE_SOURCE="https://wahapedia.ru/wh40k11ed/Source.csv"
GW_DOWNLOADS="https://www.warhammer-community.com/en-gb/downloads/warhammer-40000/"
MAX_BYTES=120*1024*1024

def fetch_bytes(url,limit=None):
    req=urllib.request.Request(url,headers={"User-Agent":"WH40K-Tabletop-Knowledge-Base/1.0"})
    with urllib.request.urlopen(req,timeout=120) as r:
        status=getattr(r,"status",200)
        headers={k.lower():v for k,v in r.headers.items()}
        if limit is None:
            body=r.read()
        else:
            body=r.read(limit+1)
            if len(body)>limit: raise RuntimeError(f"response exceeds {limit} bytes")
        return status,headers,body,r.geturl()

def parse_source_csv(data):
    text=data.decode("utf-8-sig")
    rows=[]
    for raw in csv.DictReader(io.StringIO(text),delimiter="|"):
        row={str(k).strip().lower():(v or "").strip() for k,v in raw.items() if k}
        if any(row.values()): rows.append(row)
    return rows

def normalized_source(row):
    return {
        "id":row.get("id",""),"name":row.get("name",""),"type":row.get("type",""),
        "edition":row.get("edition",""),"version":row.get("version",""),
        "errata_date":row.get("errata_date",""),"errata_link":row.get("errata_link",""),
    }

def verify_pdf(url):
    req=urllib.request.Request(url,headers={"User-Agent":"WH40K-Tabletop-Knowledge-Base/1.0"})
    h=hashlib.sha256(); size=0; first=b""
    with urllib.request.urlopen(req,timeout=180) as r:
        status=getattr(r,"status",200)
        headers={k.lower():v for k,v in r.headers.items()}
        final_url=r.geturl()
        while True:
            chunk=r.read(1024*1024)
            if not chunk: break
            if not first: first=chunk[:8]
            size+=len(chunk)
            if size>MAX_BYTES: raise RuntimeError(f"PDF exceeds safety cap {MAX_BYTES}")
            h.update(chunk)
    return {
        "status":status,
        "final_url":final_url,
        "content_type":headers.get("content-type"),
        "content_length_header":headers.get("content-length"),
        "etag":headers.get("etag"),
        "last_modified":headers.get("last-modified"),
        "bytes":size,
        "sha256":h.hexdigest(),
        "pdf_magic":first.startswith(b"%PDF-"),
    }

def main():
    committed=json.loads((WROOT/"source_catalog.json").read_text(encoding="utf-8"))
    committed11=[normalized_source(x) for x in committed if str(x.get("edition"))=="11"]

    st,headers,live_body,live_url=fetch_bytes(LIVE_SOURCE,10*1024*1024)
    live_rows=parse_source_csv(live_body)
    live11=[normalized_source(x) for x in live_rows if x.get("edition")=="11"]
    c_by={x["id"]:x for x in committed11}; l_by={x["id"]:x for x in live11}
    drift=[]
    for sid in sorted(set(c_by)|set(l_by)):
        if c_by.get(sid)!=l_by.get(sid):
            drift.append({"id":sid,"committed":c_by.get(sid),"live":l_by.get(sid)})

    dst,dheaders,downloads_body,downloads_url=fetch_bytes(GW_DOWNLOADS,15*1024*1024)

    assets=[]; failures=[]
    for row in sorted(live11,key=lambda x:x["name"]):
        link=row.get("errata_link","")
        if row.get("name")=="Munitorum Field Manual":
            assets.append({**row,"verification":"HANDLED_BY_WAVE_A_MFM","url":link})
            continue
        rec={**row,"url":link}
        if not link.startswith("https://assets.warhammer-community.com/"):
            rec["verification"]="NON_OFFICIAL_ASSET_URL"
            failures.append(rec); assets.append(rec); continue
        try:
            v=verify_pdf(link); rec.update(v)
            rec["verification"]="PASS" if v["status"]==200 and v["pdf_magic"] else "FAIL"
            if rec["verification"]!="PASS": failures.append(rec)
        except Exception as exc:
            rec["verification"]="FAIL"; rec["error"]=str(exc); failures.append(rec)
        assets.append(rec)

    report={
        "schema_version":"1.0",
        "audited_at":datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z"),
        "snapshot_date":DATE,
        "status":"PASS" if not drift and not failures else "FAIL",
        "live_source_csv":{
            "url":live_url,"http_status":st,"sha256":hashlib.sha256(live_body).hexdigest(),
            "edition_11_rows":len(live11),"committed_edition_11_rows":len(committed11),
            "catalog_drift_count":len(drift),"catalog_drift":drift,
        },
        "official_downloads_page":{
            "url":downloads_url,"http_status":dst,"bytes":len(downloads_body),
            "sha256":hashlib.sha256(downloads_body).hexdigest(),
            "statement_scope":"Official Downloads page is the normative update/FAQ entry point; exact faction asset identity is verified below."
        },
        "official_assets":{
            "edition_11_sources":len(live11),
            "mfm_sources":sum(1 for x in assets if x.get("verification")=="HANDLED_BY_WAVE_A_MFM"),
            "pdf_assets":sum(1 for x in assets if x.get("verification")!="HANDLED_BY_WAVE_A_MFM"),
            "verified_pdf_assets":sum(1 for x in assets if x.get("verification")=="PASS"),
            "failures":len(failures),
            "assets":assets,
        },
        "promotion_guidance":{
            "faq_errata_source_catalog":"CURRENT" if not drift else "DRIFT",
            "official_asset_reachability":"VERIFIED" if not failures else "BLOCKED",
            "semantic_content_normative_equivalence":"NOT_CLAIMED",
            "note":"Official PDF reachability/hash proves exact referenced GW asset existence, not that Wahapedia prose is normatively identical to every PDF passage."
        }
    }
    out=ROOT/"sources"/"snapshots"/f"gw_11e_official_assets_{DATE}.json"
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({
        "status":report["status"],"edition_11_sources":len(live11),
        "catalog_drift":len(drift),"verified_pdf_assets":report["official_assets"]["verified_pdf_assets"],
        "failures":len(failures)
    },ensure_ascii=False,indent=2))
    return 0 if report["status"]=="PASS" else 2

if __name__=="__main__":
    raise SystemExit(main())
