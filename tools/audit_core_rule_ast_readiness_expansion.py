#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

from audit_core_rule_semantic_ast_readiness import (
    CONDITION_IDS,
    MODAL_IDS,
    SENTENCE_BOUNDARY_RE,
    TERMINAL_PUNCTUATION_RE,
)
from build_core_rule_reference_atoms import verified_core_pages
from build_core_rules_structure import fingerprint_normalize, sha256_text
from classify_core_rule_paragraph_semantics import count_signals

ROOT=Path(__file__).resolve().parents[1]
VERSION="CORE_RULE_AST_READINESS_EXPANSION_V1"
PARENT_READINESS="rules/11e/snapshots/2026-09-30/core_rule_semantic_ast_readiness/index.json"
SEMANTICS_PATH="rules/11e/snapshots/2026-09-30/core_rule_paragraph_semantics/index.json"
ATOMS_PATH="rules/11e/snapshots/2026-09-30/core_rule_paragraph_atoms/index.json"
SEMANTIC_VALIDATION_PATH="reports/CORE_RULE_DIRECT_MODAL_AST_SEMANTIC_VALIDATION_CURRENT.json"

PARENT_STATES={
    "BLOCKED_SENTENCE_SHAPE",
    "BLOCKED_COMPLEX_DELIMITERS",
    "BLOCKED_PARENTHETICAL_SCOPE",
}
POSITIVE_STATE="CANDIDATE_SINGLE_MODAL_SENTENCE"
VALID_STATES={
    POSITIVE_STATE,
    "BLOCKED_SENTENCE_SEGMENTATION",
    "BLOCKED_MODAL_SENTENCE_NOT_UNIQUE",
    "BLOCKED_CONDITION_OUTSIDE_MODAL_SENTENCE",
    "BLOCKED_MODAL_SENTENCE_COMPLEX_DELIMITERS",
    "BLOCKED_MODAL_SENTENCE_PARENTHETICAL_SCOPE",
    "BLOCKED_MODAL_SENTENCE_NONTERMINAL",
    "BLOCKED_DELIMITER_SCOPE",
    "BLOCKED_PARENTHETICAL_SCOPE",
}
CLOSERS=set("\"'”’)]")


def load(path:Path)->dict:
    return json.loads(path.read_text(encoding="utf-8"))


def signal_count(raw:str, ids)->int:
    counts=count_signals(raw)
    return sum(int(counts.get(x,0)) for x in ids)


def trim_bounds(raw:str,start:int,end:int)->tuple[int,int]:
    while start<end and raw[start].isspace():
        start+=1
    while end>start and raw[end-1].isspace():
        end-=1
    return start,end


def sentence_ranges(raw:str)->list[dict]:
    ranges=[]
    start=0
    for match in SENTENCE_BOUNDARY_RE.finditer(raw):
        end=match.end()
        while end<len(raw) and raw[end] in CLOSERS:
            end+=1
        s,e=trim_bounds(raw,start,end)
        if e>s:
            segment=raw[s:e]
            ranges.append({
                "relative_char_start":s,
                "relative_char_end":e,
                "terminal":bool(TERMINAL_PUNCTUATION_RE.search(fingerprint_normalize(segment))),
            })
        start=end
    s,e=trim_bounds(raw,start,len(raw))
    if e>s:
        segment=raw[s:e]
        ranges.append({
            "relative_char_start":s,
            "relative_char_end":e,
            "terminal":bool(TERMINAL_PUNCTUATION_RE.search(fingerprint_normalize(segment))),
        })
    return ranges


def sentence_shape(raw:str)->dict:
    normalized=fingerprint_normalize(raw)
    return {
        "complex_delimiter_count":normalized.count(":")+normalized.count(";"),
        "parenthetical_delimiter_count":sum(normalized.count(x) for x in "()[]"),
        "terminal_punctuation_at_end":bool(TERMINAL_PUNCTUATION_RE.search(normalized)),
    }


def analyze_row(raw:str,parent:dict,absolute_base:int)->dict:
    parent_state=parent["readiness_state"]
    modal_axis=parent["modal_axis"]
    modal_ids=MODAL_IDS.get(modal_axis,())
    parent_modal=int(parent.get("modal_occurrences",0))
    parent_conditions=int(parent.get("condition_cues",0))

    if parent_state=="BLOCKED_COMPLEX_DELIMITERS":
        return {
            "expansion_state":"BLOCKED_DELIMITER_SCOPE",
            "sentence_count":len(sentence_ranges(raw)),
            "modal_sentence_ordinal":None,
            "candidate":None,
        }
    if parent_state=="BLOCKED_PARENTHETICAL_SCOPE":
        return {
            "expansion_state":"BLOCKED_PARENTHETICAL_SCOPE",
            "sentence_count":len(sentence_ranges(raw)),
            "modal_sentence_ordinal":None,
            "candidate":None,
        }
    if parent_state!="BLOCKED_SENTENCE_SHAPE":
        raise RuntimeError(f"Unexpected parent state: {parent_state}")

    ranges=sentence_ranges(raw)
    if len(ranges)<2:
        return {
            "expansion_state":"BLOCKED_SENTENCE_SEGMENTATION",
            "sentence_count":len(ranges),
            "modal_sentence_ordinal":None,
            "candidate":None,
        }

    detailed=[]
    for ordinal,rng in enumerate(ranges,1):
        segment=raw[rng["relative_char_start"]:rng["relative_char_end"]]
        modal_count=signal_count(segment,modal_ids)
        condition_count=signal_count(segment,CONDITION_IDS)
        shape=sentence_shape(segment)
        detailed.append({
            **rng,
            "ordinal":ordinal,
            "modal_count":modal_count,
            "condition_count":condition_count,
            "shape":shape,
        })

    modal_rows=[x for x in detailed if x["modal_count"]>0]
    if parent_modal!=1 or len(modal_rows)!=1 or modal_rows[0]["modal_count"]!=1:
        return {
            "expansion_state":"BLOCKED_MODAL_SENTENCE_NOT_UNIQUE",
            "sentence_count":len(ranges),
            "modal_sentence_ordinal":modal_rows[0]["ordinal"] if len(modal_rows)==1 else None,
            "candidate":None,
        }

    modal_row=modal_rows[0]
    outside_conditions=sum(x["condition_count"] for x in detailed if x["ordinal"]!=modal_row["ordinal"])
    if outside_conditions>0 or modal_row["condition_count"]!=parent_conditions:
        return {
            "expansion_state":"BLOCKED_CONDITION_OUTSIDE_MODAL_SENTENCE",
            "sentence_count":len(ranges),
            "modal_sentence_ordinal":modal_row["ordinal"],
            "candidate":None,
        }

    shape=modal_row["shape"]
    if shape["complex_delimiter_count"]>0:
        return {
            "expansion_state":"BLOCKED_MODAL_SENTENCE_COMPLEX_DELIMITERS",
            "sentence_count":len(ranges),
            "modal_sentence_ordinal":modal_row["ordinal"],
            "candidate":None,
        }
    if shape["parenthetical_delimiter_count"]>0:
        return {
            "expansion_state":"BLOCKED_MODAL_SENTENCE_PARENTHETICAL_SCOPE",
            "sentence_count":len(ranges),
            "modal_sentence_ordinal":modal_row["ordinal"],
            "candidate":None,
        }
    if shape["terminal_punctuation_at_end"] is not True:
        return {
            "expansion_state":"BLOCKED_MODAL_SENTENCE_NONTERMINAL",
            "sentence_count":len(ranges),
            "modal_sentence_ordinal":modal_row["ordinal"],
            "candidate":None,
        }

    s=int(modal_row["relative_char_start"])
    e=int(modal_row["relative_char_end"])
    segment=raw[s:e]
    normalized=fingerprint_normalize(segment)
    candidate={
        "sentence_ordinal":modal_row["ordinal"],
        "relative_char_start":s,
        "relative_char_end":e,
        "absolute_char_start":absolute_base+s,
        "absolute_char_end":absolute_base+e,
        "char_count":e-s,
        "token_count":len(normalized.split()) if normalized else 0,
        "semantic_sha256":sha256_text(normalized),
        "modal_axis":modal_axis,
        "modal_occurrences":1,
        "condition_cues":parent_conditions,
        "complex_delimiter_count":0,
        "parenthetical_delimiter_count":0,
        "terminal_punctuation_at_end":True,
    }
    return {
        "expansion_state":POSITIVE_STATE,
        "sentence_count":len(ranges),
        "modal_sentence_ordinal":modal_row["ordinal"],
        "candidate":candidate,
    }


def build_snapshot(as_of:str,cache_dir:Path,root:Path=ROOT)->dict:
    parent=load(root/PARENT_READINESS)
    semantics=load(root/SEMANTICS_PATH)
    atoms=load(root/ATOMS_PATH)
    semantic_validation=load(root/SEMANTIC_VALIDATION_PATH)

    if parent.get("status")!="PASS" or parent.get("readiness_version")!="CORE_RULE_SEMANTIC_AST_READINESS_V1":
        raise RuntimeError("Parent AST readiness is not the closed PASS v1 baseline")
    ps=parent.get("summary",{})
    if ps.get("shape_blocked")!=33 or ps.get("source_shape_analysis_candidates")!=34:
        raise RuntimeError("Parent shape-blocked baseline drifted")
    if ps.get("shape_state_counts")!={
        "BLOCKED_COMPLEX_DELIMITERS":4,
        "BLOCKED_PARENTHETICAL_SCOPE":1,
        "BLOCKED_SENTENCE_SHAPE":28,
        "PILOT_READY_DIRECT_MODAL":1,
    }:
        raise RuntimeError("Parent shape-state baseline drifted")

    if semantic_validation.get("status")!="PASS":
        raise RuntimeError("Direct-modal semantic validation is not PASS")
    sv=semantic_validation.get("validation",{})
    if sv.get("decision")!="OPAQUE_PRESERVED" or sv.get("ast_mutated") is not False:
        raise RuntimeError("Validated direct-modal node baseline drifted")
    if sv.get("interaction_edges_created")!=0 or sv.get("additional_paragraphs_admitted")!=0:
        raise RuntimeError("Validated direct-modal scope drifted")

    sem_by={x["paragraph_key"]:x for x in semantics.get("classifications",[])}
    atom_by={x["paragraph_key"]:x for x in atoms.get("paragraph_atoms",[])}
    blocked=[x for x in parent.get("rows",[]) if x.get("readiness_state") in PARENT_STATES]
    if len(blocked)!=33:
        raise RuntimeError(f"Expected 33 parent shape-blocked rows, got {len(blocked)}")
    if Counter(x["readiness_state"] for x in blocked)!=Counter({
        "BLOCKED_SENTENCE_SHAPE":28,
        "BLOCKED_COMPLEX_DELIMITERS":4,
        "BLOCKED_PARENTHETICAL_SCOPE":1,
    }):
        raise RuntimeError("Parent blocked-state population drifted")

    page_texts,page_sha,source,verification=verified_core_pages(cache_dir,root)
    rows=[]
    state_counts=Counter()
    parent_counts=Counter()
    hashes_reproduced=0

    for parent_row in blocked:
        key=parent_row["paragraph_key"]
        sem=sem_by.get(key)
        atom=atom_by.get(key)
        if not sem or not atom:
            raise RuntimeError(f"Missing parent paragraph evidence: {key}")

        page=int(atom["page"])
        start=int(atom["char_start"])
        end=int(atom["char_end"])
        if not 1<=page<=len(page_texts) or start<0 or end<start:
            raise RuntimeError(f"Invalid source range: {key}")

        raw=page_texts[page-1][start:end]
        paragraph_sha=sha256_text(fingerprint_normalize(raw))
        if paragraph_sha!=atom.get("semantic_sha256") or paragraph_sha!=sem.get("semantic_sha256"):
            raise RuntimeError(f"Paragraph semantic SHA drift: {key}")
        if page_sha[page-1]!=atom.get("page_semantic_sha256") or page_sha[page-1]!=sem.get("page_semantic_sha256"):
            raise RuntimeError(f"Page semantic SHA drift: {key}")
        hashes_reproduced+=1

        analysis=analyze_row(raw,parent_row,start)
        state=analysis["expansion_state"]
        if state not in VALID_STATES:
            raise RuntimeError(f"Unknown expansion state: {state}")
        state_counts[state]+=1
        parent_counts[parent_row["readiness_state"]]+=1

        row={
            "paragraph_key":key,
            "rule_ref":parent_row["rule_ref"],
            "rule_key":parent_row.get("rule_key"),
            "family_id":parent_row.get("family_id"),
            "occurrence_key":parent_row["occurrence_key"],
            "page":page,
            "paragraph_char_start":start,
            "paragraph_char_end":end,
            "paragraph_token_count":int(atom["token_count"]),
            "paragraph_semantic_sha256":paragraph_sha,
            "page_semantic_sha256":page_sha[page-1],
            "parent_readiness_state":parent_row["readiness_state"],
            "modal_axis":parent_row["modal_axis"],
            "modal_occurrences":int(parent_row["modal_occurrences"]),
            "condition_cues":int(parent_row["condition_cues"]),
            "source_hash_reproduced":True,
            "sentence_count":int(analysis["sentence_count"]),
            "modal_sentence_ordinal":analysis["modal_sentence_ordinal"],
            "expansion_state":state,
            "sentence_candidate":analysis["candidate"],
            "ast_node_created":False,
            "interaction_edges_created":0,
        }
        rows.append(row)

    candidates=[x for x in rows if x["expansion_state"]==POSITIVE_STATE]
    complete=(
        len(rows)==33
        and len({x["paragraph_key"] for x in rows})==33
        and hashes_reproduced==33
        and parent_counts==Counter({
            "BLOCKED_SENTENCE_SHAPE":28,
            "BLOCKED_COMPLEX_DELIMITERS":4,
            "BLOCKED_PARENTHETICAL_SCOPE":1,
        })
        and sum(state_counts.values())==33
        and all(x["ast_node_created"] is False for x in rows)
        and all(x["interaction_edges_created"]==0 for x in rows)
        and all(
            c["sentence_candidate"]
            and c["sentence_candidate"]["modal_occurrences"]==1
            and c["sentence_candidate"]["condition_cues"]==c["condition_cues"]
            and c["sentence_candidate"]["complex_delimiter_count"]==0
            and c["sentence_candidate"]["parenthetical_delimiter_count"]==0
            and c["sentence_candidate"]["terminal_punctuation_at_end"] is True
            for c in candidates
        )
    )

    return {
        "schema_version":"1.0",
        "status":"PASS" if complete else "FAIL",
        "snapshot_date":as_of,
        "authority":"GAMES_WORKSHOP_OFFICIAL",
        "expansion_version":VERSION,
        "source":source,
        "source_verification":verification,
        "parent_readiness":{
            "path":PARENT_READINESS,
            "readiness_version":parent.get("readiness_version"),
            "shape_blocked":ps.get("shape_blocked"),
            "shape_state_counts":ps.get("shape_state_counts"),
        },
        "validated_existing_ast":{
            "report":SEMANTIC_VALIDATION_PATH,
            "node_key":semantic_validation.get("parent_pilot",{}).get("node_key"),
            "decision":sv.get("decision"),
            "ast_mutated":sv.get("ast_mutated"),
            "interaction_edges_created":sv.get("interaction_edges_created"),
            "additional_paragraphs_admitted":sv.get("additional_paragraphs_admitted"),
        },
        "rows":rows,
        "summary":{
            "rows_audited":len(rows),
            "unique_paragraph_keys":len({x["paragraph_key"] for x in rows}),
            "parent_state_counts":dict(sorted(parent_counts.items())),
            "expansion_state_counts":dict(sorted(state_counts.items())),
            "source_hashes_reproduced":hashes_reproduced,
            "sentence_candidates":len(candidates),
            "candidate_modal_axis_counts":dict(sorted(Counter(x["modal_axis"] for x in candidates).items())),
            "candidate_condition_counts":dict(sorted(Counter(str(x["condition_cues"]) for x in candidates).items())),
            "new_ast_nodes_created":0,
            "interaction_edges_created":0,
            "existing_ast_nodes_mutated":0,
            "additional_paragraphs_admitted":0,
        },
        "authority_boundary":{
            "readiness_expansion_complete":complete,
            "sentence_candidate_is_not_ast_node":True,
            "sentence_candidate_is_not_parser_admission":True,
            "ast_nodes_created":False,
            "interaction_edges_created":False,
            "existing_ast_mutated":False,
            "parent_review_blockers_relaxed":False,
            "modal_multiplicity_blockers_relaxed":False,
            "repeated_variant_blockers_relaxed":False,
            "complex_semantic_blockers_relaxed":False,
            "paragraph_prose_committed":False,
            "condition_effect_ast_complete":False,
            "rule_interaction_graph_complete":False,
            "app_codex_equivalence":"NOT_CLAIMED",
            "full_faction_promotion":False,
            "current_normalized_factions_change":0,
            "copyright_policy":"Parent paragraph IDs/ranges/hashes plus candidate sentence ranges/counts/hashes only; no paragraph or sentence prose committed.",
        },
    }


def compact_report(snapshot:dict)->dict:
    candidates=[
        {
            "paragraph_key":x["paragraph_key"],
            "rule_ref":x["rule_ref"],
            "page":x["page"],
            "modal_axis":x["modal_axis"],
            "condition_cues":x["condition_cues"],
            "sentence_count":x["sentence_count"],
            "sentence_candidate":x["sentence_candidate"],
        }
        for x in snapshot.get("rows",[])
        if x["expansion_state"]==POSITIVE_STATE
    ]
    return {
        "schema_version":snapshot["schema_version"],
        "status":snapshot["status"],
        "snapshot_date":snapshot["snapshot_date"],
        "authority":snapshot["authority"],
        "expansion_version":snapshot["expansion_version"],
        "source":snapshot["source"],
        "source_verification":snapshot["source_verification"],
        "parent_readiness":snapshot["parent_readiness"],
        "validated_existing_ast":snapshot["validated_existing_ast"],
        "summary":snapshot["summary"],
        "sentence_candidates":candidates,
        "authority_boundary":snapshot["authority_boundary"],
    }


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--as-of",default="2026-09-30")
    ap.add_argument("--output",type=Path,default=Path("rules/11e/snapshots/2026-09-30/core_rule_ast_readiness_expansion/index.json"))
    ap.add_argument("--summary-output",type=Path,default=Path("reports/CORE_RULE_AST_READINESS_EXPANSION_CURRENT.json"))
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
            "expansion_version":VERSION,
            "error":str(exc),
            "authority_boundary":{
                "fail_closed":True,
                "ast_nodes_created":False,
                "interaction_edges_created":False,
                "existing_ast_mutated":False,
            },
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
