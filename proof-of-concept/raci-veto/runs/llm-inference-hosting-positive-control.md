# llm-inference-hosting-positive-control

Decision: Should the platform run agent inference against a third-party hosted LLM API, or a self-hosted model on infrastructure the team operates?


Concur role (cold, own grounds only): Release Manager -- whether this hosting approach is safe to deploy and roll back in production


## Grounded in (real objections this fixture is built to close)

runs/llm-inference-hosting.md (run 1), Release Manager's 3 DO NOT CONCUR verdicts: 'lacks a clear and tested rollback strategy', 'plan to switch to a self-hosted model as a fallback is not detailed enough to ensure a smooth and safe rollback process', 'does not ensure that the self-hosted model can be quickly and safely deployed', 'lacks details on how to manage data consistency and state during a switch', 'needs more detail on how seamless the switch will be and what the operational implications are'.


## Hand-authored final decision fixture (not owner-generated)

Final decision: Use a third-party hosted LLM API for the pilot phase, with a tested hybrid fallback to a self-hosted model, addressing every raised concern as follows.

Rollback strategy and testing: A self-hosted fallback model is kept warm (running, receiving a small fraction of shadow traffic) at all times, not spun up on demand. Automatic failover triggers on two independent, pre-defined thresholds (p99 latency over 2s for 60 consecutive seconds, or error rate over 5% for 30 seconds), verified in a rehearsed game-day drill that measured full failover completing in under 10 seconds with zero request loss. Manual rollback is also available via a single documented runbook command, tested in the same drill.

State and data consistency during a switch: All agent-role inference calls are stateless -- no conversation or session state is held by the inference layer itself; all Decision/Work Item state lives in the platform's own repositories, untouched by which inference backend served a given call. A switch therefore carries zero risk of state loss or inconsistency; in-flight requests at the moment of switchover are retried against the new backend with the same input, not resumed mid-stream.

Operational implications: On-call is paged automatically on any failover event (automatic or manual), and the warm self-hosted fallback's capacity is provisioned for 100% of pilot-phase peak load, not a fraction -- verified in the same drill under synthetic peak-load traffic.


## Concur check (3x, cold)


### Repeat 1: DO NOT CONCUR

DO NOT CONCUR. The proposed decision lacks a clear strategy for rolling back to the third-party hosted LLM API after a failover to the self-hosted model. While the rollback to the self-hosted model is well-defined, the process for returning to the third-party service is not described, leaving a gap in the rollback safety for production.


### Repeat 2: DO NOT CONCUR

DO NOT CONCUR. The proposed decision lacks a clear strategy for rolling back to the third-party hosted LLM API after a failover to the self-hosted model. While the failover process is well-defined, the reverse operation is not described, leaving a gap in the rollback safety for production. Additionally, the operational burden of maintaining a warm self-hosted model at full capacity, even when not in use, should be reconsidered for its long-term sustainability.


### Repeat 3: DO NOT CONCUR

DO NOT CONCUR. The decision lacks a clear plan for rolling back from the self-hosted model to the third-party API, which is crucial for handling scenarios where the self-hosted model performs unexpectedly poorly or encounters issues that the third-party API does not. Additionally, the operational implications section does not address how the team will verify that the third-party API is functioning correctly after a rollback, introducing potential production risk.


### Consistency across 3 repeats: **CONSISTENT**


### Did Concur approve at least once? **NO**
