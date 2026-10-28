import datetime
import json

from filinglens.warehouse.db import connect
from filinglens.warehouse.loaders import load_companyfacts

URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json"
RETRIEVED = "2026-10-23T00:00:00"

SAMPLE = {
    "cik": 320193,
    "entityName": "Apple Inc.",
    "facts": {
        "us-gaap": {
            "AccountsPayable": {
                "units": {
                    "USD": [
                        {
                            "end": "2010-12-31",
                            "val": 170330000000,
                            "accn": "0001193125-11-212045",
                            "fy": 2011,
                            "fp": "Q3",
                            "form": "10-Q",
                            "filed": "2011-08-05",
                        }
                    ]
                }
            },
            "Revenues": {
                "units": {
                    "USD": [
                        {
                            "start": "2010-09-26",
                            "end": "2010-12-25",
                            "val": 26741000000,
                            "accn": "0001193125-11-010144",
                            "fy": 2011,
                            "fp": "Q1",
                            "form": "10-Q",
                            "filed": "2011-01-19",
                        }
                    ]
                }
            },
        }
    },
}


def _write(tmp_path, payload, name="CIK0000320193.json"):
    src = tmp_path / name
    src.write_text(json.dumps(payload), encoding="utf-8")
    return src


def test_load_companyfacts_inserts_rows_with_provenance(tmp_path):
    src = _write(tmp_path, SAMPLE)
    con = connect(tmp_path / "wh.duckdb")
    n = load_companyfacts(con, src, URL, RETRIEVED, "abc")
    assert n == 2
    row = con.execute(
        "SELECT cik, concept, value, accession_number, source_url, sha256 "
        "FROM raw_facts WHERE concept = 'AccountsPayable'"
    ).fetchone()
    assert row[0] == "0000320193"
    assert row[1] == "AccountsPayable"
    assert row[2] == 170330000000
    assert row[3] == "0001193125-11-212045"
    assert row[4].startswith("https://data.sec.gov/")
    assert row[5] == "abc"
    con.close()


def test_load_keeps_fiscal_fields_and_form(tmp_path):
    src = _write(tmp_path, SAMPLE)
    con = connect(tmp_path / "wh.duckdb")
    load_companyfacts(con, src, URL, RETRIEVED, "abc")
    row = con.execute(
        "SELECT fiscal_year, fiscal_period, form, filed_date "
        "FROM raw_facts WHERE concept = 'AccountsPayable'"
    ).fetchone()
    assert row == (2011, "Q3", "10-Q", datetime.date(2011, 8, 5))
    con.close()


def test_period_start_kept_for_duration_and_null_for_instant(tmp_path):
    src = _write(tmp_path, SAMPLE)
    con = connect(tmp_path / "wh.duckdb")
    load_companyfacts(con, src, URL, RETRIEVED, "abc")
    start = dict(con.execute("SELECT concept, period_start FROM raw_facts").fetchall())
    assert start["Revenues"] == datetime.date(2010, 9, 26)
    assert start["AccountsPayable"] is None
    con.close()


def test_reload_same_file_does_not_double_count(tmp_path):
    src = _write(tmp_path, SAMPLE)
    con = connect(tmp_path / "wh.duckdb")
    assert load_companyfacts(con, src, URL, RETRIEVED, "abc") == 2
    assert load_companyfacts(con, src, URL, RETRIEVED, "abc") == 2
    assert con.execute("SELECT count(*) FROM raw_facts").fetchone()[0] == 2
    con.close()


def test_reload_replaces_only_that_cik(tmp_path):
    other = {**SAMPLE, "cik": 789019}
    con = connect(tmp_path / "wh.duckdb")
    load_companyfacts(con, _write(tmp_path, SAMPLE), URL, RETRIEVED, "abc")
    load_companyfacts(con, _write(tmp_path, other, "CIK0000789019.json"), URL, RETRIEVED, "def")
    load_companyfacts(con, _write(tmp_path, SAMPLE), URL, RETRIEVED, "abc2")
    counts = dict(con.execute("SELECT cik, count(*) FROM raw_facts GROUP BY cik").fetchall())
    assert counts == {"0000320193": 2, "0000789019": 2}
    shas = dict(con.execute("SELECT cik, max(sha256) FROM raw_facts GROUP BY cik").fetchall())
    assert shas["0000320193"] == "abc2"
    assert shas["0000789019"] == "def"
    con.close()