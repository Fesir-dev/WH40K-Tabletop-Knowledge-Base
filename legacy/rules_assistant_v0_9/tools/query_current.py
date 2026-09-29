#!/usr/bin/env python3
"""Search only the current v0.6 MFM 1.2 + Faction Pack v1.1 user-faction layer."""
from __future__ import annotations
import argparse, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DB=json.loads((ROOT/'data'/'mfm_v1_2_user_factions_20260815.json').read_text(encoding='utf-8'))
UPDATES=[json.loads(x) for x in (ROOT/'data'/'current_rule_update_index_20260815.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]

def has(s,q): return q.casefold() in str(s).casefold()
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('query')
    ap.add_argument('--faction',choices=sorted(DB['factions']))
    a=ap.parse_args(); q=a.query
    print(f"CURRENT runtime: MFM {DB['source']['interactive_version']} / official update {DB['source']['official_updated']} / checked {DB['source']['checked_at']}")
    hits=0
    for slug,f in DB['factions'].items():
        if a.faction and slug!=a.faction: continue
        for u in f['units']:
            if has(u['name_en'],q) or any(has(x,q) for x in u.get('aliases',[])):
                print(f"UNIT [{slug}] {u['name_en']}: {json.dumps(u['cost_bands'],ensure_ascii=False)}"); hits+=1
        for d in f['detachments']:
            if has(d['name_en'],q) or has(d.get('force_disposition',''),q):
                print(f"DETACHMENT [{slug}] {d['name_en']}: {d['dp']} DP | {d['force_disposition']} | tags={d.get('unique_tags',[])}"); hits+=1
        for link in f['leader_support_links']:
            if has(link.get('name_en',''),q) or any(has(z,q) for z in link.get('can_join',[])):
                print(f"LEADER/SUPPORT [{slug}] {link.get('name_en')}: {link.get('role')} -> {', '.join(link.get('can_join',[]))}"); hits+=1
    for x in UPDATES:
        if a.faction and x['faction']!=a.faction: continue
        if has(x['target'],q) or has(x['summary'],q) or has(x['scope'],q):
            print(f"RULE UPDATE [{x['faction']}] {x['scope']} / {x['target']}: {x['summary']} [Faction Pack v1.1]"); hits+=1
    if not hits: print('NO CURRENT LOCAL MATCH. Check official live source/App; do not fall back silently to historical snapshots.')
if __name__=='__main__': main()
