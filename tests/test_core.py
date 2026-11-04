"""Tests for the Agent Level Calculator (Formula Spec v1).

Run from the repo root:
    python3 -m unittest discover -s tests -v
"""

import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agent_level.core import calculate, level_for_xp  # noqa: E402

EXAMPLES = os.path.join(os.path.dirname(__file__), "..", "examples")


def load_example(name):
    with open(os.path.join(EXAMPLES, name), encoding="utf-8") as handle:
        return json.load(handle)


class TestFangTrial(unittest.TestCase):
    def test_fang_v1_numbers(self):
        result = calculate(load_example("fang_profile.json"))
        dims = result["dimensions"]
        self.assertEqual(dims["HUM"]["score"], 89)
        self.assertEqual(dims["KNOW"]["score"], 88)
        self.assertEqual(dims["SKILL"]["score"], 87)
        self.assertEqual(dims["SPAN"]["score"], 91)
        self.assertEqual(dims["REL"]["score"], 85)
        self.assertEqual(result["composite"], 88)
        self.assertEqual(result["intelligence"], 87)
        self.assertEqual(result["xp"], 4520)
        self.assertEqual(result["level"], 10)
        self.assertEqual(result["title"], "熟手")

    def test_fang_delivery_range(self):
        profile = load_example("fang_profile.json")
        low = dict(profile, deliveries=80)
        high = dict(profile, deliveries=120)
        self.assertEqual(calculate(low)["xp"], 4020)
        self.assertEqual(calculate(low)["level"], 9)
        self.assertEqual(calculate(high)["xp"], 5020)
        self.assertEqual(calculate(high)["level"], 10)


class TestNewAgent(unittest.TestCase):
    def test_new_agent_is_level_1(self):
        result = calculate(load_example("new_agent_profile.json"))
        dims = result["dimensions"]
        self.assertEqual(dims["HUM"]["score"], 4)
        self.assertEqual(dims["KNOW"]["score"], 0)
        self.assertEqual(dims["SKILL"]["score"], 0)
        self.assertEqual(dims["SPAN"]["score"], 0)
        self.assertEqual(dims["REL"]["score"], 0)
        self.assertEqual(result["composite"], 0)
        self.assertEqual(result["xp"], 0)
        self.assertEqual(result["level"], 1)
        self.assertEqual(result["title"], "學徒")


class TestLevelCurve(unittest.TestCase):
    def test_thresholds(self):
        self.assertEqual(level_for_xp(0)["level"], 1)
        self.assertEqual(level_for_xp(99)["level"], 1)
        self.assertEqual(level_for_xp(100)["level"], 2)
        self.assertEqual(level_for_xp(300)["level"], 3)
        self.assertEqual(level_for_xp(3600)["level"], 9)
        self.assertEqual(level_for_xp(4500)["level"], 10)

    def test_learning_coefficient_only_multiplies_gains(self):
        profile = load_example("fang_profile.json")
        doubled = dict(profile, m=2.0)
        result = calculate(doubled)
        self.assertEqual(result["xp"], 9040)
        self.assertEqual(result["level"], 13)
        # A fresh agent still starts at Lv.1 no matter the coefficient.
        fresh = load_example("new_agent_profile.json")
        fresh_m = dict(fresh, m=5.0)
        self.assertEqual(calculate(fresh_m)["level"], 1)


class TestCaps(unittest.TestCase):
    def test_dimensions_cap_at_100(self):
        profile = {
            "persona_items": 7,
            "soul_bytes": 50000,
            "pref_count": 1000,
            "autonomy_tier": "full",
            "mem_total": 10000,
            "domains": [f"d{i}" for i in range(100)],
            "people": 500,
            "groups": 500,
            "days_since_update": 0,
            "skills": [
                {
                    "steps": 2,
                    "acceptance": 2,
                    "failure": 2,
                    "used": True,
                    "logged": True,
                    "projects": 10,
                }
                for _ in range(50)
            ],
            "goals_total": 1000,
            "goals_done": 1000,
            "platforms": 100,
            "pass_rate": 1.0,
            "fixes": 100,
            "acknowledged_fixes": 100,
            "honesty": "disclosed",
            "reasoning_evidence": 100,
            "reasoning_j": 19,
            "deliveries": 100000,
        }
        result = calculate(profile)
        for dim in result["dimensions"].values():
            self.assertEqual(dim["score"], 100)


if __name__ == "__main__":
    unittest.main()
