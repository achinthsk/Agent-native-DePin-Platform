"""Shared rate limiter — identity = API key or IP."""

from __future__ import annotations

import threading
import time
from collections import defaultdict, deque


class RateLimiter:
    """Rolling-window limiter. Default: 60 requests / 60 seconds / identity."""

    def __init__(self, *, limit: int = 60, window_seconds: float = 60.0) -> None:
        self.limit = int(limit)
        self.window_seconds = float(window_seconds)
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def check(self, identity: str) -> tuple[bool, int, int]:
        """
        Returns (allowed, remaining, retry_after_seconds).
        On deny, remaining is 0 and retry_after_seconds is > 0.
        """
        now = time.monotonic()
        cutoff = now - self.window_seconds
        with self._lock:
            q = self._hits[identity]
            while q and q[0] < cutoff:
                q.popleft()
            if len(q) >= self.limit:
                retry = int(max(1, self.window_seconds - (now - q[0])))
                return False, 0, retry
            q.append(now)
            remaining = self.limit - len(q)
            return True, remaining, 0


# Module singleton configured at app startup.
limiter = RateLimiter(limit=60, window_seconds=60.0)


def configure_rate_limit(*, limit: int = 60, window_seconds: float = 60.0) -> None:
    global limiter
    limiter = RateLimiter(limit=limit, window_seconds=window_seconds)
