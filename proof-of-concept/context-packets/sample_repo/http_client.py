"""Shared HTTP client wrapper. Every outbound call in this codebase must go through here.

Background (incident INC-482): the vendor notification API silently drops requests
under load instead of returning an error or a 5xx status — it just accepts the
connection and never responds with anything meaningful, or times out with no body.
A bare `requests.post(...)` call has no way to distinguish that from a genuinely
successful, empty-body response, so failures were going unnoticed in production for
weeks before anyone traced dropped reminders back to this behavior.

`request_with_retry` exists specifically to paper over that: it retries with backoff
and jitter, and treats an ambiguous/empty response as a failure worth retrying rather
than a success. Do not bypass it by calling `requests` directly, even for "simple"
calls — see conventions.md, rule 1.
"""

import logging
import random
import time
from dataclasses import dataclass, field

import requests

from config import MAX_RETRIES, RETRY_BASE_DELAY_SECONDS

logger = logging.getLogger(__name__)


class UpstreamCallFailed(Exception):
    pass


@dataclass
class CallStats:
    """Rolling stats for a single outbound host, used only for local logging today.

    A real circuit breaker (trip after N consecutive failures, half-open probe,
    etc.) has been proposed twice in planning but is not implemented — see the
    #finance-eng backlog. Do not assume this class does any tripping; it is
    purely observational right now.
    """

    host: str
    attempts: int = 0
    failures: int = 0
    last_status_codes: list[int] = field(default_factory=list)

    def record(self, status_code: int | None, failed: bool) -> None:
        self.attempts += 1
        if failed:
            self.failures += 1
        if status_code is not None:
            self.last_status_codes.append(status_code)
            if len(self.last_status_codes) > 20:
                self.last_status_codes.pop(0)


_STATS_BY_HOST: dict[str, CallStats] = {}


def _stats_for(url: str) -> CallStats:
    host = url.split("/")[2] if "://" in url else url
    if host not in _STATS_BY_HOST:
        _STATS_BY_HOST[host] = CallStats(host=host)
    return _STATS_BY_HOST[host]


def _looks_like_silent_drop(response: requests.Response) -> bool:
    """Detect the INC-482 failure signature: a 2xx with no meaningful body.

    The vendor notification API sometimes accepts a connection under load and
    responds with an empty 200 instead of a timeout or a 5xx. To a naive caller
    that looks identical to a real success. We treat "2xx but empty body" as a
    failure worth retrying, not a success, specifically because of this incident.
    """
    if response.status_code >= 500:
        return True
    if not response.content:
        return True
    return False


def request_with_retry(method: str, url: str, **kwargs) -> requests.Response:
    """The only sanctioned way to make an outbound HTTP call in this codebase.

    Background (incident INC-482): the vendor notification API silently drops
    requests under load instead of returning an error or a 5xx status — it just
    accepts the connection and never responds with anything meaningful, or
    responds with a 200 and an empty body. A bare `requests.post(...)` call has
    no way to distinguish that from a genuinely successful, empty-body response,
    so failures were going unnoticed in production for weeks before anyone
    traced dropped reminders back to this behavior.

    This function exists specifically to paper over that: it retries with
    exponential backoff and jitter, and treats an ambiguous/empty response as a
    failure worth retrying rather than a success. Do not bypass it by calling
    `requests` directly, even for "simple" calls that seem unlikely to hit this
    — see conventions.md, rule 1.
    """
    stats = _stats_for(url)
    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.request(method, url, timeout=10, **kwargs)
            if _looks_like_silent_drop(response):
                stats.record(response.status_code, failed=True)
                raise UpstreamCallFailed(f"empty or 5xx response: {response.status_code}")
            stats.record(response.status_code, failed=False)
            return response
        except (requests.RequestException, UpstreamCallFailed) as exc:
            last_error = exc
            if not isinstance(exc, UpstreamCallFailed):
                stats.record(None, failed=True)
            delay = RETRY_BASE_DELAY_SECONDS * (2**attempt) + random.uniform(0, 0.25)
            logger.warning("retrying %s %s after error: %s (delay=%.2fs)", method, url, exc, delay)
            time.sleep(delay)
    raise UpstreamCallFailed(f"giving up after {MAX_RETRIES} attempts against {url}: {last_error}")


def get_host_stats(url: str) -> CallStats:
    """Exposed for debugging/ad-hoc inspection; not wired into any dashboard."""
    return _stats_for(url)
