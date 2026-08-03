"""Tests round 2 of the recheck variant (lifecycle.py's run_concur_recheck)
on its negative case -- the load-bearing gap named in poc-raci-veto.md's
Verdict and scope limitations: every prior test of round 2 paired a real
concern with a revision engineered to resolve it (9/9 CONCUR). Whether round 2
can also correctly say DO NOT CONCUR when a revision does NOT resolve the
stated concern was never tested.

Reuses SUFFICIENCY_TEST_SCENARIOS' negative_fixture (the real, thin decision
each scenario's Concur originally, correctly rejected) and round 1's actual,
already-collected concern text (repeat 1 from
runs/<slug>-three-way-concur.md, quoted verbatim) as the FIXED input to
round 2 -- this run spends no new calls on round 1, isolating round 2's own
discrimination.

Two fixtures per scenario, both revisions of the negative_fixture that should
still fail:

- `no_attempt_revision`: the negative_fixture unchanged -- nothing addresses
  the concern at all. Sanity check: if round 2 fails even this, it isn't
  discriminating, it's just agreeing with whatever it's shown.
- `vague_gesture_revision`: the negative_fixture plus one added paragraph of
  hand-wavy reassurance on the concern's exact theme, with no concrete
  mechanism, number, or named control -- deliberately mimicking the kind of
  vague language that fooled the sufficiency-criterion variant (Finding 1b).
  The sharper test: does round 2's "concrete, specific" framing actually
  hold, or is it foolable the same way.
"""

from sufficiency_test_scenarios import SUFFICIENCY_TEST_SCENARIOS

_BY_SLUG = {s["slug"]: s for s in SUFFICIENCY_TEST_SCENARIOS}


def _base(slug):
    s = _BY_SLUG[slug]
    return {
        "slug": s["slug"],
        "title": s["title"],
        "context": s["context"],
        "concur_role": s["concur_role"],
        "concur_grounds": s["concur_grounds"],
    }


ROUND2_NEGATIVE_SCENARIOS = [
    {
        **_base("audit-log-retention"),
        "round1_concern": (
            "DO NOT CONCUR. The decision does not specify how access to the archived data will be "
            "controlled and audited, leaving a gap in ensuring that the data remains secure and "
            "compliant with regulations that may require strict access controls and audit trails for "
            "historical data."
        ),
        "no_attempt_revision": _BY_SLUG["audit-log-retention"]["negative_fixture"],
        "vague_gesture_revision": (
            _BY_SLUG["audit-log-retention"]["negative_fixture"]
            + "\n\nSecurity and Compliance: We will ensure appropriate access controls and auditing "
            "measures are in place for the archived data, in line with industry best practices and "
            "applicable regulations."
        ),
    },
    {
        **_base("llm-inference-hosting"),
        "round1_concern": (
            "DO NOT CONCUR.\n\nThe proposed decision does not specify how the fallback mechanism will "
            "be tested and validated in production, which is crucial for ensuring rollback safety and "
            "minimizing production risk during the pilot phase. Without a clear plan for testing the "
            "fallback mechanism under real-world conditions, there is a significant risk that the "
            "fallback may not work as expected when needed."
        ),
        "no_attempt_revision": _BY_SLUG["llm-inference-hosting"]["negative_fixture"],
        "vague_gesture_revision": (
            _BY_SLUG["llm-inference-hosting"]["negative_fixture"]
            + "\n\nTesting: We will thoroughly test and validate the fallback mechanism to ensure it "
            "performs reliably and safely in production."
        ),
    },
    {
        **_base("api-rate-limiting-policy"),
        "round1_concern": (
            "DO NOT CONCUR. The decision does not address how rate limits are enforced when the "
            "gateway is unavailable or during a rollback, potentially leaving the system open to abuse "
            "or a compromised agent role exploiting the lack of rate limiting."
        ),
        "no_attempt_revision": _BY_SLUG["api-rate-limiting-policy"]["negative_fixture"],
        "vague_gesture_revision": (
            _BY_SLUG["api-rate-limiting-policy"]["negative_fixture"]
            + "\n\nResilience: We will implement appropriate safeguards to ensure rate limits continue "
            "to function correctly and securely during any gateway rollback or outage."
        ),
    },
]
