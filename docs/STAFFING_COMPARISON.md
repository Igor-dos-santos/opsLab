# Compare staffing without changing the workload

Implemented with AI assistance. All cases are synthetic, and time units are minutes.
This is a controlled example, not a staffing recommendation or cost estimate.

Run this Python code from the project root:
```python
from opslab.scenarios import compare_staffing
from opslab.simulation import generate_cases

cases = generate_cases(100, 42)  # Generate once, outside the staffing loop.
for row in compare_staffing(cases, [2, 3, 4]):
    r = row.result
    print(row.agents, r.mean_wait, r.maximum_wait,
          r.total_service_minutes, r.final_completion)
```

Observed locally on 2026-10-20:

| Agents | Mean wait | Maximum wait | Total service | Final completion |
| --- | --- | --- | --- | --- |
| 2 | 11.12260704571623 | 30.04467183254087 | 431.609365564085 | 248.91481607734613 |
| 3 | 0.9513027012401756 | 6.975970587585238 | 431.609365564085 | 236.49216502423639 |
| 4 | 0.20221891703524947 | 3.1841187056138835 | 431.609365564085 | 236.49216502423639 |

The comparison changes only agent count. Arrival times, service durations, case
count and tie order are held fixed. Required service stays identical because no
case is dropped and adding agents does not shorten case durations in this model.
Completion is the latest finish, not the sum of all durations. Three and four
agents happen to have the same completion here despite different waiting times.

## API contract and failure policy

`compare_staffing(cases, agent_counts)` returns a list of frozen `StaffingResult`
records, each with `agents` and the existing simulation `result` record. Count
order is preserved. Counts must be a nonempty list of unique positive integers;
booleans, tuples, duplicates and non-integers are rejected with ValueError before
any simulation runs. It passes the same case list to every simulation and does
not modify either input. Case validation and numerical errors come from simulate.
Any failed scenario raises: no partial result list is returned. Earlier scenarios
may have been computed locally before a later simulation fails. This is not a
transactional persistence mechanism; the function has no external writes.

## Interpretation and next steps

One seed gives a repeatable example, not an uncertainty estimate. Future repeated
trials should generate one workload per seed, compare staffing within that seed,
and analyze paired differences across seeds. Do not generate a different workload
for each staffing level. Do not silently discard failed trials.

No shifts, breaks, abandonment, agent skills, cost, quality, AI or rework are
modeled. There is no optimal-staffing decision rule or financial savings claim.
No CLI comparison mode or hosted demo exists yet. The API repeats sorting and
validation for each scenario to reuse the tested simulator; optimizing that is
not necessary for this small example. Count/agent resource limits remain absent.
