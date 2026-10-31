# OpsLab v1: focused synthetic staffing simulator

This scope supersedes the earlier broader roadmap as of 2026-10-30.
Deliver coherent usable features with implementation, integration, tests and docs
in one focused run. Do not split layers across days or add statistical scope.

## Outcome milestones

1. **Usable local interface:** implemented 2026-10-31. Inputs, same-workload
   comparisons, repeated-trial descriptive table/chart, raw and summary CSV,
   explicit minute units, validation and local setup. Existing CLI/API preserved.
2. **Integrated demonstration and verification:** next. Complete a timed five-minute
   worked demonstration and plain-English case trace; verify live browser form,
   errors and downloads, narrow-screen usability, and reproducible clean setup.
   Current checks cover HTTP behavior and visual rendering separately, not a full
   interactive browser session against the live Python server.
3. **Release documentation and checks:** verify acceptance below, finalize release
   notes and publish an actual versioned release only when checks pass.

These are outcome milestones, not promised dates or run counts. Work incrementally
through December 24, 2026; do not rush gates to meet a calendar target.

## Engineering acceptance

- Existing queue simulation, fair comparisons, repeated summaries and CSV work.
- A local user can enter assumptions, inspect table/chart and export matching data.
- Clean Python 3.10+ setup is documented; meaningful tests pass.
- A five-minute worked demo explains data flow and one case's wait calculation.
- Limits, synthetic assumptions and AI-assisted development are explicit.
- Actual release checks and results are recorded. No hosted demo is required or
  claimed without deployment evidence.

## Learning gate

After engineering completion, hold for actual evidence: explain data flow, trace
code, make a change and diagnose a bug. Never infer understanding from delivery or
add features simply to fill time while waiting.

## Deferred backlog

Forecasting, AI routing/rework, quality/cost models and inferential uncertainty
intervals. Existing paired differences and method design are preserved but do not
expand v1. CaseFlow, IncidentLab and CostPilot are backlog, not an automatic sequence.

## Proposed next project

EvalGate AI-security lab: synthetic prompt-injection, customer-data access and tool
permission tests, deterministic controls, baseline comparisons and honest failures.
Do not create a repository until scope and designated repository are settled, and
both OpsLab engineering and learner gates are met.
