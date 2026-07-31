"""Simple token-bucket rate limiter, written for a proposed self-service
expense-submission API that would be exposed to third-party integrations.
That API was never shipped (deprioritized after the 2024 planning review), so
this module is currently unused by any running code path. Kept because the
third-party API proposal may come back, per the platform team's notes.
"""

import time


class TokenBucket:
    def __init__(self, capacity: int, refill_per_second: float):
        self.capacity = capacity
        self.refill_per_second = refill_per_second
        self._tokens = float(capacity)
        self._last_refill = time.monotonic()

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(self.capacity, self._tokens + elapsed * self.refill_per_second)
        self._last_refill = now

    def try_consume(self, amount: int = 1) -> bool:
        self._refill()
        if self._tokens >= amount:
            self._tokens -= amount
            return True
        return False


_BUCKETS_BY_CLIENT: dict[str, TokenBucket] = {}


def allow_request(client_id: str, capacity: int = 60, refill_per_second: float = 1.0) -> bool:
    if client_id not in _BUCKETS_BY_CLIENT:
        _BUCKETS_BY_CLIENT[client_id] = TokenBucket(capacity, refill_per_second)
    return _BUCKETS_BY_CLIENT[client_id].try_consume()
