# Preserved legacy upload artifacts

The original uploaded ZIP archives are preserved exactly as base64 chunks because GitHub Contents writes text while the source artifacts are binary ZIP files.

Reconstruction is deterministic:

```bash
python tools/reconstruct_legacy_artifacts.py
```

The script concatenates the ordered `.b64` chunks, decodes them, writes the original ZIP and verifies its SHA-256 against `artifact_reconstruction_manifest.json`.

These artifacts are immutable historical evidence. Do not edit chunk files in place. New project state belongs in normalized/current repository domains.
