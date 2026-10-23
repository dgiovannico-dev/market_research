# Per-source endpoint & payload analysis

One file per `connector_key`: `{key}.md`. These sheets are the detailed fill-in for [ENDPOINT_PAGE_ANALYSIS.md](../ENDPOINT_PAGE_ANALYSIS.md) (tracker stays in the workbook; schema/field maps live here to avoid sprawl).

| Analysis value | Meaning |
|----------------|---------|
| `DONE` | Live or code-verified endpoint + payload keys + RawJob map |
| `PARTIAL_SCAFFOLD` | Keyed connector; map from code only (no live keyed probe) |
| `TODO` | Not started |

## Regenerate workbook links

After adding/updating sheets:

```bash
python3 backend/scripts/generate_endpoint_page_analysis.py
```

The generator marks tracker **Analysis** as `DONE` when `docs/sources/analysis/{key}.md` exists and contains `| Analysis | DONE |`.

## Fill order

1. ACTIVE free job collectors  
2. Credentialed scaffolds (`PARTIAL_SCAFFOLD`)  
3. UNDER_REVIEW only when prioritizing a new connector  

## Index

See [INDEX.md](INDEX.md) for all sheets and Analysis status.

Hand-deepened (live + narrative): all **43** ACTIVE free job sheets now include live probe notes (batches remote/ATS/EU/APAC). Credentialed remain `PARTIAL_SCAFFOLD` until keyed ingest.
## Candidates (no connector)

Sheets for catalog entries without a wired collector: [`candidates/`](candidates/README.md) · [`candidates/INDEX.md`](candidates/INDEX.md).
