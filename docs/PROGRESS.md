# Progress

## 2026-10-22: Comparison CSV command-line mode

Implemented with AI assistance, preserving existing attribution.
Base: [bc1319c9ba011d2ae0fd4d2838a5648c13ea9d25](https://github.com/Igor-dos-santos/opsLab/commit/bc1319c9ba011d2ae0fd4d2838a5648c13ea9d25).
This increment's commit is available in
[file history](https://github.com/Igor-dos-santos/opsLab/commits/main/docs/PROGRESS.md).

Added `--compare-agents N [N ...]` to the existing CLI. Comparison mode generates
one workload, reuses it for every requested staffing count, and writes only the
existing unit-bearing CSV schema to standard output. It is mutually exclusive with
the single-scenario `--agents` JSON mode. Invalid counts, workload errors and
simulation failures exit 2 through argparse without partial CSV or tracebacks.
There is no file-path or overwrite policy; callers can use shell redirection.

Local evidence from the project root:
- `python -m unittest discover -s tests -v`: baseline 36 tests passed.
- Before implementation, five focused CLI tests ran and four failed because
  `--compare-agents` was unrecognized. The invalid-count test initially passed for
  the wrong reason because it accepted any usage error; its assertions were tightened
  to require the domain messages `positive integers` or `unique`.
- After implementation, all six focused CLI tests passed and the complete suite
  passed 42 tests. They cover exact CSV and requested order with custom workload
  means, mutually exclusive modes, invalid counts without partial output, workload
  and simulation failure propagation, and help text.
- `python -m opslab --cases 100 --agents 3 --seed 42`: exit 0 with the unchanged
  JSON mean wait 0.9513027012401756 and completion 236.49216502423639 minutes.
- `python -m opslab --cases 100 --seed 42 --compare-agents 2 3 4`: exit 0 with
  CSV mean waits 11.12260704571623, 0.9513027012401756 and 0.20221891703524947
  minutes. Total service remained 431.609365564085 minutes in every row.
- `python -m compileall -q opslab tests` and `git diff --check`: passed before
  publication.

Concepts: mutually exclusive CLI modes, stdout versus stderr contracts, exit codes,
machine-readable output, same-workload experimental control and regression tests.
The command holds the workload, scenario results and CSV string in memory, and there
are no explicit resource caps. Local tests are not CI evidence. No release or hosted
demo is claimed. Only synthetic data and sanitized documentation were added. No
learner understanding is inferred.

Next bounded task: add raw repeated paired trials that record seed and staffing count
without yet claiming uncertainty or optimal staffing. Forecasting, AI/rework, costs,
uncertainty summaries and an interface remain later milestones.

## 2026-10-21: Unit-bearing CSV serialization

Implemented with AI assistance, preserving existing attribution.
Base: [b43e78c7c55cb490ea6df183ec4140017e3f46e7](https://github.com/Igor-dos-santos/opsLab/commit/b43e78c7c55cb490ea6df183ec4140017e3f46e7).
This increment's commit is available in
[file history](https://github.com/Igor-dos-santos/opsLab/commits/main/docs/PROGRESS.md).

Added `opslab.export.staffing_results_to_csv`, a standard-library CSV serializer
for staffing comparison records. Its six fixed columns distinguish counts from
minute-based metrics, preserve scenario order and numeric representations, always
include a header, and use LF line endings. The serializer has no external writes,
does not modify results or workloads, and introduces no dependency or CLI change.

Local evidence from the project root:
- `python -m unittest discover -s tests -v`: baseline 31 tests passed.
- Test-first discovery of `test_export.py` failed with `ModuleNotFoundError` before
  `opslab.export` existed. After implementation, five focused tests passed and the
  complete suite passed 36 tests.
- Exported the existing 100-case, seed-42 comparison for 2/3/4 agents. The CSV
  preserved mean waits 11.12260704571623, 0.9513027012401756 and
  0.20221891703524947 minutes, with total service 431.609365564085 minutes in every
  row. This confirms serialization of the controlled example, not model accuracy.
- `python -m opslab --cases 100 --agents 3 --seed 42`: exit 0 with unchanged mean
  wait 0.9513027012401756 and final completion 236.49216502423639 minutes.
- `git diff --check`: passed before publication.

Concepts: stable data contracts, explicit units, deterministic serialization,
separation of computation from persistence, invariants and test-first development.
Only numeric simulator fields are exported; future text fields need spreadsheet
formula-injection analysis. Output is held in memory, no CLI CSV mode exists, and
local tests are not CI evidence. No release or hosted demo is claimed. Only synthetic
data and sanitized documentation were added. No learner understanding is inferred.

Next bounded task: add an explicit CLI comparison mode that emits the same CSV schema
without mixing human-readable and machine-readable output. Repeated paired trials,
forecasting, AI/rework, costs, uncertainty and an interface remain later milestones.

## 2026-10-20: Same-workload staffing comparison API

Implemented with AI assistance, preserving existing attribution.
Base: [553e0c3efc29a72d585fcbfc685f09585920dccd](https://github.com/Igor-dos-santos/opsLab/commit/553e0c3efc29a72d585fcbfc685f09585920dccd).
This increment's commit is available in
[file history](https://github.com/Igor-dos-santos/opsLab/commits/main/docs/PROGRESS.md).

Added `opslab.scenarios.compare_staffing` and frozen StaffingResult records. The
API reuses the identical caller-supplied case list for every agent count, preserves
count order and input lists, validates all counts before running, and propagates
simulation failures without returning partial comparison rows. No new CLI mode,
cost model, randomness, dependency, AI or deployment was added.

Local evidence from the project root:
- `python -m unittest discover -s tests -v`: baseline 24 tests passed.
- Test-first discovery of test_scenarios.py failed with ModuleNotFoundError before
  the new scenarios module existed. This was missing implementation, not a
  numerical regression. After implementation, the full command passed 31 tests.
- Seven added tests cover hand-calculated staffing outcomes and unchanged input,
  identical case-list identity across runs, seeded repeatability/direct-result
  equivalence and service conservation, invalid counts rejected before simulation,
  empty workloads, invalid cases and late-scenario overflow propagation.
- Ran the Python example in docs/STAFFING_COMPARISON.md, generating 100 cases with
  seed 42 once. Mean waits for 2/3/4 agents: 11.12260704571623,
  0.9513027012401756, 0.20221891703524947 minutes. Each total service:
  431.609365564085 minutes. Full metrics and interpretation are in that document.
- `python -m opslab --cases 100 --agents 3 --seed 42`: exit 0 with unchanged
  default mean wait 0.9513027012401756 and completion 236.49216502423639 minutes.

Concepts: controlled experiments, separation of workload generation and scenarios,
structured results, validation-before-work, failure propagation and invariants.
No external blocker found. Local tests are not CI evidence; no hosted demo verified.
Only synthetic data and sanitized technical documentation were added.
Next bounded task: CSV export of comparison results with explicit units and tests.
Repeated paired trials, CLI comparison integration, forecasts, AI/rework, costs,
uncertainty and interface remain later milestones. No project release or learner
understanding is inferred from this implementation.

## 2026-10-19: Reject simulation arithmetic overflow

Implemented with AI assistance, preserving the existing public attribution.
Base: [84008a7b63a8bf91b0483a8943a9af1c9eeea99f](https://github.com/Igor-dos-santos/opsLab/commit/84008a7b63a8bf91b0483a8943a9af1c9eeea99f).
This increment's commit is discoverable in
[file history](https://github.com/Igor-dos-santos/opsLab/commits/main/docs/PROGRESS.md).

Scope: reject non-finite completion times, service totals and waiting totals
instead of returning infinity. No comparison engine, AI, dependency or deployment
was added. Normal queue behavior and seeded results remain unchanged.

Evidence from the project root:
- Baseline `python -m unittest discover -s tests -v`: 17 tests passed.
- Before the fix, `python -m unittest discover -s tests -p test_boundaries.py -v`:
  six new tests ran; three failed because overflow did not raise ValueError.
  Reproductions isolate completion overflow (`Case(1e308, 1e308)`), service-total
  overflow (two `Case(0, 1e308)` with two agents), and wait-total overflow
  (`Case(0, 1e308)` followed by two zero-duration cases, one agent).
- After the fix, `python -m unittest discover -s tests -v`: 24 tests passed.
  Seven new tests include the three overflow regressions, large representable
  results, zero durations/idle gaps, unchanged input order with a hand-calculated
  two-agent result, and CLI overflow exit 2 without JSON output or traceback.
- `python -m opslab --cases 100 --agents 3 --seed 42`: exit 0; mean wait
  0.9513027012401756, maximum wait 6.975970587585238, total service
  431.609365564085, final completion 236.49216502423639 minutes, unchanged.

Concepts: input versus derived-value validation, floating-point overflow,
red/green regression tests, queue invariants and CLI error propagation.
Policy: reject any overflowing aggregate, even if a different averaging algorithm
could represent the final mean. No arbitrary precision or numeric-type expansion.
These checks do not address floating-point rounding or resource exhaustion.

Validation is local, not CI evidence. No hosted demo is verified. Source and docs:
[repository](https://github.com/Igor-dos-santos/opsLab). No external blocker found.
Next bounded task: document and test staffing comparisons on the same generated
workload, preserving service workload and reporting synthetic assumptions.
CSV export, forecasts, AI/rework, uncertainty experiments and interface remain.

## 2026-10-18: Configurable workload means

Implemented with AI assistance, following the existing public attribution.
Base: [dd6394d667f984a605723a5d5393013cd7ab3f7e](https://github.com/Igor-dos-santos/opsLab/commit/dd6394d667f984a605723a5d5393013cd7ab3f7e).
The commit containing this entry is discoverable in
[file history](https://github.com/Igor-dos-santos/opsLab/commits/main/docs/PROGRESS.md).

Scope: keyword-only mean_interarrival and mean_service parameters plus matching
CLI flags, with minutes documented explicitly. Existing defaults and draw order
are preserved. Validation rejects invalid means, nonrepresentable reciprocal
rates and generated non-finite times. No comparison engine, AI, deployment or
extra dependency was added.

Validation from the project root:
- Baseline: python -m unittest discover -s tests -v: 8 tests passed.
- After implementation: same command: 17 tests passed, including nine new tests.
  Coverage includes original draw sequence, custom reproducibility, separate
  arrival/service scaling, empty workloads, invalid types/values, generated
  overflow, CLI propagation, help units and expected CLI failures.
- python -m opslab --cases 100 --agents 3 --seed 42: exit 0;
  mean wait 0.9513027012401756, total service 431.609365564085 minutes,
  unchanged from the baseline.
- python -m opslab --cases 100 --agents 3 --seed 42 --mean-interarrival 4 --mean-service 7:
  exit 0; mean wait 0.3592054456646032, maximum wait 5.111221451305639,
  total service 604.2531117897194, final completion 467.5601588474354 minutes.
  This changes workload assumptions, not staffing; it is not a staffing benefit estimate.
- python -m opslab --mean-service 0: expected exit 2, useful error, no traceback.
- git diff --check: passed before publication.

Concepts: keyword-only parameters, means versus rates, validation at boundaries,
regression tests, controlled experiments and CLI integration tests.
The tiny-positive-mean case needs reciprocal validation: finite input alone does
not guarantee a finite exponential rate. Overflow of generated arrival sums also
needs explicit rejection.

Limitations: local validation only, not a CI result; no hosted demo. Existing
simulation aggregates are not yet guarded against overflow for extreme finite
inputs. Synthetic assumptions remain uncalibrated. No new blocker was found.
Next bounded task: validate numerical boundaries and queue invariants further,
fix any demonstrated failures, then document a same-workload staffing experiment.
CSV export and scenario automation remain later milestones.

## 2026-10-17: Initial increment
Implemented a human-only queue simulator, seeded synthetic workload generator,
CLI, input validation, and hand-calculated and invariant tests.
Concepts: dataclasses, lists, functions, loops, stable sorting, heaps, exceptions,
pseudorandom seeds, means, and unit tests.
No actual customer data, secrets, credentials, or AI API calls are present.
Publication and CI status must be recorded from tool results, not assumed.
Next: expose arrival/service parameters, validate them, compare two scenarios.
Learner understanding: not yet assessed.

Validation: 8 unittest tests passed locally; CLI ran for 100 cases, 3 agents, seed 42. Initial test invocation used the parent directory and failed discovery; rerunning from the project root passed. Revalidated all 8 tests before initial publication. Repository initialized with documentation commit a8666707676dafbf335aa5ddf48262b139265d1a. This increment publishes the simulator and learning notes; no hosted demo or CI run is claimed.
