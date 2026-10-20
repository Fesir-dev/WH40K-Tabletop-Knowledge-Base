#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "OFFICIAL_PUBLIC_MIRROR_OVERLAP_CURRENT.json"
SUMMARY = ROOT / "reports" / "OFFICIAL_PUBLIC_MIRROR_OVERLAP_SUMMARY_CURRENT.json"
SNAPSHOT = ROOT / "rules" / "11e" / "snapshots" / "2026-09-30" / "official_public_overlap" / "index.json"

EXPECTED = {
    "official_documents": 29,
    "core_rules": 1,
    "faction_packs": 28,
    "mirror_units": 13572,
    "exact_public_overlap_units": 5636,
    "promotable_scoped_units": 4070,
    "unscoped_exact_units": 1566,
    "no_exact_overlap_units": 7936,
    "official_pages": 1430,
    "official_pages_with_overlap": 1268,
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    report = load(REPORT)
    compact = load(SUMMARY)
    snap = load(SNAPSHOT)

    assert report.get("status") == "PASS", report.get("status")
    assert report.get("as_of") == "2026-09-30", report.get("as_of")
    assert compact.get("status") == "PASS", compact.get("status")
    assert compact.get("as_of") == "2026-09-30", compact.get("as_of")
    assert snap.get("status") == "PASS", snap.get("status")
    assert snap.get("authority") == "GAMES_WORKSHOP_OFFICIAL_PUBLIC_OVERLAP"
    assert snap.get("scope") == "EXACT_PUBLIC_OVERLAP_ONLY"

    summary = report.get("summary", {})
    compact_summary = compact.get("summary", {})
    for key, value in EXPECTED.items():
        assert summary.get(key) == value, (key, summary.get(key), value)
        assert compact_summary.get(key) == value, (key, compact_summary.get(key), value)

    assert snap.get("summary", {}).get("units") == EXPECTED["promotable_scoped_units"]
    assert report.get("authority_boundary", {}).get("full_codex_app_equivalence_claimed") is False
    assert report.get("authority_boundary", {}).get("faction_pack_is_full_codex_replacement") is False
    assert report.get("authority_boundary", {}).get("app_only_wording_inferred") is False
    assert snap.get("authority_boundary", {}).get("full_faction_current_verified") is False
    assert snap.get("authority_boundary", {}).get("current_normalized_factions_change") == 0
    assert snap.get("authority_boundary", {}).get("full_codex_app_equivalence") == "NOT_CLAIMED"

    for key in ("milestone", "by_kind", "documents", "authority_boundary", "source_state", "promotion_policy"):
        assert compact.get(key) == report.get(key), key

    forbidden = {"text", "description", "rules_text", "official_text", "mirror_text"}

    def walk(value):
        if isinstance(value, dict):
            for key, child in value.items():
                assert key not in forbidden, f"long-text field forbidden: {key}"
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(report)
    walk(snap)

    print(json.dumps({
        "status": "PASS",
        "as_of": "2026-09-30",
        "mirror_units": EXPECTED["mirror_units"],
        "promotable_scoped_units": EXPECTED["promotable_scoped_units"],
        "mode": "IMMUTABLE_CHECKPOINT_VALIDATION",
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
