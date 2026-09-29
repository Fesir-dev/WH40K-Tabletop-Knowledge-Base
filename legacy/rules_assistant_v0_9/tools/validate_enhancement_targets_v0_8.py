#!/usr/bin/env python3
import json, unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def canon(s):
    s=unicodedata.normalize('NFKC',str(s)).replace('‑','-').replace('–','-').replace('—','-').replace('‐','-').replace('’',"'")
    return ' '.join(s.split())
def norm(s): return canon(s).casefold()

p=json.loads((ROOT/'data/enhancement_target_predicates_v0_8_20260815.json').read_text(encoding='utf-8'))
m=json.loads((ROOT/'data/enhancement_metadata_v0_7_20260815.json').read_text(encoding='utf-8'))
fm=json.loads((ROOT/'data/mfm_v1_2_user_factions_20260815.json').read_text(encoding='utf-8'))
aliases=json.loads((ROOT/'data/enhancement_name_aliases_v0_8_20260815.json').read_text(encoding='utf-8'))
alias_map={(x['faction'],norm(x['detachment']),norm(x['source_name'])):norm(x['current_name']) for x in aliases.get('aliases',[])}
errors=[]; total=execn=alias_hits=0
for f,fd in p['factions'].items():
    meta={(norm(x['detachment']),norm(x['name'])) for x in m['factions'][f]['entries']}
    costs={(norm(d),norm(n)) for d,rows in fm['factions'][f]['enhancement_costs'].items() for n in rows}
    for x in fd['entries']:
        total+=1
        key=(norm(x['detachment']),norm(x['name']))
        if key not in meta:errors.append(f'{f}: predicate not in metadata {(x["detachment"],x["name"])}')
        cost_key=key
        if cost_key not in costs:
            ali=alias_map.get((f,key[0],key[1]))
            if ali:
                cost_key=(key[0],ali); alias_hits+=1
        if cost_key not in costs:errors.append(f'{f}: predicate not in current MFM costs {(x["detachment"],x["name"])}')
        if not x.get('raw_target_clause'):errors.append(f'{f}: missing target clause {(x["detachment"],x["name"])}')
        if x.get('normalization_status')=='EXECUTABLE':execn+=1
        else:errors.append(f'{f}: non-executable predicate {(x["detachment"],x["name"])}: {x.get("normalization_status")}')
print(f'enhancement target predicates: {execn}/{total} executable; alias reconciliations: {alias_hits}')
if errors:
    print('\n'.join('ERROR '+x for x in errors));raise SystemExit(1)
print('PASS')
