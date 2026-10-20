#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import urllib.error
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
LEGACY_VALIDATOR = ROOT / "tools" / "validate_new_recruit_runtime.py"
REPORT = ROOT / "reports" / "NEW_RECRUIT_RUNTIME_VALIDATION_CURRENT.json"


def load_validator():
    spec = importlib.util.spec_from_file_location("nr_runtime_legacy", LEGACY_VALIDATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {LEGACY_VALIDATOR}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def collect_named_points(module, data, unit_name):
    vals = []
    def walk(value):
        if isinstance(value, list):
            for item in value:
                walk(item)
        elif isinstance(value, dict):
            if module.norm(value.get("name")) == module.norm(unit_name):
                for cost in value.get("costs", []) or []:
                    if cost.get("name") == "pts":
                        try:
                            vals.append(int(cost.get("value")))
                        except Exception:
                            pass
            for item in value.values():
                walk(item)
    walk(data)
    return sorted(set(vals))


def install_library_aware_bsdata_points(module):
    original = module.bsdata_points
    def library_aware(roster_slug, unit_name, ref):
        value, filename = original(roster_slug, unit_name, ref)
        if value is not None:
            return value, filename
        cat = module.fetch_bsdata_catalog(roster_slug, ref)
        data = cat.get("data")
        if data is None:
            return None, filename
        catalogue = data.get("catalogue", {}) if isinstance(data, dict) else {}
        library_names = [link.get("name") for link in catalogue.get("catalogueLinks", []) or [] if link.get("name") and "Library" in link.get("name")]
        all_values, resolved_files = [], []
        for name in dict.fromkeys(library_names):
            lib_file = f"{name}.json"
            url = f"https://raw.githubusercontent.com/{module.BSDATA_REPO}/{ref}/{quote(lib_file)}"
            try:
                lib_data = module.fetch_json(url)
            except urllib.error.HTTPError as exc:
                if exc.code == 404:
                    continue
                raise
            vals = collect_named_points(module, lib_data, unit_name)
            if vals:
                all_values.extend(vals)
                resolved_files.append(lib_file)
        uniq = sorted(set(all_values))
        if len(uniq) == 1:
            return uniq[0], ";".join(resolved_files) or filename
        return None, ";".join(resolved_files) or filename
    module.bsdata_points = library_aware


def current_provenance(module):
    mfm = module.CURRENT_RULES.get("wave_a_mfm", {})
    waha_manifest = json.loads((module.WAHAPEDIA_ROOT / "manifest.json").read_text(encoding="utf-8"))
    return {"mfm_version": str(mfm.get("version")), "mfm_last_updated": mfm.get("last_updated"), "wahapedia_last_update": waha_manifest.get("source", {}).get("last_update")}


def normalize_report_provenance(module):
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    prov = current_provenance(module)
    def patch_record(rec):
        revisions = rec.get("source_revisions")
        if not isinstance(revisions, dict):
            return
        if isinstance(revisions.get("gw_mfm"), dict):
            revisions["gw_mfm"]["version"] = prov["mfm_version"]
            revisions["gw_mfm"]["official_last_updated"] = prov["mfm_last_updated"]
        if isinstance(revisions.get("wahapedia"), dict):
            revisions["wahapedia"]["last_update"] = prov["wahapedia_last_update"]
    points = report.get("representative_points", {})
    for key in ("rows", "known_drifts", "new_drifts"):
        for rec in points.get(key, []) or []:
            patch_record(rec)
    report.setdefault("provenance", {})["current_rules"] = {
        "mfm_version": prov["mfm_version"],
        "mfm_last_updated": prov["mfm_last_updated"],
        "wahapedia_last_update": prov["wahapedia_last_update"],
        "bsdata_revision": module.PINNED_BSDATA_COMMIT,
        "validator": "tools/validate_new_recruit_runtime_current.py",
        "legacy_validator": "tools/validate_new_recruit_runtime.py",
        "library_resolution": "ENABLED_FOR_IMPORTED_BSDATA_LIBRARIES",
    }
    report["schema_version"] = "2.1"
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main():
    module = load_validator()
    install_library_aware_bsdata_points(module)
    result = module.main()
    report = normalize_report_provenance(module)
    print(json.dumps({
        "status": report.get("status"),
        "new_point_drifts": report.get("representative_points", {}).get("new_drift_count"),
        "known_point_drifts": report.get("representative_points", {}).get("known_drift_count"),
        "mfm_version": report.get("provenance", {}).get("current_rules", {}).get("mfm_version"),
        "wahapedia_last_update": report.get("provenance", {}).get("current_rules", {}).get("wahapedia_last_update"),
    }, ensure_ascii=False))
    return result


if __name__ == "__main__":
    raise SystemExit(main())
