# Le Forem (`le_forem`)

| Field | Value |
|-------|-------|
| Analysis | DONE |
| collection_mode | dump |
| Collector file | `backend/app/collectors/le_forem.py` |
| Probed_at | 2026-10-21 |
| Sample_records | 200 (`MAX_RECORDS`, 2 ODWB pages) |

## Endpoint

- **URL:** `GET https://www.odwb.be/api/explore/v2.1/catalog/datasets/offres-d-emploi-forem/records`
- **Params:** `limit` (≤100), `offset`; max 3 pages, 200 records.
- Optional client `query` substring on title/employer/métier/sectors/locations.

## Payload / page structure

- Opendatasoft Explore v2.1: `{ "results": [ flat Forem offer fields ] }`.
- Fields include `numerooffreforem`, `titreoffre`, `nomemployeur`, `url`, `metier`, `secteurs`, `lieuxtravaillocalite`, `typecontrat`, `regimetravail`, `datedebutdiffusion`.

## Field map → RawJob

| RawJob | Source |
|--------|--------|
| `source_job_id` | `numerooffreforem` |
| `url` | `url` or leforem detail fallback |
| `title` | `titreoffre` |
| `company` | `nomemployeur` |
| `description` | synthetic: métier, contract, régime, secteurs (not full HTML ad) |
| `location` | localities/regions + forced `"Belgium"` suffix |
| `published_at` | `datedebutdiffusion` (date or ISO) |
| `salary_text` | `None` |
| `tags` | métier, secteurs, langues, `metiercodedimeco` |
| `job_type` | `typecontrat` |
| `remote_hint` | `regimetravail` contains télétravail/remote |
| `raw` | trimmed core fields |

## Gaps / precision risks

- Open-data row lacks long-form job description.
- Location always includes Belgium for country classification (by design).
- Sampled dump only (200 rows).

## Live sample (redacted)

```json
{
  "source_job_id": "2080441",
  "title": "Responsable qualité (H/F/X)",
  "company": "Itzu Jobs",
  "location": "…, Belgium"
}
```
