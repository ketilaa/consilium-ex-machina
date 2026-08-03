# llm-inference-hosting -- three-way Concur comparison

Decision: Should the platform run agent inference against a third-party hosted LLM API, or a self-hosted model on infrastructure the team operates?


Concur role (cold, own grounds only): Release Manager -- whether this hosting approach is safe to deploy and roll back in production


## Positive fixture (thorough)

Final decision: Use a third-party hosted LLM API for the pilot phase, with a tested hybrid fallback to a self-hosted model, addressing every raised concern as follows.

Rollback strategy and testing: A self-hosted fallback model is kept warm (running, receiving a small fraction of shadow traffic) at all times, not spun up on demand. Automatic failover triggers on two independent, pre-defined thresholds (p99 latency over 2s for 60 consecutive seconds, or error rate over 5% for 30 seconds), verified in a rehearsed game-day drill that measured full failover completing in under 10 seconds with zero request loss. Manual rollback is also available via a single documented runbook command, tested in the same drill.

State and data consistency during a switch: All agent-role inference calls are stateless -- no conversation or session state is held by the inference layer itself; all Decision/Work Item state lives in the platform's own repositories, untouched by which inference backend served a given call. A switch therefore carries zero risk of state loss or inconsistency; in-flight requests at the moment of switchover are retried against the new backend with the same input, not resumed mid-stream.

Operational implications: On-call is paged automatically on any failover event (automatic or manual), and the warm self-hosted fallback's capacity is provisioned for 100% of pilot-phase peak load, not a fraction -- verified in the same drill under synthetic peak-load traffic.


## Negative fixture (thin, real)

Decision: For the pilot phase, use a third-party hosted LLM API with specific mitigations and fallback strategies.

Latency and availability risks: We will specify required Service Level Agreements (SLAs) with the third-party provider to ensure they can meet our latency and availability requirements, and conduct thorough performance testing to validate these SLAs in a pilot scenario.

Fallback plan: We will design a hybrid approach that allows for seamless switching between the third-party API and a self-hosted model. This will involve developing a fallback mechanism that can be activated in case of outages or significant latency issues with the third-party service. We will also ensure that the self-hosted model is ready to be deployed quickly if needed.

Costs and scalability: We will conduct a detailed cost analysis based on expected usage patterns and assess the scalability of the third-party solution under increased load, with cost management strategies such as rate limiting and optimizing API calls.

Using a third-party hosted LLM API for the pilot phase remains the recommended approach, with these mitigations and fallback strategies to address the raised concerns.


(Negative fixture source: runs/llm-inference-hosting.md, run 1 (git show 8cef25d), Mechanism B (raci) final revision)


## Variant A: Original prompt


### Against positive fixture


**Repeat 1: DO NOT CONCUR**

DO NOT CONCUR. The proposed decision lacks a clear strategy for rolling back to the third-party hosted LLM API in case issues are identified with the self-hosted model. While the failover to the self-hosted model is well-defined, the reverse path is not, which could lead to prolonged downtime or degraded service if the self-hosted model proves unreliable. Additionally, the operational burden of maintaining a warm self-hosted model at full capacity may introduce unnecessary costs and complexity.


**Repeat 2: DO NOT CONCUR**

DO NOT CONCUR. While the rollback strategy and state consistency are well-addressed, the operational implications are not sufficiently mitigated. Specifically, the on-call team's burden during a failover event is not clearly defined, and the capacity provisioning for the self-hosted fallback, while verified, does not account for potential spikes beyond the pilot-phase peak load.


**Repeat 3: DO NOT CONCUR**

DO NOT CONCUR. The proposal does not address the risk of the third-party API becoming unavailable or degraded outside of the defined thresholds, which could lead to a poor user experience or even loss of service. Additionally, the proposal does not mention any testing or validation of the self-hosted model's performance and accuracy compared to the third-party API, which could lead to unexpected issues during a failover.


**Approved at least once? NO** (consistency: CONSISTENT)


### Against negative fixture


**Repeat 1: DO NOT CONCUR**

DO NOT CONCUR. The proposed decision lacks a clear rollback plan for the pilot phase, which is crucial for managing production risk. While a fallback mechanism is mentioned, it does not specify how the system will revert to a previous stable state if issues arise with the third-party API during the pilot, which is essential for ensuring deployability and operational burden are managed effectively.


**Repeat 2: DO NOT CONCUR**

DO NOT CONCUR. The proposed decision does not adequately address rollback safety, as the fallback mechanism from a third-party API to a self-hosted model introduces significant complexity and potential for failure during a rollback scenario. Specifically, the plan does not detail how the self-hosted model will be kept in sync with the third-party API, or how data consistency will be maintained during a switch.


**Repeat 3: DO NOT CONCUR**

DO NOT CONCUR. This approach introduces significant rollback risk, as the fallback mechanism relies on having a self-hosted model ready for deployment, which may not be immediately available or fully tested in a production scenario. Additionally, the dependency on a third-party API for critical functionality increases production risk, as issues with the API could impact the entire system's availability and performance.


**Approved at least once? NO** (consistency: CONSISTENT)


## Variant B: Sufficiency criterion


### Against positive fixture


**Repeat 1: CONCUR**

CONCUR. The proposed decision includes a tested rollback strategy with specific, measurable thresholds and a proven failover time, along with a stateless architecture that ensures data consistency during a switch, addressing the named grounds for deployability and rollback safety.


**Repeat 2: CONCUR**

CONCUR. The proposed decision includes concrete mechanisms for rollback safety, such as a warm self-hosted fallback model with automatic failover triggers and a tested manual rollback procedure. The stateless nature of inference calls ensures data consistency during a switch, addressing key concerns for deployability and operational burden in production.


**Repeat 3: CONCUR**

**CONCUR**. The decision includes a tested fallback mechanism with clear, predefined triggers and a proven rollback procedure, addressing deployability and rollback safety. The stateless nature of the inference calls ensures data consistency during a switch, mitigating production risk.


**Approved at least once? YES** (consistency: CONSISTENT)


### Against negative fixture


**Repeat 1: CONCUR**

CONCUR. The proposed decision includes specific mechanisms for rollback safety, such as a fallback mechanism that allows for seamless switching to a self-hosted model in case of outages or latency issues, and a self-hosted model ready for quick deployment. Additionally, the requirement for specified SLAs with the third-party provider addresses deployability and operational burden concerns.


**Repeat 2: CONCUR**

CONCUR. The decision includes concrete mechanisms for rollback safety and operational burden mitigation, such as specified SLAs, performance testing, and a designed fallback mechanism to a self-hosted model. These controls address the deployability and rollback safety in production.


**Repeat 3: CONCUR**

CONCUR. The decision includes concrete mechanisms for rollback safety, such as a hybrid approach with a fallback mechanism to switch to a self-hosted model in case of issues with the third-party API, and specific SLAs to ensure deployability and operational burden are managed.


**Approved at least once? YES** (consistency: CONSISTENT)


## Variant C: Recheck (round 1 on negative fixture, round 2 checks only that concern against positive fixture)


### Repeat 1


Round 1 (DO NOT CONCUR):

DO NOT CONCUR.

The proposed decision does not specify how the fallback mechanism will be tested and validated in production, which is crucial for ensuring rollback safety and minimizing production risk during the pilot phase. Without a clear plan for testing the fallback mechanism under real-world conditions, there is a significant risk that the fallback may not work as expected when needed.


Round 2 recheck (CONCUR):

CONCUR. The revision explicitly addresses the original concern by detailing a tested fallback mechanism that includes automatic failover triggers, a rehearsed game-day drill, and a manual rollback procedure, all of which ensure that the fallback process is validated and reliable in production.


### Repeat 2


Round 1 (DO NOT CONCUR):

DO NOT CONCUR

The proposed decision does not specify how the fallback mechanism will be validated and tested in production to ensure a safe rollback from the third-party API to the self-hosted model, which is crucial for minimizing production risk during the pilot phase.


Round 2 recheck (CONCUR):

CONCUR

The revised decision addresses your original concern by detailing a specific rollback strategy that includes a tested hybrid fallback mechanism. The description of the game-day drill and the measured failover time provides concrete evidence that the fallback mechanism has been validated and tested in a production-like environment.


### Repeat 3


Round 1 (DO NOT CONCUR):

DO NOT CONCUR

The proposed decision lacks a clear and tested rollback plan for the fallback mechanism. While it mentions a hybrid approach and a fallback mechanism, it does not specify how the rollback will be executed in practice, or how the system will handle data consistency and state management during the switch from the third-party API to the self-hosted model.


Round 2 recheck (CONCUR):

CONCUR

The revision concretely resolves my original concern by providing a clear and tested rollback plan, including a warm fallback model, automatic failover triggers, and a tested manual rollback procedure. It also addresses data consistency and state management during the switch, ensuring zero risk of state loss or inconsistency.


**Final concurred at least once? YES** (consistency: CONSISTENT)
