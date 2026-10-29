import argparse
from dataclasses import asdict
import json

from .export import (
    staffing_results_to_csv,
    summary_results_to_csv,
    trial_results_to_csv,
)
from .scenarios import (
    compare_staffing,
    run_paired_trials,
    summarize_mean_wait,
)
from .simulation import generate_cases, simulate


MAX_PAIRED_CASE_RUNS = 1_000_000
MAX_PAIRED_RESULT_ROWS = 10_000


def _validate_paired_experiment_budget(case_count, seeds, agent_counts):
    """Reject oversized paired CLI work before workload generation."""
    result_rows = len(seeds) * len(agent_counts)
    if result_rows > MAX_PAIRED_RESULT_ROWS:
        raise ValueError(
            "paired experiment budget allows at most "
            f"{MAX_PAIRED_RESULT_ROWS} result rows; requested {result_rows}"
        )
    case_runs = case_count * result_rows
    if case_runs > MAX_PAIRED_CASE_RUNS:
        raise ValueError(
            "paired experiment budget allows at most "
            f"{MAX_PAIRED_CASE_RUNS} case-runs; requested {case_runs}"
        )


def main():
    parser = argparse.ArgumentParser(
        description="Simulate synthetic support cases",
        epilog=(
            "Paired CLI modes allow at most 1000000 case-runs and "
            "10000 result rows per command."
        ),
    )
    parser.add_argument("--cases", type=int, default=100)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--agents", type=int, default=3,
                      help="agents for one JSON simulation (default: 3)")
    mode.add_argument("--compare-agents", type=int, nargs="+", metavar="N",
                      help="compare agent counts on the same workload and emit CSV")
    mode.add_argument("--trial-seeds", type=int, nargs="+", metavar="N",
                      help="run paired workloads for these seeds and emit CSV")
    mode.add_argument(
        "--summary-seeds", type=int, nargs="+", metavar="N",
        help="run paired workloads for these seeds and emit descriptive summary CSV",
    )
    parser.add_argument("--trial-agents", type=int, nargs="+", metavar="N",
                        help="agent counts for paired trial or summary modes")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--mean-interarrival", type=float, default=2.0,
                        help="mean gap between arrivals in minutes (default: 2)")
    parser.add_argument("--mean-service", type=float, default=5.0,
                        help="mean service duration in minutes (default: 5)")
    args = parser.parse_args()
    paired_seeds = (
        args.trial_seeds
        if args.trial_seeds is not None
        else args.summary_seeds
    )
    if paired_seeds is None and args.trial_agents is not None:
        parser.error("--trial-agents requires --trial-seeds or --summary-seeds")
    if args.trial_seeds is not None and args.trial_agents is None:
        parser.error("--trial-seeds requires --trial-agents")
    if args.summary_seeds is not None and args.trial_agents is None:
        parser.error("--summary-seeds requires --trial-agents")
    if args.trial_seeds is not None and args.seed is not None:
        parser.error("--seed cannot be used with --trial-seeds")
    if args.summary_seeds is not None and args.seed is not None:
        parser.error("--seed cannot be used with --summary-seeds")
    try:
        if paired_seeds is not None:
            _validate_paired_experiment_budget(
                args.cases, paired_seeds, args.trial_agents,
            )
            rows = run_paired_trials(
                paired_seeds,
                args.trial_agents,
                case_count=args.cases,
                mean_interarrival=args.mean_interarrival,
                mean_service=args.mean_service,
            )
            if args.summary_seeds is None:
                output = trial_results_to_csv(rows)
            else:
                output = summary_results_to_csv(summarize_mean_wait(rows))
        else:
            cases = generate_cases(
                args.cases,
                42 if args.seed is None else args.seed,
                mean_interarrival=args.mean_interarrival,
                mean_service=args.mean_service,
            )
            if args.compare_agents is None:
                output = json.dumps(asdict(simulate(cases, args.agents)), indent=2) + "\n"
            else:
                rows = compare_staffing(cases, args.compare_agents)
                output = staffing_results_to_csv(rows)
    except ValueError as error:
        parser.error(str(error))
    print(output, end="")


if __name__ == "__main__":
    main()
