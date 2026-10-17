import math
import unittest
from opslab.simulation import Case, generate_cases, simulate

class SimulationTests(unittest.TestCase):
    def test_hand_calculated_single_agent(self):
        result = simulate([Case(0, 5), Case(1, 3), Case(10, 2)], 1)
        self.assertAlmostEqual(result.mean_wait, 4 / 3)
        self.assertEqual(result.maximum_wait, 4)
        self.assertEqual(result.total_service_minutes, 10)
        self.assertEqual(result.final_completion, 12)

    def test_two_agents_avoid_wait(self):
        self.assertEqual(simulate([Case(0, 5), Case(1, 3)], 2).mean_wait, 0)

    def test_unsorted_input(self):
        self.assertEqual(simulate([Case(1, 3), Case(0, 5)], 1).maximum_wait, 4)

    def test_simultaneous_arrivals_are_stable(self):
        self.assertEqual(simulate([Case(0, 5), Case(0, 1)], 1).mean_wait, 2.5)

    def test_empty(self):
        self.assertEqual(simulate([], 1).final_completion, 0)

    def test_reproducibility(self):
        self.assertEqual(generate_cases(10, 7), generate_cases(10, 7))
        self.assertNotEqual(generate_cases(10, 7), generate_cases(10, 8))

    def test_invalid_values(self):
        for agents in (0, -1, True, 1.5):
            with self.subTest(agents=agents), self.assertRaises(ValueError):
                simulate([], agents)
        for value in (-1, math.inf, math.nan):
            with self.subTest(value=value), self.assertRaises(ValueError):
                simulate([Case(0, value)], 1)
        for count in (-1, True, 1.5):
            with self.subTest(count=count), self.assertRaises(ValueError):
                generate_cases(count)

    def test_workload_conservation(self):
        cases = generate_cases(50)
        self.assertAlmostEqual(simulate(cases, 3).total_service_minutes,
                               sum(case.duration for case in cases))

if __name__ == "__main__":
    unittest.main()
