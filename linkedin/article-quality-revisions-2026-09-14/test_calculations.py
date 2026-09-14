import unittest
from calculations import expected_escapes, repair_hours, zero_failure_upper_bound


class CalculationTests(unittest.TestCase):
    def test_five_escape_example(self):
        self.assertAlmostEqual(expected_escapes(100000, .005, .05, .8), 5)

    def test_sensitivity_table(self):
        for recall, escapes in ((.5, 12.5), (.8, 5), (.95, 1.25)):
            self.assertAlmostEqual(expected_escapes(100000, .005, .05, recall), escapes)

    def test_routing_and_reviewer_detection(self):
        self.assertAlmostEqual(expected_escapes(100000, .005, .05, .8 * .8), 9)

    def test_old_rule_workload(self):
        self.assertAlmostEqual(repair_hours(400, 1, .04, 20), 16 / 3)
        self.assertEqual(round(repair_hours(400, 5, .04, 20), 1), 26.7)
        self.assertEqual(repair_hours(400, 15, .04, 20), 80)

    def test_counterfactual_and_sensitivity(self):
        for rate, old, avoided in ((.02, 40, 20), (.04, 80, 60), (.06, 120, 100)):
            self.assertEqual(repair_hours(400, 15, rate, 20), old)
            self.assertAlmostEqual(repair_hours(400, 15, rate, 20) - repair_hours(400, 15, .01, 20), avoided)

    def test_faster_bad_rule(self):
        extra = repair_hours(400, 5, .06, 20) - repair_hours(400, 5, .04, 20)
        self.assertEqual(round(extra, 1), 13.3)

    def test_zero_event_bound(self):
        bound = zero_failure_upper_bound(100)
        self.assertEqual(round(100 * bound, 2), 2.95)
        self.assertAlmostEqual((1 - bound) ** 100, .05)

    def test_invalid_inputs(self):
        for rate in (-.01, 1.01, float("nan")):
            with self.assertRaises(ValueError):
                expected_escapes(100, rate, .05, .8)
        with self.assertRaises(ValueError):
            zero_failure_upper_bound(0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
