#!/usr/bin/env python3
from __future__ import annotations
import json,subprocess,tempfile,sys,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'data/roster_regression_v0_9.json').read_text(encoding='utf-8'))
VAL=ROOT/'tools/validate_roster_v0_9.py'
failed=[]
for case in DATA['cases']:
    path=None
    try:
        with tempfile.NamedTemporaryFile('w',encoding='utf-8',suffix='.json',delete=False) as f:
            json.dump(case['roster'],f,ensure_ascii=False); path=f.name
        p=subprocess.run([sys.executable,str(VAL),path],capture_output=True,text=True)
        try: out=json.loads(p.stdout)
        except Exception as ex:
            failed.append((case['id'],f'non-json output: {ex}: {p.stdout[-500:]}')); continue
        err={x['code'] for x in out.get('checks',[]) if x.get('severity')=='ERROR'}
        pas={x['code'] for x in out.get('checks',[]) if x.get('severity')=='PASS'}
        problems=[]
        for c in case.get('expect_error_codes',[]):
            if c not in err:problems.append(f'missing ERROR {c}')
        for c in case.get('expect_pass_codes',[]):
            if c not in pas:problems.append(f'missing PASS {c}')
        for c in case.get('expect_no_error_codes',[]):
            if c in err:problems.append(f'unexpected ERROR {c}')
        cert=case.get('expect_certification')
        if cert and out.get('summary',{}).get('certification')!=cert:problems.append(f'cert {out.get("summary",{}).get("certification")} != {cert}')
        if problems:failed.append((case['id'],'; '.join(problems),out))
        else:print('PASS',case['id'])
    finally:
        if path:
            try: os.unlink(path)
            except OSError: pass
print(f'RESULT {len(DATA["cases"])-len(failed)}/{len(DATA["cases"])} PASS')
if failed:
    for item in failed:
        print('FAIL',item[0],item[1])
        if len(item)>2: print(json.dumps(item[2],ensure_ascii=False,indent=2)[:6000])
    raise SystemExit(1)
