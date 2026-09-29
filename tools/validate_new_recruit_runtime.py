#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
import unicodedata
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parents[1]
SYSTEM_URL = "https://www.newrecruit.eu/wiki/wh40k-11e/warhammer-40,000-11th-edition"
UA = {"User-Agent": "WH40K-Tabletop-Knowledge-Base/1.0"}

EXPECTED = {
    "chaos_daemons":"Chaos - Chaos Daemons",
    "chaos_knights":"Chaos - Chaos Knights",
    "chaos_space_marines":"Chaos - Chaos Space Marines",
    "death_guard":"Chaos - Death Guard",
    "emperors_children":"Chaos - Emperor's Children",
    "thousand_sons":"Chaos - Thousand Sons",
    "titanicus_traitoris":"Chaos - Titanicus Traitoris",
    "world_eaters":"Chaos - World Eaters",
    "adepta_sororitas":"Imperium - Adepta Sororitas",
    "black_templars":"Imperium - Adeptus Astartes - Black Templars",
    "blood_angels":"Imperium - Adeptus Astartes - Blood Angels",
    "dark_angels":"Imperium - Adeptus Astartes - Dark Angels",
    "deathwatch":"Imperium - Adeptus Astartes - Deathwatch",
    "imperial_fists":"Imperium - Adeptus Astartes - Imperial Fists",
    "iron_hands":"Imperium - Adeptus Astartes - Iron Hands",
    "raven_guard":"Imperium - Adeptus Astartes - Raven Guard",
    "salamanders":"Imperium - Adeptus Astartes - Salamanders",
    "space_marines":"Imperium - Adeptus Astartes - Space Marines",
    "space_wolves":"Imperium - Adeptus Astartes - Space Wolves",
    "ultramarines":"Imperium - Adeptus Astartes - Ultramarines",
    "white_scars":"Imperium - Adeptus Astartes - White Scars",
    "adeptus_custodes":"Imperium - Adeptus Custodes",
    "adeptus_mechanicus":"Imperium - Adeptus Mechanicus",
    "adeptus_titanicus":"Imperium - Adeptus Titanicus",
    "agents_of_the_imperium":"Imperium - Agents of the Imperium",
    "astra_militarum":"Imperium - Astra Militarum",
    "grey_knights":"Imperium - Grey Knights",
    "imperial_knights":"Imperium - Imperial Knights",
    "aeldari_craftworlds":"Xenos - Aeldari",
    "drukhari":"Xenos - Drukhari",
    "genestealer_cults":"Xenos - Genestealer Cults",
    "leagues_of_votann":"Xenos - Leagues of Votann",
    "necrons":"Xenos - Necrons",
    "orks":"Xenos - Orks",
    "tau_empire":"Xenos - T'au Empire",
    "tyranids":"Xenos - Tyranids",
    "unaligned_forces":"Unaligned Forces",
}

SAMPLES = [
    ("adeptus_custodes","Trajann Valoris","adeptus-custodes"),
    ("orks","Ghazghkull Thraka","orks"),
    ("necrons","Imotekh The Stormlord","necrons"),
    ("tau_empire","Commander Farsight","tau-empire"),
    ("astra_militarum","Lord Solar Leontus","astra-militarum"),
    ("chaos_space_marines","Abaddon The Despoiler","chaos-space-marines"),
    ("tyranids","The Swarmlord","tyranids"),
    ("aeldari_craftworlds","Avatar Of Khaine","aeldari"),
    ("imperial_knights","Canis Rex","imperial-knights"),
    ("leagues_of_votann","ûthar The Destined","leagues-of-votann"),
]

def norm(v):
    v = unicodedata.normalize("NFKD", html.unescape(v or ""))
    v = "".join(ch for ch in v if not unicodedata.combining(ch))
    v = v.replace("’", "'").replace("‘", "'")
    return " ".join(re.sub(r"[^a-z0-9]+", " ", v.casefold()).split())

class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.text = []
        self._href = None
        self._parts = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self._href = dict(attrs).get("href")
            self._parts = []

    def handle_data(self, data):
        if data.strip():
            self.text.append(data.strip())
        if self._href is not None:
            self._parts.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self._href is not None:
            self.links.append((" ".join("".join(self._parts).split()), self._href))
            self._href = None
            self._parts = []

def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=90) as r:
        body = r.read().decode("utf-8", "replace")
        return getattr(r, "status", 200), r.geturl(), body

def parse(url):
    status, final, body = fetch(url)
    p = PageParser()
    p.feed(body)
    return status, final, p, " ".join(p.text)

def link_map(parser, base):
    out = {}
    for text, href in parser.links:
        if text and href:
            out.setdefault(norm(text), []).append({"text": text, "url": urljoin(base, href)})
    return out

def expected_mfm_points(mfm_slug, unit_name):
    path = ROOT / "rules" / "11e" / "snapshots" / "2026-09-29" / "mfm" / "factions" / f"{mfm_slug}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    hits = [
        x for x in data.get("units", [])
        if norm(x.get("name")) == norm(unit_name) and not x.get("legends")
    ]
    if len(hits) != 1:
        raise RuntimeError(f"MFM sample resolution failed: {mfm_slug} / {unit_name}: {len(hits)}")
    costs = []
    for tier in hits[0].get("pricing", []):
        for row in tier.get("costs", []):
            try:
                costs.append((int(row["models"]), int(row["points"])))
            except Exception:
                pass
    if not costs:
        raise RuntimeError(f"MFM sample has no pricing: {mfm_slug} / {unit_name}")
    costs.sort()
    return costs[0][1]

def main():
    drift_doc = json.loads((ROOT / "sources" / "runtime_drift_registry.json").read_text(encoding="utf-8"))
    active = [x for x in drift_doc.get("active", []) if x.get("state") == "ACTIVE"]
    known_by = {
        (
            x["roster_slug"],
            norm(x["unit"]),
            int(x["normative"]["points"]),
            int(x["runtime"]["points"]),
        ): x
        for x in active
    }

    status, final, parser, text = parse(SYSTEM_URL)
    links = link_map(parser, final)

    missing = []
    resolved = {}
    for slug, label in EXPECTED.items():
        hits = links.get(norm(label), [])
        if not hits:
            missing.append({"slug": slug, "label": label})
        else:
            resolved[slug] = hits[0]

    m = re.search(r"Catalogues\s*\((\d+)\)", text, re.I)
    catalogue_count = int(m.group(1)) if m else None
    m = re.search(r"Libraries\s*\((\d+)\)", text, re.I)
    library_count = int(m.group(1)) if m else None

    page_checks = []
    for slug, hit in sorted(resolved.items()):
        st, url, page, page_text = parse(hit["url"])
        is_library = slug == "unaligned_forces"
        marker = "(Library)" if is_library else "(Catalogue)"
        marker_present = marker.casefold() in page_text.casefold()
        page_checks.append({
            "slug": slug,
            "label": EXPECTED[slug],
            "url": url,
            "http_status": st,
            "page_type_marker": marker,
            "marker_required": not is_library,
            "marker_present": marker_present,
            "status": "PASS" if st == 200 and (is_library or marker_present) else "FAIL",
        })

    cost_checks = []
    for roster_slug, unit_name, mfm_slug in SAMPLES:
        expected_points = expected_mfm_points(mfm_slug, unit_name)
        cat = resolved.get(roster_slug)
        if not cat:
            cost_checks.append({
                "slug": roster_slug,
                "unit": unit_name,
                "expected_points": expected_points,
                "status": "CATALOGUE_MISSING",
                "classification": "NEW_RUNTIME_PROJECTION_DRIFT",
            })
            continue

        st, url, page, page_text = parse(cat["url"])
        unit_links = link_map(page, url).get(norm(unit_name), [])
        if not unit_links:
            cost_checks.append({
                "slug": roster_slug,
                "unit": unit_name,
                "expected_points": expected_points,
                "status": "UNIT_LINK_MISSING",
                "classification": "NEW_RUNTIME_PROJECTION_DRIFT",
            })
            continue

        ust, unit_url, unit_page, unit_text = parse(unit_links[0]["url"])
        cm = re.search(r"Costs:\s*(\d+)\s*pts\b", unit_text, re.I)
        actual = int(cm.group(1)) if cm else None
        state = "MATCH" if actual == expected_points else "MISMATCH"
        rec = {
            "slug": roster_slug,
            "unit": unit_name,
            "url": unit_url,
            "http_status": ust,
            "expected_points": expected_points,
            "runtime_points": actual,
            "status": state,
        }
        if state == "MISMATCH":
            known = known_by.get((roster_slug, norm(unit_name), expected_points, actual))
            if known:
                rec["classification"] = "KNOWN_RUNTIME_PROJECTION_DRIFT"
                rec["known_drift_id"] = known["id"]
            else:
                rec["classification"] = "NEW_RUNTIME_PROJECTION_DRIFT"
        cost_checks.append(rec)

    page_fail = [x for x in page_checks if x["status"] != "PASS"]
    mismatches = [x for x in cost_checks if x["status"] != "MATCH"]
    known_matches = [x for x in mismatches if x.get("classification") == "KNOWN_RUNTIME_PROJECTION_DRIFT"]
    new_fail = [x for x in mismatches if x.get("classification") != "KNOWN_RUNTIME_PROJECTION_DRIFT"]

    observed_known = {x.get("known_drift_id") for x in known_matches}
    resolved_known = [
        {"id": x["id"], "classification": "RESOLVED_CANDIDATE"}
        for x in active
        if x["id"] not in observed_known
    ]

    hard_fail = bool(status != 200 or catalogue_count != 36 or missing or page_fail or new_fail)
    if hard_fail:
        overall = "NEW_RUNTIME_PROJECTION_DRIFT"
    elif known_matches:
        overall = "PASS_WITH_KNOWN_RUNTIME_DRIFT"
    else:
        overall = "PASS"

    report = {
        "schema_version": "1.1",
        "status": overall,
        "system": {
            "url": final,
            "http_status": status,
            "catalogues_reported": catalogue_count,
            "libraries_reported": library_count,
        },
        "universe": {
            "expected_roster_identities": 37,
            "resolved_runtime_identities": len(resolved),
            "missing": missing,
            "page_checks": page_checks,
        },
        "representative_points": {
            "checks": len(cost_checks),
            "matched": sum(1 for x in cost_checks if x["status"] == "MATCH"),
            "known_drift_count": len(known_matches),
            "new_drift_count": len(new_fail),
            "known_drifts": known_matches,
            "new_drifts": new_fail,
            "rows": cost_checks,
        },
        "known_drift_registry": {
            "path": "sources/runtime_drift_registry.json",
            "active": len(active),
            "resolved_candidates": resolved_known,
        },
        "lineage": {
            "runtime_source": "NEW_RECRUIT_WIKI",
            "expected_upstream": "BSDATA_WH40K_11E",
            "pinned_bsdata_commit": "951d5900d1b4a952a4ba560a30c43788e622ccfc",
            "exact_sync_cadence": "UNKNOWN_NOT_INFERRED",
        },
        "policy": {
            "meaning": "Validates New Recruit public runtime/wiki projection against the canonical repository MFM layer and the known runtime drift registry.",
            "known_drift_behavior": "Known exact drifts are reported but do not fail the scheduled workflow.",
            "new_drift_behavior": "New or changed runtime projection drift fails the workflow and requires classification.",
            "not_claimed": "Does not prove every builder constraint or the undocumented BSData-to-New-Recruit synchronization interval.",
        },
    }

    out = ROOT / "reports" / "NEW_RECRUIT_RUNTIME_VALIDATION_CURRENT.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": overall,
        "resolved": len(resolved),
        "catalogues": catalogue_count,
        "point_matches": report["representative_points"]["matched"],
        "known_drifts": len(known_matches),
        "new_drifts": len(new_fail),
    }, ensure_ascii=False, indent=2))
    return 2 if hard_fail else 0

if __name__ == "__main__":
    raise SystemExit(main())
