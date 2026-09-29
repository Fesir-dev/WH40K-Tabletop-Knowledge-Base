#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
import urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
UA="WH40K-Tabletop-Knowledge-Base/official-public-fingerprint-v1"
NORMALIZATION_VERSION="OFFICIAL_TEXT_NFKC_WS_V1"

CLASS_PATTERNS={
    "CONTENTS": re.compile(r"\bCONTENTS\b", re.I),
    "DETACHMENT_RULES": re.compile(r"\bDETACHMENT RULES\b", re.I),
    "ENHANCEMENTS": re.compile(r"\bENHANCEMENTS?\b", re.I),
    "STRATAGEMS": re.compile(r"\bSTRATAGEMS?\b", re.I),
    "DATASHEET": re.compile(r"\bDATASHEETS?\b", re.I),
    "RULES_UPDATES": re.compile(r"\bRULES UPDATES?\b", re.I),
    "FAQ_ERRATA": re.compile(r"\bFAQ(?:S)?\b|\bERRATA\b", re.I),
    "LEGENDS": re.compile(r"\bLEGENDS\b", re.I),
    "IMPERIAL_ARMOUR": re.compile(r"\bIMPERIAL ARMOUR\b", re.I),
    "CORE_RULES": re.compile(r"\bCORE RULES\b", re.I),
}

def sha256_bytes(raw:bytes)->str:
    return hashlib.sha256(raw).hexdigest()

def normalize_text(text:str)->str:
    text=unicodedata.normalize("NFKC", text)
    text=text.replace("\u00ad","")
    text=text.replace("\u2010","-").replace("\u2011","-").replace("\u2012","-").replace("\u2013","-").replace("\u2014","-")
    lines=[]
    for line in text.splitlines():
        line=" ".join(line.split())
        if not line:
            continue
        if re.fullmatch(r"\d{1,3}", line):
            continue
        lines.append(line)
    return "\n".join(lines).strip()

def semantic_classes(text:str)->list[str]:
    head="\n".join(text.splitlines()[:35])
    return [name for name,rx in CLASS_PATTERNS.items() if rx.search(head)]

def download(url:str, timeout:int=120)->bytes:
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/pdf,*/*"})
    with urllib.request.urlopen(req,timeout=timeout) as r:
        raw=r.read()
        ctype=(r.headers.get("Content-Type") or "").lower()
    if not raw.startswith(b"%PDF"):
        raise RuntimeError(f"Not a PDF: {url} content-type={ctype} bytes={len(raw)}")
    return raw

def build_sources()->list[dict]:
    discovery=json.loads((ROOT/"sources"/"discoveries"/"gw_public_rules_surface_2026-09-29.json").read_text(encoding="utf-8"))
    assets=json.loads((ROOT/"sources"/"snapshots"/"gw_11e_official_assets_2026-09-29.json").read_text(encoding="utf-8"))

    core=next(x for x in discovery["findings"] if x["id"]=="GW_11E_CORE_RULES_PUBLIC")
    docs=[{
        "document_id":"GW_11E_CORE_RULES_PUBLIC",
        "title":"Warhammer 40,000 Core Rules",
        "document_type":"CORE_RULES",
        "url":core["asset_url"],
        "expected_binary_sha256":None,
        "source_scope":"PUBLIC_FULL_CORE_RULES",
    }]
    for row in assets["official_assets"]["assets"]:
        if row.get("type")!="Faction Pack" or str(row.get("edition"))!="11":
            continue
        docs.append({
            "document_id":"GW_11E_FACTION_PACK_"+str(row["id"]),
            "title":row["name"],
            "document_type":"FACTION_PACK",
            "url":row["url"],
            "expected_binary_sha256":row.get("sha256"),
            "source_version":row.get("version"),
            "source_scope":"PUBLIC_SUPPLEMENTAL_FACTION_PACK_NOT_FULL_CODEX",
        })
    docs.sort(key=lambda x:(0 if x["document_type"]=="CORE_RULES" else 1, x["title"]))
    return docs

def extract_document(source:dict, cache:Path)->dict:
    try:
        from pypdf import PdfReader
    except Exception as exc:
        raise RuntimeError("pypdf is required; install the pinned workflow dependency") from exc

    cache.mkdir(parents=True,exist_ok=True)
    key=hashlib.sha256(source["url"].encode()).hexdigest()[:20]
    pdf_path=cache/f"{key}.pdf"
    if pdf_path.exists():
        raw=pdf_path.read_bytes()
    else:
        raw=download(source["url"])
        pdf_path.write_bytes(raw)

    binary_sha=sha256_bytes(raw)
    expected=source.get("expected_binary_sha256")
    if expected and binary_sha!=expected:
        raise RuntimeError(f"Binary SHA mismatch for {source['title']}: {binary_sha} != {expected}")

    reader=PdfReader(str(pdf_path))
    pages=[]
    document_parts=[]
    for idx,page in enumerate(reader.pages,1):
        extracted=page.extract_text() or ""
        norm=normalize_text(extracted)
        document_parts.append(norm)
        pages.append({
            "page":idx,
            "text_char_count":len(norm),
            "semantic_sha256":hashlib.sha256(norm.encode("utf-8")).hexdigest(),
            "semantic_classes":semantic_classes(norm),
        })
    all_text="\n\n".join(document_parts)
    if not all_text.strip():
        raise RuntimeError(f"No extractable text for {source['title']}")
    return {
        **source,
        "binary_sha256":binary_sha,
        "page_count":len(pages),
        "text_char_count":len(all_text),
        "semantic_sha256":hashlib.sha256(all_text.encode("utf-8")).hexdigest(),
        "pages":pages,
        "verification":"PASS",
    }

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--as-of",default="2026-09-29")
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--cache-dir",type=Path,default=ROOT/".cache"/"official-public-rules")
    ap.add_argument("--document-id",action="append",default=[])
    args=ap.parse_args()

    sources=build_sources()
    if args.document_id:
        wanted=set(args.document_id)
        sources=[x for x in sources if x["document_id"] in wanted]
        missing=wanted-{x["document_id"] for x in sources}
        if missing:
            raise SystemExit("Unknown document ids: "+", ".join(sorted(missing)))

    documents=[]
    failures=[]
    for source in sources:
        try:
            documents.append(extract_document(source,args.cache_dir))
            print(f"PASS {source['document_id']} {source['title']}",file=sys.stderr)
        except Exception as exc:
            failures.append({"document_id":source["document_id"],"title":source["title"],"error":str(exc)})
            print(f"FAIL {source['document_id']} {source['title']}: {exc}",file=sys.stderr)

    summary={
        "documents":len(sources),
        "core_rules":sum(x["document_type"]=="CORE_RULES" for x in sources),
        "faction_packs":sum(x["document_type"]=="FACTION_PACK" for x in sources),
        "verified":len(documents),
        "failures":len(failures),
        "pages":sum(x["page_count"] for x in documents),
        "text_chars":sum(x["text_char_count"] for x in documents),
    }
    report={
        "schema_version":"1.0",
        "status":"PASS" if not failures and len(documents)==len(sources) else "FAIL",
        "as_of":args.as_of,
        "authority":"GAMES_WORKSHOP_OFFICIAL",
        "extraction_contract":{
            "engine":"pypdf 5.9.0",
            "normalization_version":NORMALIZATION_VERSION,
            "copyright_policy":"Store hashes/counts/classes only; do not vendor long Games Workshop rules prose.",
            "binary_verification":"Faction Pack binaries must match the previously verified official asset SHA-256. Core Rules SHA-256 is observed by this pipeline.",
        },
        "documents":documents,
        "failures":failures,
        "summary":summary,
    }
    out=args.output if args.output.is_absolute() else ROOT/args.output
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":report["status"],"summary":summary},ensure_ascii=False))
    return 0 if report["status"]=="PASS" else 2

if __name__=="__main__":
    raise SystemExit(main())
