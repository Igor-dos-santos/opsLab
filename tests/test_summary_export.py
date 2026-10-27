import unittest

from opslab.export import SUMMARY_CSV_HEADER, summary_results_to_csv
from opslab.scenarios import (
    TrialWaitSummary,
    run_paired_trials,
    summarize_mean_wait,
)


class SummaryCsvTests(unittest.TestCase):
    def test_hand_calculated_rows_have_unit_bearing_schema(self):
        rows = [
            TrialWaitSummary(3, 2, 4.5, 1.25, 7.75),
            TrialWaitSummary(1, 2, 9.0, 6.0, 12.0),
        ]

        output = summary_results_to_csv(rows)

        self.assertEqual(
            SUMMARY_CSV_HEADER,
            (
                "agents",
                "trials",
                "average_mean_wait_minutes",
                "minimum_mean_wait_minutes",
                "maximum_mean_wait_minutes",
            ),
        )
        self.assertEqual(
            output,
            "agents,trials,average_mean_wait_minutes,minimum_mean_wait_minutes,"
            "maximum_mean_wait_minutes\n"
            "3,2,4.5,1.25,7.75\n"
            "1,2,9.0,6.0,12.0\n",
        )

    def test_serialization_preserves_summary_order_and_values(self):
        summaries = summarize_mean_wait(
            run_paired_trials([11, 7], [4, 2], case_count=6)
        )

        output = summary_results_to_csv(summaries)

        lines = output.splitlines()
        self.assertEqual(
            [line.split(",", 1)[0] for line in lines[1:]],
            ["4", "2"],
        )
        for summary, line in zip(summaries, lines[1:]):
            self.assertEqual(
                line,
                f"{summary.agents},{summary.trials},"
                f"{summary.average_mean_wait_minutes},"
                f"{summary.minimum_mean_wait_minutes},"
                f"{summary.maximum_mean_wait_minutes}",
            )

    def test_empty_results_still_include_the_header(self):
        self.assertEqual(
            summary_results_to_csv([]),
            "agents,trials,average_mean_wait_minutes,minimum_mean_wait_minutes,"
            "maximum_mean_wait_minutes\n",
        )

    def test_output_uses_lf_line_endings(self):
        output = summary_results_to_csv(
            [TrialWaitSummary(1, 1, 0.0, 0.0, 0.0)]
        )

        self.assertNotIn("\r", output)
        self.assertTrue(output.endswith("\n"))

    def test_serialization_does_not_modify_summary_rows(self):
        summaries = summarize_mean_wait(
            run_paired_trials([3, 5], [2, 1], case_count=4)
        )
        before = list(summaries)

        summary_results_to_csv(summaries)

        self.assertEqual(summaries, before)


if __name__ == "__main__":
    unittest.main()
