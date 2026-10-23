# HelloWorld.rs (`helloworld_rs`)

| Field | Value |
|-------|-------|
| Analysis | DONE |
| collection_mode | feed |
| Collector file | `backend/app/collectors/helloworld_rs.py` |
| Probed_at | 2026-10-21 |
| Sample_records | 15 (RSS, `MAX_RECORDS=40`) |

## Endpoint

- **URL:** `GET https://helloworld.rs/rss`
- **Filter:** optional client query on title/description.
- **Cap:** 40 items.

## Payload / page structure

- RSS `channel/item`; description sometimes `"Company - …"` prefix before body text.

## Field map → RawJob

| RawJob | Source |
|--------|--------|
| `source_job_id` | numeric id from URL path |
| `url` | `link` without query string |
| `title` | `title` |
| `company` | text before first `" - "` in stripped description |
| `description` | HTML-stripped description |
| `location` | constant `"Serbia"` |
| `published_at` | `pubDate` |
| `salary_text` | `None` |
| `tags` | `["IT"]` (static) |
| `job_type` | `None` |
| `remote_hint` | `None` |
| `raw` | `{title, link}` |

## Gaps / precision risks

- Company heuristic fragile if description lacks `" - "` separator.
- Location not parsed from ad text.
- Small RSS window (15 items at probe time).

## Live sample (redacted)

```json
{
  "source_job_id": "762974",
  "title": "Koordinator sistem administracije",
  "url": "https://helloworld.rs/posao/Koordinator-sistem-administracije/Effecta-Solutions/",
  "company": null,
  "tags": ["IT"]
}
```
