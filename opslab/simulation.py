"""A small deterministic first-come-first-served queue simulator.

All times are minutes. Cases finish even after the arrival window closes.
This first increment models human processing only; AI and forecasts come later.
"""
from dataclasses import dataclass
import heapq
import math
from random import Random

@dataclass(frozen=True)
class Case:
    arrival: float
    duration: float

@dataclass(frozen=True)
class Result:
    cases: int
    mean_wait: float
    maximum_wait: float
    total_service_minutes: float
    final_completion: float


def simulate(cases: list[Case], agents: int) -> Result:
    """Assign each arriving case to the earliest available agent."""
    if isinstance(agents, bool) or not isinstance(agents, int) or agents < 1:
        raise ValueError("agents must be a positive integer")
    for case in cases:
        if not all(math.isfinite(x) and x >= 0 for x in (case.arrival, case.duration)):
            raise ValueError("arrival and duration must be finite and nonnegative")
    availability = [0.0] * agents
    waits = []
    total_service = 0.0
    completion = 0.0
    # Stable sort retains input order for simultaneous arrivals.
    for case in sorted(cases, key=lambda item: item.arrival):
        available = heapq.heappop(availability)
        start = max(available, case.arrival)
        finish = start + case.duration
        waits.append(start - case.arrival)
        total_service += case.duration
        completion = max(completion, finish)
        heapq.heappush(availability, finish)
    return Result(len(cases), sum(waits) / len(waits) if waits else 0.0,
                  max(waits, default=0.0), total_service, completion)


def generate_cases(count: int, seed: int = 42) -> list[Case]:
    """Generate synthetic arrivals with mean gap 2 and mean service time 5."""
    if isinstance(count, bool) or not isinstance(count, int) or count < 0:
        raise ValueError("count must be a nonnegative integer")
    rng = Random(seed)
    arrival = 0.0
    cases = []
    for _ in range(count):
        arrival += rng.expovariate(1 / 2)
        cases.append(Case(arrival, rng.expovariate(1 / 5)))
    return cases
