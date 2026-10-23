import duckdb

from filinglens.warehouse.db import connect


def test_connect_creates_raw_tables(tmp_path):
    con = connect(tmp_path / "test.duckdb")
    tables = {row[0] for row in con.execute("SHOW TABLES").fetchall()}
    assert {"raw_companies", "raw_filings", "raw_facts"} <= tables
    con.close()


def test_connect_is_idempotent(tmp_path):
    path = tmp_path / "test.duckdb"
    connect(path).close()
    con = connect(path)  # second open must not fail
    count = con.execute("SELECT count(*) FROM raw_facts").fetchone()[0]
    assert count == 0
    con.close()


def test_provenance_columns_present(tmp_path):
    con = connect(tmp_path / "test.duckdb")
    cols = {row[0] for row in con.execute("DESCRIBE raw_facts").fetchall()}
    assert {"source_url", "retrieved_at", "sha256"} <= cols
    con.close()
