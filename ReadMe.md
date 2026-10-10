# FilingLens

**Provenance-first SEC research for AI assistants.** An MCP server that answers questions about US public company filings and shows its proof: every result carries the filing, the section and the date it came from.

> **Status: under active development.** v0.1 is planned for launch on Oct 22, 2026. Sections marked *planned* describe what is being built, not what exists yet.

## Why

AI assistants can read financial filings, but their answers are hard to verify. A revenue figure with no source is a guess. FilingLens is built around one rule: **no answer without a source.** Every tool response includes the filing's accession number, section, filing date and the time the data was retrieved, so you can check any claim in one click.

## What it does *(planned)*

- Ingests 10-K and 10-Q filings and XBRL financial data from SEC EDGAR for about 30 large US companies.
- Builds a tested data pipeline: raw (bronze) data, cleaned (silver) tables and analysis-ready (gold) tables in DuckDB, with dbt tests.
- Splits filings into sections (Item 1, 1A, 7, 8) and indexes them for hybrid search (BM25 + vector search with rank fusion).
- Exposes everything to MCP-compatible clients (Claude Desktop, Claude Code and others) through five read-only tools.
- Ships with a public evaluation suite of 50 questions, so retrieval quality is measured, not claimed.

## MCP tools *(planned)*

| Tool | What it does |
|---|---|
| `search_filings(query, ticker, form, year)` | Hybrid search over filing sections |
| `get_financial_fact(ticker, concept, period)` | Structured XBRL fact for a company, concept and period |
| `get_filing_section(accession, section)` | Full text of one section of a specific filing |
| `compare_metrics(tickers, concept, periods)` | One metric compared across companies |
| `data_freshness(ticker)` | How current the stored data is for a company |

All tools are read-only. Filing text is returned inside clear delimiters and marked as untrusted data.

## How it works *(planned)*

```
SEC EDGAR
   |
   v
bronze (raw JSON/HTML) --> DuckDB + dbt (silver, gold) --> structured facts
   |
   v
section parser --> chunks --> LanceDB (vectors) + BM25
                                   |
                                   v
                         hybrid retrieval + provenance
                                   |
                                   v
                              MCP server (stdio)
```

The server returns passages and facts. Your AI client writes the answer. This keeps the server free to run and makes the evals deterministic.

## Install *(planned)*

```bash
# Not published yet. Target for v0.1:
uvx filinglens
```

A Docker option and Claude Desktop configuration example will be added at launch.

## Evaluation *(planned)*

The repo will include 50 questions: 25 numeric questions scored against XBRL ground truth and 25 retrieval questions with a known source passage. Results and the scripts to reproduce them will be published in `EVALS.md`.

| Metric | Result |
|---|---|
| Numeric accuracy | TBD |
| Retrieval hit@k | TBD |

## Roadmap

- **v0.1:** US filers (about 30 companies), 10-K/10-Q, five tools, published evals.
- **v0.2:** India adapter (BSE/NSE filings, AMFI mutual fund NAVs, RBI data), subject to each source's terms of use.
- **Later:** Form 4 and 13F, more companies, optional reranker.

## Security

Tools are read-only and never execute trades or write data. Filing text is untrusted input and is delimited to reduce prompt-injection risk. See `SECURITY.md` *(planned)*.

## Contributing

Contributions are welcome once v0.1 ships. Look for issues labelled `good first issue`. See `CONTRIBUTING.md` *(planned)*.

## Disclaimer

FilingLens is a research tool, not financial advice. Data comes from SEC EDGAR and may be incomplete or delayed. Always verify against the original filing.

## License

MIT *(or Apache-2.0, to be confirmed)*