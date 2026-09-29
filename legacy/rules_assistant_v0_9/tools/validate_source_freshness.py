#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
from datetime import date

ROOT=Path(__file__).resolve().parents[1]
errors=[]
warnings=[]
state_path=ROOT/'data'/'live_rules_source_state_20260815.json'
uru_path=ROOT/'data'/'universal_rules_updates_v1_0_20260722.json'
old_mfm=ROOT/'data'/'mfm_live_snapshot_20260710.json'
current_mfm=ROOT/'data'/'mfm_v1_2_user_factions_20260815.json'
for p in (state_path,uru_path,old_mfm,current_mfm):
    if not p.exists(): errors.append(f'Missing {p.relative_to(ROOT)}')
if errors:
    print('FAIL\n'+'\n'.join(errors)); raise SystemExit(1)
state=json.loads(state_path.read_text(encoding='utf-8'))
uru=json.loads(uru_path.read_text(encoding='utf-8'))
if state.get('as_of')!='2026-08-15': errors.append('Unexpected source-state checkpoint date')
ids={x['id'] for x in state.get('sources',[])}
required={'CORE_11E_CURRENT_20260815','UNIVERSAL_RULES_UPDATES_1_0_20260722','MFM_CURRENT_20260722','WAHAPEDIA_11E_CURRENT_20260815'}
missing=required-ids
if missing: errors.append('Missing current source IDs: '+', '.join(sorted(missing)))
cur=json.loads(current_mfm.read_text(encoding='utf-8'))
if cur.get('source',{}).get('interactive_version')!='1.2': errors.append('Current runtime is not MFM 1.2')
if cur.get('source',{}).get('official_updated')!='2026-07-22': errors.append('Unexpected current MFM update date')
if len(cur.get('factions',{}))!=8: errors.append('Expected 8 current user factions')
if len(uru.get('rules',[]))!=4: errors.append('Expected 4 normalized Universal Rules Updates v1.0 entries')
if uru.get('legal_from')!='2026-07-22': errors.append('Unexpected URU legal_from')
old=json.loads(old_mfm.read_text(encoding='utf-8'))
old_updated=old.get('source',{}).get('updated')
if old_updated and old_updated >= '2026-07-22': errors.append('Historical MFM unexpectedly claims current-or-newer source date')
if old_updated and old_updated < '2026-07-22': warnings.append(f'Historical MFM source {old_updated} is older than current official update 2026-07-22 (expected).')
if errors:
    print('FAIL')
    print('\n'.join(errors))
    raise SystemExit(1)
print('PASS: source hierarchy checkpoint is internally consistent.')
for w in warnings: print('WARN:',w)
print('NOTE: this is an offline integrity/freshness-metadata check; live web freshness must still be checked at query time.')
