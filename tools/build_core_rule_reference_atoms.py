#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from build_core_rules_structure import (
    CORE_ID,
    SourceDrift,
    build_sources,
    clean_short_label,
    download,
    fingerprint_normalize,
    heading_candidates,
    sha256_bytes,
    sha256_text,
)

ROOT=Path(__file__).resolve().parents[1]
ATOMIZATION_VERSION="CORE_RULE_REFERENCE_ATOMIZATION_V1"
PARENT_STRUCTURE="rules/11e/snapshots/2026-09-30/core_rules_structure/index.json"
FINGERPRINT_REPORT="reports/OFFICIAL_PUBLIC_RULES_SEMANTIC_FINGERPRINT_CURRENT.json"


def load(path:Path)->dict:
    return json.loads(path.read_text(encoding="utf-8"))


def ref_rx(rule_ref:str)->re.Pattern:
    return re.compile(rf"(?<!\d){re.escape(rule_ref)}(?!\d)")


def classify_heading_evidence(labels_by_page:dict[int,list[str]])->str:
    pages=sorted(labels_by_page)
    if not pages:
        return "HEADING_RECOVERY_GAP"
    if any(len(set(labels_by_page[p]))>1 for p in pages):
        return "MULTIPLE_LABELS_SAME_PAGE"
    if len(pages)>1:
        return "REPEATED_IN_FAMILY_HEADING"
    return "UNIQUE_IN_FAMILY_HEADING"


def verified_core_pages(cache_dir:Path, root:Path=ROOT)->tuple[list[str],list[str],dict,dict]:
    try:
        from pypdf import PdfReader
    except Exception as exc:
        raise RuntimeError("pypdf 5.9.0 is required") from exc

    fp=load(root/FINGERPRINT_REPORT)
    expected=next((x for x in fp.get("documents",[]) if x.get("document_id")==CORE_ID),None)
    if not expected:
        raise RuntimeError("Committed Core Rules fingerprint evidence is missing")

    source=next((x for x in build_sources() if x["document_id"]==CORE_ID),None)
    if not source:
        raise RuntimeError("Core Rules source registration is missing")

    cache_dir.mkdir(parents=True,exist_ok=True)
    pdf_path=cache_dir/"core_rules_11e.pdf"
    if pdf_path.exists():
        raw=pdf_path.read_bytes()
        if sha256_bytes(raw)!=expected["binary_sha256"]:
            pdf_path.unlink()
            raw=download(source["url"])
            pdf_path.write_bytes(raw)
    else:
        raw=download(source["url"])
        pdf_path.write_bytes(raw)

    binary_sha=sha256_bytes(raw)
    if binary_sha!=expected["binary_sha256"]:
        raise SourceDrift(f"Core Rules binary drift: {binary_sha} != {expected['binary_sha256']}")

    reader=PdfReader(str(pdf_path))
    page_texts=[page.extract_text() or "" for page in reader.pages]
    if len(page_texts)!=expected["page_count"]:
        raise SourceDrift(f"Core Rules page count drift: {len(page_texts)} != {expected['page_count']}")

    normalized=[fingerprint_normalize(x) for x in page_texts]
    page_sha=[sha256_text(x) for x in normalized]
    expected_pages=expected.get("pages",[])
    if len(expected_pages)!=len(page_sha):
        raise SourceDrift("Committed Core Rules page fingerprint count drift")
    for idx,digest in enumerate(page_sha):
        if digest!=expected_pages[idx].get("semantic_sha256"):
            raise SourceDrift(f"Core Rules page semantic drift at page {idx+1}")

    document_semantic="\n\n".join(normalized)
    if sha256_text(document_semantic)!=expected["semantic_sha256"]:
        raise SourceDrift("Core Rules document semantic drift")

    source_evidence={
        "document_id":CORE_ID,
        "source_url":source["url"],
        "binary_sha256":binary_sha,
        "semantic_sha256":expected["semantic_sha256"],
        "page_count":len(page_texts),
        "fingerprint_report":FINGERPRINT_REPORT,
    }
    verification={
        "binary_sha256_match":True,
        "page_semantic_fingerprints_match":len(page_sha),
        "document_semantic_sha256_match":True,
    }
    return page_texts,page_sha,source_evidence,verification


def atomize_reference(
    rule_ref:str,
    family:dict,
    candidates:dict[int,list[str]],
    normalized_pages:list[str],
    page_sha:list[str],
)->dict:
    start=int(family["page_start"])
    end=int(family["page_end"])
    rx=ref_rx(rule_ref)

    labels_by_page:dict[int,list[str]]=defaultdict(list)
    for page in range(start,end+1):
        for label in candidates.get(page,[]):
            if not rx.search(label):
                continue
            short=clean_short_label(label)
            if short and short not in labels_by_page[page]:
                labels_by_page[page].append(short)

    in_pages=sorted(labels_by_page)
    classification=classify_heading_evidence(labels_by_page)
    primary=in_pages[0] if in_pages else None

    heading_labels=[]
    for page in in_pages:
        for label in labels_by_page[page]:
            heading_labels.append({
                "page":page,
                "label":label,
                "label_sha256":sha256_text(label),
            })

    all_occurrence_pages=[
        idx+1 for idx,text in enumerate(normalized_pages)
        if rx.search(text)
    ]
    cross=[p for p in all_occurrence_pages if p<start or p>end]

    return {
        "rule_ref":rule_ref,
        "rule_key":"core-rule-"+rule_ref.replace(".","-"),
        "family_id":str(family["family_id"]),
        "classification":classification,
        "family_page_start":start,
        "family_page_end":end,
        "family_page_range_sha256":family.get("page_range_sha256"),
        "in_family_heading_pages":in_pages,
        "primary_heading_page":primary,
        "heading_labels":heading_labels,
        "page_semantic_sha256":{str(p):page_sha[p-1] for p in in_pages},
        "cross_reference_pages":cross,
        "all_reference_pages":all_occurrence_pages,
    }


def build_atomization(as_of:str, cache_dir:Path, root:Path=ROOT)->dict:
    parent=load(root/PARENT_STRUCTURE)
    if parent.get("status")!="PASS":
        raise RuntimeError("Parent Core Rules structure is not PASS")
    if parent.get("summary",{}).get("rule_reference_family_ids")!=[f"{i:02d}" for i in range(1,25)]:
        raise RuntimeError("Parent Core Rules family set is not exactly 01-24")
    if parent.get("summary",{}).get("rule_reference_count")!=141:
        raise RuntimeError("Parent Core Rules reference count is not 141")

    page_texts,page_sha,source_evidence,verification=verified_core_pages(cache_dir,root)
    normalized_pages=[fingerprint_normalize(x) for x in page_texts]
    candidates=heading_candidates(page_texts)

    families=parent.get("rule_reference_families",[])
    family_ids=[str(x.get("family_id")) for x in families]
    if family_ids!=[f"{i:02d}" for i in range(1,25)]:
        raise RuntimeError("Parent family ordering drift")

    atoms=[]
    for family in families:
        fid=str(family["family_id"])
        for rule_ref in sorted(family.get("rule_refs",[])):
            if not rule_ref.startswith(fid+"."):
                raise RuntimeError(f"Reference {rule_ref} does not belong to family {fid}")
            atoms.append(atomize_reference(rule_ref,family,candidates,normalized_pages,page_sha))

    keys=[x["rule_key"] for x in atoms]
    refs=[x["rule_ref"] for x in atoms]
    if len(keys)!=len(set(keys)) or len(refs)!=len(set(refs)):
        raise RuntimeError("Duplicate Core rule atom identity")

    counts=Counter(x["classification"] for x in atoms)
    gaps=[x["rule_ref"] for x in atoms if x["classification"]=="HEADING_RECOVERY_GAP"]
    families_with_atoms=sorted({x["family_id"] for x in atoms})
    complete=(
        len(atoms)==141
        and not gaps
        and families_with_atoms==[f"{i:02d}" for i in range(1,25)]
        and all(x["in_family_heading_pages"] for x in atoms)
    )

    return {
        "schema_version":"1.0",
        "status":"PASS" if complete else "FAIL",
        "snapshot_date":as_of,
        "authority":"GAMES_WORKSHOP_OFFICIAL",
        "atomization_version":ATOMIZATION_VERSION,
        "source":source_evidence,
        "source_verification":verification,
        "parent_structure":{
            "path":PARENT_STRUCTURE,
            "structure_version":parent.get("structure_version"),
            "rule_reference_families":len(families),
            "rule_reference_count":parent.get("summary",{}).get("rule_reference_count"),
        },
        "atoms":atoms,
        "summary":{
            "atoms":len(atoms),
            "unique_rule_refs":len(set(refs)),
            "unique_rule_keys":len(set(keys)),
            "families":len(families_with_atoms),
            "family_ids":families_with_atoms,
            "classification_counts":dict(sorted(counts.items())),
            "heading_recovery_gaps":len(gaps),
            "heading_recovery_gap_refs":gaps,
            "atoms_with_cross_references":sum(bool(x["cross_reference_pages"]) for x in atoms),
            "all_atoms_have_in_family_heading":all(bool(x["in_family_heading_pages"]) for x in atoms),
        },
        "authority_boundary":{
            "numbered_reference_identity_complete":complete,
            "definition_evidence_heading_only":True,
            "paragraph_level_rules_ast_complete":False,
            "rule_interaction_graph_complete":False,
            "app_codex_equivalence":"NOT_CLAIMED",
            "full_faction_promotion":False,
            "current_normalized_factions_change":0,
            "copyright_policy":"Numbered IDs, short headings <=160 chars, page/range hashes and structural evidence only; no paragraph rule prose committed.",
        },
    }


def compact_report(snapshot:dict)->dict:
    ambiguous=[
        {
            "rule_ref":x["rule_ref"],
            "family_id":x["family_id"],
            "classification":x["classification"],
            "in_family_heading_pages":x["in_family_heading_pages"],
            "heading_labels":x["heading_labels"][:4],
        }
        for x in snapshot.get("atoms",[])
        if x["classification"]!="UNIQUE_IN_FAMILY_HEADING"
    ]
    return {
        "schema_version":snapshot["schema_version"],
        "status":snapshot["status"],
        "snapshot_date":snapshot["snapshot_date"],
        "authority":snapshot["authority"],
        "atomization_version":snapshot["atomization_version"],
        "source":snapshot["source"],
        "source_verification":snapshot["source_verification"],
        "parent_structure":snapshot["parent_structure"],
        "summary":snapshot["summary"],
        "non_unique_atoms":ambiguous,
        "authority_boundary":snapshot["authority_boundary"],
    }


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--as-of",default="2026-09-30")
    ap.add_argument("--output",type=Path,default=Path("rules/11e/snapshots/2026-09-30/core_rule_atoms/index.json"))
    ap.add_argument("--summary-output",type=Path,default=Path("reports/CORE_RULE_REFERENCE_ATOMIZATION_CURRENT.json"))
    ap.add_argument("--cache-dir",type=Path,default=ROOT/".cache"/"official-public-rules")
    args=ap.parse_args()

    out=args.output if args.output.is_absolute() else ROOT/args.output
    summary_out=args.summary_output if args.summary_output.is_absolute() else ROOT/args.summary_output

    try:
        snapshot=build_atomization(args.as_of,args.cache_dir)
    except SourceDrift as exc:
        failure={
            "schema_version":"1.0",
            "status":"SOURCE_DRIFT",
            "snapshot_date":args.as_of,
            "authority":"GAMES_WORKSHOP_OFFICIAL",
            "error":str(exc),
            "authority_boundary":{"fail_closed":True,"atomization_promoted":False},
        }
        summary_out.parent.mkdir(parents=True,exist_ok=True)
        summary_out.write_text(json.dumps(failure,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        print(json.dumps(failure,ensure_ascii=False))
        return 2

    out.parent.mkdir(parents=True,exist_ok=True)
    summary_out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(snapshot,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    summary_out.write_text(json.dumps(compact_report(snapshot),ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":snapshot["status"],"summary":snapshot["summary"]},ensure_ascii=False,indent=2))
    return 0 if snapshot["status"]=="PASS" else 2


if __name__=="__main__":
    raise SystemExit(main())
