#!/usr/bin/env python3
from __future__ import annotations
import json,tempfile,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from rules_engine_v0_7 import answer
CASES=json.loads((ROOT/'data/rules_engine_regression_v0_7.json').read_text(encoding='utf-8'))['interaction_cases']

def run_roster(roster):
    with tempfile.NamedTemporaryFile('w',encoding='utf-8',suffix='.json',delete=False) as f:
        json.dump(roster,f,ensure_ascii=False); fn=f.name
    p=subprocess.run([sys.executable,str(ROOT/'tools/validate_roster_v0_7.py'),fn],capture_output=True,text=True)
    Path(fn).unlink(missing_ok=True)
    return p.returncode,json.loads(p.stdout)

def base_custodes():
    return {
      'faction':'adeptus_custodes','battle_size':'incursion',
      'units':[
        {'id':'cap','name':'Shield-Captain','models':1},
        {'id':'guard','name':'Custodian Guard','models':4},
        {'id':'sisters','name':'Prosecutors','models':4},
        {'id':'rhino','name':'Anathema Psykana Rhino','models':1}],
      'detachments':['Might of the Moritoi'],'warlord_unit_id':'cap',
      'attachments':[{'character_unit_id':'cap','bodyguard_unit_id':'guard'}],
      'dedicated_transport_loads':[{'transport_unit_id':'rhino','embarked_unit_ids':['sisters']}],
      'enhancements':[]}

def main():
    total=passed=0
    for c in CASES:
        total+=1; r=answer(c['query']); ok=(r.get('result')==c.get('expect')) if 'expect' in c else (r.get('adjusted_cp')==c.get('expect_adjusted_cp'))
        print(('PASS' if ok else 'FAIL'),'-',c['name'],r); passed+=int(ok)
    roster_cases=[]
    r=base_custodes(); roster_cases.append(('valid incursion core roster',r,0,None))
    r=base_custodes(); r['detachments']=['Talons of the Emperor']; roster_cases.append(('incursion single 3DP exception',r,0,None))
    r=base_custodes(); r['detachments']=['Talons of the Emperor','Might of the Moritoi']; roster_cases.append(('incursion DP overflow',r,1,'detachment_points'))
    r=base_custodes(); r['dedicated_transport_loads']=[]; roster_cases.append(('empty dedicated transport rejected',r,1,'dedicated_transport_loaded'))
    r=base_custodes(); r['units']=[{'id':'t1','name':'Trajann Valoris','models':1},{'id':'t2','name':'Trajann Valoris','models':1}]; r['warlord_unit_id']='t1'; r['attachments']=[]; r['dedicated_transport_loads']=[]; roster_cases.append(('Epic Hero duplicate rejected',r,1,'unit_limit'))
    r=base_custodes(); r['units']=[{'id':f'g{i}','name':'Custodian Guard','models':4} for i in range(5)]+[{'id':'cap','name':'Shield-Captain','models':1}]; r['warlord_unit_id']='cap'; r['attachments']=[]; r['dedicated_transport_loads']=[]; roster_cases.append(('Incursion Battleline fifth copy rejected',r,1,'unit_limit'))
    r={'faction':'adeptus_mechanicus','battle_size':'incursion','units':[{'id':'marshal','name':'Skitarii Marshal','models':1},{'id':'rangers','name':'Skitarii Rangers','models':10}], 'detachments':['Rad-Zone Corps'],'warlord_unit_id':'marshal','attachments':[],'enhancements':[],'dedicated_transport_loads':[]}
    roster_cases.append(('Support must be attached',r,1,'support_must_attach'))
    for name,roster,expect_rc,expect_code in roster_cases:
        total+=1; rc,o=run_roster(roster); codes={x['code'] for x in o.get('checks',[]) if x.get('severity')=='ERROR'}
        ok=(rc==expect_rc and (expect_code is None or expect_code in codes)); print(('PASS' if ok else 'FAIL'),'-',name,'summary=',o.get('summary'),'errors=',sorted(codes)); passed+=int(ok)
    print(f'RESULT: {passed}/{total} PASS')
    return 0 if passed==total else 1
if __name__=='__main__': raise SystemExit(main())
