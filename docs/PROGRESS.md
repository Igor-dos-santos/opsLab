# Progress

## 2026-10-28: Atomic descriptive-summary CSV command

Implemented with AI assistance, preserving existing attribution.
Base: [1cb1782cd5d72707984daf5404019cbd882fd3c0](https://github.com/Igor-dos-santos/opsLab/commit/1cb1782cd5d72707984daf5404019cbd882fd3c0).
This increment's commit is available in
[file history](https://github.com/Igor-dos-santos/opsLab/commits/main/docs/PROGRESS.md).

Added the explicit `--summary-seeds N [N ...]` mode. With the required
`--trial-agents N [N ...]`, the command reuses `run_paired_trials`, validates and
aggregates the complete seed-by-agent matrix with `summarize_mean_wait`, serializes
the summaries with `summary_results_to_csv`, and writes only the completed
five-column CSV. The mode is argparse-mutually-exclusive with single-scenario JSON,
one-workload comparison CSV and raw paired-trial CSV. It rejects the single-workload
`--seed` option instead of silently ignoring it.

Local evidence from the project root:
- `python -m unittest discover -s tests -v`: baseline 73 tests passed.
- Before implementation, `python -m unittest discover -s tests -p
  test_summary_cli.py -v` ran seven new tests and failed because
  `--summary-seeds` and the CLI summary import did not exist. The focused run
  reported the expected unrecognized-argument failures plus one missing-symbol mock
  error.
- After implementation, all seven focused tests passed and the complete suite passed
  80 tests. Coverage includes exact CSV and staffing order with custom workload
  means, mode exclusivity, paired-option requirements, rejection of ambiguous
  `--seed`, invalid lists, a late aggregation failure with empty standard output,
  and help text.
- `python -m opslab --cases 100 --summary-seeds 40 41 42 --trial-agents
  2 3 4` exited 0 with one header and three deterministic rows. Average mean waits
  remained 34.170984373131745, 7.775144386029897 and 1.1376757981918428 minutes for
  2, 3 and 4 agents.
- `python -m compileall -q opslab tests` passed.

Concepts: explicit CLI modes, orchestration through existing domain APIs, mutual
exclusion, paired arguments, ambiguity rejection, deterministic serialization,
failure atomicity and regression testing. All simulations, aggregation and
serialization complete before standard output is written. Results and the complete
CSV remain in memory, and the command has no explicit experiment-size cap. Observed
ranges are descriptive only, not confidence intervals, prediction intervals,
hypothesis tests, staffing recommendations or evidence of external validity. No CI,
release or hosted demo is claimed, and no learner understanding is inferred.

Next bounded task: add an explicit experiment-size budget for paired CLI modes,
validated before workload generation, with boundary and no-partial-output tests.
Uncertainty methods, forecasting, AI/rework, costs and an interface remain later
milestones.

## 2026-10-27: Deterministic descriptive-summary CSV

Implemented with AI assistance, preserving existing attribution.
Base: [b0ae6f0be54cad0e3a88561388ee35541aed471e](https://github.com/Igor-dos-santos/opsLab/commit/b0ae6f0be54cad0e3a88561388ee35541aed471e).
This increment's commit is available in
[file history](https://github.com/Igor-dos-santos/opsLab/commits/main/docs/PROGRESS.md).

Added `SUMMARY_CSV_HEADER` and `summary_results_to_csv`. The Python serializer
emits a fixed five-column schema for staffing count, trial count, average mean wait,
observed minimum mean wait and observed maximum mean wait. Minute-bearing names make
units explicit. It preserves first-seen staffing order and Python numeric
representations, includes the header for empty input, uses LF line endings, and
leaves summary and raw trial records unchanged. Summary calculation stays separate
from presentation so callers can retain auditable seed-level observations.

Local evidence from the project root:
- `python -m unittest discover -s tests -v`: baseline 68 tests passed.
- Before implementation, `python -m unittest discover -s tests -p
  test_summary_export.py -v` failed with `ImportError` because the summary CSV
  header and serializer did not exist.
- After implementation, all five focused tests passed and the complete suite passed
  73 tests. Coverage includes the exact schema and values, preserved staffing order
  and numeric representations, empty input, LF line endings and unchanged records.
- A three-seed 100-case example emitted deterministic rows for 2, 3 and 4 agents,
  preserving average mean waits of 34.170984373131745, 7.775144386029897 and
  1.1376757981918428 minutes and their documented observed ranges.
- `python -m compileall -q opslab tests` passed.

Concepts: stable schemas, explicit units, deterministic serialization, separation of
calculation from presentation, provenance retention, order preservation and
regression testing. The serializer accepts already validated summary records; it does
not recalculate or independently validate them. It holds the complete CSV in memory
and performs no external write. Observed ranges remain descriptive only, not
confidence or prediction intervals, hypothesis tests, staffing recommendations or
evidence of external validity. No CLI mode, CI, release or hosted demo is claimed,
and no learner understanding is inferred.

Next bounded task: add an explicit summary CSV CLI mode that reuses the validated
aggregation and serializer, preserves atomic standard output, and remains mutually
exclusive with existing modes. Uncertainty methods, forecasting, AI/rework, costs
and an interface remain later milestones.

## 2026-10-26: Validated descriptive wait summaries

Implemented with AI assistance, preserving existing attribution.
Base: [302c8e56078cd025b9206261d0ffb752de5bad52](https://github.com/Igor-dos-santos/opsLab/commit/302c8e56078cd025b9206261d0ffb752de5bad52).
This increment's commit is available in
[file history](https://github.com/Igor-dos-santos/opsLab/commits/main/docs/PROGRESS.md).

Added `TrialWaitSummary` and `summarize_mean_wait`. The Python API groups complete
paired-trial rows by staffing count and reports the trial count, arithmetic average,
observed minimum and observed maximum of the per-trial mean waits. It preserves the
first-seen staffing order and leaves raw rows unchanged. It requires a nonempty,
duplicate-free, complete seed-by-agent matrix with one shared case count, finite
nonnegative mean waits and valid identifiers. This prevents silent aggregation of
missing, duplicated or incomparable observations.

Local evidence from the project root:
- `python -m unittest discover -s tests -v`: baseline 60 tests passed.
- Before implementation, `python -m unittest discover -s tests -p test_summaries.py -v`
  failed with `ImportError` because the summary type and function did not exist.
- After implementation, all eight focused tests passed and the complete suite passed
  68 tests. Coverage includes hand-calculated summaries, first-seen agent order,
  unchanged generated rows, empty input, duplicate pairs, incomplete matrices,
  inconsistent case counts, malformed values and large finite means.
- The three-seed 100-case example produced descriptive average mean waits of
  34.170984373131745, 7.775144386029897 and 1.1376757981918428 minutes for 2, 3 and
  4 agents. Observed ranges were 11.12260704571623 to 63.88369229370024,
  0.9513027012401756 to 19.756955845567838, and 0.20221891703524947 to
  2.7904431154731766 minutes respectively.
- `python -m compileall -q opslab tests` passed.

Concepts: descriptive versus inferential statistics, complete factorial data,
duplicate detection, equal-weight per-trial aggregation, stable group order, numeric
overflow avoidance and validation before calculation. The observed ranges cover only
the supplied caller-selected synthetic seeds. They are not confidence intervals,
prediction intervals, significance tests, staffing recommendations or evidence of
external validity. No CLI or CSV summary output was added. No CI, release or hosted
demo is claimed, and no learner understanding is inferred.

Next bounded task: add deterministic, unit-bearing CSV serialization for descriptive
wait summaries while keeping raw rows available and inferential claims out of scope.
Forecasting, AI/rework, costs and an interface remain later milestones.

## 2026-10-25: Atomic repeated-trial CSV command

Implemented with AI assistance, preserving existing attribution.
Base: [1fbe3cd459c36767d6c9c1b154b1548ebb0ceb3e](https://github.com/Igor-dos-santos/opsLab/commit/1fbe3cd459c36767d6c9c1b154b1548ebb0ceb3e).
This increment's commit is available in
[file history](https://github.com/Igor-dos-santos/opsLab/commits/main/docs/PROGRESS.md).

Added `--trial-seeds N [N ...]` and the paired `--trial-agents N [N ...]` option.
The mode calls the existing paired-trial engine and seven-column serializer, preserves
seed-then-agent order, applies the existing workload means and case count, and writes
only CSV to standard output. Both options are required together. Trial mode is
mutually exclusive with the JSON and one-workload comparison modes, and explicitly
rejects the single-workload `--seed` option instead of ignoring it. All trials and
serialization finish before output is written, preserving failure atomicity.

Local evidence from the project root:
- `python -m unittest discover -s tests -v`: baseline 53 tests passed.
- Before implementation, `python -m unittest discover -s tests -p test_trial_cli.py -v`
  ran seven new tests and failed because the trial flags and CLI import did not exist.
- After implementation, all seven focused tests passed and the complete suite passed
  60 tests. Coverage includes exact CSV and requested order with custom workload
  means, mode exclusivity, paired-option requirements, rejection of ambiguous
  `--seed`, list validation, late-failure atomicity and help text.
- `python -m opslab --cases 5 --trial-seeds 40 41 --trial-agents 2 3` exited 0
  with one header and four deterministic rows. Within each seed, total service was
  conserved across both staffing counts: 22.67806530162165 minutes for seed 40 and
  26.140916818204612 minutes for seed 41.
- `python -m opslab --cases 100 --agents 3 --seed 42` retained the existing JSON
  mean wait 0.9513027012401756 and completion 236.49216502423639 minutes.
- `python -m compileall -q opslab tests` passed.

Concepts: command-line mode design, paired arguments, ambiguity rejection, reuse of
domain APIs, stdout/stderr contracts, failure atomicity, deterministic serialization
and regression testing. Trial results and the complete CSV remain in memory with no
explicit resource cap. The command provides raw synthetic observations, not an
uncertainty estimate, optimized staffing decision or production benchmark. No CI,
release or hosted demo is claimed. No learner understanding is inferred.

Next bounded task: design and add descriptive per-agent summaries across paired seeds
with explicit interpretation limits, without presenting them as confidence intervals
or staffing recommendations. Forecasting, AI/rework, costs and an interface remain.

## 2026-10-24: Raw paired-trial CSV serialization

Implemented with AI assistance, preserving existing attribution.
Base: [61437f8ee5d76a952539a36896b70fe3ce3724e0](https://github.com/Igor-dos-santos/opsLab/commit/61437f8ee5d76a952539a36896b70fe3ce3724e0).
This increment's commit is available in
[file history](https://github.com/Igor-dos-santos/opsLab/commits/main/docs/PROGRESS.md).

Added `trial_results_to_csv` and a fixed seven-column schema containing `seed`,
`agents`, `cases`, and four explicitly minute-based metrics. Serialization preserves
the raw seed-then-agent row order and Python numeric representations, always includes
the header, uses LF line endings, does not modify inputs, and performs no external
write or aggregation. No repeated-trial CLI mode or statistical summary was added.

Local evidence from the project root:
- `python -m unittest discover -s tests -v`: baseline 48 tests passed.
- Before implementation, focused discovery of `test_trial_export.py` failed with
  `ImportError` because the raw-trial header and serializer did not exist.
- After implementation, all five focused tests passed and the complete suite passed
  53 tests. Coverage includes exact seed/unit schema and values, seed-then-agent
  order, full result values, empty input, LF endings and unchanged trial rows.
- A two-seed, two-staffing, five-case example produced four deterministic CSV rows.
  Seed 40 retained total service 22.67806530162165 minutes across 2/3 agents; seed
  41 retained 26.140916818204612 minutes.
- `python -m compileall -q opslab tests` and `git diff --check`: passed before
  publication.

Concepts: stable schemas, explicit units, provenance-preserving serialization,
deterministic output, separation of computation from presentation, raw observations
versus summaries, and regression testing. The API and serializer hold results and the
complete CSV in memory. Numeric-only fields avoid current spreadsheet formula input,
but future text fields require formula-injection analysis. Local tests are not CI
evidence. No release or hosted demo is claimed. Only synthetic data and sanitized
documentation were added. No learner understanding is inferred.

Next bounded task: add an explicit repeated-trial CLI mode that emits this schema
without mixing outputs or returning partial CSV. Statistical summaries, forecasting,
AI/rework, costs, uncertainty and an interface remain later milestones.

## 2026-10-23: Raw repeated paired trials

Implemented with AI assistance, preserving existing attribution.
Base: [c1144cc7f15a780179f889b493f73bf72942fd3b](https://github.com/Igor-dos-santos/opsLab/commit/c1144cc7f15a780179f889b493f73bf72942fd3b).
This increment's commit is available in
[file history](https://github.com/Igor-dos-santos/opsLab/commits/main/docs/PROGRESS.md).

Added `run_paired_trials` and frozen `TrialResult` records. The Python API accepts
explicit unique seeds and staffing counts, generates one workload per seed, reuses
that workload across every staffing count, and returns raw rows ordered by seed then
staffing count. Every row records both identifiers. No aggregation, CSV/CLI mode,
uncertainty estimate, optimization, cost model or AI behavior was added.

Local evidence from the project root:
- `python -m unittest discover -s tests -v`: baseline 42 tests passed.
- Before implementation, focused discovery of `test_trials.py` failed with
  `ImportError` because `run_paired_trials` did not exist.
- After implementation, all six focused tests passed and the complete suite passed
  48 tests. Coverage includes seed and staffing order, equivalence to direct
  simulation, one workload generation per seed, unchanged inputs, validation before
  generation, and propagation of a late-trial failure without a partial return.
- A three-seed, three-staffing example produced nine raw rows. Within each seed,
  total service was conserved across 2/3/4 agents: 461.1749923638263 minutes for
  seed 40, 574.9463819546643 for seed 41, and 431.609365564085 for seed 42.
- `python -m compileall -q opslab tests` and `git diff --check`: passed before
  publication.

Concepts: paired experimental design, raw observations versus summaries, explicit
provenance, deterministic seeds, nested ordering, validation-before-work, immutable
records and failure atomicity at the return boundary. Results are stored in memory
and the API has no CSV or CLI mode. Seed choice is not real-world sampling, and raw
repetition alone supplies no confidence interval or staffing recommendation. Local
tests are not CI evidence. No release or hosted demo is claimed. Only synthetic data
and sanitized documentation were added. No learner understanding is inferred.

Next bounded task: add deterministic CSV serialization for raw trial rows with seed
and agent columns, without aggregating or claiming uncertainty. Statistical summaries,
forecasting, AI/rework, costs and an interface remain later milestones.

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
