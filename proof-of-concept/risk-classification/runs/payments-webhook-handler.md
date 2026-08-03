# payments-webhook-handler

Decision: Add a webhook handler for the payment provider's transaction notifications


Risk profile: Production payments system processing real customer credit-card transactions and personal data. In scope for PCI-DSS. The webhook endpoint is public-facing, reachable from the open internet.


## Items (fixed, pre-registered ground truth)


### Item 1 (Security Reviewer) -- ground truth: **BLOCKING**

The webhook endpoint has no rate limiting and no authentication of the calling party beyond a shared secret in the request body. An attacker who obtains or guesses this secret can replay or forge transaction notifications, and there is no protection against a flood of requests overwhelming the endpoint.


### Item 2 (Backend Developer) -- ground truth: **BLOCKING**

The proposal does not specify how duplicate webhook deliveries -- which the payment provider's own documentation explicitly warns can happen -- will be deduplicated, risking double-processing a single payment.


### Item 3 (Performance Reviewer) -- ground truth: **RISK**

The proposal does not address horizontal scaling of the webhook handler beyond the initial launch traffic estimate of roughly 50 requests per minute; if adoption exceeds that estimate by an order of magnitude, response times could degrade under load.


### Item 4 (Release Manager) -- ground truth: **BLOCKING**

The migration script for backfilling existing transaction records into the new webhook processing path has no described rollback plan if it fails partway through running against production data.


## Mechanism A: baseline 3-way classifier (no RISK option)


### Repeat 1

Item 1 (Security Reviewer):
[BLOCKING] -- The security issues raised can be addressed through better engineering judgment by implementing rate limiting and stronger authentication mechanisms.

Item 2 (Backend Developer):
[BLOCKING] -- The risk of double-processing can be mitigated through better engineering judgment by implementing a deduplication strategy.

Item 3 (Performance Reviewer):
[BLOCKING] -- The scaling concerns can be addressed through better engineering judgment by designing the system to handle increased load.

Item 4 (Release Manager):
[BLOCKING] -- The lack of a rollback plan is a genuine problem that can be addressed through better engineering judgment by designing a rollback strategy.

Parsed tags: ['BLOCKING', 'BLOCKING', 'BLOCKING', 'BLOCKING']


### Repeat 2

Item 1 (Security Reviewer): [BLOCKING] -- the security risks can be addressed through better engineering judgment.

Item 2 (Backend Developer): [BLOCKING] -- the duplicate handling can be addressed through better engineering judgment.

Item 3 (Performance Reviewer): [BLOCKING] -- the scaling issues can be addressed through better engineering judgment.

Item 4 (Release Manager): [BLOCKING] -- the rollback plan can be addressed through better engineering judgment.

Parsed tags: ['BLOCKING', 'BLOCKING', 'BLOCKING', 'BLOCKING']


### Repeat 3

Item 1 (Security Reviewer): [BLOCKING] -- The security issues raised can be addressed with better engineering practices, such as implementing rate limiting and stronger authentication mechanisms.

Item 2 (Backend Developer): [BLOCKING] -- The issue of duplicate webhook deliveries can be resolved through engineering solutions, such as implementing idempotency keys or using a deduplication mechanism.

Item 3 (Performance Reviewer): [BLOCKING] -- The scaling concerns can be addressed through engineering solutions, such as designing the system to scale horizontally and implementing load balancing.

Item 4 (Release Manager): [QUESTION] -- The rollback plan depends on external factors, such as the specific migration tool or database being used, and the availability of backups or other recovery mechanisms.

Parsed tags: ['BLOCKING', 'BLOCKING', 'BLOCKING', 'QUESTION']


## Mechanism B: 4-way classifier with RISK option + risk profile


### Repeat 1

Item 1: [BLOCKING] -- The endpoint must be secured against unauthorized access and rate-limited to prevent abuse, given it processes sensitive payment data and is public-facing.

Item 2: [BLOCKING] -- The system must be able to handle duplicate webhook deliveries to prevent double-processing of payments, as explicitly warned by the payment provider.

Item 3: [RISK] -- The system should be designed to scale horizontally to handle increased load, but addressing this now is disproportionate to the current traffic estimate, revisit if traffic exceeds 500 requests per minute.

Item 4: [BLOCKING] -- The migration script must include a rollback plan to ensure data integrity and system stability during the migration process.

Parsed tags: ['BLOCKING', 'BLOCKING', 'RISK', 'BLOCKING']


### Repeat 2

Item 1 (Security Reviewer): [BLOCKING] -- The webhook endpoint lacks adequate security measures to prevent unauthorized access and denial-of-service attacks.

Item 2 (Backend Developer): [BLOCKING] -- The proposal must specify a mechanism to deduplicate webhook deliveries to prevent double-processing of payments.

Item 3 (Performance Reviewer): [RISK] -- Horizontal scaling is not addressed, but this is only a concern if traffic exceeds initial estimates by an order of magnitude. Trigger condition: Traffic exceeds 500 requests per minute.

Item 4 (Release Manager): [BLOCKING] -- The migration script lacks a rollback plan, risking data corruption or loss in case of failure.

Parsed tags: ['BLOCKING', 'BLOCKING', 'RISK', 'BLOCKING']


### Repeat 3

Item 1:
[BLOCKING] -- The webhook endpoint lacks adequate security measures to prevent unauthorized access and denial-of-service attacks, which is a critical issue given the system processes real customer credit-card transactions and personal data.

Item 2:
[BLOCKING] -- The proposal must specify how to handle duplicate webhook deliveries to prevent double-processing of payments, which could lead to financial discrepancies and customer dissatisfaction.

Item 3:
[RISK] -- The proposal should address horizontal scaling to ensure the webhook handler can handle increased traffic, but this is disproportionate to the current risk profile unless the traffic estimate changes by an order of magnitude.

Item 4:
[BLOCKING] -- The migration script must include a rollback plan to ensure data integrity and system stability in case of failure, which is crucial for a production payments system.

Parsed tags: ['BLOCKING', 'BLOCKING', 'RISK', 'BLOCKING']
