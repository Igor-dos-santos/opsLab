import argparse
from dataclasses import asdict
import json
from .simulation import generate_cases, simulate

def main():
    parser = argparse.ArgumentParser(description="Simulate synthetic support cases")
    parser.add_argument("--cases", type=int, default=100)
    parser.add_argument("--agents", type=int, default=3)
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
        result = simulate(cases, args.agents)
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps(asdict(result), indent=2))

if __name__ == "__main__":
    main()
