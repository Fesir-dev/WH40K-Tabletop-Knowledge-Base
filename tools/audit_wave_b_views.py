#!/usr/bin/env python3
import json, collections
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATE="2026-09-29"
WROOT=ROOT/"rules"/"11e"/"snapshots"/DATE/"wahapedia"
manifest=json.loads((WROOT/"manifest.json").read_text(encoding="utf-8"))
source_catalog=json.loads((WROOT/"source_catalog.json").read_text(encoding="utf-8"))

def inspect_faction(slug):
    p=WROOT/"factions"/f"{slug}.json"
    d=json.loads(p.read_text(encoding="utf-8"))
    source_counts=collections.Counter()
    faction_kw=collections.Counter()
    all_kw=collections.Counter()
    source_keyword_pairs=collections.Counter()
    for ds in d.get("datasheets",[]):
        src=ds.get("source_name") or "<none>"
        source_counts[src]+=1
        kws=[]
        for k in ds.get("keywords",[]):
            kw=k.get("keyword")
            if not kw: continue
            all_kw[kw]+=1
            if str(k.get("is_faction_keyword","")).lower()=="true":
                faction_kw[kw]+=1
                kws.append(kw)
        for kw in kws:
            source_keyword_pairs[(src,kw)]+=1
    return {
        "datasheets":len(d.get("datasheets",[])),
        "source_counts":dict(source_counts.most_common()),
        "faction_keyword_counts":dict(faction_kw.most_common()),
        "all_keyword_counts_top100":dict(all_kw.most_common(100)),
        "source_faction_keyword_pairs":[
            {"source":a,"keyword":b,"count":c}
            for (a,b),c in source_keyword_pairs.most_common()
        ],
        "sample_datasheets":[
            {
                "name":x.get("name"),
                "source_name":x.get("source_name"),
                "source_edition":x.get("source_edition"),
                "source_version":x.get("source_version"),
                "faction_keywords":[k.get("keyword") for k in x.get("keywords",[]) if str(k.get("is_faction_keyword","")).lower()=="true"]
            }
            for x in d.get("datasheets",[])[:400]
        ]
    }

targets={}
for slug in ["space_marines","adeptus_titanicus","chaos_daemons","chaos_space_marines"]:
    p=WROOT/"factions"/f"{slug}.json"
    if p.exists():
        targets[slug]=inspect_faction(slug)

titan_sources=[s for s in source_catalog if "titan" in (s.get("name") or "").lower() or "traitor" in (s.get("name") or "").lower()]

out={
    "schema_version":"1.0",
    "snapshot_date":DATE,
    "wahapedia_last_update":manifest["source"]["last_update"],
    "targets":targets,
    "titan_related_sources":titan_sources,
}
path=ROOT/"reports"/f"WAVE_B_VIEW_DIAGNOSTICS_{DATE}.json"
path.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(path)
