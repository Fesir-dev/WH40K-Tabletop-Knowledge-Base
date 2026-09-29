#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

SEMANTIC_DIMS=[
    "datasheets",
    "wargear_constraints",
    "keywords",
    "detachments",
    "enhancements",
    "stratagems",
    "faq_errata",
]

ALIAS_CANDIDATES={
    "aeldari_craftworlds":"Aeldari",
    "adeptus_titanicus":"Adeptus Titanicus (Forge World)",
    "agents_of_the_imperium":"Imperial Agents",
}


def load(path:Path):
    return json.loads(path.read_text(encoding="utf-8"))


def norm(value:str|None)->str:
    value=unicodedata.normalize("NFKD",value or "")
    value="".join(ch for ch in value if not unicodedata.combining(ch))
    return " ".join(re.sub(r"[^a-z0-9]+"," ",value.casefold()).split())


def source_by_id(registry:dict, source_id:str)->dict:
    hits=[x for x in registry.get("sources",[]) if x.get("id")==source_id]
    if len(hits)!=1:
        raise RuntimeError(f"Expected one registry source for {source_id}, got {len(hits)}")
    return hits[0]


def gate_by_id(gate:dict, source_id:str)->dict:
    hits=[x for x in gate.get("required_checks",[]) if x.get("id")==source_id]
    if len(hits)!=1:
        raise RuntimeError(f"Expected one currentness gate row for {source_id}, got {len(hits)}")
    return hits[0]


def build_audit(root:Path=ROOT)->dict:
    current=load(root/"rules/11e/current.json")
    coverage=load(root/"coverage/current.json")
    gate=load(root/"sources/currentness_gate.json")
    registry=load(root/"sources/registry.json")
    catalog=load(root/"factions/catalog.json")
    source_catalog=load(root/"rules/11e/snapshots/2026-09-29/wahapedia/source_catalog.json")
    official_assets=load(root/"sources/snapshots/gw_11e_official_assets_2026-09-29.json")
    semantic_audit=load(root/"reports/WAVE_B_SEMANTIC_FINGERPRINT_AUDIT_2026-09-29.json")
    discovery=load(root/"sources/discoveries/gw_public_rules_surface_2026-09-29.json")

    factions=catalog["factions"]
    cov_rows=coverage["factions"]
    cov_by_slug={x["slug"]:x for x in cov_rows}

    mfm_dims=list(current["wave_a_mfm"]["dimensions"])
    mfm_complete={
        dim:sum(1 for row in cov_rows if row.get("coverage",{}).get(dim)==100)
        for dim in mfm_dims
    }
    semantic_complete={
        dim:sum(1 for row in cov_rows if row.get("coverage",{}).get(dim)==100)
        for dim in SEMANTIC_DIMS
    }
    semantic_zero={
        dim:sum(1 for row in cov_rows if row.get("coverage",{}).get(dim)==0)
        for dim in SEMANTIC_DIMS
    }

    packs=[
        x for x in source_catalog
        if str(x.get("edition"))=="11" and x.get("type")=="Faction Pack"
    ]
    pack_by_norm={norm(x.get("name")):x for x in packs}
    faction_by_slug={x["slug"]:x for x in factions}

    mapping_rows=[]
    for faction in factions:
        slug=faction["slug"]
        direct=pack_by_norm.get(norm(faction.get("name")))
        alias_name=ALIAS_CANDIDATES.get(slug)
        alias=pack_by_norm.get(norm(alias_name)) if alias_name else None
        parent=faction_by_slug.get(faction.get("parent_slug")) if faction.get("parent_slug") else None
        parent_pack=pack_by_norm.get(norm(parent.get("name"))) if parent else None

        if direct:
            state="DIRECT_NAME_MATCH"
            candidate=direct["name"]
        elif alias:
            state="NAMING_ALIAS_CANDIDATE"
            candidate=alias["name"]
        elif parent_pack:
            state="PARENT_SOURCE_CANDIDATE"
            candidate=parent_pack["name"]
        else:
            state="NO_PUBLIC_FACTION_PACK_MAPPING"
            candidate=None

        cov=cov_by_slug[slug]
        mapping_rows.append({
            "slug":slug,
            "name":faction.get("name"),
            "roster_kind":faction.get("roster_kind"),
            "parent_slug":faction.get("parent_slug"),
            "mapping_state":state,
            "candidate_official_pack":candidate,
            "structural_current":bool(cov.get("structural_current")),
            "secondary_semantic_current":cov.get("semantic_current_mirror",{}).get("state")=="FULL_FINGERPRINT_MATCH",
            "normative_equivalence_verified":bool(cov.get("semantic_current_mirror",{}).get("normative_equivalence_verified")),
            "current_normalized":bool(cov.get("current_normalized")),
        })

    mapping_counts=Counter(x["mapping_state"] for x in mapping_rows)

    gw_app=source_by_id(registry,"GW_40K_APP")
    gw_downloads=source_by_id(registry,"GW_40K_DOWNLOADS")
    gw_mfm=source_by_id(registry,"GW_MFM")
    app_gate=gate_by_id(gate,"GW_40K_APP")
    downloads_gate=gate_by_id(gate,"GW_40K_DOWNLOADS")
    mfm_gate=gate_by_id(gate,"GW_MFM")

    discovery_by_id={x["id"]:x for x in discovery.get("findings",[])}
    core_public=discovery_by_id["GW_11E_CORE_RULES_PUBLIC"]
    pack_scope=discovery_by_id["GW_FACTION_PACK_SCOPE"]

    off=official_assets["official_assets"]
    sem_expected=int(semantic_audit.get("expected_fingerprints",0))
    sem_match=int(semantic_audit.get("counts",{}).get("MATCH",0))

    closed_layers=[
        {
            "id":"MFM_NORMATIVE_DIMENSIONS",
            "state":"CLOSED_CURRENT_NORMATIVE",
            "authority":"GW_MFM",
            "evidence":{
                "version":current["wave_a_mfm"]["version"],
                "last_updated":current["wave_a_mfm"]["last_updated"],
                "dimensions":mfm_dims,
                "complete_roster_identities_by_dimension":mfm_complete,
                "gate_state":mfm_gate.get("state"),
            },
        },
        {
            "id":"OFFICIAL_FACTION_ASSET_PROVENANCE",
            "state":"CLOSED_ASSET_LEVEL",
            "authority":"GW_40K_DOWNLOADS",
            "evidence":{
                "edition_11_sources":off.get("edition_11_sources"),
                "faction_pack_pdf_assets":off.get("pdf_assets"),
                "verified_pdf_assets":off.get("verified_pdf_assets"),
                "failures":off.get("failures"),
                "source_catalog_drift":official_assets.get("live_source_csv",{}).get("catalog_drift_count"),
            },
        },
        {
            "id":"SECONDARY_MIRROR_SEMANTIC_CURRENTNESS",
            "state":"CLOSED_SECONDARY_ONLY",
            "authority":"WAHAPEDIA_11E",
            "evidence":{
                "expected_fingerprints":sem_expected,
                "matched_fingerprints":sem_match,
                "problems":len(semantic_audit.get("problems",[])),
                "current_mirror_roster_identities":coverage["global"].get("wave_b_current_mirror_semantic_roster_identities"),
                "normative_equivalence_claimed":False,
            },
        },
    ]

    gaps=[
        {
            "id":"OFFICIAL_CORE_RULES_SEMANTIC_INGESTION",
            "state":"CLOSABLE_WITH_CURRENT_PUBLIC_SOURCE",
            "blocking_scope":["core_rules_content","system_normative_semantics"],
            "evidence":{
                "repository_state":current["source_currentness"]["core_rules_content"]["state"],
                "currentness_profile":gate["scope_profiles"]["core_rules"],
                "official_public_source":core_public,
                "downloads_source_health":gw_downloads.get("status"),
                "downloads_gate_state":downloads_gate.get("state"),
            },
            "next_action":"Register the 2026-06-01 official 11E Core Rules asset and build copyright-safe official semantic fingerprints/structured extraction.",
        },
        {
            "id":"PUBLIC_FACTION_SUPPLEMENT_SEMANTIC_INGESTION",
            "state":"CLOSABLE_WITH_CURRENT_PUBLIC_SOURCES",
            "blocking_scope":["public_faction_supplements","faq_errata","public_extra_datasheets","public_extra_detachments"],
            "evidence":{
                "verified_public_faction_pack_pdfs":off.get("verified_pdf_assets"),
                "official_scope":pack_scope,
                "faq_errata_normative_complete":semantic_complete["faq_errata"],
            },
            "next_action":"Fingerprint and structurally extract the public official faction-pack supplement/FAQ semantics without treating them as complete Codex replacements.",
        },
        {
            "id":"FULL_FACTION_CODEX_APP_SEMANTICS",
            "state":"BLOCKED_OR_CONDITIONAL_ON_AUTHORIZED_CODEX_APP_EVIDENCE",
            "blocking_scope":["full_normative_faction","datasheets","wargear_constraints","keywords","detachments","enhancements","stratagems"],
            "evidence":{
                "faction_rules_profile":gate["scope_profiles"]["faction_rules"],
                "app_profile":gate["scope_profiles"]["app_wording"],
                "public_faction_pack_scope":"SUPPLEMENTS_CODEX_NOT_FULL_CODEX",
                "gw_app_status":gw_app.get("status"),
                "gw_app_repository_coverage_state":gw_app.get("repository_coverage_state"),
                "gw_app_gate_state":app_gate.get("state"),
            },
            "next_action":"Do not infer missing Codex/app-only text from Wahapedia, BSData or New Recruit. Close per-faction only when official public content is complete or authorized app/Codex evidence is captured.",
        },
        {
            "id":"MIRROR_TO_OFFICIAL_SEMANTIC_EQUIVALENCE",
            "state":"PARTIALLY_CLOSABLE_PUBLIC_OVERLAP_ONLY",
            "blocking_scope":["normative_semantic_equivalence","full_normative_faction"],
            "evidence":{
                "secondary_mirror_fingerprints_expected":sem_expected,
                "secondary_mirror_fingerprints_matched":sem_match,
                "factions_with_normative_equivalence_verified":sum(
                    1 for row in cov_rows
                    if row.get("semantic_current_mirror",{}).get("normative_equivalence_verified") is True
                ),
                "public_official_faction_packs":len(packs),
            },
            "next_action":"Compare only overlapping public official Core/Faction Pack semantics against the mirror. Never generalize overlap matches into full-faction equivalence where Codex/app-only text is absent.",
        },
        {
            "id":"GW_APP_WORDING_AND_LOCKED_DATASHEET_CROSSCHECK",
            "state":"BLOCKED_ON_AUTHORIZED_APP_EVIDENCE",
            "blocking_scope":["app_wording","app_locked_datasheet_crosscheck"],
            "evidence":{
                "source_status":gw_app.get("status"),
                "checked_at":gw_app.get("checked_at"),
                "repository_coverage_state":gw_app.get("repository_coverage_state"),
                "gate_state":app_gate.get("state"),
                "required_for":app_gate.get("required_for"),
                "official_role_discovered":True,
            },
            "next_action":"Keep PENDING until authorized, versioned app evidence can be captured. Do not assign a polling cadence or infer app-only wording.",
        },
        {
            "id":"OFFICIAL_SOURCE_TO_ROSTER_IDENTITY_MAPPING",
            "state":"CLOSABLE_WITH_METADATA_AND_CONTENT_REVIEW",
            "blocking_scope":["per_roster_normative_provenance"],
            "evidence":{
                "roster_identities":len(mapping_rows),
                "direct_name_matches":mapping_counts["DIRECT_NAME_MATCH"],
                "naming_alias_candidates":mapping_counts["NAMING_ALIAS_CANDIDATE"],
                "parent_source_candidates":mapping_counts["PARENT_SOURCE_CANDIDATE"],
                "no_public_faction_pack_mapping":mapping_counts["NO_PUBLIC_FACTION_PACK_MAPPING"],
                "candidate_rows":[
                    x for x in mapping_rows
                    if x["mapping_state"]!="DIRECT_NAME_MATCH"
                ],
            },
            "next_action":"Create an explicit reviewed source-to-roster mapping contract. Alias/parent mappings are candidates only until official content scope confirms them.",
        },
        {
            "id":"NORMATIVE_COVERAGE_ACCOUNTING",
            "state":"INTENTIONAL_ZERO_NOT_MIRROR_DATA_LOSS",
            "blocking_scope":["current_normalized_factions","full_normative_semantic_factions"],
            "evidence":{
                "current_normalized_factions":coverage["global"].get("current_normalized_factions"),
                "full_normative_semantic_factions":coverage["global"].get("full_normative_semantic_factions"),
                "secondary_semantic_roster_identities":coverage["global"].get("wave_b_current_mirror_semantic_roster_identities"),
                "semantic_dimensions_complete":semantic_complete,
                "semantic_dimensions_zero":semantic_zero,
            },
            "next_action":"Preserve separate normative and secondary-mirror coverage. Do not convert mirror completeness into normative coverage percentages.",
        },
    ]

    return {
        "schema_version":"1.0",
        "status":"PASS",
        "as_of":"2026-09-29",
        "milestone":"NORMATIVE_APP_EQUIVALENCE_GAP_AUDIT",
        "authority_boundary":{
            "normative_authority":"GAMES_WORKSHOP",
            "secondary_mirror":"WAHAPEDIA_11E",
            "structured_implementation":"BSDATA_WH40K_11E",
            "runtime_projection":"NEW_RECRUIT_RUNTIME",
            "mirror_hash_match_is_normative_equivalence":False,
            "faction_pack_is_full_codex_replacement":False,
            "app_wording_inference_allowed":False,
        },
        "coverage_summary":{
            "roster_universe":coverage["global"].get("catalogued_roster_universe"),
            "current_normalized_factions":coverage["global"].get("current_normalized_factions"),
            "full_normative_semantic_factions":coverage["global"].get("full_normative_semantic_factions"),
            "secondary_semantic_current_roster_identities":coverage["global"].get("wave_b_current_mirror_semantic_roster_identities"),
            "mfm_dimensions":mfm_dims,
            "mfm_complete_roster_identities_by_dimension":mfm_complete,
            "normative_semantic_dimensions":SEMANTIC_DIMS,
            "normative_semantic_complete_by_dimension":semantic_complete,
            "normative_semantic_zero_by_dimension":semantic_zero,
        },
        "official_public_surface":{
            "core_rules_public_source_discovered":core_public.get("state")=="PUBLIC_OFFICIAL_SOURCE_DISCOVERED_NOT_INGESTED",
            "core_rules_asset_url":core_public.get("asset_url"),
            "edition_11_source_catalog_rows":off.get("edition_11_sources"),
            "verified_public_faction_pack_pdfs":off.get("verified_pdf_assets"),
            "faction_pack_scope":"SUPPLEMENTAL_NOT_FULL_CODEX",
            "gw_app_role_confirmed":True,
            "gw_app_repository_ingested":gw_app.get("repository_coverage_state")!="NOT_INGESTED",
        },
        "roster_source_mapping":{
            "counts":dict(sorted(mapping_counts.items())),
            "rows":mapping_rows,
            "policy":"Direct/alias/parent rows are provenance candidates only. No candidate mapping grants normative semantic equivalence without official content-scope review.",
        },
        "closed_layers":closed_layers,
        "gaps":gaps,
        "conclusion":{
            "why_current_normalized_factions_is_zero":"The repository has strong current MFM and secondary-mirror coverage, but it intentionally requires official normative semantic completeness. Public faction packs are supplemental to Codex content, mirror hashes prove mirror currentness only, and app/Codex-only wording is not ingested.",
            "publicly_closable_now":[
                "OFFICIAL_CORE_RULES_SEMANTIC_INGESTION",
                "PUBLIC_FACTION_SUPPLEMENT_SEMANTIC_INGESTION",
                "public-overlap portion of MIRROR_TO_OFFICIAL_SEMANTIC_EQUIVALENCE",
                "OFFICIAL_SOURCE_TO_ROSTER_IDENTITY_MAPPING",
            ],
            "must_remain_pending_without_new_authorized_evidence":[
                "GW_APP_WORDING_AND_LOCKED_DATASHEET_CROSSCHECK",
                "Codex/app-only portion of FULL_FACTION_CODEX_APP_SEMANTICS",
            ],
            "recommended_next_milestone":"OFFICIAL_PUBLIC_RULES_SEMANTIC_FINGERPRINT_PIPELINE",
            "expected_effect":"Close Core Rules plus public faction supplement/FAQ official semantics and establish official-vs-mirror overlap fingerprints. This should improve normative scoped coverage but must not automatically promote full-faction normalization.",
        },
    }


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",type=Path)
    args=ap.parse_args()
    report=build_audit()
    payload=json.dumps(report,ensure_ascii=False,indent=2)+"\n"
    if args.output:
        out=args.output if args.output.is_absolute() else ROOT/args.output
        out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(payload,encoding="utf-8")
    else:
        print(payload,end="")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
