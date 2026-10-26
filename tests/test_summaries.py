import unittest

from opslab.scenarios import (
    TrialResult,
    TrialWaitSummary,
    run_paired_trials,
    summarize_mean_wait,
)
from opslab.simulation import Result


class TrialSummaryTests(unittest.TestCase):
    def test_hand_calculated_summary_preserves_first_agent_order(self):
        rows = [
            TrialResult(10, 3, Result(5, 2.0, 3.0, 10.0, 12.0)),
            TrialResult(10, 1, Result(5, 6.0, 8.0, 10.0, 20.0)),
            TrialResult(20, 3, Result(5, 4.0, 5.0, 11.0, 13.0)),
            TrialResult(20, 1, Result(5, 10.0, 12.0, 11.0, 24.0)),
        ]

        summaries = summarize_mean_wait(rows)

        self.assertEqual(
            summaries,
            [
                TrialWaitSummary(3, 2, 3.0, 2.0, 4.0),
                TrialWaitSummary(1, 2, 8.0, 6.0, 10.0),
            ],
        )

    def test_generated_rows_match_direct_descriptive_calculation(self):
        rows = run_paired_trials([40, 41, 42], [4, 2], case_count=10)
        before = list(rows)

        summaries = summarize_mean_wait(rows)

        self.assertEqual([row.agents for row in summaries], [4, 2])
        self.assertEqual([row.trials for row in summaries], [3, 3])
        for summary in summaries:
            values = [
                row.result.mean_wait for row in rows
                if row.agents == summary.agents
            ]
            self.assertAlmostEqual(
                summary.average_mean_wait_minutes,
                sum(values) / len(values),
            )
            self.assertEqual(summary.minimum_mean_wait_minutes, min(values))
            self.assertEqual(summary.maximum_mean_wait_minutes, max(values))
        self.assertEqual(rows, before)

    def test_empty_rows_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "nonempty list"):
            summarize_mean_wait([])

    def test_duplicate_seed_agent_pair_is_rejected(self):
        row = TrialResult(1, 2, Result(3, 1.0, 2.0, 3.0, 4.0))

        with self.assertRaisesRegex(ValueError, "duplicate seed-agent pair"):
            summarize_mean_wait([row, row])

    def test_incomplete_seed_agent_matrix_is_rejected(self):
        rows = [
            TrialResult(1, 2, Result(3, 1.0, 2.0, 3.0, 4.0)),
            TrialResult(1, 3, Result(3, 0.5, 1.0, 3.0, 3.5)),
            TrialResult(2, 2, Result(3, 2.0, 3.0, 4.0, 5.0)),
        ]

        with self.assertRaisesRegex(ValueError, "every seed and agent"):
            summarize_mean_wait(rows)

    def test_inconsistent_case_counts_are_rejected(self):
        rows = [
            TrialResult(1, 2, Result(3, 1.0, 2.0, 3.0, 4.0)),
            TrialResult(2, 2, Result(4, 2.0, 3.0, 4.0, 5.0)),
        ]

        with self.assertRaisesRegex(ValueError, "same case count"):
            summarize_mean_wait(rows)

    def test_invalid_rows_and_mean_wait_values_are_rejected(self):
        invalid = (
            None,
            TrialResult(True, 2, Result(3, 1.0, 2.0, 3.0, 4.0)),
            TrialResult(1, 0, Result(3, 1.0, 2.0, 3.0, 4.0)),
            TrialResult(1, 2, Result(3, float("nan"), 2.0, 3.0, 4.0)),
            TrialResult(1, 2, Result(3, -1.0, 2.0, 3.0, 4.0)),
        )
        for row in invalid:
            with self.subTest(row=row), self.assertRaises(ValueError):
                summarize_mean_wait([row])

    def test_large_finite_wait_average_does_not_overflow(self):
        rows = [
            TrialResult(1, 2, Result(1, 1e308, 1e308, 1.0, 1.0)),
            TrialResult(2, 2, Result(1, 1e308, 1e308, 1.0, 1.0)),
        ]

        summary = summarize_mean_wait(rows)[0]

        self.assertEqual(summary.average_mean_wait_minutes, 1e308)


if __name__ == "__main__":
    unittest.main()
