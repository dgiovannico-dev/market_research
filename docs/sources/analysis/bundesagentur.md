# Bundesagentur (`bundesagentur`)

| Field | Value |
|-------|-------|
| Analysis | PARTIAL_SCAFFOLD |
| collection_mode | search |
| Collector file | `backend/app/collectors/bundesagentur.py` |
| Credentials gate | `BUNDESAGENTUR_API_KEY` |

## Env keys

| Variable | Required | Role |
|----------|----------|------|
| `BUNDESAGENTUR_API_KEY` | yes | Header `X-API-Key` |
| `BUNDESAGENTUR_LOCATION` | no | Query `wo` (default `Berlin`) |

## Endpoint (from code)

- **Method / URL:** `GET https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v6/jobs`
- **Headers:** `X-API-Key`, `Accept: application/json`, `User-Agent: FMI-MarketIntel/1.0`
- **Query:** `was=<keyword>`, `wo=<location>`, `page=1`, `size=50`
- **Pagination:** single page in scaffold
- **Fail-closed:** missing key → error; HTTP 401/403 → auth error

## Response shape (assumed)

- **Path to job list:** `ergebnisliste` or fallback `stellenangebote`

## Field map → RawJob

| Source path | RawJob field | Transform / notes |
|-------------|--------------|-------------------|
| `referenznummer` or `refnr` | source_job_id | required |
| `externeURL` or constructed arbeitsagentur jobdetail URL | url | |
| `stellenangebotsTitel` or `titel` | title | fallback `"Untitled"` |
| `firma` or `firma.name` | company | string or dict |
| _(none)_ | description | not mapped |
| `stellenlokationen[0].adresse.ort` or `plz` | location | |
| `datumErsteVeroeffentlichung` or `aenderungsdatum` | published_at | ISO; else now UTC |
| `festgehalt` + `verguetungsangabe` | salary_text | concatenated |
| `stellenangebotsart` | job_type | |
| `homeofficemoeglich` | remote_hint | `"remote"` if truthy else `None` |
| whole item | raw | |

## Gaps

- API reuse / deployment terms not confirmed in code
- Which top-level array key the v6 API returns in production not live-verified
- No description text pulled; detail endpoint not used
- Multi-page search not implemented
