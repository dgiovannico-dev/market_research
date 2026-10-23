# Jobweb Kenya (`jobweb_kenya`)

| Field | Value |
|-------|-------|
| Analysis | DONE |
| collection_mode | feed |
| Collector file | `backend/app/collectors/jobweb_kenya.py` |
| Probed_at | 2026-10-21 |
| Sample_records | 10 (live collect, no query filter) |

## Endpoint

- **Method / URL:** `GET https://www.jobwebkenya.com/feed/`
- **Auth:** none
- **Format:** RSS 2.0 (`application/rss+xml`)
- **Cap:** `MAX_RECORDS=40` items from `channel/item`
- **Optional filter:** query in `title` or `description` (case-insensitive)

## Payload / page structure

- **Parser:** `xml.etree.ElementTree` on response body
- **Item paths:** `./channel/item` → `title`, `link`, `description`, `pubDate`
- **Title convention:** often `"Role at Company"` → split on last `" at "`

## Field map → RawJob

| Source path | RawJob field | Transform / notes |
|-------------|--------------|-------------------|
| link slug | source_job_id | last path segment of `link` |
| `link` | url | required |
| `title` | title | role part after `_split_title`; else full title |
| `title` | company | company part after `" at "` |
| `description` | description | strip HTML tags via regex |
| _(literal)_ | location | always `"Kenya"` |
| `pubDate` | published_at | RFC 2822 via `parsedate_to_datetime` |
| _(none)_ | salary_text, tags, job_type, remote_hint | empty / `None` |
| `{title, link}` | raw | minimal |

## Gaps / precision risks

- Title parsing fails when title lacks `" at "` (company stays null)
- Location never granular (city not extracted)
- Feed length varies (live: 10 items)
- Description may contain HTML entities before strip

## Live sample (redacted)

```json
{
  "title": "Veterinary Internship Programme at Ministry of Agriculture…",
  "link": "https://jobwebkenya.com/jobs/veterinary-internship-programme…",
  "pubDate": "Tue, 21 Oct 2026 09:03:12 +0000",
  "description": "<p>…truncated HTML…</p>"
}
```
