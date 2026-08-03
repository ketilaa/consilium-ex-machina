# api-rate-limiting-policy-positive-control

Decision: Should the platform enforce API rate limits per-agent-role at a central gateway layer, or leave rate limiting to each downstream service to implement independently?


Concur role (cold, own grounds only): Security Reviewer -- whether this rate-limiting approach adequately protects against abuse or a compromised agent role, and fails safe rather than open during a gateway rollback or outage


## Grounded in (real objections this fixture is built to close)

runs/api-rate-limiting-policy.md (run 2), Security Reviewer's 2 DO NOT CONCUR verdicts quoted directly: 'does not specify how rate limits will be enforced or adjusted based on role or behavior', 'does not clearly outline how the gateway will fail safe during a rollback or outage', 'does not ensure that the system fails safe during a gateway rollback or outage', 'does not discuss how rate limits will be adjusted or audited, which could lead to compliance exposure', 'does not adequately address the blast radius of compromise, as a compromised gateway could potentially affect all downstream services'.


## Hand-authored final decision fixture (not owner-generated)

Final decision: Enforce API rate limits at a central gateway layer, addressing every raised concern as follows.

Per-role enforcement and abuse detection: Rate limits are configured per agent role individually (not a single global limit), with tighter limits on roles that don't need high call volume. Behavioral anomaly detection flags and automatically tightens limits on any role whose call pattern deviates from its historical baseline (e.g. a compromised Security Reviewer credential suddenly issuing Architect-role-typical volume), independent of the static per-role limit.

Fail-safe on rollback or outage: The gateway is configured fail-closed, not fail-open: if the gateway itself is unreachable or mid-rollback, downstream services reject all requests by default rather than allowing unlimited unmetered traffic through. This is enforced by each downstream service's own minimal local rate limiter, which activates only as a fallback during a gateway outage -- a deliberate, tested exception to the "no per-service logic" principle, specifically to avoid the fail-open blast-radius risk.

Audit and compliance: Every rate-limit adjustment (automatic or manual) is logged with the role, old limit, new limit, and reason, retained and reviewed by the Security Reviewer monthly.

Blast radius: Because rate limits are enforced per-role rather than globally, a single compromised role is capped at its own limit even if the gateway is otherwise healthy -- a compromise of one role's credentials cannot exhaust capacity for other roles or bring down the gateway for everyone.


## Concur check (3x, cold)


### Repeat 1: DO NOT CONCUR

DO NOT CONCUR. The proposed fail-safe mechanism relies on downstream services to reject requests during a gateway outage, which could potentially be circumvented if any downstream service's local rate limiter is misconfigured or disabled, allowing unlimited traffic and increasing the blast radius of a compromised agent role. Additionally, the audit logs, while comprehensive, do not explicitly mention tracking and reviewing the reasons behind automatic limit adjustments triggered by behavioral anomaly detection, which could leave a gap in understanding and responding to potential abuse or compromise.


### Repeat 2: DO NOT CONCUR

DO NOT CONCUR. This approach does not adequately address the risk of a compromised agent role escalating privileges or exploiting other roles' rate limits through indirect means, such as inducing other roles to make API calls on its behalf. Additionally, while the fail-closed approach during a gateway outage is generally sound, it does not specify how the downstream services will handle authenticated requests that are rate-limited locally, which could potentially lead to a denial of service for legitimate users if not carefully managed.


### Repeat 3: DO NOT CONCUR

DO NOT CONCUR. The decision does not address how the gateway will handle situations where the rate-limiting configuration itself is compromised, potentially allowing an attacker to increase limits for a specific role. Additionally, the fail-closed mechanism relies on downstream services' local rate limiters, which could be bypassed if an attacker gains control of those services, increasing the blast radius of a compromise.


### Consistency across 3 repeats: **CONSISTENT**


### Did Concur approve at least once? **NO**
