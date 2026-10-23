# Recruitee Careers Site offers (`recruitee`)

| Field | Value |
|-------|-------|
| Analysis | DONE |
| collection_mode | dump |
| Collector file | `backend/app/collectors/recruitee.py` |
| Probed_at | 2026-10-21 |
| Sample_records | max 40/slug (`MAX_PER_TENANT`) |

## Endpoint

- **Method / URL template:** `GET https://{slug}.recruitee.com/api/offers/`
- **Auth:** none until **2027-02-10** (then `X-Careers-Sites-Token` per Recruitee docs)
- **Env tenant list:** `RECRUITEE_SLUGS` (CSV; see `docs/sources/ATS_TENANTS.md`)
- **Pagination:** single response per slug (no page loop); ingest stops at **40** matched jobs
- **Not used:** `api.recruitee.com` ATS API (token; PARTNER_ONLY)

## Payload / page structure

- **Content-Type:** `application/json`
- **Path:** `offers[]`
- **Per-item keys used:** `id`, `slug`, `title`, `company_name`, `careers_url`, `city`/`country`/`location`/`locations`, `description`/`requirements`, `published_at`, `department`/`tags`, `remote`/`hybrid`/`on_site`

## Field map → RawJob

| Source path | RawJob field | Transform / notes |
|-------------|--------------|-------------------|
| `{slug}:{id}` | source_job_id | |
| `careers_url` else built `/o/{slug}` | url | |
| `title` | title | |
| `company_name` else slug | company | |
| `description` else `requirements` | description | HTML kept |
| `city` + `country` (or `locations[0]`) | location | |
| `published_at` (`YYYY-MM-DD HH:MM:SS UTC`) | published_at | |
| `department` + `tags` | tags | max 12 |
| `remote` / `on_site` / `hybrid` | remote_hint | remote→True; on_site→False; hybrid→None |

## Gaps / precision risks

- **2027-02-10** unauth deadline — add token env before then
- Empty `offers[]` is valid (200); still counts as success with 0 records for that slug
- Custom careers domains not in allowlist shape (slug-only); prefer `*.recruitee.com` slugs

## Live sample (redacted)

```json
{
  "id": 2783543,
  "slug": "head-of-product-6",
  "title": "Head of Product",
  "company_name": "bunq",
  "careers_url": "https://careers.bunq.com/o/head-of-product-6",
  "city": "Amsterdam",
  "country": "Netherlands",
  "department": "Product",
  "published_at": "2026-10-15 09:31:36 UTC",
  "hybrid": true
}
```
