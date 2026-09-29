#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/'data'/'mfm_v1_2_user_factions_20260815.json').read_text(encoding='utf-8'))
T=json.loads((ROOT/'data'/'current_regression_tests_v0_6.json').read_text(encoding='utf-8'))['tests']
U={}
for slug in D['factions']:
    U[slug]=json.loads((ROOT/'factions'/slug/'rules_updates_v1_1_20260722.json').read_text(encoding='utf-8'))

def unit_cost(f,n,models,copy):
    u=next(x for x in D['factions'][f]['units'] if x['name_en']==n)
    b=next(x for x in u['cost_bands'] if copy>=x['min_copy'] and (x['max_copy'] is None or copy<=x['max_copy']))
    return b['sizes'][str(models)]
errors=[]
for t in T:
    try:
        if t['type']=='unit_cost':
            got=unit_cost(t['faction'],t['unit'],t['models'],t['copy'])
            if got!=t['expected']: errors.append(f"{t['id']}: {got} != {t['expected']}")
        elif t['type']=='detachment':
            d=next(x for x in D['factions'][t['faction']]['detachments'] if x['name_en']==t['detachment'])
            got=(d['dp'],d['force_disposition']); exp=(t['expected_dp'],t['expected_disposition'])
            if got!=exp: errors.append(f"{t['id']}: {got} != {exp}")
        elif t['type']=='rule_update':
            hay=' '.join(x['target']+' '+x['summary'] for x in U[t['faction']]['change_summary'])
            if t['contains'].casefold() not in hay.casefold(): errors.append(f"{t['id']}: missing semantic marker {t['contains']}")
        else: errors.append(f"{t['id']}: unknown type")
    except Exception as e: errors.append(f"{t['id']}: {type(e).__name__}: {e}")
if errors:
    print('FAIL'); print('\n'.join(errors)); raise SystemExit(1)
print(f'PASS: {len(T)}/{len(T)} current-runtime regression cases.')
