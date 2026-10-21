"""Stable CSV serialization for OpsLab staffing comparisons."""
import csv
from collections.abc import Iterable
from io import StringIO

from .scenarios import StaffingResult


CSV_HEADER = (
    "agents",
    "cases",
    "mean_wait_minutes",
    "maximum_wait_minutes",
    "total_service_minutes",
    "final_completion_minutes",
)


def staffing_results_to_csv(rows: Iterable[StaffingResult]) -> str:
    """Return comparison rows as UTF-8-ready CSV with explicit time units.

    The fixed schema and LF line endings make identical inputs reproducible across
    platforms. Scenario order and numeric precision are preserved. This function
    does not modify the rows or their underlying workload.
    """
    output = StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(CSV_HEADER)
    for row in rows:
        result = row.result
        writer.writerow((
            row.agents,
            result.cases,
            result.mean_wait,
            result.maximum_wait,
            result.total_service_minutes,
            result.final_completion,
        ))
    return output.getvalue()
