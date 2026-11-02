import unittest

from synth_market import DEFECTS, basic_checker, clean_campaign, generate, plant, score
import random


class SynthMarketTest(unittest.TestCase):
    def test_same_seed_same_market(self):
        self.assertEqual(generate(20, seed=3), generate(20, seed=3))

    def test_clean_campaign_has_no_findings(self):
        c = clean_campaign(1, "HR", random.Random(1))
        self.assertEqual(basic_checker(c), [])

    def test_every_planted_defect_changes_the_campaign(self):
        for d in DEFECTS:
            c = clean_campaign(1, "HR", random.Random(1))
            before = dict(c)
            self.assertNotEqual(plant(dict(c), d), before, d)

    def test_basic_checker_blind_to_wrong_currency(self):
        campaigns, key = generate(200, defect_rate=0.5, seed=11)
        s = score(basic_checker, campaigns, key)
        self.assertEqual(list(s["missed"].keys()), ["wrong_currency"])
        self.assertEqual(s["false_alarms"], 0)


if __name__ == "__main__":
    unittest.main()
