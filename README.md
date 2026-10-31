# OpsLab

A learning-oriented synthetic staffing simulator with a local browser interface.

## Current status
Current increment: a reproducible human-only queue simulation, configurable workload
means, controlled staffing comparisons, raw repeated paired trials, CSV serialization,
command-line and local browser interfaces, and tests. No AI model, forecast, cloud deployment,
or production claims yet. All generated cases are synthetic. Initial parameters are
illustrative, not calibrated.

## Local browser interface

From the extracted repository folder, run `python -m opslab.web` and open
`http://127.0.0.1:8000`. On macOS try `python3`; on Windows try `py` if needed.
No package installation is required. Use `--port 8001` if port 8000 is occupied.
Stop with Ctrl+C. This is local software, not a hosted demo.

Enter case count, worker counts, seeds and average durations. Select **Compare
staffing** for a table and bar chart, then download summary or raw-trial CSV.
See [the local interface guide](docs/LOCAL_INTERFACE.md) for setup, an example,
limits and troubleshooting.

## Run (Python 3.10+; no third-party dependencies)
```sh
python -m opslab --cases 100 --agents 3 --seed 42
python -m opslab --cases 100 --agents 3 --seed 42 --mean-interarrival 4 --mean-service 7
python -m opslab --cases 100 --seed 42 --compare-agents 2 3 4
python -m opslab --cases 100 --trial-seeds 40 41 42 --trial-agents 2 3 4
python -m opslab --cases 100 --summary-seeds 40 41 42 --trial-agents 2 3 4
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

Complete paired-trial rows can be summarized and serialized by staffing count in
Python:
```python
from opslab.export import summary_results_to_csv
from opslab.scenarios import summarize_mean_wait

summaries = summarize_mean_wait(rows)
csv_text = summary_results_to_csv(summaries)
```
The function returns the arithmetic average and observed minimum/maximum of the
per-trial mean waits. It requires a complete seed-by-agent matrix with no duplicate
pairs and one shared case count, and preserves first-seen staffing order. These are
descriptive statistics, not confidence intervals or staffing recommendations. The
five-column summary CSV preserves staffing order and numeric representations, uses
explicit minute units and LF line endings, and leaves raw rows unchanged.
`--summary-seeds N [N ...]` exposes the same pipeline from the command line when
paired with `--trial-agents`. It is mutually exclusive with the existing JSON,
single-workload comparison and raw-trial modes. All work completes before output is
written, so failures produce exit 2 without partial CSV or a traceback.
Both paired CLI modes reject experiments above 1,000,000 case-runs or 10,000 result
rows before generating a workload. A case-run is one case simulated for one
seed-agent pair; a result row is one seed-agent pair. These fixed safety limits bound
CPU work and accumulated output records, but they are not a benchmark or a promise
that every allowed experiment will meet a particular runtime or memory target.

Python callers can also retain one signed mean-wait difference per seed for a chosen
baseline and comparison:
```python
from opslab.scenarios import paired_mean_wait_differences

differences = paired_mean_wait_differences(
    rows, baseline_agents=2, comparison_agents=4,
)
```
Each record contains both observed means and `comparison_minus_baseline_minutes`.
Negative values mean lower mean wait for the comparison within that synthetic seed.
The complete paired matrix is validated first. This API performs no aggregation,
uncertainty interval, hypothesis test, optimization or recommendation. See the
[paired uncertainty method design](docs/UNCERTAINTY_METHOD.md).

Raw trial rows can be serialized with their seed provenance and explicit units:
```python
from opslab.export import trial_results_to_csv

csv_text = trial_results_to_csv(rows)
with open("paired_trials.csv", "w", encoding="utf-8", newline="") as output:
    output.write(csv_text)
```
The seven columns are `seed`, `agents`, `cases`, `mean_wait_minutes`,
`maximum_wait_minutes`, `total_service_minutes`, and
`final_completion_minutes`. Serialization preserves raw row order and numeric
representations, uses LF line endings, and includes the header for empty input.
It performs no aggregation or external write. The command-line mode requires both
`--trial-seeds` and `--trial-agents`; it is mutually exclusive with `--agents` and
`--compare-agents`, and the single-workload `--seed` option is rejected in trial
mode. All trials finish before the complete CSV is written, so validation, workload,
or simulation failures exit 2 without partial standard output or a traceback.

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
The first release focuses on usable synthetic staffing comparisons. Next: complete
the five-minute demo and release verification. Forecasting, AI routing/rework, costs
and inferential intervals are deferred; existing calculations remain available.

## Limitations
Independent exponential arrivals and service times do not represent a validated
real operation. This version omits breaks, language skills, quality, and costs.
Raw repeated seeds improve experimental coverage but do not by themselves provide
statistical confidence, calibrated uncertainty, or external validity.

## Development
Owned and directed by Igor, developed with AI assistance as an educational portfolio.
Authorship and measured results must be represented accurately. See docs/ROADMAP.md.
