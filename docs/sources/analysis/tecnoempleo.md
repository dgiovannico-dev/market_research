# Tecnoempleo (`tecnoempleo`)

| Field | Value |
|-------|-------|
| Analysis | DONE |
| collection_mode | feed |
| Collector file | `backend/app/collectors/tecnoempleo.py` |
| Probed_at | 2026-10-21 |
| Sample_records | 80 (RSS, `MAX_RECORDS`) |

## Endpoint

- **URL:** `GET https://www.tecnoempleo.com/alertas-empleo-rss.php`
- **Params:** optional `te` (technologies / search text).
- **Cap:** 80 items per fetch.

## Payload / page structure

- RSS `channel/item`: `title`, `link`, `description` (HTML with `<b>Label:</b> value` rows), `pubDate`, `guid`.
- Parsed labels: empresa, provincia, población, salario, tecnologías, tipo de contrato.

## Field map → RawJob

| RawJob | Source |
|--------|--------|
| `source_job_id` | `/rf-{hex}` from link/guid or path tail |
| `url` | `link` |
| `title` | `title` |
| `company` | parsed `empresa` |
| `description` | HTML-stripped full `description` |
| `location` | `provincia` or `población` or `"Spain"` |
| `published_at` | `pubDate` RFC2822 |
| `salary_text` | parsed `salario` |
| `tags` | split `tecnologías`; always prefixed `"IT"` |
| `job_type` | `tipo de contrato` |
| `remote_hint` | `"remote"` / `"hybrid"` strings from location+desc (not bool) |
| `raw` | `{title, link, mode: rss}` |

## Gaps / precision risks

- `remote_hint` type mismatch vs `RawJob` (`bool | None`); downstream may coerce oddly.
- RSS snippet may duplicate structured fields in description.
- No pagination beyond feed window.

## Live sample (redacted)

```json
{
  "source_job_id": "96751bf12257436c9347",
  "title": "Técnico/a de Soporte",
  "company": "Baoss",
  "location": "Spain",
  "job_type": "Indefinido"
}
```
