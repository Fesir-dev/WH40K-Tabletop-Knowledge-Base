#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import io
import json
import re
import sys
import unicodedata
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

from build_official_public_semantic_fingerprints import (
    build_sources,
    download,
    normalize_text as official_fingerprint_normalize,
)

ROOT = Path(__file__).resolve().parents[1]
WAHA_BASE = "https://wahapedia.ru/wh40k11ed/"
UA = "WH40K-Tabletop-Knowledge-Base/official-public-mirror-overlap-v1"
NORMALIZATION_VERSION = "OFFICIAL_MIRROR_OVERLAP_NFKC_ALNUM_V1"
MIN_MATCH_CHARS = 40
MIN_MATCH_TOKENS = 6

MIRROR_FILES = [
    "Last_update.csv",
    "Source.csv",
    "Factions.csv",
    "Datasheets.csv",
    "Datasheets_abilities.csv",
    "Datasheets_options.csv",
    "Datasheets_unit_composition.csv",
    "Abilities.csv",
    "Detachment_abilities.csv",
    "Enhancements.csv",
    "Stratagems.csv",
]

PACK_NAME_ALIASES = {
    "adeptus titanicus": "adeptus titanicus forge world",
    "agents of the imperium": "imperial agents",
}

PROMOTABLE_SCOPES = {"DIRECT_SOURCE_SCOPED", "DIRECT_FACTION_SCOPED"}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def overlap_normalize(value: str | None) -> str:
    value = html.unescape(value or "")
    value = re.sub(r"<[^>]+>", " ", value)
    value = unicodedata.normalize("NFKC", value)
    value = value.replace("\u00ad", "")
    for ch in ("\u2010", "\u2011", "\u2012", "\u2013", "\u2014"):
        value = value.replace(ch, "-")
    value = value.casefold()
    value = "".join(ch if ch.isalnum() else " " for ch in value)
    return " ".join(value.split())


def name_norm(value: str | None) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.casefold()
    value = "".join(ch if ch.isalnum() else " " for ch in value)
    return " ".join(value.split())


def resolve_current_wahapedia_root(root: Path = ROOT) -> Path:
    current = load(root / "rules" / "11e" / "current.json")
    pointer = current.get("wave_b_structural", {}).get("snapshot")
    if not pointer:
        raise RuntimeError("rules/11e/current.json has no wave_b_structural.snapshot pointer")
    index_path = root / pointer
    if index_path.name != "index.json" or index_path.parent.name != "roster_views":
        raise RuntimeError(f"Unexpected current Wahapedia pointer: {pointer}")
    wroot = index_path.parent.parent
    if not (wroot / "manifest.json").exists():
        raise RuntimeError(f"Current Wahapedia manifest missing: {wroot}")
    return wroot


def fetch(url: str, timeout: int = 120) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read()


def parse_pipe_csv(raw: bytes) -> list[dict]:
    text = raw.decode("utf-8-sig")
    rows = []
    for source in csv.DictReader(io.StringIO(text), delimiter="|"):
        row = {str(k).strip().lower(): (v or "").strip() for k, v in source.items() if k}
        if any(row.values()):
            rows.append(row)
    return rows


def load_verified_mirror(root: Path = ROOT) -> tuple[dict[str, list[dict]], dict]:
    wroot = resolve_current_wahapedia_root(root)
    manifest = load(wroot / "manifest.json")
    expected = {x["name"]: x for x in manifest.get("files", [])}
    tables: dict[str, list[dict]] = {}
    checks = []
    for filename in MIRROR_FILES:
        if filename not in expected:
            raise RuntimeError(f"Current Wahapedia manifest lacks {filename}")
        raw = fetch(WAHA_BASE + filename)
        actual_sha = sha256_bytes(raw)
        expected_sha = expected[filename]["sha256"]
        if actual_sha != expected_sha:
            raise SourceDrift(
                f"Wahapedia source drift: {filename} {actual_sha} != {expected_sha}"
            )
        tables[filename] = parse_pipe_csv(raw)
        checks.append({
            "file": filename,
            "sha256": actual_sha,
            "rows": len(tables[filename]),
            "verification": "PASS",
        })
    return tables, {
        "snapshot_date": manifest.get("snapshot_date"),
        "last_update": manifest.get("source", {}).get("last_update"),
        "files_verified": len(checks),
        "files": checks,
    }


class SourceDrift(RuntimeError):
    pass


def official_expected_by_id(root: Path = ROOT) -> dict[str, dict]:
    report = load(root / "reports" / "OFFICIAL_PUBLIC_RULES_SEMANTIC_FINGERPRINT_CURRENT.json")
    if report.get("status") != "PASS":
        raise RuntimeError("Official public semantic fingerprint evidence is not PASS")
    return {x["document_id"]: x for x in report.get("documents", [])}


def verified_official_documents(cache_dir: Path, root: Path = ROOT) -> list[dict]:
    try:
        from pypdf import PdfReader
    except Exception as exc:
        raise RuntimeError("pypdf 5.9.0 is required") from exc

    expected_by_id = official_expected_by_id(root)
    docs = []
    cache_dir.mkdir(parents=True, exist_ok=True)

    for source in build_sources():
        expected = expected_by_id.get(source["document_id"])
        if not expected:
            raise RuntimeError(f"Missing committed fingerprint evidence for {source['document_id']}")

        key = hashlib.sha256(source["url"].encode()).hexdigest()[:20]
        pdf_path = cache_dir / f"{key}.pdf"
        if pdf_path.exists():
            raw = pdf_path.read_bytes()
            if sha256_bytes(raw) != expected["binary_sha256"]:
                pdf_path.unlink()
                raw = download(source["url"])
                pdf_path.write_bytes(raw)
        else:
            raw = download(source["url"])
            pdf_path.write_bytes(raw)

        binary_sha = sha256_bytes(raw)
        if binary_sha != expected["binary_sha256"]:
            raise SourceDrift(
                f"Official binary drift: {source['document_id']} {binary_sha} != {expected['binary_sha256']}"
            )

        reader = PdfReader(str(pdf_path))
        page_raw = [(page.extract_text() or "") for page in reader.pages]
        page_fp = [official_fingerprint_normalize(x) for x in page_raw]
        page_fp_sha = [sha256_text(x) for x in page_fp]
        expected_pages = expected.get("pages", [])
        if len(page_raw) != expected.get("page_count") or len(expected_pages) != len(page_raw):
            raise SourceDrift(f"Official page-count drift: {source['document_id']}")
        for idx, digest in enumerate(page_fp_sha):
            if digest != expected_pages[idx].get("semantic_sha256"):
                raise SourceDrift(
                    f"Official page semantic drift: {source['document_id']} page {idx + 1}"
                )
        semantic = "\n\n".join(page_fp)
        if sha256_text(semantic) != expected.get("semantic_sha256"):
            raise SourceDrift(f"Official document semantic drift: {source['document_id']}")

        source_id = None
        prefix = "GW_11E_FACTION_PACK_"
        if source["document_id"].startswith(prefix):
            source_id = source["document_id"][len(prefix):]

        docs.append({
            "document_id": source["document_id"],
            "title": source["title"],
            "document_type": source["document_type"],
            "source_id": source_id,
            "binary_sha256": binary_sha,
            "semantic_sha256": expected["semantic_sha256"],
            "page_count": len(page_raw),
            "page_semantic_sha256": page_fp_sha,
            "page_comparison_text": [overlap_normalize(x) for x in page_raw],
        })
    return docs


def build_pack_mapping(tables: dict[str, list[dict]], official_docs: list[dict]) -> tuple[dict[str, str], dict[str, str]]:
    pack_doc_by_source = {
        x["source_id"]: x["document_id"]
        for x in official_docs
        if x.get("source_id")
    }
    sources = [
        x for x in tables["Source.csv"]
        if str(x.get("edition")) == "11" and x.get("type") == "Faction Pack"
    ]
    source_by_name = {name_norm(x.get("name")): x.get("id") for x in sources}
    faction_pack_source: dict[str, str] = {}
    for faction in tables["Factions.csv"]:
        fid = faction.get("id")
        n = name_norm(faction.get("name"))
        target = PACK_NAME_ALIASES.get(n, n)
        sid = source_by_name.get(target)
        if sid and sid in pack_doc_by_source:
            faction_pack_source[fid] = sid
    return pack_doc_by_source, faction_pack_source


def unit_record(kind: str, key: str, identity: dict, text: str, source_id: str | None = None, faction_id: str | None = None) -> dict | None:
    raw = (text or "").strip()
    if not raw:
        return None
    comp = overlap_normalize(raw)
    tokens = comp.split()
    return {
        "unit_key": key,
        "kind": kind,
        "identity": identity,
        "source_id": source_id,
        "faction_id": faction_id,
        "mirror_text_sha256": sha256_text(raw),
        "comparison_sha256": sha256_text(comp),
        "text_char_count": len(raw),
        "comparison_char_count": len(comp),
        "token_count": len(tokens),
        "_comparison_text": comp,
        "_anchor": " ".join(tokens[:MIN_MATCH_TOKENS]) if len(tokens) >= MIN_MATCH_TOKENS else None,
    }


def build_mirror_units(tables: dict[str, list[dict]]) -> list[dict]:
    datasheets = {x.get("id"): x for x in tables["Datasheets.csv"] if x.get("id")}
    units: list[dict] = []

    def add(row: dict | None):
        if row:
            units.append(row)

    for ds in datasheets.values():
        dsid = ds.get("id")
        common = {
            "datasheet_id": dsid,
            "name": ds.get("name"),
        }
        for field, label in [
            ("loadout", "datasheet-loadout"),
            ("transport", "datasheet-transport"),
            ("damaged_description", "datasheet-damaged-description"),
        ]:
            add(unit_record(
                label,
                f"{label}:{dsid}",
                {**common, "field": field},
                ds.get(field),
                ds.get("source_id"),
                ds.get("faction_id"),
            ))

    for row in tables["Datasheets_abilities.csv"]:
        ds = datasheets.get(row.get("datasheet_id"), {})
        add(unit_record(
            "datasheet-ability",
            f"datasheet-ability:{row.get('datasheet_id')}:{row.get('line')}",
            {
                "datasheet_id": row.get("datasheet_id"),
                "line": row.get("line"),
                "name": row.get("name"),
                "datasheet_name": ds.get("name"),
            },
            row.get("description"),
            ds.get("source_id"),
            ds.get("faction_id"),
        ))

    for row in tables["Datasheets_options.csv"]:
        ds = datasheets.get(row.get("datasheet_id"), {})
        add(unit_record(
            "datasheet-option",
            f"datasheet-option:{row.get('datasheet_id')}:{row.get('line')}",
            {
                "datasheet_id": row.get("datasheet_id"),
                "line": row.get("line"),
                "datasheet_name": ds.get("name"),
            },
            row.get("description"),
            ds.get("source_id"),
            ds.get("faction_id"),
        ))

    for row in tables["Datasheets_unit_composition.csv"]:
        ds = datasheets.get(row.get("datasheet_id"), {})
        add(unit_record(
            "unit-composition",
            f"unit-composition:{row.get('datasheet_id')}:{row.get('line')}",
            {
                "datasheet_id": row.get("datasheet_id"),
                "line": row.get("line"),
                "datasheet_name": ds.get("name"),
            },
            row.get("description"),
            ds.get("source_id"),
            ds.get("faction_id"),
        ))

    for row in tables["Abilities.csv"]:
        add(unit_record(
            "ability",
            f"ability:{row.get('id')}:{row.get('faction_id') or '_'}",
            {"id": row.get("id"), "name": row.get("name"), "faction_id": row.get("faction_id")},
            row.get("description"),
            None,
            row.get("faction_id"),
        ))

    for filename, kind in [
        ("Detachment_abilities.csv", "detachment-ability"),
        ("Enhancements.csv", "enhancement"),
        ("Stratagems.csv", "stratagem"),
    ]:
        for row in tables[filename]:
            add(unit_record(
                kind,
                f"{kind}:{row.get('id')}:{row.get('faction_id') or '_'}",
                {
                    "id": row.get("id"),
                    "name": row.get("name"),
                    "faction_id": row.get("faction_id"),
                    "detachment_id": row.get("detachment_id"),
                    "detachment": row.get("detachment"),
                },
                row.get("description"),
                None,
                row.get("faction_id"),
            ))

    # Identical logical rows can occasionally appear more than once in live export.
    dedup: dict[tuple[str, str], dict] = {}
    for unit in units:
        key = (unit["unit_key"], unit["mirror_text_sha256"])
        dedup[key] = unit
    return sorted(dedup.values(), key=lambda x: (x["kind"], x["unit_key"], x["mirror_text_sha256"]))


def page_candidates(text: str, anchor_index: dict[str, list[int]]) -> set[int]:
    words = text.split()
    candidates: set[int] = set()
    if len(words) < MIN_MATCH_TOKENS:
        return candidates
    for idx in range(len(words) - MIN_MATCH_TOKENS + 1):
        shingle = " ".join(words[idx:idx + MIN_MATCH_TOKENS])
        for unit_idx in anchor_index.get(shingle, ()):
            candidates.add(unit_idx)
    return candidates


def add_hit(hits: dict[int, list[dict]], unit_idx: int, doc: dict, start: int, end: int):
    key = (doc["document_id"], start, end)
    existing = {(x["document_id"], x["page_start"], x["page_end"]) for x in hits[unit_idx]}
    if key in existing:
        return
    pages = doc["page_semantic_sha256"][start - 1:end]
    hits[unit_idx].append({
        "document_id": doc["document_id"],
        "document_type": doc["document_type"],
        "source_id": doc.get("source_id"),
        "page_start": start,
        "page_end": end,
        "page_semantic_sha256": pages,
        "document_binary_sha256": doc["binary_sha256"],
    })


def find_exact_hits(units: list[dict], official_docs: list[dict]) -> dict[int, list[dict]]:
    anchor_index: dict[str, list[int]] = defaultdict(list)
    for idx, unit in enumerate(units):
        if unit["comparison_char_count"] < MIN_MATCH_CHARS or not unit["_anchor"]:
            continue
        anchor_index[unit["_anchor"]].append(idx)

    hits: dict[int, list[dict]] = defaultdict(list)

    # First prefer exact containment within a single official page.
    for doc in official_docs:
        for page_no, page_text in enumerate(doc["page_comparison_text"], 1):
            for unit_idx in page_candidates(page_text, anchor_index):
                unit = units[unit_idx]
                if unit["_comparison_text"] in page_text:
                    add_hit(hits, unit_idx, doc, page_no, page_no)

    # Then allow an exact unit split by a PDF page boundary, but only for units
    # that did not match inside any single page.
    unmatched = {idx for idx, unit in enumerate(units) if unit["_anchor"] and not hits.get(idx)}
    if unmatched:
        pair_index: dict[str, list[int]] = defaultdict(list)
        for idx in unmatched:
            pair_index[units[idx]["_anchor"]].append(idx)
        for doc in official_docs:
            pages = doc["page_comparison_text"]
            for page_idx in range(len(pages) - 1):
                pair = (pages[page_idx] + " " + pages[page_idx + 1]).strip()
                for unit_idx in page_candidates(pair, pair_index):
                    if units[unit_idx]["_comparison_text"] in pair:
                        add_hit(hits, unit_idx, doc, page_idx + 1, page_idx + 2)

    return hits


def classify_provenance(unit: dict, unit_hits: list[dict], pack_doc_by_source: dict[str, str], faction_pack_source: dict[str, str]) -> tuple[str, list[dict]]:
    direct_source = unit.get("source_id")
    if direct_source and direct_source in pack_doc_by_source:
        expected_doc = pack_doc_by_source[direct_source]
        scoped = [x for x in unit_hits if x["document_id"] == expected_doc]
        if scoped:
            return "DIRECT_SOURCE_SCOPED", scoped

    faction_id = unit.get("faction_id")
    faction_source = faction_pack_source.get(faction_id)
    if faction_source and faction_source in pack_doc_by_source:
        expected_doc = pack_doc_by_source[faction_source]
        scoped = [x for x in unit_hits if x["document_id"] == expected_doc]
        if scoped:
            return "DIRECT_FACTION_SCOPED", scoped

    if any(x["document_type"] == "CORE_RULES" for x in unit_hits):
        return "CORE_PUBLIC_TEXT_ONLY", [x for x in unit_hits if x["document_type"] == "CORE_RULES"]

    return "GLOBAL_PUBLIC_TEXT_ONLY", unit_hits


def public_match_classification(unit_hits: list[dict]) -> str:
    docs = {x["document_id"] for x in unit_hits}
    return "EXACT_NORMALIZED_TEXT_MATCH_MULTI_OFFICIAL" if len(docs) > 1 else "EXACT_NORMALIZED_TEXT_MATCH"


def build_outputs(as_of: str, cache_dir: Path, root: Path = ROOT) -> tuple[dict, dict]:
    tables, mirror_state = load_verified_mirror(root)
    official_docs = verified_official_documents(cache_dir, root)
    if len(official_docs) != 29:
        raise RuntimeError(f"Expected 29 official public documents, got {len(official_docs)}")

    pack_doc_by_source, faction_pack_source = build_pack_mapping(tables, official_docs)
    units = build_mirror_units(tables)
    hits = find_exact_hits(units, official_docs)

    by_kind: dict[str, Counter] = defaultdict(Counter)
    document_stats: dict[str, dict] = {
        doc["document_id"]: {
            "document_id": doc["document_id"],
            "title": doc["title"],
            "document_type": doc["document_type"],
            "source_id": doc.get("source_id"),
            "binary_sha256": doc["binary_sha256"],
            "semantic_sha256": doc["semantic_sha256"],
            "pages": doc["page_count"],
            "pages_with_overlap": set(),
            "exact_units": 0,
            "promotable_units": 0,
        }
        for doc in official_docs
    }

    matches = []
    normalized_units = []
    exact_count = promotable_count = unscoped_count = no_exact_count = 0

    for idx, unit in enumerate(units):
        kind_counter = by_kind[unit["kind"]]
        kind_counter["mirror_units"] += 1
        unit_hits = sorted(
            hits.get(idx, []),
            key=lambda x: (x["document_id"], x["page_start"], x["page_end"]),
        )
        if not unit_hits:
            no_exact_count += 1
            kind_counter["no_exact_public_overlap"] += 1
            if unit["comparison_char_count"] < MIN_MATCH_CHARS or unit["token_count"] < MIN_MATCH_TOKENS:
                kind_counter["too_short_for_safe_auto_match"] += 1
            continue

        exact_count += 1
        kind_counter["exact_public_overlap"] += 1
        classification = public_match_classification(unit_hits)
        provenance_scope, scoped_hits = classify_provenance(
            unit, unit_hits, pack_doc_by_source, faction_pack_source
        )
        promotable = provenance_scope in PROMOTABLE_SCOPES
        if promotable:
            promotable_count += 1
            kind_counter["promotable_scoped"] += 1
        else:
            unscoped_count += 1
            kind_counter["unscoped_exact"] += 1

        for hit in unit_hits:
            stats = document_stats[hit["document_id"]]
            stats["exact_units"] += 1
            stats["pages_with_overlap"].update(range(hit["page_start"], hit["page_end"] + 1))
        if promotable:
            for hit in scoped_hits:
                document_stats[hit["document_id"]]["promotable_units"] += 1

        public = {
            "unit_key": unit["unit_key"],
            "kind": unit["kind"],
            "identity": unit["identity"],
            "classification": classification,
            "provenance_scope": provenance_scope,
            "promotion_eligible": promotable,
            "mirror_text_sha256": unit["mirror_text_sha256"],
            "comparison_sha256": unit["comparison_sha256"],
            "text_char_count": unit["text_char_count"],
            "comparison_char_count": unit["comparison_char_count"],
            "token_count": unit["token_count"],
            "mirror_source_id": unit.get("source_id"),
            "mirror_faction_id": unit.get("faction_id"),
            "official_evidence": unit_hits,
        }
        matches.append(public)

        if promotable:
            normalized_units.append({
                "unit_key": unit["unit_key"],
                "kind": unit["kind"],
                "identity": unit["identity"],
                "classification": classification,
                "provenance_scope": provenance_scope,
                "mirror_text_sha256": unit["mirror_text_sha256"],
                "comparison_sha256": unit["comparison_sha256"],
                "mirror_source_id": unit.get("source_id"),
                "mirror_faction_id": unit.get("faction_id"),
                "official_evidence": scoped_hits,
            })

    doc_rows = []
    for doc in official_docs:
        row = document_stats[doc["document_id"]]
        row["pages_with_overlap"] = len(row["pages_with_overlap"])
        doc_rows.append(row)

    by_kind_json = {key: dict(sorted(value.items())) for key, value in sorted(by_kind.items())}
    summary = {
        "official_documents": len(official_docs),
        "core_rules": sum(x["document_type"] == "CORE_RULES" for x in official_docs),
        "faction_packs": sum(x["document_type"] == "FACTION_PACK" for x in official_docs),
        "mirror_units": len(units),
        "exact_public_overlap_units": exact_count,
        "promotable_scoped_units": promotable_count,
        "unscoped_exact_units": unscoped_count,
        "no_exact_overlap_units": no_exact_count,
        "official_pages": sum(x["page_count"] for x in official_docs),
        "official_pages_with_overlap": sum(x["pages_with_overlap"] for x in doc_rows),
    }

    report = {
        "schema_version": "1.0",
        "status": "PASS",
        "as_of": as_of,
        "milestone": "OFFICIAL_PUBLIC_RULES_MIRROR_OVERLAP_AUDIT",
        "authority_boundary": {
            "normative_authority": "GAMES_WORKSHOP",
            "current_mirror": "WAHAPEDIA_11E",
            "full_codex_app_equivalence_claimed": False,
            "faction_pack_is_full_codex_replacement": False,
            "app_only_wording_inferred": False,
            "current_normalized_factions_promoted_by_this_audit": False,
        },
        "source_state": {
            "official_public": {
                "verification": "PASS",
                "documents_verified": len(official_docs),
                "fingerprint_report": "reports/OFFICIAL_PUBLIC_RULES_SEMANTIC_FINGERPRINT_CURRENT.json",
            },
            "current_mirror": {
                "verification": "PASS",
                **mirror_state,
            },
        },
        "comparison_contract": {
            "normalization_version": NORMALIZATION_VERSION,
            "minimum_match_characters": MIN_MATCH_CHARS,
            "minimum_match_tokens": MIN_MATCH_TOKENS,
            "eligible_exact_classifications": [
                "EXACT_NORMALIZED_TEXT_MATCH",
                "EXACT_NORMALIZED_TEXT_MATCH_MULTI_OFFICIAL",
            ],
            "promotable_provenance_scopes": sorted(PROMOTABLE_SCOPES),
            "copyright_policy": "No long official or mirror rules prose is committed; only identities, hashes, counts and page evidence.",
            "no_exact_match_semantics": "NO_EXACT_PUBLIC_OVERLAP is not automatically a conflict; Codex/app-only or extraction-scope differences remain possible.",
        },
        "summary": summary,
        "by_kind": by_kind_json,
        "documents": doc_rows,
        "matches": matches,
        "promotion_policy": {
            "structured_snapshot": f"rules/11e/snapshots/{as_of}/official_public_overlap/index.json",
            "exact_match_required": True,
            "direct_scope_required": True,
            "full_faction_promotion": False,
            "core_rules_full_ast_claimed": False,
            "app_codex_equivalence": "PENDING",
        },
    }

    norm_by_kind = Counter(x["kind"] for x in normalized_units)
    norm_by_doc = Counter(
        evidence["document_id"]
        for unit in normalized_units
        for evidence in unit["official_evidence"]
    )
    snapshot = {
        "schema_version": "1.0",
        "status": "PASS",
        "snapshot_date": as_of,
        "authority": "GAMES_WORKSHOP_OFFICIAL_PUBLIC_OVERLAP",
        "scope": "EXACT_PUBLIC_OVERLAP_ONLY",
        "source_report": "reports/OFFICIAL_PUBLIC_MIRROR_OVERLAP_CURRENT.json",
        "source_fingerprint_report": "reports/OFFICIAL_PUBLIC_RULES_SEMANTIC_FINGERPRINT_CURRENT.json",
        "current_mirror_snapshot": str(resolve_current_wahapedia_root(root).relative_to(root)),
        "comparison_normalization": NORMALIZATION_VERSION,
        "units": normalized_units,
        "summary": {
            "units": len(normalized_units),
            "by_kind": dict(sorted(norm_by_kind.items())),
            "official_evidence_refs_by_document": dict(sorted(norm_by_doc.items())),
        },
        "authority_boundary": {
            "scope": "Only exact source/faction-scoped semantic units independently present in public GW material.",
            "full_codex_app_equivalence": "NOT_CLAIMED",
            "full_faction_current_verified": False,
            "current_normalized_factions_change": 0,
            "unmatched_mirror_semantics": "NOT_PROMOTED_NOT_ASSUMED_WRONG",
            "core_rules_full_structured_normalization": "PENDING",
        },
    }
    return report, snapshot


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--as-of", default="2026-09-30")
    ap.add_argument("--report-output", type=Path, default=Path("reports/OFFICIAL_PUBLIC_MIRROR_OVERLAP_CURRENT.json"))
    ap.add_argument("--snapshot-output", type=Path)
    ap.add_argument("--cache-dir", type=Path, default=ROOT / ".cache" / "official-public-rules")
    args = ap.parse_args()

    snapshot_output = args.snapshot_output or Path(
        f"rules/11e/snapshots/{args.as_of}/official_public_overlap/index.json"
    )
    report_path = args.report_output if args.report_output.is_absolute() else ROOT / args.report_output
    snapshot_path = snapshot_output if snapshot_output.is_absolute() else ROOT / snapshot_output

    try:
        report, snapshot = build_outputs(args.as_of, args.cache_dir)
    except SourceDrift as exc:
        failure = {
            "schema_version": "1.0",
            "status": "SOURCE_DRIFT",
            "as_of": args.as_of,
            "milestone": "OFFICIAL_PUBLIC_RULES_MIRROR_OVERLAP_AUDIT",
            "error": str(exc),
            "promotion_policy": {"structured_snapshot_generated": False, "fail_closed": True},
        }
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(failure, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(failure, ensure_ascii=False))
        return 2

    report_path.parent.mkdir(parents=True, exist_ok=True)
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    snapshot_path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "summary": report["summary"], "snapshot_units": snapshot["summary"]["units"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
