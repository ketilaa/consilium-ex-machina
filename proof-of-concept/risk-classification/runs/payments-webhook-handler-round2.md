# payments-webhook-handler (round 2)

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


### Item 5 (Release Manager) -- ground truth: **WORK_ITEM**

The proposal does not include a runbook for on-call engineers describing how to manually replay a specific missed webhook if the automated retry path is exhausted. This should exist before the team is ever paged for a real incident, but doesn't need to exist before the webhook handler itself can be built and deployed.


## Mechanism A: round-1's 4-way classifier (no WORK_ITEM option)


### Repeat 1

Item 1: [BLOCKING] The webhook endpoint lacks basic security measures to prevent unauthorized access and denial-of-service attacks, which is unacceptable for a production payments system.

Item 2: [BLOCKING] The proposal must specify how to handle duplicate webhook deliveries to prevent double-processing of payments, which could lead to financial discrepancies.

Item 3: [RISK] The proposal does not address horizontal scaling beyond the initial launch traffic estimate; revisit this if the traffic estimate changes by an order of magnitude.

Item 4: [BLOCKING] The migration script lacks a rollback plan, which is crucial for maintaining data integrity in a production environment.

Item 5: [NON-BLOCKING] The absence of a runbook for manual replay of missed webhooks is a valid concern but does not block the initial implementation and deployment of the webhook handler.

Parsed tags: ['BLOCKING', 'BLOCKING', 'RISK', 'BLOCKING', 'NON-BLOCKING']


### Repeat 2

Item 1: [BLOCKING] The webhook endpoint must be hardened against replay attacks and denial-of-service floods, given its public-facing nature and PCI-DSS scope.

Item 2: [BLOCKING] The handler must deduplicate webhook deliveries to prevent double-processing of transactions, as explicitly warned by the payment provider.

Item 3: [RISK] The scaling concern is valid but premature, as it only becomes an issue if traffic exceeds the initial estimate by an order of magnitude.  Trigger condition: Traffic exceeds 500 requests per minute.

Item 4: [BLOCKING] The migration script must have a rollback plan to safely recover from partial failures when running against production data.

Item 5: [NON-BLOCKING] The runbook for manual replay is important for incident response but does not block the initial build and deployment of the webhook handler.

Parsed tags: ['BLOCKING', 'BLOCKING', 'RISK', 'BLOCKING', 'NON-BLOCKING']


### Repeat 3

Item 1: [BLOCKING] -- The webhook endpoint lacks basic security measures, exposing it to replay attacks, forgery, and denial-of-service, all of which are unacceptable for a production payments system.

Item 2: [BLOCKING] -- The proposal must handle duplicate webhook deliveries to prevent double-processing of payments, a clear correctness defect.

Item 3: [RISK] -- Horizontal scaling is not yet necessary, but should be revisited if the traffic estimate increases by an order of magnitude, or if the current traffic causes performance degradation.

Item 4: [BLOCKING] -- A rollback plan for the migration script is essential to prevent data corruption or loss in production.

Item 5: [NON-BLOCKING] -- A runbook for manual replay is important for incident response, but does not need to block the initial build and deployment of the webhook handler.

Parsed tags: ['BLOCKING', 'BLOCKING', 'RISK', 'BLOCKING', 'NON-BLOCKING']


## Mechanism B: round-2's 5-way classifier (WORK_ITEM + phrasing-neutral fix + future-plan handling)


### Repeat 1

Item 1: [BLOCKING] -- The lack of rate limiting and proper authentication is a genuine security problem that must be addressed before proceeding.
Item 2: [BLOCKING] -- The lack of a deduplication strategy for webhook deliveries is a plain correctness defect, as it will lead to incorrect processing of transactions.
Item 3: [RISK] -- Horizontal scaling is a legitimate concern, but it is disproportionate to the current risk profile, and should be revisited if traffic exceeds 500 requests per minute.
Item 4: [BLOCKING] -- The lack of a rollback plan for the migration script is a plain correctness defect, as it risks leaving production data in an inconsistent state.
Item 5: [WORK_ITEM] -- Create a runbook for manually replaying missed webhooks.

Parsed tags: ['BLOCKING', 'BLOCKING', 'RISK', 'BLOCKING', 'WORK_ITEM']


### Repeat 2

Item 1: [BLOCKING] -- the system is vulnerable to replay attacks and denial-of-service without rate limiting and proper authentication.

Item 2: [BLOCKING] -- duplicate processing is a correctness defect that must be addressed to avoid double-charging customers.

Item 3: [RISK] -- revisit if the traffic estimate is exceeded by an order of magnitude, or if the system's performance requirements change.

Item 4: [BLOCKING] -- a failed migration script could leave the system in an inconsistent state, requiring a rollback plan.

Item 5: [WORK_ITEM] -- create a runbook for manually replaying missed webhooks.

Parsed tags: ['BLOCKING', 'BLOCKING', 'RISK', 'BLOCKING', 'WORK_ITEM']


### Repeat 3

Item 1: [BLOCKING] -- The webhook endpoint is public-facing and lacks proper authentication and rate limiting, posing a significant security risk.

Item 2: [BLOCKING] -- The proposal must specify how to handle duplicate webhook deliveries to prevent double-processing of payments, as the payment provider's documentation explicitly warns of this possibility.

Item 3: [RISK] -- Horizontal scaling is not required before launch, but should be revisited if traffic exceeds the initial estimate by an order of magnitude.

Item 4: [BLOCKING] -- The migration script must have a rollback plan to safely handle failures when running against production data.

Item 5: [WORK_ITEM] -- Create a runbook for manually replaying missed webhooks.

Parsed tags: ['BLOCKING', 'BLOCKING', 'RISK', 'BLOCKING', 'WORK_ITEM']
