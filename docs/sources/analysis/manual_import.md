# Manual CSV/JSON/XLSX Import (`manual_import`)

| Field | Value |
|-------|-------|
| Analysis | DONE |
| Role | Operator upload path — **not** remote scrape |
| Sample | `data/samples/jobs_sample.csv` |

## Access

- In-app / API upload of tabular job rows; mapped into canonical jobs by ingestion.

## Field map

- Depends on column headers supplied by operator; see import validation in backend ingest.

## Gaps

- No remote endpoint; quality = operator data quality.
