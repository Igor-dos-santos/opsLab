from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import sys
import unittest
from unittest.mock import patch

from opslab import __main__ as cli


class ExperimentBudgetCliTests(unittest.TestCase):
    def run_main(self, *args):
        stdout = StringIO()
        stderr = StringIO()
        with patch.object(sys, "argv", ["opslab", *args]), \
                redirect_stdout(stdout), redirect_stderr(stderr):
            try:
                cli.main()
            except SystemExit as error:
                return error.code, stdout.getvalue(), stderr.getvalue()
        return 0, stdout.getvalue(), stderr.getvalue()

    def test_raw_trial_case_run_budget_is_checked_before_generation(self):
        with patch.object(cli, "run_paired_trials") as run:
            code, stdout, stderr = self.run_main(
                "--cases", "500001", "--trial-seeds", "1",
                "--trial-agents", "1", "2",
            )

        self.assertEqual(code, 2)
        self.assertEqual(stdout, "")
        self.assertIn("1000000 case-runs", stderr)
        self.assertNotIn("Traceback", stderr)
        run.assert_not_called()

    def test_summary_result_row_budget_is_checked_before_generation(self):
        seeds = [str(seed) for seed in range(101)]
        agents = [str(agents) for agents in range(1, 101)]
        with patch.object(cli, "run_paired_trials") as run:
            code, stdout, stderr = self.run_main(
                "--cases", "0", "--summary-seeds", *seeds,
                "--trial-agents", *agents,
            )

        self.assertEqual(code, 2)
        self.assertEqual(stdout, "")
        self.assertIn("10000 result rows", stderr)
        self.assertNotIn("Traceback", stderr)
        run.assert_not_called()

    def test_exact_case_run_boundary_reaches_trial_engine(self):
        with patch.object(
            cli, "run_paired_trials", side_effect=ValueError("engine reached"),
        ) as run:
            code, stdout, stderr = self.run_main(
                "--cases", "500000", "--trial-seeds", "1",
                "--trial-agents", "1", "2",
            )

        self.assertEqual(code, 2)
        self.assertEqual(stdout, "")
        self.assertIn("engine reached", stderr)
        self.assertNotIn("experiment budget", stderr)
        run.assert_called_once()

    def test_help_documents_paired_experiment_limits(self):
        code, stdout, stderr = self.run_main("--help")

        self.assertEqual(code, 0)
        self.assertEqual(stderr, "")
        self.assertIn("1000000 case-runs", stdout)
        self.assertIn("10000 result rows", stdout)


if __name__ == "__main__":
    unittest.main()
