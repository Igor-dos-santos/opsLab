import json
import math
from pathlib import Path
from random import Random
import subprocess
import sys
import unittest
from unittest.mock import patch

from opslab.simulation import Case, generate_cases, simulate


class WorkloadTests(unittest.TestCase):
    def test_defaults_preserve_original_draw_sequence(self):
        rng = Random(42)
        arrival = 0.0
        expected = []
        for _ in range(20):
            arrival += rng.expovariate(1 / 2)
            expected.append(Case(arrival, rng.expovariate(1 / 5)))
        self.assertEqual(generate_cases(20, 42), expected)

    def test_custom_means_are_repeatable(self):
        options = dict(mean_interarrival=4.0, mean_service=7.0)
        self.assertEqual(generate_cases(20, 9, **options),
                         generate_cases(20, 9, **options))

    def test_doubling_each_mean_scales_only_its_component(self):
        baseline = generate_cases(20, 7)
        arrivals = generate_cases(20, 7, mean_interarrival=4)
        services = generate_cases(20, 7, mean_service=10)
        for original, spaced, longer in zip(baseline, arrivals, services):
            self.assertAlmostEqual(spaced.arrival, original.arrival * 2)
            self.assertEqual(spaced.duration, original.duration)
            self.assertEqual(longer.arrival, original.arrival)
            self.assertAlmostEqual(longer.duration, original.duration * 2)

    def test_reject_invalid_means_even_for_empty_workload(self):
        invalid = (0, -1, math.inf, -math.inf, math.nan, True, False,
                   "2", None, 5e-324, 10 ** 400)
        for name in ("mean_interarrival", "mean_service"):
            for value in invalid:
                for count in (0, 2):
                    with self.subTest(name=name, value=value, count=count):
                        with self.assertRaises(ValueError):
                            generate_cases(count, **{name: value})

    def test_empty_custom_workload(self):
        self.assertEqual(generate_cases(0, mean_interarrival=0.5,
                                        mean_service=0.25), [])

    def test_generated_overflow_is_rejected(self):
        for draws in ([math.inf, 1], [1, math.inf],
                      [1e308, 1, 1e308, 1]):
            with self.subTest(draws=draws):
                with patch("opslab.simulation.Random") as random_class:
                    random_class.return_value.expovariate.side_effect = draws
                    with self.assertRaisesRegex(ValueError, "overflowed"):
                        generate_cases(len(draws) // 2)


class WorkloadCliTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, "-m", "opslab", *args],
                              cwd=Path(__file__).resolve().parents[1],
                              text=True, capture_output=True, timeout=10)

    def test_custom_options_reach_simulator(self):
        process = self.run_cli("--cases", "12", "--agents", "2", "--seed", "7",
                               "--mean-interarrival", "4", "--mean-service", "7")
        self.assertEqual(process.returncode, 0, process.stderr)
        output = json.loads(process.stdout)
        expected = simulate(generate_cases(12, 7, mean_interarrival=4,
                                           mean_service=7), 2)
        self.assertEqual(output["mean_wait"], expected.mean_wait)
        self.assertEqual(output["total_service_minutes"], expected.total_service_minutes)
        self.assertEqual(output["cases"], 12)

    def test_bad_cli_means_are_usage_errors_without_tracebacks(self):
        for option in ("--mean-interarrival", "--mean-service"):
            for value in ("0", "-1", "nan", "inf", "abc", "5e-324"):
                with self.subTest(option=option, value=value):
                    process = self.run_cli(option, value)
                    self.assertEqual(process.returncode, 2)
                    self.assertEqual(process.stdout, "")
                    self.assertNotIn("Traceback", process.stderr)
                    self.assertIn("error:", process.stderr)

    def test_help_documents_units(self):
        process = self.run_cli("--help")
        self.assertEqual(process.returncode, 0)
        self.assertIn("--mean-interarrival", process.stdout)
        self.assertIn("--mean-service", process.stdout)
        self.assertIn("minutes", process.stdout)

    def test_simulation_overflow_is_a_usage_error(self):
        process = self.run_cli("--cases", "100", "--agents", "1", "--seed", "42",
                               "--mean-service", "1e307")
        self.assertEqual(process.returncode, 2)
        self.assertEqual(process.stdout, "")
        self.assertIn("simulation", process.stderr)
        self.assertIn("overflowed", process.stderr)
        self.assertNotIn("Traceback", process.stderr)


if __name__ == "__main__":
    unittest.main()
