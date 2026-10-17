# OpsLab

A learning-oriented simulator for the operational cost of human and AI work.

## Current status
First increment: a reproducible human-only queue simulation, command-line interface,
and tests. No AI model, forecast, web app, cloud deployment, or production claims yet.
All generated cases are synthetic. Initial parameters are illustrative, not calibrated.

## Run (Python 3.10+; no third-party dependencies)
```sh
python -m opslab --cases 100 --agents 3 --seed 42
python -m unittest discover -s tests -v
```

## How it works
A min-heap stores agent availability. Cases are processed in arrival order. Each
case starts when both it and its assigned agent are available. Waiting time is
start minus arrival. Sorting costs O(n log n), assignments O(n log a), where a is
agent count. All cases finish; there is no abandonment or shift boundary yet.

## Planned investigation
Does AI automation still reduce cost after errors, rework, and human review?
Next: configurable workload assumptions, CSV export, scenario comparisons, data
validation, forecasting baselines, AI routing/rework, and an interactive view.

## Limitations
Independent exponential arrivals and service times do not represent a validated
real operation. This version omits breaks, language skills, quality, and costs.
Seeded repetition gives reproducibility, not statistical confidence.

## Development
Owned and directed by Igor, developed with AI assistance as an educational portfolio.
Authorship and measured results must be represented accurately. See docs/ROADMAP.md.
