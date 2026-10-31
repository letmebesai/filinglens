"""Silver and gold views over raw_facts."""

from __future__ import annotations

import duckdb

SILVER_FACTS_SQL = """
CREATE OR REPLACE VIEW silver_facts AS
SELECT *
FROM raw_facts
WHERE period_end IS NOT NULL
  AND value IS NOT NULL
  AND filed_date IS NOT NULL
"""

GOLD_FACTS_LATEST_SQL = """
CREATE OR REPLACE VIEW gold_facts_latest AS
WITH ranked AS (
    SELECT
        cik, taxonomy, concept, unit, period_start, period_end, value,
        accession_number, fiscal_year, fiscal_period, form, filed_date,
        source_url, retrieved_at, sha256,
        row_number() OVER w AS rn,
        count(*) OVER k AS n_reports,
        min(filed_date) OVER k AS first_filed,
        min(value) OVER k AS min_value,
        max(value) OVER k AS max_value
    FROM silver_facts
    WINDOW
        k AS (PARTITION BY cik, taxonomy, concept, unit, period_start, period_end),
        w AS (PARTITION BY cik, taxonomy, concept, unit, period_start, period_end
              ORDER BY filed_date DESC, accession_number DESC NULLS LAST)
)
SELECT
    cik, taxonomy, concept, unit, period_start, period_end, value,
    accession_number, fiscal_year, fiscal_period, form,
    filed_date AS latest_filed,
    n_reports,
    first_filed,
    (min_value <> max_value) AS restated,
    source_url, retrieved_at, sha256
FROM ranked
WHERE rn = 1
"""


def build_models(con: duckdb.DuckDBPyConnection) -> None:
    """(Re)create the silver and gold views."""
    con.execute(SILVER_FACTS_SQL)
    con.execute(GOLD_FACTS_LATEST_SQL)