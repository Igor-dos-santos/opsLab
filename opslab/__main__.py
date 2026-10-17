import argparse
from dataclasses import asdict
import json
from .simulation import generate_cases, simulate

def main():
    parser = argparse.ArgumentParser(description="Simulate synthetic support cases")
    parser.add_argument("--cases", type=int, default=100)
    parser.add_argument("--agents", type=int, default=3)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    try:
        result = simulate(generate_cases(args.cases, args.seed), args.agents)
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps(asdict(result), indent=2))

if __name__ == "__main__":
    main()
