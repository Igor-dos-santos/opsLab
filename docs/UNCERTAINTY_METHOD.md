# Paired uncertainty method design

## Scope

OpsLab compares staffing counts against the same synthetic workload within each
seed. Any future uncertainty calculation must preserve that pairing. This document
defines the target quantity and selects a method before an interval is implemented.
It does not claim uncertainty about a real support operation.

## Raw paired quantity

For seed `s`, baseline staffing `b`, and comparison staffing `c`, define:

```text
d_s = mean_wait(s, c) - mean_wait(s, b)
```

Negative values mean the comparison staffing count had a lower mean wait for that
synthetic seed. Positive values mean it had a higher mean wait. The new
`paired_mean_wait_differences` API returns one auditable record per seed and does not
aggregate or discard the original trial rows.

```python
from opslab.scenarios import (
    paired_mean_wait_differences,
    run_paired_trials,
)

rows = run_paired_trials([40, 41, 42], [2, 4], case_count=100)
differences = paired_mean_wait_differences(
    rows, baseline_agents=2, comparison_agents=4,
)
```

The verified comparison-minus-baseline differences for this example are
`-27.086288417911653`, `-61.09324917822707`, and `-10.92038812868098` minutes.
These three selected synthetic seeds are an example, not evidence for a staffing
decision.

## Selected future interval

The planned first interval is a two-sided Student t interval for the mean of the
per-seed paired differences:

```text
mean(d) +/- t_(0.975, n-1) * sample_standard_deviation(d) / sqrt(n)
```

The initial implementation should support only a clearly named 95 percent interval.
It should require at least two complete paired differences, use the sample standard
deviation with `n - 1` degrees of freedom, retain the sign convention above, and
return the count, mean difference, standard error, and lower and upper bounds.
It should not produce a p-value, one-sided bound, optimal staffing label, or automatic
recommendation.

## Why paired Student t

- The estimand is the mean within-seed change, not the difference between two
  unrelated groups of trials.
- Pairing removes between-workload variation from each within-seed subtraction.
- A t interval reflects the additional uncertainty from estimating variability with
  a finite number of simulated draws better than a fixed normal critical value.
- The formula is inspectable and teachable. The raw differences remain available for
  diagnostics and alternative analyses.

## Assumptions and interpretation

- Distinct seeds under one unchanged generator configuration are treated as separate
  draws from the simulator distribution.
- The paired differences should be reasonably independent across seeds.
- Strong skew or extreme outliers can make a small-sample t interval misleading.
- A zero-width interval caused by identical simulated differences is not proof of
  real-world certainty.
- The interval describes Monte Carlo variation under the current synthetic model and
  chosen parameters only. It does not cover model misspecification, real operational
  variation, external validity, quality, cost, abandonment, skills, breaks, or
  AI/rework behavior.
- The seed list and all workload parameters must be reported with the result.

## Alternatives not selected first

- Observed minimum and maximum are descriptive ranges, not uncertainty intervals.
- An unpaired interval discards the controlled same-workload design.
- A normal z interval understates small-sample critical-value uncertainty.
- A percentile bootstrap could be added later, but it introduces a resampling seed,
  replicate-count policy, percentile convention, and additional Monte Carlo error.

## Implementation gate

No interval is implemented in this increment. Before publication, a future interval
must have hand-calculated tests, invalid and incomplete-matrix tests, order and sign
tests, zero-variance behavior, and clear reporting limits. Results must remain framed
as simulator-only uncertainty, never as a production staffing recommendation.
