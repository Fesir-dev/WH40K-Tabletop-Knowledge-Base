#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'tests'/'test_repository_contracts.py'


def replace_once(text, old, new):
    n=text.count(old)
    if n!=1:
        raise RuntimeError(f'expected one match, found {n}: {old[:100]!r}')
    return text.replace(old,new,1)


def main():
    text=PATH.read_text(encoding='utf-8')
    text=replace_once(text,
'''        self.assertEqual(self.release["schema_version"], "1.2")''',
'''        self.assertEqual(self.release["schema_version"], "1.3")''')
    text=replace_once(text,
'''        self.assertEqual(policy["state"], "OPERATIONAL_READINESS_V1")''',
'''        self.assertEqual(policy["state"], "OPERATIONAL_READINESS_V1_SCOPED_RELEASES_RECONCILED")''')
    text=replace_once(text,
'''        self.assertEqual(report["as_of"], "2026-09-29")
        self.assertFalse(report["global_policy"]["auto_promote"])
        rows={x["transition_id"]:x for x in report["transitions"]}
        self.assertEqual(set(rows), {"SPACE_MARINES_CODEX_2026","ADEPTUS_CUSTODES_CODEX_2026"})
        self.assertEqual(rows["SPACE_MARINES_CODEX_2026"]["state"], "PRE_RELEASE_HOLD")
        self.assertEqual(rows["ADEPTUS_CUSTODES_CODEX_2026"]["state"], "UPCOMING_HOLD_NO_RELEASE_DATE")
        self.assertTrue(all(x["promotion_eligible"] is False for x in rows.values()))''',
'''        self.assertEqual(report["as_of"], "2026-10-20")
        self.assertFalse(report["global_policy"]["auto_promote"])
        self.assertTrue(report["global_policy"]["scoped_currentness_does_not_claim_full_codex_app_equivalence"])
        rows={x["transition_id"]:x for x in report["transitions"]}
        self.assertEqual(set(rows), {"SPACE_MARINES_CODEX_2026","ADEPTUS_CUSTODES_CODEX_2026"})
        self.assertTrue(all(x["state"] == "CURRENT_SCOPED_RECONCILED" for x in rows.values()))
        self.assertTrue(all(x["scoped_current_legal_confirmed"] for x in rows.values()))
        self.assertTrue(all(not x["full_codex_app_semantics_confirmed"] for x in rows.values()))
        self.assertTrue(all(x["promotion_eligible"] is False for x in rows.values()))''')
    text=replace_once(text,
'''            self.assertFalse(manifest["activation_evidence"]["current_legal_confirmed"])
            self.assertTrue(manifest["policy"]["preview_never_promotes"])''',
'''            self.assertFalse(manifest["activation_evidence"]["current_legal_confirmed"])
            self.assertTrue(manifest["activation_evidence"]["scoped_current_legal_confirmed"])
            self.assertFalse(manifest["activation_evidence"]["full_codex_app_semantics_confirmed"])
            self.assertEqual(manifest["transition_state"], "CURRENT_SCOPED_RECONCILED")
            self.assertTrue(manifest["reviewed_promotion"]["applied"])
            self.assertEqual(manifest["reviewed_promotion"]["promotion_id"], "REINGEST_49496d868bd7")
            self.assertTrue(manifest["policy"]["preview_never_promotes"])''')
    text=replace_once(text,
'''        self.assertEqual(report["as_of"], "2026-09-29")
        self.assertEqual(report["summary"]["transition_count"], 2)
        self.assertEqual(report["summary"]["no_action"], 2)''',
'''        self.assertEqual(report["as_of"], "2026-10-20")
        self.assertEqual(report["summary"]["transition_count"], 2)
        self.assertEqual(report["summary"]["no_action"], 2)
        self.assertEqual(report["summary"]["scoped_current_reconciled"], 2)''')
    text=replace_once(text,
'''        self.assertEqual(rows["SPACE_MARINES_CODEX_2026"]["watch_state"], "NO_ACTION")
        self.assertEqual(rows["SPACE_MARINES_CODEX_2026"]["next_action"], "WAIT_PRE_RELEASE")
        self.assertEqual(rows["ADEPTUS_CUSTODES_CODEX_2026"]["watch_state"], "NO_ACTION")
        self.assertEqual(rows["ADEPTUS_CUSTODES_CODEX_2026"]["next_action"], "WAIT_OFFICIAL_RELEASE_SIGNAL")''',
'''        self.assertEqual(rows["SPACE_MARINES_CODEX_2026"]["watch_state"], "NO_ACTION")
        self.assertEqual(rows["SPACE_MARINES_CODEX_2026"]["next_action"], "ALREADY_CURRENT_SCOPED")
        self.assertEqual(rows["ADEPTUS_CUSTODES_CODEX_2026"]["watch_state"], "NO_ACTION")
        self.assertEqual(rows["ADEPTUS_CUSTODES_CODEX_2026"]["next_action"], "ALREADY_CURRENT_SCOPED")
        self.assertTrue(all(x["scoped_current_legal_confirmed"] for x in rows.values()))
        self.assertTrue(all(not x["full_codex_app_semantics_confirmed"] for x in rows.values()))''')
    PATH.write_text(text,encoding='utf-8')
    print('release-transition repository regressions patched')
    return 0

if __name__=='__main__':
    raise SystemExit(main())
