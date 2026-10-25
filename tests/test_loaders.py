import json

from filinglens.warehouse.db import connect
from filinglens.warehouse.loaders import load_companyfacts

SAMPLE = {
    "cik": 320193,
    "entityName": "Apple Inc.",
    "facts": {
        "us-gaap": {
            "AccountsPayable": {
                "units": {
                    "USD": [
                        {"end": "2010-12-31", "val": 170330000000, "accn": "0001193125-11-212045", "filed": "2011-08-05", "form": "10-Q"}
                    ]
                }
            }
        }
    },
}


def test_load_companyfacts_inserts_rows_with_provenance(tmp_path):
    src = tmp_path / "CIK0000320193.json"
    src.write_text(json.dumps(SAMPLE), encoding="utf-8")
    con = connect(tmp_path / "wh.duckdb")
    n = load_companyfacts(con, src, "https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json", "2026-10-23T00:00:00", "abc")
    assert n == 1
    row = con.execute("SELECT cik, concept, value, accession_number, source_url FROM raw_facts").fetchone()
    assert row[0] == "0000320193"
    assert row[1] == "AccountsPayable"
    assert row[2] == 170330000000
    assert row[3] == "0001193125-11-212045"
    assert row[4].startswith("https://data.sec.gov/")
    con.close()
