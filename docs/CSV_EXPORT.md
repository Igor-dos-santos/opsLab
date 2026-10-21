# Export staffing comparisons as CSV

Implemented with AI assistance. The CSV contains synthetic simulation results only.
Its fixed columns make units explicit and preserve scenario order:

| Column | Meaning | Unit |
| --- | --- | --- |
| `agents` | Available parallel agents | count |
| `cases` | Completed synthetic cases | count |
| `mean_wait_minutes` | Mean time before service starts | minutes |
| `maximum_wait_minutes` | Longest time before service starts | minutes |
| `total_service_minutes` | Sum of required service durations | minutes |
| `final_completion_minutes` | Latest case completion from time zero | minutes |

Generate one workload, compare staffing against it, then serialize the results:

```python
from opslab.export import staffing_results_to_csv
from opslab.scenarios import compare_staffing
from opslab.simulation import generate_cases

cases = generate_cases(100, 42)
rows = compare_staffing(cases, [2, 3, 4])
csv_text = staffing_results_to_csv(rows)

with open("staffing.csv", "w", encoding="utf-8", newline="") as output:
    output.write(csv_text)
```

The seed-42 example begins:

```csv
agents,cases,mean_wait_minutes,maximum_wait_minutes,total_service_minutes,final_completion_minutes
2,100,11.12260704571623,30.04467183254087,431.609365564085,248.91481607734613
3,100,0.9513027012401756,6.975970587585238,431.609365564085,236.49216502423639
4,100,0.20221891703524947,3.1841187056138835,431.609365564085,236.49216502423639
```

## Contract and tradeoffs

- The standard-library `csv` module produces RFC-style comma-separated fields;
  fixed LF line endings make identical results reproducible across platforms.
- The function accepts an iterable of `StaffingResult` records and emits the header
  even when the iterable is empty. It does not modify results or workload inputs.
- Python's numeric text representation is preserved instead of rounding away detail.
  Display rounding should be a separate presentation decision.
- All current fields are validated numeric values created by the simulator. If text
  fields are added later, spreadsheet formula injection must be considered before
  opening untrusted CSV data in spreadsheet software.
- The complete CSV is held in memory. A streaming writer may be preferable for large
  experiments, but current comparisons are intentionally small.
- There is no CLI CSV mode or file-path policy yet. Callers choose whether and where
  to persist the returned text, so the serializer itself performs no external writes.

This export is evidence from one synthetic model, not a staffing recommendation,
uncertainty estimate, cost calculation, or production benchmark.
