#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

from build_official_public_semantic_fingerprints import (
    build_sources,
    download,
    normalize_text as fingerprint_normalize,
)

ROOT = Path(__file__).resolve().parents[1]
CORE_ID = "GW_11E_CORE_RULES_PUBLIC"
STRUCTURE_VERSION = "CORE_RULES_SECTION_STRUCTURE_V1"


class SourceDrift(RuntimeError):
    pass


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def clean_short_label(value: str | None) -> str:
    value = unicodedata.normalize("NFKC", value or "")
    value = value.replace("\u00ad", "")
    value = " ".join(value.split()).strip()
    return value[:160]


def slug(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.casefold()
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value[:80] or "section"


def is_heading_candidate(line: str) -> bool:
    line = clean_short_label(line)
    if not line or len(line) < 3 or len(line) > 120:
        return False
    if re.fullmatch(r"\d{1,3}", line):
        return False
    tokens = line.split()
    if len(tokens) > 14:
        return False
    if line.endswith((".", ";", ",")):
        return False
    alpha = [ch for ch in line if ch.isalpha()]
    if not alpha:
        return False
    upper_ratio = sum(ch.isupper() for ch in alpha) / len(alpha)
    titleish = sum(tok[:1].isupper() for tok in tokens if tok[:1].isalpha()) >= max(1, len(tokens) - 1)
    numbered = bool(re.match(r"^(?:\d+|[A-Z])(?:[.)]|\s)", line))
    return upper_ratio >= 0.72 or titleish or numbered


def heading_candidates(page_texts: list[str]) -> dict[int, list[str]]:
    raw: dict[int, list[str]] = {}
    frequency = Counter()
    for page_no, text in enumerate(page_texts, 1):
        seen = set()
        rows = []
        for line in text.splitlines():
            label = clean_short_label(line)
            if label in seen or not is_heading_candidate(label):
                continue
            seen.add(label)
            rows.append(label)
            frequency[label] += 1
        raw[page_no] = rows[:16]

    filtered = {}
    for page_no, rows in raw.items():
        # Repeated running headers/footers are not structural evidence.
        filtered[page_no] = [x for x in rows if frequency[x] <= 4][:10]
    return filtered


def flatten_outline(reader) -> list[dict]:
    rows: list[dict] = []

    def walk(items, depth: int):
        for item in items or []:
            if isinstance(item, list):
                walk(item, depth + 1)
                continue
            title = clean_short_label(getattr(item, "title", str(item)))
            if not title:
                continue
            try:
                page = reader.get_destination_page_number(item) + 1
            except Exception:
                continue
            rows.append({"title": title, "depth": depth, "page_start": page})

    try:
        walk(reader.outline, 0)
    except Exception:
        return []
    return rows


def dedupe_outline(rows: list[dict], page_count: int) -> list[dict]:
    out = []
    seen = set()
    for row in rows:
        page = int(row["page_start"])
        if page < 1 or page > page_count:
            continue
        key = (row["title"], int(row["depth"]), page)
        if key in seen:
            continue
        seen.add(key)
        out.append({"title": row["title"], "depth": int(row["depth"]), "page_start": page})
    return out


def assign_ranges(rows: list[dict], page_count: int, page_semantic_sha: list[str], candidates: dict[int, list[str]]) -> list[dict]:
    sections = []
    for idx, row in enumerate(rows):
        depth = row["depth"]
        start = row["page_start"]
        end = page_count
        for later in rows[idx + 1:]:
            if later["depth"] <= depth:
                end = max(start, later["page_start"] - 1)
                break
        key = f"{slug(row['title'])}--d{depth}--p{start}--n{idx+1}"
        evidence = []
        for label in candidates.get(start, []):
            if slug(row["title"]) in slug(label) or slug(label) in slug(row["title"]):
                evidence.append({"page": start, "label": label, "label_sha256": sha256_text(label)})
        sections.append({
            "section_key": key,
            "title": row["title"],
            "depth": depth,
            "page_start": start,
            "page_end": end,
            "page_range_sha256": sha256_text("\n".join(page_semantic_sha[start - 1:end])),
            "children": [],
            "outline_source": True,
            "heading_evidence": evidence[:4],
        })

    for idx, section in enumerate(sections):
        d = section["depth"]
        children = []
        for later in sections[idx + 1:]:
            if later["depth"] <= d:
                break
            if later["depth"] == d + 1:
                children.append(later["section_key"])
        section["children"] = children
    return sections


def fallback_sections(page_count: int, page_semantic_sha: list[str], candidates: dict[int, list[str]]) -> list[dict]:
    anchors = []
    for page, labels in candidates.items():
        for label in labels[:2]:
            anchors.append((page, label))
            break
    if not anchors:
        raise RuntimeError("No PDF outline and no conservative heading candidates")
    rows = [{"title": label, "depth": 0, "page_start": page} for page, label in anchors]
    rows.sort(key=lambda x: x["page_start"])
    return assign_ranges(rows, page_count, page_semantic_sha, candidates)


def build_snapshot(as_of: str, cache_dir: Path, root: Path = ROOT) -> dict:
    try:
        from pypdf import PdfReader
    except Exception as exc:
        raise RuntimeError("pypdf 5.9.0 is required") from exc

    fp = load(root / "reports" / "OFFICIAL_PUBLIC_RULES_SEMANTIC_FINGERPRINT_CURRENT.json")
    expected = next((x for x in fp.get("documents", []) if x.get("document_id") == CORE_ID), None)
    if not expected:
        raise RuntimeError("Committed Core Rules fingerprint evidence is missing")

    source = next((x for x in build_sources() if x["document_id"] == CORE_ID), None)
    if not source:
        raise RuntimeError("Core Rules source registration is missing")

    cache_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = cache_dir / "core_rules_11e.pdf"
    if pdf_path.exists():
        raw = pdf_path.read_bytes()
        if sha256_bytes(raw) != expected["binary_sha256"]:
            pdf_path.unlink()
            raw = download(source["url"])
            pdf_path.write_bytes(raw)
    else:
        raw = download(source["url"])
        pdf_path.write_bytes(raw)

    binary_sha = sha256_bytes(raw)
    if binary_sha != expected["binary_sha256"]:
        raise SourceDrift(f"Core Rules binary drift: {binary_sha} != {expected['binary_sha256']}")

    reader = PdfReader(str(pdf_path))
    page_texts = [(page.extract_text() or "") for page in reader.pages]
    if len(page_texts) != expected["page_count"]:
        raise SourceDrift("Core Rules page count drift")

    normalized_pages = [fingerprint_normalize(x) for x in page_texts]
    page_sha = [sha256_text(x) for x in normalized_pages]
    expected_pages = expected.get("pages", [])
    if len(expected_pages) != len(page_sha):
        raise SourceDrift("Committed Core Rules page evidence length drift")
    for idx, digest in enumerate(page_sha):
        if digest != expected_pages[idx].get("semantic_sha256"):
            raise SourceDrift(f"Core Rules page semantic drift at page {idx + 1}")

    document_semantic = "\n\n".join(normalized_pages)
    if sha256_text(document_semantic) != expected["semantic_sha256"]:
        raise SourceDrift("Core Rules document semantic drift")

    candidates = heading_candidates(page_texts)
    outline = dedupe_outline(flatten_outline(reader), len(page_texts))
    if outline:
        sections = assign_ranges(outline, len(page_texts), page_sha, candidates)
        mode = "PDF_OUTLINE_PRIMARY"
    else:
        sections = fallback_sections(len(page_texts), page_sha, candidates)
        mode = "HEADING_CANDIDATE_FALLBACK"

    depth_counts = Counter(str(x["depth"]) for x in sections)
    pages_represented = sorted({p for s in sections for p in range(s["page_start"], s["page_end"] + 1)})
    heading_pages = sum(bool(v) for v in candidates.values())

    return {
        "schema_version": "1.0",
        "status": "PASS",
        "snapshot_date": as_of,
        "authority": "GAMES_WORKSHOP_OFFICIAL",
        "structure_version": STRUCTURE_VERSION,
        "document": {
            "document_id": CORE_ID,
            "title": "Warhammer 40,000 Core Rules",
            "binary_sha256": binary_sha,
            "semantic_sha256": expected["semantic_sha256"],
            "page_count": len(page_texts),
            "source_url": source["url"],
        },
        "source_verification": {
            "binary_sha256_match": True,
            "page_semantic_fingerprints_match": len(page_sha),
            "document_semantic_sha256_match": True,
            "fingerprint_report": "reports/OFFICIAL_PUBLIC_RULES_SEMANTIC_FINGERPRINT_CURRENT.json",
        },
        "structure_mode": mode,
        "sections": sections,
        "summary": {
            "sections": len(sections),
            "root_sections": sum(x["depth"] == 0 for x in sections),
            "max_depth": max((x["depth"] for x in sections), default=0),
            "sections_by_depth": dict(sorted(depth_counts.items(), key=lambda x: int(x[0]))),
            "pages_represented": len(pages_represented),
            "heading_candidate_pages": heading_pages,
            "heading_candidate_count": sum(len(v) for v in candidates.values()),
        },
        "authority_boundary": {
            "section_level_structure_complete_for_public_pdf": True,
            "paragraph_level_rules_ast_complete": False,
            "app_codex_equivalence": "NOT_CLAIMED",
            "full_faction_promotion": False,
            "current_normalized_factions_change": 0,
            "copyright_policy": "Short headings, hierarchy, page ranges and hashes only; no long rules prose committed.",
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--as-of", default="2026-09-30")
    ap.add_argument("--output", type=Path, default=Path("rules/11e/snapshots/2026-09-30/core_rules_structure/index.json"))
    ap.add_argument("--summary-output", type=Path, default=Path("reports/CORE_RULES_STRUCTURE_CURRENT.json"))
    ap.add_argument("--cache-dir", type=Path, default=ROOT / ".cache" / "official-public-rules")
    args = ap.parse_args()

    out = args.output if args.output.is_absolute() else ROOT / args.output
    summary_out = args.summary_output if args.summary_output.is_absolute() else ROOT / args.summary_output

    try:
        snapshot = build_snapshot(args.as_of, args.cache_dir)
    except SourceDrift as exc:
        failure = {
            "schema_version": "1.0",
            "status": "SOURCE_DRIFT",
            "snapshot_date": args.as_of,
            "authority": "GAMES_WORKSHOP_OFFICIAL",
            "error": str(exc),
            "authority_boundary": {"fail_closed": True, "structure_promoted": False},
        }
        summary_out.parent.mkdir(parents=True, exist_ok=True)
        summary_out.write_text(json.dumps(failure, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(failure, ensure_ascii=False))
        return 2

    out.parent.mkdir(parents=True, exist_ok=True)
    summary_out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    compact = {
        "schema_version": snapshot["schema_version"],
        "status": snapshot["status"],
        "snapshot_date": snapshot["snapshot_date"],
        "authority": snapshot["authority"],
        "structure_version": snapshot["structure_version"],
        "document": snapshot["document"],
        "source_verification": snapshot["source_verification"],
        "structure_mode": snapshot["structure_mode"],
        "summary": snapshot["summary"],
        "root_sections": [
            {
                "section_key": x["section_key"],
                "title": x["title"],
                "page_start": x["page_start"],
                "page_end": x["page_end"],
                "children": len(x["children"]),
            }
            for x in snapshot["sections"] if x["depth"] == 0
        ],
        "authority_boundary": snapshot["authority_boundary"],
    }
    summary_out.write_text(json.dumps(compact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "summary": snapshot["summary"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
