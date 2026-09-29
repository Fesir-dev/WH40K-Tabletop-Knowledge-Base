import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))

from build_official_public_semantic_fingerprints import (  # noqa: E402
    build_sources,
    normalize_text,
    semantic_classes,
)


class OfficialPublicSemanticFingerprintContracts(unittest.TestCase):
    def test_public_corpus_is_core_plus_28_faction_packs(self):
        docs=build_sources()
        self.assertEqual(len(docs),29)
        self.assertEqual(sum(x["document_type"]=="CORE_RULES" for x in docs),1)
        self.assertEqual(sum(x["document_type"]=="FACTION_PACK" for x in docs),28)
        core=next(x for x in docs if x["document_type"]=="CORE_RULES")
        self.assertEqual(core["document_id"],"GW_11E_CORE_RULES_PUBLIC")
        self.assertIsNone(core["expected_binary_sha256"])
        self.assertTrue(core["url"].startswith("https://assets.warhammer-community.com/"))
        packs=[x for x in docs if x["document_type"]=="FACTION_PACK"]
        self.assertTrue(all(x["expected_binary_sha256"] and len(x["expected_binary_sha256"])==64 for x in packs))
        self.assertTrue(all(x["source_scope"]=="PUBLIC_SUPPLEMENTAL_FACTION_PACK_NOT_FULL_CODEX" for x in packs))

    def test_normalization_is_stable_and_removes_page_number_only_lines(self):
        raw="  DETACHMENT   RULES  \n12\nAlpha\u2011Beta\u00ad\n\n  one   two "
        self.assertEqual(normalize_text(raw),"DETACHMENT RULES\nAlpha-Beta\none two")

    def test_semantic_classes_are_heading_limited(self):
        text="AELDARI\nFACTION PACK\nCONTENTS\nDetachments\nDATASHEETS\nRULES UPDATES\nFAQ"
        classes=semantic_classes(text)
        self.assertIn("CONTENTS",classes)
        self.assertIn("DATASHEET",classes)
        self.assertIn("RULES_UPDATES",classes)
        self.assertIn("FAQ_ERRATA",classes)

    def test_report_schema_exists_and_is_valid_json(self):
        schema=json.loads((ROOT/"schemas/official_public_semantic_fingerprint.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["authority"]["const"],"GAMES_WORKSHOP_OFFICIAL")


if __name__=="__main__":
    unittest.main()
