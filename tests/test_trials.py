from unittest import mock
import unittest

from opslab.scenarios import compare_staffing, run_paired_trials
from opslab.simulation import generate_cases


class PairedTrialTests(unittest.TestCase):
    def test_records_seed_and_agent_order_with_direct_results(self):
        seeds = [7, 11]
        agent_counts = [3, 1]

        rows = run_paired_trials(
            seeds,
            agent_counts,
            case_count=8,
            mean_interarrival=4,
            mean_service=7,
        )

        self.assertEqual(
            [(row.seed, row.agents) for row in rows],
            [(7, 3), (7, 1), (11, 3), (11, 1)],
        )
        expected = []
        for seed in seeds:
            cases = generate_cases(
                8, seed, mean_interarrival=4, mean_service=7,
            )
            expected.extend(
                result.result for result in compare_staffing(cases, agent_counts)
            )
        self.assertEqual([row.result for row in rows], expected)

    def test_generates_one_workload_per_seed(self):
        with mock.patch(
            "opslab.scenarios.generate_cases", wraps=generate_cases,
        ) as generate:
            run_paired_trials([2, 5, 8], [1, 2], case_count=4)

        self.assertEqual(generate.call_count, 3)
        self.assertEqual(
            [call.args[:2] for call in generate.call_args_list],
            [(4, 2), (4, 5), (4, 8)],
        )

    def test_inputs_are_not_modified(self):
        seeds = [3, 9]
        agent_counts = [4, 2]

        run_paired_trials(seeds, agent_counts, case_count=5)

        self.assertEqual(seeds, [3, 9])
        self.assertEqual(agent_counts, [4, 2])

    def test_invalid_seeds_are_rejected_before_generation(self):
        invalid = (None, [], [True], [1.5], [2, 2])
        for seeds in invalid:
            with self.subTest(seeds=seeds), mock.patch(
                "opslab.scenarios.generate_cases",
            ) as generate:
                with self.assertRaises(ValueError):
                    run_paired_trials(seeds, [1, 2], case_count=5)
                generate.assert_not_called()

    def test_invalid_agent_counts_are_rejected_before_generation(self):
        invalid = (None, [], [0, 2], [2, 2], [True, 2])
        for agent_counts in invalid:
            with self.subTest(agent_counts=agent_counts), mock.patch(
                "opslab.scenarios.generate_cases",
            ) as generate:
                with self.assertRaises(ValueError):
                    run_paired_trials([1, 2], agent_counts, case_count=5)
                generate.assert_not_called()

    def test_late_failure_does_not_return_partial_rows(self):
        with mock.patch(
            "opslab.scenarios.compare_staffing",
            side_effect=[compare_staffing(generate_cases(2, 1), [1]),
                         ValueError("late trial failed")],
        ):
            with self.assertRaisesRegex(ValueError, "late trial failed"):
                run_paired_trials([1, 2], [1], case_count=2)


if __name__ == "__main__":
    unittest.main()
