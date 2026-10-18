# OpsLab

A learning-oriented simulator for the operational cost of human and AI work.

## Current status
Current increment: a reproducible human-only queue simulation, configurable workload
means, command-line interface, and tests. No AI model, forecast, web app, cloud
deployment, or production claims yet.
All generated cases are synthetic. Initial parameters are illustrative, not calibrated.

## Run (Python 3.10+; no third-party dependencies)
```sh
python -m opslab --cases 100 --agents 3 --seed 42
python -m opslab --cases 100 --agents 3 --seed 42 --mean-interarrival 4 --mean-service 7
python -m unittest discover -s tests -v
```

Both workload means are in **minutes**, not rates. Defaults are a 2-minute
interarrival gap and 5-minute service duration, preserving the original seeded
results. The exponential rate is the reciprocal of the mean: a 4-minute mean
gap uses rate 0.25 per minute. Means must be positive finite numbers with finite
positive reciprocal rates, including for an empty workload. Invalid CLI values
produce an argument error (exit 2). Generated non-finite times are rejected.

Python callers can use keyword-only options:
```python
from opslab.simulation import generate_cases, simulate

cases = generate_cases(100, 42, mean_interarrival=4, mean_service=7)
result = simulate(cases, agents=3)
```

These are distribution expectations, not exact sample averages. Reuse the same
case list when comparing staffing; changing both demand and staffing confounds
the comparison. No staffing-comparison command has been added yet.

## How it works
A min-heap stores agent availability. Cases are processed in arrival order. Each
case starts when both it and its assigned agent are available. Waiting time is
start minus arrival. Sorting costs O(n log n), assignments O(n log a), where a is
agent count. All cases finish; there is no abandonment or shift boundary yet.

## Planned investigation
Does AI automation still reduce cost after errors, rework, and human review?
Next: CSV export, scenario comparisons, additional data
validation, forecasting baselines, AI routing/rework, and an interactive view.

## Limitations
Independent exponential arrivals and service times do not represent a validated
real operation. This version omits breaks, language skills, quality, and costs.
Seeded repetition gives reproducibility, not statistical confidence.

## Development
Owned and directed by Igor, developed with AI assistance as an educational portfolio.
Authorship and measured results must be represented accurately. See docs/ROADMAP.md.
