from pathlib import Path

from filinglens.sec.tickers import read_tickers


def test_read_tickers_skips_blanks_and_comments(tmp_path):
    f = tmp_path / "tickers.txt"
    f.write_text("aapl\n\n# comment\nmsft  # inline\n", encoding="utf-8")
    assert read_tickers(f) == ["AAPL", "MSFT"]
