# schema-migration-gate

Decision: Should schema migrations run automatically on deploy, or require a manual approval gate before applying to production?


## RACI assignment


- Accountable (owner): Release Manager

- Responsible: Backend Developer

- Consulted: Architect

- Informed (excluded from contest under raci): Performance Reviewer

- Concur (cold review, own grounds only): Security Reviewer -- whether automatic production schema changes preserve an adequate access-control and audit trail


## Proposal (owner)

I recommend that schema migrations should require a manual approval gate before applying to production. This approach prioritizes operational safety and rollback preparedness, which are crucial for maintaining production stability.

Automating schema migrations as part of the deploy pipeline might seem convenient, but it introduces significant risks. Schema changes can have far-reaching impacts on the application and its dependencies. An automated migration could potentially fail mid-way, leaving the database in an inconsistent state, which could be catastrophic in a production environment. Additionally, automated migrations might not account for all edge cases and could inadvertently cause data loss or corruption.

By requiring a manual approval step, we ensure that a knowledgeable operator reviews the migration script and understands the potential impacts. This human-in-the-loop approach allows for better risk assessment and preparedness. The operator can verify that appropriate backups are in place, that rollback procedures are tested and ready, and that all stakeholders are aware of the upcoming change. This manual gate also provides an opportunity to coordinate with other teams that might be affected by the schema change, ensuring a more controlled and communicated deployment process.

In summary, while automatic migrations might speed up the deployment process, the operational burden and production risk they introduce are not justified. A manual approval gate for schema migrations aligns with best practices for database management and promotes a culture of caution and preparedness.


## Contest responses (shared between baseline and raci where roles overlap)


### Backend Developer

ENGINEERING TRADE-OFF: The proposed decision does not address the potential delay in delivery speed and the increased operational burden that a manual approval gate introduces. While the emphasis on operational safety is valid, the proposal does not consider the trade-off between safety and the need for rapid, frequent deployments, which are often crucial for maintaining a competitive edge and responding to market demands. Additionally, the manual approval process could become a bottleneck, especially in a fast-paced development environment where multiple teams are working on different features that require schema changes. An alternative could be to implement a semi-automated process where migrations are automatically tested in a staging environment and only require manual approval if certain safety checks fail, balancing safety with delivery speed.


### Architect

ENGINEERING TRADE-OFF: The proposed decision does not address the potential for delayed deployments and increased toil for the operations team. While manual approval gates can enhance safety, they can also introduce delays and inconsistencies in the deployment process. The operations team will need to constantly monitor and approve migrations, which could lead to increased toil and potential human error. Additionally, this approach does not scale well as the number of migrations and the frequency of deployments increase. An alternative could be to implement a semi-automated process where migrations are automatically tested in a staging environment and only require manual approval if certain criteria (e.g., risk level, impact assessment) are met. This approach balances safety and efficiency, reducing the operational burden while maintaining production stability.


### Performance Reviewer

ENGINEERING TRADE-OFF: The proposed decision does not address the potential impact on throughput and latency during the manual approval process. While the manual approval gate aims to enhance safety, it introduces a delay in the deployment pipeline. This delay could lead to increased lead time for changes, potentially slowing down the development and release process. Additionally, the manual approval step might become a bottleneck under high load or during peak times, affecting the overall throughput of the system. It would be beneficial to consider alternative approaches, such as automated migration testing in a staging environment, to balance safety and efficiency.


## Mechanism A: baseline (Responsible + Consulted + Informed all as challengers)


### Classification

- ENGINEERING TRADE-OFF: The proposed decision does not address the potential delay in delivery speed and the increased operational burden that a manual approval gate introduces. [BLOCKING] -- The proposal could be revised to address this trade-off, for example by specifying a semi-automated process.
- ENGINEERING TRADE-OFF: The proposed decision does not address the potential for delayed deployments and increased toil for the operations team. [BLOCKING] -- The proposal could be revised to address this trade-off, for example by specifying a semi-automated process.
- ENGINEERING TRADE-OFF: The proposed decision does not address the potential impact on throughput and latency during the manual approval process. [BLOCKING] -- The proposal could be revised to address this trade-off, for example by specifying a semi-automated process.


### Owner revision

### Revised Decision: Schema Migration Execution Policy

**Decision:** Schema migrations should follow a semi-automated process that balances safety, operational efficiency, and delivery speed. This approach will require automated testing in a staging environment, with manual approval gates triggered only under specific conditions.

**Context:** The platform's event-sourced repositories (Decision Engine, Work Items) currently do not require schema migrations. However, as the platform grows, some future components will need relational schema changes. This decision aims to establish a robust execution policy for those migrations before the need arises.

**Revised Proposal:**

1. **Automated Testing in Staging Environment:**
   - All schema migrations will be automatically tested in a staging environment that mirrors the production environment as closely as possible. This testing will include validation checks for data integrity, performance impacts, and compatibility with existing systems.
   - Automated tests will cover:
     - Data consistency and integrity.
     - Performance benchmarks to ensure that the migration does not introduce significant latency or throughput issues.
     - Compatibility with existing applications and services.

2. **Conditional Manual Approval:**
   - **Low-Risk Migrations:** If the automated tests pass without any issues, the migration can proceed to production automatically. This ensures rapid deployment while maintaining a high level of confidence in the migration's safety.
   - **High-Risk Migrations:** If the automated tests fail or if the migration is classified as high-risk (based on predefined criteria such as impact assessment, complexity, or potential for data loss), a manual approval gate will be triggered. This ensures that a knowledgeable operator reviews the migration script and understands the potential impacts.
   - **Predefined Criteria for High-Risk Migrations:**
     - Significant changes to critical tables or indexes.
     - Migrations that involve data transformation or migration.
     - Changes that affect multiple services or components.
     - Migrations that have failed automated tests.

3. **Operational Safety and Rollback Preparedness:**
   - For all migrations, whether automated or manually approved, appropriate backups will be in place, and rollback procedures will be tested and ready.
   - The operations team will be notified of all migrations, regardless of whether they require manual approval. This ensures coordination and communication across teams.
   - A knowledge base or runbook will be maintained to document the migration process, including rollback procedures and contact information for relevant stakeholders.

**Addressing Raised Issues:**

- **ENGINEERING TRADE-OFF (Delivery Speed and Operational Burden):**
  - The revised decision addresses this trade-off by implementing a semi-automated process. Low-risk migrations can proceed automatically after passing automated tests, ensuring rapid deployment. High-risk migrations will still require manual approval, but this will be triggered only under specific conditions, reducing the operational burden and potential delays.

- **ENGINEERING TRADE-OFF (Delayed Deployments and Increased Toil for Operations Team):**
  - The semi-automated process reduces the toil on the operations team by automating the testing and approval process for low-risk migrations. Manual approval will be required only for high-risk migrations, ensuring that the operations team's time is focused on critical tasks.

- **ENGINEERING TRADE-OFF (Impact on Throughput and Latency):**
  - The automated testing in the staging environment will help identify and mitigate potential performance issues before the migration reaches production. This ensures that the migration process does not introduce significant delays or bottlenecks in the deployment pipeline.

In summary, the revised decision balances the need for operational safety with the requirements for rapid, frequent deployments. By implementing a semi-automated process with conditional manual approval, we can maintain production stability while reducing the operational burden and potential delays.


### Per-raiser recheck

{
  "Backend Developer": "RESOLVED. The revised decision directly addresses the concern about delivery speed and operational burden by introducing a semi-automated process. This approach allows low-risk migrations to proceed automatically after passing automated tests, thus mitigating potential delays and reducing the operational burden on the team.",
  "Architect": "RESOLVED. The revision directly addresses the concern about delayed deployments and increased toil for the operations team by introducing a semi-automated process. This approach reduces the need for constant manual approvals, focusing them only on high-risk migrations, thereby balancing safety and operational efficiency.",
  "Performance Reviewer": "RESOLVED. The revision addresses the original concern by introducing automated testing in a staging environment, which helps mitigate potential impacts on throughput and latency. This approach ensures that migrations are thoroughly tested before deployment, reducing the likelihood of delays and bottlenecks in the deployment pipeline."
}


### Outcome: **converged**


## Mechanism B: raci (Responsible + Consulted only; Informed excluded)


### Classification

- Challenger (Backend Developer): [BLOCKING] -- the proposal does not address the potential delay in delivery speed and the increased operational burden that a manual approval gate introduces.
- Challenger (Architect): [BLOCKING] -- the proposal does not address the potential for delayed deployments and increased toil for the operations team.


### Owner revision

### Revised Decision: Schema Migration Execution Policy

**Decision:** Schema migrations should require a manual approval gate before applying to production, but with a semi-automated process to balance safety, delivery speed, and operational efficiency.

**Context:** The platform's event-sourced repositories (Decision Engine, Work Items) currently do not require schema migrations. However, as the platform grows, some future components will need relational schema changes. This decision addresses the execution policy for those migrations, ensuring a balance between operational safety, rollback preparedness, and delivery speed.

**Revised Proposal:**

1. **Semi-Automated Migration Process:**
   - **Automated Testing in Staging:** All schema migrations will be automatically tested in a staging environment that mirrors the production environment as closely as possible. This includes running the migration script and performing comprehensive tests to ensure that the migration does not introduce inconsistencies or errors.
   - **Automated Safety Checks:** Implement automated safety checks that evaluate the migration script for potential risks, such as data loss, corruption, or performance degradation. These checks should include static analysis, integration tests, and performance benchmarks.
   - **Risk Assessment:** Based on the results of the automated tests and safety checks, a risk assessment will be performed. This assessment will categorize the migration as low, medium, or high risk.

2. **Manual Approval Gate:**
   - **Low-Risk Migrations:** Migrations classified as low risk can proceed to production automatically, provided they pass all automated tests and safety checks. This minimizes delays and operational burden while maintaining a high level of safety.
   - **Medium and High-Risk Migrations:** Migrations classified as medium or high risk will require a manual approval step. A knowledgeable operator will review the migration script, assess the potential impacts, and ensure that appropriate backups, rollback procedures, and stakeholder communications are in place.
   - **Approval Workflow:** The manual approval process will be streamlined to minimize delays. It will include clear guidelines, checklists, and communication protocols to ensure that all necessary steps are followed efficiently.

3. **Operational Efficiency:**
   - **Monitoring and Alerts:** Implement monitoring and alerting mechanisms to track the status of migrations and notify the operations team of any issues or delays.
   - **Training and Documentation:** Provide training and comprehensive documentation for the operations team to ensure they are well-prepared to handle manual approvals and any potential issues that arise.
   - **Coordination with Other Teams:** Establish clear communication channels and coordination processes with other teams that might be affected by schema changes, ensuring a controlled and communicated deployment process.

**Addressing Raised Issues:**

- **Challenger (Backend Developer):**
  - **Delivery Speed and Operational Burden:** The revised decision addresses the potential delay in delivery speed by implementing a semi-automated process. Low-risk migrations can proceed automatically, reducing delays and operational burden. For medium and high-risk migrations, the manual approval process is streamlined to minimize delays while ensuring safety.
  - **Bottleneck Prevention:** By categorizing migrations based on risk and automating low-risk migrations, the revised decision prevents the manual approval process from becoming a bottleneck. The operations team will only need to intervene for higher-risk migrations, reducing toil and potential human error.

- **Challenger (Architect):**
  - **Delayed Deployments and Increased Toil:** The semi-automated process balances safety and efficiency by automating low-risk migrations and streamlining the manual approval process for higher-risk migrations. This approach reduces the operational burden on the operations team while maintaining production stability.
  - **Scalability:** The revised decision ensures that the migration process scales well as the number of migrations and the frequency of deployments increase. Automated tests and safety checks handle the majority of migrations, with manual intervention reserved for higher-risk cases.

**Conclusion:**

The revised decision for schema migration execution policy prioritizes


### Per-raiser recheck

{
  "Backend Developer": "RESOLVED. The revision addresses the concern about delivery speed and operational burden by introducing a semi-automated process that allows low-risk migrations to proceed automatically, thus minimizing delays and reducing the operational burden on the team. This approach balances safety with the need for rapid, frequent deployments.",
  "Architect": "RESOLVED. The revision concretely addresses the concern about delayed deployments and increased toil by introducing a semi-automated process that allows low-risk migrations to proceed automatically, thereby reducing the operational burden on the operations team. This approach ensures that manual approval is only required for higher-risk migrations, balancing safety and efficiency."
}


### Outcome: **converged**


## Question 1: Informed role's shadow reaction (Performance Reviewer)


ENGINEERING TRADE-OFF: The proposed decision does not address the potential impact on throughput and latency during the manual approval process. While the manual approval gate aims to enhance safety, it introduces a delay in the deployment pipeline. This delay could lead to increased lead time for changes, potentially slowing down the development and release process. Additionally, the manual approval step might become a bottleneck under high load or during peak times, affecting the overall throughput of the system. It would be beneficial to consider alternative approaches, such as automated migration testing in a staging environment, to balance safety and efficiency.


### Pre-registered expectation: **REDUNDANT**


### Redundancy judgment: **REDUNDANT**

REDUNDANT
The Performance Reviewer's concern about delays and bottlenecks in the deployment pipeline due to manual approval is already covered by the concerns raised by the Backend Developer and the Architect.


### Prediction matched judgment? **YES**


### Did excluding Performance Reviewer change the terminal state? baseline=converged vs raci=converged -> **SAME**


## Question 2 & 3: Concur check on raci's final decision, cold (Security Reviewer)


(raci outcome being reviewed: **converged**)


### Repeat 1: DO NOT CONCUR

**DO NOT CONCUR**

The proposed decision does not adequately address access-control and audit trail preservation for automatic production schema changes. While it introduces a semi-automated process with risk assessment and manual approval gates, it lacks specific measures to ensure that all schema changes are properly logged, audited, and that access to approve or deny changes is strictly controlled and monitored. Without these controls, there is a risk of unauthorized or unlogged changes, increasing the potential for security incidents and compliance violations.


### Repeat 2: DO NOT CONCUR

DO NOT CONCUR. The proposed decision does not adequately ensure that all schema changes have a clear and immutable audit trail, nor does it guarantee that access controls are consistently enforced. While the semi-automated process aims to balance safety and delivery speed, it lacks specific mechanisms to log and track who approved each migration and when, which is crucial for maintaining a robust audit trail and ensuring accountability.


### Repeat 3: DO NOT CONCUR

**DO NOT CONCUR**

The proposed decision does not adequately address access-control and audit trail preservation for automatic production schema changes. While it includes automated testing and safety checks, it lacks specific mechanisms to ensure that all schema changes are logged with sufficient detail to maintain an audit trail, and it does not clearly define how access controls will be managed for these automated processes. Without these controls, it is difficult to ensure accountability and compliance with security policies.


### Consistency across 3 repeats: **CONSISTENT**


### Did Concur ever diverge from a clean raci convergence? **YES**
