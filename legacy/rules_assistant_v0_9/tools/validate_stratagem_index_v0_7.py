#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/'data/stratagem_semantic_index_v0_7_20260815.json').read_text(encoding='utf-8'))
errors=[]; total=0
for f,v in D['factions'].items():
 total+=v['count']
 if v['count']!=len(v['entries']): errors.append(f'{f}: count mismatch')
 seen=set()
 for x in v['entries']:
  k=(x['detachment'],x['name'])
  if k in seen: errors.append(f'{f}: duplicate {k}')
  seen.add(k)
  if x['cp'] is None: errors.append(f'{f}/{x["name"]}: missing CP')
print(json.dumps({'status':'PASS' if not errors else 'FAIL','total':total,'factions':{f:v['count'] for f,v in D['factions'].items()},'errors':errors},indent=2))
raise SystemExit(1 if errors else 0)
