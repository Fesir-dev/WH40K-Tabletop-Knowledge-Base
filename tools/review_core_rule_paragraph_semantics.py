#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REVIEW_VERSION="CORE_RULE_PARAGRAPH_SEMANTIC_REVIEW_V1"
PARENT_PATH="rules/11e/snapshots/2026-09-30/core_rule_paragraph_semantics/index.json"

MODAL_FAMILIES=("PERMISSION","OBLIGATION","PROHIBITION")
STRONG_FAMILIES={
    "PERMISSION",
    "OBLIGATION",
    "PROHIBITION",
    "CONDITION_OR_TRIGGER",
    "PROCEDURE_OR_SEQUENCE",
    "DEFINITION",
    "MODIFICATION_OR_REPLACEMENT",
}


def load(path:Path)->dict:
    return json.loads(path.read_text(encoding="utf-8"))


def review_profile(row:dict)->dict:
    family_counts=dict(row.get("signal_family_counts",{}))
    families=set(family_counts)

    modals=[x for x in MODAL_FAMILIES if x in families]
    if len(modals)==0:
        modal_axis="NONE"
    elif len(modals)==1:
        modal_axis=modals[0]
    else:
        modal_axis="MULTI_MODAL"

    strong_present=bool(families & STRONG_FAMILIES)

    if len(modals)>=2:
        review_state="MULTI_MODAL_REVIEW_REQUIRED"
        review_reason="MULTIPLE_NORMATIVE_MODAL_FAMILIES"
    elif strong_present:
        review_state="AXIS_PROFILE_READY"
        review_reason="NO_MODAL_CONFLICT_WITH_STRONG_EVIDENCE"
    else:
        review_state="NO_STRONG_SIGNAL_REVIEW_REQUIRED"
        review_reason="NO_STRONG_SEMANTIC_FAMILY"

    signal_ids=[x.get("id") for x in row.get("signals",[]) if x.get("id")]

    return {
        "paragraph_key":row["paragraph_key"],
        "rule_ref":row["rule_ref"],
        "rule_key":row.get("rule_key"),
        "family_id":row.get("family_id"),
        "occurrence_key":row["occurrence_key"],
        "occurrence_ordinal":row.get("occurrence_ordinal"),
        "paragraph_ordinal_in_occurrence":row.get("paragraph_ordinal_in_occurrence"),
        "parent_paragraph_classification":row.get("parent_paragraph_classification"),
        "parent_primary_role":row["primary_role"],
        "parent_confidence":row["classification_confidence"],
        "semantic_sha256":row["semantic_sha256"],
        "signal_ids":signal_ids,
        "signal_family_counts":family_counts,
        "modal_axis":modal_axis,
        "condition_trigger_present":"CONDITION_OR_TRIGGER" in families,
        "procedure_sequence_present":"PROCEDURE_OR_SEQUENCE" in families,
        "definition_present":"DEFINITION" in families,
        "modification_replacement_present":"MODIFICATION_OR_REPLACEMENT" in families,
        "reference_present":"REFERENCE_OR_CROSS_REFERENCE" in families,
        "structural_list_present":"STRUCTURAL_LIST" in families or "BULLET_LIKE" in signal_ids,
        "review_state":review_state,
        "review_reason":review_reason,
        "ast_readiness_claimed":False,
    }


def build_snapshot(as_of:str,root:Path=ROOT)->dict:
    parent=load(root/PARENT_PATH)
    if parent.get("status")!="PASS":
        raise RuntimeError("Parent paragraph semantic classification is not PASS")
    if parent.get("classifier_version")!="CORE_RULE_PARAGRAPH_SEMANTIC_CLASSIFICATION_V1":
        raise RuntimeError("Parent classifier version drifted")

    summary=parent.get("summary",{})
    expected={
        "paragraphs":310,
        "unique_paragraph_keys":310,
        "mixed_paragraphs":134,
        "unclassified_paragraphs":112,
        "paragraph_hashes_reproduced_from_verified_pdf":310,
    }
    for key,value in expected.items():
        if summary.get(key)!=value:
            raise RuntimeError(f"Parent semantic classification drift: {key}={summary.get(key)} != {value}")

    confidence=summary.get("confidence_counts",{})
    if confidence!={"HIGH":64,"MIXED":134,"NONE":112}:
        raise RuntimeError(f"Parent confidence baseline drifted: {confidence}")

    rows=parent.get("classifications",[])
    if len(rows)!=310:
        raise RuntimeError(f"Parent classification row count drifted: {len(rows)}")

    profiles=[review_profile(row) for row in rows]
    keys=[x["paragraph_key"] for x in profiles]
    if len(set(keys))!=310:
        raise RuntimeError("Review profile paragraph keys are not unique")

    state_counts=Counter(x["review_state"] for x in profiles)
    modal_counts=Counter(x["modal_axis"] for x in profiles)
    parent_role_counts=Counter(x["parent_primary_role"] for x in profiles)
    repeated_state_counts=Counter(
        x["review_state"]
        for x in profiles
        if x["parent_paragraph_classification"]=="REPEATED_OCCURRENCE_PARAGRAPH_VARIANT"
    )

    mixed_rows=[x for x in profiles if x["parent_primary_role"]=="MIXED"]
    unclassified_rows=[x for x in profiles if x["parent_primary_role"]=="UNCLASSIFIED"]

    mixed_decomposition={
        "axis_profile_ready":sum(x["review_state"]=="AXIS_PROFILE_READY" for x in mixed_rows),
        "multi_modal_review_required":sum(x["review_state"]=="MULTI_MODAL_REVIEW_REQUIRED" for x in mixed_rows),
        "no_strong_signal_review_required":sum(x["review_state"]=="NO_STRONG_SIGNAL_REVIEW_REQUIRED" for x in mixed_rows),
    }
    unclassified_decomposition={
        "signal_free":sum(len(x["signal_ids"])==0 for x in unclassified_rows),
        "weak_only":sum(len(x["signal_ids"])>0 for x in unclassified_rows),
        "review_required":sum(x["review_state"]!="AXIS_PROFILE_READY" for x in unclassified_rows),
    }

    expected_states={
        "AXIS_PROFILE_READY":156,
        "MULTI_MODAL_REVIEW_REQUIRED":42,
        "NO_STRONG_SIGNAL_REVIEW_REQUIRED":112,
    }
    expected_modals={
        "MULTI_MODAL":42,
        "NONE":173,
        "OBLIGATION":17,
        "PERMISSION":67,
        "PROHIBITION":11,
    }

    complete=(
        dict(sorted(state_counts.items()))==dict(sorted(expected_states.items()))
        and dict(sorted(modal_counts.items()))==dict(sorted(expected_modals.items()))
        and mixed_decomposition=={
            "axis_profile_ready":92,
            "multi_modal_review_required":42,
            "no_strong_signal_review_required":0,
        }
        and unclassified_decomposition=={
            "signal_free":110,
            "weak_only":2,
            "review_required":112,
        }
        and repeated_state_counts==Counter({
            "AXIS_PROFILE_READY":4,
            "MULTI_MODAL_REVIEW_REQUIRED":6,
        })
    )

    return {
        "schema_version":"1.0",
        "status":"PASS" if complete else "FAIL",
        "snapshot_date":as_of,
        "authority":"GAMES_WORKSHOP_OFFICIAL",
        "review_version":REVIEW_VERSION,
        "parent_classification":{
            "path":PARENT_PATH,
            "classifier_version":parent.get("classifier_version"),
            "source":parent.get("source"),
            "source_verification":parent.get("source_verification"),
            "paragraphs":summary.get("paragraphs"),
            "unique_paragraph_keys":summary.get("unique_paragraph_keys"),
            "confidence_counts":summary.get("confidence_counts"),
            "role_counts":summary.get("role_counts"),
            "paragraph_hashes_reproduced_from_verified_pdf":summary.get("paragraph_hashes_reproduced_from_verified_pdf"),
        },
        "review_contract":{
            "semantic_axes":[
                "modal_axis",
                "condition_trigger_present",
                "procedure_sequence_present",
                "definition_present",
                "modification_replacement_present",
                "reference_present",
                "structural_list_present",
            ],
            "modal_values":["NONE","PERMISSION","OBLIGATION","PROHIBITION","MULTI_MODAL"],
            "review_states":[
                "AXIS_PROFILE_READY",
                "MULTI_MODAL_REVIEW_REQUIRED",
                "NO_STRONG_SIGNAL_REVIEW_REQUIRED",
            ],
            "axis_profile_ready_is_ast_ready":False,
            "multi_modal_precedence_inferred":False,
            "unclassified_forced_resolution":False,
        },
        "profiles":profiles,
        "summary":{
            "profiles":len(profiles),
            "unique_paragraph_keys":len(set(keys)),
            "review_state_counts":dict(sorted(state_counts.items())),
            "modal_axis_counts":dict(sorted(modal_counts.items())),
            "parent_role_counts":dict(sorted(parent_role_counts.items())),
            "axis_profile_ready":state_counts.get("AXIS_PROFILE_READY",0),
            "review_required":len(profiles)-state_counts.get("AXIS_PROFILE_READY",0),
            "mixed_decomposition":mixed_decomposition,
            "unclassified_decomposition":unclassified_decomposition,
            "repeated_variant_review_state_counts":dict(sorted(repeated_state_counts.items())),
            "parent_hashes_verified":sum(len(str(x.get("semantic_sha256") or ""))==64 for x in profiles),
        },
        "authority_boundary":{
            "semantic_review_complete":complete,
            "multi_axis_profile_is_not_condition_effect_ast":True,
            "axis_profile_ready_is_not_ast_readiness_claim":True,
            "multi_modal_rows_remain_unresolved":True,
            "no_strong_signal_rows_remain_unresolved":True,
            "paragraph_prose_committed":False,
            "condition_effect_ast_complete":False,
            "rule_interaction_graph_complete":False,
            "repeated_variant_semantic_equivalence_claimed":False,
            "app_codex_equivalence":"NOT_CLAIMED",
            "full_faction_promotion":False,
            "current_normalized_factions_change":0,
            "next_milestone":"CORE_RULE_SEMANTIC_AST_READINESS_V1",
        },
    }


def compact_report(snapshot:dict)->dict:
    return {
        "schema_version":snapshot["schema_version"],
        "status":snapshot["status"],
        "snapshot_date":snapshot["snapshot_date"],
        "authority":snapshot["authority"],
        "review_version":snapshot["review_version"],
        "parent_classification":snapshot["parent_classification"],
        "review_contract":snapshot["review_contract"],
        "summary":snapshot["summary"],
        "authority_boundary":snapshot["authority_boundary"],
    }


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--as-of",default="2026-09-30")
    ap.add_argument("--output",type=Path,default=Path("rules/11e/snapshots/2026-09-30/core_rule_paragraph_semantic_review/index.json"))
    ap.add_argument("--summary-output",type=Path,default=Path("reports/CORE_RULE_PARAGRAPH_SEMANTIC_REVIEW_CURRENT.json"))
    args=ap.parse_args()

    out=args.output if args.output.is_absolute() else ROOT/args.output
    summary_out=args.summary_output if args.summary_output.is_absolute() else ROOT/args.summary_output

    try:
        snapshot=build_snapshot(args.as_of)
    except Exception as exc:
        failure={
            "schema_version":"1.0",
            "status":"FAIL",
            "snapshot_date":args.as_of,
            "authority":"GAMES_WORKSHOP_OFFICIAL",
            "review_version":REVIEW_VERSION,
            "error":str(exc),
            "authority_boundary":{"fail_closed":True,"semantic_review_promoted":False},
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
