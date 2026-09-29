#!/usr/bin/env python3
from __future__ import annotations
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CAT=json.loads((ROOT/'data/interaction_rules_v0_7_20260815.json').read_text(encoding='utf-8'))

def answer(q):
    kind=q.get('query')
    if kind=='can_make_normal_move':
        used=int(q.get('normal_moves_this_phase',0)); explicit=bool(q.get('explicit_exception',False))
        return {'result':'YES' if used<1 or explicit else 'NO','rule':'normal_move_once_per_phase','used':used,'exception_applied':explicit}
    if kind=='gain_extra_cp':
        gained=int(q.get('extra_cp_gained_this_battle_round',0)); amount=int(q.get('amount',1))
        allowed=max(0,1-gained); return {'result':'YES' if allowed>=amount else 'NO','rule':'extra_cp_once_per_round','requested':amount,'allowed_now':allowed}
    if kind=='can_use_stratagem':
        same=int(q.get('same_stratagem_uses_this_phase',0)); target=int(q.get('target_stratagems_this_phase',0)); named_repeat=bool(q.get('explicit_named_repeat_permission',False)); target_exception=bool(q.get('explicit_target_exception',False))
        reasons=[]
        if same>=1 and not named_repeat: reasons.append('same stratagem already used this phase; no explicit named repeat permission')
        if target>=1 and not target_exception: reasons.append('target unit already targeted by a stratagem this phase; no explicit exception')
        return {'result':'NO' if reasons else 'YES','rule':'stratagem_phase_caps','reasons':reasons}
    if kind=='adjust_stratagem_cp_cost':
        base=int(q.get('base_cp',0)); generic_zero=bool(q.get('generic_zero_cp_rule',False)); explicitly_named=bool(q.get('rule_explicitly_names_stratagem',False))
        if generic_zero and not explicitly_named: return {'result':'OK','adjusted_cp':max(0,base-1),'rule':'generic_zero_cp_reduction'}
        if generic_zero and explicitly_named: return {'result':'OK','adjusted_cp':0,'rule':'explicit_named_zero_cp_permission'}
        return {'result':'OK','adjusted_cp':base,'rule':'no_adjustment'}
    if kind=='revived_character_attachment':
        return {'result':'SEPARATE_UNIT','rule':'revived_character_attachment_scope','effect':'Revived slain Character returns as its own unit of one.','effective_from':'2026-07-22','source_priority':'newer official July update overrides June core wording'}
    return {'result':'UNKNOWN','reason':f'Unsupported query: {kind}'}

def main():
    if len(sys.argv)!=2: print('Usage: rules_engine_v0_7.py query.json'); return 2
    q=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8')); print(json.dumps(answer(q),ensure_ascii=False,indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
