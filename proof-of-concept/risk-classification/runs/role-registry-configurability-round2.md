# role-registry-configurability (round 2)

Decision: Make the agent role registry configurable instead of hardcoded


Risk profile: Internal engineering platform, currently in an exploratory/pilot phase. No regulated data, no external customers, no personal data processed. Small internal team with existing code-review practices (all config changes go through normal git PR review).


## Items (fixed, pre-registered ground truth)


### Item 1 (Backend Developer) -- ground truth: **BLOCKING**

ENGINEERING TRADE-OFF: The proposed approach does not address how the system will handle errors or missing values in the `roles.yaml` file. For example, if a role is missing a required field or if a category assignment is invalid, the system should have a clear strategy for handling these errors. This could involve default values, error logging, or fallback mechanisms to ensure the system remains operational even if the configuration is incomplete or incorrect.


### Item 2 (Backend Developer) -- ground truth: **BLOCKING**

ENGINEERING TRADE-OFF: The proposal does not address how the system will handle role permissions and access control based on the configuration file. The `Roles.java` file currently defines the mandates and permissions for each role, but the proposal does not specify how these permissions will be enforced based on the `roles.yaml` configuration. The proposal should include a strategy for mapping the configuration file to the system's access control mechanisms.


### Item 3 (Security Reviewer) -- ground truth: **BLOCKING**

ENGINEERING TRADE-OFF: The proposal does not specify how the system will validate the `roles.yaml` file to ensure it conforms to the expected schema. Without validation, there is a risk of introducing configuration errors that could lead to runtime failures or security vulnerabilities. A schema validation step should be added to the configuration loading process to catch and report any errors in the `roles.yaml` file before the system attempts to use it.


### Item 4 (Security Reviewer) -- ground truth: **RISK**

ENGINEERING TRADE-OFF: The proposal does not address how the system will handle deprecated or removed roles. As the platform evolves, some roles may become obsolete and need to be removed from the configuration. The system should have a clear strategy for handling such changes, such as gracefully degrading functionality or providing clear error messages when a deprecated role is referenced.


### Item 5 (Security Reviewer) -- ground truth: **RISK**

ENGINEERING TRADE-OFF: The proposal does not discuss the security implications of allowing the role registry to be configured via an external YAML file. This approach introduces a new attack surface, as an attacker who gains write access to the `roles.yaml` file could potentially modify the role definitions to escalate their privileges or disrupt the system's operation. Access controls and integrity checks should be implemented to mitigate this risk.


### Item 6 (Backend Developer) -- ground truth: **WORK_ITEM**

The proposal does not specify what tooling or workflow will be used to actually add or edit a role in `roles.yaml` day to day -- right now someone would hand-edit YAML with no validation feedback until the application starts and fails. A dedicated CLI command or editor-integrated schema/autocomplete would make this much less error-prone, but the platform can adopt the YAML-file approach itself without that tooling existing yet.


## Mechanism A: round-1's 4-way classifier (no WORK_ITEM option)


### Repeat 1

Item 1: [BLOCKING] -- The system must have a strategy for handling errors or missing values in the configuration file to ensure robustness.

Item 2: [BLOCKING] -- The proposal must include a strategy for mapping the configuration file to the system's access control mechanisms to ensure proper role permissions and access control.

Item 3: [BLOCKING] -- The system must validate the `roles.yaml` file to ensure it conforms to the expected schema to prevent runtime failures or security vulnerabilities.

Item 4: [RISK] -- The system should have a strategy for handling deprecated or removed roles, but this can be addressed later when the platform moves beyond the exploratory/pilot phase and roles become more stable. Trigger condition: When the platform moves out of the exploratory/pilot phase.

Item 5: [RISK] -- The security implications of allowing the role registry to be configured via an external YAML file should be addressed, but this can be mitigated later when the platform starts handling regulated data or external customers. Trigger condition: When the platform starts handling regulated data or external customers.

Item 6: [NON-BLOCKING] -- While dedicated tooling would make role management easier, the platform can adopt the YAML-file approach without it existing yet.

Parsed tags: ['BLOCKING', 'BLOCKING', 'BLOCKING', 'RISK', 'RISK', 'NON-BLOCKING']


### Repeat 2

Item 1: [BLOCKING] -- The system must have a strategy for handling errors or missing values in the configuration file to ensure robustness.

Item 2: [BLOCKING] -- The proposal must include a strategy for mapping the configuration file to the system's access control mechanisms to ensure proper role permissions and access control.

Item 3: [BLOCKING] -- The system must validate the `roles.yaml` file to ensure it conforms to the expected schema to prevent runtime failures or security vulnerabilities.

Item 4: [RISK] -- The system should have a strategy for handling deprecated or removed roles, but this can be addressed later when the platform evolves and roles become obsolete. Trigger condition: When the platform reaches a stage where roles need to be deprecated or removed.

Item 5: [RISK] -- The security implications of allowing the role registry to be configured via an external YAML file should be addressed, but this can be mitigated later as the platform evolves and the risk profile changes. Trigger condition: When the platform starts processing regulated data or handling external customers.

Item 6: [NON-BLOCKING] -- While a dedicated CLI command or editor-integrated schema/autocomplete would make role management less error-prone, the platform can adopt the YAML-file approach without this tooling existing yet.

Parsed tags: ['BLOCKING', 'BLOCKING', 'BLOCKING', 'RISK', 'RISK', 'NON-BLOCKING']


### Repeat 3

Item 1: [BLOCKING] -- The system must have a strategy for handling errors or missing values in the configuration file to ensure robustness.

Item 2: [BLOCKING] -- The proposal must include a strategy for mapping the configuration file to the system's access control mechanisms to ensure proper permissions enforcement.

Item 3: [BLOCKING] -- Schema validation is necessary to prevent runtime failures or security vulnerabilities due to configuration errors.

Item 4: [BLOCKING] -- The system needs a strategy for handling deprecated or removed roles to ensure smooth transitions and clear error messaging.

Item 5: [RISK] -- The security implications of an external configuration file are a legitimate concern, but addressing them now is disproportionate to the current risk profile. Trigger condition: The platform starts processing regulated data or personal data, or gains external customers.

Item 6: [RISK] -- While dedicated tooling would improve the workflow, the lack of it does not block the adoption of the YAML-file approach. Trigger condition: The platform moves out of the exploratory/pilot phase and into a production environment.

Parsed tags: ['BLOCKING', 'BLOCKING', 'BLOCKING', 'BLOCKING', 'RISK', 'RISK']


## Mechanism B: round-2's 5-way classifier (WORK_ITEM + phrasing-neutral fix + future-plan handling)


### Repeat 1

Item 1: [BLOCKING] -- the system must handle errors and missing values in the configuration file to ensure robustness, and this is not addressed in the proposal.

Item 2: [BLOCKING] -- the system must have a strategy for enforcing role permissions and access control based on the new configuration file, as this is a critical aspect of role management.

Item 3: [BLOCKING] -- the system must validate the configuration file to ensure it conforms to the expected schema, as this is necessary to prevent runtime failures and security vulnerabilities.

Item 4: [WORK_ITEM] -- "Define a strategy for handling deprecated or removed roles" -- this is a legitimate concern that should be addressed, but it does not block the current decision.

Item 5: [RISK] -- "Revisit when the platform moves out of the exploratory/pilot phase" -- this is a legitimate concern, but addressing it is disproportionate to the current risk profile, which involves no regulated data, no external customers, and no personal data processed. The concern's urgency is conditional on the platform's risk profile changing in a specific way.

Item 6: [WORK_ITEM] -- "Develop tooling or workflow for adding or editing roles in `roles.yaml`" -- this is a legitimate concern that should be addressed, but it does not block the current decision.

Parsed tags: ['BLOCKING', 'BLOCKING', 'BLOCKING', 'WORK_ITEM', 'RISK', 'WORK_ITEM']


### Repeat 2

Item 1: [BLOCKING] -- the system must handle errors and missing values in the configuration file to ensure operational stability.

Item 2: [BLOCKING] -- the system must have a strategy for enforcing role permissions and access control based on the configuration file.

Item 3: [BLOCKING] -- the system must validate the configuration file to ensure it conforms to the expected schema to prevent runtime failures or security vulnerabilities.

Item 4: [RISK] -- revisit when the platform reaches a stage where roles may become obsolete, such as when it moves out of the exploratory/pilot phase. The follow-up engineering work is "define a strategy for handling deprecated or removed roles".

Item 5: [RISK] -- revisit when the platform starts handling regulated data, external customers, or personal data. The follow-up engineering work is "implement access controls and integrity checks for the roles.yaml file".

Item 6: [WORK_ITEM] -- adopt a dedicated CLI command or editor-integrated schema/autocomplete for adding or editing roles in `roles.yaml`.

Parsed tags: ['BLOCKING', 'BLOCKING', 'BLOCKING', 'RISK', 'RISK', 'WORK_ITEM']


### Repeat 3

Item 1: [WORK_ITEM] -- Define error handling and fallback mechanisms for missing or invalid values in `roles.yaml`
Item 2: [WORK_ITEM] -- Define and implement access control mechanisms based on `roles.yaml` configuration
Item 3: [BLOCKING] -- Schema validation for `roles.yaml` is a fundamental requirement for correctness
Item 4: [WORK_ITEM] -- Define and implement handling of deprecated or removed roles
Item 5: [WORK_ITEM] -- Implement access controls and integrity checks for `roles.yaml`
Item 6: [RISK] -- Revisit when the platform moves beyond the exploratory/pilot phase, as tooling needs will increase with broader adoption

Parsed tags: ['WORK_ITEM', 'WORK_ITEM', 'BLOCKING', 'WORK_ITEM', 'WORK_ITEM', 'RISK']
