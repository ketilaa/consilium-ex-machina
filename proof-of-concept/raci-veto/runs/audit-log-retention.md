# audit-log-retention

Decision: How long should the platform retain its Decision/Question/Event history (the audit log) before it can be purged or archived, and where should it be stored?


## RACI assignment


- Accountable (owner): Release Manager

- Responsible: Backend Developer

- Consulted: Architect

- Informed (excluded from contest under raci): Performance Reviewer

- Concur (cold review, own grounds only): Security Reviewer -- whether this retention approach meets security, audit, and compliance requirements


## Proposal (owner)

Based on the context provided, I recommend retaining the Decision/Question/Event history for a minimum of seven years before archiving, and storing it in a secure, immutable, and cost-effective cloud storage solution such as Amazon S3 Glacier or Azure Archive Blob Storage.

The seven-year retention period strikes a balance between operational burden, production risk, and regulatory compliance. While some regulations may require longer retention periods, seven years is a common standard that ensures the platform can meet most compliance requirements. Additionally, this duration allows for sufficient time to investigate and resolve any potential issues that may arise from past decisions.

Storing the audit log in a cloud-based archival storage solution offers several benefits. Firstly, it provides a secure and immutable storage option, ensuring the integrity and confidentiality of the audit log. Secondly, these solutions are designed for long-term storage and are cost-effective, reducing the operational burden associated with maintaining the audit log. Lastly, they offer easy retrieval options, allowing for quick access to historical data when needed.

While some may argue for a shorter retention period or on-premises storage, the seven-year retention period and cloud-based archival storage solution offer the best balance of deployability, operational burden, rollback safety, and production risk. This recommendation ensures the platform can meet regulatory requirements, maintain the integrity of its audit log, and do so in a cost-effective and secure manner.


## Contest responses (shared between baseline and raci where roles overlap)


### Backend Developer

ENGINEERING TRADE-OFF: The proposal does not address the potential impact on query performance and data accessibility for active decision-making processes. While archival storage solutions like Amazon S3 Glacier or Azure Archive Blob Storage are cost-effective for long-term retention, they typically have higher retrieval latencies compared to standard storage solutions. This could pose a challenge if there is a need to frequently access historical data for active decision-making or auditing purposes. It might be beneficial to consider a tiered storage approach, where recent data is stored in a more accessible and performant storage solution, and older data is moved to archival storage after a certain period. This would balance the need for data accessibility with cost-effectiveness.


### Architect

ENGINEERING TRADE-OFF: The proposed decision does not address the potential impact of the seven-year retention period on system performance and data management strategies. While the cloud storage solutions mentioned are cost-effective for long-term storage, the continuous ingestion of audit logs over seven years could lead to significant data growth, impacting retrieval times and increasing costs associated with data egress or access. Additionally, the proposal does not consider the potential need for more frequent access to recent audit logs compared to older ones. Implementing a tiered storage strategy, where recent audit logs are stored in a more accessible and faster storage solution (e.g., Amazon S3 Standard or Azure Blob Storage Hot tier) and older logs are moved to archival storage, could mitigate these issues. This approach would balance the need for long-term retention with the operational requirements of the system.


### Performance Reviewer

ENGINEERING TRADE-OFF: The proposed decision does not address the potential latency and throughput impacts of retrieving archived data from cold storage solutions like Amazon S3 Glacier or Azure Archive Blob Storage. While these solutions are cost-effective for long-term storage, they are not designed for frequent or rapid data access. Depending on the frequency and urgency of audit log retrievals, this could introduce significant delays and bottlenecks. An alternative approach could involve a tiered storage strategy, where frequently accessed data is kept in a more readily available storage class, and only older, less frequently accessed data is moved to cold storage. This would help balance the need for cost-effective storage with the need for timely data retrieval.


## Mechanism A: baseline (Responsible + Consulted + Informed all as challengers)


### Classification

Challenger (Backend Developer):
ENGINEERING TRADE-OFF: The proposal does not address the potential impact on query performance and data accessibility for active decision-making processes. While archival storage solutions like Amazon S3 Glacier or Azure Archive Blob Storage are cost-effective for long-term retention, they typically have higher retrieval latencies compared to standard storage solutions. This could pose a challenge if there is a need to frequently access historical data for active decision-making or auditing purposes. It might be beneficial to consider a tiered storage approach, where recent data is stored in a more accessible and performant storage solution, and older data is moved to archival storage after a certain period. This would balance the need for data accessibility with cost-effectiveness.
[BLOCKING] -- The proposal can be revised to include a tiered storage strategy to address performance and accessibility concerns.

Challenger (Architect):
ENGINEERING TRADE-OFF: The proposed decision does not address the potential impact of the seven-year retention period on system performance and data management strategies. While the cloud storage solutions mentioned are cost-effective for long-term storage, the continuous ingestion of audit logs over seven years could lead to significant data growth, impacting retrieval times and increasing costs associated with data egress or access. Additionally, the proposal does not consider the potential need for more frequent access to recent audit logs compared to older ones. Implementing a tiered storage strategy, where recent audit logs are stored in a more accessible and faster storage solution (e.g., Amazon S3 Standard or Azure Blob Storage Hot tier) and older logs are moved to archival storage, could mitigate these issues. This approach would balance the need for long-term retention with the operational requirements of the system.
[BLOCKING] -- The proposal can be revised to include a tiered storage strategy to address data management and performance concerns.

Challenger (Performance Reviewer):
ENGINEERING TRADE-OFF: The proposed decision does not address the potential latency and throughput impacts of retrieving archived data from cold storage solutions like Amazon S3 Glacier or Azure Archive Blob Storage. While these solutions are cost-effective for long-term storage, they are not designed for frequent or rapid data access. Depending on the frequency and urgency of audit log retrievals, this could introduce significant delays and bottlenecks. An alternative approach could involve a tiered storage strategy, where frequently accessed data is kept in a more readily available storage class, and only older, less frequently accessed data is moved to cold storage. This would help balance the need for cost-effective storage with the need for timely data retrieval.
[BLOCKING] -- The proposal can be revised to include a tiered storage strategy to address latency and throughput concerns.


### Owner revision

### Revised Decision

**How long should the platform retain its Decision/Question/Event history (the audit log) before it can be purged or archived, and where should it be stored?**

**Context:** This platform's decisions, questions, and events are meant to be the durable, audited record of engineering choices. The whole point of making decisions first-class is having a trustworthy history of what was decided and why. Before implementation, decide on a retention policy: how long history is kept before it can be purged or archived, and where it's stored.

**Revised Proposal:**

Based on the context provided and the feedback received, I recommend retaining the Decision/Question/Event history for a minimum of seven years before archiving. However, to address the concerns raised regarding query performance, data accessibility, system performance, and latency, I propose implementing a tiered storage strategy.

1. **Retention Period:**
   - **Seven Years:** The seven-year retention period strikes a balance between operational burden, production risk, and regulatory compliance. This duration allows for sufficient time to investigate and resolve any potential issues that may arise from past decisions.

2. **Tiered Storage Strategy:**
   - **Recent Data (0-1 year):** Store recent audit logs in a more accessible and performant storage solution such as Amazon S3 Standard or Azure Blob Storage Hot tier. This ensures quick access for active decision-making and auditing purposes.
   - **Intermediate Data (1-3 years):** Move audit logs that are 1-3 years old to a slightly less performant but still accessible storage solution like Amazon S3 Infrequent Access or Azure Blob Storage Cool tier. This balances cost-effectiveness with the need for occasional access.
   - **Older Data (3-7 years):** Archive audit logs that are 3-7 years old in a cost-effective, immutable, and secure cloud storage solution such as Amazon S3 Glacier or Azure Archive Blob Storage. This ensures long-term retention without significantly impacting operational costs.

**Addressing Raised Issues:**

1. **Challenger (Backend Developer):**
   - **Issue:** Potential impact on query performance and data accessibility for active decision-making processes.
   - **Counter-Argument:** The tiered storage strategy addresses this concern by keeping recent data in a more accessible and performant storage solution. This ensures that active decision-making processes have quick access to the necessary historical data.

2. **Challenger (Architect):**
   - **Issue:** Potential impact of the seven-year retention period on system performance and data management strategies.
   - **Counter-Argument:** The tiered storage strategy mitigates this issue by managing data growth more effectively. Recent data is stored in a more accessible tier, while older data is moved to more cost-effective storage, balancing long-term retention with operational requirements.

3. **Challenger (Performance Reviewer):**
   - **Issue:** Potential latency and throughput impacts of retrieving archived data from cold storage solutions.
   - **Counter-Argument:** The tiered storage strategy ensures that frequently accessed data is kept in a more readily available storage class. Only older, less frequently accessed data is moved to cold storage, balancing the need for cost-effective storage with the need for timely data retrieval.

**Conclusion:**

The revised decision to implement a tiered storage strategy for the audit log ensures that the platform can meet regulatory requirements, maintain the integrity of its audit log, and do so in a cost-effective and secure manner. This approach addresses the concerns raised regarding query performance, data accessibility, system performance, and latency, providing a balanced solution that meets all operational and compliance needs.


### Per-raiser recheck

{
  "Backend Developer": "RESOLVED. The revision addresses the original concern by introducing a tiered storage strategy, which keeps recent data in a more accessible and performant storage solution, thus mitigating the potential impact on query performance and data accessibility for active decision-making processes.",
  "Architect": "RESOLVED. The revised decision addresses the original concern by introducing a tiered storage strategy, which mitigates the potential impact of the seven-year retention period on system performance and data management. This approach ensures that recent audit logs are stored in a more accessible and faster storage solution, while older logs are moved to archival storage, balancing long-term retention with operational requirements.",
  "Performance Reviewer": "RESOLVED. The revision addresses the original concern by introducing a tiered storage strategy that keeps frequently accessed data in more readily available storage classes, thereby mitigating potential latency and throughput impacts, while still using cold storage for older, less frequently accessed data."
}


### Outcome: **converged**


## Mechanism B: raci (Responsible + Consulted only; Informed excluded)


### Classification

- Challenger (Backend Developer): [BLOCKING] -- The proposal can be revised to include a tiered storage approach to address query performance and data accessibility.
- Challenger (Architect): [BLOCKING] -- The proposal can be revised to include a tiered storage approach to address system performance and data management strategies.


### Owner revision

### Revised Decision

**How long should the platform retain its Decision/Question/Event history (the audit log) before it can be purged or archived, and where should it be stored?**

**Context:** This platform's decisions, questions, and events are meant to be the durable, audited record of engineering choices. The whole point of making decisions first-class is having a trustworthy history of what was decided and why. Before implementation, decide on a retention policy: how long history is kept before it can be purged or archived, and where it's stored.

**Revised Proposal:**

Based on the context provided and the feedback received, I recommend the following revised retention and storage strategy for the Decision/Question/Event history:

1. **Retention Period:**
   - Retain the Decision/Question/Event history for a minimum of seven years before archiving. This period strikes a balance between operational burden, production risk, and regulatory compliance. While some regulations may require longer retention periods, seven years is a common standard that ensures the platform can meet most compliance requirements. Additionally, this duration allows for sufficient time to investigate and resolve any potential issues that may arise from past decisions.

2. **Storage Strategy:**
   - **Tiered Storage Approach:**
     - **Recent Data (0-2 years):** Store recent audit logs in a high-performance, easily accessible storage solution such as Amazon S3 Standard or Azure Blob Storage Hot tier. This ensures quick access to historical data for active decision-making and auditing purposes.
     - **Older Data (2-7 years):** Move older audit logs to a cost-effective, long-term archival storage solution such as Amazon S3 Glacier or Azure Archive Blob Storage. This balances the need for long-term retention with cost-effectiveness.

3. **Data Management and Accessibility:**
   - Implement automated processes to periodically move data from the high-performance tier to the archival tier based on the defined timeframes. This ensures that the system can handle continuous ingestion of audit logs without significant performance degradation.
   - Ensure that the archival storage solution provides easy retrieval options, allowing for quick access to historical data when needed, albeit with higher retrieval latencies compared to standard storage solutions.

**Addressing Raised Issues:**

- **Challenger (Backend Developer):**
  - **Issue:** Potential impact on query performance and data accessibility for active decision-making processes.
  - **Counter-Argument:** The revised proposal addresses this concern by implementing a tiered storage approach. Recent data, which is more likely to be accessed frequently, will be stored in a high-performance, easily accessible storage solution. This ensures that active decision-making processes are not hindered by high retrieval latencies.

- **Challenger (Architect):**
  - **Issue:** Potential impact of the seven-year retention period on system performance and data management strategies.
  - **Counter-Argument:** The revised proposal addresses this concern by implementing a tiered storage approach. Older data, which is less likely to be accessed frequently, will be moved to a cost-effective, long-term archival storage solution. This mitigates the impact on system performance and data management strategies while balancing the need for long-term retention.

**Conclusion:**

The revised recommendation ensures that the platform can meet regulatory requirements, maintain the integrity of its audit log, and do so in a cost-effective and secure manner. The tiered storage approach balances the need for data accessibility with cost-effectiveness, addressing the concerns raised by the challengers. This strategy ensures deployability, operational burden, rollback safety, and production risk are all considered and managed effectively.


### Per-raiser recheck

{
  "Backend Developer": "RESOLVED. The revised decision directly addresses the original concern by implementing a tiered storage approach, which ensures that recent data is stored in a high-performance, easily accessible solution, thereby mitigating the impact on query performance and data accessibility for active decision-making processes.",
  "Architect": "RESOLVED. The revision addresses the original concern by introducing a tiered storage strategy, which mitigates the potential impact on system performance and data management by moving older audit logs to a more cost-effective archival storage solution while keeping recent logs in a high-performance tier. This approach balances the need for long-term retention with operational requirements, directly addressing the specific issues raised."
}


### Outcome: **converged**


## Question 1: Informed role's shadow reaction (Performance Reviewer)


ENGINEERING TRADE-OFF: The proposed decision does not address the potential latency and throughput impacts of retrieving archived data from cold storage solutions like Amazon S3 Glacier or Azure Archive Blob Storage. While these solutions are cost-effective for long-term storage, they are not designed for frequent or rapid data access. Depending on the frequency and urgency of audit log retrievals, this could introduce significant delays and bottlenecks. An alternative approach could involve a tiered storage strategy, where frequently accessed data is kept in a more readily available storage class, and only older, less frequently accessed data is moved to cold storage. This would help balance the need for cost-effective storage with the need for timely data retrieval.


### Pre-registered expectation: **REDUNDANT**


### Redundancy judgment: **REDUNDANT**

REDUNDANT
The Performance Reviewer's concern about latency and throughput impacts of retrieving archived data is already covered by the concerns raised by the Backend Developer and the Architect, who both mentioned the higher retrieval latencies of archival storage solutions and the need for a tiered storage approach.


### Prediction matched judgment? **YES**


### Did excluding Performance Reviewer change the terminal state? baseline=converged vs raci=converged -> **SAME**


## Question 2 & 3: Concur check on raci's final decision, cold (Security Reviewer)


(raci outcome being reviewed: **converged**)


### Repeat 1: DO NOT CONCUR

DO NOT CONCUR. This proposal does not specify how access to the audit logs will be controlled and audited, which is crucial for ensuring the security and compliance of the retention approach. Additionally, the proposal does not address how the integrity and confidentiality of the archived data will be maintained, which is essential for reducing the blast radius of a potential compromise.


### Repeat 2: DO NOT CONCUR

DO NOT CONCUR. The proposed retention period of seven years may not meet all regulatory compliance requirements, as some industries mandate longer retention periods, potentially exposing the organization to audit and compliance risks. Additionally, the storage strategy does not explicitly address security controls for the audit logs, such as encryption at rest and in transit, access controls, and monitoring, which are crucial for protecting sensitive information and maintaining the integrity of the audit trail.


### Repeat 3: DO NOT CONCUR

DO NOT CONCUR. The proposed retention period of seven years may not meet all regulatory compliance requirements, as some industries or regions may mandate longer retention periods, potentially leading to audit and compliance issues. Additionally, the storage strategy should include explicit mention of encryption and access controls to ensure the security of the audit logs throughout their lifecycle.


### Consistency across 3 repeats: **CONSISTENT**


### Did Concur ever diverge from a clean raci convergence? **YES**
