"""A small thread-safe rate limiter that spaces requests evenly."""

from __future__ import annotations

import threading
import time
from collections.abc import Callable


class RateLimiter:
    """Allow at most `max_per_second` calls to `wait()` per second, evenly spaced."""

    def __init__(
        self,
        max_per_second: float,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        if max_per_second <= 0:
            raise ValueError("max_per_second must be positive")
        self._interval = 1.0 / max_per_second
        self._clock = clock
        self._sleep = sleep
        self._lock = threading.Lock()
        self._next_allowed = 0.0

    def wait(self) -> None:
        """Block until the next request is allowed."""
        with self._lock:
            now = self._clock()
            start = max(now, self._next_allowed)
            self._next_allowed = start + self._interval
            delay = start - now
        if delay > 0:
            self._sleep(delay)
