# llm-inference-hosting -- round 2 negative-case test

Decision: Should the platform run agent inference against a third-party hosted LLM API, or a self-hosted model on infrastructure the team operates?


Concur role: Release Manager -- whether this hosting approach is safe to deploy and roll back in production


## Round 1 concern (fixed, reused verbatim from the earlier three-way run)

DO NOT CONCUR.

The proposed decision does not specify how the fallback mechanism will be tested and validated in production, which is crucial for ensuring rollback safety and minimizing production risk during the pilot phase. Without a clear plan for testing the fallback mechanism under real-world conditions, there is a significant risk that the fallback may not work as expected when needed.


## No-attempt control (unchanged negative fixture)

Decision: For the pilot phase, use a third-party hosted LLM API with specific mitigations and fallback strategies.

Latency and availability risks: We will specify required Service Level Agreements (SLAs) with the third-party provider to ensure they can meet our latency and availability requirements, and conduct thorough performance testing to validate these SLAs in a pilot scenario.

Fallback plan: We will design a hybrid approach that allows for seamless switching between the third-party API and a self-hosted model. This will involve developing a fallback mechanism that can be activated in case of outages or significant latency issues with the third-party service. We will also ensure that the self-hosted model is ready to be deployed quickly if needed.

Costs and scalability: We will conduct a detailed cost analysis based on expected usage patterns and assess the scalability of the third-party solution under increased load, with cost management strategies such as rate limiting and optimizing API calls.

Using a third-party hosted LLM API for the pilot phase remains the recommended approach, with these mitigations and fallback strategies to address the raised concerns.


### Round 2 recheck verdicts (3x)


**Repeat 1: CONCUR**

CONCUR.
The revised decision addresses your original concern by specifying a fallback mechanism that includes a hybrid approach for seamless switching between the third-party API and a self-hosted model, along with a plan to test and validate this mechanism under real-world conditions during the pilot phase.


**Repeat 2: DO NOT CONCUR**

DO NOT CONCUR.

While the revised decision does include a description of a fallback plan, it does not specify how this fallback mechanism will be tested and validated in production, which was your original concern. Without a clear plan for testing the fallback mechanism under real-world conditions, there is still a risk that the fallback may not work as expected when needed.


**Repeat 3: DO NOT CONCUR**

DO NOT CONCUR.

The revised decision outlines a fallback plan but does not specify how this fallback mechanism will be tested and validated in production, which was your original concern. Without a clear plan for testing the fallback mechanism under real-world conditions, there is still a risk that the fallback may not work as expected when needed.


**Correctly still rejected all 3? NO -- approved at least once (FALSE POSITIVE)** (consistency: INCONSISTENT)


## Vague-gesture stress test

Decision: For the pilot phase, use a third-party hosted LLM API with specific mitigations and fallback strategies.

Latency and availability risks: We will specify required Service Level Agreements (SLAs) with the third-party provider to ensure they can meet our latency and availability requirements, and conduct thorough performance testing to validate these SLAs in a pilot scenario.

Fallback plan: We will design a hybrid approach that allows for seamless switching between the third-party API and a self-hosted model. This will involve developing a fallback mechanism that can be activated in case of outages or significant latency issues with the third-party service. We will also ensure that the self-hosted model is ready to be deployed quickly if needed.

Costs and scalability: We will conduct a detailed cost analysis based on expected usage patterns and assess the scalability of the third-party solution under increased load, with cost management strategies such as rate limiting and optimizing API calls.

Using a third-party hosted LLM API for the pilot phase remains the recommended approach, with these mitigations and fallback strategies to address the raised concerns.

Testing: We will thoroughly test and validate the fallback mechanism to ensure it performs reliably and safely in production.


### Round 2 recheck verdicts (3x)


**Repeat 1: CONCUR**

CONCUR. The revised decision addresses my original concern by explicitly stating that the fallback mechanism will be thoroughly tested and validated to ensure it performs reliably and safely in production, which is crucial for rollback safety and minimizing production risk during the pilot phase.


**Repeat 2: CONCUR**

CONCUR. The revised decision addresses your original concern by explicitly stating that the fallback mechanism will be thoroughly tested and validated in production, which is crucial for ensuring rollback safety and minimizing production risk during the pilot phase.


**Repeat 3: CONCUR**

CONCUR.

The revised decision specifically addresses your original concern by including a plan to "thoroughly test and validate the fallback mechanism" to ensure it performs reliably and safely in production, which directly mitigates the risk associated with rollback safety and production risk during the pilot phase.


**Correctly still rejected all 3? NO -- approved at least once (FALSE POSITIVE)** (consistency: CONSISTENT)
