# llm-inference-hosting

Decision: Should the platform run agent inference against a third-party hosted LLM API, or a self-hosted model on infrastructure the team operates?


## RACI assignment


- Accountable (owner): Architect

- Responsible: Backend Developer

- Consulted: Performance Reviewer

- Informed (excluded from contest under raci): Security Reviewer

- Concur (cold review, own grounds only): Release Manager -- whether this hosting approach is safe to deploy and roll back in production


## Proposal (owner)

For the pilot phase, I recommend using a third-party hosted LLM API. This decision is driven by several key factors that align with the principles of system-wide consistency, long-term maintainability, and coherence between components.

Firstly, leveraging a third-party hosted LLM API allows the team to focus on core competencies rather than getting bogged down by the operational complexities of maintaining and scaling a self-hosted model. This includes handling infrastructure, updates, and ensuring high availability, all of which can divert resources away from the primary goals of the pilot phase. By offloading these responsibilities to a reliable third-party provider, the team can ensure a more consistent and maintainable system.

Secondly, using a third-party API promotes coherence between components. It provides a standardized interface that can be easily integrated across different agent roles, ensuring that the LLM capabilities are consistent and reliable. This consistency is crucial for the pilot phase, where the focus should be on validating the overall architecture and gathering feedback rather than troubleshooting infrastructure issues.

Additionally, third-party APIs often come with robust security measures and compliance certifications, which can be challenging to replicate in a self-hosted environment. This is particularly important given the sensitive nature of the data that may be processed by the agents. By relying on a trusted third-party provider, the team can ensure that security and compliance requirements are met without additional overhead.

In summary, using a third-party hosted LLM API for the pilot phase is the recommended approach. It allows the team to maintain focus on core objectives, ensures system-wide consistency, and promotes long-term maintainability and coherence between components. This decision will help in avoiding architectural drift and setting a strong foundation for future phases.


## Contest responses (shared between baseline and raci where roles overlap)


### Backend Developer

ENGINEERING TRADE-OFF: The proposal does not address the potential latency and availability risks associated with relying on a third-party hosted LLM API. While the proposal mentions high availability, it does not consider the scenario where the third-party service experiences outages or significant latency issues. These problems could severely impact the performance and reliability of the agents, especially if the agents require real-time or near-real-time responses. Additionally, the proposal does not discuss the potential costs associated with high usage of the third-party API, which could become a significant operational burden as the system scales. It would be prudent to have a fallback plan or a hybrid approach that allows for seamless switching between the third-party API and a self-hosted model in case of such issues.


### Performance Reviewer

ENGINEERING TRADE-OFF: The proposal does not address the potential latency and throughput implications of using a third-party hosted LLM API. While offloading operational complexities to a third-party provider has its advantages, it introduces dependencies on external network conditions, API response times, and potential rate limiting or throttling. These factors can significantly impact the latency and throughput of the system, especially under load. It is crucial to evaluate the performance characteristics of the third-party API in a pilot scenario to ensure it meets the required service level agreements (SLAs) for the platform. Additionally, consider the scalability of the third-party solution under increased load and the associated costs, as these factors could affect the overall performance and resource efficiency of the system.


### Security Reviewer

ENGINEERING TRADE-OFF: The proposed decision does not address the increased blast radius of compromise that comes with using a third-party hosted LLM API. By relying on an external service, the platform becomes dependent on the security posture of the third-party provider. A compromise of the third-party API could potentially affect all agents using it, leading to a significant blast radius. Additionally, the platform loses direct control over the infrastructure, making it harder to implement and audit security measures tailored to the specific needs of the project. To mitigate this, consider evaluating the third-party provider's security practices, implementing strict access controls, and having a contingency plan in case the third-party service is compromised. Alternatively, explore hybrid approaches where critical components are self-hosted to reduce the blast radius.


## Mechanism A: baseline (Responsible + Consulted + Informed all as challengers)


### Classification

1. **Latency and availability risks** [BLOCKING] -- The team could address this by negotiating SLAs with the third-party provider, implementing caching strategies, or designing a fallback mechanism.
2. **Costs associated with high usage** [QUESTION] -- This depends on the specific pricing model of the third-party provider, which is not available in the discussion.
3. **Latency and throughput implications** [BLOCKING] -- The team could conduct performance testing with the third-party API to understand and mitigate these issues.
4. **Scalability under increased load** [QUESTION] -- This depends on the specific scalability limits and pricing of the third-party provider, which are not available in the discussion.
5. **Increased blast radius of compromise** [NON-BLOCKING] -- While this is a valid concern, it is not a blocking issue as the team can implement additional security measures and contingency plans to mitigate this risk.
6. **Loss of direct control over infrastructure** [NON-BLOCKING] -- This is a valid point but does not block the decision, as the team can work with the third-party provider to ensure security measures are in place.


### Owner revision

### Revised Decision

**Decision:** For the pilot phase, I recommend using a third-party hosted LLM API, with specific measures to address the raised issues. This decision is driven by several key factors that align with the principles of system-wide consistency, long-term maintainability, and coherence between components.

#### Addressing Raised Issues

1. **Latency and availability risks** [BLOCKING]
   - **Action:** Negotiate Service Level Agreements (SLAs) with the third-party provider to ensure high availability and low latency. Implement caching strategies to reduce the frequency of API calls and mitigate latency issues. Design a fallback mechanism that allows the system to switch to a self-hosted model in case of significant outages or latency problems. This fallback mechanism will ensure that the platform remains reliable and performant even if the third-party service experiences issues.

2. **Costs associated with high usage** [QUESTION]
   - **Action:** Conduct a detailed cost analysis based on the expected usage patterns and the pricing model of the third-party provider. Include contingency plans for scaling costs in the budget. Consider implementing usage monitoring and optimization strategies to manage costs effectively. If the costs become prohibitive, explore hybrid approaches that balance third-party usage with self-hosted solutions.

3. **Latency and throughput implications** [BLOCKING]
   - **Action:** Perform comprehensive performance testing with the third-party API under various load conditions to understand its latency and throughput characteristics. Use the results to optimize the integration and ensure it meets the required Service Level Agreements (SLAs). Implement load balancing and throttling mechanisms to manage API usage and maintain performance.

4. **Scalability under increased load** [QUESTION]
   - **Action:** Evaluate the scalability limits and pricing of the third-party provider. Ensure that the provider can scale to meet the anticipated load and that the associated costs are manageable. Develop a scalability plan that includes potential upgrades or migrations to more scalable solutions if needed.

5. **Increased blast radius of compromise** [NON-BLOCKING]
   - **Counter-argument:** While this is a valid concern, it does not block the decision. The team will implement additional security measures, including strict access controls, regular security audits, and a contingency plan in case of a compromise. The third-party provider's security practices will be thoroughly evaluated to ensure they meet the platform's security requirements.

6. **Loss of direct control over infrastructure** [NON-BLOCKING]
   - **Counter-argument:** This is a valid point but does not block the decision. The team will work closely with the third-party provider to ensure that security measures are in place and that the provider adheres to the platform's security standards. Regular audits and compliance checks will be conducted to maintain control over the security posture of the infrastructure.

#### Summary

Using a third-party hosted LLM API for the pilot phase remains the recommended approach. By addressing the latency and availability risks through SLAs, caching, and fallback mechanisms, and by conducting thorough performance and cost analyses, the team can ensure a reliable and maintainable system. The additional security measures and contingency plans will mitigate the increased blast radius of compromise, while regular audits and compliance checks will address the loss of direct control over infrastructure. This decision will help in avoiding architectural drift and setting a strong foundation for future phases.


### Per-raiser recheck

{
  "Backend Developer": "RESOLVED. The revised decision addresses the original concern by implementing SLAs, caching strategies, and a fallback mechanism to mitigate latency and availability risks associated with the third-party hosted LLM API. These measures ensure that the system can remain reliable and performant even if the third-party service experiences issues.",
  "Performance Reviewer": "NOT RESOLVED. The revised decision does not provide a specific, attributable answer to your original question about the potential latency and throughput implications of using a third-party hosted LLM API. While it mentions plans to perform performance testing, it does not supply the actual results or specific data points that would address the missing fact you raised.",
  "Security Reviewer": "NOT RESOLVED. The revised decision does mention implementing additional security measures, strict access controls, regular security audits, and a contingency plan, but it does not provide concrete details on how these measures will be implemented or verified to effectively mitigate the increased blast radius of compromise you originally raised."
}


### Outcome: **escalated_to_human**


## Mechanism B: raci (Responsible + Consulted only; Informed excluded)


### Classification

1. **ENGINEERING TRADE-OFF: The proposal does not address the potential latency and availability risks associated with relying on a third-party hosted LLM API.** [BLOCKING] -- The team could address this by specifying required SLAs and ensuring the third-party provider can meet them, and by planning for fallback strategies.

2. **These problems could severely impact the performance and reliability of the agents, especially if the agents require real-time or near-real-time responses.** [NON-BLOCKING] -- This is a valid concern but does not necessitate a change in the decision; it's a risk that can be managed.

3. **Additionally, the proposal does not discuss the potential costs associated with high usage of the third-party API, which could become a significant operational burden as the system scales.** [QUESTION] -- This depends on the specific pricing model of the third-party provider, which is not available.

4. **It would be prudent to have a fallback plan or a hybrid approach that allows for seamless switching between the third-party API and a self-hosted model in case of such issues.** [BLOCKING] -- The team could address this by designing a hybrid approach or a clear fallback plan.

5. **The proposal does not address the potential latency and throughput implications of using a third-party hosted LLM API.** [BLOCKING] -- The team could address this by conducting performance testing and ensuring the third-party provider can meet the required SLAs.

6. **It is crucial to evaluate the performance characteristics of the third-party API in a pilot scenario to ensure it meets the required service level agreements (SLAs) for the platform.** [BLOCKING] -- The team could address this by specifying required SLAs and conducting performance testing.

7. **Additionally, consider the scalability of the third-party solution under increased load and the associated costs, as these factors could affect the overall performance and resource efficiency of the system.** [QUESTION] -- This depends on the specific scalability and pricing model of the third-party provider, which is not available.


### Owner revision

### Revised Decision

**Decision: For the pilot phase, I recommend using a third-party hosted LLM API with specific mitigations and fallback strategies.**

#### Addressing Raised Issues

1. **ENGINEERING TRADE-OFF: The proposal does not address the potential latency and availability risks associated with relying on a third-party hosted LLM API.** [BLOCKING]
   - **Counter-Argument/Action:** We will specify required Service Level Agreements (SLAs) with the third-party provider to ensure they can meet our latency and availability requirements. Additionally, we will conduct thorough performance testing to validate these SLAs in a pilot scenario.

2. **These problems could severely impact the performance and reliability of the agents, especially if the agents require real-time or near-real-time responses.** [NON-BLOCKING]
   - **Counter-Argument:** This is a valid concern but does not necessitate a change in the decision. We will manage this risk by ensuring the third-party provider can meet our SLAs and by implementing monitoring and alerting mechanisms to quickly identify and address any performance issues.

3. **Additionally, the proposal does not discuss the potential costs associated with high usage of the third-party API, which could become a significant operational burden as the system scales.** [QUESTION]
   - **Counter-Argument/Action:** We will conduct a detailed cost analysis based on the expected usage patterns and the specific pricing model of the third-party provider. This analysis will help us understand the potential costs and plan for scaling accordingly. We will also explore cost management strategies, such as rate limiting and optimizing API calls.

4. **It would be prudent to have a fallback plan or a hybrid approach that allows for seamless switching between the third-party API and a self-hosted model in case of such issues.** [BLOCKING]
   - **Counter-Argument/Action:** We will design a hybrid approach that allows for seamless switching between the third-party API and a self-hosted model. This will involve developing a fallback mechanism that can be activated in case of outages or significant latency issues with the third-party service. We will also ensure that the self-hosted model is ready to be deployed quickly if needed.

5. **The proposal does not address the potential latency and throughput implications of using a third-party hosted LLM API.** [BLOCKING]
   - **Counter-Argument/Action:** We will conduct performance testing to evaluate the latency and throughput implications of using the third-party API. This testing will include stress testing under expected load conditions to ensure the API can meet our performance requirements. We will also specify required SLAs with the third-party provider to address these concerns.

6. **It is crucial to evaluate the performance characteristics of the third-party API in a pilot scenario to ensure it meets the required service level agreements (SLAs) for the platform.** [BLOCKING]
   - **Counter-Argument/Action:** We will conduct a pilot phase where we thoroughly evaluate the performance characteristics of the third-party API. This will include performance testing, monitoring, and validation against our required SLAs. The results of this evaluation will inform our decision to continue with the third-party API or consider alternative solutions.

7. **Additionally, consider the scalability of the third-party solution under increased load and the associated costs, as these factors could affect the overall performance and resource efficiency of the system.** [QUESTION]
   - **Counter-Argument/Action:** We will assess the scalability of the third-party solution by conducting load testing and evaluating the provider's ability to handle increased demand. We will also analyze the associated costs and ensure they align with our budget and resource efficiency goals. This assessment will help us make informed decisions about scaling and potential cost management strategies.

#### Summary

Using a third-party hosted LLM API for the pilot phase remains the recommended approach, but with specific mitigations and fallback strategies to address the raised concerns. We will:

-


### Per-raiser recheck

{
  "Backend Developer": "RESOLVED. The revised decision addresses the original concern by specifying that a hybrid approach will be designed, allowing for seamless switching between the third-party API and a self-hosted model in case of outages or significant latency issues. This directly mitigates the potential latency and availability risks associated with relying solely on a third-party hosted LLM API.",
  "Performance Reviewer": "RESOLVED. The revised decision directly addresses your concern by committing to performance testing to evaluate latency and throughput, and by specifying required SLAs with the third-party provider to ensure they meet performance requirements."
}


### Outcome: **converged**


## Question 1: Informed role's shadow reaction (Security Reviewer)


ENGINEERING TRADE-OFF: The proposed decision does not address the increased blast radius of compromise that comes with using a third-party hosted LLM API. By relying on an external service, the platform becomes dependent on the security posture of the third-party provider. A compromise of the third-party API could potentially affect all agents using it, leading to a significant blast radius. Additionally, the platform loses direct control over the infrastructure, making it harder to implement and audit security measures tailored to the specific needs of the project. To mitigate this, consider evaluating the third-party provider's security practices, implementing strict access controls, and having a contingency plan in case the third-party service is compromised. Alternatively, explore hybrid approaches where critical components are self-hosted to reduce the blast radius.


### Redundancy judgment: **NEW**

NEW. The Security Reviewer raises a distinct concern about the security risks and increased blast radius of compromise associated with using a third-party hosted LLM API, which was not explicitly addressed in the existing concerns.


### Did excluding Security Reviewer change the terminal state? baseline=escalated_to_human vs raci=converged -> **DIFFERS**


## Question 2 & 3: Concur check on raci's final decision, cold (Release Manager)


(raci outcome being reviewed: **converged**)


### Repeat 1: DO NOT CONCUR

DO NOT CONCUR. The decision lacks a clear and tested rollback strategy in case the third-party hosted LLM API fails to meet expectations or experiences significant issues, which is crucial for production safety. Additionally, the plan to switch to a self-hosted model as a fallback is not detailed enough to ensure a smooth and safe rollback process.


### Repeat 2: DO NOT CONCUR

DO NOT CONCUR. The proposal does not adequately address rollback safety: the hybrid approach described does not ensure that the self-hosted model can be quickly and safely deployed in case of issues with the third-party API. Additionally, the plan lacks details on how to manage data consistency and state during a switch between the third-party API and the self-hosted model.


### Repeat 3: DO NOT CONCUR

**DO NOT CONCUR**. The proposal does not adequately address the rollback safety and operational burden associated with switching between the third-party API and a self-hosted model. Specifically, the plan for a hybrid approach and fallback mechanism needs more detail on how seamless the switch will be and what the operational implications are, particularly in a production environment.


### Consistency across 3 repeats: **CONSISTENT**


### Did Concur ever diverge from a clean raci convergence? **YES**
