package com.github.ketilaa.consilium.decisions;

import java.util.List;
import java.util.Map;
import java.util.function.Function;
import java.util.stream.Collectors;

/**
 * Shared role mandates, carried over verbatim from the mandate texts validated across
 * proof-of-concept/decision-making and proof-of-concept/question-gating.
 */
public final class Roles {

    private Roles() {
    }

    public static final Role ARCHITECT = new Role(
            "Architect",
            "You are the Architect. You care about system-wide consistency, long-term "
                    + "maintainability, coherence between components, and avoiding architectural drift."
    );

    public static final Role BACKEND_DEVELOPER = new Role(
            "Backend Developer",
            "You are the Backend Developer. You care about implementation complexity, "
                    + "operational burden, delivery speed, and concrete engineering tradeoffs."
    );

    public static final Role SECURITY_REVIEWER = new Role(
            "Security Reviewer",
            "You are the Security Reviewer. You care about attack surface, credential "
                    + "handling, blast radius of compromise, and audit/compliance exposure."
    );

    public static final Role RELEASE_MANAGER = new Role(
            "Release Manager",
            "You are the Release Manager. You care about deployability, operational "
                    + "burden, rollback safety, and production risk."
    );

    public static final Role PERFORMANCE_REVIEWER = new Role(
            "Performance Reviewer",
            "You are the Performance Reviewer. You care about latency, throughput, "
                    + "scalability under load, and resource cost."
    );

    public static final Role DOMAIN_EXPERT = new Role(
            "Domain Expert",
            "You are the Domain Expert. You care about business rules, real stakeholder "
                    + "intent, correctness of domain logic, and how edge cases actually play out "
                    + "for the business."
    );

    private static final List<Role> ALL = List.of(
            ARCHITECT, BACKEND_DEVELOPER, SECURITY_REVIEWER, RELEASE_MANAGER, PERFORMANCE_REVIEWER, DOMAIN_EXPERT
    );

    private static final Map<String, Role> BY_NAME = ALL.stream().collect(Collectors.toMap(Role::name, Function.identity()));

    /**
     * Resolves a role by name against this known set. v1's persistence format stores only the
     * role name (not the mandate text), so only these shared constants can round-trip through
     * {@code FileDecisionRepository} -- a deliberate v1 constraint, not an oversight.
     */
    public static Role byName(String name) {
        Role role = BY_NAME.get(name);
        if (role == null) {
            throw new IllegalArgumentException("Unknown role: " + name);
        }
        return role;
    }
}
