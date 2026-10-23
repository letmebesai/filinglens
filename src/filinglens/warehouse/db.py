"""Connection helper for the DuckDB warehouse."""

from __future__ import annotations

from pathlib import Path

import duckdb

from filinglens.warehouse.schema import RAW_TABLES_SQL


def connect(db_path: Path) -> duckdb.DuckDBPyConnection:
    """Open the warehouse and make sure the raw tables exist."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(db_path))
    con.execute(RAW_TABLES_SQL)
    return con
