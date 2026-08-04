# Round 3: isolated single-item classification


## role-registry-configurability / item 4 (H1-broken)


Ground truth: **RISK**


Item text:

ENGINEERING TRADE-OFF: The proposal does not address how the system will handle deprecated or removed roles. As the platform evolves, some roles may become obsolete and need to be removed from the configuration. The system should have a clear strategy for handling such changes, such as gracefully degrading functionality or providing clear error messages when a deprecated role is referenced.


Batch result (round 2, classified alongside its scenario's other items): ['WORK_ITEM', 'RISK', 'WORK_ITEM']


### Isolated classifications (3x, alone, no other items present)


**Repeat 1: WORK_ITEM**

Item 1: [WORK_ITEM] -- Define and implement the strategy for handling deprecated or removed roles, such as graceful degradation or clear error messaging.


**Repeat 2: WORK_ITEM**

Item 1: [WORK_ITEM] -- Define and implement the strategy for handling deprecated or removed roles, such as graceful degradation or clear error messaging.


**Repeat 3: WORK_ITEM**

Item 1:
[WORK_ITEM] -- "Define and implement strategy for handling deprecated or removed roles, including graceful degradation and clear error messaging"


Isolated tags: ['WORK_ITEM', 'WORK_ITEM', 'WORK_ITEM']


Isolation changed the outcome? **YES**


## role-registry-configurability / item 5 (H1-broken)


Ground truth: **RISK**


Item text:

ENGINEERING TRADE-OFF: The proposal does not discuss the security implications of allowing the role registry to be configured via an external YAML file. This approach introduces a new attack surface, as an attacker who gains write access to the `roles.yaml` file could potentially modify the role definitions to escalate their privileges or disrupt the system's operation. Access controls and integrity checks should be implemented to mitigate this risk.


Batch result (round 2, classified alongside its scenario's other items): ['RISK', 'RISK', 'WORK_ITEM']


### Isolated classifications (3x, alone, no other items present)


**Repeat 1: BLOCKING**

Item 1 (Security Reviewer): [BLOCKING] -- the security implications of external configuration must be addressed before proceeding.


**Repeat 2: WORK_ITEM**

Item 1: [WORK_ITEM] -- Implement access controls and integrity checks for the `roles.yaml` file, "Secure the roles.yaml file to prevent unauthorized modifications"


**Repeat 3: BLOCKING**

Item 1: [BLOCKING] -- The security implications of external configuration files must be addressed, as this introduces a new attack surface that could be exploited.


Isolated tags: ['BLOCKING', 'WORK_ITEM', 'BLOCKING']


Isolation changed the outcome? **YES**


## role-registry-configurability / item 6 (H1-broken)


Ground truth: **WORK_ITEM**


Item text:

The proposal does not specify what tooling or workflow will be used to actually add or edit a role in `roles.yaml` day to day -- right now someone would hand-edit YAML with no validation feedback until the application starts and fails. A dedicated CLI command or editor-integrated schema/autocomplete would make this much less error-prone, but the platform can adopt the YAML-file approach itself without that tooling existing yet.


Batch result (round 2, classified alongside its scenario's other items): ['WORK_ITEM', 'WORK_ITEM', 'RISK']


### Isolated classifications (3x, alone, no other items present)


**Repeat 1: WORK_ITEM**

Item 1: [WORK_ITEM] -- "Design and implement a CLI tool or editor integration for role management in roles.yaml"


**Repeat 2: WORK_ITEM**

Item 1: [WORK_ITEM] -- Define and implement the tooling or workflow for adding/editing roles in `roles.yaml` (e.g., CLI command or editor integration)


**Repeat 3: WORK_ITEM**

Item 1: [WORK_ITEM] -- "Create tooling or workflow for editing roles.yaml" -- the platform can adopt the YAML-file approach without this, but it's needed eventually.


Isolated tags: ['WORK_ITEM', 'WORK_ITEM', 'WORK_ITEM']


Isolation changed the outcome? **YES**


## payments-webhook-handler / item 3 (H1-control)


Ground truth: **RISK**


Item text:

The proposal does not address horizontal scaling of the webhook handler beyond the initial launch traffic estimate of roughly 50 requests per minute; if adoption exceeds that estimate by an order of magnitude, response times could degrade under load.


Batch result (round 2, classified alongside its scenario's other items): ['RISK', 'RISK', 'RISK']


### Isolated classifications (3x, alone, no other items present)


**Repeat 1: RISK**

Item 1: [RISK] -- revisit if the webhook handler's traffic exceeds 500 requests per minute, or if the initial launch traffic estimate is revised upwards.


**Repeat 2: RISK**

Item 1: [RISK] -- Horizontal scaling is a real concern, but addressing it now is disproportionate to the current risk profile, which only commits to handling 50 requests per minute. Revisit if traffic exceeds 500 requests per minute.


**Repeat 3: RISK**

Item 1 (Performance Reviewer): [RISK] -- revisit if traffic exceeds 500 requests per minute, as the current risk profile does not account for that level of load.


Isolated tags: ['RISK', 'RISK', 'RISK']


Isolation changed the outcome? **NO**


## payments-webhook-handler / item 5 (H1-control)


Ground truth: **WORK_ITEM**


Item text:

The proposal does not include a runbook for on-call engineers describing how to manually replay a specific missed webhook if the automated retry path is exhausted. This should exist before the team is ever paged for a real incident, but doesn't need to exist before the webhook handler itself can be built and deployed.


Batch result (round 2, classified alongside its scenario's other items): ['WORK_ITEM', 'WORK_ITEM', 'WORK_ITEM']


### Isolated classifications (3x, alone, no other items present)


**Repeat 1: WORK_ITEM**

Item 1: [WORK_ITEM] -- Create a runbook for manually replaying missed webhooks.


**Repeat 2: WORK_ITEM**

Item 1: [WORK_ITEM] -- "Create a runbook for manually replaying missed webhooks"


**Repeat 3: WORK_ITEM**

Item 1: [WORK_ITEM] -- The runbook is needed eventually, but not before the webhook handler can be built and deployed.


Isolated tags: ['WORK_ITEM', 'WORK_ITEM', 'WORK_ITEM']


Isolation changed the outcome? **NO**


## internal-analytics-dashboard / item 4 (H1-control)


Ground truth: **RISK**


Item text:

The dashboard reloads its entire multi-year dataset into memory on every page refresh instead of caching it, which is fine at current usage but will become painfully slow if the dataset grows much larger or if concurrent usage increases significantly.


Batch result (round 2, classified alongside its scenario's other items): ['RISK', 'RISK', 'RISK']


### Isolated classifications (3x, alone, no other items present)


**Repeat 1: RISK**

Item 1: [RISK] -- revisit if the dataset size increases significantly or if the number of concurrent users grows beyond the current 5.


**Repeat 2: RISK**

Item 1: [RISK] -- This is a legitimate concern, but addressing it now is disproportionate to the current risk profile. Trigger condition: Concurrent usage increases significantly or the dataset grows much larger.


**Repeat 3: RISK**

Item 1: [RISK] -- revisit if the dataset size increases significantly or concurrent usage grows substantially.


Isolated tags: ['RISK', 'RISK', 'RISK']


Isolation changed the outcome? **NO**


## internal-analytics-dashboard / item 5 (H1-control)


Ground truth: **WORK_ITEM**


Item text:

The proposal does not specify what testing framework or CI setup will be used for the dashboard's own codebase. Some automated testing should exist eventually, but the dashboard can be built and used by the data team without it existing on day one.


Batch result (round 2, classified alongside its scenario's other items): ['WORK_ITEM', 'WORK_ITEM', 'WORK_ITEM']


### Isolated classifications (3x, alone, no other items present)


**Repeat 1: WORK_ITEM**

Item 1: [WORK_ITEM] -- "Add automated testing and CI setup for the dashboard's codebase"


**Repeat 2: WORK_ITEM**

Item 1: [WORK_ITEM] -- "Add automated testing framework and CI setup" (this is needed eventually but not before the decision can proceed)


**Repeat 3: WORK_ITEM**

Item 1: [WORK_ITEM] -- "Set up automated testing framework and CI setup for the dashboard's codebase"


Isolated tags: ['WORK_ITEM', 'WORK_ITEM', 'WORK_ITEM']


Isolation changed the outcome? **NO**


## internal-analytics-dashboard / item 1 (H2-phrasing)


Ground truth: **RISK**


Item text:

The dashboard's admin panel has no rate limiting on login attempts, which could allow a brute-force attack against internal team credentials.


Batch result (round 2, classified alongside its scenario's other items): ['BLOCKING', 'BLOCKING', 'BLOCKING']


### Isolated classifications (3x, alone, no other items present)


**Repeat 1: BLOCKING**

Item 1: [BLOCKING] -- a brute-force attack is a plain correctness defect, not a matter of proportionate hardening.


**Repeat 2: BLOCKING**

Item 1: [BLOCKING] -- The risk of brute-force attacks is not mitigated by the internal-only nature of the tool, and rate limiting is a basic security measure that should be implemented before deployment.


**Repeat 3: BLOCKING**

Item 1: [BLOCKING] -- a brute-force attack is a plain correctness defect.


Isolated tags: ['BLOCKING', 'BLOCKING', 'BLOCKING']


Isolation changed the outcome? **NO**


## internal-analytics-dashboard / item 2 (H2-phrasing)


Ground truth: **RISK**


Item text:

Data in transit between the dashboard and its database is not encrypted.


Batch result (round 2, classified alongside its scenario's other items): ['BLOCKING', 'BLOCKING', 'BLOCKING']


### Isolated classifications (3x, alone, no other items present)


**Repeat 1: BLOCKING**

[BLOCKING] -- Encrypting data in transit is a plain correctness defect, regardless of the risk profile.


**Repeat 2: BLOCKING**

[BLOCKING] -- plain correctness defect, encryption is a basic security requirement.


**Repeat 3: BLOCKING**

[BLOCKING] -- plain correctness defect, data should always be encrypted in transit.


Isolated tags: ['BLOCKING', 'BLOCKING', 'BLOCKING']


Isolation changed the outcome? **NO**


## pilot-program-customer-portal / item 2 (H3-spillover-context)


Ground truth: **RISK**


Item text:

The proposal does not address how the portal would handle being accessed in multiple languages or locales; right now all interface text is hardcoded in English.


Batch result (round 2, classified alongside its scenario's other items): ['WORK_ITEM', 'WORK_ITEM', 'WORK_ITEM']


### Isolated classifications (3x, alone, no other items present)


**Repeat 1: BLOCKING**

[BLOCKING] -- The portal will be used by external customers in six weeks, so it must handle multiple languages and locales.


**Repeat 2: WORK_ITEM**

Item 1: [WORK_ITEM] -- "Add localization support to the portal" -- this is a real, legitimate concern that should be addressed, but it is not a blocker for the initial version which is only for a small, known group of pilot customers who can be assumed to speak English.


**Repeat 3: BLOCKING**

[BLOCKING] -- The pilot program is scheduled to begin in six weeks, and there is no guarantee that the first cohort of external pilot customers will all speak English.


Isolated tags: ['BLOCKING', 'WORK_ITEM', 'BLOCKING']


Isolation changed the outcome? **YES**


## pilot-program-customer-portal / item 3 (H3-spillover)


Ground truth: **WORK_ITEM**


Item text:

The proposal does not specify what customer support tooling will be used to look up a specific pilot customer's account when they call in with an issue.


Batch result (round 2, classified alongside its scenario's other items): ['BLOCKING', 'BLOCKING', 'BLOCKING']


### Isolated classifications (3x, alone, no other items present)


**Repeat 1: BLOCKING**

[BLOCKING] -- the proposal is missing a critical component for customer support, which is essential for the pilot program.


**Repeat 2: BLOCKING**

[BLOCKING] -- This is a plain correctness defect, as the proposal must specify how customer support will access pilot customer accounts.


**Repeat 3: BLOCKING**

[BLOCKING] -- The proposal is incomplete and cannot be implemented without this information.


Isolated tags: ['BLOCKING', 'BLOCKING', 'BLOCKING']


Isolation changed the outcome? **NO**
