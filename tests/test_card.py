"""Tests for the result card generator.

Run from the repo root:
    python3 -m unittest discover -s tests -v
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from PIL import Image  # noqa: E402

from agent_level.card import CARD_VERSION_LABEL, generate_card  # noqa: E402
from agent_level.core import calculate  # noqa: E402

FANG_RESULT = {
    "dimensions": {
        "HUM": {"score": 89},
        "KNOW": {"score": 88},
        "SKILL": {"score": 87},
        "SPAN": {"score": 91},
        "REL": {"score": 85},
    },
    "composite": 88,
    "intelligence": 87,
    "level": 10,
    "title": "熟手",
}


class TestCard(unittest.TestCase):
    def test_card_without_logo_or_birthday(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "card.png")
            path = generate_card(FANG_RESULT, name="Fang", species="Muse",
                                 output_path=out)
            with Image.open(path) as img:
                self.assertEqual(img.size, (1200, 1500))
                self.assertEqual(img.format, "PNG")

    def test_card_with_logo_and_birthday(self):
        with tempfile.TemporaryDirectory() as tmp:
            logo_path = os.path.join(tmp, "logo.png")
            Image.new("RGB", (320, 100), (11, 42, 74)).save(logo_path)
            out = os.path.join(tmp, "card.png")
            generate_card(FANG_RESULT, name="Fang", species="Muse",
                          birthday="2026-09-23", logo_path=logo_path,
                          output_path=out)
            with Image.open(out) as img:
                self.assertEqual(img.size, (1200, 1500))

    def test_card_from_calculated_result(self):
        profile = {
            "persona_items": 1, "soul_bytes": 500, "pref_count": 0,
            "autonomy_tier": "none", "mem_total": 0, "domains": [],
            "people": 0, "groups": 0, "days_since_update": None,
            "skills": [], "goals_total": 0, "goals_done": 0, "platforms": 0,
            "pass_rate": None, "fixes": 0, "acknowledged_fixes": 0,
            "honesty": "none", "reasoning_evidence": 0, "reasoning_j": 0,
            "deliveries": 0,
        }
        result = calculate(profile)
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "card.png")
            generate_card(result, output_path=out)
            self.assertTrue(os.path.getsize(out) > 0)

    def test_card_version_label(self):
        self.assertEqual(CARD_VERSION_LABEL, "測試版本 v0.01")


if __name__ == "__main__":
    unittest.main()
