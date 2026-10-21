import unittest

from opslab.export import CSV_HEADER, staffing_results_to_csv
from opslab.scenarios import compare_staffing
from opslab.simulation import Case, generate_cases


class StaffingCsvTests(unittest.TestCase):
    def test_hand_calculated_results_have_stable_schema_and_values(self):
        rows = compare_staffing(
            [Case(2, 1), Case(0, 4), Case(1, 2)],
            [2, 1],
        )

        output = staffing_results_to_csv(rows)

        self.assertEqual(
            output,
            "agents,cases,mean_wait_minutes,maximum_wait_minutes,"
            "total_service_minutes,final_completion_minutes\n"
            "2,3,0.3333333333333333,1,7.0,4.0\n"
            "1,3,2.3333333333333335,4.0,7.0,7.0\n",
        )

    def test_empty_results_still_include_the_header(self):
        self.assertEqual(
            staffing_results_to_csv([]),
            ",".join(CSV_HEADER) + "\n",
        )

    def test_serialization_preserves_scenario_order_and_values(self):
        cases = generate_cases(10, 42)
        rows = compare_staffing(cases, [4, 2, 3])
        original_rows = rows.copy()

        lines = staffing_results_to_csv(rows).splitlines()

        self.assertEqual([line.split(",")[0] for line in lines[1:]], ["4", "2", "3"])
        self.assertEqual(rows, original_rows)

    def test_serialization_does_not_modify_comparison_inputs(self):
        cases = generate_cases(10, 42)
        original_cases = cases.copy()
        counts = [2, 3]
        rows = compare_staffing(cases, counts)

        staffing_results_to_csv(rows)

        self.assertEqual(cases, original_cases)
        self.assertEqual(counts, [2, 3])

    def test_output_uses_lf_line_endings_for_reproducibility(self):
        rows = compare_staffing([], [1])

        output = staffing_results_to_csv(rows)

        self.assertNotIn("\r", output)
        self.assertEqual(output.count("\n"), 2)


if __name__ == "__main__":
    unittest.main()
