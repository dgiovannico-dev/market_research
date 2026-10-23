# Jobindex (`jobindex`)

| Field | Value |
|-------|-------|
| Analysis | DONE |
| collection_mode | feed |
| Collector file | `backend/app/collectors/jobindex.py` |
| Probed_at | 2026-10-21 |
| Sample_records | 20 (RSS default feed, `MAX_RECORDS=50`) |

## Endpoint

- **URL:** `GET https://www.jobindex.dk/jobsoegning.rss`
- **Params:** optional `q` keyword.
- **Cap:** 50 items.

## Payload / page structure

- RSS `channel/item`: `title`, `link`, `description`, `pubDate`, `guid`.
- Title pattern often `"Role, Company"` (split on last comma).

## Field map → RawJob

| RawJob | Source |
|--------|--------|
| `source_job_id` | `/vis-job/{id}` or trailing digits from link/guid |
| `url` | `link` |
| `title` | role part after title split, or full title |
| `company` | company part after title split |
| `description` | HTML-stripped `description` |
| `location` | constant `"Denmark"` |
| `published_at` | `pubDate` |
| `salary_text` | `None` |
| `tags` | `[]` |
| `job_type` | `None` |
| `remote_hint` | `None` |
| `raw` | `{title, link}` |

## Gaps / precision risks

- Company/title split fails when title has no comma.
- No city/region parsing; country fixed to Denmark.
- RSS window limited; optional `q` not used in default crawl.

## Live sample (redacted)

```json
{
  "source_job_id": "h1709434",
  "title": "Markedsresearcher til Fischer Group, deltid",
  "company": "Fischer Group",
  "location": "Denmark"
}
```
