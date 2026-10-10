import pytest

from filinglens.sec.ratelimit import RateLimiter


def test_spaces_requests_evenly():
    sleeps: list[float] = []
    limiter = RateLimiter(5, clock=lambda: 0.0, sleep=sleeps.append)
    for _ in range(3):
        limiter.wait()
    assert sleeps == pytest.approx([0.2, 0.4])


def test_no_delay_when_enough_time_has_passed():
    sleeps: list[float] = []
    now = [0.0]
    limiter = RateLimiter(5, clock=lambda: now[0], sleep=sleeps.append)
    limiter.wait()
    now[0] = 10.0
    limiter.wait()
    assert sleeps == []


def test_rejects_non_positive_rate():
    with pytest.raises(ValueError):
        RateLimiter(0)
