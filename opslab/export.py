"""Stable CSV serialization for OpsLab staffing comparisons and trial results."""
import csv
from collections.abc import Iterable
from io import StringIO

from .scenarios import StaffingResult, TrialResult, TrialWaitSummary


CSV_HEADER = (
    "agents",
    "cases",
    "mean_wait_minutes",
    "maximum_wait_minutes",
    "total_service_minutes",
    "final_completion_minutes",
)

TRIAL_CSV_HEADER = (
    "seed",
    "agents",
    "cases",
    "mean_wait_minutes",
    "maximum_wait_minutes",
    "total_service_minutes",
    "final_completion_minutes",
)

SUMMARY_CSV_HEADER = (
    "agents",
    "trials",
    "average_mean_wait_minutes",
    "minimum_mean_wait_minutes",
    "maximum_mean_wait_minutes",
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


def trial_results_to_csv(rows: Iterable[TrialResult]) -> str:
    """Return raw paired-trial rows as deterministic, unit-bearing CSV.

    Seed and staffing provenance, input order, and Python numeric representations
    are preserved. Even an empty iterable returns the fixed header. This function
    does not aggregate, estimate uncertainty, modify rows, or write files.
    """
    output = StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(TRIAL_CSV_HEADER)
    for row in rows:
        result = row.result
        writer.writerow((
            row.seed,
            row.agents,
            result.cases,
            result.mean_wait,
            result.maximum_wait,
            result.total_service_minutes,
            result.final_completion,
        ))
    return output.getvalue()


def summary_results_to_csv(rows: Iterable[TrialWaitSummary]) -> str:
    """Return descriptive wait summaries as deterministic, unit-bearing CSV.

    Staffing order and Python numeric representations are preserved. Even an empty
    iterable returns the fixed header. This function does not calculate summaries,
    estimate uncertainty, modify rows, or write files.
    """
    output = StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(SUMMARY_CSV_HEADER)
    for row in rows:
        writer.writerow((
            row.agents,
            row.trials,
            row.average_mean_wait_minutes,
            row.minimum_mean_wait_minutes,
            row.maximum_mean_wait_minutes,
        ))
    return output.getvalue()
