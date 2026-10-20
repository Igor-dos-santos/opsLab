import unittest
from unittest.mock import patch

from opslab.scenarios import compare_staffing
from opslab.simulation import Case, generate_cases, simulate


class StaffingComparisonTests(unittest.TestCase):
    def test_hand_calculated_comparison_preserves_order_and_workload(self):
        cases = [Case(2, 1), Case(0, 4), Case(1, 2)]
        original = cases.copy()
        counts = [2, 1]
        rows = compare_staffing(cases, counts)
        self.assertEqual([row.agents for row in rows], [2, 1])
        self.assertAlmostEqual(rows[0].result.mean_wait, 1 / 3)
        self.assertEqual(rows[0].result.final_completion, 4)
        self.assertAlmostEqual(rows[1].result.mean_wait, 7 / 3)
        self.assertEqual(rows[1].result.final_completion, 7)
        self.assertEqual([row.result.total_service_minutes for row in rows], [7, 7])
        self.assertEqual(cases, original)
        self.assertEqual(counts, [2, 1])

    def test_each_scenario_receives_the_identical_case_list(self):
        cases = generate_cases(10, 7)
        with patch("opslab.scenarios.simulate", wraps=simulate) as run:
            compare_staffing(cases, [1, 3])
        self.assertEqual(run.call_count, 2)
        for call in run.call_args_list:
            self.assertIs(call.args[0], cases)

    def test_seeded_comparison_matches_direct_simulation(self):
        cases = generate_cases(100, 42)
        first = compare_staffing(cases, [2, 3, 4])
        self.assertEqual(first, compare_staffing(cases, [2, 3, 4]))
        for row in first:
            self.assertEqual(row.result, simulate(cases, row.agents))
            self.assertEqual(row.result.cases, 100)
            self.assertEqual(row.result.total_service_minutes,
                             first[0].result.total_service_minutes)

    def test_invalid_counts_are_rejected_before_any_simulation(self):
        invalid = ([], [1, 0], [1, -1], [1, True], [1, 1.5], [1, "2"],
                   [1, 1], None, "12", 2, (1, 2))
        for counts in invalid:
            with self.subTest(counts=counts):
                with patch("opslab.scenarios.simulate") as run:
                    with self.assertRaises(ValueError):
                        compare_staffing([], counts)
                    run.assert_not_called()

    def test_empty_workload_returns_zero_metrics_for_each_count(self):
        rows = compare_staffing([], [1, 2])
        for row in rows:
            self.assertEqual(row.result, simulate([], row.agents))
            self.assertEqual(row.result.cases, 0)
            self.assertEqual(row.result.mean_wait, 0)

    def test_invalid_case_is_not_silently_dropped(self):
        with self.assertRaisesRegex(ValueError, "finite and nonnegative"):
            compare_staffing([Case(0, -1)], [1, 2])

    def test_overflow_aborts_comparison_instead_of_returning_partial_rows(self):
        # Two agents succeed; one agent then overflows total waiting time.
        cases = [Case(0, 1e308), Case(0, 0), Case(0, 0)]
        with self.assertRaisesRegex(ValueError, "total wait overflowed"):
            compare_staffing(cases, [2, 1])


if __name__ == "__main__":
    unittest.main()
