#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from build_core_rule_reference_atoms import verified_core_pages
from build_core_rules_structure import fingerprint_normalize, sha256_text

ROOT=Path(__file__).resolve().parents[1]
PILOT_VERSION="CORE_RULE_DIRECT_MODAL_AST_PILOT_V1"
READINESS_PATH="rules/11e/snapshots/2026-09-30/core_rule_semantic_ast_readiness/index.json"
SEMANTICS_PATH="rules/11e/snapshots/2026-09-30/core_rule_paragraph_semantics/index.json"
ATOMS_PATH="rules/11e/snapshots/2026-09-30/core_rule_paragraph_atoms/index.json"
PILOT_KEY="core-rule-13-07--p50--l1--para-p50-o1"
PILOT_RULE="13.07"
CAN_RE=re.compile(r"\bcan\b",re.IGNORECASE)


def load(path:Path)->dict:
    return json.loads(path.read_text(encoding="utf-8"))


def trim_bounds(value:str,start:int,end:int)->tuple[int,int]:
    while start<end and value[start].isspace():
        start+=1
    while end>start and value[end-1].isspace():
        end-=1
    return start,end


def token_count(value:str)->int:
    normalized=fingerprint_normalize(value)
    return len(normalized.split()) if normalized else 0


def make_span(raw:str,rel_start:int,rel_end:int,absolute_base:int,semantic_type:str)->dict:
    rel_start,rel_end=trim_bounds(raw,rel_start,rel_end)
    if rel_end<=rel_start:
        raise RuntimeError(f"Empty {semantic_type}")
    value=raw[rel_start:rel_end]
    normalized=fingerprint_normalize(value)
    if not normalized:
        raise RuntimeError(f"Normalization emptied {semantic_type}")
    return {
        "relative_char_start":rel_start,
        "relative_char_end":rel_end,
        "absolute_char_start":absolute_base+rel_start,
        "absolute_char_end":absolute_base+rel_end,
        "char_count":rel_end-rel_start,
        "token_count":len(normalized.split()),
        "semantic_sha256":sha256_text(normalized),
        "semantic_type":semantic_type,
    }


def split_direct_can(raw:str,absolute_base:int)->dict:
    matches=list(CAN_RE.finditer(raw))
    if len(matches)!=1:
        raise RuntimeError(f"Expected exactly one standalone 'can', got {len(matches)}")
    match=matches[0]
    subject=make_span(raw,0,match.start(),absolute_base,"OPAQUE_SUBJECT_SPAN")
    predicate=make_span(raw,match.end(),len(raw),absolute_base,"OPAQUE_ACTION_PREDICATE_SPAN")
    modal_value=raw[match.start():match.end()]
    modal_norm=fingerprint_normalize(modal_value)
    if modal_norm!="can":
        raise RuntimeError("Direct modal did not normalize to 'can'")
    modal={
        "operator":"PERMISSION",
        "lexical_signal":"PERMISSION_CAN",
        "relative_char_start":match.start(),
        "relative_char_end":match.end(),
        "absolute_char_start":absolute_base+match.start(),
        "absolute_char_end":absolute_base+match.end(),
        "char_count":match.end()-match.start(),
        "token_count":1,
        "semantic_sha256":sha256_text(modal_norm),
    }
    return {
        "subject_span":subject,
        "modal_operator":modal,
        "action_predicate_span":predicate,
    }


def build_snapshot(as_of:str,cache_dir:Path,root:Path=ROOT)->dict:
    readiness=load(root/READINESS_PATH)
    semantics=load(root/SEMANTICS_PATH)
    atoms=load(root/ATOMS_PATH)

    if readiness.get("status")!="PASS" or readiness.get("readiness_version")!="CORE_RULE_SEMANTIC_AST_READINESS_V1":
        raise RuntimeError("Parent AST-readiness snapshot is not the closed PASS v1 baseline")
    if readiness.get("summary",{}).get("pilot_ready")!=1:
        raise RuntimeError("Parent readiness must expose exactly one pilot-ready paragraph")
    if readiness.get("summary",{}).get("repeated_variants_pilot_ready")!=0:
        raise RuntimeError("Repeated variants unexpectedly entered pilot readiness")

    pilot_rows=[
        x for x in readiness.get("rows",[])
        if x.get("readiness_state") in {"PILOT_READY_DIRECT_MODAL","PILOT_READY_CONDITIONAL_MODAL"}
    ]
    if len(pilot_rows)!=1:
        raise RuntimeError("Parent readiness pilot row cardinality drifted")
    ready=pilot_rows[0]
    if ready.get("paragraph_key")!=PILOT_KEY or ready.get("rule_ref")!=PILOT_RULE:
        raise RuntimeError("Parent readiness pilot identity drifted")
    if ready.get("readiness_state")!="PILOT_READY_DIRECT_MODAL":
        raise RuntimeError("Pilot is no longer direct-modal")
    if ready.get("modal_axis")!="PERMISSION" or int(ready.get("condition_cues",-1))!=0:
        raise RuntimeError("Pilot modal/condition profile drifted")

    sem_by={x["paragraph_key"]:x for x in semantics.get("classifications",[])}
    atom_by={x["paragraph_key"]:x for x in atoms.get("paragraph_atoms",[])}
    sem=sem_by.get(PILOT_KEY)
    atom=atom_by.get(PILOT_KEY)
    if not sem or not atom:
        raise RuntimeError("Pilot parent paragraph evidence missing")
    if sem.get("signals")!=[{"id":"PERMISSION_CAN","count":1}]:
        raise RuntimeError("Pilot lexical signal baseline drifted")
    if sem.get("primary_role")!="PERMISSION" or sem.get("classification_confidence")!="HIGH":
        raise RuntimeError("Pilot semantic classification baseline drifted")
    if atom.get("token_count")!=17:
        raise RuntimeError("Pilot parent token-count baseline drifted")

    page_texts,page_sha,source,verification=verified_core_pages(cache_dir,root)
    page=int(atom["page"])
    start=int(atom["char_start"])
    end=int(atom["char_end"])
    if page!=50 or start!=29 or end!=143:
        raise RuntimeError("Pilot source range baseline drifted")
    if sem.get("page_semantic_sha256")!=page_sha[page-1] or atom.get("page_semantic_sha256")!=page_sha[page-1]:
        raise RuntimeError("Pilot page semantic SHA drifted")

    raw=page_texts[page-1][start:end]
    paragraph_norm=fingerprint_normalize(raw)
    paragraph_sha=sha256_text(paragraph_norm)
    if paragraph_sha!="07bde679c8d572db04fb606c75742d71fd86691b768bc2a6e4e1dc4b86f02f52":
        raise RuntimeError("Pilot paragraph known semantic SHA drifted")
    if paragraph_sha!=sem.get("semantic_sha256") or paragraph_sha!=atom.get("semantic_sha256"):
        raise RuntimeError("Pilot paragraph parent semantic SHA mismatch")
    if token_count(raw)!=atom.get("token_count"):
        raise RuntimeError("Pilot paragraph token count does not reproduce")

    parts=split_direct_can(raw,start)
    subject=parts["subject_span"]
    modal=parts["modal_operator"]
    predicate=parts["action_predicate_span"]

    if not (subject["relative_char_end"]<=modal["relative_char_start"]<modal["relative_char_end"]<=predicate["relative_char_start"]):
        raise RuntimeError("Pilot AST spans overlap or are out of order")
    if subject["token_count"]+modal["token_count"]+predicate["token_count"]!=atom["token_count"]:
        raise RuntimeError("Pilot AST token partition does not cover parent token count")

    node={
        "node_key":"core-ast-direct-modal--13-07--p50-o1",
        "node_type":"DIRECT_MODAL_CLAUSE",
        "rule_ref":PILOT_RULE,
        "rule_key":atom["rule_key"],
        "family_id":atom["family_id"],
        "occurrence_key":atom["occurrence_key"],
        "paragraph_key":PILOT_KEY,
        "page":page,
        "paragraph_absolute_char_start":start,
        "paragraph_absolute_char_end":end,
        "paragraph_char_count":end-start,
        "paragraph_token_count":atom["token_count"],
        "paragraph_semantic_sha256":paragraph_sha,
        "page_semantic_sha256":page_sha[page-1],
        "subject_span":subject,
        "modal_operator":modal,
        "action_predicate_span":predicate,
        "condition":None,
        "validation":{
            "source_hash_reproduced":True,
            "page_hash_reproduced":True,
            "unique_modal_split":True,
            "subject_nonempty":True,
            "action_predicate_nonempty":True,
            "spans_ordered_non_overlapping":True,
            "token_partition_complete":True,
            "parent_readiness_state":"PILOT_READY_DIRECT_MODAL",
            "parent_condition_cues":0,
            "interaction_edges_created":0,
        },
    }

    complete=(
        node["subject_span"]["token_count"]>0
        and node["action_predicate_span"]["token_count"]>0
        and node["modal_operator"]["token_count"]==1
        and node["validation"]["token_partition_complete"] is True
    )
    return {
        "schema_version":"1.0",
        "status":"PASS" if complete else "FAIL",
        "snapshot_date":as_of,
        "authority":"GAMES_WORKSHOP_OFFICIAL",
        "pilot_version":PILOT_VERSION,
        "source":source,
        "source_verification":verification,
        "parent_readiness":{
            "path":READINESS_PATH,
            "readiness_version":readiness.get("readiness_version"),
            "pilot_ready":readiness.get("summary",{}).get("pilot_ready"),
            "pilot_paragraph_key":PILOT_KEY,
            "pilot_rule_ref":PILOT_RULE,
            "readiness_state":"PILOT_READY_DIRECT_MODAL",
        },
        "nodes":[node],
        "summary":{
            "ast_nodes":1,
            "unique_node_keys":1,
            "paragraphs_parsed":1,
            "direct_modal_nodes":1,
            "permission_nodes":1,
            "conditional_nodes":0,
            "subject_spans":1,
            "action_predicate_spans":1,
            "source_hashes_reproduced":1,
            "token_partitions_complete":1,
            "interaction_edges_created":0,
            "additional_paragraphs_admitted":0,
        },
        "authority_boundary":{
            "direct_modal_ast_pilot_complete":complete,
            "ast_scope":"ONE_PARAGRAPH_ONLY",
            "paragraph_prose_committed":False,
            "subject_semantic_type_resolved":False,
            "action_semantic_type_resolved":False,
            "target_object_resolved":False,
            "quantifier_resolved":False,
            "condition_effect_ast_complete":False,
            "rule_interaction_graph_complete":False,
            "repeated_variant_semantic_equivalence_claimed":False,
            "app_codex_equivalence":"NOT_CLAIMED",
            "full_faction_promotion":False,
            "current_normalized_factions_change":0,
        },
    }


def compact_report(snapshot:dict)->dict:
    node=snapshot["nodes"][0]
    return {
        "schema_version":snapshot["schema_version"],
        "status":snapshot["status"],
        "snapshot_date":snapshot["snapshot_date"],
        "authority":snapshot["authority"],
        "pilot_version":snapshot["pilot_version"],
        "source":snapshot["source"],
        "source_verification":snapshot["source_verification"],
        "parent_readiness":snapshot["parent_readiness"],
        "pilot_node":{
            "node_key":node["node_key"],
            "node_type":node["node_type"],
            "rule_ref":node["rule_ref"],
            "paragraph_key":node["paragraph_key"],
            "page":node["page"],
            "paragraph_semantic_sha256":node["paragraph_semantic_sha256"],
            "subject_span":node["subject_span"],
            "modal_operator":node["modal_operator"],
            "action_predicate_span":node["action_predicate_span"],
            "validation":node["validation"],
        },
        "summary":snapshot["summary"],
        "authority_boundary":snapshot["authority_boundary"],
    }


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--as-of",default="2026-09-30")
    ap.add_argument("--output",type=Path,default=Path("rules/11e/snapshots/2026-09-30/core_rule_direct_modal_ast_pilot/index.json"))
    ap.add_argument("--summary-output",type=Path,default=Path("reports/CORE_RULE_DIRECT_MODAL_AST_PILOT_CURRENT.json"))
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
            "pilot_version":PILOT_VERSION,
            "error":str(exc),
            "authority_boundary":{"fail_closed":True,"ast_node_promoted":False},
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
