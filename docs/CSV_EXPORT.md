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

The command line exposes the same controlled path and writes CSV to standard output:

```sh
python -m opslab --cases 100 --seed 42 --compare-agents 2 3 4
python -m opslab --cases 100 --seed 42 --compare-agents 2 3 4 > staffing.csv
```

`--compare-agents N [N ...]` is mutually exclusive with `--agents`. The workload
options apply to both modes. Comparison counts keep their requested order and must
be distinct positive integers. Invalid counts, invalid workload parameters, and
simulation failures produce a usage error on standard error, exit 2, and no partial
CSV on standard output. The original single-scenario mode continues to emit JSON.

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
- The CLI writes CSV to standard output rather than accepting a file path. Shell
  redirection lets the caller choose the destination and overwrite policy, while the
  application remains free of filesystem writes.

This export is evidence from one synthetic model, not a staffing recommendation,
uncertainty estimate, cost calculation, or production benchmark.

## Raw paired-trial CSV

Repeated paired trials use a separate seven-column schema so every observation keeps
its seed provenance:

```python
from opslab.export import trial_results_to_csv
from opslab.scenarios import run_paired_trials

rows = run_paired_trials([40, 41], [2, 3], case_count=5)
csv_text = trial_results_to_csv(rows)
```

```csv
seed,agents,cases,mean_wait_minutes,maximum_wait_minutes,total_service_minutes,final_completion_minutes
40,2,5,0.9182388876103434,3.64436787635948,22.67806530162165,16.185193651000027
40,3,5,0.0,0.0,22.67806530162165,15.23836708930779
41,2,5,1.656579807732431,4.24739550262702,26.140916818204612,15.619765177146832
41,3,5,0.0,0.0,26.140916818204612,13.579863941284975
```

The raw-trial serializer has the same deterministic line-ending, order-preservation,
numeric-representation and no-external-write policies as the single-workload
serializer. The same path is available from the command line:

```sh
python -m opslab --cases 100 --trial-seeds 40 41 42 --trial-agents 2 3 4
python -m opslab --cases 100 --trial-seeds 40 41 42 --trial-agents 2 3 4 > paired_trials.csv
```

Both trial options are required together. Trial mode is mutually exclusive with the
single-scenario and one-workload comparison modes, and it rejects `--seed` rather
than silently ignoring it. Inputs are fully validated and every trial completes before
the CSV is written to standard output. Failures produce exit 2 and an explanation on
standard error, with no partial CSV or traceback. The mode does not aggregate trials
or compute uncertainty.
