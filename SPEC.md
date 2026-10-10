# FilingLens: specification (v0.1)

## Goal
An MCP server that lets AI assistants answer questions about US public company filings, where every result carries its proof: accession number, section, filing date and retrieval time.

## Who it is for
- Developers and analysts who use MCP clients (Claude Desktop, Claude Code and others) and need verifiable answers about company filings.
- Contributors who want a clean, tested example of a data pipeline feeding a retrieval system.

## Principles
1. **No answer without a source.** Every tool response includes provenance.
2. **The server returns evidence; the client LLM writes the answer.** No LLM calls inside the server, so it is free to run and its evals are deterministic.
3. **Read-only.** No tool writes data or executes anything.
4. **Filing text is untrusted input.** It is delimited and marked as data.
5. **Measured, not claimed.** Quality is reported from a public eval suite.

## Data sources
- SEC EDGAR: filing submissions, XBRL company facts, 10-K and 10-Q documents.
- Compliance: declared User-Agent on every request and a rate limit kept below SEC's published limit.

## Scope (v0.1)
- About 30 large US companies (see `tickers.txt`).
- 10-K and 10-Q filings, last 2 years.
- XBRL structured financial facts.

## Out of scope for v0.1
India adapter (v0.2), Form 4 and 13F, streaming ingestion, orchestration (Dagster), web UI.

## MCP tools
| Tool | Purpose |
|---|---|
| `search_filings(query, ticker, form, year)` | Hybrid search over filing sections |
| `get_financial_fact(ticker, concept, period)` | Structured XBRL fact |
| `get_filing_section(accession, section)` | Full text of one section |
| `compare_metrics(tickers, concept, periods)` | One metric across companies |
| `data_freshness(ticker)` | How current the stored data is |

Every response includes a provenance block: accession number, section, filed date, source URL, retrieved_at, freshness.

## Architecture
SEC EDGAR -> bronze (raw JSON/HTML) -> DuckDB + dbt (silver, gold) -> section parser -> chunks -> LanceDB + BM25 -> hybrid retrieval -> MCP server (stdio).

## Evaluation plan
50 questions in `evals/questions.jsonl`:
- 25 numeric questions scored against XBRL ground truth.
- 25 retrieval questions with a known source section, scored by hit@k.

Results and reproduction scripts are published in `EVALS.md`.

## Definition of done (v0.1)
- Installs and runs on a clean machine in under 60 seconds.
- Eval numbers published in the README with reproducible scripts.
- Listed in at least 3 MCP directories.
- 5 good-first-issue tickets open.

## Open questions
- How a new user gets data on first run: prebuilt bundle or first-run build.
- Final license choice (MIT assumed).
- Project name availability on PyPI.
