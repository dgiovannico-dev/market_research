# Canada Job Bank (`jobbank_ca`)

| Field | Value |
|-------|-------|
| Analysis | DONE |
| collection_mode | dump |
| Collector file | `backend/app/collectors/jobbank_ca.py` |
| Probed_at | 2026-10-21 |
| Sample_records | 200 (live collect, query `software`) |

## Endpoint

- **Step 1:** `GET https://open.canada.ca/data/api/3/action/package_show?id=ea639e28-c0fc-48bf-b5dd-b8899bd43072` (CKAN)
- **Step 2:** `GET` latest English **all-job-postings** TSV resource URL from `result.resources[]`
- **Auth:** none (Open Government Licence — Canada)
- **Encoding:** UTF-16 tab-separated CSV; download capped at `MAX_BYTES=55_000_000`
- **Output cap:** `MAX_RECORDS=200` IT rows after sort by `First Posting Date`

## Payload / page structure

- **Not HTML:** monthly open-data dump (WIC snapshot rows)
- **Key columns:** `WIC Job Location Snapshot ID`, `Job Title`, `City`, `Province/Territory`, `First Posting Date`, `Salary Minimum|Maximum|Per`, `NOC21 Code`, `NOC21 Code Name`, `Employment Type`, `Employment Term`, `Employment Term Telework`, `Official Language`
- **Row filter:** `_is_it_row` — NOC prefixes (212*, 2222, 20012, 21311) or IT keyword blob match + optional query

## Field map → RawJob

| Source path | RawJob field | Transform / notes |
|-------------|--------------|-------------------|
| `WIC Job Location Snapshot ID` | source_job_id | required |
| _(built)_ | url | Job Bank **search deep-link** + `fmi_snap={snap}` (live `/jobposting/{id}` often 410) |
| `Job Title` | title | |
| _(none)_ | company | always `None` (open data has no employer name) |
| synthetic | description | `{NOC name} — {title} ({prov}; snap {id})` for dedup |
| City + Province + `CA` | location | |
| `First Posting Date` | published_at | `%Y/%m/%d` or `%Y-%m-%d` |
| salary columns | salary_text | `{lo}-{hi} CAD/{per}` |
| NOC, employment fields | tags | max 10 |
| `Employment Type` | job_type | skip `NA` |
| `Employment Term Telework` | remote_hint | yes→True, no→False |
| metadata dict | raw | country CA, evidence_tier thin, noc21, licence OGL |

## Gaps / precision risks

- Sampled IT subset only; not full Job Bank corpus
- No employer; canonical URL is search link, not posting page
- Monthly snapshot lag vs live site
- `dump_complete` default false (capped ingest)

## Live sample (redacted)

```json
{
  "WIC Job Location Snapshot ID": "15919248",
  "Job Title": "software developer",
  "City": "Dartmouth",
  "Province/Territory": "Nova Scotia",
  "First Posting Date": "2026/09/30",
  "Salary Minimum": "110000",
  "Salary Maximum": "130000",
  "Salary Per": "Year",
  "NOC21 Code": "21232"
}
```
