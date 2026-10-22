from filinglens.sec.tickers import build_cik_map, resolve

PAYLOAD = {
    "0": {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."},
    "1": {"cik_str": 789019, "ticker": "msft", "title": "Microsoft Corp"},
}


def test_build_cik_map_pads_and_uppercases():
    assert build_cik_map(PAYLOAD) == {"AAPL": "0000320193", "MSFT": "0000789019"}


def test_resolve_splits_found_and_missing():
    cik_map = build_cik_map(PAYLOAD)
    found, missing = resolve(["aapl", "XYZ"], cik_map)
    assert found == {"AAPL": "0000320193"}
    assert missing == ["XYZ"]
