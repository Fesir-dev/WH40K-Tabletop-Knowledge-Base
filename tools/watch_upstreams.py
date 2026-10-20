#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURRENT = json.loads((ROOT / "rules" / "11e" / "current.json").read_text(encoding="utf-8"))
WAHA_INDEX = ROOT / CURRENT["wave_b_structural"]["snapshot"]
WROOT = WAHA_INDEX.parent.parent
REG = json.loads((ROOT / "sources" / "registry.json").read_text(encoding="utf-8"))
MAN = json.loads((WROOT / "manifest.json").read_text(encoding="utf-8"))
BY_ID = {x["id"]: x for x in REG["sources"]}
UA = {"User-Agent": "WH40K-Tabletop-Knowledge-Base/1.0"}
GW_DOWNLOADS = "https://www.warhammer-community.com/en-gb/downloads/warhammer-40000/"


def get_bytes(url, limit=40 * 1024 * 1024):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=90) as r:
        body = r.read(limit + 1)
        if len(body) > limit:
            raise RuntimeError("response too large: " + url)
        return body


def get_json(url):
    return json.loads(get_bytes(url).decode("utf-8"))


def github_head(repo):
    return get_json("https://api.github.com/repos/" + repo + "/branches/main")["commit"]["sha"]


def github_compare(repo, base, head):
    if base == head:
        return {"status": "identical", "files": []}
    url = "https://api.github.com/repos/" + repo + "/compare/" + urllib.parse.quote(base, safe="") + "..." + urllib.parse.quote(head, safe="")
    data = get_json(url)
    return {
        "status": data.get("status", "unknown"),
        "ahead_by": data.get("ahead_by"),
        "behind_by": data.get("behind_by"),
        "files": [
            {
                "filename": x.get("filename"),
                "status": x.get("status"),
                "additions": x.get("additions"),
                "deletions": x.get("deletions"),
                "changes": x.get("changes"),
            }
            for x in data.get("files", [])
        ],
    }


def classify_path(path):
    p = (path or "").casefold()
    if any(x in p for x in ["space marine", "black templar", "blood angel", "dark angel", "space wolves"]):
        return "ASTARTES"
    if p.startswith("data/"):
        return "MFM_DATA"
    if p.endswith(".json"):
        return "FACTION_OR_LIBRARY_DATA"
    if p.endswith(".md") or "readme" in p:
        return "DOCUMENTATION"
    if ".github/" in p:
        return "CI"
    return "OTHER"


def official_mfm_update() -> dict:
    body = get_bytes(GW_DOWNLOADS, 15 * 1024 * 1024)
    text = body.decode("utf-8", errors="replace")
    marker = text.casefold().find("munitorum field manual")
    if marker < 0:
        return {"state": "PARSE_FAILED", "reason": "MFM marker not found", "page_sha256": hashlib.sha256(body).hexdigest()}
    window = text[marker:marker + 12000]
    match = re.search(r"updated\s+(\d{1,2})/(\d{1,2})/(\d{4})", window, flags=re.IGNORECASE)
    if not match:
        return {"state": "PARSE_FAILED", "reason": "MFM updated date not found near marker", "page_sha256": hashlib.sha256(body).hexdigest()}
    day, month, year = map(int, match.groups())
    value = dt.date(year, month, day).isoformat()
    return {"state": "PASS", "updated_at": value, "page_sha256": hashlib.sha256(body).hexdigest(), "url": GW_DOWNLOADS}


def main():
    pinned_bs = BY_ID["BSDATA_WH40K_11E"]["observed_revision"]["commit_sha"]
    pinned_mfm = BY_ID["BSDATA_MFM_11E"]["observed_revision"]["commit_sha"]
    live_bs = github_head("BSData/wh40k-11e")
    live_mfm = github_head("BSData/wh40k-11e-mfm")

    github_sources = []
    for source_id, repo, pinned, live in [
        ("BSDATA_WH40K_11E", "BSData/wh40k-11e", pinned_bs, live_bs),
        ("BSDATA_MFM_11E", "BSData/wh40k-11e-mfm", pinned_mfm, live_mfm),
    ]:
        comparison = github_compare(repo, pinned, live)
        relation = comparison["status"]
        # A pinned reviewed commit may legitimately be ahead of upstream main (for example
        # an open automated MFM extraction PR). Only a live head that is ahead/diverged is new drift.
        changed = relation not in {"identical", "behind"}
        github_sources.append({
            "source_id": source_id,
            "repository": repo,
            "pinned": pinned,
            "live": live,
            "relation_from_pinned_to_live": relation,
            "ahead_by": comparison.get("ahead_by"),
            "behind_by": comparison.get("behind_by"),
            "changed": changed,
            "files": [dict(x, classification=classify_path(x["filename"])) for x in comparison.get("files", [])] if changed else [],
            "note": "LIVE_BEHIND_PINNED_REVIEWED_COMMIT" if relation == "behind" else None,
        })

    mfm_live = official_mfm_update()
    mfm_pinned_date = BY_ID["GW_MFM"].get("observed_revision", {}).get("updated_at")
    mfm_changed = mfm_live.get("state") != "PASS" or mfm_live.get("updated_at") != mfm_pinned_date
    official_sources = [{
        "source_id": "GW_MFM",
        "pinned_updated_at": mfm_pinned_date,
        "live_updated_at": mfm_live.get("updated_at"),
        "state": mfm_live.get("state"),
        "changed": mfm_changed,
        "page_sha256": mfm_live.get("page_sha256"),
        "url": mfm_live.get("url", GW_DOWNLOADS),
        "reason": mfm_live.get("reason"),
    }]

    waha_changes = []
    for rec in MAN["files"]:
        name = rec["name"]
        body = get_bytes("https://wahapedia.ru/wh40k11ed/" + name)
        sha = hashlib.sha256(body).hexdigest()
        if sha != rec["sha256"]:
            waha_changes.append({
                "file": name,
                "snapshot_sha256": rec["sha256"],
                "live_sha256": sha,
                "snapshot_bytes": rec["bytes"],
                "live_bytes": len(body),
            })

    last_body = get_bytes("https://wahapedia.ru/wh40k11ed/Last_update.csv").decode("utf-8-sig")
    lines = [x.strip() for x in last_body.splitlines() if x.strip()]
    live_last = lines[1].strip("|") if len(lines) > 1 else ""

    github_changed = [x["source_id"] for x in github_sources if x["changed"]]
    official_changed = [x["source_id"] for x in official_sources if x["changed"]]
    changed = bool(github_changed or official_changed or waha_changes or live_last != MAN["source"]["last_update"])
    report = {
        "schema_version": "1.1",
        "status": "CHANGE_DETECTED" if changed else "NO_CHANGE",
        "baseline_snapshot": str(WROOT.parent.name),
        "official_sources": official_sources,
        "github_sources": github_sources,
        "wahapedia": {
            "snapshot_last_update": MAN["source"]["last_update"],
            "live_last_update": live_last,
            "manifest_files_checked": len(MAN["files"]),
            "changed_files": waha_changes,
        },
        "change_summary": {
            "official_sources_changed": official_changed,
            "github_sources_changed": github_changed,
            "wahapedia_files_changed": len(waha_changes),
            "wahapedia_last_update_changed": live_last != MAN["source"]["last_update"],
        },
        "policy": {
            "auto_promote": False,
            "on_change": "Persist classified report, fail workflow, require ingestion/reconciliation/promotion pipeline.",
            "pinned_ahead_of_live_main": "Not drift by itself; preserve the reviewed pin until upstream main catches up or diverges.",
        },
    }
    out = ROOT / "reports" / "UPSTREAM_CHANGE_WATCH_CURRENT.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "summary": report["change_summary"]}, ensure_ascii=False, indent=2))
    return 2 if changed else 0


if __name__ == "__main__":
    raise SystemExit(main())
