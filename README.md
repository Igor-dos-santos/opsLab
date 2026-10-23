# OpsLab

A learning-oriented simulator for the operational cost of human and AI work.

## Current status
Current increment: a reproducible human-only queue simulation, configurable workload
means, controlled staffing comparisons, raw repeated paired trials, CSV serialization,
command-line interface, and tests. No AI model, forecast, web app, cloud deployment,
or production claims yet. All generated cases are synthetic. Initial parameters are
illustrative, not calibrated.

## Run (Python 3.10+; no third-party dependencies)
```sh
python -m opslab --cases 100 --agents 3 --seed 42
python -m opslab --cases 100 --agents 3 --seed 42 --mean-interarrival 4 --mean-service 7
python -m opslab --cases 100 --seed 42 --compare-agents 2 3 4
python -m unittest discover -s tests -v
```

Both workload means are in **minutes**, not rates. Defaults are a 2-minute
interarrival gap and 5-minute service duration, preserving the original seeded
results. The exponential rate is the reciprocal of the mean: a 4-minute mean
gap uses rate 0.25 per minute. Means must be positive finite numbers with finite
positive reciprocal rates, including for an empty workload. Invalid CLI values
produce an argument error (exit 2). Generated non-finite times are rejected.
Simulation also rejects overflow of completion times, total service, or total
waiting time with ValueError (CLI exit 2). Finite inputs alone cannot guarantee
finite sums. This conservative policy rejects an overflowing total wait even
when dividing it by the case count could yield a representable mean; arbitrary
precision arithmetic and overflow-resistant averaging are not implemented.

Python callers can use keyword-only options:
```python
from opslab.simulation import generate_cases, simulate

cases = generate_cases(100, 42, mean_interarrival=4, mean_service=7)
result = simulate(cases, agents=3)
```

These are distribution expectations, not exact sample averages. Reuse the same
case list when comparing staffing; changing both demand and staffing confounds
the comparison. The Python API now supports controlled staffing comparisons:
```python
from opslab.scenarios import compare_staffing

for row in compare_staffing(cases, [2, 3, 4]):
    print(row.agents, row.result.mean_wait, row.result.total_service_minutes)
```
Counts must be a nonempty list of distinct positive integers (not booleans).
Results preserve count order; all scenarios use the identical case list and
neither input is modified. Any simulation error aborts the call rather than
returning partial results. `--compare-agents N [N ...]` generates the workload once
and emits CSV only. It is mutually exclusive with the single-scenario `--agents`
option; invalid comparisons exit 2 without partial CSV or a traceback.
See [the reproducible experiment](docs/STAFFING_COMPARISON.md) for results and limits.

Python callers can repeat the controlled comparison across explicit seeds:
```python
from opslab.scenarios import run_paired_trials

rows = run_paired_trials([40, 41, 42], [2, 3, 4], case_count=100)
for row in rows:
    print(row.seed, row.agents, row.result.mean_wait)
```
The function generates one workload per seed, applies every requested staffing count
to that workload, and records a raw row with the seed and agent count. Seeds and
agent counts are unique nonempty integer lists, booleans excluded. Order is seed-first,
then agent-count order. The function returns no partial list if a later trial fails.
It does not aggregate results or estimate uncertainty. See
[raw paired trials](docs/PAIRED_TRIALS.md).

Comparison results can be serialized with a fixed, unit-bearing CSV schema:
```python
from opslab.export import staffing_results_to_csv

rows = compare_staffing(cases, [2, 3, 4])
csv_text = staffing_results_to_csv(rows)
with open("staffing.csv", "w", encoding="utf-8", newline="") as output:
    output.write(csv_text)
```
The columns are `agents`, `cases`, `mean_wait_minutes`,
`maximum_wait_minutes`, `total_service_minutes`, and
`final_completion_minutes`. Row order and full Python numeric representations are
preserved, and even an empty result set includes the header. Output uses LF line
endings for cross-platform reproducibility. The serializer and CLI hold the complete
CSV in memory. See [CSV export](docs/CSV_EXPORT.md).

## How it works
A min-heap stores agent availability. Cases are processed in arrival order. Each
case starts when both it and its assigned agent are available. Waiting time is
start minus arrival. Sorting costs O(n log n), assignments O(n log a), where a is
agent count. All cases finish; there is no abandonment or shift boundary yet.

## Planned investigation
Does AI automation still reduce cost after errors, rework, and human review?
Next: paired-trial CSV serialization, uncertainty summaries, additional data
validation, forecasting baselines, AI routing/rework, and an interactive view.

## Limitations
Independent exponential arrivals and service times do not represent a validated
real operation. This version omits breaks, language skills, quality, and costs.
Raw repeated seeds improve experimental coverage but do not by themselves provide
statistical confidence, calibrated uncertainty, or external validity.

## Development
Owned and directed by Igor, developed with AI assistance as an educational portfolio.
Authorship and measured results must be represented accurately. See docs/ROADMAP.md.
