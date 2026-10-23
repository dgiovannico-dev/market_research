# Duunitori (`duunitori`)

| Field | Value |
|-------|-------|
| Analysis | DONE |
| collection_mode | search |
| Collector file | `backend/app/collectors/duunitori.py` |
| Probed_at | 2026-10-21 |
| Sample_records | 20 (`search=software`, page 1 only) |

## Endpoint

- **URL:** `GET https://duunitori.fi/api/v1/jobentries`
- **Params:** `search`, `page=1` (no multi-page loop).
- **Cap:** `MAX_RECORDS=50`. Blank query → `missing_query`.

## Payload / page structure

- JSON `{ "results": [ { slug, heading, company_name, descr, municipality_name, date_posted, ... } ] }`.

## Field map → RawJob

| RawJob | Source |
|--------|--------|
| `source_job_id` | `slug` |
| `url` | `https://duunitori.fi/tyopaikat/tyo/{slug}` |
| `title` | `heading` |
| `company` | `company_name` |
| `description` | `descr` if string |
| `location` | `municipality_name` or `"Finland"` |
| `published_at` | `date_posted` ISO |
| `salary_text` | `None` |
| `tags` | `[]` |
| `job_type` | `None` |
| `remote_hint` | `None` |
| `raw` | slug/heading/company/municipality/date |

## Gaps / precision risks

- Single API page; total results may exceed 20–50 shown.
- `descr` may be truncated teaser vs full posting.
- No remote/salary signals extracted.

## Live sample (redacted)

```json
{
  "source_job_id": "aidian-junior-software-engineer-sdsuu-2066736",
  "title": "Junior Software Engineer",
  "company": "Aidian Oy",
  "location": "…"
}
```
