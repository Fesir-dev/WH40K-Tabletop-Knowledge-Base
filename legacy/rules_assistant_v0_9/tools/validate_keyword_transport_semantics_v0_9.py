#!/usr/bin/env python3
from __future__ import annotations
import json,sys,unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
K=json.loads((ROOT/'data/keyword_membership_current_v0_9_20260815.json').read_text(encoding='utf-8'))
T=json.loads((ROOT/'data/transport_profiles_v0_9_20260815.json').read_text(encoding='utf-8'))
M=json.loads((ROOT/'data/mfm_v1_2_user_factions_20260815.json').read_text(encoding='utf-8'))
def norm(s):
 s=unicodedata.normalize('NFKC',str(s)).replace('‑','-').replace('–','-').replace('—','-').replace('’',"'")
 return ' '.join(s.split()).casefold()
errors=[]; kw_records=0; member_assertions=0; complete=0
for fac, kws in K.get('factions',{}).items():
 if fac not in M['factions']: errors.append(f'unknown faction in keyword layer: {fac}'); continue
 local={norm(u['name_en']) for u in M['factions'][fac]['units']}
 for kw,rec in kws.items():
  kw_records+=1; member_assertions+=len(rec.get('members',[])); complete+=bool(rec.get('complete_for_local_mfm'))
  seen=set()
  for name in rec.get('members',[]):
   n=norm(name)
   if n in seen: errors.append(f'duplicate keyword member {fac}/{kw}: {name}')
   seen.add(n)
   if n not in local: errors.append(f'keyword member not in current local MFM {fac}/{kw}: {name}')
profiles=0;ded=0;non=0
for p in T.get('profiles',[]):
 profiles+=1; ded+=bool(p.get('dedicated')); non+=not bool(p.get('dedicated'))
 fac=p['faction']; unit=norm(p['unit'])
 if fac not in M['factions']: errors.append(f'unknown transport faction: {fac}'); continue
 local={norm(u['name_en']) for u in M['factions'][fac]['units']}
 if unit not in local: errors.append(f'transport not in current local MFM {fac}: {p["unit"]}')
 if int(p.get('capacity',0))<=0: errors.append(f'invalid capacity {fac}: {p["unit"]}')
 if p.get('status')!='CURRENT_EXACT': errors.append(f'non-current-exact transport profile {fac}: {p["unit"]}')
print(f'keyword records: {kw_records}; member assertions: {member_assertions}; complete local keyword sets: {complete}')
print(f'transport profiles: {profiles}; dedicated: {ded}; non-dedicated: {non}')
if errors:
 print('FAIL')
 for e in errors: print('-',e)
 sys.exit(1)
print('PASS keyword + transport semantics v0.9')
