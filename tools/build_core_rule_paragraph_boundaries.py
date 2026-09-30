#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from build_core_rule_reference_atoms import verified_core_pages
from build_core_rules_structure import clean_short_label, fingerprint_normalize, sha256_text

ROOT=Path(__file__).resolve().parents[1]
BOUNDARY_VERSION="CORE_RULE_PARAGRAPH_BOUNDARY_EXTRACTION_V1"
ATOM_SNAPSHOT="rules/11e/snapshots/2026-09-30/core_rule_atoms/index.json"


def load(path:Path)->dict:
    return json.loads(path.read_text(encoding="utf-8"))


def raw_sha(value:str)->str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def token_count(value:str)->int:
    return len(re.findall(r"\S+", value or ""))


def build_line_records(page_text:str)->list[dict]:
    rows=[]
    offset=0
    chunks=page_text.splitlines(keepends=True)
    if not chunks and page_text:
        chunks=[page_text]
    for idx,chunk in enumerate(chunks,1):
        content=chunk.rstrip("\r\n")
        start=offset
        end=start+len(content)
        rows.append({
            "line":idx,
            "text":content,
            "clean":clean_short_label(content),
            "char_start":start,
            "char_end":end,
        })
        offset+=len(chunk)
    return rows


def is_blank(row:dict)->bool:
    return not row.get("clean","").strip()


def trim_selected(selected:list[tuple[int,dict]])->list[tuple[int,dict]]:
    start=0
    end=len(selected)
    while start<end and is_blank(selected[start][1]):
        start+=1
    while end>start and is_blank(selected[end-1][1]):
        end-=1
    return selected[start:end]


def group_page_spans(selected:list[tuple[int,dict]], page_texts:list[str], page_sha:list[str])->list[dict]:
    by_page=defaultdict(list)
    for page,row in selected:
        by_page[page].append(row)
    spans=[]
    for page in sorted(by_page):
        rows=by_page[page]
        start=rows[0]
        end=rows[-1]
        raw=page_texts[page-1][start["char_start"]:end["char_end"]]
        norm=fingerprint_normalize(raw)
        spans.append({
            "page":page,
            "line_start":start["line"],
            "line_end":end["line"],
            "char_start":start["char_start"],
            "char_end":end["char_end"],
            "line_count":len(rows),
            "char_count":len(raw),
            "token_count":token_count(norm),
            "raw_sha256":raw_sha(raw),
            "semantic_sha256":sha256_text(norm),
            "page_semantic_sha256":page_sha[page-1],
        })
    return spans


def paragraph_candidates(selected:list[tuple[int,dict]], page_texts:list[str])->list[dict]:
    by_page=defaultdict(list)
    for page,row in selected:
        by_page[page].append(row)
    out=[]
    for page in sorted(by_page):
        rows=by_page[page]
        group=[]
        groups=[]
        for row in rows:
            if is_blank(row):
                if group:
                    groups.append(group)
                    group=[]
                continue
            group.append(row)
        if group:
            groups.append(group)
        for ordinal,grp in enumerate(groups,1):
            start,end=grp[0],grp[-1]
            raw=page_texts[page-1][start["char_start"]:end["char_end"]]
            norm=fingerprint_normalize(raw)
            if not norm:
                continue
            out.append({
                "page":page,
                "ordinal_on_page":ordinal,
                "line_start":start["line"],
                "line_end":end["line"],
                "char_start":start["char_start"],
                "char_end":end["char_end"],
                "line_count":len(grp),
                "char_count":len(raw),
                "token_count":token_count(norm),
                "semantic_sha256":sha256_text(norm),
            })
    return out


def occurrence_classification(occurrences:list[dict])->str:
    if any(x.get("state")=="HEADING_LINE_RECOVERY_GAP" for x in occurrences):
        return "HEADING_LINE_RECOVERY_GAP"
    if any(x.get("state")=="EMPTY_BODY_BOUNDARY" for x in occurrences):
        return "EMPTY_BODY_BOUNDARY"
    hashes=[x.get("body_semantic_sha256") for x in occurrences]
    if len(occurrences)==1:
        return "SINGLE_OCCURRENCE_BOUNDARY"
    if len(set(hashes))==1:
        return "REPEATED_OCCURRENCE_BOUNDARIES_IDENTICAL_HASH"
    return "REPEATED_OCCURRENCE_BOUNDARIES_VARIANT_HASH"


def resolve_heading_anchors(atoms:list[dict], page_lines:dict[int,list[dict]])->tuple[list[dict],list[dict]]:
    anchors=[]
    gaps=[]
    for atom in atoms:
        for heading in atom.get("heading_labels",[]):
            page=int(heading["page"])
            label=heading["label"]
            matches=[
                row for row in page_lines.get(page,[])
                if row["clean"]==label
            ]
            if len(matches)!=1:
                gaps.append({
                    "rule_ref":atom["rule_ref"],
                    "rule_key":atom["rule_key"],
                    "family_id":atom["family_id"],
                    "page":page,
                    "heading_label_sha256":heading["label_sha256"],
                    "candidate_line_count":len(matches),
                })
                continue
            row=matches[0]
            anchors.append({
                "rule_ref":atom["rule_ref"],
                "rule_key":atom["rule_key"],
                "family_id":atom["family_id"],
                "family_page_start":atom["family_page_start"],
                "family_page_end":atom["family_page_end"],
                "heading_page":page,
                "heading_line":row["line"],
                "heading_char_start":row["char_start"],
                "heading_char_end":row["char_end"],
                "heading_label_sha256":heading["label_sha256"],
            })
    return anchors,gaps


def select_between(
    start_page:int,
    start_line_exclusive:int,
    end_page:int,
    end_line_exclusive:int|None,
    page_lines:dict[int,list[dict]],
)->list[tuple[int,dict]]:
    selected=[]
    for page in range(start_page,end_page+1):
        rows=page_lines.get(page,[])
        for row in rows:
            if page==start_page and row["line"]<=start_line_exclusive:
                continue
            if page==end_page and end_line_exclusive is not None and row["line"]>=end_line_exclusive:
                continue
            selected.append((page,row))
    return trim_selected(selected)


def build_boundary_snapshot(as_of:str, cache_dir:Path, root:Path=ROOT)->dict:
    parent=load(root/ATOM_SNAPSHOT)
    if parent.get("status")!="PASS":
        raise RuntimeError("Parent Core atomization is not PASS")
    ps=parent.get("summary",{})
    if ps.get("atoms")!=141 or ps.get("heading_recovery_gaps")!=0:
        raise RuntimeError("Parent Core atomization baseline is incomplete")

    page_texts,page_sha,source,verification=verified_core_pages(cache_dir,root)
    page_lines={i+1:build_line_records(text) for i,text in enumerate(page_texts)}
    atoms=parent.get("atoms",[])

    anchors,gaps=resolve_heading_anchors(atoms,page_lines)
    by_family=defaultdict(list)
    for anchor in anchors:
        by_family[anchor["family_id"]].append(anchor)
    for fid in by_family:
        by_family[fid].sort(key=lambda x:(x["heading_page"],x["heading_line"],x["rule_ref"]))

    atom_by_ref={x["rule_ref"]:x for x in atoms}
    occurrences_by_ref=defaultdict(list)

    for fid,fanchors in sorted(by_family.items()):
        for idx,anchor in enumerate(fanchors):
            next_anchor=fanchors[idx+1] if idx+1<len(fanchors) else None
            if next_anchor:
                end_page=next_anchor["heading_page"]
                end_line=next_anchor["heading_line"]
                end_boundary={
                    "kind":"NEXT_IN_FAMILY_NUMBERED_HEADING",
                    "rule_ref":next_anchor["rule_ref"],
                    "page":end_page,
                    "line":end_line,
                }
            else:
                end_page=int(anchor["family_page_end"])
                end_line=None
                end_boundary={
                    "kind":"FAMILY_RANGE_END",
                    "page":end_page,
                    "line":None,
                }

            selected=select_between(
                anchor["heading_page"],
                anchor["heading_line"],
                end_page,
                end_line,
                page_lines,
            )
            if not selected:
                occurrence={
                    **anchor,
                    "occurrence_key":f'{anchor["rule_key"]}--p{anchor["heading_page"]}--l{anchor["heading_line"]}',
                    "state":"EMPTY_BODY_BOUNDARY",
                    "end_boundary":end_boundary,
                    "body_spans":[],
                    "paragraph_candidates":[],
                    "body_line_count":0,
                    "body_char_count":0,
                    "body_token_count":0,
                    "body_raw_sha256":None,
                    "body_semantic_sha256":None,
                }
            else:
                raw="\n".join(row["text"] for _,row in selected)
                norm=fingerprint_normalize(raw)
                occurrence={
                    **anchor,
                    "occurrence_key":f'{anchor["rule_key"]}--p{anchor["heading_page"]}--l{anchor["heading_line"]}',
                    "state":"BOUNDARY_RESOLVED",
                    "end_boundary":end_boundary,
                    "body_spans":group_page_spans(selected,page_texts,page_sha),
                    "paragraph_candidates":paragraph_candidates(selected,page_texts),
                    "body_line_count":len(selected),
                    "body_char_count":len(raw),
                    "body_token_count":token_count(norm),
                    "body_raw_sha256":raw_sha(raw),
                    "body_semantic_sha256":sha256_text(norm),
                }
            occurrences_by_ref[anchor["rule_ref"]].append(occurrence)

    # Preserve unresolved headings as atom-level gaps.
    gaps_by_ref=defaultdict(list)
    for gap in gaps:
        gaps_by_ref[gap["rule_ref"]].append(gap)

    rules=[]
    for atom in atoms:
        ref=atom["rule_ref"]
        occ=occurrences_by_ref.get(ref,[])
        if gaps_by_ref.get(ref):
            for gap in gaps_by_ref[ref]:
                occ.append({
                    "occurrence_key":f'{atom["rule_key"]}--unresolved-p{gap["page"]}',
                    "state":"HEADING_LINE_RECOVERY_GAP",
                    "heading_page":gap["page"],
                    "heading_label_sha256":gap["heading_label_sha256"],
                    "candidate_line_count":gap["candidate_line_count"],
                    "body_spans":[],
                    "paragraph_candidates":[],
                    "body_semantic_sha256":None,
                })
        classification=occurrence_classification(occ)
        rules.append({
            "rule_ref":ref,
            "rule_key":atom["rule_key"],
            "family_id":atom["family_id"],
            "classification":classification,
            "parent_atom_classification":atom["classification"],
            "occurrence_count":len(occ),
            "occurrences":occ,
        })

    counts=Counter(x["classification"] for x in rules)
    gap_rules=[x["rule_ref"] for x in rules if x["classification"]=="HEADING_LINE_RECOVERY_GAP"]
    empty_rules=[x["rule_ref"] for x in rules if x["classification"]=="EMPTY_BODY_BOUNDARY"]
    paragraph_total=sum(
        len(occ.get("paragraph_candidates",[]))
        for rule in rules for occ in rule["occurrences"]
    )
    occurrence_total=sum(len(x["occurrences"]) for x in rules)
    complete=(
        len(rules)==141
        and not gap_rules
        and not empty_rules
        and all(x["occurrences"] for x in rules)
        and all(
            occ.get("body_semantic_sha256")
            for rule in rules
            for occ in rule["occurrences"]
            if occ.get("state")=="BOUNDARY_RESOLVED"
        )
    )

    return {
        "schema_version":"1.0",
        "status":"PASS" if complete else "FAIL",
        "snapshot_date":as_of,
        "authority":"GAMES_WORKSHOP_OFFICIAL",
        "boundary_version":BOUNDARY_VERSION,
        "source":source,
        "source_verification":verification,
        "parent_atomization":{
            "path":ATOM_SNAPSHOT,
            "atomization_version":parent.get("atomization_version"),
            "atoms":ps.get("atoms"),
            "families":ps.get("families"),
            "heading_recovery_gaps":ps.get("heading_recovery_gaps"),
        },
        "rules":rules,
        "summary":{
            "rules":len(rules),
            "occurrences":occurrence_total,
            "families":len({x["family_id"] for x in rules}),
            "classification_counts":dict(sorted(counts.items())),
            "heading_line_recovery_gaps":len(gap_rules),
            "heading_line_recovery_gap_refs":gap_rules,
            "empty_body_boundaries":len(empty_rules),
            "empty_body_boundary_refs":empty_rules,
            "paragraph_candidates":paragraph_total,
            "rules_with_multiple_occurrences":sum(len(x["occurrences"])>1 for x in rules),
            "all_rules_have_nonempty_boundaries":not gap_rules and not empty_rules,
        },
        "authority_boundary":{
            "rule_body_boundary_complete":complete,
            "paragraph_boundaries_are_extraction_candidates":True,
            "paragraph_level_rules_ast_complete":False,
            "rule_interaction_graph_complete":False,
            "repeated_occurrence_hash_equality_is_semantic_equivalence":False,
            "app_codex_equivalence":"NOT_CLAIMED",
            "full_faction_promotion":False,
            "current_normalized_factions_change":0,
            "copyright_policy":"Offsets/ranges/counts/hashes only. No paragraph or rule-body prose committed.",
        },
    }


def compact_report(snapshot:dict)->dict:
    special=[
        {
            "rule_ref":x["rule_ref"],
            "family_id":x["family_id"],
            "classification":x["classification"],
            "occurrence_count":x["occurrence_count"],
            "occurrence_hashes":[
                y.get("body_semantic_sha256")
                for y in x["occurrences"]
                if y.get("body_semantic_sha256")
            ],
        }
        for x in snapshot.get("rules",[])
        if x["classification"]!="SINGLE_OCCURRENCE_BOUNDARY"
    ]
    return {
        "schema_version":snapshot["schema_version"],
        "status":snapshot["status"],
        "snapshot_date":snapshot["snapshot_date"],
        "authority":snapshot["authority"],
        "boundary_version":snapshot["boundary_version"],
        "source":snapshot["source"],
        "source_verification":snapshot["source_verification"],
        "parent_atomization":snapshot["parent_atomization"],
        "summary":snapshot["summary"],
        "special_rules":special,
        "authority_boundary":snapshot["authority_boundary"],
    }


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--as-of",default="2026-09-30")
    ap.add_argument("--output",type=Path,default=Path("rules/11e/snapshots/2026-09-30/core_rule_boundaries/index.json"))
    ap.add_argument("--summary-output",type=Path,default=Path("reports/CORE_RULE_PARAGRAPH_BOUNDARIES_CURRENT.json"))
    ap.add_argument("--cache-dir",type=Path,default=ROOT/".cache"/"official-public-rules")
    args=ap.parse_args()

    out=args.output if args.output.is_absolute() else ROOT/args.output
    summary_out=args.summary_output if args.summary_output.is_absolute() else ROOT/args.summary_output

    try:
        snapshot=build_boundary_snapshot(args.as_of,args.cache_dir)
    except Exception as exc:
        failure={
            "schema_version":"1.0",
            "status":"SOURCE_DRIFT",
            "snapshot_date":args.as_of,
            "authority":"GAMES_WORKSHOP_OFFICIAL",
            "boundary_version":BOUNDARY_VERSION,
            "error":str(exc),
            "authority_boundary":{"fail_closed":True,"boundary_layer_promoted":False},
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
