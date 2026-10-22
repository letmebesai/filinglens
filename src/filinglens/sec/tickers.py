"""Map tickers to SEC CIKs using the SEC company_tickers.json file."""

from __future__ import annotations

from collections.abc import Iterable


def build_cik_map(payload: dict) -> dict[str, str]:
    """Build {TICKER: 10-digit CIK} from the SEC company_tickers.json payload.

    The SEC payload looks like:
        {"0": {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."}, ...}
    """
    cik_map: dict[str, str] = {}
    for entry in payload.values():
        ticker = str(entry["ticker"]).strip().upper()
        cik = str(entry["cik_str"]).zfill(10)
        cik_map.setdefault(ticker, cik)
    return cik_map


def resolve(tickers: Iterable[str], cik_map: dict[str, str]) -> tuple[dict[str, str], list[str]]:
    """Return (found, missing): found maps ticker -> CIK, missing lists unknown tickers."""
    found: dict[str, str] = {}
    missing: list[str] = []
    for raw in tickers:
        ticker = raw.strip().upper()
        if ticker in cik_map:
            found[ticker] = cik_map[ticker]
        else:
            missing.append(ticker)
    return found, missing
