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

ROOT=Path(__file__).resolve().parents[1]
SYSTEM_URL="https://www.newrecruit.eu/wiki/wh40k-11e/warhammer-40,000-11th-edition"
UA={"User-Agent":"WH40K-Tabletop-Knowledge-Base/1.0"}

EXPECTED={
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

SAMPLES=[
 ("adeptus_custodes","Trajann Valoris","adeptus-custodes",135),
 ("orks","Ghazghkull Thraka","orks",300),
 ("necrons","Imotekh The Stormlord","necrons",100),
 ("tau_empire","Commander Farsight","tau-empire",70),
 ("astra_militarum","Lord Solar Leontus","astra-militarum",130),
 ("chaos_space_marines","Abaddon The Despoiler","chaos-space-marines",295),
 ("tyranids","The Swarmlord","tyranids",210),
 ("aeldari_craftworlds","Avatar Of Khaine","aeldari",250),
 ("imperial_knights","Canis Rex","imperial-knights",415),
 ("leagues_of_votann","ûthar The Destined","leagues-of-votann",90),
]

def norm(v):
    v=unicodedata.normalize("NFKD",html.unescape(v or ""))
    v="".join(ch for ch in v if not unicodedata.combining(ch))
    v=v.replace("’","'").replace("‘","'")
    return " ".join(re.sub(r"[^a-z0-9]+"," ",v.casefold()).split())

class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links=[]; self.text=[]; self._href=None; self._parts=[]
    def handle_starttag(self,tag,attrs):
        if tag=="a":
            self._href=dict(attrs).get("href"); self._parts=[]
    def handle_data(self,data):
        if data.strip(): self.text.append(data.strip())
        if self._href is not None: self._parts.append(data)
    def handle_endtag(self,tag):
        if tag=="a" and self._href is not None:
            self.links.append((" ".join("".join(self._parts).split()),self._href))
            self._href=None; self._parts=[]

def fetch(url):
    req=urllib.request.Request(url,headers=UA)
    with urllib.request.urlopen(req,timeout=90) as r:
        body=r.read().decode("utf-8","replace")
        return getattr(r,"status",200),r.geturl(),body

def parse(url):
    status,final,body=fetch(url)
    p=PageParser(); p.feed(body)
    return status,final,p," ".join(p.text)

def link_map(parser,base):
    out={}
    for text,href in parser.links:
        if text and href:
            out.setdefault(norm(text),[]).append({"text":text,"url":urljoin(base,href)})
    return out

def main():
    status,final,p,text=parse(SYSTEM_URL)
    links=link_map(p,final)
    missing=[]; resolved={}
    for slug,label in EXPECTED.items():
        hits=links.get(norm(label),[])
        if not hits:
            missing.append({"slug":slug,"label":label})
        else:
            resolved[slug]=hits[0]

    catalogue_count=None
    m=re.search(r"Catalogues\s*\((\d+)\)",text,re.I)
    if m: catalogue_count=int(m.group(1))
    library_count=None
    m=re.search(r"Libraries\s*\((\d+)\)",text,re.I)
    if m: library_count=int(m.group(1))

    page_checks=[]
    for slug,hit in sorted(resolved.items()):
        st,fu,pp,pt=parse(hit["url"])
        marker="(Library)" if slug=="unaligned_forces" else "(Catalogue)"
        page_checks.append({
            "slug":slug,"label":EXPECTED[slug],"url":fu,"http_status":st,
            "page_type_marker":marker,"marker_present":marker.casefold() in pt.casefold(),
        })

    cost_checks=[]
    for roster_slug,unit_name,mfm_slug,expected_points in SAMPLES:
        cat=resolved.get(roster_slug)
        if not cat:
            cost_checks.append({"slug":roster_slug,"unit":unit_name,"status":"CATALOGUE_MISSING"})
            continue
        st,fu,pp,pt=parse(cat["url"])
        lm=link_map(pp,fu)
        hits=lm.get(norm(unit_name),[])
        if not hits:
            cost_checks.append({"slug":roster_slug,"unit":unit_name,"expected_points":expected_points,"status":"UNIT_LINK_MISSING"})
            continue
        ust,ufu,up,ut=parse(hits[0]["url"])
        cm=re.search(r"Costs:\s*(\d+)\s*pts\b",ut,re.I)
        actual=int(cm.group(1)) if cm else None
        cost_checks.append({
            "slug":roster_slug,"unit":unit_name,"url":ufu,"http_status":ust,
            "expected_points":expected_points,"runtime_points":actual,
            "status":"MATCH" if actual==expected_points else "MISMATCH",
        })

    page_fail=[x for x in page_checks if x["http_status"]!=200 or not x["marker_present"]]
    cost_fail=[x for x in cost_checks if x["status"]!="MATCH"]
    ok=(status==200 and catalogue_count==36 and not missing and not page_fail and not cost_fail)

    report={
        "schema_version":"1.0",
        "status":"PASS" if ok else "RUNTIME_PROJECTION_DRIFT",
        "system":{
            "url":final,"http_status":status,
            "catalogues_reported":catalogue_count,
            "libraries_reported":library_count,
        },
        "universe":{
            "expected_roster_identities":37,
            "resolved_runtime_identities":len(resolved),
            "missing":missing,
            "page_checks":page_checks,
        },
        "representative_points":{
            "checks":len(cost_checks),
            "matched":sum(1 for x in cost_checks if x["status"]=="MATCH"),
            "failures":cost_fail,
            "rows":cost_checks,
        },
        "lineage":{
            "runtime_source":"NEW_RECRUIT_WIKI",
            "expected_upstream":"BSDATA_WH40K_11E",
            "pinned_bsdata_commit":"951d5900d1b4a952a4ba560a30c43788e622ccfc",
            "exact_sync_cadence":"UNKNOWN_NOT_INFERRED",
        },
        "policy":{
            "meaning":"Validates public New Recruit runtime/wiki projection, roster-universe presence and representative current MFM points.",
            "not_claimed":"Does not prove every builder constraint or the undocumented BSData-to-New-Recruit synchronization interval.",
        },
    }
    out=ROOT/"reports"/"NEW_RECRUIT_RUNTIME_VALIDATION_CURRENT.json"
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":report["status"],"resolved":len(resolved),"catalogues":catalogue_count,"point_matches":report["representative_points"]["matched"]},ensure_ascii=False,indent=2))
    return 0 if ok else 2

if __name__=="__main__":
    raise SystemExit(main())
