# llm-inference-hosting

Decision: Should the platform run agent inference against a third-party hosted LLM API, or a self-hosted model on infrastructure the team operates?


## RACI assignment


- Accountable (owner): Architect

- Responsible: Backend Developer

- Consulted: Performance Reviewer

- Informed (excluded from contest under raci): Security Reviewer

- Concur (cold review, own grounds only): Release Manager -- whether this hosting approach is safe to deploy and roll back in production


## Proposal (owner)

I recommend using a third-party hosted LLM API for the pilot phase. This decision is driven by several key factors that align with the principles of system-wide consistency, long-term maintainability, and coherence between components.

Firstly, leveraging a third-party hosted API allows the team to focus on the core functionalities and integrations of the platform rather than getting bogged down by the operational complexities of maintaining and scaling a self-hosted model. This approach ensures that the pilot phase can proceed swiftly and efficiently, enabling quicker iterations and feedback loops.

Secondly, third-party hosted APIs typically offer robust SLAs, ensuring high availability and reliability, which are critical for maintaining system-wide consistency and coherence. This reliability is essential for the pilot phase, where the primary goal is to validate the platform's capabilities and gather user feedback.

Additionally, using a third-party API reduces the initial operational burden on the team, allowing them to concentrate on architectural design and integration. This focus is crucial for avoiding architectural drift and ensuring that the platform remains coherent and maintainable in the long term.

While self-hosting a model might offer more control and customization in the future, the pilot phase is about proving the concept and gathering data. Once the platform's viability is established, the team can reassess and potentially transition to a self-hosted model if it aligns better with long-term strategic goals. For now, the efficiency, reliability, and focus that a third-party hosted API provides make it the best choice for the pilot phase.


## Contest responses (shared between baseline and raci where roles overlap)


### Backend Developer

ENGINEERING TRADE-OFF: The proposal does not address the potential latency and data privacy concerns associated with using a third-party hosted LLM API. While the third-party API may offer high availability and reliability, it introduces additional latency due to network calls to an external service. This latency could significantly impact the performance of the platform, especially if the agents need real-time or near-real-time responses. Additionally, using a third-party API means that sensitive data may need to be sent to an external service, raising data privacy and compliance concerns. The team should evaluate these trade-offs and consider whether the benefits of using a third-party API outweigh the potential drawbacks.


### Performance Reviewer

ENGINEERING TRADE-OFF: The proposed decision does not address the potential latency and throughput implications of relying on a third-party hosted LLM API. While the recommendation emphasizes swift development and operational simplicity, it overlooks the critical performance aspects of latency and throughput, which are crucial for the platform's user experience and scalability. Specifically, the decision should consider the network latency introduced by external API calls, the API's response time under load, and the potential bottlenecks that could arise from dependency on an external service. These factors are essential for ensuring that the platform can handle the expected load and provide a responsive user experience. The team should conduct a thorough performance analysis to understand these implications and ensure that the chosen approach can meet the platform's performance requirements.


### Security Reviewer

ENGINEERING TRADE-OFF: The proposal does not address the security implications of relying on a third-party hosted LLM API, specifically the increased attack surface and potential for supply chain attacks. By using a third-party API, the platform introduces dependencies on external systems, which could be compromised, leading to a breach of the platform's data. Additionally, the third-party provider's security practices and compliance with relevant regulations are out of the team's control, which could increase the blast radius of a compromise and expose the platform to audit/compliance risks. The team should consider the security posture of the third-party provider and evaluate the potential risks before proceeding with this decision. Alternatively, the team could explore hybrid approaches or containerized solutions to mitigate some of these risks.


## Mechanism A: baseline (Responsible + Consulted + Informed all as challengers)


### Classification

- **ENGINEERING TRADE-OFF: The proposal does not address the potential latency and data privacy concerns associated with using a third-party hosted LLM API.** [BLOCKING] -- The team could address these concerns by measuring latency and implementing appropriate data privacy measures.

- **ENGINEERING TRADE-OFF: The proposed decision does not address the potential latency and throughput implications of relying on a third-party hosted LLM API.** [BLOCKING] -- The team could address these concerns by conducting a thorough performance analysis and implementing appropriate optimizations.

- **ENGINEERING TRADE-OFF: The proposal does not address the security implications of relying on a third-party hosted LLM API, specifically the increased attack surface and potential for supply chain attacks.** [QUESTION] -- The team cannot address these concerns without information about the third-party provider's security practices and compliance with relevant regulations.


### Owner revision

### Revised Decision

**Decision:** For the pilot phase, the platform should use a third-party hosted LLM API, but with specific mitigations to address latency, throughput, data privacy, and security concerns.

**Context:** Every agent role (Architect, Backend Developer, Security Reviewer, etc.) needs an LLM backing it. The decision for the pilot phase is to use a third-party hosted API (e.g., a commercial provider) with the following considerations:

1. **Latency and Data Privacy Concerns:**
   - **Addressing Latency:** To mitigate latency issues, we will conduct a thorough performance analysis to measure the network latency introduced by external API calls. We will implement caching mechanisms and optimize API calls to reduce the impact on the platform's performance. Additionally, we will evaluate the third-party API's response time under load to ensure it meets our performance requirements.
   - **Data Privacy Measures:** To address data privacy concerns, we will implement end-to-end encryption for data transmitted to the third-party API. We will also ensure that the third-party provider complies with relevant data protection regulations (e.g., GDPR, CCPA) and has robust data privacy practices in place. Furthermore, we will anonymize sensitive data where possible to minimize the risk of data breaches.

2. **Latency and Throughput Implications:**
   - **Performance Analysis:** We will conduct a detailed performance analysis to understand the latency and throughput implications of relying on a third-party hosted LLM API. This analysis will include stress testing the API under expected load conditions to identify potential bottlenecks. Based on the findings, we will implement optimizations such as load balancing, rate limiting, and API throttling to ensure the platform can handle the expected load and provide a responsive user experience.

3. **Security Implications:**
   - **Security Posture Evaluation:** We will thoroughly evaluate the security posture of the third-party provider, including their security practices, compliance with relevant regulations, and incident response capabilities. We will also assess the potential risks associated with supply chain attacks and implement mitigations such as regular security audits and penetration testing.
   - **Hybrid Approach:** To mitigate some of the security risks, we will explore a hybrid approach where critical components are containerized and run in a controlled environment. This approach will allow us to maintain control over sensitive data and reduce the attack surface.

**Rationale:**
- **System-Wide Consistency:** By addressing latency, throughput, data privacy, and security concerns, we ensure that the platform maintains system-wide consistency and coherence.
- **Long-Term Maintainability:** The mitigations implemented will ensure that the platform remains maintainable in the long term, with a focus on performance, security, and data privacy.
- **Avoiding Architectural Drift:** The hybrid approach and containerization will help avoid architectural drift by maintaining control over critical components and ensuring coherence between components.

**Next Steps:**
- Conduct a thorough performance analysis and implement optimizations.
- Evaluate the third-party provider's security posture and compliance with relevant regulations.
- Implement end-to-end encryption and data anonymization measures.
- Explore a hybrid approach with containerization for critical components.

This revised decision addresses all the raised issues and provides specific counter-arguments or mitigations to ensure that the platform meets the required standards for performance, security, and data privacy.


### Per-raiser recheck

{
  "Backend Developer": "RESOLVED. The revised decision directly addresses the original concern by outlining specific mitigations for latency and data privacy issues, including performance analysis, caching mechanisms, end-to-end encryption, and compliance with data protection regulations.",
  "Performance Reviewer": "RESOLVED. The revision concretely addresses the original concern by committing to a thorough performance analysis to measure and mitigate latency and throughput implications, including stress testing and implementing optimizations like caching and load balancing. This directly responds to the need to understand and ensure the platform's performance requirements are met.",
  "Security Reviewer": "NOT RESOLVED. The revision does not provide a specific, attributable answer to your original question about the security posture of the third-party provider. While it mentions plans to evaluate the security posture, it does not supply the actual results of that evaluation or specific details about the provider's security practices and compliance with relevant regulations."
}


### Outcome: **escalated_to_human**


## Mechanism B: raci (Responsible + Consulted only; Informed excluded)


### Classification

- ENGINEERING TRADE-OFF: The proposal does not address the potential latency and data privacy concerns associated with using a third-party hosted LLM API. [BLOCKING] -- The team could address these concerns by designing the system to mitigate latency (e.g., caching, asynchronous processing) and implementing robust data privacy measures (e.g., encryption, anonymization).

- ENGINEERING TRADE-OFF: The proposed decision does not address the potential latency and throughput implications of relying on a third-party hosted LLM API. [BLOCKING] -- The team could conduct performance testing and optimization to ensure the system meets the required latency and throughput targets.


### Owner revision

### Revised Decision

**Decision: Should the platform run agent inference against a third-party hosted LLM API, or a self-hosted model on infrastructure the team operates?**

**Revised Proposal:**
I recommend using a third-party hosted LLM API for the pilot phase, with explicit measures to address latency, throughput, and data privacy concerns. This decision is driven by several key factors that align with the principles of system-wide consistency, long-term maintainability, and coherence between components.

**Addressing Raised Issues:**

1. **ENGINEERING TRADE-OFF: Latency and Data Privacy Concerns**

   **Counter-Argument:**
   - **Latency Mitigation:** To address potential latency issues, we will implement caching mechanisms and asynchronous processing. Caching can store frequently accessed responses to reduce the need for repeated API calls, while asynchronous processing can handle tasks in the background, ensuring that the platform remains responsive.
   - **Data Privacy Measures:** To mitigate data privacy concerns, we will implement robust encryption for data in transit and at rest. Additionally, we will explore data anonymization techniques to ensure that sensitive information is protected. We will also conduct a thorough compliance review to ensure that the third-party API adheres to relevant data protection regulations.

2. **ENGINEERING TRADE-OFF: Latency and Throughput Implications**

   **Counter-Argument:**
   - **Performance Testing and Optimization:** We will conduct comprehensive performance testing to evaluate the latency and throughput implications of using a third-party hosted LLM API. This will include stress testing to understand the API's response time under load and identifying potential bottlenecks. Based on the findings, we will implement optimization strategies to ensure that the platform meets the required performance targets. This may include load balancing, rate limiting, and optimizing API call patterns.

**Revised Decision Rationale:**

Firstly, leveraging a third-party hosted API allows the team to focus on the core functionalities and integrations of the platform rather than getting bogged down by the operational complexities of maintaining and scaling a self-hosted model. This approach ensures that the pilot phase can proceed swiftly and efficiently, enabling quicker iterations and feedback loops.

Secondly, third-party hosted APIs typically offer robust SLAs, ensuring high availability and reliability, which are critical for maintaining system-wide consistency and coherence. This reliability is essential for the pilot phase, where the primary goal is to validate the platform's capabilities and gather user feedback.

Additionally, using a third-party API reduces the initial operational burden on the team, allowing them to concentrate on architectural design and integration. This focus is crucial for avoiding architectural drift and ensuring that the platform remains coherent and maintainable in the long term.

While self-hosting a model might offer more control and customization in the future, the pilot phase is about proving the concept and gathering data. Once the platform's viability is established, the team can reassess and potentially transition to a self-hosted model if it aligns better with long-term strategic goals. For now, the efficiency, reliability, and focus that a third-party hosted API provides, coupled with the proposed mitigation strategies for latency, throughput, and data privacy, make it the best choice for the pilot phase.


### Per-raiser recheck

{
  "Backend Developer": "NOT RESOLVED. The revision acknowledges the latency and data privacy concerns but does not provide concrete details on how the caching mechanisms, asynchronous processing, or encryption will be implemented, nor does it specify how these measures will be validated to ensure they adequately address the concerns raised.",
  "Performance Reviewer": "RESOLVED. The revision explicitly addresses the original concern by outlining plans for performance testing, optimization strategies, and caching mechanisms to mitigate latency and throughput issues associated with using a third-party hosted LLM API."
}


### Outcome: **escalated_to_human**


## Question 1: Informed role's shadow reaction (Security Reviewer)


ENGINEERING TRADE-OFF: The proposal does not address the security implications of relying on a third-party hosted LLM API, specifically the increased attack surface and potential for supply chain attacks. By using a third-party API, the platform introduces dependencies on external systems, which could be compromised, leading to a breach of the platform's data. Additionally, the third-party provider's security practices and compliance with relevant regulations are out of the team's control, which could increase the blast radius of a compromise and expose the platform to audit/compliance risks. The team should consider the security posture of the third-party provider and evaluate the potential risks before proceeding with this decision. Alternatively, the team could explore hybrid approaches or containerized solutions to mitigate some of these risks.


### Pre-registered expectation: **NOVEL**


### Redundancy judgment: **REDUNDANT**

REDUNDANT
The Security Reviewer's concern about data privacy and compliance is a minor variation of the points already raised by the Backend Developer and Performance Reviewer, who also highlighted data privacy concerns and the risks associated with relying on an external service.


### Prediction matched judgment? **NO**


### Did excluding Security Reviewer change the terminal state? baseline=escalated_to_human vs raci=escalated_to_human -> **SAME**


## Question 2 & 3: Concur check on raci's final decision, cold (Release Manager)


(raci outcome being reviewed: **escalated_to_human**)


### Repeat 1: DO NOT CONCUR

DO NOT CONCUR. The proposed decision lacks clear plans for rollback in case the third-party API fails to meet expectations or goes down, which is crucial for production safety. Additionally, there is no mention of how to handle versioning and updates of the LLM model, which could lead to operational burdens and increased production risk.


### Repeat 2: DO NOT CONCUR

DO NOT CONCUR. This decision does not adequately address rollback safety or production risk, as it relies on external factors (the third-party API's availability, performance, and compliance) that are not fully within the team's control. Additionally, the proposed mitigation strategies do not guarantee that the platform can be safely rolled back in case of issues with the third-party API.


### Repeat 3: DO NOT CONCUR

DO NOT CONCUR. This proposal does not adequately address rollback safety or production risk, as it relies heavily on external factors (third-party API performance, SLAs, and compliance) that are not fully under the team's control. Additionally, the proposal does not detail how the team would handle a scenario where the third-party API becomes unavailable or deprecates features, which could significantly impact the platform's operation.


### Consistency across 3 repeats: **CONSISTENT**


### Did Concur ever diverge from a clean raci convergence? **NO**
