#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
gate = json.loads((ROOT / "sources" / "currentness_gate.json").read_text(encoding="utf-8"))

pending = [
    check["id"]
    for check in gate["required_checks"]
    if check["authority"] == "official_primary" and check["state"] != "PASS"
]

if pending:
    print("CURRENT_PENDING_RECHECK")
    for source_id in pending:
        print("-", source_id)
    raise SystemExit(2)

print("Official-primary currentness gate PASS")
