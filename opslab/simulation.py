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


def _rate_from_mean(value: float, name: str) -> float:
    """Convert a positive finite mean in minutes to an exponential rate."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a positive finite number of minutes")
    try:
        valid = math.isfinite(value) and value > 0
        rate = 1 / value if valid else 0.0
    except OverflowError:
        valid, rate = False, 0.0
    if not valid or not math.isfinite(rate) or rate <= 0:
        raise ValueError(f"{name} must have a positive finite reciprocal rate")
    return rate


def generate_cases(count: int, seed: int = 42, *,
                   mean_interarrival: float = 2.0,
                   mean_service: float = 5.0) -> list[Case]:
    """Generate independent exponential gaps/services; means are in minutes.

    Defaults preserve the original seeded workload. Means must be positive and
    finite with representable reciprocal rates, even when count is zero.
    """
    if isinstance(count, bool) or not isinstance(count, int) or count < 0:
        raise ValueError("count must be a nonnegative integer")
    arrival_rate = _rate_from_mean(mean_interarrival, "mean_interarrival")
    service_rate = _rate_from_mean(mean_service, "mean_service")
    rng = Random(seed)
    arrival = 0.0
    cases = []
    for _ in range(count):
        arrival += rng.expovariate(arrival_rate)
        duration = rng.expovariate(service_rate)
        if not math.isfinite(arrival) or not math.isfinite(duration):
            raise ValueError("generated times overflowed; reduce workload means or count")
        cases.append(Case(arrival, duration))
    return cases
