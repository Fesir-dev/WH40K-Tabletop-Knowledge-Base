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
CLASSIFIER_VERSION="CORE_RULE_PARAGRAPH_SEMANTIC_CLASSIFICATION_V1"
PARENT_ATOMS="rules/11e/snapshots/2026-09-30/core_rule_paragraph_atoms/index.json"

ROLE_ORDER=[
    "PROHIBITION",
    "OBLIGATION",
    "PERMISSION",
    "DEFINITION",
    "MODIFICATION_OR_REPLACEMENT",
    "PROCEDURE_OR_SEQUENCE",
    "CONDITION_OR_TRIGGER",
    "REFERENCE_OR_CROSS_REFERENCE",
]
VALID_ROLES=set(ROLE_ORDER)|{"MIXED","UNCLASSIFIED"}

SIGNAL_FAMILIES={
    "PROHIBITION_MUST_NOT":"PROHIBITION",
    "PROHIBITION_CANNOT":"PROHIBITION",
    "OBLIGATION_MUST":"OBLIGATION",
    "PERMISSION_CAN":"PERMISSION",
    "PERMISSION_MAY":"PERMISSION",
    "DEFINITION_MEANS":"DEFINITION",
    "DEFINITION_KNOWN_AS":"DEFINITION",
    "DEFINITION_REFERRED_TO_AS":"DEFINITION",
    "REPLACEMENT_INSTEAD":"MODIFICATION_OR_REPLACEMENT",
    "MODIFIER_ADD_SUBTRACT":"MODIFICATION_OR_REPLACEMENT",
    "ORDERED_STEP":"PROCEDURE_OR_SEQUENCE",
    "BULLET_LIKE":"PROCEDURE_OR_SEQUENCE",
    "SEQUENCE_BEFORE":"PROCEDURE_OR_SEQUENCE",
    "SEQUENCE_AFTER":"PROCEDURE_OR_SEQUENCE",
    "SEQUENCE_THEN":"PROCEDURE_OR_SEQUENCE",
    "CONDITION_IF":"CONDITION_OR_TRIGGER",
    "TRIGGER_WHEN":"CONDITION_OR_TRIGGER",
    "DURATION_WHILE":"CONDITION_OR_TRIGGER",
    "EXCEPTION_UNLESS":"CONDITION_OR_TRIGGER",
    "REFERENCE_SEE":"REFERENCE_OR_CROSS_REFERENCE",
    "REFERENCE_RULE_REF":"REFERENCE_OR_CROSS_REFERENCE",
    "REFERENCE_PAGE":"REFERENCE_OR_CROSS_REFERENCE",
}

STRONG_FAMILIES=set(ROLE_ORDER)-{"REFERENCE_OR_CROSS_REFERENCE"}

PATTERNS={
    "PROHIBITION_MUST_NOT":re.compile(r"\bmust\s+not\b",re.I),
    "PROHIBITION_CANNOT":re.compile(r"\bcannot\b|\bcan['’]?t\b",re.I),
    "OBLIGATION_MUST":re.compile(r"\bmust\b(?!\s+not\b)",re.I),
    "PERMISSION_CAN":re.compile(r"(?<!cannot\s)\bcan\b",re.I),
    "PERMISSION_MAY":re.compile(r"\bmay\b",re.I),
    "CONDITION_IF":re.compile(r"\bif\b",re.I),
    "TRIGGER_WHEN":re.compile(r"\bwhen\b",re.I),
    "DURATION_WHILE":re.compile(r"\bwhile\b",re.I),
    "EXCEPTION_UNLESS":re.compile(r"\bunless\b",re.I),
    "SEQUENCE_BEFORE":re.compile(r"\bbefore\b",re.I),
    "SEQUENCE_AFTER":re.compile(r"\bafter\b",re.I),
    "SEQUENCE_THEN":re.compile(r"\bthen\b",re.I),
    "DEFINITION_MEANS":re.compile(r"\bmeans\b",re.I),
    "DEFINITION_KNOWN_AS":re.compile(r"\bknown\s+as\b",re.I),
    "DEFINITION_REFERRED_TO_AS":re.compile(r"\breferred\s+to\s+as\b",re.I),
    "REPLACEMENT_INSTEAD":re.compile(r"\binstead\b",re.I),
    "MODIFIER_ADD_SUBTRACT":re.compile(r"\b(?:add|adds|adding|subtract|subtracts|subtracting)\b",re.I),
    "REFERENCE_SEE":re.compile(r"(?:^|[.;:]\s*)see\s+(?:also\s+)?",re.I),
    "REFERENCE_RULE_REF":re.compile(r"\b(?:rule|rules|section|sections)\s+\d{1,2}\.\d{1,2}\b",re.I),
    "REFERENCE_PAGE":re.compile(r"\b(?:page|pg\.?|p\.)\s*\d{1,3}\b",re.I),
}

ORDERED_STEP_RE=re.compile(r"^\s*(?:\d{1,2}[.)]|[A-Z][.)])\s+")
BULLET_LINE_RE=re.compile(r"^\s*(?:[•●▪◦‣⁃*-])\s+")


def load(path:Path)->dict:
    return json.loads(path.read_text(encoding="utf-8"))


def count_signals(raw:str)->Counter:
    counts=Counter()
    for signal,pattern in PATTERNS.items():
        n=len(pattern.findall(raw))
        if n:
            counts[signal]+=n

    lines=raw.splitlines()
    if any(ORDERED_STEP_RE.match(line) for line in lines):
        counts["ORDERED_STEP"]+=sum(1 for line in lines if ORDERED_STEP_RE.match(line))
    bullet_count=sum(1 for line in lines if BULLET_LINE_RE.match(line))
    if bullet_count>=2:
        counts["BULLET_LIKE"]+=bullet_count
    return counts


def family_counts(signals:Counter)->Counter:
    out=Counter()
    for signal,count in signals.items():
        family=SIGNAL_FAMILIES.get(signal)
        if family:
            out[family]+=count
    return out


def choose_role(families:Counter)->tuple[str,str]:
    strong={k:v for k,v in families.items() if k in STRONG_FAMILIES and v>0}
    refs=families.get("REFERENCE_OR_CROSS_REFERENCE",0)

    if len(strong)==1:
        return next(iter(strong)),"HIGH"
    if len(strong)>1:
        return "MIXED","MIXED"
    if refs>0:
        return "REFERENCE_OR_CROSS_REFERENCE","HIGH"
    return "UNCLASSIFIED","NONE"


def classify_paragraph(raw:str)->dict:
    signals=count_signals(raw)
    families=family_counts(signals)
    role,confidence=choose_role(families)
    return {
        "signals":[
            {"id":signal,"count":signals[signal]}
            for signal in sorted(signals)
        ],
        "signal_family_counts":{
            family:families[family]
            for family in ROLE_ORDER
            if families.get(family,0)>0
        },
        "primary_role":role,
        "classification_confidence":confidence,
    }


def build_snapshot(as_of:str,cache_dir:Path,root:Path=ROOT)->dict:
    parent=load(root/PARENT_ATOMS)
    if parent.get("status")!="PASS":
        raise RuntimeError("Parent paragraph atomization snapshot is not PASS")

    ps=parent.get("summary",{})
    required={
        "paragraph_atoms":310,
        "unique_paragraph_keys":310,
        "rules_represented":141,
        "occurrences_represented":146,
        "families_represented":24,
        "range_validation_failures":0,
        "paragraph_hashes_reproduced_from_verified_pdf":310,
    }
    for key,value in required.items():
        if ps.get(key)!=value:
            raise RuntimeError(f"Parent paragraph atomization drift: {key}={ps.get(key)} != {value}")
    if ps.get("all_parent_candidates_atomized") is not True:
        raise RuntimeError("Parent paragraph atomization is incomplete")

    page_texts,page_sha,source,verification=verified_core_pages(cache_dir,root)
    if len(page_texts)!=88:
        raise RuntimeError(f"Verified Core page count drift: {len(page_texts)}")

    parent_source=parent.get("source",{})
    for key in ("document_id","binary_sha256","semantic_sha256","page_count"):
        if parent_source.get(key)!=source.get(key):
            raise RuntimeError(f"Parent/source verification drift for {key}")

    classifications=[]
    role_counts=Counter()
    confidence_counts=Counter()
    signal_counts=Counter()
    repeated_roles=Counter()

    atoms=parent.get("paragraph_atoms",[])
    if len(atoms)!=310:
        raise RuntimeError(f"Parent paragraph atom count drift: {len(atoms)}")

    for atom in atoms:
        page=int(atom["page"])
        start=int(atom["char_start"])
        end=int(atom["char_end"])
        if not 1<=page<=len(page_texts) or start<0 or end<start:
            raise RuntimeError(f"Invalid paragraph range: {atom.get('paragraph_key')}")

        raw=page_texts[page-1][start:end]
        semantic_sha=sha256_text(fingerprint_normalize(raw))
        if semantic_sha!=atom.get("semantic_sha256"):
            raise RuntimeError(f"Paragraph semantic SHA does not reproduce: {atom.get('paragraph_key')}")
        if atom.get("page_semantic_sha256")!=page_sha[page-1]:
            raise RuntimeError(f"Parent page semantic SHA drift: {atom.get('paragraph_key')}")

        result=classify_paragraph(raw)
        if result["primary_role"] not in VALID_ROLES:
            raise RuntimeError(f"Unknown classifier role: {result['primary_role']}")

        row={
            "paragraph_key":atom["paragraph_key"],
            "rule_ref":atom["rule_ref"],
            "rule_key":atom["rule_key"],
            "family_id":atom["family_id"],
            "occurrence_key":atom["occurrence_key"],
            "occurrence_ordinal":atom["occurrence_ordinal"],
            "paragraph_ordinal_in_occurrence":atom["paragraph_ordinal_in_occurrence"],
            "parent_paragraph_classification":atom["classification"],
            "page":page,
            "line_start":int(atom["line_start"]),
            "line_end":int(atom["line_end"]),
            "char_start":start,
            "char_end":end,
            "semantic_sha256":semantic_sha,
            "page_semantic_sha256":page_sha[page-1],
            "signals":result["signals"],
            "signal_family_counts":result["signal_family_counts"],
            "primary_role":result["primary_role"],
            "classification_confidence":result["classification_confidence"],
            "classifier_version":CLASSIFIER_VERSION,
        }
        classifications.append(row)
        role_counts[row["primary_role"]]+=1
        confidence_counts[row["classification_confidence"]]+=1
        for signal in row["signals"]:
            signal_counts[signal["id"]]+=signal["count"]
        if row["parent_paragraph_classification"]=="REPEATED_OCCURRENCE_PARAGRAPH_VARIANT":
            repeated_roles[row["primary_role"]]+=1

    keys=[x["paragraph_key"] for x in classifications]
    complete=(
        len(classifications)==310
        and len(set(keys))==310
        and set(keys)=={x["paragraph_key"] for x in atoms}
        and sum(role_counts.values())==310
        and sum(confidence_counts.values())==310
    )

    return {
        "schema_version":"1.0",
        "status":"PASS" if complete else "FAIL",
        "snapshot_date":as_of,
        "authority":"GAMES_WORKSHOP_OFFICIAL",
        "classifier_version":CLASSIFIER_VERSION,
        "source":source,
        "source_verification":verification,
        "parent_paragraph_atoms":{
            "path":PARENT_ATOMS,
            "atomization_version":parent.get("atomization_version"),
            "paragraph_atoms":ps.get("paragraph_atoms"),
            "unique_paragraph_keys":ps.get("unique_paragraph_keys"),
            "rules_represented":ps.get("rules_represented"),
            "occurrences_represented":ps.get("occurrences_represented"),
            "paragraph_hashes_reproduced_from_verified_pdf":ps.get("paragraph_hashes_reproduced_from_verified_pdf"),
        },
        "classification_contract":{
            "role_vocabulary":ROLE_ORDER+["MIXED","UNCLASSIFIED"],
            "signal_vocabulary":sorted(SIGNAL_FAMILIES),
            "reference_signals_are_weak":True,
            "mixed_is_preferred_over_forced_single_role":True,
            "unclassified_is_allowed":True,
        },
        "classifications":classifications,
        "summary":{
            "paragraphs":len(classifications),
            "unique_paragraph_keys":len(set(keys)),
            "role_counts":dict(sorted(role_counts.items())),
            "confidence_counts":dict(sorted(confidence_counts.items())),
            "signal_occurrence_counts":dict(sorted(signal_counts.items())),
            "paragraphs_with_signals":sum(bool(x["signals"]) for x in classifications),
            "paragraphs_without_signals":sum(not x["signals"] for x in classifications),
            "mixed_paragraphs":role_counts.get("MIXED",0),
            "unclassified_paragraphs":role_counts.get("UNCLASSIFIED",0),
            "repeated_variant_paragraphs":sum(
                x["parent_paragraph_classification"]=="REPEATED_OCCURRENCE_PARAGRAPH_VARIANT"
                for x in classifications
            ),
            "repeated_variant_role_counts":dict(sorted(repeated_roles.items())),
            "paragraph_hashes_reproduced_from_verified_pdf":len(classifications),
        },
        "authority_boundary":{
            "semantic_role_classification_complete":complete,
            "classification_is_lexical_structural_not_full_semantic_ast":True,
            "mixed_and_unclassified_are_valid_fail_closed_states":True,
            "paragraph_prose_committed":False,
            "condition_effect_ast_complete":False,
            "rule_interaction_graph_complete":False,
            "repeated_variant_semantic_equivalence_claimed":False,
            "app_codex_equivalence":"NOT_CLAIMED",
            "full_faction_promotion":False,
            "current_normalized_factions_change":0,
            "copyright_policy":"Stable IDs, role/signal labels, counts, ranges and hashes only; no paragraph prose or matched phrases committed.",
        },
    }


def compact_report(snapshot:dict)->dict:
    return {
        "schema_version":snapshot["schema_version"],
        "status":snapshot["status"],
        "snapshot_date":snapshot["snapshot_date"],
        "authority":snapshot["authority"],
        "classifier_version":snapshot["classifier_version"],
        "source":snapshot["source"],
        "source_verification":snapshot["source_verification"],
        "parent_paragraph_atoms":snapshot["parent_paragraph_atoms"],
        "classification_contract":snapshot["classification_contract"],
        "summary":snapshot["summary"],
        "authority_boundary":snapshot["authority_boundary"],
    }


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--as-of",default="2026-09-30")
    ap.add_argument("--output",type=Path,default=Path("rules/11e/snapshots/2026-09-30/core_rule_paragraph_semantics/index.json"))
    ap.add_argument("--summary-output",type=Path,default=Path("reports/CORE_RULE_PARAGRAPH_SEMANTIC_CLASSIFICATION_CURRENT.json"))
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
            "classifier_version":CLASSIFIER_VERSION,
            "error":str(exc),
            "authority_boundary":{"fail_closed":True,"semantic_classification_promoted":False},
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
