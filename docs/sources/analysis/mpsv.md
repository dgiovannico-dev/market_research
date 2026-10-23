# MPSV Volná místa (`mpsv`)

| Field | Value |
|-------|-------|
| Analysis | DONE |
| collection_mode | dump |
| Collector file | `backend/app/collectors/mpsv.py` (+ `mpsv_stream.py`) |
| Probed_at | 2026-10-21 |
| Sample_records | 300 (`MAX_RECORDS`, IT keyword filter, JSON-LD stream) |

## Endpoint

- **Primary (often 404):** `https://data.mpsv.cz/od/soubory/volna-mista/volna-mista.json`
- **Live dump:** streamed `volna-mista.jsonld` (~180MB), `polozky` items via incremental parser.
- **Caps:** `MAX_RECORDS=300`, `MAX_SCAN=12000`, `MAX_BYTES=40MB` read budget.
- Blank query → `DEFAULT_IT_KEYWORDS` Czech/EN IT terms; custom query → space-split terms.

## Payload / page structure

- JSON-LD job objects: `portalId`, `referencniCislo`, `pozadovanaProfese` (cs), `zamestnavatel`, `mistoVykonuPrace`, `mesicniMzdaOd/Do`, `datumVlozeni`, `profeseCzIsco`, `upresnujiciInformace`, `urlAdresa`.

## Field map → RawJob

| RawJob | Source |
|--------|--------|
| `source_job_id` | `portalId` or `referencniCislo` or `id` |
| `url` | `urlAdresa` or `https://data.mpsv.cz/zdroj/{id}` |
| `title` | `pozadovanaProfese.cs` |
| `company` | `zamestnavatel.nazev` |
| `description` | `upresnujiciInformace.cs` (max 4000) |
| `location` | `mistoVykonuPrace.adresaText` or workplace name; default `"Czechia"` |
| `published_at` | `datumVlozeni` or `datumZmeny` |
| `salary_text` | monthly CZK range |
| `tags` | ISCO id + profession title |
| `job_type` | `None` |
| `remote_hint` | keyword scan home office / remote in haystack |
| `raw` | trimmed portal/salary/location fields |

## Gaps / precision risks

- Heavily filtered sample, not national complete dump (`dump_complete` false).
- Stream may stop at byte/scan caps with `scan_cap` error note.
- Compact JSON path documented but unavailable (404/HTML).

## Live sample (redacted)

```json
{
  "source_job_id": "67304060",
  "title": "Vedoucí Oddělení správy Základního modelu…",
  "company": "Zeměměřický úřad",
  "salary_text": "… CZK"
}
```
