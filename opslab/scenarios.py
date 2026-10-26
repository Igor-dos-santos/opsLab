"""Controlled staffing comparisons over one already-generated workload."""
from dataclasses import dataclass
import math

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


@dataclass(frozen=True)
class TrialWaitSummary:
    agents: int
    trials: int
    average_mean_wait_minutes: float
    minimum_mean_wait_minutes: float
    maximum_mean_wait_minutes: float


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


def summarize_mean_wait(rows: list[TrialResult]) -> list[TrialWaitSummary]:
    """Describe per-agent mean waits across a complete paired-trial matrix.

    Returns the arithmetic average and observed minimum/maximum of each trial's
    mean wait. Every seed must contain exactly one row for every staffing count,
    and every row must use the same case count. Summary order follows the first
    occurrence of each staffing count. This is descriptive aggregation only: it
    does not estimate uncertainty or recommend staffing.
    """
    if not isinstance(rows, list) or not rows:
        raise ValueError("rows must be a nonempty list")

    agent_order = []
    values_by_agent = {}
    agents_by_seed = {}
    pairs = set()
    case_count = None
    for row in rows:
        if not isinstance(row, TrialResult):
            raise ValueError("rows must contain TrialResult records")
        if isinstance(row.seed, bool) or not isinstance(row.seed, int):
            raise ValueError("trial seeds must be integers")
        if (isinstance(row.agents, bool) or not isinstance(row.agents, int)
                or row.agents < 1):
            raise ValueError("trial agents must be positive integers")
        if not isinstance(row.result, Result):
            raise ValueError("trial results must contain Result records")
        if (isinstance(row.result.cases, bool)
                or not isinstance(row.result.cases, int)
                or row.result.cases < 0):
            raise ValueError("trial case counts must be nonnegative integers")
        if case_count is None:
            case_count = row.result.cases
        elif row.result.cases != case_count:
            raise ValueError("trial rows must use the same case count")
        mean_wait = row.result.mean_wait
        if (isinstance(mean_wait, bool)
                or not isinstance(mean_wait, (int, float))
                or not math.isfinite(mean_wait)
                or mean_wait < 0):
            raise ValueError("trial mean waits must be finite and nonnegative")

        pair = (row.seed, row.agents)
        if pair in pairs:
            raise ValueError("rows contain a duplicate seed-agent pair")
        pairs.add(pair)
        agents_by_seed.setdefault(row.seed, set()).add(row.agents)
        if row.agents not in values_by_agent:
            agent_order.append(row.agents)
            values_by_agent[row.agents] = []
        values_by_agent[row.agents].append(mean_wait)

    expected_agents = set(agent_order)
    if any(agents != expected_agents for agents in agents_by_seed.values()):
        raise ValueError("rows must contain one result for every seed and agent")

    summaries = []
    for agents in agent_order:
        values = values_by_agent[agents]
        trials = len(values)
        average = math.fsum(value / trials for value in values)
        summaries.append(TrialWaitSummary(
            agents,
            trials,
            average,
            min(values),
            max(values),
        ))
    return summaries
