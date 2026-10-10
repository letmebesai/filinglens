"""HTTP client for SEC EDGAR: declared User-Agent, rate limiting, retries with backoff."""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

import httpx

from filinglens.config import MAX_REQUESTS_PER_SECOND, get_user_agent
from filinglens.sec.ratelimit import RateLimiter

DATA_BASE = "https://data.sec.gov"
WWW_BASE = "https://www.sec.gov"
RETRY_STATUS = {429, 500, 502, 503, 504}


class SecError(Exception):
    """Raised when SEC EDGAR cannot be reached or returns an error."""


class SecClient:
    def __init__(
        self,
        user_agent: str | None = None,
        limiter: RateLimiter | None = None,
        max_retries: int = 4,
        backoff_base: float = 1.0,
        timeout: float = 30.0,
        transport: httpx.BaseTransport | None = None,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._limiter = limiter or RateLimiter(MAX_REQUESTS_PER_SECOND)
        self._max_retries = max_retries
        self._backoff_base = backoff_base
        self._sleep = sleep
        self._http = httpx.Client(
            headers={"User-Agent": user_agent or get_user_agent()},
            timeout=timeout,
            transport=transport,
            follow_redirects=True,
        )

    def __enter__(self) -> SecClient:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def close(self) -> None:
        self._http.close()

    def get(self, url: str) -> httpx.Response:
        """GET a URL politely. Retries 429/5xx and network errors; fails fast on other 4xx."""
        last_error: Exception | None = None
        for attempt in range(self._max_retries + 1):
            self._limiter.wait()
            try:
                response = self._http.get(url)
            except httpx.TransportError as exc:
                last_error = exc
            else:
                if response.status_code < 400:
                    return response
                if response.status_code not in RETRY_STATUS:
                    raise SecError(f"HTTP {response.status_code} for {url}")
                last_error = SecError(f"HTTP {response.status_code} for {url}")
            if attempt < self._max_retries:
                self._sleep(self._backoff_base * 2**attempt)
        raise SecError(
            f"Giving up on {url} after {self._max_retries + 1} attempts"
        ) from last_error

    def get_json(self, url: str) -> Any:
        return self.get(url).json()

    # Endpoints. Confirm paths against SEC's EDGAR API documentation.
    def company_tickers(self) -> Any:
        return self.get_json(f"{WWW_BASE}/files/company_tickers.json")

    def submissions(self, cik: int | str) -> Any:
        return self.get_json(f"{DATA_BASE}/submissions/CIK{int(cik):010d}.json")

    def company_facts(self, cik: int | str) -> Any:
        return self.get_json(f"{DATA_BASE}/api/xbrl/companyfacts/CIK{int(cik):010d}.json")
