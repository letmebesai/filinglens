import httpx
import pytest

from filinglens.sec.client import SecClient, SecError
from filinglens.sec.ratelimit import RateLimiter

UA = "Test User test@example.com"


def make_client(handler, sleeps=None, max_retries=3):
    return SecClient(
        user_agent=UA,
        limiter=RateLimiter(1000),
        max_retries=max_retries,
        backoff_base=1.0,
        transport=httpx.MockTransport(handler),
        sleep=(sleeps.append if sleeps is not None else lambda s: None),
    )


def test_sends_declared_user_agent():
    seen = {}

    def handler(request):
        seen["ua"] = request.headers["User-Agent"]
        return httpx.Response(200, json={"ok": True})

    with make_client(handler) as client:
        assert client.get_json("https://data.sec.gov/x") == {"ok": True}
    assert seen["ua"] == UA


def test_retries_then_succeeds():
    calls = {"n": 0}
    sleeps: list[float] = []

    def handler(request):
        calls["n"] += 1
        if calls["n"] < 3:
            return httpx.Response(503)
        return httpx.Response(200, json={"ok": True})

    with make_client(handler, sleeps) as client:
        assert client.get_json("https://data.sec.gov/x") == {"ok": True}
    assert calls["n"] == 3
    assert sleeps == [1.0, 2.0]


def test_gives_up_after_max_retries():
    def handler(request):
        return httpx.Response(500)

    with make_client(handler, max_retries=2) as client:
        with pytest.raises(SecError):
            client.get("https://data.sec.gov/x")


def test_does_not_retry_not_found():
    calls = {"n": 0}

    def handler(request):
        calls["n"] += 1
        return httpx.Response(404)

    with make_client(handler) as client:
        with pytest.raises(SecError):
            client.get("https://data.sec.gov/x")
    assert calls["n"] == 1


def test_cik_is_zero_padded_in_urls():
    urls = []

    def handler(request):
        urls.append(str(request.url))
        return httpx.Response(200, json={})

    with make_client(handler) as client:
        client.submissions(320193)
        client.company_facts("320193")
    assert urls == [
        "https://data.sec.gov/submissions/CIK0000320193.json",
        "https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json",
    ]
