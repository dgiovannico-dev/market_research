# Landing.jobs (`landing_jobs`)

| Field | Value |
|-------|-------|
| Analysis | DONE |
| collection_mode | dump |
| Collector file | `backend/app/collectors/landing_jobs.py` |
| Probed_at | 2026-10-21 |
| Sample_records | 50 (full list capped at `MAX_RECORDS=80`) |

## Endpoint

- **URL:** `GET https://landing.jobs/api/v1/jobs`
- **Pagination:** none; returns JSON array. Optional client-side `query` substring filter on title/tags/role_description.
- **Cap:** first 80 matching rows.

## Payload / page structure

- Top-level JSON **array** of job objects: `id`, `title`, `url`, `tags`, `type`, `remote`, `locations[]`, salary fields, `role_description`, `main_requirements`, timestamps.

## Field map → RawJob

| RawJob | Source |
|--------|--------|
| `source_job_id` | `id` |
| `url` | `url` |
| `title` | `title` |
| `company` | parsed from URL path `/at/{slug}/` → title-cased slug |
| `description` | `role_description` or `main_requirements` |
| `location` | join up to 3 `locations[].city` + `country_code` |
| `published_at` | `published_at` / `updated_at` / `created_at` |
| `salary_text` | `gross_salary_low-high` + `currency_code`/year |
| `tags` | `tags` (max 15) |
| `job_type` | `type` |
| `remote_hint` | boolean `remote` |
| `raw` | trimmed id/title/url/salary/locations/remote/dates |

## Gaps / precision risks

- Company name inferred from URL slug, not API employer field.
- Dump is bounded sample, not full EU corpus (`dump_complete` false).
- Query filter is naive substring match.

## Live sample (redacted)

```json
{
  "source_job_id": "19066",
  "title": "Senior Java Software Developer",
  "url": "https://landing.jobs/at/inscale/senior-java-software-developer-in-lisbon-2025",
  "company": "Inscale",
  "remote_hint": false
}
```
