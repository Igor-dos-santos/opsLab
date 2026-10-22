import argparse
from dataclasses import asdict
import json

from .export import staffing_results_to_csv
from .scenarios import compare_staffing
from .simulation import generate_cases, simulate


def main():
    parser = argparse.ArgumentParser(description="Simulate synthetic support cases")
    parser.add_argument("--cases", type=int, default=100)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--agents", type=int, default=3,
                      help="agents for one JSON simulation (default: 3)")
    mode.add_argument("--compare-agents", type=int, nargs="+", metavar="N",
                      help="compare agent counts on the same workload and emit CSV")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--mean-interarrival", type=float, default=2.0,
                        help="mean gap between arrivals in minutes (default: 2)")
    parser.add_argument("--mean-service", type=float, default=5.0,
                        help="mean service duration in minutes (default: 5)")
    args = parser.parse_args()
    try:
        cases = generate_cases(args.cases, args.seed,
                               mean_interarrival=args.mean_interarrival,
                               mean_service=args.mean_service)
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
