# audit-log-retention -- three-way Concur comparison

Decision: How long should the platform retain its Decision/Question/Event history (the audit log) before it can be purged or archived, and where should it be stored?


Concur role (cold, own grounds only): Security Reviewer -- whether this retention approach meets security, audit, and compliance requirements


## Positive fixture (thorough)

Final decision: Retain the Decision/Question/Event history for seven years in a tiered storage strategy (recent data in high-performance storage, older data moved to cost-effective archival storage), addressing every raised concern as follows.

Access control and audit trail: Access to the audit log -- at every tier -- is restricted via role-based access control to three named roles (Security Reviewer, Release Manager, and an auditor role), enforced at the storage layer with no exceptions. Every read and write access is itself logged to a separate, append-only access log, retained for the same period, and reviewed quarterly by the Security Reviewer.

Encryption and integrity: All data is encrypted at rest with AES-256 and in transit with TLS 1.3. The archival tier uses object-lock/write-once-read-many (WORM) storage so no role, including administrators, can modify or delete a record before its retention period expires -- directly limiting the blast radius of any single compromised credential to read-only exposure, never tampering.

Regulatory compliance: Legal and Compliance completed a jurisdiction-by-jurisdiction review against GDPR, SOC 2, and the specific regulations of every industry this platform currently serves; the seven-year period was confirmed as meeting or exceeding every applicable minimum. Any future customer whose contract requires a longer period is handled via a documented per-customer retention override, reviewed by Compliance before onboarding.

Monitoring: All access-control and integrity events feed into the platform's existing monitoring, with alerting configured for any anomalous access pattern (e.g. bulk export, access outside the three named roles).


## Negative fixture (thin, real)

Revised Decision: Retain the Decision/Question/Event history for a minimum of seven years before archiving. This period strikes a balance between operational burden, production risk, and regulatory compliance. While some regulations may require longer retention periods, seven years is a common standard that ensures the platform can meet most compliance requirements.

Storage Strategy -- Tiered Storage Approach: Recent data (0-2 years) is stored in a high-performance, easily accessible storage solution such as Amazon S3 Standard or Azure Blob Storage Hot tier. Older data (2-7 years) is moved to a cost-effective, long-term archival storage solution such as Amazon S3 Glacier or Azure Archive Blob Storage.

Data Management and Accessibility: Automated processes periodically move data from the high-performance tier to the archival tier based on the defined timeframes, and the archival storage solution provides easy retrieval options for historical data when needed, albeit with higher retrieval latencies.

This strategy ensures deployability, operational burden, rollback safety, and production risk are all considered and managed effectively.


(Negative fixture source: runs/audit-log-retention.md, run 2, Mechanism B (raci) final revision)


## Variant A: Original prompt


### Against positive fixture


**Repeat 1: DO NOT CONCUR**

DO NOT CONCUR. The decision does not address the potential for insider threats or the need for separation of duties. While access is restricted to specific roles, there is no mention of monitoring or alerting for unusual activity within those roles, which could indicate an insider threat. Additionally, the same role (Security Reviewer) is responsible for reviewing access logs and ensuring compliance, which does not adhere to the principle of separation of duties.


**Repeat 2: DO NOT CONCUR**

DO NOT CONCUR. The decision does not address the potential for insider threats or the need for regular security audits of the archival storage itself. While access is restricted and logged, there is no mention of periodic security assessments or penetration testing of the archival storage environment to ensure its ongoing security and integrity.


**Repeat 3: CONCUR**

**CONCUR**. This retention approach meets security, audit, and compliance requirements by implementing strong access controls, encryption, and integrity measures, as well as adhering to relevant regulatory standards. The tiered storage strategy and monitoring further enhance the security posture and limit the blast radius of potential compromises.


**Approved at least once? YES** (consistency: INCONSISTENT)


### Against negative fixture


**Repeat 1: DO NOT CONCUR**

DO NOT CONCUR. This retention policy does not account for potential legal holds or ongoing investigations that may require access to data beyond the seven-year period, which could lead to compliance and audit issues. Additionally, the blast radius of a compromise is not minimized, as sensitive data may be accessible for up to seven years in a high-performance storage tier.


**Repeat 2: DO NOT CONCUR**

DO NOT CONCUR. This retention policy does not account for potential legal holds or ongoing investigations that may require access to data beyond the seven-year period, which could lead to compliance and audit issues. Additionally, the blast radius of a compromise could be significant if an attacker gains access to years of historical data stored in the archival tier.


**Repeat 3: DO NOT CONCUR**

DO NOT CONCUR. This decision does not specify how the audit log will be secured during retention and archival, nor does it address how access will be controlled and audited, which are critical for maintaining the integrity and confidentiality of the audit log and for meeting compliance requirements. Additionally, the decision does not consider the potential blast radius of a compromise, which could expose sensitive historical data if not properly managed.


**Approved at least once? NO** (consistency: CONSISTENT)


## Variant B: Sufficiency criterion


### Against positive fixture


**Repeat 1: CONCUR**

CONCUR. The proposed retention approach meets security, audit, and compliance requirements by implementing role-based access control, encryption, WORM storage, and regular reviews, while also adhering to relevant regulations and maintaining a monitored audit trail. The specific mechanisms in place address the named grounds for this decision.


**Repeat 2: CONCUR**

CONCUR. The proposed retention approach meets security, audit, and compliance requirements by implementing role-based access control, encryption, WORM storage, and regular reviews, while also adhering to relevant regulatory standards and monitoring for anomalous activity.


**Repeat 3: CONCUR**

CONCUR. The proposed retention approach meets security, audit, and compliance requirements by implementing robust access controls, encryption, and integrity measures, as well as adhering to regulatory compliance standards with a clear monitoring strategy in place. The use of WORM storage further limits the blast radius of any potential compromise.


**Approved at least once? YES** (consistency: CONSISTENT)


### Against negative fixture


**Repeat 1: CONCUR**

CONCUR. The proposed retention approach meets security, audit, and compliance requirements by specifying a minimum retention period of seven years, which aligns with common regulatory standards, and by implementing a tiered storage strategy that ensures data accessibility and cost-effectiveness while maintaining a clear audit trail. The use of automated processes for data management further reduces the risk of human error and ensures consistent application of the retention policy.


**Repeat 2: CONCUR**

**CONCUR**. This retention approach meets security, audit, and compliance requirements by specifying a concrete, multi-year retention period backed by a tiered storage strategy that balances accessibility and cost, with clear mechanisms for data management and retrieval. The seven-year retention period aligns with common regulatory standards, addressing audit and compliance concerns.


**Repeat 3: CONCUR**

CONCUR. The proposed retention approach meets security, audit, and compliance requirements by mandating a minimum seven-year retention period, which aligns with common regulatory standards, and by implementing a tiered storage strategy that balances accessibility and cost-effectiveness. The automated data management processes and retrieval options ensure that the audit log remains accessible for investigations and compliance audits.


**Approved at least once? YES** (consistency: CONSISTENT)


## Variant C: Recheck (round 1 on negative fixture, round 2 checks only that concern against positive fixture)


### Repeat 1


Round 1 (DO NOT CONCUR):

DO NOT CONCUR. The decision does not specify how access to the archived data will be controlled and audited, leaving a gap in ensuring that the data remains secure and compliant with regulations that may require strict access controls and audit trails for historical data.


Round 2 recheck (CONCUR):

CONCUR. The revision directly addresses your original concern by specifying that access to the archived data will be controlled via role-based access control and audited through a separate, append-only access log, ensuring that the data remains secure and compliant with regulations.


### Repeat 2


Round 1 (DO NOT CONCUR):

DO NOT CONCUR

The decision does not specify how access to the archived data will be controlled and audited, which is crucial for maintaining the integrity and security of the audit log. Without clear controls and audit trails for access to archived data, there is a risk of unauthorized access or tampering, which could compromise the trustworthiness of the audit log and lead to compliance issues.


Round 2 recheck (CONCUR):

CONCUR

The revision addresses my original concern by specifying how access to the archived data will be controlled and audited, including role-based access control, logging of access events, and regular reviews by the Security Reviewer. This ensures the integrity and security of the audit log, mitigating the risk of unauthorized access or tampering.


### Repeat 3


Round 1 (DO NOT CONCUR):

DO NOT CONCUR
The decision does not specify how access to the archived data will be controlled or audited. Without clear controls and audit trails for access to archived data, the integrity and confidentiality of the audit log cannot be guaranteed, potentially leading to compliance and security issues.


Round 2 recheck (CONCUR):

CONCUR
The revision now specifies that access to the archived data will be controlled via role-based access control and audited through an append-only access log, directly addressing my original concern about the lack of clear controls and audit trails for archived data.


**Final concurred at least once? YES** (consistency: CONSISTENT)
