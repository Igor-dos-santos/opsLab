"""Controlled staffing comparisons over one already-generated workload."""
from dataclasses import dataclass

from .simulation import Case, Result, simulate


@dataclass(frozen=True)
class StaffingResult:
    agents: int
    result: Result


def compare_staffing(cases: list[Case], agent_counts: list[int]) -> list[StaffingResult]:
    """Reuse the exact case list for each distinct staffing count, in input order.

    Counts must be a nonempty list of unique positive integers, excluding bool.
    Validate all counts before running. Simulation errors propagate: the caller
    receives no partial comparison if any scenario fails. Neither input is changed.
    No randomness, cost model, optimization or uncertainty estimate is added here.
    """
    if not isinstance(agent_counts, list) or not agent_counts:
        raise ValueError("agent_counts must be a nonempty list")
    seen = set()
    for agents in agent_counts:
        if isinstance(agents, bool) or not isinstance(agents, int) or agents < 1:
            raise ValueError("agent_counts must contain positive integers")
        if agents in seen:
            raise ValueError("agent_counts must be unique")
        seen.add(agents)
    return [StaffingResult(agents, simulate(cases, agents)) for agents in agent_counts]
