#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
catalog=json.loads((ROOT/"factions/catalog.json").read_text(encoding="utf-8"))

parser=argparse.ArgumentParser(description="Query current normalized MFM v1.4 data.")
parser.add_argument("faction", help="repository faction slug, e.g. orks or imperial_fists")
parser.add_argument("--unit")
parser.add_argument("--detachment")
parser.add_argument("--summary", action="store_true")
args=parser.parse_args()

rows={x["slug"]:x for x in catalog["factions"]}
if args.faction not in rows:
    raise SystemExit(f"Unknown faction slug: {args.faction}")
row=rows[args.faction]
source=row.get("mfm_source_slug")
if not source:
    raise SystemExit(f"No MFM mapping for {args.faction}")
snap=json.loads((ROOT/"rules/11e/snapshots/2026-09-29/mfm/factions"/f"{source}.json").read_text(encoding="utf-8"))
mode=row.get("mfm_view_mode")
group=row.get("mfm_group_title")

def unit_visible(u):
    if mode=="base_only":
        return not u.get("groupTitle")
    if mode=="base_plus_group":
        return not u.get("groupTitle") or u.get("groupTitle")==group
    return True

units=[u for u in snap["units"] if unit_visible(u)]
result={
    "faction":args.faction,
    "source_faction":source,
    "mfm_version":snap["mfm_version"],
    "official_last_updated":snap["official_last_updated"],
    "view_mode":mode,
    "group_title":group,
    "provenance":snap["provenance"],
}
if args.summary:
    result["summary"]={
        "visible_units":len(units),
        "source_detachments":len(snap["detachments"]),
        "note":"For derived Space Marine chapter views, unit filtering is base + chapter group; detachment availability remains source-page scoped."
    }
elif args.unit:
    matches=[u for u in units if u["name"].casefold()==args.unit.casefold()]
    result["units"]=matches
elif args.detachment:
    matches=[d for d in snap["detachments"] if d["name"].casefold()==args.detachment.casefold()]
    result["detachments"]=matches
else:
    result["units"]=units
    result["detachments"]=snap["detachments"]
print(json.dumps(result,ensure_ascii=False,indent=2))
