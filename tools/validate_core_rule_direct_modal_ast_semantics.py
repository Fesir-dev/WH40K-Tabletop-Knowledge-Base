#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from build_core_rule_reference_atoms import verified_core_pages
from build_core_rules_structure import fingerprint_normalize, sha256_text

ROOT=Path(__file__).resolve().parents[1]
VERSION="CORE_RULE_DIRECT_MODAL_AST_SEMANTIC_VALIDATION_V1"
PILOT_PATH="rules/11e/snapshots/2026-09-30/core_rule_direct_modal_ast_pilot/index.json"
TARGET_NODE="core-ast-direct-modal--13-07--p50-o1"
TARGET_PARAGRAPH="core-rule-13-07--p50--l1--para-p50-o1"

SUBJECT_LEXICON={
    "model":"MODEL",
    "models":"MODEL",
    "unit":"UNIT",
    "units":"UNIT",
    "player":"PLAYER",
    "players":"PLAYER",
    "weapon":"WEAPON",
    "weapons":"WEAPON",
    "attack":"ATTACK",
    "attacks":"ATTACK",
    "objective":"OBJECTIVE",
    "objectives":"OBJECTIVE",
    "aircraft":"AIRCRAFT",
    "vehicle":"VEHICLE",
    "vehicles":"VEHICLE",
    "monster":"MONSTER",
    "monsters":"MONSTER",
    "psyker":"PSYKER",
    "psykers":"PSYKER",
    "character":"CHARACTER",
    "characters":"CHARACTER",
    "transport":"TRANSPORT",
    "transports":"TRANSPORT",
    "infantry":"INFANTRY",
    "mounted":"MOUNTED",
}

ACTION_LEXICON={
    ("move",):"MOVE",
    ("moves",):"MOVE",
    ("shoot",):"SHOOT",
    ("shoots",):"SHOOT",
    ("charge",):"CHARGE",
    ("charges",):"CHARGE",
    ("fight",):"FIGHT",
    ("fights",):"FIGHT",
    ("advance",):"ADVANCE",
    ("advances",):"ADVANCE",
    ("embark",):"EMBARK",
    ("embarks",):"EMBARK",
    ("disembark",):"DISEMBARK",
    ("disembarks",):"DISEMBARK",
    ("deploy",):"DEPLOY",
    ("deploys",):"DEPLOY",
    ("select",):"SELECT",
    ("selects",):"SELECT",
    ("target",):"TARGET",
    ("targets",):"TARGET",
    ("use",):"USE",
    ("uses",):"USE",
    ("fall","back"):"FALL_BACK",
    ("set","up"):"SET_UP",
}

CONDITION_CUES={"if","when","while","unless","after","before"}
MODAL_CUES={"can","cannot","cant","may","must","should","could","would"}
NEGATION_CUES={"not","never","cannot","cant"}
COORDINATION_CUES={"and","or"}
SUBORDINATE_CUES={"that","which","who","where","until","because","except"}


def load(path:Path)->dict:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_tokens(value:str)->list[str]:
    norm=fingerprint_normalize(value).casefold()
    norm=norm.replace("’","'").replace("‘","'")
    return re.findall(r"[a-z0-9]+(?:'[a-z0-9]+)?",norm)


def semantic_hash(value:str)->str:
    return sha256_text(fingerprint_normalize(value))


def span_text(page_text:str,node:dict,span:dict)->str:
    start=int(span["absolute_char_start"])
    end=int(span["absolute_char_end"])
    pstart=int(node["paragraph_absolute_char_start"])
    pend=int(node["paragraph_absolute_char_end"])
    if not (pstart<=start<end<=pend):
        raise RuntimeError("Child span escapes pilot paragraph range")
    return page_text[start:end]


def classify_subject(raw:str,span:dict)->dict:
    toks=canonical_tokens(raw)
    if len(toks)!=1:
        return {
            "state":"OPAQUE_PRESERVED",
            "resolved":False,
            "semantic_type":"OPAQUE_SUBJECT_SPAN",
            "token_count":len(toks),
            "semantic_sha256":semantic_hash(raw),
            "reason":"SUBJECT_NOT_SINGLE_CANONICAL_TOKEN",
        }
    token=toks[0]
    resolved=SUBJECT_LEXICON.get(token)
    return {
        "state":"DETERMINISTIC_TYPE" if resolved else "OPAQUE_PRESERVED",
        "resolved":bool(resolved),
        "semantic_type":resolved or "OPAQUE_SUBJECT_SPAN",
        "token_count":1,
        "semantic_sha256":semantic_hash(raw),
        "lexeme_sha256":sha256_text(token),
        "reason":"EXACT_CLOSED_SUBJECT_LEXICON" if resolved else "LEXEME_NOT_IN_CLOSED_SUBJECT_LEXICON",
    }


def action_head(tokens:list[str])->tuple[str|None,int]:
    for width in (2,1):
        if len(tokens)>=width:
            key=tuple(tokens[:width])
            if key in ACTION_LEXICON:
                return ACTION_LEXICON[key],width
    return None,0


def classify_predicate(raw:str,span:dict)->dict:
    toks=canonical_tokens(raw)
    action,width=action_head(toks)
    blockers=[]
    tail=toks[width:] if width else toks
    if not action:
        blockers.append("UNRECOGNIZED_ACTION_HEAD")
    if any(x in MODAL_CUES for x in toks):
        blockers.append("ADDITIONAL_MODAL_CUE")
    if any(x in CONDITION_CUES for x in toks):
        blockers.append("CONDITION_CUE")
    if any(x in NEGATION_CUES for x in toks):
        blockers.append("NEGATION_CUE")
    if any(x in COORDINATION_CUES for x in toks):
        blockers.append("COORDINATION_CUE")
    if any(x in SUBORDINATE_CUES for x in toks):
        blockers.append("SUBORDINATE_CLAUSE_CUE")
    blockers=sorted(set(blockers))
    decomposable=bool(action) and not blockers
    head_char_end=None
    head_hash=None
    arg_hash=None
    if decomposable:
        # Derive a lexical head only; arguments remain opaque.
        words=list(re.finditer(r"[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?",raw))
        if len(words)<width:
            raise RuntimeError("Action token/character indexing drift")
        head_char_end=words[width-1].end()
        head_hash=semantic_hash(raw[:head_char_end])
        arg_hash=semantic_hash(raw[head_char_end:]) if raw[head_char_end:].strip() else None
    return {
        "state":"ACTION_HEAD_TYPED_ARGUMENTS_OPAQUE" if decomposable else "OPAQUE_PRESERVED",
        "decomposable":decomposable,
        "action_type":action,
        "action_head_token_count":width,
        "predicate_token_count":len(toks),
        "semantic_sha256":semantic_hash(raw),
        "action_head_semantic_sha256":head_hash,
        "opaque_arguments_semantic_sha256":arg_hash,
        "opaque_arguments_token_count":len(tail) if decomposable else len(toks),
        "blockers":blockers,
    }


def build_snapshot(as_of:str,cache_dir:Path,root:Path=ROOT)->dict:
    pilot=load(root/PILOT_PATH)
    if pilot.get("status")!="PASS" or pilot.get("pilot_version")!="CORE_RULE_DIRECT_MODAL_AST_PILOT_V1":
        raise RuntimeError("Parent direct-modal pilot is not the closed PASS v1 baseline")
    nodes=pilot.get("nodes",[])
    if len(nodes)!=1:
        raise RuntimeError("Semantic validation requires exactly one pilot node")
    node=nodes[0]
    if node.get("node_key")!=TARGET_NODE or node.get("paragraph_key")!=TARGET_PARAGRAPH:
        raise RuntimeError("Pilot target identity drifted")
    if pilot.get("summary",{}).get("additional_paragraphs_admitted")!=0:
        raise RuntimeError("Pilot unexpectedly admitted additional paragraphs")
    if pilot.get("summary",{}).get("interaction_edges_created")!=0:
        raise RuntimeError("Pilot unexpectedly created interaction edges")

    pages,page_sha,source,verification=verified_core_pages(cache_dir,root)
    page=int(node["page"])
    if node.get("page_semantic_sha256")!=page_sha[page-1]:
        raise RuntimeError("Pilot page hash no longer reproduces")
    pstart=int(node["paragraph_absolute_char_start"])
    pend=int(node["paragraph_absolute_char_end"])
    paragraph_raw=pages[page-1][pstart:pend]
    if semantic_hash(paragraph_raw)!=node["paragraph_semantic_sha256"]:
        raise RuntimeError("Pilot paragraph semantic hash no longer reproduces")

    subject_raw=span_text(pages[page-1],node,node["subject_span"])
    predicate_raw=span_text(pages[page-1],node,node["action_predicate_span"])
    if semantic_hash(subject_raw)!=node["subject_span"]["semantic_sha256"]:
        raise RuntimeError("Subject span hash no longer reproduces")
    if semantic_hash(predicate_raw)!=node["action_predicate_span"]["semantic_sha256"]:
        raise RuntimeError("Predicate span hash no longer reproduces")

    subject=classify_subject(subject_raw,node["subject_span"])
    predicate=classify_predicate(predicate_raw,node["action_predicate_span"])
    resolved=int(subject["resolved"])+int(predicate["decomposable"])
    decision={
        2:"FULL_REFINEMENT_ALLOWED",
        1:"PARTIAL_REFINEMENT_ALLOWED",
        0:"OPAQUE_PRESERVED",
    }[resolved]

    return {
        "schema_version":"1.0",
        "status":"PASS",
        "snapshot_date":as_of,
        "authority":"GAMES_WORKSHOP_OFFICIAL",
        "validation_version":VERSION,
        "source":source,
        "source_verification":verification,
        "parent_pilot":{
            "path":PILOT_PATH,
            "node_key":TARGET_NODE,
            "paragraph_key":TARGET_PARAGRAPH,
            "rule_ref":node["rule_ref"],
            "node_type":node["node_type"],
            "paragraph_semantic_sha256":node["paragraph_semantic_sha256"],
            "subject_span_semantic_sha256":node["subject_span"]["semantic_sha256"],
            "action_predicate_span_semantic_sha256":node["action_predicate_span"]["semantic_sha256"],
        },
        "validation":{
            "subject":subject,
            "action_predicate":predicate,
            "decision":decision,
            "ast_mutated":False,
            "interaction_edges_created":0,
            "additional_paragraphs_admitted":0,
        },
        "summary":{
            "nodes_validated":1,
            "paragraphs_validated":1,
            "subject_types_resolved":int(subject["resolved"]),
            "predicate_heads_resolved":int(predicate["decomposable"]),
            "full_refinement_allowed":int(decision=="FULL_REFINEMENT_ALLOWED"),
            "partial_refinement_allowed":int(decision=="PARTIAL_REFINEMENT_ALLOWED"),
            "opaque_preserved":int(decision=="OPAQUE_PRESERVED"),
            "interaction_edges_created":0,
            "additional_paragraphs_admitted":0,
        },
        "authority_boundary":{
            "semantic_validation_only":True,
            "ast_mutation_allowed":False,
            "second_paragraph_allowed":False,
            "interaction_edges_allowed":False,
            "subject_closed_lexicon_only":True,
            "predicate_closed_action_lexicon_only":True,
            "arguments_remain_opaque":True,
            "condition_effect_ast_complete":False,
            "rule_interaction_graph_complete":False,
            "repeated_variant_semantic_equivalence_claimed":False,
            "app_codex_equivalence":"NOT_CLAIMED",
            "full_faction_promotion":False,
            "current_normalized_factions_change":0,
            "copyright_policy":"No paragraph prose committed; validation stores only semantic identifiers, blockers, offsets inherited from the parent node and hashes.",
        },
    }


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--as-of",default="2026-09-30")
    ap.add_argument("--output",type=Path,default=Path("reports/CORE_RULE_DIRECT_MODAL_AST_SEMANTIC_VALIDATION_CURRENT.json"))
    ap.add_argument("--snapshot-output",type=Path,default=Path("rules/11e/snapshots/2026-09-30/core_rule_direct_modal_ast_semantic_validation/index.json"))
    ap.add_argument("--cache-dir",type=Path,default=ROOT/".cache"/"official-public-rules")
    args=ap.parse_args()
    out=args.output if args.output.is_absolute() else ROOT/args.output
    snap=args.snapshot_output if args.snapshot_output.is_absolute() else ROOT/args.snapshot_output
    try:
        data=build_snapshot(args.as_of,args.cache_dir)
    except Exception as exc:
        failure={
            "schema_version":"1.0",
            "status":"SOURCE_DRIFT",
            "snapshot_date":args.as_of,
            "authority":"GAMES_WORKSHOP_OFFICIAL",
            "validation_version":VERSION,
            "error":str(exc),
            "authority_boundary":{"fail_closed":True,"ast_mutated":False},
        }
        out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(failure,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        print(json.dumps(failure,ensure_ascii=False))
        return 2
    out.parent.mkdir(parents=True,exist_ok=True)
    snap.parent.mkdir(parents=True,exist_ok=True)
    payload=json.dumps(data,ensure_ascii=False,indent=2)+"\n"
    out.write_text(payload,encoding="utf-8")
    snap.write_text(payload,encoding="utf-8")
    print(json.dumps({"status":data["status"],"decision":data["validation"]["decision"],"summary":data["summary"]},ensure_ascii=False,indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
