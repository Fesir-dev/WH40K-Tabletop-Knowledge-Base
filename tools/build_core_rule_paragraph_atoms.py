#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from build_core_rule_reference_atoms import verified_core_pages

ROOT=Path(__file__).resolve().parents[1]
ATOMIZATION_VERSION="CORE_RULE_PARAGRAPH_ATOMIZATION_V1"
PARENT_BOUNDARIES="rules/11e/snapshots/2026-09-30/core_rule_boundaries/index.json"


def load(path:Path)->dict:
    return json.loads(path.read_text(encoding="utf-8"))


def make_paragraph_key(occurrence_key:str,page:int,ordinal_on_page:int)->str:
    return f"{occurrence_key}--para-p{int(page)}-o{int(ordinal_on_page)}"


def paragraph_classification(rule:dict)->str:
    if int(rule.get("occurrence_count",len(rule.get("occurrences",[]))))>1:
        return "REPEATED_OCCURRENCE_PARAGRAPH_VARIANT"
    return "SINGLE_OCCURRENCE_PARAGRAPH"


def candidate_within_spans(candidate:dict,spans:list[dict])->bool:
    page=int(candidate["page"])
    for span in spans:
        if int(span["page"])!=page:
            continue
        if int(candidate["line_start"])<int(span["line_start"]):
            continue
        if int(candidate["line_end"])>int(span["line_end"]):
            continue
        if int(candidate["char_start"])<int(span["char_start"]):
            continue
        if int(candidate["char_end"])>int(span["char_end"]):
            continue
        return True
    return False


def build_snapshot(as_of:str,cache_dir:Path,root:Path=ROOT)->dict:
    parent=load(root/PARENT_BOUNDARIES)
    if parent.get("status")!="PASS":
        raise RuntimeError("Parent Core paragraph-boundary snapshot is not PASS")

    ps=parent.get("summary",{})
    required_parent={
        "rules":141,
        "occurrences":146,
        "families":24,
        "paragraph_candidates":310,
        "heading_line_recovery_gaps":0,
        "empty_body_boundaries":0,
    }
    for key,value in required_parent.items():
        if ps.get(key)!=value:
            raise RuntimeError(f"Parent boundary baseline drift: {key}={ps.get(key)} != {value}")
    if ps.get("all_rules_have_nonempty_boundaries") is not True:
        raise RuntimeError("Parent boundary snapshot contains unresolved/empty rules")

    _page_texts,page_sha,source,verification=verified_core_pages(cache_dir,root)

    parent_source=parent.get("source",{})
    for key in ("document_id","binary_sha256","semantic_sha256","page_count"):
        if parent_source.get(key)!=source.get(key):
            raise RuntimeError(f"Parent/source verification drift for {key}")

    atoms=[]
    range_failures=[]
    parent_candidate_count=0
    represented_rules=set()
    represented_occurrences=set()

    for rule in parent.get("rules",[]):
        rule_ref=rule["rule_ref"]
        rule_key=rule["rule_key"]
        family_id=rule["family_id"]
        classification=paragraph_classification(rule)
        occurrences=rule.get("occurrences",[])
        for occurrence_ordinal,occ in enumerate(occurrences,1):
            if occ.get("state")!="BOUNDARY_RESOLVED":
                raise RuntimeError(f"Parent occurrence unresolved: {occ.get('occurrence_key')}")
            occurrence_key=occ["occurrence_key"]
            candidates=sorted(
                occ.get("paragraph_candidates",[]),
                key=lambda x:(int(x["page"]),int(x["char_start"]),int(x["char_end"]),int(x["ordinal_on_page"])),
            )
            if not candidates:
                raise RuntimeError(f"Parent occurrence has no paragraph candidates: {occurrence_key}")

            represented_rules.add(rule_ref)
            represented_occurrences.add(occurrence_key)
            parent_candidate_count+=len(candidates)

            for paragraph_ordinal,candidate in enumerate(candidates,1):
                page=int(candidate["page"])
                if not 1<=page<=len(page_sha):
                    raise RuntimeError(f"Paragraph page outside verified source: {page}")

                if not candidate_within_spans(candidate,occ.get("body_spans",[])):
                    range_failures.append({
                        "occurrence_key":occurrence_key,
                        "page":page,
                        "ordinal_on_page":int(candidate["ordinal_on_page"]),
                    })

                span=next(
                    (
                        x for x in occ.get("body_spans",[])
                        if int(x["page"])==page
                        and int(candidate["line_start"])>=int(x["line_start"])
                        and int(candidate["line_end"])<=int(x["line_end"])
                        and int(candidate["char_start"])>=int(x["char_start"])
                        and int(candidate["char_end"])<=int(x["char_end"])
                    ),
                    None,
                )
                verified_page_sha=page_sha[page-1]
                if span and span.get("page_semantic_sha256")!=verified_page_sha:
                    raise RuntimeError(f"Parent page semantic SHA drift at page {page}")

                semantic_sha=str(candidate.get("semantic_sha256",""))
                parent_body_sha=str(occ.get("body_semantic_sha256",""))
                if len(semantic_sha)!=64 or len(parent_body_sha)!=64:
                    raise RuntimeError(f"Missing paragraph/body semantic hash for {occurrence_key}")

                atom={
                    "paragraph_key":make_paragraph_key(
                        occurrence_key,page,int(candidate["ordinal_on_page"])
                    ),
                    "rule_ref":rule_ref,
                    "rule_key":rule_key,
                    "family_id":family_id,
                    "occurrence_key":occurrence_key,
                    "occurrence_ordinal":occurrence_ordinal,
                    "paragraph_ordinal_in_occurrence":paragraph_ordinal,
                    "classification":classification,
                    "parent_rule_classification":rule.get("classification"),
                    "page":page,
                    "ordinal_on_page":int(candidate["ordinal_on_page"]),
                    "line_start":int(candidate["line_start"]),
                    "line_end":int(candidate["line_end"]),
                    "char_start":int(candidate["char_start"]),
                    "char_end":int(candidate["char_end"]),
                    "line_count":int(candidate["line_count"]),
                    "char_count":int(candidate["char_count"]),
                    "token_count":int(candidate["token_count"]),
                    "semantic_sha256":semantic_sha,
                    "page_semantic_sha256":verified_page_sha,
                    "parent_body_semantic_sha256":parent_body_sha,
                }
                atoms.append(atom)

    keys=[x["paragraph_key"] for x in atoms]
    counts=Counter(x["classification"] for x in atoms)
    repeated_refs=sorted({
        x["rule_ref"]
        for x in atoms
        if x["classification"]=="REPEATED_OCCURRENCE_PARAGRAPH_VARIANT"
    })

    complete=(
        len(atoms)==310
        and parent_candidate_count==310
        and len(set(keys))==310
        and len(represented_rules)==141
        and len(represented_occurrences)==146
        and not range_failures
        and counts==Counter({
            "SINGLE_OCCURRENCE_PARAGRAPH":300,
            "REPEATED_OCCURRENCE_PARAGRAPH_VARIANT":10,
        })
        and repeated_refs==["15.07","15.08","15.09","15.10","15.11"]
    )

    return {
        "schema_version":"1.0",
        "status":"PASS" if complete else "FAIL",
        "snapshot_date":as_of,
        "authority":"GAMES_WORKSHOP_OFFICIAL",
        "atomization_version":ATOMIZATION_VERSION,
        "source":source,
        "source_verification":verification,
        "parent_boundaries":{
            "path":PARENT_BOUNDARIES,
            "boundary_version":parent.get("boundary_version"),
            "rules":ps.get("rules"),
            "occurrences":ps.get("occurrences"),
            "paragraph_candidates":ps.get("paragraph_candidates"),
            "heading_line_recovery_gaps":ps.get("heading_line_recovery_gaps"),
            "empty_body_boundaries":ps.get("empty_body_boundaries"),
        },
        "paragraph_atoms":atoms,
        "summary":{
            "paragraph_atoms":len(atoms),
            "unique_paragraph_keys":len(set(keys)),
            "parent_paragraph_candidates":parent_candidate_count,
            "rules_represented":len(represented_rules),
            "occurrences_represented":len(represented_occurrences),
            "families_represented":len({x["family_id"] for x in atoms}),
            "classification_counts":dict(sorted(counts.items())),
            "repeated_occurrence_rule_refs":repeated_refs,
            "range_validation_failures":len(range_failures),
            "range_validation_failure_samples":range_failures[:20],
            "all_parent_candidates_atomized":parent_candidate_count==len(atoms)==310,
        },
        "authority_boundary":{
            "stable_paragraph_identity_complete":complete,
            "paragraph_boundaries_are_extraction_candidates":True,
            "paragraph_semantic_ast_complete":False,
            "condition_effect_parsing_complete":False,
            "rule_interaction_graph_complete":False,
            "repeated_paragraph_variant_is_semantic_conflict":False,
            "app_codex_equivalence":"NOT_CLAIMED",
            "full_faction_promotion":False,
            "current_normalized_factions_change":0,
            "copyright_policy":"Stable IDs, parent provenance, ranges/counts and hashes only. No paragraph or rule-body prose committed.",
        },
    }


def compact_report(snapshot:dict)->dict:
    repeated=[
        {
            "paragraph_key":x["paragraph_key"],
            "rule_ref":x["rule_ref"],
            "occurrence_key":x["occurrence_key"],
            "page":x["page"],
            "ordinal_on_page":x["ordinal_on_page"],
            "semantic_sha256":x["semantic_sha256"],
            "parent_body_semantic_sha256":x["parent_body_semantic_sha256"],
        }
        for x in snapshot.get("paragraph_atoms",[])
        if x["classification"]=="REPEATED_OCCURRENCE_PARAGRAPH_VARIANT"
    ]
    return {
        "schema_version":snapshot["schema_version"],
        "status":snapshot["status"],
        "snapshot_date":snapshot["snapshot_date"],
        "authority":snapshot["authority"],
        "atomization_version":snapshot["atomization_version"],
        "source":snapshot["source"],
        "source_verification":snapshot["source_verification"],
        "parent_boundaries":snapshot["parent_boundaries"],
        "summary":snapshot["summary"],
        "repeated_occurrence_paragraphs":repeated,
        "authority_boundary":snapshot["authority_boundary"],
    }


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--as-of",default="2026-09-30")
    ap.add_argument("--output",type=Path,default=Path("rules/11e/snapshots/2026-09-30/core_rule_paragraph_atoms/index.json"))
    ap.add_argument("--summary-output",type=Path,default=Path("reports/CORE_RULE_PARAGRAPH_ATOMIZATION_CURRENT.json"))
    ap.add_argument("--cache-dir",type=Path,default=ROOT/".cache"/"official-public-rules")
    args=ap.parse_args()

    out=args.output if args.output.is_absolute() else ROOT/args.output
    summary_out=args.summary_output if args.summary_output.is_absolute() else ROOT/args.summary_output

    try:
        snapshot=build_snapshot(args.as_of,args.cache_dir)
    except Exception as exc:
        failure={
            "schema_version":"1.0",
            "status":"SOURCE_DRIFT",
            "snapshot_date":args.as_of,
            "authority":"GAMES_WORKSHOP_OFFICIAL",
            "atomization_version":ATOMIZATION_VERSION,
            "error":str(exc),
            "authority_boundary":{"fail_closed":True,"paragraph_atomization_promoted":False},
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
