#!/usr/bin/env python3
from __future__ import annotations
import json,sys,unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
K=json.loads((ROOT/'data/keyword_membership_current_v0_9_20260815.json').read_text(encoding='utf-8'))
M=json.loads((ROOT/'data/mfm_v1_2_user_factions_20260815.json').read_text(encoding='utf-8'))
def norm(s):
 s=unicodedata.normalize('NFKC',str(s)).replace('‑','-').replace('–','-').replace('—','-').replace('’',"'")
 return ' '.join(s.split()).casefold()
def main():
 if len(sys.argv)<3:
  print('Usage: query_semantics_v0_9.py <faction> <unit name>'); return 2
 f=sys.argv[1]; name=' '.join(sys.argv[2:]); units=M.get('factions',{}).get(f,{}).get('units',[])
 u=next((x for x in units if norm(x['name_en'])==norm(name) or any(norm(a)==norm(name) for a in x.get('aliases',[]))),None)
 if not u:
  print(json.dumps({'found':False,'faction':f,'query':name},ensure_ascii=False,indent=2)); return 1
 yes=[]; no=[]
 for kw,rec in K.get('factions',{}).get(f,{}).items():
  members={norm(x) for x in rec.get('members',[])}
  if norm(u['name_en']) in members: yes.append(kw)
  elif rec.get('complete_for_local_mfm'): no.append(kw)
 print(json.dumps({'found':True,'faction':f,'unit':u['name_en'],'proven_keywords':sorted(yes),'proven_absent_keywords':sorted(no),'as_of':K['as_of']},ensure_ascii=False,indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
