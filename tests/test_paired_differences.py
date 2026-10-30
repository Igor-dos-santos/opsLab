import unittest

from opslab.scenarios import (
    PairedMeanWaitDifference,
    TrialResult,
    paired_mean_wait_differences,
    run_paired_trials,
)
from opslab.simulation import Result


class PairedMeanWaitDifferenceTests(unittest.TestCase):
    def test_hand_calculated_differences_preserve_seed_order_and_sign(self):
        rows = [
            TrialResult(20, 4, Result(5, 4.0, 5.0, 10.0, 12.0)),
            TrialResult(20, 2, Result(5, 10.0, 12.0, 10.0, 20.0)),
            TrialResult(10, 4, Result(5, 2.0, 3.0, 11.0, 13.0)),
            TrialResult(10, 2, Result(5, 8.0, 9.0, 11.0, 19.0)),
        ]

        differences = paired_mean_wait_differences(
            rows, baseline_agents=2, comparison_agents=4,
        )

        self.assertEqual(
            differences,
            [
                PairedMeanWaitDifference(20, 2, 4, 10.0, 4.0, -6.0),
                PairedMeanWaitDifference(10, 2, 4, 8.0, 2.0, -6.0),
            ],
        )

    def test_generated_rows_match_direct_within_seed_subtraction(self):
        rows = run_paired_trials([40, 41, 42], [2, 4], case_count=10)

        differences = paired_mean_wait_differences(
            rows, baseline_agents=2, comparison_agents=4,
        )

        expected = []
        for seed in [40, 41, 42]:
            values = {
                row.agents: row.result.mean_wait
                for row in rows if row.seed == seed
            }
            expected.append(values[4] - values[2])
        self.assertEqual([row.seed for row in differences], [40, 41, 42])
        self.assertEqual(
            [row.comparison_minus_baseline_minutes for row in differences],
            expected,
        )

    def test_agent_identifiers_must_be_distinct_positive_integers(self):
        invalid = (
            (True, 2),
            (0, 2),
            (2, 1.5),
            (2, 2),
        )
        for baseline, comparison in invalid:
            with self.subTest(baseline=baseline, comparison=comparison):
                with self.assertRaises(ValueError):
                    paired_mean_wait_differences(
                        [],
                        baseline_agents=baseline,
                        comparison_agents=comparison,
                    )

    def test_requested_agents_must_exist_in_the_complete_matrix(self):
        rows = [
            TrialResult(1, 2, Result(3, 2.0, 3.0, 4.0, 5.0)),
            TrialResult(1, 3, Result(3, 1.0, 2.0, 4.0, 4.0)),
        ]

        with self.assertRaisesRegex(ValueError, "requested agents"):
            paired_mean_wait_differences(
                rows, baseline_agents=2, comparison_agents=4,
            )

    def test_incomplete_matrix_is_rejected_before_subtraction(self):
        rows = [
            TrialResult(1, 2, Result(3, 2.0, 3.0, 4.0, 5.0)),
            TrialResult(1, 4, Result(3, 1.0, 2.0, 4.0, 4.0)),
            TrialResult(2, 2, Result(3, 3.0, 4.0, 5.0, 6.0)),
        ]

        with self.assertRaisesRegex(ValueError, "every seed and agent"):
            paired_mean_wait_differences(
                rows, baseline_agents=2, comparison_agents=4,
            )

    def test_input_rows_are_not_modified(self):
        rows = run_paired_trials([3, 9], [3, 1], case_count=5)
        before = list(rows)

        paired_mean_wait_differences(
            rows, baseline_agents=1, comparison_agents=3,
        )

        self.assertEqual(rows, before)


if __name__ == "__main__":
    unittest.main()
