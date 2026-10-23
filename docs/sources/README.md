# Global data sources

Catalog of IT / freelance / contractor intelligence candidates (prompt categories **A–I**). Entry in the catalog does **not** mean the connector is integrated.

| Doc | Purpose |
|-----|---------|
| [ENDPOINT_PAGE_ANALYSIS.md](ENDPOINT_PAGE_ANALYSIS.md) | Workbook tracker: endpoint + Analysis status for **all** catalog sources |
| [analysis/](analysis/README.md) · [INDEX](analysis/INDEX.md) | Per-connector sheets: endpoint + RawJob field map (ACTIVE + scaffolds) |
| [analysis/candidates/](analysis/candidates/README.md) | Catalog entries **without** connector yet — access path / ToS / scrape research |
| [analysis/NEXT_CONNECTORS.md](analysis/NEXT_CONNECTORS.md) | P0/P1 shortlist of next authorized connectors from candidate research |
| [VALIDATION_REPORT.md](VALIDATION_REPORT.md) | Probe results and ACTIVE connectors |
| [COVERAGE_GAPS.md](COVERAGE_GAPS.md) | Geographic / role / source-type gaps |
| [GEO_COVERAGE_GAP.md](GEO_COVERAGE_GAP.md) | Connector-vs-region matrix (IT/CH/LU/DE focus) |
| [GEO_PRIORITY_P0.md](GEO_PRIORITY_P0.md) | Consolidated P0 shortlist + shipped checklist (keys/partner gate remains) |
| [GEO_RESEARCH_IT_CH_LU_DE.md](GEO_RESEARCH_IT_CH_LU_DE.md) | Deep research: Italy, Switzerland, Luxembourg, Germany |
| [ADEM_LU_SKILLS_OPENDATA.md](ADEM_LU_SKILLS_OPENDATA.md) | LU ADEM CC0 skills×vacancy CSV (baseline stats, not job ingest) |
| [GEO_RESEARCH_EU.md](GEO_RESEARCH_EU.md) | Deep research: rest of EU (FR/ES/BE/Nordics/CEE, …) |
| [GEO_RESEARCH_UK_US_AU.md](GEO_RESEARCH_UK_US_AU.md) | Deep research: UK, US, Australia |
| [GEO_RESEARCH_ACCESS_PATHS.md](GEO_RESEARCH_ACCESS_PATHS.md) | Access paths (EURES, BA, StepStone, CH/LU/IT, Adzuna/Jooble) |
| [ATS_TENANTS.md](ATS_TENANTS.md) | Greenhouse / Lever / Ashby / SmartRecruiters / Personio / Teamtailor / Recruitee / Pinpoint / Workable / Workday / BambooHR public tenant allowlist |
| [CREDENTIALED_CONNECTORS.md](CREDENTIALED_CONNECTORS.md) | Env keys for keyed scaffolds (Adzuna, USAJOBS, France Travail, Bundesagentur, Jooble, Findwork, Careerjet, InfoJobs; Reed is free RSS) |
| [../specs/SPEC-sources.md](../specs/SPEC-sources.md) | Verification statuses + mandatory procedure |
| [../specs/SPEC-ux-shell.md](../specs/SPEC-ux-shell.md) | Atlas IA (four nav zones), design tokens, chrome plan |
| [../superpowers/plans/2026-10-20-global-sources.md](../superpowers/plans/2026-10-20-global-sources.md) | Deliverables + expansion slices |
| [`data/sources/catalog.json`](../../data/sources/catalog.json) | Full registry (~193 + manual import) |

## Categories

| Id | Meaning |
|----|---------|
| A | Job aggregators / search APIs |
| B | Freelance / contractor marketplaces |
| C | Recruiting agencies |
| D | Public ATS board APIs |
| E | Official labour / wage statistics |
| F | Salary surveys / tech reports |
| G | FX, ISO codes, taxonomies |
| H | Public procurement |
| I | Discovery support |

## Statuses

`DISCOVERED` · `UNDER_REVIEW` · `NEEDS_CREDENTIALS` · `PENDING_ACCESS` · `VALIDATED` · `IMPLEMENTED` · `ACTIVE` · `DEGRADED` · `BLOCKED` · `DEPRECATED` · `REJECTED`

`ACTIVE` only after a connector in-repo returns real records.

## API

- `GET /api/v1/sources` — DB sources (runnable + catalog-synced)
- `GET /api/v1/sources/catalog` — full catalog JSON (`?status=&category=`)
- `GET /api/v1/sources/catalog/summary` — counts by status
- `GET /api/v1/fx/rates` — Frankfurter + ECB
- `POST /api/v1/sources/{id}/run` — run enabled collector
- `POST /api/v1/admin/seed` — sync catalog into DB

## Regenerate catalog

```bash
python3 backend/scripts/generate_source_catalog.py
```

## UI

Frontend **Sources** page: run collectors, inspect statuses. Spec: [../specs/SPEC-dashboard.md](../specs/SPEC-dashboard.md).
