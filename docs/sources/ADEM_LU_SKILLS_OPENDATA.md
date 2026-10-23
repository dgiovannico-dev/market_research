# ADEM Luxembourg — skills in declared vacancies (open data)

**Not a job-posting ingest.** This dataset is official **skills-demand microdata** (vacancy × ESCO skill rows). It does **not** map to `RawJob` and must not be mixed into live job KPIs without explicit labeling.

| Field | Detail |
|-------|--------|
| **Country** | Luxembourg |
| **Producer** | ADEM (Agence pour le développement de l'emploi) |
| **Portal** | https://data.public.lu/en/datasets/skills-required-in-adem-job-vacancies/ |
| **License** | [Creative Commons Zero (CC0)](https://creativecommons.org/publicdomain/zero/1.0/) |
| **Update cadence** | **Quarterly** (dataset metadata); file bundles refreshed on each release (e.g. **2026-10-20**) |
| **Temporal coverage** | Vacancies transferred to ADEM **2015 → present** (split across six CSV files by two-year windows) |
| **Category (catalog)** | **E** — official labour / demand statistics (reference baseline), not category A job API |

## Download URLs (stable pattern; check portal for newest `20261020-*` paths)

| File | URL |
|------|-----|
| 2025–2026 (latest slice) | https://download.data.public.lu/resources/skills-required-in-adem-job-vacancies/20261020-090239/datasc-skills-vacancies-2025-2026.csv |
| 2023–2024 | https://download.data.public.lu/resources/skills-required-in-adem-job-vacancies/20261020-090233/datasc-skills-vacancies-2023-2024.csv |
| 2021–2022 | https://download.data.public.lu/resources/skills-required-in-adem-job-vacancies/20261020-090228/datasc-skills-vacancies-2021-2022.csv |
| 2019–2020 | https://download.data.public.lu/resources/skills-required-in-adem-job-vacancies/20261020-090223/datasc-skills-vacancies-2019-2020.csv |
| 2017–2018 | https://download.data.public.lu/resources/skills-required-in-adem-job-vacancies/20261020-090218/datasc-skills-vacancies-2017-2018.csv |
| 2015–2016 | https://download.data.public.lu/resources/skills-required-in-adem-job-vacancies/20261020-090215/datasc-skills-vacancies-2015-2016.csv |

Permalinks and MD5 checksums are listed on each resource row on the dataset page.

## Schema (CSV)

Header (verified 2026-10-21):

```text
vacancy_id,skill,skill_uri,positions,month,year,canton,occupation_code,occupation_label,nace_code,nace_label
```

- **Grain:** one row per **(vacancy_id, skill)** pair. Multiple rows share the same `vacancy_id` when several ESCO skills were inferred.
- **Empty `skill`:** algorithm found no skill keywords for that vacancy (still one row or skill-less row per portal description).
- **Skills:** ESCO preferred labels + URIs (`http://data.europa.eu/esco/skill/...`).
- **Occupation:** ROME codes/labels (Luxembourg ADEM ROME index).
- **Sector:** NACE code + label (employer-declared).
- **Time:** `month`, `year` = publication time (not “still open” snapshot date).
- **Geo:** `canton` (Luxembourg districts).
- **Volume:** `positions` = headcount advertised on that vacancy (repeat on each skill row for the same vacancy).

## Methodology and limitations

From the dataset description:

1. Employers must declare open vacancies to ADEM; data are **transferred vacancies**, not a scrape of third-party boards.
2. **Active/open ads are not published** — vacancies close after ~2 months; recent 2–3 months in each file are **incomplete**.
3. Skills are **NLP / fuzzy keyword → ESCO** (see paper *Evaluating ESCO Skill Classifiers*, DOI [10.1177/18747655251395229](https://doi.org/10.1177/18747655251395229)).
4. Public dashboard: https://skillopendata.shinyapps.io/skillopendata_dashboard/

## Why not a `RawJob` collector?

| `RawJob` field | ADEM CSV |
|----------------|----------|
| `source_job_id` | `vacancy_id` exists but is opaque, not stable across portal refreshes for live ingest |
| `url` | **Missing** — no apply link |
| `title` | **Missing** |
| `company` | **Missing** |
| `description` | **Missing** (only inferred skills) |
| `published_at` | Partial (`year`/`month` only) |
| Grain | **Skill rows**, not one record per vacancy |

**Recommendation:** treat as **LU skills-demand baseline** (counts, ESCO mix, NACE/ROME filters). Pair with live LU posting sources ([jobs.lu JobWS](GEO_RESEARCH_IT_CH_LU_DE.md#7-jobs-lu-jobws-soap--p1), EURES/ADEM jobboard, Careerjet `fr_LU`) for vacancy ingest.

## API + tooling

```bash
# CLI summary JSON from a local CSV (or --download-latest for the 2025-2026 file)
python3 backend/scripts/adem_skills_summary.py --csv /path/to/datasc-skills-vacancies-2025-2026.csv -o /tmp/adem_lu_summary.json

python3 backend/scripts/adem_skills_summary.py --download-latest -o /tmp/adem_lu_summary.json

# HTTP (reference stats only — set path; no auto-download of ~120MB)
# ADEM_CSV_PATH=/path/to/datasc-skills-vacancies-2025-2026.csv
curl -sS -H "X-API-Key: $API_KEY" \
  "http://127.0.0.1:8000/api/v1/stats/adem/skills-summary?nace_prefix=J&top_skills=25"
```

Without `ADEM_CSV_PATH`, the endpoint returns `status=not_configured` plus the portal download URL.

Output shape: distinct vacancy counts by month, top ESCO skills (by row count and position-weighted), optional NACE prefix filter (e.g. `J` for information/communication).
## Related docs

- [GEO_RESEARCH_IT_CH_LU_DE.md](GEO_RESEARCH_IT_CH_LU_DE.md) — §6 ADEM open data, jobs.lu, EURES jobboard
- [GEO_PRIORITY_P0.md](GEO_PRIORITY_P0.md) — LU P0 mix (JobWS + ADEM baseline)
