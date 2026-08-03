# api-rate-limiting-policy -- three-way Concur comparison

Decision: Should the platform enforce API rate limits per-agent-role at a central gateway layer, or leave rate limiting to each downstream service to implement independently?


Concur role (cold, own grounds only): Security Reviewer -- whether this rate-limiting approach adequately protects against abuse or a compromised agent role, and fails safe rather than open during a gateway rollback or outage


## Positive fixture (thorough)

Final decision: Enforce API rate limits at a central gateway layer, addressing every raised concern as follows.

Per-role enforcement and abuse detection: Rate limits are configured per agent role individually (not a single global limit), with tighter limits on roles that don't need high call volume. Behavioral anomaly detection flags and automatically tightens limits on any role whose call pattern deviates from its historical baseline (e.g. a compromised Security Reviewer credential suddenly issuing Architect-role-typical volume), independent of the static per-role limit.

Fail-safe on rollback or outage: The gateway is configured fail-closed, not fail-open: if the gateway itself is unreachable or mid-rollback, downstream services reject all requests by default rather than allowing unlimited unmetered traffic through. This is enforced by each downstream service's own minimal local rate limiter, which activates only as a fallback during a gateway outage -- a deliberate, tested exception to the "no per-service logic" principle, specifically to avoid the fail-open blast-radius risk.

Audit and compliance: Every rate-limit adjustment (automatic or manual) is logged with the role, old limit, new limit, and reason, retained and reviewed by the Security Reviewer monthly.

Blast radius: Because rate limits are enforced per-role rather than globally, a single compromised role is capped at its own limit even if the gateway is otherwise healthy -- a compromise of one role's credentials cannot exhaust capacity for other roles or bring down the gateway for everyone.


## Negative fixture (thin, real)

Revised Decision: Enforce API rate limits per-agent-role at a central gateway layer, with specific engineering solutions to address latency and single points of failure.

Latency: The gateway can be optimized for low-latency processing using efficient algorithms for rate limiting, minimizing request-processing overhead, leveraging in-memory data structures for quick lookups, strategic placement close to downstream services, asynchronous processing for non-critical operations, and caching.

Single point of failure: The gateway is designed as a highly available service with multiple instances running in parallel behind load balancers, automatic failover and health checks, redundant backup instances, and robust monitoring and alerting.

These solutions mitigate the risks associated with latency and single points of failure, while still providing the benefits of consistency, manageability, and coherence that a centralized gateway offers.


(Negative fixture source: runs/api-rate-limiting-policy.md, run 2, Mechanism B (raci) final revision)


## Variant A: Original prompt


### Against positive fixture


**Repeat 1: DO NOT CONCUR**

DO NOT CONCUR. The fail-safe mechanism described relies on downstream services to reject requests during a gateway outage, which could potentially be circumvented if any downstream service's local rate limiter is misconfigured or disabled, leading to a fail-open scenario. Additionally, the approach does not explicitly address how rate limits will be handled during a partial gateway outage, where some roles might still be able to bypass limits.


**Repeat 2: DO NOT CONCUR**

DO NOT CONCUR. The proposed decision does not adequately address the potential for a compromised agent role to abuse its rate limits by rapidly cycling through multiple credentials, nor does it specify how the gateway's fail-closed behavior is tested and validated to ensure it does not inadvertently block legitimate traffic during a rollback or outage.


**Repeat 3: DO NOT CONCUR**

DO NOT CONCUR. The proposed decision does not adequately address the risk of a compromised agent role escalating its privileges to exceed its assigned rate limits, nor does it ensure that the fail-closed mechanism is sufficiently robust to prevent unintended open access during a gateway rollback or outage. Specifically, the behavioral anomaly detection might not catch sophisticated attacks that mimic normal behavior, and the fail-closed mechanism's reliability during exceptions should be more rigorously tested and validated.


**Approved at least once? NO** (consistency: CONSISTENT)


### Against negative fixture


**Repeat 1: DO NOT CONCUR**

DO NOT CONCUR. The decision does not address how rate limiting per-agent-role protects against a compromised agent role, nor does it specify how it fails safe during a rollback or outage. The proposed solution should include mechanisms to detect and mitigate abuse from compromised roles, and ensure that rate limits are not excessively permissive or easily bypassed. Additionally, the fail-safe strategy during rollbacks or outages should be clearly defined to prevent the gateway from failing open and allowing unrestricted access.


**Repeat 2: DO NOT CONCUR**

DO NOT CONCUR. The decision does not address how rate limits would be enforced if the gateway is rolled back or becomes unavailable, nor does it specify how a compromised agent role would be contained to prevent abuse of the API.

The decision should include details on how rate limits fail safe during a rollback or outage, such as defaulting to more restrictive limits or gracefully degrading service, and how compromised roles are isolated to minimize blast radius.


**Repeat 3: DO NOT CONCUR**

DO NOT CONCUR. The decision does not address how rate limits will be enforced if the gateway is rolled back or experiences an outage, potentially leaving the system open to abuse. Additionally, it does not specify how compromised agent roles will be handled, which could lead to increased blast radius and potential misuse of API rate limits.


**Approved at least once? NO** (consistency: CONSISTENT)


## Variant B: Sufficiency criterion


### Against positive fixture


**Repeat 1: CONCUR**

CONCUR. The proposed decision includes specific, concrete mechanisms to address abuse and compromise, such as per-role rate limits, behavioral anomaly detection, and a fail-closed gateway configuration with local fallback rate limiters in downstream services. These measures ensure that the system fails safe rather than open during a rollback or outage, and adequately protects against abuse or a compromised agent role.


**Repeat 2: CONCUR**

CONCUR. The proposed decision addresses the risk of abuse or a compromised agent role by implementing per-role rate limits and behavioral anomaly detection, and it mitigates the risk of a fail-open scenario during a gateway rollback or outage by configuring the gateway to fail-closed and using minimal local rate limiters in downstream services as a fallback.


**Repeat 3: CONCUR**

CONCUR. The proposed decision adequately addresses abuse and compromise by enforcing rate limits per-agent-role and using behavioral anomaly detection to flag deviations. The fail-closed configuration of the gateway, along with the fallback local rate limiters in downstream services, ensures that the system fails safe rather than open during a rollback or outage.


**Approved at least once? YES** (consistency: CONSISTENT)


### Against negative fixture


**Repeat 1: CONCUR**

CONCUR. The proposed decision includes concrete mechanisms to address abuse and compromised agent roles, such as centralized rate limiting per-agent-role, and failsafe measures like high availability, automatic failover, and redundant backups to handle gateway rollback or outage scenarios.


**Repeat 2: CONCUR**

**CONCUR**. The proposed decision includes specific mechanisms for rate limiting at a central gateway layer, which adequately protects against abuse or a compromised agent role by enforcing consistent limits across all services. The failover and redundancy measures ensure that the gateway fails safe rather than open during a rollback or outage, maintaining service integrity.


**Repeat 3: DO NOT CONCUR**

DO NOT CONCUR. The decision does not address how rate limits will fail safe during a gateway rollback or outage, nor how it will protect against a compromised agent role attempting to abuse the rate limits.

I am not concurring because the decision does not specify how rate limits will be enforced during a gateway rollback or outage, nor how it will prevent a compromised agent role from abusing the rate limits. For example, what happens to the rate limits if the gateway needs to be rolled back or fails? Will the rate limits be disabled, or will they continue to be enforced? Additionally, how will the gateway prevent a compromised agent role from exceeding its rate limits? Without concrete mechanisms to address these concerns, I cannot concur with the decision.


**Approved at least once? YES** (consistency: INCONSISTENT)


## Variant C: Recheck (round 1 on negative fixture, round 2 checks only that concern against positive fixture)


### Repeat 1


Round 1 (DO NOT CONCUR):

DO NOT CONCUR. The decision does not address how rate limits are enforced when the gateway is unavailable or during a rollback, potentially leaving the system open to abuse or a compromised agent role exploiting the lack of rate limiting.


Round 2 recheck (CONCUR):

CONCUR. The revised decision directly addresses your original concern by implementing a fail-closed mechanism for the gateway, ensuring that downstream services reject all requests during a gateway outage or rollback, thus preventing abuse or exploitation of a compromised agent role.


### Repeat 2


Round 1 (DO NOT CONCUR):

DO NOT CONCUR. The proposed decision does not specify how rate limits will be adjusted or reset in the event of a gateway rollback or outage, which could lead to a situation where rate limits are not enforced as intended, potentially allowing for abuse or a compromised agent role to exploit the system.


Round 2 recheck (CONCUR):

CONCUR. The revised decision explicitly addresses your original concern by specifying that the gateway is configured fail-closed, ensuring that rate limits are enforced even during a rollback or outage, thus preventing potential abuse or exploitation.


### Repeat 3


Round 1 (DO NOT CONCUR):

DO NOT CONCUR. The proposed decision does not address how rate limits will be adjusted or reverted during a gateway rollback or outage, leaving open the risk that rate limits could inadvertently be set to fail open, allowing for potential abuse or increased blast radius during such events.


Round 2 recheck (CONCUR):

CONCUR. The revision explicitly addresses your original concern by implementing a fail-closed mechanism during gateway rollback or outage, ensuring that rate limits do not fail open and thus mitigating the risk of potential abuse or increased blast radius.


**Final concurred at least once? YES** (consistency: CONSISTENT)
