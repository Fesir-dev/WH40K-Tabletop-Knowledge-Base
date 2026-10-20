#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "tools" / "validate_repo.py"


def replace_once(text: str, old: str, new: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Expected exactly one validation-contract match, found {count}: {old[:120]!r}")
    return text.replace(old, new, 1)


def main() -> int:
    text = PATH.read_text(encoding="utf-8")

    text = replace_once(
        text,
        '''    if off.get("verified_pdf_assets") != off.get("pdf_assets"):\n        errors.append("Not all referenced official faction-pack PDFs are verified")''',
        '''    declared_public = off.get("declared_public_pdf_assets", off.get("pdf_assets"))\n    if off.get("verified_pdf_assets") != declared_public:\n        errors.append("Not all declared public official faction-pack PDFs are verified")\n    if int(off.get("blocking_failures", off.get("failures", 0))) != 0:\n        errors.append("Official public asset audit contains blocking failures")\n    # Codex/app-only sources may legitimately have no public PDF. Keep them as explicit\n    # authority gaps rather than treating an absent public asset as a broken PDF.\n    if int(off.get("no_public_asset_declared", 0)) < 0:\n        errors.append("Official public-asset gap count is invalid")'''
    )

    text = replace_once(
        text,
        '''    if nr_runtime.get("schema_version") != "2.0":\n        errors.append("New Recruit runtime report schema must be 2.0")''',
        '''    if nr_runtime.get("schema_version") != "2.1":\n        errors.append("New Recruit runtime report schema must be 2.1")'''
    )

    text = replace_once(
        text,
        '''    changed_sources = summary.get("github_sources_changed", [])\n    if watch_status == "NO_CHANGE" and changed_sources:\n        errors.append("Upstream watcher says NO_CHANGE but GitHub source changes are listed")\n    if watch_status == "CHANGE_DETECTED" and not changed_sources and not summary.get("wahapedia_files_changed") and not summary.get("wahapedia_last_update_changed"):\n        errors.append("Upstream watcher says CHANGE_DETECTED without any classified source change")''',
        '''    changed_sources = summary.get("github_sources_changed", [])\n    official_changed = summary.get("official_sources_changed", [])\n    if watch_status == "NO_CHANGE" and (changed_sources or official_changed):\n        errors.append("Upstream watcher says NO_CHANGE but source changes are listed")\n    if watch_status == "CHANGE_DETECTED" and not changed_sources and not official_changed and not summary.get("wahapedia_files_changed") and not summary.get("wahapedia_last_update_changed"):\n        errors.append("Upstream watcher says CHANGE_DETECTED without any classified source change")'''
    )

    old = '''    if watch_status == "CHANGE_DETECTED":\n        if current_watch.get("bsdata_wh40k_11e", {}).get("live") != "374f50544f0274296ab53c2103766ae3945e8799":\n            errors.append("Current rules live BSData revision differs from detected upstream head")\n        if current_watch.get("bsdata_mfm_11e", {}).get("live") != "c3ddc8ce1884877c9ad8f08224667d1cdb5bd390":\n            errors.append("Current rules live MFM extractor revision differs from detected upstream head")'''
    new = '''    watch_rows = {x.get("source_id"): x for x in upstream_watch.get("github_sources", [])}\n    for source_id, key in (("BSDATA_WH40K_11E", "bsdata_wh40k_11e"), ("BSDATA_MFM_11E", "bsdata_mfm_11e")):\n        row = watch_rows.get(source_id, {})\n        current_row = current_watch.get(key, {})\n        for field in ("pinned", "live", "changed"):\n            if current_row.get(field) != row.get(field):\n                errors.append(f"Current rules {key}.{field} differs from upstream watch report")\n        if current_row.get("relation") != row.get("relation_from_pinned_to_live"):\n            errors.append(f"Current rules {key}.relation differs from upstream watch report")\n    waha_watch = upstream_watch.get("wahapedia", {})\n    current_waha = current_watch.get("wahapedia", {})\n    if current_waha.get("manifest_files_checked") != waha_watch.get("manifest_files_checked"):\n        errors.append("Current rules Wahapedia watch manifest count differs from report")\n    if current_waha.get("changed_files") != len(waha_watch.get("changed_files", [])):\n        errors.append("Current rules Wahapedia changed-file count differs from report")'''
    text = replace_once(text, old, new)

    PATH.write_text(text, encoding="utf-8")
    print("rules refresh validation contracts patched")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
