# NAV Arbeidsplassen (`nav_arbeidsplassen`)

| Field | Value |
|-------|-------|
| Analysis | DONE |
| collection_mode | search |
| Collector file | `backend/app/collectors/nav_arbeidsplassen.py` |
| Probed_at | 2026-10-21 |
| Sample_records | 25 (`q=software`, `size=50` cap) |

## Endpoint

- **URL:** `GET https://arbeidsplassen.nav.no/stillinger/api/search`
- **Params:** `q`, `size=50` (`MAX_RECORDS`).
- Blank query → `missing_query`.

## Payload / page structure

- Elasticsearch-style JSON: `hits.hits[]` with `_source` (or flat hit).
- `_source`: `uuid`, `title`, `published`, `employer`, `properties`, `locationList`, `categoryList`, `generatedSearchMetadata`.

## Field map → RawJob

| RawJob | Source |
|--------|--------|
| `source_job_id` | `_source.uuid` or `_id` |
| `url` | `https://arbeidsplassen.nav.no/stillinger/stilling/{uuid}` |
| `title` | `_source.title` |
| `company` | `employer.name` or `properties.employer` or `businessName` |
| `description` | `generatedSearchMetadata.shortSummary` only |
| `location` | `properties.location` or first `locationList` city/county/country; default `"Norway"` |
| `published_at` | `published` ISO |
| `salary_text` | `None` |
| `tags` | `properties.searchtagsai`, `keywords`, `categoryList.name` (deduped, max 20) |
| `job_type` | `None` |
| `remote_hint` | `properties.remote` text (hjemme/remote/hybrid vs kontor) |
| `raw` | trimmed uuid/title/published/employer/location/remote |

## Dedupe vs `nav_stilling_feed`

- Same vacancy UUID → same `https://arbeidsplassen.nav.no/stillinger/stilling/{uuid}` URL.
- Ingest merges across sources on `canonical_url`. Feed dump covers recent ACTIVE without a search query.

## Gaps / precision risks

- No full ad text in search API; summary-only description.
- No salary extraction.
- Single page; no scroll/search_after.

## Live sample (redacted)

```json
{
  "source_job_id": "ff180b88-49a5-4f21-805e-8cdbfa6d2292",
  "title": "Vil du jobbe med kvalitet i software?",
  "company": "KONGSBERG DEFENCE & AEROSPACE AS AVD KON"
}
```
