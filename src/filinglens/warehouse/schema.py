"""Raw table definitions for the DuckDB warehouse.

Every raw table carries provenance columns so any row can be traced back
to the bronze file and SEC URL it came from.
"""

RAW_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS raw_companies (
    cik            VARCHAR NOT NULL,
    ticker         VARCHAR NOT NULL,
    title          VARCHAR,
    source_url     VARCHAR NOT NULL,
    retrieved_at   TIMESTAMP NOT NULL,
    sha256         VARCHAR NOT NULL,
    PRIMARY KEY (cik, ticker, retrieved_at)
);

CREATE TABLE IF NOT EXISTS raw_filings (
    cik                VARCHAR NOT NULL,
    accession_number   VARCHAR NOT NULL,
    form               VARCHAR,
    filing_date        DATE,
    primary_document   VARCHAR,
    source_url         VARCHAR NOT NULL,
    retrieved_at       TIMESTAMP NOT NULL,
    sha256             VARCHAR NOT NULL,
    PRIMARY KEY (cik, accession_number, retrieved_at)
);

CREATE TABLE IF NOT EXISTS raw_facts (
    cik            VARCHAR NOT NULL,
    taxonomy       VARCHAR NOT NULL,
    concept        VARCHAR NOT NULL,
    unit           VARCHAR NOT NULL,
    period_end     DATE,
    value          DOUBLE,
    accession_number VARCHAR,
    filed_date     DATE,
    source_url     VARCHAR NOT NULL,
    retrieved_at   TIMESTAMP NOT NULL,
    sha256         VARCHAR NOT NULL
);
"""
