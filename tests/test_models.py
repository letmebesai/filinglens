import datetime

from filinglens.warehouse.db import connect
from filinglens.warehouse.models import build_models


def _ins(con, accn, filed, value, start="2010-09-26", end="2010-12-25"):
    con.execute(
        "INSERT INTO raw_facts VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        ["0000000001", "us-gaap", "Revenues", "USD", start, end, value, accn,
         2011, "Q1", "10-Q", filed, "https://data.sec.gov/x", "2026-10-23T00:00:00", "abc"],
    )


def test_gold_picks_latest_and_flags_restatement(tmp_path):
    con = connect(tmp_path / "wh.duckdb")
    _ins(con, "A", "2011-01-19", 100)
    _ins(con, "B", "2012-01-20", 110)
    build_models(con)
    rows = con.execute(
        "SELECT value, accession_number, n_reports, first_filed, latest_filed, restated FROM gold_facts_latest"
    ).fetchall()
    assert rows == [(110, "B", 2, datetime.date(2011, 1, 19), datetime.date(2012, 1, 20), True)]
    con.close()


def test_single_report_is_not_restated(tmp_path):
    con = connect(tmp_path / "wh.duckdb")
    _ins(con, "A", "2011-01-19", 100)
    build_models(con)
    row = con.execute("SELECT n_reports, restated FROM gold_facts_latest").fetchone()
    assert row == (1, False)
    con.close()


def test_same_filed_date_tie_is_deterministic_and_not_restated(tmp_path):
    con = connect(tmp_path / "wh.duckdb")
    _ins(con, "A", "2011-01-19", 100)
    _ins(con, "B", "2011-01-19", 100)
    build_models(con)
    row = con.execute("SELECT accession_number, n_reports, restated FROM gold_facts_latest").fetchone()
    assert row == ("B", 2, False)
    con.close()


def test_silver_drops_rows_without_value(tmp_path):
    con = connect(tmp_path / "wh.duckdb")
    _ins(con, "A", "2011-01-19", None)
    build_models(con)
    assert con.execute("SELECT count(*) FROM silver_facts").fetchone()[0] == 0
    con.close()