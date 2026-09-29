#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlparse

ROOT=Path(__file__).resolve().parents[1]
MANIFESTS={
    "SPACE_MARINES_CODEX_2026": ROOT/"ingestion"/"release_transitions"/"space_marines_codex_2026.json",
    "ADEPTUS_CUSTODES_CODEX_2026": ROOT/"ingestion"/"release_transitions"/"adeptus_custodes_codex_2026.json",
}
OFFICIAL_HOST_SUFFIXES=("warhammer-community.com","warhammer.com","games-workshop.com")


def is_official_https(url:str)->bool:
    try:
        p=urlparse(url)
    except Exception:
        return False
    if p.scheme!="https" or not p.hostname:
        return False
    host=p.hostname.lower()
    return any(host==suffix or host.endswith("."+suffix) for suffix in OFFICIAL_HOST_SUFFIXES)


def main()->int:
    ap=argparse.ArgumentParser(description="Record explicit official current-legal evidence for a release transition. Never mutates rules/11e/current.json.")
    ap.add_argument("--transition-id",required=True,choices=sorted(MANIFESTS))
    ap.add_argument("--confirmed-at",required=True)
    ap.add_argument("--url",required=True)
    ap.add_argument("--published-at")
    ap.add_argument("--note",required=True)
    ap.add_argument("--authority",default="GAMES_WORKSHOP_OFFICIAL")
    ap.add_argument("--apply",action="store_true")
    args=ap.parse_args()

    if args.authority!="GAMES_WORKSHOP_OFFICIAL":
        raise SystemExit("Only GAMES_WORKSHOP_OFFICIAL evidence can activate a release transition.")
    if not is_official_https(args.url):
        raise SystemExit("Activation evidence URL must be an official HTTPS Games Workshop / Warhammer domain.")

    path=MANIFESTS[args.transition_id]
    data=json.loads(path.read_text(encoding="utf-8"))
    evidence={
        "authority":"GAMES_WORKSHOP_OFFICIAL",
        "url":args.url,
        "published_at":args.published_at,
        "confirmed_at":args.confirmed_at,
        "note":args.note,
    }
    proposal={
        "transition_id":args.transition_id,
        "manifest":str(path.relative_to(ROOT)),
        "activation_change":{
            "current_legal_confirmed":True,
            "confirmed_at":args.confirmed_at,
            "evidence_append":evidence,
        },
        "direct_current_rules_mutation":False,
        "next_required_step":"Run release-transition readiness evaluator; if upstream projection changed, route through guarded reingestion candidate.",
    }
    if not args.apply:
        print(json.dumps(proposal,ensure_ascii=False,indent=2))
        return 0

    activation=data.setdefault("activation_evidence",{})
    activation["current_legal_confirmed"]=True
    activation["confirmed_at"]=args.confirmed_at
    activation.setdefault("evidence",[]).append(evidence)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":"RECORDED","transition_id":args.transition_id,"manifest":str(path.relative_to(ROOT))},ensure_ascii=False))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
