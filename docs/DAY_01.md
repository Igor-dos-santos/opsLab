# Day 1: Queues before machine learning

## Purpose
Learn the behavior we will later forecast and optimize. A simple baseline makes
advanced features measurable. The first version models only human work.

## Trace this example
One agent; cases (arrival, duration): (0,5), (1,3), (10,2).
Start times: 0,5,10. Finishes: 5,8,12. Waits: 0,4,0.
Mean wait is 4/3 minutes. The idle interval 8 to 10 creates no negative waiting.

## Concepts and intentions
- A frozen dataclass groups related fields and prevents accidental reassignment.
- A min-heap returns the earliest available agent without sorting the whole list each time.
- max(availability, arrival) respects both constraints on starting a case.
- A local seeded Random instance makes experiments repeatable without changing global state.
- Tests compare against manually computed answers, not just copied implementation logic.
- Workload conservation means total service minutes equals the sum of input durations.

## Challenge
Simultaneous arrivals need a documented tie rule; stable sorting preserves input order.
Non-finite inputs would contaminate metrics, so validation rejects them.
Reproducibility does not establish realism or quantify uncertainty.

## Quiz: 10 questions
1. What does Case represent, and why keep arrival separate from duration?
2. Trace the three example cases with two agents. What is the mean wait?
3. Why use max(available, arrival)? Give an example where each argument wins.
4. What error would occur conceptually if we used min instead?
5. Why must cases be processed in arrival order?
6. What does a fixed seed guarantee, and what does it not guarantee?
7. Why reject infinity and NaN even though they are floating-point values?
8. Which test checks a property that should hold across different agent counts?
9. What business assumptions make this simulation unrealistic today?
10. Add a test for two cases separated by a long idle gap, and explain the expected wait.

## Answer guide (attempt first)
1. One work item; arrival is when it enters and duration is service required.
2. Both early cases start immediately; all waits are zero.
3. A busy agent forces waiting; an idle agent still waits for a future arrival.
4. Work could start before arrival or before the agent is free.
5. Otherwise later cases could improperly occupy agents ahead of earlier cases.
6. Repeatable pseudorandom draws in the same implementation; not realistic data or certainty.
7. Such values make ordering and aggregate metrics meaningless.
8. Workload conservation; capacity changes do not change required service in this model.
9. No breaks, abandonment, language routing, quality, correlated arrivals, or shift limit.
10. Example Case(0,2), Case(20,3), one agent: both waits zero, final completion 23.

## Next step
Parameterize workload rates and compare staffing using identical cases, avoiding
confounding a staffing change with a different random workload.
