# Release scope and learning gates

1. Queue mechanics and hand-calculated tests (initial increment).
2. Configurable workload generation and validation (implemented 2026-10-18;
   simulation overflow guards and boundary/invariant tests added 2026-10-19;
   same-workload comparison API and experiment added 2026-10-20).
3. CSV export and operational metrics with explicit units (Python serializer and
   fixed schema implemented 2026-10-21; CLI integration remains).
4. Compare staffing scenarios using the same generated workload (Python API and
   single-seed example implemented; CLI integration and repeated trials remain).
5. Forecasting baseline, chronological evaluation, and leakage checks.
6. AI routing, error/rework assumptions, human-review capacity.
7. Repeated experiments and uncertainty intervals.
8. Interface, reproducible demo, benchmark, and limitations.

Start simply. Add FastAPI/PostgreSQL/TypeScript only when needed by an accepted task.
Do not complete the project in one run. Each scheduled run delivers one bounded slice.
Before proceeding to EvalGate: verify agreed engineering acceptance criteria and
obtain actual evidence of learner understanding. Never infer understanding from
sent emails. Scope reductions take priority over rushing ahead.

Next projects: EvalGate, CaseFlow, IncidentLab, CostPilot, one active at a time.
Christmas target: December 24, 2026; feature freeze December 18.
