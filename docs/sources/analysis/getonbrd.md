# Get on Board (`getonbrd`)

| Field | Value |
|-------|-------|
| Analysis | DONE |
| collection_mode | dump |
| Collector file | `backend/app/collectors/getonbrd.py` |
| Probed_at | 2026-10-21 |
| Sample_records | 50 (programming category dump, `per_page=50`) |

## Endpoint

- **With query:** `GET https://www.getonbrd.com/api/v0/search/jobs?query=&per_page=50&page=1`
- **Without query:** `GET https://www.getonbrd.com/api/v0/categories/programming/jobs?per_page=50&page=1`
- **Cap:** `MAX_RECORDS=80` client-side.

## Payload / page structure

- JSON:API-ish `{ "data": [ { "id", "attributes": {...}, "links": {...} } ] }`.
- Attributes: title, description/projects, salaries, remote flags, countries, cities, tags, category_name, nested `company.data.id`.

## Field map → RawJob

| RawJob | Source |
|--------|--------|
| `source_job_id` | `id` |
| `url` | `links.public_url` or `/jobs/{id}` |
| `title` | `attributes.title` |
| `company` | `company:{id}` placeholder (name not resolved) |
| `description` | `description` or `projects` string |
| `location` | countries + cities + Remote zone text |
| `published_at` | `published_at` unix seconds |
| `salary_text` | min-max + currency/month or undeclared |
| `tags` | category_name + tag names |
| `job_type` | `None` |
| `remote_hint` | boolean `remote` |
| `raw` | trimmed attributes + links |

## Gaps / precision risks

- LATAM-focused API listed among EU set; geography is attribute-driven, not EU-only.
- Company label is opaque id, not human-readable name (included in API but not mapped).
- Single page fetch; not full programming catalog.

## Live sample (redacted)

```json
{
  "source_job_id": "go-engineer-microservices-improving-remote",
  "title": "Senior Go Engineer",
  "company": "company:4161",
  "remote_hint": true,
  "location": "…, Remote (…)"
}
```
