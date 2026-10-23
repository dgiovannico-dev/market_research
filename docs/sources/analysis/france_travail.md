# France Travail (`france_travail`)

| Field | Value |
|-------|-------|
| Analysis | PARTIAL_SCAFFOLD |
| collection_mode | search |
| Collector file | `backend/app/collectors/france_travail.py` |
| Credentials gate | `FRANCE_TRAVAIL_CLIENT_ID` + `FRANCE_TRAVAIL_CLIENT_SECRET` |

## Env keys

| Variable | Required | Role |
|----------|----------|------|
| `FRANCE_TRAVAIL_CLIENT_ID` | yes | OAuth2 `client_id` |
| `FRANCE_TRAVAIL_CLIENT_SECRET` | yes | OAuth2 `client_secret` |
| `FRANCE_TRAVAIL_SCOPE` | no | Token scope (default `api_offresdemploiv2 o2dsoffre`) |

## Endpoints (from code)

1. **Token:** `POST https://entreprise.francetravail.fr/connexion/oauth2/access_token?realm=%2Fpartenaire`
   - Body (form): `grant_type=client_credentials`, `client_id`, `client_secret`, `scope`
2. **Search:** `GET https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search`
   - Header: `Authorization: Bearer <access_token>`
   - Query: `motsCles`, `codeROME` (fixed IT codes M1805/M1802/M1806), `range=start-end` (page size 50, max 2 pages)
   - Pagination hint: `Content-Range` header total via `parse_content_range_total`

## Response shape (assumed)

- **Path to job list:** `resultats[]`

## Field map → RawJob

| Source path | RawJob field | Transform / notes |
|-------------|--------------|-------------------|
| `id` | source_job_id | required |
| `origineOffre.urlOrigine` or `url` | url | |
| `intitule` | title | fallback `"Untitled"` |
| `entreprise.nom` | company | |
| `description` | description | |
| `lieuTravail.libelle` | location | |
| `dateCreation` or `dateActualisation` | published_at | ISO; else now UTC |
| `salaire.libelle` | salary_text | |
| `typeContrat` | job_type | |
| _(none)_ | remote_hint | always `None` |
| whole item | raw | |

## Gaps

- Emploi Store / Offres v2 subscription and scope strings not verified without credentials
- IT `codeROME` filter biases results; non-IT queries not represented
- Token expiry and refresh not implemented (single token per collect)
- Live `Content-Range` format and empty-result edge cases unverified
