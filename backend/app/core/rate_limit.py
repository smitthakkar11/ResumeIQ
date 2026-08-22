"""Minimal in-memory rate limiter for authentication endpoints.

Without this, /auth/login can be brute-forced: bcrypt makes each guess cost
~200ms, but an attacker can run thousands in parallel.

Honest limitation: the counters live in this process's memory, so with several
uvicorn workers each gets its own allowance, and a restart clears them. That is
acceptable for a single-instance deployment. A multi-instance one needs a
shared store (Redis) — the interface below would not change.
"""

import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request, status


class RateLimiter:
    """Sliding window: at most `limit` requests per `window` seconds, per IP."""

    def __init__(self, limit: int, window_seconds: int) -> None:
        self.limit = limit
        self.window = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def __call__(self, request: Request) -> None:
        key = request.client.host if request.client else "unknown"
        now = time.monotonic()
        hits = self._hits[key]

        # Drop timestamps that have fallen out of the window.
        while hits and now - hits[0] > self.window:
            hits.popleft()

        if len(hits) >= self.limit:
            retry_after = int(self.window - (now - hits[0])) + 1
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many attempts. Please wait and try again.",
                headers={"Retry-After": str(retry_after)},
            )

        hits.append(now)


# 10 attempts per 5 minutes: generous for a person mistyping a password,
# useless for a dictionary attack.
login_rate_limit = RateLimiter(limit=10, window_seconds=300)
signup_rate_limit = RateLimiter(limit=5, window_seconds=3600)
