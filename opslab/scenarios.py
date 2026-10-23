"""Controlled staffing comparisons over one already-generated workload."""
from dataclasses import dataclass

from .simulation import Case, Result, generate_cases, simulate


@dataclass(frozen=True)
class StaffingResult:
    agents: int
    result: Result


@dataclass(frozen=True)
class TrialResult:
    seed: int
    agents: int
    result: Result


def _validate_agent_counts(agent_counts: list[int]) -> None:
    """Validate a complete staffing plan before any simulation starts."""
    if not isinstance(agent_counts, list) or not agent_counts:
        raise ValueError("agent_counts must be a nonempty list")
    seen = set()
    for agents in agent_counts:
        if isinstance(agents, bool) or not isinstance(agents, int) or agents < 1:
            raise ValueError("agent_counts must contain positive integers")
        if agents in seen:
            raise ValueError("agent_counts must be unique")
        seen.add(agents)


def compare_staffing(cases: list[Case], agent_counts: list[int]) -> list[StaffingResult]:
    """Reuse the exact case list for each distinct staffing count, in input order.

    Counts must be a nonempty list of unique positive integers, excluding bool.
    Validate all counts before running. Simulation errors propagate: the caller
    receives no partial comparison if any scenario fails. Neither input is changed.
    No randomness, cost model, optimization or uncertainty estimate is added here.
    """
    _validate_agent_counts(agent_counts)
    return [StaffingResult(agents, simulate(cases, agents)) for agents in agent_counts]


def run_paired_trials(seeds: list[int], agent_counts: list[int], *,
                      case_count: int, mean_interarrival: float = 2.0,
                      mean_service: float = 5.0) -> list[TrialResult]:
    """Run each staffing count against one shared workload for every seed.

    Seeds and staffing counts must be nonempty lists of unique integers; booleans
    are excluded. Output is ordered first by seed, then by staffing count. Each
    raw row records both identifiers and one simulation result. No aggregation,
    uncertainty estimate, optimization, or staffing recommendation is produced.
    """
    if not isinstance(seeds, list) or not seeds:
        raise ValueError("seeds must be a nonempty list")
    seen = set()
    for seed in seeds:
        if isinstance(seed, bool) or not isinstance(seed, int):
            raise ValueError("seeds must contain integers")
        if seed in seen:
            raise ValueError("seeds must be unique")
        seen.add(seed)
    _validate_agent_counts(agent_counts)

    rows = []
    for seed in seeds:
        cases = generate_cases(
            case_count,
            seed,
            mean_interarrival=mean_interarrival,
            mean_service=mean_service,
        )
        for comparison in compare_staffing(cases, agent_counts):
            rows.append(TrialResult(seed, comparison.agents, comparison.result))
    return rows
