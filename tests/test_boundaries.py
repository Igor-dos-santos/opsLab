import math
import unittest

from opslab.simulation import Case, simulate


class SimulationBoundaryTests(unittest.TestCase):
    def test_completion_overflow_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "completion overflowed"):
            simulate([Case(1e308, 1e308)], 1)

    def test_service_total_overflow_is_rejected_without_completion_overflow(self):
        with self.assertRaisesRegex(ValueError, "total service overflowed"):
            simulate([Case(0, 1e308), Case(0, 1e308)], 2)

    def test_wait_total_overflow_is_rejected(self):
        cases = [Case(0, 1e308), Case(0, 0), Case(0, 0)]
        with self.assertRaisesRegex(ValueError, "total wait overflowed"):
            simulate(cases, 1)

    def test_large_representable_result_is_allowed(self):
        result = simulate([Case(0, 1e308), Case(0, 0)], 1)
        self.assertEqual(result.mean_wait, 5e307)
        self.assertEqual(result.maximum_wait, 1e308)
        self.assertEqual(result.total_service_minutes, 1e308)
        self.assertEqual(result.final_completion, 1e308)
        self.assertTrue(all(math.isfinite(value) for value in (
            result.mean_wait, result.maximum_wait,
            result.total_service_minutes, result.final_completion)))

    def test_zero_duration_and_idle_gap(self):
        result = simulate([Case(0, 0), Case(20, 0)], 1)
        self.assertEqual(result.mean_wait, 0)
        self.assertEqual(result.maximum_wait, 0)
        self.assertEqual(result.total_service_minutes, 0)
        self.assertEqual(result.final_completion, 20)

    def test_simulation_does_not_reorder_or_modify_input(self):
        cases = [Case(2, 1), Case(0, 3), Case(1, 4)]
        original = cases.copy()
        result = simulate(cases, 2)
        self.assertEqual(cases, original)
        self.assertAlmostEqual(result.mean_wait, 1 / 3)
        self.assertEqual(result.maximum_wait, 1)
        self.assertEqual(result.total_service_minutes, 8)
        self.assertEqual(result.final_completion, 5)


if __name__ == "__main__":
    unittest.main()
