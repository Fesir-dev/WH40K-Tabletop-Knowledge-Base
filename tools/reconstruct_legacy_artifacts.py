#!/usr/bin/env python3
from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "legacy" / "artifacts"
MANIFEST = json.loads((BASE / "artifact_reconstruction_manifest.json").read_text(encoding="utf-8"))

OUT = ROOT / ".reconstructed_legacy"
OUT.mkdir(exist_ok=True)

for artifact in MANIFEST["artifacts"]:
    chunk_dir = BASE / artifact["id"]
    pieces: list[str] = []
    for chunk in artifact["chunks"]:
        path = chunk_dir / chunk["file"]
        text = path.read_text(encoding="ascii")
        got_text_sha = hashlib.sha256(text.encode("ascii")).hexdigest()
        if got_text_sha != chunk["sha256_text"]:
            raise SystemExit(f"Chunk checksum mismatch: {path}")
        if len(text) != chunk["chars"]:
            raise SystemExit(f"Chunk length mismatch: {path}")
        pieces.append(text)

    payload = "".join(pieces)
    if len(payload) != artifact["base64_chars"]:
        raise SystemExit(f"Base64 length mismatch: {artifact['id']}")

    raw = base64.b64decode(payload, validate=True)
    got_sha = hashlib.sha256(raw).hexdigest()
    if got_sha != artifact["sha256"]:
        raise SystemExit(f"Artifact checksum mismatch: {artifact['id']}")
    if len(raw) != artifact["size_bytes"]:
        raise SystemExit(f"Artifact size mismatch: {artifact['id']}")

    target = OUT / artifact["original_filename"]
    target.write_bytes(raw)
    print(f"PASS {artifact['id']}: {target.name} {len(raw)} bytes {got_sha}")
