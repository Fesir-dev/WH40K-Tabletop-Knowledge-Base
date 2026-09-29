#!/usr/bin/env python3
from __future__ import annotations
import hashlib
import json
import urllib.parse
import urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CURRENT=json.loads((ROOT/"rules"/"11e"/"current.json").read_text(encoding="utf-8"))
WAHA_INDEX=ROOT/CURRENT["wave_b_structural"]["snapshot"]
WROOT=WAHA_INDEX.parent.parent
REG=json.loads((ROOT/"sources"/"registry.json").read_text(encoding="utf-8"))
MAN=json.loads((WROOT/"manifest.json").read_text(encoding="utf-8"))
BY_ID={x["id"]:x for x in REG["sources"]}
UA={"User-Agent":"WH40K-Tabletop-Knowledge-Base/1.0"}

def get_bytes(url,limit=40*1024*1024):
    req=urllib.request.Request(url,headers=UA)
    with urllib.request.urlopen(req,timeout=90) as r:
        body=r.read(limit+1)
        if len(body)>limit:
            raise RuntimeError("response too large: "+url)
        return body

def get_json(url):
    return json.loads(get_bytes(url).decode("utf-8"))

def github_head(repo):
    return get_json("https://api.github.com/repos/"+repo+"/branches/main")["commit"]["sha"]

def github_diff(repo,old,new):
    if old==new:
        return []
    data=get_json("https://api.github.com/repos/"+repo+"/compare/"+urllib.parse.quote(old,safe="")+"..."+urllib.parse.quote(new,safe=""))
    return [
        {
            "filename":x.get("filename"),
            "status":x.get("status"),
            "additions":x.get("additions"),
            "deletions":x.get("deletions"),
            "changes":x.get("changes"),
        }
        for x in data.get("files",[])
    ]

def classify_path(path):
    p=(path or "").casefold()
    if any(x in p for x in ["space marine","black templar","blood angel","dark angel","space wolves"]):
        return "ASTARTES"
    if p.startswith("data/"):
        return "MFM_DATA"
    if p.endswith(".json"):
        return "FACTION_OR_LIBRARY_DATA"
    if p.endswith(".md") or "readme" in p:
        return "DOCUMENTATION"
    if ".github/" in p:
        return "CI"
    return "OTHER"

def main():
    pinned_bs=BY_ID["BSDATA_WH40K_11E"]["observed_revision"]["commit_sha"]
    pinned_mfm=BY_ID["BSDATA_MFM_11E"]["observed_revision"]["commit_sha"]
    live_bs=github_head("BSData/wh40k-11e")
    live_mfm=github_head("BSData/wh40k-11e-mfm")

    github_sources=[]
    for source_id,repo,pinned,live in [
        ("BSDATA_WH40K_11E","BSData/wh40k-11e",pinned_bs,live_bs),
        ("BSDATA_MFM_11E","BSData/wh40k-11e-mfm",pinned_mfm,live_mfm),
    ]:
        files=github_diff(repo,pinned,live)
        github_sources.append({
            "source_id":source_id,
            "repository":repo,
            "pinned":pinned,
            "live":live,
            "changed":pinned!=live,
            "files":[dict(x,classification=classify_path(x["filename"])) for x in files],
        })

    waha_changes=[]
    for rec in MAN["files"]:
        name=rec["name"]
        body=get_bytes("https://wahapedia.ru/wh40k11ed/"+name)
        sha=hashlib.sha256(body).hexdigest()
        if sha!=rec["sha256"]:
            waha_changes.append({
                "file":name,
                "snapshot_sha256":rec["sha256"],
                "live_sha256":sha,
                "snapshot_bytes":rec["bytes"],
                "live_bytes":len(body),
            })

    last_body=get_bytes("https://wahapedia.ru/wh40k11ed/Last_update.csv").decode("utf-8-sig")
    lines=[x.strip() for x in last_body.splitlines() if x.strip()]
    live_last=lines[1].strip("|") if len(lines)>1 else ""

    changed_sources=[x["source_id"] for x in github_sources if x["changed"]]
    changed=bool(changed_sources or waha_changes or live_last!=MAN["source"]["last_update"])
    report={
        "schema_version":"1.0",
        "status":"CHANGE_DETECTED" if changed else "NO_CHANGE",
        "baseline_snapshot":str(WROOT.parent.name),
        "github_sources":github_sources,
        "wahapedia":{
            "snapshot_last_update":MAN["source"]["last_update"],
            "live_last_update":live_last,
            "manifest_files_checked":len(MAN["files"]),
            "changed_files":waha_changes,
        },
        "change_summary":{
            "github_sources_changed":changed_sources,
            "wahapedia_files_changed":len(waha_changes),
            "wahapedia_last_update_changed":live_last!=MAN["source"]["last_update"],
        },
        "policy":{
            "auto_promote":False,
            "on_change":"Persist classified report, fail workflow, require ingestion/reconciliation/promotion pipeline.",
        },
    }
    out=ROOT/"reports"/"UPSTREAM_CHANGE_WATCH_CURRENT.json"
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":report["status"],"summary":report["change_summary"]},ensure_ascii=False,indent=2))
    return 2 if changed else 0

if __name__=="__main__":
    raise SystemExit(main())
