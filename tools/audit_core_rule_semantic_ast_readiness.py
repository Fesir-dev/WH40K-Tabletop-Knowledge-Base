#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

from build_core_rule_reference_atoms import verified_core_pages
from build_core_rules_structure import fingerprint_normalize, sha256_text

ROOT=Path(__file__).resolve().parents[1]
READINESS_VERSION="CORE_RULE_SEMANTIC_AST_READINESS_V1"
REVIEW_PATH="rules/11e/snapshots/2026-09-30/core_rule_paragraph_semantic_review/index.json"
SEMANTICS_PATH="rules/11e/snapshots/2026-09-30/core_rule_paragraph_semantics/index.json"
ATOMS_PATH="rules/11e/snapshots/2026-09-30/core_rule_paragraph_atoms/index.json"

MODAL_IDS={
    "PERMISSION":("PERMISSION_CAN","PERMISSION_MAY"),
    "OBLIGATION":("OBLIGATION_MUST",),
    "PROHIBITION":("PROHIBITION_CANNOT","PROHIBITION_MUST_NOT"),
}
CONDITION_IDS=("CONDITION_IF","TRIGGER_WHEN","DURATION_WHILE","EXCEPTION_UNLESS")
DISALLOWED_SIGNAL_IDS={
    "SEQUENCE_BEFORE","SEQUENCE_AFTER","SEQUENCE_THEN","ORDERED_STEP",
    "REFERENCE_SEE","REFERENCE_RULE_REF","REFERENCE_PAGE",
    "REPLACEMENT_INSTEAD","MODIFIER_ADD_SUBTRACT",
    "DEFINITION_MEANS","DEFINITION_KNOWN_AS","DEFINITION_REFERRED_TO_AS",
}
SENTENCE_BOUNDARY_RE=re.compile(r"[.!?](?=(?:[\\\"'”’)\\]]*)?(?:\\s|$))")
TERMINAL_PUNCTUATION_RE=re.compile(r"[.!?][\\\"'”’)\\]]*$")

PRE_SHAPE_BLOCKERS={
    "BLOCKED_PARENT_REVIEW",
    "BLOCKED_NO_NORMATIVE_MODAL",
    "BLOCKED_MODAL_MULTIPLICITY",
    "BLOCKED_COMPLEX_SEMANTIC_AXES",
    "BLOCKED_MULTIPLE_CONDITION_CUES",
    "BLOCKED_REPEATED_VARIANT",
}
SHAPE_BLOCKERS={
    "BLOCKED_SENTENCE_SHAPE",
    "BLOCKED_COMPLEX_DELIMITERS",
    "BLOCKED_PARENTHETICAL_SCOPE",
}
PILOT_READY={
    "PILOT_READY_DIRECT_MODAL",
    "PILOT_READY_CONDITIONAL_MODAL",
}


def load(path:Path)->dict:
    return json.loads(path.read_text(encoding="utf-8"))


def signal_counts(row:dict)->dict[str,int]:
    return {
        str(x["id"]):int(x["count"])
        for x in row.get("signals",[])
        if x.get("id") and int(x.get("count",0))>0
    }


def count_ids(counts:dict[str,int], ids)->int:
    return sum(int(counts.get(x,0)) for x in ids)


def pre_shape_gate(profile:dict, semantic_row:dict)->tuple[str|None,dict]:
    counts=signal_counts(semantic_row)
    modal_axis=profile.get("modal_axis")
    condition_cues=count_ids(counts,CONDITION_IDS)

    evidence={
        "modal_occurrences":0,
        "condition_cues":condition_cues,
    }

    if profile.get("review_state")!="AXIS_PROFILE_READY":
        return "BLOCKED_PARENT_REVIEW",evidence

    if modal_axis=="NONE":
        return "BLOCKED_NO_NORMATIVE_MODAL",evidence

    if modal_axis not in MODAL_IDS:
        return "BLOCKED_PARENT_REVIEW",evidence

    modal_occurrences=count_ids(counts,MODAL_IDS[modal_axis])
    evidence["modal_occurrences"]=modal_occurrences
    if modal_occurrences!=1:
        return "BLOCKED_MODAL_MULTIPLICITY",evidence

    if (
        profile.get("procedure_sequence_present")
        or profile.get("definition_present")
        or profile.get("modification_replacement_present")
        or profile.get("reference_present")
        or profile.get("structural_list_present")
        or any(counts.get(x,0)>0 for x in DISALLOWED_SIGNAL_IDS)
    ):
        return "BLOCKED_COMPLEX_SEMANTIC_AXES",evidence

    if condition_cues>1:
        return "BLOCKED_MULTIPLE_CONDITION_CUES",evidence

    if profile.get("parent_paragraph_classification")=="REPEATED_OCCURRENCE_PARAGRAPH_VARIANT":
        return "BLOCKED_REPEATED_VARIANT",evidence

    return None,evidence


def range_shape(raw:str)->dict:
    normalized=fingerprint_normalize(raw)
    sentence_boundaries=len(SENTENCE_BOUNDARY_RE.findall(normalized))
    terminal=bool(TERMINAL_PUNCTUATION_RE.search(normalized))
    complex_delimiters=normalized.count(":")+normalized.count(";")
    parenthetical_delimiters=sum(normalized.count(x) for x in "()[]")
    return {
        "sentence_boundary_count":sentence_boundaries,
        "terminal_punctuation_at_end":terminal,
        "complex_delimiter_count":complex_delimiters,
        "parenthetical_delimiter_count":parenthetical_delimiters,
    }


def shape_gate(shape:dict,condition_cues:int)->str:
    if shape["sentence_boundary_count"]!=1 or shape["terminal_punctuation_at_end"] is not True:
        return "BLOCKED_SENTENCE_SHAPE"
    if shape["complex_delimiter_count"]>0:
        return "BLOCKED_COMPLEX_DELIMITERS"
    if shape["parenthetical_delimiter_count"]>0:
        return "BLOCKED_PARENTHETICAL_SCOPE"
    return "PILOT_READY_CONDITIONAL_MODAL" if condition_cues==1 else "PILOT_READY_DIRECT_MODAL"


def build_snapshot(as_of:str,cache_dir:Path,root:Path=ROOT)->dict:
    review=load(root/REVIEW_PATH)
    semantics=load(root/SEMANTICS_PATH)
    atoms=load(root/ATOMS_PATH)

    if review.get("status")!="PASS" or review.get("review_version")!="CORE_RULE_PARAGRAPH_SEMANTIC_REVIEW_V1":
        raise RuntimeError("Parent semantic review is not the closed v1 PASS baseline")
    if semantics.get("status")!="PASS" or semantics.get("classifier_version")!="CORE_RULE_PARAGRAPH_SEMANTIC_CLASSIFICATION_V1":
        raise RuntimeError("Parent semantic classification is not the closed v1 PASS baseline")
    if atoms.get("status")!="PASS" or atoms.get("atomization_version")!="CORE_RULE_PARAGRAPH_ATOMIZATION_V1":
        raise RuntimeError("Parent paragraph atomization is not the closed v1 PASS baseline")

    expected_review={
        "AXIS_PROFILE_READY":156,
        "MULTI_MODAL_REVIEW_REQUIRED":42,
        "NO_STRONG_SIGNAL_REVIEW_REQUIRED":112,
    }
    if review.get("summary",{}).get("review_state_counts")!=expected_review:
        raise RuntimeError("Parent semantic review-state baseline drifted")

    profiles=review.get("profiles",[])
    semantic_rows=semantics.get("classifications",[])
    atom_rows=atoms.get("paragraph_atoms",[])
    if len(profiles)!=310 or len(semantic_rows)!=310 or len(atom_rows)!=310:
        raise RuntimeError("Parent paragraph row counts drifted from 310")

    sem_by_key={x["paragraph_key"]:x for x in semantic_rows}
    atom_by_key={x["paragraph_key"]:x for x in atom_rows}
    if set(sem_by_key)!={x["paragraph_key"] for x in profiles} or set(atom_by_key)!=set(sem_by_key):
        raise RuntimeError("Parent paragraph identity sets do not match")

    page_texts,page_sha,source,verification=verified_core_pages(cache_dir,root)
    if len(page_texts)!=88:
        raise RuntimeError(f"Verified Core page count drift: {len(page_texts)}")

    rows=[]
    state_counts=Counter()
    shape_state_counts=Counter()
    hash_reproduced=0
    shape_analyzed=0

    for profile in profiles:
        key=profile["paragraph_key"]
        sem=sem_by_key[key]
        atom=atom_by_key[key]

        state,evidence=pre_shape_gate(profile,sem)
        shape=None
        hash_verified=False

        if state is None:
            shape_analyzed+=1
            page=int(sem["page"])
            start=int(sem["char_start"])
            end=int(sem["char_end"])
            if not 1<=page<=len(page_texts) or start<0 or end<start:
                raise RuntimeError(f"Invalid source range for {key}")
            raw=page_texts[page-1][start:end]
            reproduced=sha256_text(fingerprint_normalize(raw))
            if reproduced!=sem.get("semantic_sha256"):
                raise RuntimeError(f"Semantic SHA does not reproduce for readiness candidate {key}")
            if sem.get("page_semantic_sha256")!=page_sha[page-1]:
                raise RuntimeError(f"Page semantic SHA drift for readiness candidate {key}")
            hash_verified=True
            hash_reproduced+=1
            shape=range_shape(raw)
            state=shape_gate(shape,int(evidence["condition_cues"]))
            shape_state_counts[state]+=1

        state_counts[state]+=1

        rows.append({
            "paragraph_key":key,
            "rule_ref":profile["rule_ref"],
            "rule_key":profile.get("rule_key"),
            "family_id":profile.get("family_id"),
            "occurrence_key":profile["occurrence_key"],
            "parent_paragraph_classification":profile.get("parent_paragraph_classification"),
            "semantic_sha256":profile["semantic_sha256"],
            "parent_review_state":profile["review_state"],
            "modal_axis":profile["modal_axis"],
            "modal_occurrences":int(evidence["modal_occurrences"]),
            "condition_cues":int(evidence["condition_cues"]),
            "token_count":int(atom["token_count"]),
            "line_count":int(atom["line_count"]),
            "char_count":int(atom["char_count"]),
            "readiness_state":state,
            "source_shape_analyzed":shape is not None,
            "source_hash_reproduced":hash_verified,
            "shape_evidence":shape,
            "ast_node_created":False,
        })

    expected_pre={
        "BLOCKED_PARENT_REVIEW":154,
        "BLOCKED_NO_NORMATIVE_MODAL":61,
        "BLOCKED_MODAL_MULTIPLICITY":27,
        "BLOCKED_COMPLEX_SEMANTIC_AXES":26,
        "BLOCKED_MULTIPLE_CONDITION_CUES":6,
        "BLOCKED_REPEATED_VARIANT":2,
    }
    pre_counts={k:state_counts.get(k,0) for k in expected_pre}
    pilot_ready=sum(state_counts.get(x,0) for x in PILOT_READY)
    shape_blocked=sum(state_counts.get(x,0) for x in SHAPE_BLOCKERS)
    repeated_ready=sum(
        1 for x in rows
        if x["parent_paragraph_classification"]=="REPEATED_OCCURRENCE_PARAGRAPH_VARIANT"
        and x["readiness_state"] in PILOT_READY
    )

    complete=(
        len(rows)==310
        and len({x["paragraph_key"] for x in rows})==310
        and pre_counts==expected_pre
        and shape_analyzed==34
        and hash_reproduced==34
        and pilot_ready+shape_blocked==34
        and sum(state_counts.values())==310
        and repeated_ready==0
        and all(x["ast_node_created"] is False for x in rows)
    )

    return {
        "schema_version":"1.0",
        "status":"PASS" if complete else "FAIL",
        "snapshot_date":as_of,
        "authority":"GAMES_WORKSHOP_OFFICIAL",
        "readiness_version":READINESS_VERSION,
        "source":source,
        "source_verification":verification,
        "parent_review":{
            "path":REVIEW_PATH,
            "review_version":review.get("review_version"),
            "profiles":review.get("summary",{}).get("profiles"),
            "review_state_counts":review.get("summary",{}).get("review_state_counts"),
            "axis_profile_ready":review.get("summary",{}).get("axis_profile_ready"),
            "review_required":review.get("summary",{}).get("review_required"),
        },
        "readiness_contract":{
            "ordered_gates":[
                "PARENT_REVIEW",
                "NORMATIVE_MODAL_AXIS",
                "MODAL_LEXICAL_MULTIPLICITY",
                "EXTRA_SEMANTIC_AXES",
                "CONDITION_CUE_MULTIPLICITY",
                "REPEATED_VARIANT",
                "SENTENCE_SHAPE",
                "COMPLEX_DELIMITERS",
                "PARENTHETICAL_SCOPE",
            ],
            "pilot_ready_states":sorted(PILOT_READY),
            "pilot_ready_is_ast_complete":False,
            "ast_nodes_created":False,
        },
        "rows":rows,
        "summary":{
            "rows":len(rows),
            "unique_paragraph_keys":len({x["paragraph_key"] for x in rows}),
            "readiness_state_counts":dict(sorted(state_counts.items())),
            "pre_shape_blocker_counts":pre_counts,
            "source_shape_analysis_candidates":shape_analyzed,
            "source_shape_hashes_reproduced":hash_reproduced,
            "shape_state_counts":dict(sorted(shape_state_counts.items())),
            "pilot_ready":pilot_ready,
            "pilot_ready_direct_modal":state_counts.get("PILOT_READY_DIRECT_MODAL",0),
            "pilot_ready_conditional_modal":state_counts.get("PILOT_READY_CONDITIONAL_MODAL",0),
            "shape_blocked":shape_blocked,
            "repeated_variants_pilot_ready":repeated_ready,
        },
        "authority_boundary":{
            "ast_readiness_audit_complete":complete,
            "pilot_ready_is_not_ast_node":True,
            "pilot_ready_is_not_normative_semantic_equivalence":True,
            "paragraph_prose_committed":False,
            "ast_nodes_created":False,
            "condition_effect_ast_complete":False,
            "rule_interaction_graph_complete":False,
            "repeated_variant_semantic_equivalence_claimed":False,
            "app_codex_equivalence":"NOT_CLAIMED",
            "full_faction_promotion":False,
            "current_normalized_factions_change":0,
        },
    }


def compact_report(snapshot:dict)->dict:
    return {
        "schema_version":snapshot["schema_version"],
        "status":snapshot["status"],
        "snapshot_date":snapshot["snapshot_date"],
        "authority":snapshot["authority"],
        "readiness_version":snapshot["readiness_version"],
        "source":snapshot["source"],
        "source_verification":snapshot["source_verification"],
        "parent_review":snapshot["parent_review"],
        "readiness_contract":snapshot["readiness_contract"],
        "summary":snapshot["summary"],
        "authority_boundary":snapshot["authority_boundary"],
    }


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--as-of",default="2026-09-30")
    ap.add_argument("--output",type=Path,default=Path("rules/11e/snapshots/2026-09-30/core_rule_semantic_ast_readiness/index.json"))
    ap.add_argument("--summary-output",type=Path,default=Path("reports/CORE_RULE_SEMANTIC_AST_READINESS_CURRENT.json"))
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
            "readiness_version":READINESS_VERSION,
            "error":str(exc),
            "authority_boundary":{"fail_closed":True,"ast_readiness_promoted":False,"ast_nodes_created":False},
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
