# Raw repeated paired trials

`run_paired_trials` repeats a controlled staffing comparison across an explicit list
of pseudorandom seeds. For each seed, OpsLab generates one synthetic workload and
reuses that exact case list for every requested staffing count. Each raw result records
both the seed and agent count so the pairing remains visible to later analysis.

```python
from opslab.scenarios import run_paired_trials

rows = run_paired_trials([40, 41, 42], [2, 3, 4], case_count=100)
for row in rows:
    print(row.seed, row.agents, row.result.mean_wait,
          row.result.total_service_minutes)
```

Verified output from that example:

| seed | agents | mean wait (minutes) | total service (minutes) |
|---:|---:|---:|---:|
| 40 | 2 | 27.506653779978755 | 461.1749923638263 |
| 40 | 3 | 2.617174611281678 | 461.1749923638263 |
| 40 | 4 | 0.4203653620671025 | 461.1749923638263 |
| 41 | 2 | 63.88369229370024 | 574.9463819546643 |
| 41 | 3 | 19.756955845567838 | 574.9463819546643 |
| 41 | 4 | 2.7904431154731766 | 574.9463819546643 |
| 42 | 2 | 11.12260704571623 | 431.609365564085 |
| 42 | 3 | 0.9513027012401756 | 431.609365564085 |
| 42 | 4 | 0.20221891703524947 | 431.609365564085 |

## Contract

- `seeds` and `agent_counts` are nonempty lists of unique integers; booleans are
  rejected. Agent counts must be positive. Negative seeds are valid inputs to
  Python's deterministic pseudorandom generator.
- Output order is seed order first, then agent-count order. Inputs are not modified.
- Workload options are passed to `generate_cases` for every seed.
- All staffing counts are validated before any workload is generated.
- A generation or simulation failure raises `ValueError`; the caller receives no
  partial result list.
- The API holds every raw result in memory and currently has no CLI or CSV mode.

## Interpretation and limits

Pairing reduces noise in comparisons because staffing alternatives face the same
workload within each seed. Differences between seeds show that one reproducible draw
is not a stable basis for a staffing conclusion. The raw rows are evidence that the
experiment ran, not an uncertainty estimate or optimization result.

The seed list is chosen by the caller and is not a probability sample of real support
operations. The synthetic arrival and service assumptions remain uncalibrated. No
confidence interval, hypothesis test, multiple-comparison correction, cost model,
quality model, abandonment behavior, or AI/rework behavior is implemented. Do not use
these rows as a production staffing recommendation.
