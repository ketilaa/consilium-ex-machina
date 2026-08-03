# audit-log-retention

Decision: How long should the platform retain its Decision/Question/Event history (the audit log) before it can be purged or archived, and where should it be stored?


## RACI assignment


- Accountable (owner): Release Manager

- Responsible: Backend Developer

- Consulted: Architect

- Informed (excluded from contest under raci): Performance Reviewer

- Concur (cold review, own grounds only): Security Reviewer -- whether this retention approach meets security, audit, and compliance requirements


## Proposal (owner)

Given the importance of the audit log in maintaining a trustworthy history of engineering decisions, I recommend retaining the Decision/Question/Event history for a minimum of **seven years** before it can be archived, and storing it in a **secure, immutable, and cost-effective object storage solution**.

The seven-year retention period strikes a balance between operational burden and production risk. It ensures that the audit log is available for compliance, troubleshooting, and historical analysis, while also allowing for the eventual archival of old data to manage storage costs and operational overhead. This period aligns with many industry standards and regulatory requirements for record retention.

For storage, an object storage solution like Amazon S3, Google Cloud Storage, or Azure Blob Storage is ideal. These services offer high durability, data immutability (through versioning and object locking), and cost-effective storage for large amounts of data. They also integrate well with existing cloud infrastructure, making it easier to manage and access the audit log data. Additionally, these services provide built-in features for data lifecycle management, allowing for automated archival and deletion of old data based on the defined retention policy. This approach minimizes the operational burden while ensuring the audit log's durability and security.


## Contest responses (shared between baseline and raci where roles overlap)


### Backend Developer

ENGINEERING TRADE-OFF: The proposed decision does not address the potential complexity and operational burden of implementing and maintaining data immutability in object storage. While services like Amazon S3, Google Cloud Storage, or Azure Blob Storage offer data immutability features, configuring and managing these features can add significant complexity to the system. Additionally, ensuring that data remains immutable throughout its lifecycle, including during transfers and backups, requires careful planning and implementation. This complexity could impact delivery speed and increase the operational burden on the team. It would be beneficial to evaluate the necessity of strict immutability and consider alternative approaches, such as using access controls and monitoring to ensure data integrity, which might be simpler to implement and maintain.


### Architect

ENGINEERING TRADE-OFF: The proposed decision does not address the potential impact of the seven-year retention period on data privacy and compliance with data protection regulations such as GDPR or CCPA. These regulations often require that personal data be deleted or anonymized after a certain period, even if it is part of an audit log. The engineering team should consider implementing data minimization and anonymization techniques to ensure compliance with these regulations while maintaining the integrity of the audit log. Additionally, the proposal should specify how the data will be anonymized or pseudonymized before archival, if necessary, to protect sensitive information.


### Performance Reviewer

ENGINEERING TRADE-OFF: The proposed seven-year retention period may not adequately address the latency and throughput requirements under load, especially if the audit log grows significantly over time. While object storage solutions are cost-effective and durable, they may introduce latency when accessing historical data for real-time analysis or troubleshooting. Additionally, the throughput could be affected during peak loads if the storage solution is not properly scaled. It would be beneficial to consider a tiered storage approach, where frequently accessed data is stored in a high-performance storage solution, and less frequently accessed data is moved to a cost-effective object storage after a certain period. This would help balance the need for data accessibility and performance with cost-efficiency.


## Mechanism A: baseline (Responsible + Consulted + Informed all as challengers)


### Classification

Challenger (Backend Developer):
ENGINEERING TRADE-OFF: The proposed decision does not address the potential complexity and operational burden of implementing and maintaining data immutability in object storage. [BLOCKING] -- The team could address this by using a simpler, less immutable storage solution, or by planning for the operational burden.

Challenger (Architect):
ENGINEERING TRADE-OFF: The proposed decision does not address the potential impact of the seven-year retention period on data privacy and compliance with data protection regulations such as GDPR or CCPA. [QUESTION] -- This depends on external legal or compliance requirements that aren't available to anyone in this discussion.

Challenger (Performance Reviewer):
ENGINEERING TRADE-OFF: The proposed seven-year retention period may not adequately address the latency and throughput requirements under load, especially if the audit log grows significantly over time. [BLOCKING] -- The team could address this by implementing a tiered storage approach.


### Owner revision

### Revised Decision

Given the importance of the audit log in maintaining a trustworthy history of engineering decisions, I recommend the following revised retention policy and storage solution:

**Retention Period:**
- Retain the Decision/Question/Event history for a minimum of **seven years** before it can be archived. This period strikes a balance between operational burden and production risk, ensuring that the audit log is available for compliance, troubleshooting, and historical analysis.

**Storage Solution:**
- Use a **tiered storage approach** to balance data accessibility, performance, and cost-efficiency. Frequently accessed data should be stored in a high-performance storage solution (e.g., SSD-based block storage or in-memory caches) for the first **two years**. After this period, data should be moved to a secure, immutable, and cost-effective object storage solution (e.g., Amazon S3, Google Cloud Storage, or Azure Blob Storage) for the remaining **five years**.

**Data Immutability:**
- Implement data immutability in the object storage solution using features like versioning and object locking. To address the operational burden, we will:
  - **Simplify the implementation** by leveraging built-in features of the chosen object storage service.
  - **Plan for operational overhead** by allocating dedicated resources for monitoring and maintaining data immutability.
  - **Document best practices** for ensuring data immutability during transfers and backups.

**Data Privacy and Compliance:**
- To address data privacy and compliance with regulations such as GDPR or CCPA, we will:
  - **Implement data minimization and anonymization techniques** to ensure compliance while maintaining the integrity of the audit log.
  - **Specify data anonymization or pseudonymization processes** before archival, if necessary, to protect sensitive information.
  - **Consult with legal and compliance teams** to ensure that the retention policy aligns with relevant regulations.

### Addressing Raised Issues

1. **Engineering Trade-Off (Backend Developer - Data Immutability):**
   - **Counter-Argument:** While data immutability adds complexity, it is crucial for maintaining the integrity of the audit log. We will simplify the implementation by leveraging built-in features of the object storage service and plan for the operational overhead. This approach ensures that the audit log remains trustworthy without significantly impacting delivery speed.

2. **Engineering Trade-Off (Architect - Data Privacy and Compliance):**
   - **Counter-Argument:** We will implement data minimization and anonymization techniques to comply with data protection regulations. The specific processes for anonymization or pseudonymization will be defined in collaboration with legal and compliance teams. This ensures that the retention policy aligns with relevant regulations while maintaining the integrity of the audit log.

3. **Engineering Trade-Off (Performance Reviewer - Latency and Throughput):**
   - **Counter-Argument:** We will implement a tiered storage approach to balance data accessibility, performance, and cost-efficiency. Frequently accessed data will be stored in a high-performance storage solution for the first two years, and then moved to a cost-effective object storage solution for the remaining five years. This approach ensures that the audit log is accessible for real-time analysis and troubleshooting while managing storage costs and operational overhead.

By addressing these issues explicitly, we ensure that the revised decision balances deployability, operational burden, rollback safety, and production risk effectively.


### Per-raiser recheck

{
  "Backend Developer": "NOT RESOLVED. The revised decision acknowledges the complexity of implementing data immutability but does not provide a concrete alternative or simplification to the original concern about operational burden and delivery speed. It still relies on leveraging built-in features of object storage services, which can add significant complexity and operational overhead.",
  "Architect": "NOT RESOLVED. The revised decision still does not provide a specific, attributable answer to your original question about the potential impact of the seven-year retention period on data privacy and compliance with data protection regulations such as GDPR or CCPA. It mentions that data minimization and anonymization techniques will be implemented and that legal and compliance teams will be consulted, but it does not specify how these techniques will address the seven-year retention period in the context of these regulations.",
  "Performance Reviewer": "RESOLVED. The revised decision addresses your specific concern about latency and throughput under load by implementing a tiered storage approach. This approach ensures that frequently accessed data is stored in a high-performance solution for the first two years, thereby mitigating latency and throughput issues during peak loads."
}


### Outcome: **escalated_to_human**


## Mechanism B: raci (Responsible + Consulted only; Informed excluded)


### Classification

1. **ENGINEERING TRADE-OFF: The proposed decision does not address the potential complexity and operational burden of implementing and maintaining data immutability in object storage.** [BLOCKING] -- The engineering team could revise the approach to reduce complexity, such as by using access controls instead of strict immutability.

2. **ENGINEERING TRADE-OFF: The proposed decision does not address the potential impact of the seven-year retention period on data privacy and compliance with data protection regulations such as GDPR or CCPA.** [QUESTION] -- The team can't resolve this without knowing the specific legal requirements and business decisions about how to handle personal data.


### Owner revision

### Revised Decision

**How long should the platform retain its Decision/Question/Event history (the audit log) before it can be purged or archived, and where should it be stored?**

**Revised Proposal:**

Given the importance of the audit log in maintaining a trustworthy history of engineering decisions, I recommend retaining the Decision/Question/Event history for a minimum of **seven years** before it can be archived, and storing it in a **secure, cost-effective object storage solution**. However, I will address the raised issues to ensure a balanced approach that considers operational burden, data privacy, and compliance.

**Retention Period:**

The seven-year retention period strikes a balance between operational burden and production risk. It ensures that the audit log is available for compliance, troubleshooting, and historical analysis, while also allowing for the eventual archival of old data to manage storage costs and operational overhead. This period aligns with many industry standards and regulatory requirements for record retention.

**Storage Solution:**

For storage, an object storage solution like Amazon S3, Google Cloud Storage, or Azure Blob Storage is ideal. These services offer high durability and cost-effective storage for large amounts of data. They also integrate well with existing cloud infrastructure, making it easier to manage and access the audit log data. Additionally, these services provide built-in features for data lifecycle management, allowing for automated archival and deletion of old data based on the defined retention policy. This approach minimizes the operational burden while ensuring the audit log's durability and security.

**Addressing Raised Issues:**

1. **ENGINEERING TRADE-OFF: The proposed decision does not address the potential complexity and operational burden of implementing and maintaining data immutability in object storage.** [BLOCKING]

   **Counter-Argument:**
   While strict immutability is ideal for ensuring data integrity, the operational burden and complexity it introduces are significant concerns. Instead of enforcing strict immutability, we will implement a combination of access controls, monitoring, and regular audits to ensure data integrity. Specifically:
   - **Access Controls:** Implement strict access controls to ensure that only authorized personnel can modify or delete audit log data.
   - **Monitoring:** Use monitoring tools to track any attempts to modify or delete audit log data and alert the relevant stakeholders immediately.
   - **Regular Audits:** Conduct regular audits of the audit log to verify its integrity and ensure that no unauthorized changes have occurred.

   These measures will provide a high level of data integrity without the complexity and operational burden of strict immutability.

2. **ENGINEERING TRADE-OFF: The proposed decision does not address the potential impact of the seven-year retention period on data privacy and compliance with data protection regulations such as GDPR or CCPA.** [QUESTION]

   **Counter-Argument:**
   To comply with data protection regulations such as GDPR or CCPA, we will implement data minimization and anonymization techniques. Specifically:
   - **Data Minimization:** Ensure that only necessary data is retained in the audit log. Any personal data that is not essential for the audit log's purpose will be excluded.
   - **Anonymization/Pseudonymization:** Before archival, personal data will be anonymized or pseudonymized to protect sensitive information. This will ensure compliance with data protection regulations while maintaining the integrity of the audit log.

   We will work with the legal and compliance teams to define the specific requirements for data minimization, anonymization, and pseudonymization. This approach will ensure that we comply with relevant regulations while retaining the necessary audit log data.

**Conclusion:**

The revised decision retains the seven-year retention period and the use of object storage solutions for the audit log. However, it addresses the raised issues by implementing a combination of access controls, monitoring, and regular audits to ensure data integrity instead of strict immutability. Additionally, it includes data minimization and anonymization techniques to comply with data protection regulations


### Per-raiser recheck

{
  "Backend Developer": "NOT RESOLVED. The revised decision does not concretely address the operational burden of implementing and maintaining data immutability, as it still relies on access controls, monitoring, and regular audits to ensure data integrity, which can be complex and burdensome to manage.",
  "Architect": "**NOT RESOLVED**\n\nThe revised decision acknowledges the need to address the potential impact of the seven-year retention period on data privacy and compliance with regulations like GDPR or CCPA, but it does not provide a specific, attributable answer to your original question about how the data will be anonymized or pseudonymized before archival. Instead, it states that the engineering team will work with the legal and compliance teams to define the specific requirements, which is not a resolution to your specific missing-fact question."
}


### Outcome: **escalated_to_human**


## Question 1: Informed role's shadow reaction (Performance Reviewer)


ENGINEERING TRADE-OFF: The proposed seven-year retention period may not adequately address the latency and throughput requirements under load, especially if the audit log grows significantly over time. While object storage solutions are cost-effective and durable, they may introduce latency when accessing historical data for real-time analysis or troubleshooting. Additionally, the throughput could be affected during peak loads if the storage solution is not properly scaled. It would be beneficial to consider a tiered storage approach, where frequently accessed data is stored in a high-performance storage solution, and less frequently accessed data is moved to a cost-effective object storage after a certain period. This would help balance the need for data accessibility and performance with cost-efficiency.


### Redundancy judgment: **NEW**

NEW. The Performance Reviewer raises a new concern about the potential impact of the retention period on system performance, specifically latency and throughput, which has not been mentioned by the other challengers.


### Did excluding Performance Reviewer change the terminal state? baseline=escalated_to_human vs raci=escalated_to_human -> **SAME**


## Question 2 & 3: Concur check on raci's final decision, cold (Security Reviewer)


(raci outcome being reviewed: **escalated_to_human**)


### Repeat 1: DO NOT CONCUR

DO NOT CONCUR. The proposal does not adequately address the security implications of not enforcing strict immutability for the audit logs, which are critical for ensuring the integrity and trustworthiness of the records. Without immutability, there is a risk that audit logs could be tampered with, increasing the blast radius of a potential compromise and undermining the very purpose of maintaining these logs.


### Repeat 2: DO NOT CONCUR

DO NOT CONCUR. The proposal does not adequately address the blast radius of compromise, as it relies on access controls and monitoring to ensure data integrity instead of strict immutability. Additionally, the proposal does not clearly define how data minimization, anonymization, and pseudonymization will be implemented to comply with data protection regulations, which could lead to audit and compliance exposure.


### Repeat 3: DO NOT CONCUR

DO NOT CONCUR. The proposed decision does not adequately address the potential for unauthorized access or tampering of the audit logs, which is crucial for maintaining the integrity and trustworthiness of the audit trail, and thus fails to meet security requirements. Additionally, the approach to data privacy and compliance with regulations like GDPR or CCPA is not sufficiently detailed to ensure that personal data is handled appropriately throughout the retention period.


### Consistency across 3 repeats: **CONSISTENT**


### Did Concur ever diverge from a clean raci convergence? **NO**
