# Arbetsförmedlingen JobSearch (`arbetsformedlingen`)

| Field | Value |
|-------|-------|
| Analysis | DONE |
| collection_mode | search |
| Collector file | `backend/app/collectors/arbetsformedlingen.py` |
| Probed_at | 2026-10-21 |
| Sample_records | 100 (`query=software`, `limit=100`) |

## Endpoint

- **URL:** `GET https://jobsearch.api.jobtechdev.se/search`
- **Params:** `q`, `limit=100`, `offset=0` (single page only).
- **Auth:** none. Blank query → `missing_query`.

## Payload / page structure

- JSON root with `hits[]` JobTech search documents.
- Key nested objects: `employer`, `description.text`, `workplace_address`, `occupation`, `employment_type`, `workplace_model`, `salary_description`, `publication_date`.

## Field map → RawJob

| RawJob | Source |
|--------|--------|
| `source_job_id` | `hit.id` |
| `url` | `webpage_url` or Platsbanken fallback `/annonser/{id}` |
| `title` | `headline` |
| `company` | `employer.name` or `employer.workplace` |
| `description` | `description.text` |
| `location` | city/municipality, region, country from `workplace_address` |
| `published_at` | `publication_date` or `last_publication_date` ISO |
| `salary_text` | `salary_description` stringified |
| `tags` | `[occupation.label]` if present |
| `job_type` | `employment_type.label` |
| `remote_hint` | from `workplace_model` label (remote/distans vs on-site) |
| `raw` | full `hit` |

## Gaps / precision risks

- No pagination beyond first 100 hits.
- `simplify_query_for` strips boolean OR to first clause.
- Invalid dates logged in `errors`, fall back to UTC now.

## Live sample (redacted)

```json
{
  "source_job_id": "31538929",
  "title": "Software Engineer / Senior Software Engineer",
  "url": "https://arbetsformedlingen.se/platsbanken/annonser/31538929",
  "company": "Hykmann Global Business Solutions AB"
}
```
