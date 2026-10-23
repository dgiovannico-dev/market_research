# JobUp (`jobup`)

| Field | Value |
|-------|-------|
| Analysis | DONE |
| collection_mode | search |
| Collector file | `backend/app/collectors/jobup.py` |
| Probed_at | 2026-10-21 |
| Sample_records | 60 (`query=software`, 3 pages × 20 rows) |

## Endpoint

- **URL:** `GET https://www.jobup.ch/api/v1/public/search`
- **Params:** `query`, `rows` (max 20), `start` offset.
- **Caps:** `MAX_RECORDS=150`, `MAX_PAGES=3`; optional query fan-out (`software`, `devops`, `python`) for generic/IT queries.
- Blank query → `missing_query`.

## Payload / page structure

- JSON: `documents[]`, `total_hits`, `num_pages`, pagination fields.
- Document fields: `job_id`, `datapool_id`, `title`, `company_name`, `preview`, `place`, `salary`, `publication_date`, `listing_tags`, `_links.detail_*`, `is_active`.

## Field map → RawJob

| RawJob | Source |
|--------|--------|
| `source_job_id` | `job_id` or `datapool_id` |
| `url` | `_links.detail_en/fr/de.href` or `/en/jobs/detail/{id}/` |
| `title` | `title` |
| `company` | `company_name` |
| `description` | `preview` (snippet only) |
| `location` | `place` or `"Switzerland"` |
| `published_at` | `publication_date` or `initial_publication_date` |
| `salary_text` | `salary.range` gte/lte + currency/unit, or `salary_from` |
| `tags` | `listing_tags` (max 15) |
| `job_type` | `None` |
| `remote_hint` | `None` |
| `raw` | trimmed id/title/company/place/salary/date |

## Gaps / precision risks

- Preview ≠ full job body; no detail-page fetch.
- Fan-out can bias corpus toward hardcoded IT terms.
- Inactive jobs skipped via `is_active`.

## Live sample (redacted)

```json
{
  "source_job_id": "fd5507a3-e592-4230-b6a5-66841d981ebe",
  "title": "Développeur - Analyste",
  "url": "https://www.jobup.ch/en/jobs/detail/fd5507a3-e592-4230-b6a5-66841d981ebe/",
  "company": "Quorum Software SA"
}
```
