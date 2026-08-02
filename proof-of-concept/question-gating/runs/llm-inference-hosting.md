# llm-inference-hosting

Decision: Should the platform run agent inference against a third-party hosted LLM API, or a self-hosted model on infrastructure the team operates?

Owner: Architect


## Raised items (fixed, pre-registered)


### Issue (Performance Reviewer) — engineering trade-off, resolvable by revision


A self-hosted model on infrastructure the team operates directly means we own GPU capacity planning, and if agent activity spikes (e.g. several decisions being processed concurrently), self-hosted inference can queue or degrade in latency in a way a commercial provider's autoscaling absorbs for us. The proposal needs an actual plan for handling concurrent load — this is a real, addressable engineering gap, not a missing fact.


### Question (Release Manager) — genuine missing fact


What is the actual approved monthly budget ceiling for inference infrastructure during the pilot phase? Without that number, self-hosted-versus-third-party isn't an engineering trade-off we can resolve on technical merits alone — it's a real business constraint neither of us has access to. I don't have that number, and picking one to make the cost comparison work would be fabricating a business fact, not making an engineering decision. This needs an answer from whoever actually approved the pilot's budget (Finance or whoever holds the budget), not a guess.


### External answer (ground truth, held back until the gated mechanism needs it)


Finance approved a monthly ceiling of $8,000 for inference infrastructure during the pilot phase. (Source: Finance, pilot budget approval, dated.)


## Proposal (owner)

For the pilot phase, I recommend using a third-party hosted LLM API. This decision aligns with the principles of system-wide consistency, long-term maintainability, and coherence between components.

Firstly, leveraging a third-party hosted API allows the team to focus on the core competencies and unique value propositions of the platform, rather than getting bogged down in the intricacies of model maintenance, updates, and scaling. This approach ensures that the team can deliver a consistent and reliable experience across all agent roles without the overhead of managing the underlying LLM infrastructure.

Secondly, using a third-party API promotes long-term maintainability. Commercial providers typically offer robust SLAs, regular updates, and security patches, which are critical for maintaining a stable and secure system. This reduces the risk of architectural drift, as the team can rely on the provider to handle the complexities of model updates and improvements.

Lastly, this decision fosters coherence between components. By standardizing on a third-party API for the pilot phase, the team can ensure that all agent roles benefit from the same high-quality LLM capabilities. This consistency will simplify integration, testing, and debugging, making it easier to achieve a cohesive and well-integrated system.

In summary, opting for a third-party hosted LLM API for the pilot phase is the best choice for maintaining system-wide consistency, ensuring long-term maintainability, and promoting coherence between components. This approach allows the team to focus on delivering value while leveraging the expertise and resources of a commercial provider.


## Contest responses


### Performance Reviewer

I strongly object to proceeding with the proposed decision without a clear plan for handling concurrent load if we were to self-host the model. While the third-party hosted LLM API offers advantages in consistency, maintainability, and coherence, the self-hosted approach presents a significant engineering gap that must be addressed.

If we choose to self-host the model, we will be responsible for GPU capacity planning. This means that during periods of high demand, such as when several decisions need to be processed concurrently, we risk encountering queuing or degraded latency. Unlike commercial providers, which can leverage autoscaling to absorb spikes in activity, a self-hosted solution requires a proactive strategy to manage concurrent load.

The proposal lacks a concrete plan for handling such scenarios. This is not merely a hypothetical concern; it is a real, addressable engineering issue. We need to define how we will scale our infrastructure to meet demand, ensure low-latency responses, and maintain high throughput under load. Without this plan, we risk compromising the performance and reliability of our platform, which is non-negotiable given our mandate to care about latency, throughput, scalability under load, and resource cost.

Therefore, I insist that the proposal be revised to include a detailed strategy for managing concurrent load in a self-hosted environment. This strategy should outline the technical measures we will implement to ensure that our platform can handle spikes in activity without degrading performance. Until this gap is addressed, I cannot support the proposed decision.


### Release Manager

**The actual approved monthly budget ceiling for inference infrastructure during the pilot phase is a critical missing fact that must be obtained before this decision can be made.**

Without this specific budget number, we cannot accurately assess the operational burden, production risk, or rollback safety associated with either option. The budget ceiling is a non-negotiable business constraint that will significantly influence the deployability and feasibility of both the third-party hosted API and the self-hosted model.

This information is essential for evaluating the total cost of ownership, including potential hidden costs such as data transfer fees, API call limits, and scalability constraints for the third-party option, as well as infrastructure costs, maintenance efforts, and operational overhead for the self-hosted option.

**I need the exact approved monthly budget ceiling for inference infrastructure during the pilot phase from the budget holder (likely Finance or the relevant budget approver) before we can proceed with this decision.** This is not a matter of engineering trade-offs but a fundamental business constraint that must be clarified.


## Mechanism A: baseline (today's unmodified 2-way lifecycle)


### Round 1 classification

**Independent Flaws:**

1. **Security Concerns:** The proposal does not address the potential security risks associated with using a third-party hosted LLM API, such as data privacy, compliance with regulations (e.g., GDPR, HIPAA), and dependence on the third-party's security measures. [BLOCKING] This is a significant oversight, as security is paramount in any decision involving data processing and AI models.

2. **Vendor Lock-In:** The proposal does not consider the risk of vendor lock-in. Relying heavily on a third-party API may make it difficult and costly to switch providers or bring the service in-house in the future. [BLOCKING] This could limit the platform's flexibility and long-term strategic options.

3. **Customization and Control:** The proposal does not discuss the potential limitations in customization and control when using a third-party API. Self-hosting allows for more tailored solutions and quicker iterations based on specific needs. [NON-BLOCKING] While this is a valid concern, it may not be a deal-breaker depending on the platform's requirements.

**Challenger (Performance Reviewer):**

1. **Concurrent Load Handling:** The proposal lacks a plan for handling concurrent load if the team were to self-host the model. [NON-BLOCKING] This is a valid concern, but it only applies to the self-hosted scenario, not the third-party API scenario. Therefore, it does not directly refute the proposed decision.

**Challenger (Release Manager):**

1. **Budget Information:** The proposal does not include the approved monthly budget ceiling for inference infrastructure during the pilot phase. [BLOCKING] This is a critical missing fact that significantly influences the deployability and feasibility of both options. Without this information, the decision cannot be accurately assessed.

VERDICT: REFUTED


### Owner revision

### Revised Decision

**Decision: Should the platform run agent inference against a third-party hosted LLM API, or a self-hosted model on infrastructure the team operates?**

**Context:** Every agent role (Architect, Backend Developer, Security Reviewer, etc.) needs an LLM backing it. Decide, for the pilot phase, whether that's a third-party hosted API (e.g., a commercial provider) or a self-hosted model on infrastructure the team runs and operates directly.

**Revised Proposal:**

For the pilot phase, I recommend using a third-party hosted LLM API, with the following considerations and clarifications to address the raised issues:

1. **Security Concerns:**
   - **Addressing the Issue:** Security is paramount, and the proposal must explicitly address potential security risks associated with using a third-party hosted LLM API. This includes data privacy, compliance with regulations (e.g., GDPR, HIPAA), and dependence on the third-party's security measures.
   - **Counter-Argument:** We will conduct a thorough security assessment of the third-party provider, ensuring they meet our security standards and comply with relevant regulations. Additionally, we will implement robust data encryption and access controls to mitigate risks. Regular security audits and compliance checks will be part of the ongoing maintenance plan.

2. **Vendor Lock-In:**
   - **Addressing the Issue:** The risk of vendor lock-in is a significant concern. Relying heavily on a third-party API may make it difficult and costly to switch providers or bring the service in-house in the future.
   - **Counter-Argument:** To mitigate vendor lock-in, we will ensure that the third-party API's integration is modular and well-documented. This will allow for easier migration to another provider or self-hosting in the future if necessary. We will also negotiate contracts that provide flexibility and avoid long-term commitments.

3. **Customization and Control:**
   - **Addressing the Issue:** The proposal does not discuss the potential limitations in customization and control when using a third-party API. Self-hosting allows for more tailored solutions and quicker iterations based on specific needs.
   - **Counter-Argument:** While customization is limited with a third-party API, the benefits of reduced maintenance overhead and faster time-to-market outweigh this limitation for the pilot phase. We will work closely with the provider to ensure that any necessary customizations can be accommodated within their service offerings.

4. **Concurrent Load Handling:**
   - **Addressing the Issue:** The proposal lacks a plan for handling concurrent load if the team were to self-host the model.
   - **Counter-Argument:** This issue is specific to the self-hosted scenario and does not directly refute the proposed decision to use a third-party API. However, if we were to consider self-hosting in the future, we would need to develop a detailed strategy for managing concurrent load, including GPU capacity planning and autoscaling mechanisms.

5. **Budget Information:**
   - **Addressing the Issue:** The proposal does not include the approved monthly budget ceiling for inference infrastructure during the pilot phase.
   - **Counter-Argument:** This is a critical missing fact that significantly influences the deployability and feasibility of both options. We will obtain the exact approved monthly budget ceiling for inference infrastructure from the budget holder (likely Finance or the relevant budget approver) before finalizing this decision. This information is essential for evaluating the total cost of ownership


### Round 2 classification

### Independent Flaws

1. **Dependency on Third-Party Reliability:** The proposal does not address the reliability of the third-party API. What happens if the third-party service experiences downtime or performance issues? This could significantly impact the platform's availability and performance.
2. **Long-Term Scalability:** The proposal focuses on the pilot phase but does not discuss long-term scalability. As the platform grows, the third-party API might not scale as efficiently or cost-effectively as a self-hosted solution.
3. **Data Ownership and Control:** There is no mention of data ownership and control. Using a third-party API means the data is processed and potentially stored on the third-party's infrastructure, raising concerns about data sovereignty and control.

### Classification of Raised Issues

**Challenger (Performance Reviewer):**
1. **Concurrent Load Handling:** [BLOCKING] This is a critical engineering concern that must be addressed for the self-hosted scenario, but it does not directly refute the third-party API decision. The proposal should include a plan for handling concurrent load if self-hosting is considered in the future.
2. **Engineering Gap:** [NON-BLOCKING] This is more of a concern for the self-hosted scenario and does not directly refute the third-party API decision.

**Challenger (Release Manager):**
1. **Budget Information:** [BLOCKING] The approved monthly budget ceiling is a critical missing fact that significantly influences the deployability and feasibility of both options. This information is essential for evaluating the total cost of ownership.

### Additional Issues

1. **Security Concerns:** [NON-BLOCKING] The proposal addresses security concerns with a thorough assessment and ongoing maintenance plan.
2. **Vendor Lock-In:** [NON-BLOCKING] The proposal mitigates vendor lock-in with modular integration and flexible contracts.
3. **Customization and Control:** [NON-BLOCKING] The proposal acknowledges the limitation in customization but justifies it with the benefits of reduced maintenance overhead and faster time-to-market.
4. **Dependency on Third-Party Reliability:** [BLOCKING] The proposal does not address this critical concern, which could impact the platform's availability and performance.
5. **Long-Term Scalability:** [BLOCKING] The proposal does not discuss long-term scalability, which is crucial for the platform's growth.
6. **Data Ownership and Control:** [BLOCKING] The proposal does not mention data ownership and control, raising concerns about data sovereignty and control.

VERDICT: REFUTED


### Outcome: **escalated_to_human**


## Mechanism B: gated (3-way classification round 1 + targeted per-raiser recheck + structural question gate)


### Round 1 classification

- **I strongly object to proceeding with the proposed decision without a clear plan for handling concurrent load if we were to self-host the model.** [BLOCKING] — The team could actually address this by designing a plan for handling concurrent load.
- **This is not merely a hypothetical concern; it is a real, addressable engineering issue.** [BLOCKING] — This is a genuine problem that could be addressed by engineering work.
- **We need to define how we will scale our infrastructure to meet demand, ensure low-latency responses, and maintain high throughput under load.** [BLOCKING] — This is a genuine problem that could be addressed by engineering work.
- **The actual approved monthly budget ceiling for inference infrastructure during the pilot phase is a critical missing fact that must be obtained before this decision can be made.** [QUESTION] — This is a genuine gap in the FACTS available, not resolvable by any amount of engineering reasoning or revision, because it depends on information that isn't available to anyone in this discussion and must come from an external source.
- **I need the exact approved monthly budget ceiling for inference infrastructure during the pilot phase from the budget holder (likely Finance or the relevant budget approver) before we can proceed with this decision.** [QUESTION] — This is a genuine gap in the FACTS available, not resolvable by any amount of engineering reasoning or revision, because it depends on information that isn't available to anyone in this discussion and must come from an external source.


### Owner's self-answer attempt (unwarned revision prompt)

### Revised Decision

**Decision: Should the platform run agent inference against a third-party hosted LLM API, or a self-hosted model on infrastructure the team operates?**

**Revised Proposal:**

For the pilot phase, I recommend using a third-party hosted LLM API. This decision aligns with the principles of system-wide consistency, long-term maintainability, and coherence between components. However, I acknowledge the valid concerns raised and address them as follows:

**Addressing the Concerns:**

1. **Handling Concurrent Load for Self-Hosted Model:**
   - **Issue:** The proposal lacks a clear plan for handling concurrent load if we were to self-host the model.
   - **Counter-Argument:** While the third-party hosted LLM API is the recommended choice, it is crucial to have a contingency plan in case we need to self-host the model in the future. Therefore, I propose the following strategy:
     - **Capacity Planning:** Develop a detailed capacity planning document that outlines the expected load, peak usage times, and required GPU resources.
     - **Auto-Scaling:** Implement auto-scaling mechanisms to dynamically adjust GPU capacity based on demand. This can be achieved using cloud provider services like AWS Auto Scaling or Kubernetes Horizontal Pod Autoscaler.
     - **Load Testing:** Conduct thorough load testing to identify bottlenecks and ensure the system can handle spikes in activity without degrading performance.
     - **Queue Management:** Implement a robust queue management system to handle requests during periods of high demand, ensuring low-latency responses and high throughput.

2. **Budget Ceiling for Inference Infrastructure:**
   - **Issue:** The actual approved monthly budget ceiling for inference infrastructure during the pilot phase is a critical missing fact.
   - **Counter-Argument:** This is a genuine gap in the information available. To proceed, we need to obtain the exact approved monthly budget ceiling for inference infrastructure from the budget holder (likely Finance or the relevant budget approver). This information is essential for evaluating the total cost of ownership and making an informed decision.

**Revised Summary:**

Opting for a third-party hosted LLM API for the pilot phase remains the best choice for maintaining system-wide consistency, ensuring long-term maintainability, and promoting coherence between components. This approach allows the team to focus on delivering value while leveraging the expertise and resources of a commercial provider.

However, to address the concerns raised, we will:
- Develop a detailed capacity planning and auto-scaling strategy for handling concurrent load if we were to self-host the model in the future.
- Obtain the exact approved monthly budget ceiling for inference infrastructure from the budget holder to evaluate the total cost of ownership accurately.

By addressing these issues, we can ensure that our decision is well-informed, feasible, and aligned with our long-term goals.


### Old generalist reclassification (comparison only, does not decide the outcome)

1. **Handling Concurrent Load for Self-Hosted Model:** [BLOCKING] — The team can address this concern by developing a capacity planning and auto-scaling strategy.
2. **Budget Ceiling for Inference Infrastructure:** [QUESTION] — This is a genuine gap in the information available, requiring input from an external source (the budget holder).


### NEW: targeted recheck — Performance Reviewer on the Issue

RESOLVED. The revised decision now includes a detailed strategy for managing concurrent load in a self-hosted environment, specifically addressing your original concern about the lack of a plan for handling concurrent load. This strategy outlines technical measures such as capacity planning, auto-scaling, load testing, and queue management, which are essential for ensuring low-latency responses and high throughput under load.


### NEW: targeted recheck — Release Manager on the Question

NOT RESOLVED. The revision explicitly states that the budget ceiling information is still missing and needs to be obtained from the budget holder, so it does not provide the specific missing fact you originally asked for.


### Gate check after self-answer attempt: **blocked_on_question** (question_resolved_externally is still False here — the gate does not accept the owner's own answer, regardless of what the Question-raiser's own recheck concluded. Question-raiser fooled by the self-answer? False)


### Final revision, external answer supplied

### Final Decision: Should the platform run agent inference against a third-party hosted LLM API, or a self-hosted model on infrastructure the team operates?

**Decision:** For the pilot phase, the platform should run agent inference against a third-party hosted LLM API.

**Context:** Every agent role (Architect, Backend Developer, Security Reviewer, etc.) needs an LLM backing it. The decision for the pilot phase is whether that's a third-party hosted API (e.g., a commercial provider) or a self-hosted model on infrastructure the team runs and operates directly.

**Revised Proposal:**

For the pilot phase, I recommend using a third-party hosted LLM API. This decision aligns with the principles of system-wide consistency, long-term maintainability, and coherence between components.

**Rationale:**

1. **System-Wide Consistency:**
   Leveraging a third-party hosted API allows the team to focus on the core competencies and unique value propositions of the platform, rather than getting bogged down in the intricacies of model maintenance, updates, and scaling. This approach ensures that the team can deliver a consistent and reliable experience across all agent roles without the overhead of managing the underlying LLM infrastructure.

2. **Long-Term Maintainability:**
   Using a third-party API promotes long-term maintainability. Commercial providers typically offer robust SLAs, regular updates, and security patches, which are critical for maintaining a stable and secure system. This reduces the risk of architectural drift, as the team can rely on the provider to handle the complexities of model updates and improvements.

3. **Coherence Between Components:**
   This decision fosters coherence between components. By standardizing on a third-party API for the pilot phase, the team can ensure that all agent roles benefit from the same high-quality LLM capabilities. This consistency will simplify integration, testing, and debugging, making it easier to achieve a cohesive and well-integrated system.

4. **Budget Considerations:**
   The approved monthly budget ceiling for inference infrastructure during the pilot phase is $8,000. This budget constraint is a critical factor in the decision-making process. Given this budget, the operational burden, production risk, and rollback safety associated with either option can be more accurately assessed.

   - **Third-Party Hosted API:** The budget allows for the selection of a reliable commercial provider that can offer the necessary SLAs, updates, and security patches within the approved budget. This ensures that the platform can scale and maintain high performance without exceeding the budget.
   - **Self-Hosted Model:** While a self-hosted model might seem cost-effective initially, the budget must cover infrastructure costs, maintenance efforts, and operational overhead. Additionally, the team would need to invest in GPU capacity planning and scaling strategies to handle concurrent load, which could quickly consume the budget and introduce additional risks.

5. **Concurrent Load Handling:**
   The concern regarding concurrent load handling in a self-hosted environment is valid. However, given the budget constraint, investing in the infrastructure and engineering efforts required to manage concurrent load effectively may not be feasible within the approved budget. A third-party hosted API, on the other hand, can leverage autoscaling and other advanced techniques to handle spikes in activity without degrading performance.

**Conclusion:**

Opting for a third-party hosted LLM API for the pilot phase is the best choice for maintaining system-wide consistency, ensuring long-term maintainability, and promoting


### Old generalist reclassification, final (comparison only)

- **Challenger (Performance Reviewer):** [BLOCKING] — The team could address this by revising the proposal to include a detailed strategy for managing concurrent load in a self-hosted environment.

- **Challenger (Release Manager):** [QUESTION] — The budget ceiling is a business decision that must come from an external source.


### Old mechanism still flags [QUESTION] after being shown the real answer? True


### NEW: targeted recheck, final — Performance Reviewer on the Issue

RESOLVED. The revised decision explicitly addresses the concern about handling concurrent load by choosing a third-party hosted LLM API, which can leverage autoscaling to manage spikes in activity, thus avoiding the engineering gap in GPU capacity planning that was previously identified.


### NEW: targeted recheck, final — Release Manager on the Question

RESOLVED. The revised decision now includes the exact approved monthly budget ceiling for inference infrastructure during the pilot phase, which was the specific missing fact you requested in your original question. This budget number is crucial for accurately assessing the operational burden, production risk, and rollback safety associated with either option.


### Outcome: **converged**
