# Posao.hr (`posao_hr`)

| Field | Value |
|-------|-------|
| Analysis | DONE |
| collection_mode | feed |
| Collector file | `backend/app/collectors/posao_hr.py` |
| Probed_at | 2026-10-21 |
| Sample_records | 30 (RSS, `MAX_RECORDS=50`) |

## Endpoint

- **URL:** `GET https://www.posao.hr/rss`
- **Filter:** optional client `query` on title/description substring.
- **Cap:** 50 items.

## Payload / page structure

- RSS items; HTML `description` embeds `Poslodavac:` and `Mjesto rada:` labels.

## Field map → RawJob

| RawJob | Source |
|--------|--------|
| `source_job_id` | numeric id from URL path `/…/{id}/` |
| `url` | `link` |
| `title` | `title` |
| `company` | regex `Poslodavac:` from description |
| `description` | HTML-stripped description |
| `location` | regex `Mjesto rada:` or `"Croatia"` |
| `published_at` | `pubDate` |
| `salary_text` | `None` |
| `tags` | `[]` |
| `job_type` | `None` |
| `remote_hint` | `None` |
| `raw` | `{title, link}` |

## Gaps / precision risks

- Employer/location depend on Croatian label patterns in HTML.
- Feed is general labor market, not IT-only.
- No server-side search param on RSS URL.

## Live sample (redacted)

```json
{
  "source_job_id": "1253241",
  "title": "Spremačica / Domaćica (m/ž)",
  "company": "KTC d.d.",
  "location": "…"
}
```
