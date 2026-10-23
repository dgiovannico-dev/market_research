# Demand Compass — operator walkthrough

Ops sign-off for [SPEC-research-intents](../specs/SPEC-research-intents.md) §11 (UI path). Automatable checks: `backend/scripts/smoke_compass.sh`.

**Prereqs:** Compose stack healthy (`GET /readyz`, frontend up). Prefer English UI paths below (`/it/…` works the same). Discovery seeded from `data/research/discovery_watchlist.json` (enable ≥1 discovery intent if Market is empty).

---

## 1. Market lens

1. Open `/en` (Executive) or `/en/trends`.
2. Set **Lens** → **Market** (`?lens=market`).
3. Confirm rising/cooling (or KPIs) with observed `n=` — empty charts mean “run crawlers / seed discovery”, not invent data.
4. Optional: `/en/market-scan` — enable/disable discovery intents; warn if few enabled.
5. Optional: `/en/explorer` — DB search; **Refresh from sources** only if you need one query now (daily cron is the primary pipeline).

## 2. Focus intents

1. Open `/en/focus`.
2. Create a focus intent (name + query text) and leave it **enabled**.
3. **Sync now** on that intent (or wait for the next daily tick) so new crawl hits upsert `job_intent_matches`.
4. If Focus still shows `total=0` (corpus filled by dump/feed, or sync has not written matches yet), rematch existing jobs without crawling:

   ```bash
   docker compose exec -T api python scripts/rematch_focus_intents.py
   # dry-run: docker compose exec -T api python scripts/rematch_focus_intents.py --dry-run
   ```

   Optional broader provenance backfill (`kind=all` keeps discovery matches on dump jobs in the **market** lens; focus-only matches are excluded from market):

   ```bash
   curl -sf -X POST -H "X-API-Key: $API_KEY" \
     "${API_URL:-http://127.0.0.1:8000}/api/v1/research/matches/backfill?kind=all"
   # or: docker compose exec api python scripts/backfill_intent_matches.py --kind all
   ```

5. Explorer / Jobs with lens **Focus** should show jobs matched to that intent (`job_intent_matches`).

## 3. Compare lens

1. On Executive or Trends, set **Lens** → **Compare** (`?lens=compare`).
2. Confirm market vs focus pairing (dual charts / dual metrics) — compare does not redefine market as the niche focus alone.
3. On `/en/assistant`, run brief **Focus vs market** (forces compare).

## 4. Assistant suggest → accept watch

1. Open `/en/assistant` (`DemandCompassSection`).
2. Lens **Market** → chip **Suggest watches**.
3. Confirm candidates appear; intent list count must **not** grow until accept.
4. **Accept** one candidate → intent appears under Focus (or discovery if kind says so).
5. Optional: other chips (`rising_cooling`, `where_demand`, `adjacent`) for evidence coaching; disclose thin `n=`.

---

## Automation (optional)

```bash
# API up; optional API_KEY=
API_URL=http://127.0.0.1:8000 ./backend/scripts/smoke_compass.sh

# Also POST /research/watches/accept then soft-DELETE the created intent:
COMPASS_ACCEPT_WATCH=1 API_URL=http://127.0.0.1:8000 ./backend/scripts/smoke_compass.sh

# Geo connector Job.country_code DSS (Plan D) — soft-SKIP if zero rows:
API_URL=http://127.0.0.1:8000 ./backend/scripts/smoke_geo_country.sh
# or via e2e: GEO_SMOKE=1 ./backend/scripts/smoke_e2e.sh

# Force daily crawlers (bypass UTC-day idempotency):
curl -sf -X POST -H "X-API-Key: $API_KEY" \
  "${API_URL:-http://127.0.0.1:8000}/api/v1/scheduler/run?force=true"
```

Cron (production): `backend/scripts/scheduler_tick.sh` — see [PRODUCTION.md](../PRODUCTION.md).

## Pass criteria

| Step | Pass |
|------|------|
| Market | Signals or honest empty + discovery enabled |
| Focus | Intent created/enabled; matches after sync |
| Compare | Paired market/focus metrics |
| Accept watch | Persist only after Accept; smoke with `COMPASS_ACCEPT_WATCH=1` OK |

Related: [SPEC-research-intents](../specs/SPEC-research-intents.md) · [ADR-007](../decisions/ADR-007-query-first-sync.md) · [plan](../superpowers/plans/2026-10-20-query-first-daily-sync.md)
