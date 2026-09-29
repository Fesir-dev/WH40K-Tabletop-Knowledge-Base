#!/usr/bin/env python3
from __future__ import annotations
import json,sys,unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/'data/stratagem_semantic_index_v0_7_20260815.json').read_text(encoding='utf-8'))
def norm(s): return ' '.join(unicodedata.normalize('NFKC',s).casefold().replace('’',"'").split())
def main():
    if len(sys.argv)<2: print('Usage: query_stratagem_v0_7.py "name fragment" [faction_slug]'); return 2
    q=norm(sys.argv[1]); fs=[sys.argv[2]] if len(sys.argv)>2 else D['factions']; hits=[]
    for f in fs:
        if f not in D['factions']: continue
        for x in D['factions'][f]['entries']:
            if q in norm(x['name']) or q in norm(x['detachment']): hits.append({'faction':f,**x})
    print(json.dumps({'query':sys.argv[1],'hits':hits,'note':'Exact current wording must come from current official Faction Pack/App, especially when source_pack_status is CURRENT_DELTA_TOUCHED_CONSULT_V1_1_EXACT_TEXT.'},ensure_ascii=False,indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
