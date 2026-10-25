from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

from opslab.export import trial_results_to_csv
from opslab.scenarios import run_paired_trials


class TrialCliTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "opslab", *args],
            cwd=Path(__file__).resolve().parents[1],
            text=True,
            capture_output=True,
            timeout=10,
        )

    def test_trial_mode_emits_exact_csv_in_seed_then_agent_order(self):
        process = self.run_cli(
            "--cases", "6", "--trial-seeds", "11", "7",
            "--trial-agents", "4", "2",
            "--mean-interarrival", "4", "--mean-service", "7",
        )

        rows = run_paired_trials(
            [11, 7], [4, 2], case_count=6,
            mean_interarrival=4, mean_service=7,
        )
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(process.stdout, trial_results_to_csv(rows))
        self.assertEqual(process.stderr, "")

    def test_trial_mode_is_mutually_exclusive_with_existing_modes(self):
        invalid = (
            ("--agents", "2", "--trial-seeds", "1"),
            ("--compare-agents", "2", "3", "--trial-seeds", "1"),
        )
        for options in invalid:
            with self.subTest(options=options):
                process = self.run_cli(*options, "--trial-agents", "1")
                self.assertEqual(process.returncode, 2)
                self.assertEqual(process.stdout, "")
                self.assertIn("not allowed with argument", process.stderr)
                self.assertNotIn("Traceback", process.stderr)

    def test_trial_options_must_be_supplied_together(self):
        invalid = (
            (("--trial-seeds", "1", "2"), "--trial-agents"),
            (("--trial-agents", "1", "2"), "--trial-seeds"),
        )
        for options, missing in invalid:
            with self.subTest(options=options):
                process = self.run_cli(*options)
                self.assertEqual(process.returncode, 2)
                self.assertEqual(process.stdout, "")
                self.assertIn(f"requires {missing}", process.stderr)
                self.assertNotIn("Traceback", process.stderr)

    def test_single_seed_option_is_rejected_in_trial_mode(self):
        process = self.run_cli(
            "--seed", "9", "--trial-seeds", "1", "2",
            "--trial-agents", "2", "3",
        )

        self.assertEqual(process.returncode, 2)
        self.assertEqual(process.stdout, "")
        self.assertIn("--seed cannot be used with --trial-seeds", process.stderr)
        self.assertNotIn("Traceback", process.stderr)

    def test_invalid_trial_lists_produce_no_partial_csv(self):
        invalid = (
            (("--trial-seeds", "2", "2", "--trial-agents", "1"),
             "seeds must be unique"),
            (("--trial-seeds", "1", "--trial-agents", "0", "2"),
             "positive integers"),
            (("--trial-seeds", "1", "--trial-agents", "2", "2"),
             "agent_counts must be unique"),
        )
        for options, message in invalid:
            with self.subTest(options=options):
                process = self.run_cli(*options)
                self.assertEqual(process.returncode, 2)
                self.assertEqual(process.stdout, "")
                self.assertIn(message, process.stderr)
                self.assertNotIn("Traceback", process.stderr)

    def test_late_trial_failure_is_atomic_at_stdout_boundary(self):
        from opslab import __main__ as cli

        stdout = StringIO()
        stderr = StringIO()
        argv = [
            "opslab", "--trial-seeds", "1", "2",
            "--trial-agents", "1", "2",
        ]
        with patch.object(sys, "argv", argv), patch.object(
            cli, "run_paired_trials", side_effect=ValueError("late trial failed"),
        ), redirect_stdout(stdout), redirect_stderr(stderr):
            with self.assertRaisesRegex(SystemExit, "2"):
                cli.main()

        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("late trial failed", stderr.getvalue())
        self.assertNotIn("Traceback", stderr.getvalue())

    def test_help_explains_repeated_trial_csv_mode(self):
        process = self.run_cli("--help")

        self.assertEqual(process.returncode, 0)
        self.assertIn("--trial-seeds", process.stdout)
        self.assertIn("--trial-agents", process.stdout)
        self.assertIn("paired", process.stdout)
        self.assertIn("CSV", process.stdout)


if __name__ == "__main__":
    unittest.main()
