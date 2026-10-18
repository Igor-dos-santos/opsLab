# Progress

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
