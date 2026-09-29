#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import time
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

BASE_URL = "https://wahapedia.ru/wh40k11ed/"
FILES = [
    "Last_update.csv", "Source.csv", "Factions.csv", "Datasheets.csv",
    "Datasheets_models.csv", "Datasheets_models_cost.csv", "Datasheets_keywords.csv",
    "Datasheets_wargear.csv", "Datasheets_options.csv", "Datasheets_unit_composition.csv",
    "Abilities.csv", "Datasheets_abilities.csv", "Datasheets_leader.csv", "Detachments.csv",
    "Stratagems.csv", "Datasheets_stratagems.csv", "Enhancements.csv",
    "Datasheets_enhancements.csv", "Detachment_abilities.csv",
    "Datasheets_detachment_abilities.csv",
]
REQUIRED_HEADERS = {
    "Factions.csv": {"id", "name", "link"},
    "Source.csv": {"id", "name", "type", "edition"},
    "Datasheets.csv": {"id", "name", "faction_id", "source_id", "role", "link"},
    "Datasheets_models.csv": {"datasheet_id", "name", "m", "t", "sv", "w", "ld", "oc"},
    "Datasheets_keywords.csv": {"datasheet_id", "keyword", "is_faction_keyword"},
    "Datasheets_wargear.csv": {"datasheet_id", "name", "range", "type", "a", "bs_ws", "s", "ap", "d"},
    "Datasheets_abilities.csv": {"datasheet_id", "name", "description"},
    "Stratagems.csv": {"id", "faction_id", "name", "description"},
    "Enhancements.csv": {"id", "faction_id", "name", "description"},
    "Detachment_abilities.csv": {"id", "faction_id", "detachment", "name", "description"},
}

ALIASES = {
    "Aeldari": "aeldari_craftworlds",
    "Drukhari": "drukhari",
    "Chaos Daemons": "chaos_daemons",
    "Chaos Knights": "chaos_knights",
    "Chaos Space Marines": "chaos_space_marines",
    "Death Guard": "death_guard",
    "Emperor’s Children": "emperors_children",
    "Emperor's Children": "emperors_children",
    "Thousand Sons": "thousand_sons",
    "World Eaters": "world_eaters",
    "Genestealer Cults": "genestealer_cults",
    "Adepta Sororitas": "adepta_sororitas",
    "Adeptus Custodes": "adeptus_custodes",
    "Adeptus Mechanicus": "adeptus_mechanicus",
    "Imperial Agents": "agents_of_the_imperium",
    "Agents of the Imperium": "agents_of_the_imperium",
    "Astra Militarum": "astra_militarum",
    "Black Templars": "black_templars",
    "Blood Angels": "blood_angels",
    "Dark Angels": "dark_angels",
    "Deathwatch": "deathwatch",
    "Grey Knights": "grey_knights",
    "Imperial Knights": "imperial_knights",
    "Space Marines": "space_marines",
    "Space Wolves": "space_wolves",
    "Leagues of Votann": "leagues_of_votann",
    "Necrons": "necrons",
    "Orks": "orks",
    "T’au Empire": "tau_empire",
    "T'au Empire": "tau_empire",
    "Tyranids": "tyranids",
}

def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def sha_text(value: str) -> str | None:
    value = (value or "").strip()
    return hashlib.sha256(value.encode("utf-8")).hexdigest() if value else None

def fetch(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "WH40K-Tabletop-Knowledge-Base/1.0"})
    last = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                body = response.read()
            if not body:
                raise RuntimeError("empty response")
            dest.write_bytes(body)
            return
        except Exception as exc:
            last = exc
            time.sleep(2 ** attempt)
    raise RuntimeError(f"failed to download {url}: {last}")

def load_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    text = path.read_text(encoding="utf-8-sig")
    reader = csv.DictReader(text.splitlines(), delimiter="|")
    headers = [h for h in (reader.fieldnames or []) if h]
    rows = []
    for raw in reader:
        row = {k: (v or "").strip() for k, v in raw.items() if k}
        if any(row.values()):
            rows.append(row)
    return headers, rows

def clean_row(row: dict[str, str], *, prose_hash_fields=(), keep=()) -> dict:
    out = {}
    for key in keep:
        if key in row and row[key] != "":
            out[key] = row[key]
    for key in prose_hash_fields:
        if row.get(key):
            out[f"{key}_sha256"] = sha_text(row[key])
            out[f"{key}_present"] = True
    return out

def rows_by(rows: list[dict[str, str]], key: str) -> dict[str, list[dict[str, str]]]:
    out = defaultdict(list)
    for row in rows:
        if row.get(key):
            out[row[key]].append(row)
    return out

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--cache", default=".cache/wahapedia11e")
    p.add_argument("--snapshot-date", default="2026-09-29")
    p.add_argument("--repo-root", default=".")
    p.add_argument("--download", action="store_true")
    args = p.parse_args()

    root = Path(args.repo_root).resolve()
    cache = (root / args.cache).resolve()
    cache.mkdir(parents=True, exist_ok=True)

    if args.download:
        for name in FILES:
            fetch(BASE_URL + name, cache / name)

    tables = {}
    headers = {}
    file_manifest = []
    for name in FILES:
        path = cache / name
        if not path.exists():
            raise SystemExit(f"missing {path}")
        h, rows = load_csv(path)
        headers[name] = h
        tables[name] = rows
        file_manifest.append({
            "name": name,
            "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "rows": len(rows),
            "headers": h,
        })

    for name, required in REQUIRED_HEADERS.items():
        missing = required - set(headers.get(name, []))
        if missing:
            raise SystemExit(f"{name}: missing headers {sorted(missing)}")

    factions = tables["Factions.csv"]
    datasheets = tables["Datasheets.csv"]
    sources = tables["Source.csv"]
    if len(factions) < 20:
        raise SystemExit(f"suspicious faction count: {len(factions)}")
    if len(datasheets) < 1000:
        raise SystemExit(f"suspicious datasheet count: {len(datasheets)}")
    if not any(r.get("edition") == "11" for r in sources):
        raise SystemExit("Source.csv has no edition=11 rows; refusing stale/non-11E import")

    last_update = tables["Last_update.csv"][0].get("last_update", "") if tables["Last_update.csv"] else ""
    if not last_update.startswith("2026-"):
        raise SystemExit(f"suspicious Last_update.csv value: {last_update!r}")

    source_by_id = {r["id"]: r for r in sources if r.get("id")}
    faction_by_id = {r["id"]: r for r in factions if r.get("id")}
    ds_by_faction = rows_by(datasheets, "faction_id")
    related = {
        name: rows_by(rows, "datasheet_id")
        for name, rows in tables.items()
        if name.startswith("Datasheets_") and name not in {"Datasheets.csv"}
        and rows and "datasheet_id" in rows[0]
    }
    strats_by_faction = rows_by(tables["Stratagems.csv"], "faction_id")
    enh_by_faction = rows_by(tables["Enhancements.csv"], "faction_id")
    detabs_by_faction = rows_by(tables["Detachment_abilities.csv"], "faction_id")
    det_by_faction = rows_by(tables["Detachments.csv"], "faction_id") if tables["Detachments.csv"] and "faction_id" in tables["Detachments.csv"][0] else {}

    snap_dir = root / "rules" / "11e" / "snapshots" / args.snapshot_date / "wahapedia"
    faction_dir = snap_dir / "factions"
    faction_dir.mkdir(parents=True, exist_ok=True)

    source_rows = []
    for r in sources:
        source_rows.append(clean_row(r, keep=("id","name","type","edition","version","errata_date","errata_link")))

    faction_index = []
    totals = defaultdict(int)
    for fid, faction in sorted(faction_by_id.items(), key=lambda kv: kv[1].get("name","")):
        faction_name = faction.get("name", fid)
        repo_slug = ALIASES.get(faction_name)
        ds_out = []
        source_ids = set()
        for ds in ds_by_faction.get(fid, []):
            dsid = ds["id"]
            source_id = ds.get("source_id", "")
            if source_id:
                source_ids.add(source_id)
            source = source_by_id.get(source_id, {})
            is_legends = "(Warhammer Legends)" in source.get("name", "")
            models = [
                clean_row(x, keep=("line","name","m","t","sv","w","ld","oc","inv_sv","inv_sv_descr"))
                for x in related.get("Datasheets_models.csv", {}).get(dsid, [])
            ]
            weapons = [
                clean_row(x, keep=("line","line_in_wargear","dice","name","description","range","type","a","bs_ws","s","ap","d"))
                for x in related.get("Datasheets_wargear.csv", {}).get(dsid, [])
            ]
            keywords = [
                clean_row(x, keep=("keyword","model","is_faction_keyword"))
                for x in related.get("Datasheets_keywords.csv", {}).get(dsid, [])
            ]
            abilities = [
                clean_row(x, prose_hash_fields=("description",), keep=("line","ability_id","model","name","type","parameter"))
                for x in related.get("Datasheets_abilities.csv", {}).get(dsid, [])
            ]
            options = [
                clean_row(x, prose_hash_fields=("description",), keep=("line",))
                for x in related.get("Datasheets_options.csv", {}).get(dsid, [])
            ]
            composition = [
                clean_row(x, prose_hash_fields=("description",), keep=("line",))
                for x in related.get("Datasheets_unit_composition.csv", {}).get(dsid, [])
            ]
            leaders = [
                clean_row(x, keep=tuple(x.keys()))
                for x in related.get("Datasheets_leader.csv", {}).get(dsid, [])
            ]
            costs = [
                clean_row(x, keep=("line","description","cost"))
                for x in related.get("Datasheets_models_cost.csv", {}).get(dsid, [])
            ]
            ds_out.append({
                "id": dsid,
                "name": ds.get("name"),
                "role": ds.get("role"),
                "source_id": source_id or None,
                "source_name": source.get("name") or None,
                "source_version": source.get("version") or None,
                "source_edition": source.get("edition") or None,
                "is_legends": is_legends,
                "link": ds.get("link") or None,
                "loadout_sha256": sha_text(ds.get("loadout","")),
                "transport_sha256": sha_text(ds.get("transport","")),
                "damaged_description_sha256": sha_text(ds.get("damaged_description","")),
                "models": models,
                "points_rows": costs,
                "weapons": weapons,
                "keywords": keywords,
                "abilities": abilities,
                "options": options,
                "unit_composition": composition,
                "leader_links": leaders,
            })
            totals["models"] += len(models)
            totals["weapons"] += len(weapons)
            totals["keywords"] += len(keywords)
            totals["abilities"] += len(abilities)
            totals["options"] += len(options)
            totals["composition_rows"] += len(composition)
            totals["leader_rows"] += len(leaders)
        stratagems = [
            clean_row(x, prose_hash_fields=("description","legend"), keep=("id","name","type","cp_cost","turn","phase","detachment"))
            for x in strats_by_faction.get(fid, [])
        ]
        enhancements = [
            clean_row(x, prose_hash_fields=("description","legend"), keep=("id","detachment_id","detachment","name","cost"))
            for x in enh_by_faction.get(fid, [])
        ]
        detachment_abilities = [
            clean_row(x, prose_hash_fields=("description","legend"), keep=("id","detachment_id","detachment","name"))
            for x in detabs_by_faction.get(fid, [])
        ]
        detachments = [
            clean_row(x, keep=tuple(k for k in x.keys() if k not in {"description","legend"}), prose_hash_fields=("description","legend"))
            for x in det_by_faction.get(fid, [])
        ]
        payload = {
            "schema_version": "1.0",
            "snapshot_date": args.snapshot_date,
            "wahapedia_last_update": last_update,
            "faction": {
                "id": fid,
                "name": faction_name,
                "link": faction.get("link") or None,
                "repository_slug": repo_slug,
            },
            "copyright_policy": {
                "full_prose_stored": False,
                "rule_text_policy": "Names/metadata/structured characteristics are stored; long prose is represented by SHA-256 fingerprints and fetched from the source on demand.",
            },
            "sources": [source_by_id[sid] for sid in sorted(source_ids) if sid in source_by_id],
            "datasheets": ds_out,
            "detachments": detachments,
            "detachment_abilities": detachment_abilities,
            "enhancements": enhancements,
            "stratagems": stratagems,
        }
        slug = repo_slug or re.sub(r"[^a-z0-9]+", "-", faction_name.casefold()).strip("-")
        out_path = faction_dir / f"{slug}.json"
        out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        faction_index.append({
            "faction_id": fid, "name": faction_name, "repository_slug": repo_slug,
            "file": str(out_path.relative_to(root)).replace("\\","/"),
            "datasheets": len(ds_out), "detachments": len(detachments),
            "detachment_abilities": len(detachment_abilities),
            "enhancements": len(enhancements), "stratagems": len(stratagems),
        })
        totals["datasheets"] += len(ds_out)
        totals["detachments"] += len(detachments)
        totals["detachment_abilities"] += len(detachment_abilities)
        totals["enhancements"] += len(enhancements)
        totals["stratagems"] += len(stratagems)

    manifest = {
        "schema_version": "1.0",
        "captured_at": now_iso(),
        "snapshot_date": args.snapshot_date,
        "source": {
            "id": "WAHAPEDIA_11E_CSV",
            "base_url": BASE_URL,
            "last_update": last_update,
            "data_export_page": BASE_URL + "the-rules/data-export/",
        },
        "validation": {
            "edition_11_sources_present": True,
            "minimum_factions": 20,
            "minimum_datasheets": 1000,
            "copyright_reduced_snapshot": True,
        },
        "files": file_manifest,
        "counts": {"factions": len(factions), **dict(totals)},
        "factions": faction_index,
    }
    (snap_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (snap_dir / "source_catalog.json").write_text(json.dumps(source_rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = {
        "schema_version": "1.0",
        "snapshot_date": args.snapshot_date,
        "status": "STRUCTURAL_SNAPSHOT_READY_FOR_REVIEW",
        "wahapedia_last_update": last_update,
        "counts": manifest["counts"],
        "mapped_repository_factions": sum(1 for x in faction_index if x["repository_slug"]),
        "unmapped_wahapedia_factions": [x for x in faction_index if not x["repository_slug"]],
        "promotion": "NONE",
        "note": "This importer does not modify coverage/current.json. Promotion is a separate reviewed step.",
    }
    run_dir = root / "ingestion" / "runs"
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / f"{args.snapshot_date}_wahapedia_wave_b_structural.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
