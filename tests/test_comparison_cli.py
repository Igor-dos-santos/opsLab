from pathlib import Path
import subprocess
import sys
import unittest

from opslab.export import staffing_results_to_csv
from opslab.scenarios import compare_staffing
from opslab.simulation import generate_cases


class ComparisonCliTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "opslab", *args],
            cwd=Path(__file__).resolve().parents[1],
            text=True,
            capture_output=True,
            timeout=10,
        )

    def test_compare_mode_emits_only_expected_csv_in_requested_order(self):
        process = self.run_cli(
            "--cases", "12", "--seed", "7",
            "--mean-interarrival", "4", "--mean-service", "7",
            "--compare-agents", "4", "2", "3",
        )

        cases = generate_cases(12, 7, mean_interarrival=4, mean_service=7)
        expected = staffing_results_to_csv(compare_staffing(cases, [4, 2, 3]))
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(process.stdout, expected)
        self.assertEqual(process.stderr, "")

    def test_single_and_comparison_modes_are_mutually_exclusive(self):
        process = self.run_cli(
            "--agents", "2", "--compare-agents", "2", "3",
        )

        self.assertEqual(process.returncode, 2)
        self.assertEqual(process.stdout, "")
        self.assertIn("not allowed with argument", process.stderr)
        self.assertNotIn("Traceback", process.stderr)

    def test_invalid_comparison_counts_are_usage_errors_without_partial_csv(self):
        invalid = (
            (("0", "2"), "positive integers"),
            (("2", "2"), "unique"),
            (("-1", "2"), "positive integers"),
        )
        for counts, message in invalid:
            with self.subTest(counts=counts):
                process = self.run_cli("--compare-agents", *counts)

                self.assertEqual(process.returncode, 2)
                self.assertEqual(process.stdout, "")
                self.assertIn(message, process.stderr)
                self.assertNotIn("Traceback", process.stderr)

    def test_compare_mode_propagates_workload_errors_without_partial_csv(self):
        process = self.run_cli(
            "--compare-agents", "2", "3", "--mean-service", "0",
        )

        self.assertEqual(process.returncode, 2)
        self.assertEqual(process.stdout, "")
        self.assertIn("mean_service", process.stderr)
        self.assertNotIn("Traceback", process.stderr)

    def test_compare_mode_propagates_simulation_overflow_without_partial_csv(self):
        process = self.run_cli(
            "--cases", "100", "--seed", "42",
            "--compare-agents", "2", "1", "--mean-service", "1e307",
        )

        self.assertEqual(process.returncode, 2)
        self.assertEqual(process.stdout, "")
        self.assertIn("simulation total service overflowed", process.stderr)
        self.assertNotIn("Traceback", process.stderr)

    def test_help_explains_comparison_csv_mode(self):
        process = self.run_cli("--help")

        self.assertEqual(process.returncode, 0)
        self.assertIn("--compare-agents", process.stdout)
        self.assertIn("CSV", process.stdout)
        self.assertIn("same workload", process.stdout)


if __name__ == "__main__":
    unittest.main()
