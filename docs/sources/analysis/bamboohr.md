# BambooHR public careers (`bamboohr`)

| Field | Value |
|-------|-------|
| Analysis | PARTIAL_SCAFFOLD |
| collection_mode | dump |
| Collector file | `backend/app/collectors/bamboohr.py` |
| Probed_at | 2026-10-21 |
| Sample_records | max 40/slug; detail fetch capped at 15/slug |

## Endpoint

- **Method / URL template:** `GET https://{slug}.bamboohr.com/careers/list` (+ optional `/careers/{id}/detail`)
- **Auth:** none on public careers JSON
- **Env tenant list:** `BAMBOOHR_COMPANIES` (CSV; default `flyio` after local 200+jobs probe — see `docs/sources/ATS_TENANTS.md`)
- **Redirects:** **not followed** — marketing 302 ⇒ treated as missing board
- **Not used:** Open API ATS (`applicant_tracking/jobs`) — credentials / PARTNER

## Payload / page structure

- **Content-Type:** `application/json` when board exists
- **Path:** `result[]` on list; detail under `result.jobOpening`
- **List keys:** `id`, `jobOpeningName`, `departmentLabel`, `employmentStatusLabel`, `employmentType`, `location`, `isRemote`, `locationType`
- **Detail keys:** `description`, `jobOpeningShareUrl`, `datePosted`, `compensation`

## Field map → RawJob

| Source path | RawJob field | Transform / notes |
|-------------|--------------|-------------------|
| `{slug}:{id}` | source_job_id | |
| detail `jobOpeningShareUrl` else `/careers/{id}` | url | |
| `jobOpeningName` | title | |
| slug | company | |
| detail `description` | description | |
| `location.*` | location | |
| detail `datePosted` | published_at | else collect-time |
| detail `compensation` | salary_text | |
| `isRemote` / `locationType` | remote_hint | |

## Gaps / precision risks

- **Egress:** many datacenter IPs get **HTTP 503** HTML from `*.bamboohr.com`. Collector surfaces per-slug `HTTP 503` + a summary when every slug fails that way. Probe from the egress the API will use before expanding the allowlist.
- Brand guesses often **302** to marketing or return **200 with empty `result`** — neither is safe for defaults.
- Probe pass (2026-10-21, this env): `flyio` → 200 / n=10 (default); `cultureamp`/`linear`/`vercel` → 200 / n=0; most other guesses → 302.

## Local probe → set env → ACTIVE

```bash
# batch (default includes flyio; override list as needed)
BAMBOOHR_PROBE="flyio cultureamp yourslug" ./backend/scripts/probe_ats_tenants.sh | grep '^bb:'

# one-off (do not use curl -L — redirects are not careers boards)
curl -sS -o /tmp/bb.json -w "%{http_code}\n" -A "FMI-MarketIntel/1.0" -H "Accept: application/json" \
  "https://{slug}.bamboohr.com/careers/list"
python3 -c "import json; print(len(json.load(open('/tmp/bb.json')).get('result') or []))"
```

1. Keep only slugs with **HTTP 200** and **non-empty** `result`
2. Set `BAMBOOHR_COMPANIES` in `.env` (and optionally `.env.example` defaults)
3. Restart API / re-seed; `POST /api/v1/sources/{id}/run` for `bamboohr` — confirm inserts
4. Flip catalog `verification_status` to ACTIVE + regenerate catalog
