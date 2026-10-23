# DOU.ua (`dou_ua`)

| Field | Value |
|-------|-------|
| Analysis | DONE |
| collection_mode | feed |
| Collector file | `backend/app/collectors/dou_ua.py` |
| Probed_at | 2026-10-21 |
| Sample_records | 50 (RSS base feed, `MAX_RECORDS=50`) |

## Endpoint

- **URL:** `GET https://jobs.dou.ua/vacancies/feeds/` (aggregate feed; category feeds exist but unused).
- **Filter:** optional client query on title/description.
- **Cap:** 50 items.

## Payload / page structure

- RSS items; titles like `"Role в Company, City"` (Cyrillic).
- Links: `/companies/{slug}/vacancies/{id}/`.

## Field map → RawJob

| RawJob | Source |
|--------|--------|
| `source_job_id` | `/vacancies/{id}` from link or `guid` |
| `url` | `link` path only (no query/tracking) |
| `title` | full RSS `title` (includes company/city text) |
| `company` | parsed after ` в ` or URL slug title-case |
| `location` | last comma segment after ` в ` or `"Ukraine"` |
| `description` | HTML-stripped description |
| `published_at` | `pubDate` |
| `salary_text` | `None` (salary may appear in title only) |
| `tags` | `[]` |
| `job_type` | `None` |
| `remote_hint` | `None` |
| `raw` | `{title, link}` |

## Gaps / precision risks

- Title not normalized to role-only; company duplicated in title.
- Salary in title (e.g. `$1000`) not mapped to `salary_text`.
- Base feed only; no category-specific RSS in collector.

## Live sample (redacted)

```json
{
  "source_job_id": "377439",
  "title": "Content Manager в Epic Play Holding, до $1000, віддалено",
  "company": "Epic Play Holding",
  "location": "віддалено"
}
```
