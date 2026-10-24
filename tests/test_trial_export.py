import unittest

from opslab.export import TRIAL_CSV_HEADER, trial_results_to_csv
from opslab.scenarios import TrialResult, run_paired_trials
from opslab.simulation import Result


class TrialCsvTests(unittest.TestCase):
    def test_hand_calculated_row_has_seed_and_unit_bearing_schema(self):
        rows = [TrialResult(7, 3, Result(2, 1.5, 2.0, 3.5, 4.0))]

        output = trial_results_to_csv(rows)

        self.assertEqual(
            TRIAL_CSV_HEADER,
            (
                "seed", "agents", "cases", "mean_wait_minutes",
                "maximum_wait_minutes", "total_service_minutes",
                "final_completion_minutes",
            ),
        )
        self.assertEqual(
            output,
            "seed,agents,cases,mean_wait_minutes,maximum_wait_minutes,"
            "total_service_minutes,final_completion_minutes\n"
            "7,3,2,1.5,2.0,3.5,4.0\n",
        )

    def test_serialization_preserves_seed_then_agent_order_and_values(self):
        rows = run_paired_trials([11, 7], [4, 2], case_count=6)

        output = trial_results_to_csv(rows)

        lines = output.splitlines()
        self.assertEqual(
            [tuple(line.split(",", 2)[:2]) for line in lines[1:]],
            [("11", "4"), ("11", "2"), ("7", "4"), ("7", "2")],
        )
        for row, line in zip(rows, lines[1:]):
            result = row.result
            self.assertEqual(
                line,
                f"{row.seed},{row.agents},{result.cases},{result.mean_wait},"
                f"{result.maximum_wait},{result.total_service_minutes},"
                f"{result.final_completion}",
            )

    def test_empty_results_still_include_the_header(self):
        self.assertEqual(
            trial_results_to_csv([]),
            "seed,agents,cases,mean_wait_minutes,maximum_wait_minutes,"
            "total_service_minutes,final_completion_minutes\n",
        )

    def test_output_uses_lf_line_endings(self):
        rows = [TrialResult(-1, 1, Result(0, 0.0, 0.0, 0.0, 0.0))]

        output = trial_results_to_csv(rows)

        self.assertNotIn("\r", output)
        self.assertTrue(output.endswith("\n"))

    def test_serialization_does_not_modify_trial_rows(self):
        rows = run_paired_trials([3, 5], [2, 1], case_count=4)
        before = list(rows)

        trial_results_to_csv(rows)

        self.assertEqual(rows, before)


if __name__ == "__main__":
    unittest.main()
