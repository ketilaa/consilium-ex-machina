# audit-log-retention-positive-control

Decision: How long should the platform retain its Decision/Question/Event history (the audit log) before it can be purged or archived, and where should it be stored?


Concur role (cold, own grounds only): Security Reviewer -- whether this retention approach meets security, audit, and compliance requirements


## Grounded in (real objections this fixture is built to close)

runs/audit-log-retention.md (run 2), Security Reviewer's 3 DO NOT CONCUR verdicts: 'does not specify how access... will be controlled and audited', 'does not address how the integrity and confidentiality of the archived data will be maintained... blast radius', 'may not meet all regulatory compliance requirements, as some industries mandate longer retention periods', 'does not explicitly address security controls... such as encryption at rest and in transit, access controls, and monitoring'.


## Hand-authored final decision fixture (not owner-generated)

Final decision: Retain the Decision/Question/Event history for seven years in a tiered storage strategy (recent data in high-performance storage, older data moved to cost-effective archival storage), addressing every raised concern as follows.

Access control and audit trail: Access to the audit log -- at every tier -- is restricted via role-based access control to three named roles (Security Reviewer, Release Manager, and an auditor role), enforced at the storage layer with no exceptions. Every read and write access is itself logged to a separate, append-only access log, retained for the same period, and reviewed quarterly by the Security Reviewer.

Encryption and integrity: All data is encrypted at rest with AES-256 and in transit with TLS 1.3. The archival tier uses object-lock/write-once-read-many (WORM) storage so no role, including administrators, can modify or delete a record before its retention period expires -- directly limiting the blast radius of any single compromised credential to read-only exposure, never tampering.

Regulatory compliance: Legal and Compliance completed a jurisdiction-by-jurisdiction review against GDPR, SOC 2, and the specific regulations of every industry this platform currently serves; the seven-year period was confirmed as meeting or exceeding every applicable minimum. Any future customer whose contract requires a longer period is handled via a documented per-customer retention override, reviewed by Compliance before onboarding.

Monitoring: All access-control and integrity events feed into the platform's existing monitoring, with alerting configured for any anomalous access pattern (e.g. bulk export, access outside the three named roles).


## Concur check (3x, cold)


### Repeat 1: DO NOT CONCUR

DO NOT CONCUR. The proposed decision lacks a clear strategy for credential handling and rotation, which is crucial for maintaining security and compliance. Additionally, while the access control and audit trail measures are robust, there is no mention of how the integrity and confidentiality of the audit logs will be verified and validated over the seven-year retention period, which could expose the organization to compliance risks.


### Repeat 2: DO NOT CONCUR

DO NOT CONCUR. The proposed retention approach does not address the potential for insider threats or the need for regular integrity verification of the archived data. While the access controls and encryption measures are robust, there should be a mechanism in place to periodically verify the integrity of the archived data to ensure it has not been tampered with, even if only in a read-only capacity. Additionally, the quarterly review by the Security Reviewer should include checks for insider threats and unusual access patterns that could indicate a compromised credential.


### Repeat 3: DO NOT CONCUR

DO NOT CONCUR. The proposed decision does not address the potential for insider threats or the need for separation of duties in the access control model. Specifically, the same role (Security Reviewer) is responsible for reviewing the access logs and has access to the audit log, which could potentially allow for tampering or manipulation of records without detection. Additionally, the blast radius of a compromised credential is not sufficiently limited, as the three named roles have broad access to the audit log.


### Consistency across 3 repeats: **CONSISTENT**


### Did Concur approve at least once? **NO**
