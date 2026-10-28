from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

from opslab.export import summary_results_to_csv
from opslab.scenarios import run_paired_trials, summarize_mean_wait


class SummaryCliTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "opslab", *args],
            cwd=Path(__file__).resolve().parents[1],
            text=True,
            capture_output=True,
            timeout=10,
        )

    def test_summary_mode_emits_exact_csv_in_agent_order(self):
        process = self.run_cli(
            "--cases", "6", "--summary-seeds", "11", "7",
            "--trial-agents", "4", "2",
            "--mean-interarrival", "4", "--mean-service", "7",
        )

        rows = run_paired_trials(
            [11, 7], [4, 2], case_count=6,
            mean_interarrival=4, mean_service=7,
        )
        expected = summary_results_to_csv(summarize_mean_wait(rows))
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(process.stdout, expected)
        self.assertEqual(process.stderr, "")

    def test_summary_mode_is_mutually_exclusive_with_existing_modes(self):
        invalid = (
            ("--agents", "2"),
            ("--compare-agents", "2", "3"),
            ("--trial-seeds", "1", "2"),
        )
        for mode in invalid:
            with self.subTest(mode=mode):
                process = self.run_cli(
                    *mode,
                    "--summary-seeds", "1", "2",
                    "--trial-agents", "2", "3",
                )
                self.assertEqual(process.returncode, 2)
                self.assertEqual(process.stdout, "")
                self.assertIn("not allowed with argument", process.stderr)
                self.assertNotIn("Traceback", process.stderr)

    def test_summary_seeds_require_trial_agents(self):
        process = self.run_cli("--summary-seeds", "1", "2")

        self.assertEqual(process.returncode, 2)
        self.assertEqual(process.stdout, "")
        self.assertIn("--summary-seeds requires --trial-agents", process.stderr)
        self.assertNotIn("Traceback", process.stderr)

    def test_single_seed_option_is_rejected_in_summary_mode(self):
        process = self.run_cli(
            "--seed", "9", "--summary-seeds", "1", "2",
            "--trial-agents", "2", "3",
        )

        self.assertEqual(process.returncode, 2)
        self.assertEqual(process.stdout, "")
        self.assertIn("--seed cannot be used with --summary-seeds", process.stderr)
        self.assertNotIn("Traceback", process.stderr)

    def test_invalid_summary_lists_produce_no_partial_csv(self):
        invalid = (
            (("--summary-seeds", "2", "2", "--trial-agents", "1"),
             "seeds must be unique"),
            (("--summary-seeds", "1", "--trial-agents", "0", "2"),
             "positive integers"),
            (("--summary-seeds", "1", "--trial-agents", "2", "2"),
             "agent_counts must be unique"),
        )
        for options, message in invalid:
            with self.subTest(options=options):
                process = self.run_cli(*options)
                self.assertEqual(process.returncode, 2)
                self.assertEqual(process.stdout, "")
                self.assertIn(message, process.stderr)
                self.assertNotIn("Traceback", process.stderr)

    def test_late_summary_failure_is_atomic_at_stdout_boundary(self):
        from opslab import __main__ as cli

        stdout = StringIO()
        stderr = StringIO()
        argv = [
            "opslab", "--summary-seeds", "1", "2",
            "--trial-agents", "1", "2",
        ]
        with patch.object(sys, "argv", argv), patch.object(
            cli, "summarize_mean_wait", side_effect=ValueError("summary failed"),
        ), redirect_stdout(stdout), redirect_stderr(stderr):
            with self.assertRaisesRegex(SystemExit, "2"):
                cli.main()

        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("summary failed", stderr.getvalue())
        self.assertNotIn("Traceback", stderr.getvalue())

    def test_help_explains_summary_csv_mode(self):
        process = self.run_cli("--help")

        self.assertEqual(process.returncode, 0)
        self.assertIn("--summary-seeds", process.stdout)
        self.assertIn("--trial-agents", process.stdout)
        self.assertIn("descriptive", process.stdout)
        self.assertIn("CSV", process.stdout)


if __name__ == "__main__":
    unittest.main()
