#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
import unicodedata
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, urljoin

ROOT = Path(__file__).resolve().parents[1]
SYSTEM_URL = "https://www.newrecruit.eu/wiki/wh40k-11e/warhammer-40,000-11th-edition"
UA = {"User-Agent": "WH40K-Tabletop-Knowledge-Base/1.0"}
CURRENT_RULES = json.loads((ROOT / "rules" / "11e" / "current.json").read_text(encoding="utf-8"))
SOURCE_REGISTRY = json.loads((ROOT / "sources" / "registry.json").read_text(encoding="utf-8"))
MFM_ROOT = (ROOT / CURRENT_RULES["wave_a_mfm"]["snapshot"]).parent
WAHAPEDIA_ROOT = (ROOT / CURRENT_RULES["wave_b_structural"]["snapshot"]).parent.parent
PINNED_BSDATA_COMMIT = next(
    x["observed_revision"]["commit_sha"]
    for x in SOURCE_REGISTRY["sources"]
    if x["id"] == "BSDATA_WH40K_11E"
)
BSDATA_REPO = "BSData/wh40k-11e"

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
    ("adeptus_custodes","Trajann Valoris","adeptus-custodes","named_character"),
    ("orks","Ghazghkull Thraka","orks","named_character"),
    ("necrons","Imotekh The Stormlord","necrons","named_character"),
    ("tau_empire","Commander Farsight","tau-empire","named_character"),
    ("astra_militarum","Lord Solar Leontus","astra-militarum","named_character"),
    ("chaos_space_marines","Abaddon The Despoiler","chaos-space-marines","named_character"),
    ("tyranids","The Swarmlord","tyranids","named_character_monster"),
    ("aeldari_craftworlds","Avatar Of Khaine","aeldari","named_character_monster"),
    ("imperial_knights","Canis Rex","imperial-knights","named_character_vehicle"),
    ("leagues_of_votann","ûthar The Destined","leagues-of-votann","named_character"),
    ("orks","Boyz","orks","infantry_multi_size"),
    ("orks","Battlewagon","orks","vehicle"),
    ("orks","Warboss","orks","leader"),
    ("necrons","Necron Warriors","necrons","infantry_multi_size"),
    ("necrons","Monolith","necrons","vehicle"),
]

SURFACE_CHECKS = [
    {
        "id": "ORKS_CURRENT_DETACHMENT_SHOOTA_BOYZ",
        "kind": "detachment_exists",
        "roster_slug": "orks",
        "entry": "Detachment",
        "expected": ["Shoota Boyz"],
    },
    {
        "id": "ORKS_WARBOSS_LEADER_BODYGUARDS",
        "kind": "leader_bodyguard_relation",
        "roster_slug": "orks",
        "unit": "Warboss",
        "expected": ["BOYZ", "BREAKA BOYZ", "NOBZ"],
    },
    {
        "id": "ORKS_TARGETIN_GIZMOS_ENHANCEMENT",
        "kind": "enhancement_exists",
        "roster_slug": "orks",
        "unit": "Warboss",
        "expected": ["Targetin' Gizmos"],
    },
    {
        "id": "ORKS_BATTLEWAGON_WARGEAR",
        "kind": "wargear_exists",
        "roster_slug": "orks",
        "unit": "Battlewagon",
        "expected": ["Wreckin' ball", "Grabbin' klaw"],
    },
    {
        "id": "ORKS_BOYZ_CONSTRAINT",
        "kind": "constraint_behavior",
        "roster_slug": "orks",
        "unit": "Boyz",
        "expected": ["max(force): 6"],
    },
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
    path = MFM_ROOT / "factions" / f"{mfm_slug}.json"
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


_FETCH_JSON_CACHE = {}
_BSDATA_FILE_CACHE = {}
_PARSE_CACHE = {}

def fetch_json(url):
    if url in _FETCH_JSON_CACHE:
        return _FETCH_JSON_CACHE[url]
    _, _, body = fetch(url)
    data = json.loads(body)
    _FETCH_JSON_CACHE[url] = data
    return data

def parse_cached(url):
    if url in _PARSE_CACHE:
        return _PARSE_CACHE[url]
    result = parse(url)
    _PARSE_CACHE[url] = result
    _PARSE_CACHE[result[1]] = result
    return result

def wahapedia_datasheet(roster_slug, unit_name):
    path = WAHAPEDIA_ROOT / "factions" / f"{roster_slug}.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    hits = [x for x in data.get("datasheets", []) if norm(x.get("name")) == norm(unit_name)]
    return hits[0] if len(hits) == 1 else None

def wahapedia_points(roster_slug, unit_name):
    ds = wahapedia_datasheet(roster_slug, unit_name)
    if not ds:
        return None
    vals = []
    for row in ds.get("points_rows", []):
        try:
            vals.append(int(row["cost"]))
        except Exception:
            pass
    return min(vals) if vals else None

def mfm_detachment_exists(mfm_slug, detachment_name):
    path = MFM_ROOT / "factions" / f"{mfm_slug}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    return any(norm(x.get("name")) == norm(detachment_name) for x in data.get("detachments", []))

def wahapedia_detachment_exists(roster_slug, detachment_name):
    path = WAHAPEDIA_ROOT / "factions" / f"{roster_slug}.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return any(norm(x.get("name")) == norm(detachment_name) for x in data.get("detachments", []))

def live_bsdata_head():
    data = fetch_json(f"https://api.github.com/repos/{BSDATA_REPO}/commits/main")
    return data.get("sha")

def bsdata_file_candidates(roster_slug):
    label = EXPECTED[roster_slug]
    candidates = [f"{label}.json"]
    for prefix in ("Xenos - ", "Imperium - ", "Chaos - "):
        if label.startswith(prefix):
            candidates.append(f"{label[len(prefix):]}.json")
    candidates.extend({
        "aeldari_craftworlds": ["Aeldari.json"],
        "tau_empire": ["T'au Empire.json"],
        "tyranids": ["Tyranids.json"],
        "necrons": ["Necrons.json"],
        "orks": ["Orks.json"],
    }.get(roster_slug, []))
    return list(dict.fromkeys(candidates))

def fetch_bsdata_catalog(roster_slug, ref):
    key = (roster_slug, ref)
    if key in _BSDATA_FILE_CACHE:
        return _BSDATA_FILE_CACHE[key]
    for filename in bsdata_file_candidates(roster_slug):
        url = f"https://raw.githubusercontent.com/{BSDATA_REPO}/{ref}/{quote(filename)}"
        try:
            data = fetch_json(url)
            result = {"filename": filename, "data": data}
            _BSDATA_FILE_CACHE[key] = result
            return result
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                continue
            raise
    result = {"filename": None, "data": None}
    _BSDATA_FILE_CACHE[key] = result
    return result

def bsdata_points(roster_slug, unit_name, ref):
    cat = fetch_bsdata_catalog(roster_slug, ref)
    data = cat.get("data")
    if data is None:
        return None, cat.get("filename")
    vals = []
    def walk(value):
        if isinstance(value, list):
            for item in value:
                walk(item)
        elif isinstance(value, dict):
            if norm(value.get("name")) == norm(unit_name):
                for cost in value.get("costs", []) or []:
                    if cost.get("name") == "pts":
                        try:
                            vals.append(int(cost.get("value")))
                        except Exception:
                            pass
            for item in value.values():
                walk(item)
    walk(data)
    uniq = sorted(set(vals))
    return (uniq[0] if len(uniq) == 1 else None), cat.get("filename")

def bsdata_contains(roster_slug, ref, target):
    cat = fetch_bsdata_catalog(roster_slug, ref)
    data = cat.get("data")
    if data is None:
        return None
    needle = norm(target)
    found = False
    def walk(value):
        nonlocal found
        if found:
            return
        if isinstance(value, list):
            for item in value:
                walk(item)
        elif isinstance(value, dict):
            for item in value.values():
                walk(item)
        elif isinstance(value, str) and norm(value) == needle:
            found = True
    walk(data)
    return found

def classify_points(mfm, waha, pinned, live, runtime):
    if runtime == mfm:
        return "NORMATIVE_MATCH"
    if waha == mfm and pinned != live and runtime == pinned and live == mfm:
        return "UPSTREAM_REVISION_DRIFT"
    if waha == mfm and pinned == runtime and live == runtime:
        return "IMPLEMENTATION_DRIFT"
    if waha == mfm and pinned == mfm and live == mfm:
        return "RUNTIME_PROJECTION_DRIFT"
    return "UNKNOWN_RUNTIME_DRIFT"

def recommendation(classification):
    return {
        "NORMATIVE_MATCH": "No action required.",
        "IMPLEMENTATION_DRIFT": "Do not change normative KB data. Investigate/fix BSData implementation and then verify downstream projection.",
        "RUNTIME_PROJECTION_DRIFT": "Do not change normative KB data. Investigate New Recruit projection/cache synchronization against current BSData.",
        "UPSTREAM_REVISION_DRIFT": "Do not change normative KB data. Run normal ingestion/reconciliation before moving the pinned revision, then verify runtime catch-up.",
        "UNKNOWN_RUNTIME_DRIFT": "Do not change normative KB data. Gather additional source-lineage evidence before assigning ownership.",
    }[classification]

def runtime_unit_page(resolved, roster_slug, unit_name):
    cat = resolved.get(roster_slug)
    if not cat:
        return None
    st, url, page, _ = parse_cached(cat["url"])
    hits = link_map(page, url).get(norm(unit_name), [])
    if not hits:
        return None
    return parse_cached(hits[0]["url"])

def runtime_surface_checks(resolved, live_head):
    rows = []
    for spec in SURFACE_CHECKS:
        slug = spec["roster_slug"]
        cat = resolved.get(slug)
        runtime_url = cat["url"] if cat else None
        observed_text = ""
        http_status = None
        if cat:
            if spec["kind"] == "detachment_exists":
                _, curl, cpage, _ = parse_cached(cat["url"])
                hits = link_map(cpage, curl).get(norm(spec["entry"]), [])
                if hits:
                    http_status, runtime_url, _, observed_text = parse_cached(hits[0]["url"])
            else:
                result = runtime_unit_page(resolved, slug, spec["unit"])
                if result:
                    http_status, runtime_url, _, observed_text = result
        observed_norm = norm(observed_text)
        matched = all(norm(x) in observed_norm for x in spec["expected"])
        rec = {
            "check_id": spec["id"],
            "kind": spec["kind"],
            "slug": slug,
            "unit": spec.get("unit"),
            "runtime_url": runtime_url,
            "http_status": http_status,
            "expected": spec["expected"],
            "status": "MATCH" if matched else "MISMATCH",
            "classification": "NORMATIVE_MATCH" if matched else "UNKNOWN_RUNTIME_DRIFT",
        }
        if not matched and spec["kind"] == "detachment_exists":
            target = spec["expected"][0]
            lineage = {
                "gw_mfm_present": mfm_detachment_exists("orks", target),
                "wahapedia_present": wahapedia_detachment_exists(slug, target),
                "pinned_bsdata_present": bsdata_contains(slug, PINNED_BSDATA_COMMIT, target),
                "live_bsdata_present": bsdata_contains(slug, live_head, target) if live_head else None,
                "new_recruit_runtime_present": False,
            }
            rec["lineage"] = lineage
            if all(lineage[k] is True for k in ("gw_mfm_present","wahapedia_present","pinned_bsdata_present","live_bsdata_present")):
                rec["classification"] = "RUNTIME_PROJECTION_DRIFT"
            rec["recommended_action"] = recommendation(rec["classification"])
            rec["normative_kb_change_required"] = False
        rows.append(rec)
    return rows

def main():
    drift_doc = json.loads((ROOT / "sources" / "runtime_drift_registry.json").read_text(encoding="utf-8"))
    active = [x for x in drift_doc.get("active", []) if x.get("state") == "ACTIVE"]
    known_points = {}
    known_surfaces = {}
    for x in active:
        if x.get("surface") == "points":
            known_points[(x["roster_slug"], norm(x["unit"]), int(x["normative"]["points"]), int(x["runtime"]["points"]))] = x
        elif x.get("surface") == "runtime_surface":
            known_surfaces[x["check_id"]] = x

    status, final, parser, text = parse_cached(SYSTEM_URL)
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
        st, url, page, page_text = parse_cached(hit["url"])
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

    try:
        live_head = live_bsdata_head()
    except Exception:
        live_head = None

    cost_checks = []
    for roster_slug, unit_name, mfm_slug, archetype in SAMPLES:
        expected_points = expected_mfm_points(mfm_slug, unit_name)
        cat = resolved.get(roster_slug)
        rec = {
            "slug": roster_slug,
            "unit": unit_name,
            "archetype": archetype,
            "gw_mfm_value": expected_points,
            "expected_points": expected_points,
        }
        if not cat:
            rec.update({
                "status": "CATALOGUE_MISSING",
                "classification": "UNKNOWN_RUNTIME_DRIFT",
                "recommended_action": recommendation("UNKNOWN_RUNTIME_DRIFT"),
                "normative_kb_change_required": False,
            })
            cost_checks.append(rec)
            continue

        st, url, page, _ = parse_cached(cat["url"])
        unit_links = link_map(page, url).get(norm(unit_name), [])
        if not unit_links:
            rec.update({
                "status": "UNIT_LINK_MISSING",
                "classification": "UNKNOWN_RUNTIME_DRIFT",
                "recommended_action": recommendation("UNKNOWN_RUNTIME_DRIFT"),
                "normative_kb_change_required": False,
            })
            cost_checks.append(rec)
            continue

        ust, unit_url, _, unit_text = parse_cached(unit_links[0]["url"])
        cm = re.search(r"Costs:\s*(\d+)\s*pts\b", unit_text, re.I)
        actual = int(cm.group(1)) if cm else None
        state = "MATCH" if actual == expected_points else "MISMATCH"
        rec.update({
            "url": unit_url,
            "http_status": ust,
            "new_recruit_runtime_value": actual,
            "runtime_points": actual,
            "status": state,
            "classification": "NORMATIVE_MATCH" if state == "MATCH" else "UNKNOWN_RUNTIME_DRIFT",
        })
        if state == "MISMATCH":
            waha = wahapedia_points(roster_slug, unit_name)
            pinned, pinned_file = bsdata_points(roster_slug, unit_name, PINNED_BSDATA_COMMIT)
            live, live_file = bsdata_points(roster_slug, unit_name, live_head) if live_head else (None, None)
            cls = classify_points(expected_points, waha, pinned, live, actual)
            rec.update({
                "wahapedia_value": waha,
                "pinned_bsdata_value": pinned,
                "live_bsdata_value": live,
                "source_revisions": {
                    "gw_mfm": {"version": "1.4", "official_last_updated": "2026-09-02"},
                    "wahapedia": {"last_update": "2026-09-28 02:38:04"},
                    "pinned_bsdata": {"revision": PINNED_BSDATA_COMMIT, "file": pinned_file},
                    "live_bsdata": {"revision": live_head, "file": live_file},
                    "new_recruit": {"exact_sync_cadence": "UNKNOWN_NOT_INFERRED"},
                },
                "classification": cls,
                "recommended_action": recommendation(cls),
                "normative_kb_change_required": False,
            })
            known = known_points.get((roster_slug, norm(unit_name), expected_points, actual))
            if known and known.get("classification") == cls:
                rec["registry_state"] = "KNOWN_ACTIVE"
                rec["known_drift_id"] = known["id"]
            else:
                rec["registry_state"] = "UNCLASSIFIED_OR_CHANGED"
        cost_checks.append(rec)

    surface_checks = runtime_surface_checks(resolved, live_head)
    for rec in surface_checks:
        if rec["status"] == "MISMATCH":
            known = known_surfaces.get(rec["check_id"])
            if known and known.get("classification") == rec.get("classification"):
                rec["registry_state"] = "KNOWN_ACTIVE"
                rec["known_drift_id"] = known["id"]
            else:
                rec["registry_state"] = "UNCLASSIFIED_OR_CHANGED"

    page_fail = [x for x in page_checks if x["status"] != "PASS"]
    point_mismatches = [x for x in cost_checks if x["status"] != "MATCH"]
    known_points_found = [x for x in point_mismatches if x.get("registry_state") == "KNOWN_ACTIVE"]
    new_points = [x for x in point_mismatches if x.get("registry_state") != "KNOWN_ACTIVE"]
    surface_mismatches = [x for x in surface_checks if x["status"] != "MATCH"]
    known_surfaces_found = [x for x in surface_mismatches if x.get("registry_state") == "KNOWN_ACTIVE"]
    new_surfaces = [x for x in surface_mismatches if x.get("registry_state") != "KNOWN_ACTIVE"]

    observed_known = {x.get("known_drift_id") for x in known_points_found + known_surfaces_found}
    resolved_known = [
        {"id": x["id"], "classification": "RESOLVED_CANDIDATE"}
        for x in active
        if x["id"] not in observed_known
    ]

    hard_fail = bool(status != 200 or catalogue_count != 36 or missing or page_fail or new_points or new_surfaces)
    known_total = len(known_points_found) + len(known_surfaces_found)
    if hard_fail:
        overall = "NEW_RUNTIME_PROJECTION_DRIFT"
    elif known_total:
        overall = "PASS_WITH_KNOWN_RUNTIME_DRIFT"
    else:
        overall = "PASS"

    report = {
        "schema_version": "2.0",
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
            "known_drift_count": len(known_points_found),
            "new_drift_count": len(new_points),
            "known_drifts": known_points_found,
            "new_drifts": new_points,
            "archetypes": sorted(set(x["archetype"] for x in cost_checks)),
            "rows": cost_checks,
        },
        "representative_surfaces": {
            "checks": len(surface_checks),
            "matched": sum(1 for x in surface_checks if x["status"] == "MATCH"),
            "known_drift_count": len(known_surfaces_found),
            "new_drift_count": len(new_surfaces),
            "known_drifts": known_surfaces_found,
            "new_drifts": new_surfaces,
            "rows": surface_checks,
        },
        "known_drift_registry": {
            "path": "sources/runtime_drift_registry.json",
            "active": len(active),
            "observed_active": len(observed_known),
            "resolved_candidates": resolved_known,
        },
        "lineage": {
            "runtime_source": "NEW_RECRUIT_WIKI",
            "expected_upstream": "BSDATA_WH40K_11E",
            "pinned_bsdata_commit": PINNED_BSDATA_COMMIT,
            "live_bsdata_commit": live_head,
            "exact_sync_cadence": "UNKNOWN_NOT_INFERRED",
        },
        "policy": {
            "meaning": "Validates New Recruit public runtime/wiki projection against canonical MFM points, current Wahapedia mirror data, pinned/live BSData values for mismatches, and selected structural runtime surfaces.",
            "classification_field": "classification uses NORMATIVE_MATCH, IMPLEMENTATION_DRIFT, RUNTIME_PROJECTION_DRIFT, UPSTREAM_REVISION_DRIFT, or UNKNOWN_RUNTIME_DRIFT. Registry state is separate.",
            "known_drift_behavior": "Known exact drifts are reported but do not fail the scheduled workflow.",
            "new_drift_behavior": "New or changed point/surface drift fails the workflow and requires classification.",
            "normative_guard": "Runtime mismatch never automatically changes normative Games Workshop/MFM data.",
            "not_claimed": "Does not prove every builder constraint or the undocumented BSData-to-New-Recruit synchronization interval.",
        },
    }

    out = ROOT / "reports" / "NEW_RECRUIT_RUNTIME_VALIDATION_CURRENT.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": overall,
        "resolved": len(resolved),
        "catalogues": catalogue_count,
        "point_checks": report["representative_points"]["checks"],
        "point_matches": report["representative_points"]["matched"],
        "known_point_drifts": len(known_points_found),
        "new_point_drifts": len(new_points),
        "surface_checks": report["representative_surfaces"]["checks"],
        "surface_matches": report["representative_surfaces"]["matched"],
        "known_surface_drifts": len(known_surfaces_found),
        "new_surface_drifts": len(new_surfaces),
        "live_bsdata_commit": live_head,
    }, ensure_ascii=False, indent=2))
    return 2 if hard_fail else 0

if __name__ == "__main__":
    raise SystemExit(main())
