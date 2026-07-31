"""Emits operational metrics to the monitoring backend. General-purpose, not
specific to any single endpoint or workflow — used across the whole service for
dashboards. Not required reading for implementing a specific feature.

Dashboards live in the internal Grafana instance under the "expenses" folder;
alerting thresholds are configured there, not in this module.
"""

import time
from contextlib import contextmanager


_COUNTERS: dict[str, int] = {}
_GAUGES: dict[str, float] = {}


def increment(name: str, by: int = 1) -> None:
    _COUNTERS[name] = _COUNTERS.get(name, 0) + by


def set_gauge(name: str, value: float) -> None:
    _GAUGES[name] = value


def snapshot() -> dict:
    """Returns a copy of current counters/gauges, used by the /internal/metrics
    debug endpoint. Not called anywhere in the request-handling path itself.
    """
    return {"counters": dict(_COUNTERS), "gauges": dict(_GAUGES)}


@contextmanager
def timed(name: str):
    start = time.monotonic()
    try:
        yield
    finally:
        elapsed_ms = (time.monotonic() - start) * 1000
        increment(f"{name}.count")
        increment(f"{name}.total_ms", by=int(elapsed_ms))


def reset_for_tests() -> None:
    _COUNTERS.clear()
    _GAUGES.clear()
