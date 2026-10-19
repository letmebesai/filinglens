from datetime import timedelta

import httpx

from filinglens.ingest.run import run_ingest
from filinglens.sec.client import SecClient
from filinglens.sec.ratelimit import RateLimiter

TICKERS = {"0": {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."}}


def make_client(handler):
    return SecClient(
        user_agent="Test User test@example.com",
        limiter=RateLimiter(1000),
        max_retries=0,
        transport=httpx.MockTransport(handler),
        sleep=lambda s: None,
    )


def test_fetches_then_skips_fresh_files(tmp_path):
    calls = []

    def handler(request):
        calls.append(request.url.path)
        if request.url.path == "/files/company_tickers.json":
            return httpx.Response(200, json=TICKERS)
        return httpx.Response(200, json={"ok": True})

    with make_client(handler) as client:
        first = run_ingest(client, ["AAPL"], tmp_path)
        calls_after_first = len(calls)
        second = run_ingest(client, ["AAPL"], tmp_path)

    assert first.fetched == ["AAPL/submissions", "AAPL/companyfacts"]
    assert (tmp_path / "submissions" / "CIK0000320193.json").exists()
    assert (tmp_path / "companyfacts" / "CIK0000320193.meta.json").exists()
    assert second.skipped == ["AAPL/submissions", "AAPL/companyfacts"]
    assert second.fetched == []
    assert len(calls) == calls_after_first  # nothing downloaded on the second run


def test_force_redownloads(tmp_path):
    def handler(request):
        if request.url.path == "/files/company_tickers.json":
            return httpx.Response(200, json=TICKERS)
        return httpx.Response(200, json={"ok": True})

    with make_client(handler) as client:
        run_ingest(client, ["AAPL"], tmp_path)
        again = run_ingest(client, ["AAPL"], tmp_path, force=True)
    assert len(again.fetched) == 2


def test_failure_is_reported_and_does_not_stop_the_run(tmp_path):
    def handler(request):
        if request.url.path == "/files/company_tickers.json":
            return httpx.Response(200, json=TICKERS)
        if "submissions" in request.url.path:
            return httpx.Response(404)
        return httpx.Response(200, json={"ok": True})

    with make_client(handler) as client:
        report = run_ingest(client, ["AAPL"], tmp_path)
    assert "AAPL/submissions" in report.failed
    assert report.fetched == ["AAPL/companyfacts"]
    assert not report.ok


def test_unknown_ticker_is_reported(tmp_path):
    def handler(request):
        return httpx.Response(200, json=TICKERS)

    with make_client(handler) as client:
        report = run_ingest(client, ["AAPL", "NOPE"], tmp_path, max_age=timedelta(hours=1))
    assert report.missing_tickers == ["NOPE"]
    