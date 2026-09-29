#!/usr/bin/env python3
from pathlib import Path
import json, sqlite3, sys
ROOT=Path(__file__).resolve().parents[1]
errors=[]
for rel in ['data/source_registry.json','data/tournament_mission_pool.json','data/app_reference_inventory.json','data/mfm_status.json','data/rules_tests.json','templates/faction_profile_template.json','templates/game_state_template.json']:
    try: json.loads((ROOT/rel).read_text(encoding='utf-8'))
    except Exception as e: errors.append(f'{rel}: {e}')
try:
    con=sqlite3.connect(ROOT/'data/w40k11_rules.db')
    counts={t:con.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0] for t in ['sources','mission_pool','quick_rulings','app_references','regression_tests']}
    con.close()
    if counts['mission_pool']!=20: errors.append(f"mission_pool count {counts['mission_pool']} != 20")
    if counts['regression_tests']<15: errors.append('too few regression tests')
except Exception as e: errors.append(f'database: {e}')
if errors:
    print('FAIL')
    print('\n'.join(errors))
    sys.exit(1)
print('PASS: JSON, SQLite and minimum counts validated.')
