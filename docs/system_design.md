# JobBot POC System Design

## Objective

Collect fresh jobs from LinkedIn on a schedule, deduplicate them, and send a daily digest to Telegram.

## Components

- Scheduler or manual runner
- YAML config loader
- LinkedIn adapter
- SQLite state store
- Telegram notifier

## Flow

1. Load profile config.
2. Build search queries from keywords, locations, and freshness windows.
3. Query LinkedIn using the configured freshness window.
4. Fetch up to 3 LinkedIn result pages per query.
5. Normalize results into a common job schema.
6. Deduplicate within the run and against prior runs.
7. Apply configured location filters and cap the final output at 20 total postings.
8. Send the digest to Telegram.
9. Persist the fingerprints of delivered jobs.

## Notes

- The LinkedIn search URL uses `f_TPR=r{seconds}` as described in the provided PDF.
- The browser session is intentionally persistent so manual login can be reused.
- The POC is intentionally small and should be extended only after the collection flow is validated.
