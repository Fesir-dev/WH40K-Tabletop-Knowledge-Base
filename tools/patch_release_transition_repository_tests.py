#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEST_PATH = ROOT / "tests" / "test_repository_contracts.py"
VALIDATOR_PATH = ROOT / "tools" / "validate_repo.py"


def replace_once(text, old, new):
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f"expected one match, found {n}: {old[:120]!r}")
    return text.replace(old, new, 1)


def patch_tests():
    text = TEST_PATH.read_text(encoding="utf-8")
    text = replace_once(text,
'''        self.assertEqual(self.release["schema_version"], "1.2")''',
'''        self.assertEqual(self.release["schema_version"], "1.3")''')
    text = replace_once(text,
'''        self.assertEqual(policy["state"], "OPERATIONAL_READINESS_V1")''',
'''        self.assertEqual(policy["state"], "OPERATIONAL_READINESS_V1_SCOPED_RELEASES_RECONCILED")''')
    text = replace_once(text,
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
    text = replace_once(text,
'''            self.assertFalse(manifest["activation_evidence"]["current_legal_confirmed"])
            self.assertTrue(manifest["policy"]["preview_never_promotes"])''',
'''            self.assertFalse(manifest["activation_evidence"]["current_legal_confirmed"])
            self.assertTrue(manifest["activation_evidence"]["scoped_current_legal_confirmed"])
            self.assertFalse(manifest["activation_evidence"]["full_codex_app_semantics_confirmed"])
            self.assertEqual(manifest["transition_state"], "CURRENT_SCOPED_RECONCILED")
            self.assertTrue(manifest["reviewed_promotion"]["applied"])
            self.assertEqual(manifest["reviewed_promotion"]["promotion_id"], "REINGEST_49496d868bd7")
            self.assertTrue(manifest["policy"]["preview_never_promotes"])''')
    text = replace_once(text,
'''        self.assertEqual(report["as_of"], "2026-09-29")
        self.assertEqual(report["summary"]["transition_count"], 2)
        self.assertEqual(report["summary"]["no_action"], 2)''',
'''        self.assertEqual(report["as_of"], "2026-10-20")
        self.assertEqual(report["summary"]["transition_count"], 2)
        self.assertEqual(report["summary"]["no_action"], 2)
        self.assertEqual(report["summary"]["scoped_current_reconciled"], 2)''')
    text = replace_once(text,
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
    text = replace_once(text,
'''        layer=self.current["release_transition_readiness"]
        self.assertEqual(layer["state"], "OPERATIONAL_V1")
        self.assertFalse(layer["policy"]["auto_promote"])
        tracked={x["id"]:x for x in layer["tracked_transitions"]}
        self.assertEqual(tracked["SPACE_MARINES_CODEX_2026"]["state"], "PRE_RELEASE_HOLD")
        self.assertEqual(tracked["ADEPTUS_CUSTODES_CODEX_2026"]["state"], "UPCOMING_HOLD_NO_RELEASE_DATE")
        activation=self.current["release_transition_activation_watch"]
        self.assertEqual(activation["state"], "OPERATIONAL_V1")
        self.assertEqual(activation["checkpoint_status"], "NO_ACTION_REQUIRED")''',
'''        layer=self.current["release_transition_readiness"]
        self.assertEqual(layer["state"], "OPERATIONAL_V1_SCOPED_RELEASES_RECONCILED")
        self.assertFalse(layer["policy"]["auto_promote"])
        tracked={x["id"]:x for x in layer["tracked_transitions"]}
        self.assertTrue(all(x["state"] == "CURRENT_SCOPED_RECONCILED" for x in tracked.values()))
        self.assertTrue(all(x["scoped_current_legal_confirmed"] for x in tracked.values()))
        self.assertTrue(all(not x["full_codex_app_semantics_confirmed"] for x in tracked.values()))
        activation=self.current["release_transition_activation_watch"]
        self.assertEqual(activation["state"], "OPERATIONAL_V1")
        self.assertEqual(activation["checkpoint_as_of"], "2026-10-20")
        self.assertEqual(activation["checkpoint_status"], "NO_ACTION_REQUIRED")
        self.assertEqual(activation["scoped_current_reconciled"], 2)''')
    TEST_PATH.write_text(text, encoding="utf-8")


def patch_validator():
    text = VALIDATOR_PATH.read_text(encoding="utf-8")
    text = replace_once(text,
'''    if release.get("schema_version") != "1.2":
        errors.append("release_state.json must be schema 1.2 with activation watch v1")''',
'''    if release.get("schema_version") != "1.3":
        errors.append("release_state.json must be schema 1.3 after scoped release reconciliation")''')
    text = replace_once(text,
'''    if transition_policy.get("state") != "OPERATIONAL_READINESS_V1":
        errors.append("Release transition policy must be OPERATIONAL_READINESS_V1")''',
'''    if transition_policy.get("state") != "OPERATIONAL_READINESS_V1_SCOPED_RELEASES_RECONCILED":
        errors.append("Release transition policy must record scoped release reconciliation")''')
    text = replace_once(text,
'''    if readiness.get("as_of") != "2026-09-29":
        errors.append("Committed release transition readiness checkpoint must remain 2026-09-29")''',
'''    if readiness.get("as_of") != "2026-10-20":
        errors.append("Committed release transition readiness checkpoint must be 2026-10-20")''')
    text = replace_once(text,
'''    if readiness_rows.get("SPACE_MARINES_CODEX_2026", {}).get("state") != "PRE_RELEASE_HOLD":
        errors.append("Space Marines transition must remain PRE_RELEASE_HOLD at 2026-09-29 checkpoint")
    if readiness_rows.get("ADEPTUS_CUSTODES_CODEX_2026", {}).get("state") != "UPCOMING_HOLD_NO_RELEASE_DATE":
        errors.append("Custodes transition must remain UPCOMING_HOLD_NO_RELEASE_DATE at 2026-09-29 checkpoint")''',
'''    if any(x.get("state") != "CURRENT_SCOPED_RECONCILED" for x in readiness_rows.values()):
        errors.append("Tracked release transitions must be CURRENT_SCOPED_RECONCILED")
    if any(x.get("scoped_current_legal_confirmed") is not True for x in readiness_rows.values()):
        errors.append("Tracked release transitions must confirm scoped current legality")
    if any(x.get("full_codex_app_semantics_confirmed") is not False for x in readiness_rows.values()):
        errors.append("Scoped release reconciliation must not claim full Codex/app semantic equivalence")''')
    text = replace_once(text,
'''        if activation.get("current_legal_confirmed") is not False:
            errors.append(f"Pre-release manifest prematurely confirmed current legality: {tid}")''',
'''        if activation.get("current_legal_confirmed") is not False:
            errors.append(f"Scoped release manifest must not claim full current legality: {tid}")
        if activation.get("scoped_current_legal_confirmed") is not True:
            errors.append(f"Scoped release manifest lacks current scoped confirmation: {tid}")
        if activation.get("full_codex_app_semantics_confirmed") is not False:
            errors.append(f"Scoped release manifest improperly claims full Codex/app semantics: {tid}")
        if manifest.get("transition_state") != "CURRENT_SCOPED_RECONCILED":
            errors.append(f"Release manifest scoped state drifted: {tid}")
        if manifest.get("reviewed_promotion", {}).get("promotion_id") != "REINGEST_49496d868bd7":
            errors.append(f"Release manifest reviewed promotion pointer drifted: {tid}")''')
    text = replace_once(text,
'''        if row.get("current_legal_confirmation") is not False:
            errors.append(f"release_state prematurely confirmed future current legality: {tid}")''',
'''        if row.get("current_legal_confirmation") is not False:
            errors.append(f"release_state must not claim full current legality: {tid}")
        if row.get("scoped_current_legal_confirmation") is not True:
            errors.append(f"release_state lacks scoped current confirmation: {tid}")
        if row.get("readiness_state") != "CURRENT_SCOPED_RECONCILED":
            errors.append(f"release_state scoped reconciliation state drifted: {tid}")
        if row.get("full_codex_app_semantics") != "PENDING_AUTHORIZED_APP_EVIDENCE":
            errors.append(f"release_state full Codex/app boundary drifted: {tid}")''')
    text = replace_once(text,
'''    if activation_report.get("as_of") != "2026-09-29":
        errors.append("Committed activation watch checkpoint must remain 2026-09-29")''',
'''    if activation_report.get("as_of") != "2026-10-20":
        errors.append("Committed activation watch checkpoint must be 2026-10-20")''')
    text = replace_once(text,
'''    if activation_report.get("summary", {}).get("no_action") != 2:
        errors.append("Activation watch checkpoint should have two NO_ACTION transitions")''',
'''    if activation_report.get("summary", {}).get("no_action") != 2:
        errors.append("Activation watch checkpoint should have two NO_ACTION transitions")
    if activation_report.get("summary", {}).get("scoped_current_reconciled") != 2:
        errors.append("Activation watch must record two scoped-current reconciled transitions")
    if any(x.get("next_action") != "ALREADY_CURRENT_SCOPED" for x in activation_report.get("transitions", [])):
        errors.append("Activation watch scoped-current transition action drifted")''')
    text = replace_once(text,
'''    readiness_layer = current_rules.get("release_transition_readiness", {})
    if readiness_layer.get("state") != "OPERATIONAL_V1":
        errors.append("Current rules must record release transition readiness v1 as operational")
    if readiness_layer.get("policy", {}).get("auto_promote") is not False:
        errors.append("Current release transition layer must keep auto_promote=false")
    tracked = {x.get("id"): x for x in readiness_layer.get("tracked_transitions", [])}
    if tracked.get("SPACE_MARINES_CODEX_2026", {}).get("state") != "PRE_RELEASE_HOLD":
        errors.append("Current Space Marines transition state drifted")
    if tracked.get("ADEPTUS_CUSTODES_CODEX_2026", {}).get("state") != "UPCOMING_HOLD_NO_RELEASE_DATE":
        errors.append("Current Custodes transition state drifted")''',
'''    readiness_layer = current_rules.get("release_transition_readiness", {})
    if readiness_layer.get("state") != "OPERATIONAL_V1_SCOPED_RELEASES_RECONCILED":
        errors.append("Current rules must record scoped release transition reconciliation")
    if readiness_layer.get("policy", {}).get("auto_promote") is not False:
        errors.append("Current release transition layer must keep auto_promote=false")
    tracked = {x.get("id"): x for x in readiness_layer.get("tracked_transitions", [])}
    if any(x.get("state") != "CURRENT_SCOPED_RECONCILED" for x in tracked.values()):
        errors.append("Current tracked release transition state drifted")
    if any(x.get("scoped_current_legal_confirmed") is not True for x in tracked.values()):
        errors.append("Current tracked release transition lacks scoped current confirmation")
    if any(x.get("full_codex_app_semantics_confirmed") is not False for x in tracked.values()):
        errors.append("Current tracked release transition improperly claims full Codex/app semantics")''')
    text = replace_once(text,
'''    if activation_layer.get("checkpoint_status") != "NO_ACTION_REQUIRED":
        errors.append("Current release activation checkpoint status drifted")''',
'''    if activation_layer.get("checkpoint_as_of") != "2026-10-20":
        errors.append("Current release activation checkpoint date drifted")
    if activation_layer.get("checkpoint_status") != "NO_ACTION_REQUIRED":
        errors.append("Current release activation checkpoint status drifted")
    if activation_layer.get("scoped_current_reconciled") != 2:
        errors.append("Current release activation scoped reconciliation count drifted")''')
    VALIDATOR_PATH.write_text(text, encoding="utf-8")


def main():
    patch_tests()
    patch_validator()
    print("release-transition repository regressions and validator contracts patched")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
