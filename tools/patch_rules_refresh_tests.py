#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'tests'/'test_repository_contracts.py'


def rep(text, old, new):
    n=text.count(old)
    if n!=1:
        raise RuntimeError(f'expected 1 match, got {n}: {old[:100]!r}')
    return text.replace(old,new,1)


def main():
    text=PATH.read_text(encoding='utf-8')
    text=rep(text,
'''    def test_mfm_wave_a_snapshot(self):
        self.assertEqual(self.mfm["official_source"]["version"], "1.4")
        self.assertEqual(self.mfm["official_source"]["last_updated"], "2026-09-02")
        self.assertEqual(len(self.mfm["faction_files"]), 30)
        self.assertEqual(self.mfm["totals"]["units"], 1789)
        self.assertEqual(self.mfm["totals"]["pricing_rows"], 2980)
        self.assertEqual(self.mfm["totals"]["leader_relations"], 1574)
        self.assertEqual(self.mfm["totals"]["enhancement_cost_entries"], 1193)''',
'''    def test_mfm_wave_a_snapshot(self):
        self.assertEqual(self.mfm["official_source"]["version"], self.current["wave_a_mfm"]["version"])
        self.assertEqual(self.mfm["official_source"]["last_updated"], self.current["wave_a_mfm"]["last_updated"])
        self.assertEqual(self.mfm["official_source"]["version"], "1.6")
        self.assertEqual(self.mfm["official_source"]["last_updated"], "2026-10-14")
        self.assertEqual(len(self.mfm["faction_files"]), 30)
        self.assertEqual(self.mfm["totals"]["units"], 1797)
        self.assertEqual(self.mfm["totals"]["pricing_rows"], 3058)
        self.assertEqual(self.mfm["totals"]["leader_relations"], 1624)
        self.assertEqual(self.mfm["totals"]["enhancement_cost_entries"], 15)
        historical=json.loads((ROOT/"rules/11e/snapshots/2026-09-29/mfm/index.json").read_text(encoding="utf-8"))
        self.assertEqual(historical["official_source"]["version"], "1.4")
        self.assertEqual(historical["official_source"]["last_updated"], "2026-09-02")''')

    text=rep(text,
'''        self.assertEqual(off["verified_pdf_assets"], off["pdf_assets"])
        self.assertEqual(off["failures"], 0)''',
'''        self.assertEqual(off["verified_pdf_assets"], off["declared_public_pdf_assets"])
        self.assertEqual(off["blocking_failures"], 0)
        self.assertEqual(off["failures"], 0)
        self.assertGreaterEqual(off["no_public_asset_declared"], 0)''')

    text=rep(text,
'''        self.assertEqual(self.upstream_watch["status"], "CHANGE_DETECTED")
        self.assertEqual(
            self.upstream_watch["change_summary"]["github_sources_changed"],
            ["BSDATA_WH40K_11E","BSDATA_MFM_11E"],
        )
        self.assertEqual(self.upstream_watch["change_summary"]["wahapedia_files_changed"], 0)
        self.assertFalse(self.upstream_watch["change_summary"]["wahapedia_last_update_changed"])
        self.assertFalse(self.upstream_watch["policy"]["auto_promote"])

        self.assertEqual(self.nr_runtime["schema_version"], "2.0")''',
'''        self.assertEqual(self.upstream_watch["status"], "NO_CHANGE")
        self.assertEqual(self.upstream_watch["change_summary"].get("official_sources_changed", []), [])
        self.assertEqual(self.upstream_watch["change_summary"]["github_sources_changed"], [])
        self.assertEqual(self.upstream_watch["change_summary"]["wahapedia_files_changed"], 0)
        self.assertFalse(self.upstream_watch["change_summary"]["wahapedia_last_update_changed"])
        self.assertFalse(self.upstream_watch["policy"]["auto_promote"])

        self.assertEqual(self.nr_runtime["schema_version"], "2.1")''')

    text=rep(text,
'''        self.assertEqual(watch["state"], "ACTIVE_CHANGE_DETECTED")
        self.assertFalse(watch["auto_promote"])
        self.assertEqual(watch["bsdata_wh40k_11e"]["live"], "374f50544f0274296ab53c2103766ae3945e8799")
        self.assertTrue(watch["bsdata_wh40k_11e"]["changed"])
        self.assertEqual(watch["bsdata_mfm_11e"]["live"], "c3ddc8ce1884877c9ad8f08224667d1cdb5bd390")
        self.assertTrue(watch["bsdata_mfm_11e"]["changed"])
        self.assertTrue(watch["bsdata_mfm_11e"]["normative_mfm_data_change_not_inferred"])''',
'''        self.assertEqual(watch["state"], "ACTIVE_NO_CHANGE")
        self.assertFalse(watch["auto_promote"])
        upstream_rows={x["source_id"]:x for x in self.upstream_watch["github_sources"]}
        self.assertEqual(watch["bsdata_wh40k_11e"]["live"], upstream_rows["BSDATA_WH40K_11E"]["live"])
        self.assertFalse(watch["bsdata_wh40k_11e"]["changed"])
        self.assertEqual(watch["bsdata_mfm_11e"]["live"], upstream_rows["BSDATA_MFM_11E"]["live"])
        self.assertFalse(watch["bsdata_mfm_11e"]["changed"])
        self.assertIn(watch["bsdata_mfm_11e"]["relation"], {"behind","identical"})''')

    PATH.write_text(text,encoding='utf-8')
    print('rules refresh regression tests patched')
    return 0

if __name__=='__main__':
    raise SystemExit(main())
