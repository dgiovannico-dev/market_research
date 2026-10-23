# Ingest health report

Generated: 2026-10-21 (local Docker stack; post agent verification wave).

## Headline (live DB after cleanup)

| Metric | Value |
|--------|------:|
| Total jobs | **408** |
| Dedup audit | **PASS** |
| Duplicate `(source_id, source_job_id)` groups | **0** |
| Duplicate `canonical_url` (canonical) groups | **0** |
| Partial unique index `uq_jobs_canonical_url_when_canonical` | Applied (`0006`) |
| `missing://` placeholders | **0** (legacy row deleted) |
| Empty URL ingest | Rejected (`ValueError("empty_url")`) — no `missing://` fallback |
| Himalayas `pubDate` | Unix epoch parsing — runs succeed without date spam |

### Jobs by connector

| Jobs | Connector |
|-----:|-----------|
| 187 | remoteok |
| 100 | jobicy |
| 40 | himalayas |
| 25 | reed |
| 24 | weworkremotely |
| 14 | working_nomads |
| 10 | remotive |
| 4 | arbeitnow |
| 4 | manual_import |

Upsert order: native `(source_id, source_job_id)` → `canonical_url` → description hash. Cross-source same URL collapses to one row (`action=duplicate`). Re-runs update in place.

## Collector parse quality (live feeds)

| Source | Format | Quality | Notes |
|--------|--------|---------|-------|
| Remotive | JSON | OK | Naive dates forced UTC |
| Remote OK | JSON | OK | Epoch + ISO date; salary min/max |
| Jobicy | JSON | OK | Cursor pages (≤2); nested tags flattened |
| Arbeitnow | JSON | OK | Multi-page (≤3) via `links.next` |
| We Work Remotely | RSS | OK | Programming category feed |
| Himalayas | JSON | OK | Epoch `pubDate` (was ISO-only → `partial`) |

## Fixes landed this wave (uncommitted)

1. **Himalayas** — epoch `pubDate` (`collectors/himalayas.py` + `tests/test_himalayas_dates.py`)
2. **Empty URL** — reject before persist (`ingestion/service.py` + dedup tests)
3. **Canonical URL uniqueness** — migration `0006_jobs_canonical_url_unique`
4. **Pagination / fields** — Arbeitnow + Jobicy pages; RemoteOK date/salary; Remotive UTC
5. **Jobicy tags** — flatten list industries/types so classify does not crash

## Residual

- Many ACTIVE connectors still have **0** insert-evidence runs (ATS tenants, keyed APIs).
- Credentialed scaffolds need keys before honest ACTIVE promote.
- See also `VALIDATION_REPORT.md` for probe tables.

## Operator notes (DSS / geo)

| Topic | Guidance |
|-------|----------|
| `evidence_tier` | Each job is `standard` or `thin` (Alembic `0007`). Capped/snapshot ingests (Job Bank, ViewJobs, …) land as **thin**; skills/rates/trends default to `min_evidence=standard`. Inventory + Quality **by_source** (`pct_thin`) still show thin rows — see [ADR-001](../decisions/ADR-001-evidence-first-kpis.md). |
| `catalog_id` vs `sources.id` | Catalog JSON uses stable `catalog_id`; Postgres `sources.id` is local. Operator `POST /sources/{id}/run` uses **DB id**. Promote with `scripts/promote_source_active.py` after insert evidence. |
| Job Bank (`jobbank_ca`) | Monthly ESDC open-data CSV — re-run ~monthly; soft-expire ages >45d; sample capped (freshest first). Evidence tier **thin**. |
| ViewJobs (`viewjobs`) | AU MCP — weekly is enough; thin titles/snippets; excluded from skills/rates when `min_evidence=standard`. |
| Dev Global Jobs | Request ISO2 tags LU/BG; attribution required; small dump. |
| Focus → Country filter | Intent `countries` only **suggest** the chrome Country filter (Focus page); never auto-force. |
| Geo country smoke | After geo connector runs, assert known `Job.country_code` share ≥ 95% via `backend/scripts/smoke_geo_country.sh` (uses `GET /api/v1/market/quality?lens=all`). Soft-SKIP when a connector has 0 jobs. Optional: `GEO_SMOKE=1` on `smoke_e2e.sh` (default off). Connectors: okemprego→PT/BR/AO, jobbank_ca→CA, viewjobs→AU, devglobaljobs→LU/BG. |
