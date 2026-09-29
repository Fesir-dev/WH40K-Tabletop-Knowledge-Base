#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import io
import json
import re
import unicodedata
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
WAHA_BASE="https://wahapedia.ru/wh40k11ed/"
UA="WH40K-Tabletop-Knowledge-Base/official-mirror-overlap-v1"
CSV_FILES=[
    "Last_update.csv",
    "Source.csv",
    "Factions.csv",
    "Datasheets.csv",
    "Abilities.csv",
    "Datasheets_abilities.csv",
    "Datasheets_options.csv",
    "Datasheets_unit_composition.csv",
    "Detachment_abilities.csv",
    "Enhancements.csv",
    "Stratagems.csv",
]
FACTION_ALIASES={
    "aeldari":"AE",
    "imperial agents":"AoI",
    "agents of the imperium":"AoI",
    "adeptus titanicus forge world":"TL",
}

def load(path:Path):
    return json.loads(path.read_text(encoding="utf-8"))

def sha(raw:bytes)->str:
    return hashlib.sha256(raw).hexdigest()

def digest_text(text:str)->str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()

def norm_name(value:str|None)->str:
    value=unicodedata.normalize("NFKD",value or "")
    value="".join(ch for ch in value if not unicodedata.combining(ch))
    return " ".join(re.sub(r"[^a-z0-9]+"," ",value.casefold()).split())

def canonical_text(value:str|None)->str:
    value=html.unescape(value or "")
    value=re.sub(r"(?i)<br\s*/?>"," ",value)
    value=re.sub(r"<[^>]+>"," ",value)
    value=unicodedata.normalize("NFKC",value)
    value=value.replace("\u00ad","")
    value=value.replace("\u2010","-").replace("\u2011","-").replace("\u2012","-").replace("\u2013","-").replace("\u2014","-")
    # pypdf often represents a line-wrapped word as "frag- ment"; compare a second,
    # punctuation-insensitive token projection rather than claiming raw-text identity.
    value=value.casefold()
    value=re.sub(r"([a-z0-9])-\s+([a-z0-9])",r"\1\2",value)
    value=re.sub(r"[^a-z0-9]+"," ",value)
    return " ".join(value.split())

def tokens(value:str|None)->list[str]:
    c=canonical_text(value)
    return c.split() if c else []

def shingle_coverage(candidate_tokens:list[str], official_tokens:list[str], n:int=5)->float:
    if not candidate_tokens:
        return 0.0
    if len(candidate_tokens)<n:
        needle=" ".join(candidate_tokens)
        hay=" ".join(official_tokens)
        return 1.0 if needle and needle in hay else 0.0
    cand={tuple(candidate_tokens[i:i+n]) for i in range(len(candidate_tokens)-n+1)}
    off={tuple(official_tokens[i:i+n]) for i in range(len(official_tokens)-n+1)}
    return len(cand & off)/len(cand) if cand else 0.0

def classify(text:str,anchor:str,official_tokens:list[str],provenance:str)->tuple[str,float,bool]:
    ct=tokens(text)
    at=tokens(anchor)
    off_join=" ".join(official_tokens)
    cand_join=" ".join(ct)
    anchor_join=" ".join(at)
    anchor_present=bool(anchor_join and anchor_join in off_join)
    if not ct:
        return "EMPTY",0.0,anchor_present
    if len(ct)>=4 and cand_join in off_join:
        return "EXACT_TOKEN_SEQUENCE_MATCH",1.0,anchor_present
    cov=shingle_coverage(ct,official_tokens)
    if anchor_present and cov>=0.85:
        return "HIGH_OVERLAP_NORMALIZATION_MATCH",cov,True
    if anchor_present and cov>=0.40:
        return "PARTIAL_OVERLAP_REVIEW",cov,True
    if provenance=="EXACT_SOURCE_ID":
        if anchor_present:
            return "REVIEW_REQUIRED_POSSIBLE_DRIFT_OR_LAYOUT",cov,True
        return "UNMAPPED_EXACT_SOURCE_REVIEW",cov,False
    if anchor_present:
        return "TITLE_ONLY_PUBLIC_SCOPE_CANDIDATE",cov,True
    return "OUTSIDE_PUBLIC_PACK_OR_UNMAPPED",cov,False

def fetch_bytes(url:str,timeout:int=120)->bytes:
    req=urllib.request.Request(url,headers={"User-Agent":UA})
    with urllib.request.urlopen(req,timeout=timeout) as r:
        return r.read()

def fetch_csv(name:str,expected_sha:str)->list[dict]:
    raw=fetch_bytes(WAHA_BASE+name)
    actual=sha(raw)
    if actual!=expected_sha:
        raise RuntimeError(f"Wahapedia {name} SHA drift: {actual} != {expected_sha}")
    text=raw.decode("utf-8-sig")
    rows=[]
    for raw_row in csv.DictReader(io.StringIO(text),delimiter="|"):
        row={str(k).strip().lower():(v or "").strip() for k,v in raw_row.items() if k}
        if any(row.values()):
            rows.append(row)
    return rows

def extract_pdf_tokens(url:str,expected_sha:str,cache:Path)->tuple[list[str],int]:
    try:
        from pypdf import PdfReader
    except Exception as exc:
        raise RuntimeError("pypdf is required") from exc
    cache.mkdir(parents=True,exist_ok=True)
    key=hashlib.sha256(url.encode()).hexdigest()[:20]
    path=cache/f"{key}.pdf"
    if path.exists():
        raw=path.read_bytes()
    else:
        raw=fetch_bytes(url)
        path.write_bytes(raw)
    actual=sha(raw)
    if actual!=expected_sha:
        raise RuntimeError(f"Official PDF SHA drift: {actual} != {expected_sha}")
    reader=PdfReader(str(path))
    all_tokens=[]
    for page in reader.pages:
        all_tokens.extend(tokens(page.extract_text() or ""))
    return all_tokens,len(reader.pages)

def add_candidate(out:list[dict], *, kind:str, identity:dict, anchor:str, text:str, provenance:str):
    if not (text or "").strip():
        return
    out.append({
        "kind":kind,
        "identity":identity,
        "anchor":anchor,
        "mirror_text_sha256":digest_text(text.strip()),
        "mirror_canonical_sha256":digest_text(canonical_text(text)),
        "mirror_token_count":len(tokens(text)),
        "provenance":provenance,
        "_text":text,
    })

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--as-of",default="2026-09-29")
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--cache-dir",type=Path,default=ROOT/".cache"/"official-public-rules")
    args=ap.parse_args()

    manifest=load(ROOT/"rules"/"11e"/"snapshots"/"2026-09-29"/"wahapedia"/"manifest.json")
    source_catalog=load(ROOT/"rules"/"11e"/"snapshots"/"2026-09-29"/"wahapedia"/"source_catalog.json")
    fp=load(ROOT/"reports"/"OFFICIAL_PUBLIC_RULES_SEMANTIC_FINGERPRINT_CURRENT.json")

    expected_files={x["name"]:x["sha256"] for x in manifest["files"]}
    tables={name:fetch_csv(name,expected_files[name]) for name in CSV_FILES}
    last_update=tables["Last_update.csv"][0]["last_update"]
    if last_update!=manifest["source"]["last_update"]:
        raise SystemExit(f"Mirror last_update drift: {last_update} != {manifest['source']['last_update']}")

    source_by_id={x["id"]:x for x in source_catalog}
    factions_by_id={x["id"]:x for x in tables["Factions.csv"]}
    faction_id_by_name={norm_name(x["name"]):x["id"] for x in tables["Factions.csv"]}

    datasheets=tables["Datasheets.csv"]
    ds_by_id={x["id"]:x for x in datasheets}
    ds_ids_by_source=defaultdict(set)
    faction_ids_by_source=defaultdict(set)
    for ds in datasheets:
        sid=ds.get("source_id")
        if sid:
            ds_ids_by_source[sid].add(ds["id"])
            if ds.get("faction_id"):
                faction_ids_by_source[sid].add(ds["faction_id"])

    related={}
    for name in ["Datasheets_abilities.csv","Datasheets_options.csv","Datasheets_unit_composition.csv"]:
        idx=defaultdict(list)
        for row in tables[name]:
            idx[row["datasheet_id"]].append(row)
        related[name]=idx

    faction_tables=[
        ("ability","Abilities.csv",("description","legend")),
        ("detachment-ability","Detachment_abilities.csv",("description","legend")),
        ("enhancement","Enhancements.csv",("description","legend")),
        ("stratagem","Stratagems.csv",("description","legend")),
    ]

    documents=[]
    aggregate=Counter()
    official_docs=[x for x in fp["documents"] if x.get("document_type")=="FACTION_PACK"]
    for doc in official_docs:
        sid=doc["document_id"].removeprefix("GW_11E_FACTION_PACK_")
        source=source_by_id.get(sid,{})
        official_tokens,page_count=extract_pdf_tokens(doc["url"],doc["binary_sha256"],args.cache_dir)

        fids=set(faction_ids_by_source.get(sid,set()))
        if not fids:
            alias=FACTION_ALIASES.get(norm_name(doc["title"]))
            if alias:
                fids.add(alias)
            direct=faction_id_by_name.get(norm_name(doc["title"]))
            if direct:
                fids.add(direct)

        candidates=[]
        exact_ds_ids=ds_ids_by_source.get(sid,set())
        for dsid in sorted(exact_ds_ids):
            ds=ds_by_id[dsid]
            for field in ("loadout","transport","damaged_description"):
                add_candidate(
                    candidates,kind=f"datasheet-{field.replace('_','-')}",
                    identity={"datasheet_id":dsid,"name":ds.get("name"),"field":field},
                    anchor=ds.get("name",""),text=ds.get(field,""),provenance="EXACT_SOURCE_ID"
                )
            for row in related["Datasheets_abilities.csv"].get(dsid,[]):
                add_candidate(
                    candidates,kind="datasheet-ability",
                    identity={"datasheet_id":dsid,"line":row.get("line"),"name":row.get("name")},
                    anchor=row.get("name") or ds.get("name",""),text=row.get("description",""),
                    provenance="EXACT_SOURCE_ID"
                )
            for row in related["Datasheets_options.csv"].get(dsid,[]):
                add_candidate(
                    candidates,kind="datasheet-option",
                    identity={"datasheet_id":dsid,"line":row.get("line")},
                    anchor=ds.get("name",""),text=row.get("description",""),provenance="EXACT_SOURCE_ID"
                )
            for row in related["Datasheets_unit_composition.csv"].get(dsid,[]):
                add_candidate(
                    candidates,kind="unit-composition",
                    identity={"datasheet_id":dsid,"line":row.get("line")},
                    anchor=ds.get("name",""),text=row.get("description",""),provenance="EXACT_SOURCE_ID"
                )

        for kind,filename,fields in faction_tables:
            for row in tables[filename]:
                if row.get("faction_id") not in fids:
                    continue
                anchor=row.get("name") or row.get("detachment") or ""
                for field in fields:
                    add_candidate(
                        candidates,kind=kind,
                        identity={"id":row.get("id"),"faction_id":row.get("faction_id"),"name":row.get("name"),"field":field},
                        anchor=anchor,text=row.get(field,""),provenance="FACTION_SCOPE_CANDIDATE"
                    )

        results=[]
        counts=Counter()
        by_kind=defaultdict(Counter)
        by_prov=defaultdict(Counter)
        for row in candidates:
            state,cov,anchor_present=classify(row.pop("_text"),row["anchor"],official_tokens,row["provenance"])
            result={
                **row,
                "result":state,
                "shingle_coverage":round(cov,6),
                "anchor_present":anchor_present,
            }
            results.append(result)
            counts[state]+=1
            by_kind[row["kind"]][state]+=1
            by_prov[row["provenance"]][state]+=1
            aggregate[state]+=1

        documents.append({
            "document_id":doc["document_id"],
            "title":doc["title"],
            "source_id":sid,
            "source_name":source.get("name"),
            "official_binary_sha256":doc["binary_sha256"],
            "official_page_count":page_count,
            "mirror_faction_ids":sorted(fids),
            "exact_source_datasheets":len(exact_ds_ids),
            "candidate_fields":len(results),
            "counts":dict(sorted(counts.items())),
            "by_kind":{k:dict(sorted(v.items())) for k,v in sorted(by_kind.items())},
            "by_provenance":{k:dict(sorted(v.items())) for k,v in sorted(by_prov.items())},
            "results":results,
        })

    exact_strong=sum(
        count for state,count in aggregate.items()
        if state in {"EXACT_TOKEN_SEQUENCE_MATCH","HIGH_OVERLAP_NORMALIZATION_MATCH"}
    )
    review=sum(
        count for state,count in aggregate.items()
        if state in {"PARTIAL_OVERLAP_REVIEW","REVIEW_REQUIRED_POSSIBLE_DRIFT_OR_LAYOUT","UNMAPPED_EXACT_SOURCE_REVIEW"}
    )

    report={
        "schema_version":"1.0",
        "status":"PASS",
        "as_of":args.as_of,
        "authority_boundary":{
            "normative_authority":"GAMES_WORKSHOP",
            "secondary_mirror":"WAHAPEDIA_11E",
            "full_codex_app_equivalence_claimed":False,
            "public_overlap_match_promotes_full_faction":False,
            "possible_drift_requires_review":True,
        },
        "source_integrity":{
            "official_documents_verified":len(official_docs),
            "official_documents_expected":28,
            "mirror_csv_files_verified":len(CSV_FILES),
            "mirror_csv_files_expected":len(CSV_FILES),
            "mirror_last_update":last_update,
            "mirror_snapshot_last_update":manifest["source"]["last_update"],
        },
        "core_rules":{
            "state":"NO_COMPARABLE_WAVE_B_GLOBAL_RULES_CORPUS",
            "reason":"Current Wave B semantic snapshot covers faction CSV semantics; it does not contain the global Wahapedia Core Rules prose corpus.",
            "promotion":False,
        },
        "summary":{
            "faction_pack_documents":len(documents),
            "candidate_fields":sum(x["candidate_fields"] for x in documents),
            "strong_public_overlap":exact_strong,
            "review_required_exact_source_or_partial":review,
            "counts":dict(sorted(aggregate.items())),
        },
        "documents":documents,
        "interpretation":{
            "EXACT_TOKEN_SEQUENCE_MATCH":"Strong public overlap after conservative HTML/punctuation/whitespace canonicalization.",
            "HIGH_OVERLAP_NORMALIZATION_MATCH":"High shingle overlap with exact anchor; likely PDF layout/normalization differences.",
            "PARTIAL_OVERLAP_REVIEW":"Some official overlap exists but text is not sufficiently aligned for equivalence.",
            "REVIEW_REQUIRED_POSSIBLE_DRIFT_OR_LAYOUT":"Exact source provenance and anchor exist, but low text overlap. Manual review must distinguish real drift from PDF extraction/layout effects.",
            "UNMAPPED_EXACT_SOURCE_REVIEW":"Exact Faction Pack source provenance exists but no reliable official anchor/text match was found.",
            "TITLE_ONLY_PUBLIC_SCOPE_CANDIDATE":"Faction-scoped row title occurs in the pack but text overlap is weak; source provenance is not exact.",
            "OUTSIDE_PUBLIC_PACK_OR_UNMAPPED":"Faction-scoped candidate is not evidenced by this public pack and must not be treated as drift.",
            "normative_promotion":False,
            "full_faction_equivalence":False,
        },
    }

    out=args.output if args.output.is_absolute() else ROOT/args.output
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":report["status"],"summary":report["summary"],"source_integrity":report["source_integrity"]},ensure_ascii=False,indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
