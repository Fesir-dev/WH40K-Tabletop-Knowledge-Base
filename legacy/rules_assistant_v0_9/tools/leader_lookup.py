#!/usr/bin/env python3
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = json.loads((ROOT / "data" / "mfm_v1_2_user_factions_20260815.json").read_text(encoding="utf-8"))

def n(s): return " ".join(s.casefold().replace("’", "'").split())

if len(sys.argv) != 3:
    print("Usage: leader_lookup.py faction_slug 'character or bodyguard'")
    raise SystemExit(2)

slug, query = sys.argv[1], sys.argv[2]
links = DB["factions"][slug]["leader_support_links"]
q = n(query)
hits = []
for x in links:
    if q == n(x["character"]) or any(q == n(y) for y in x["can_join"]):
        hits.append(x)
if not hits:
    print("No exact link found.")
else:
    for x in hits:
        print(f"{x['character']} [{x['relation']}] -> {', '.join(x['can_join'])}")
