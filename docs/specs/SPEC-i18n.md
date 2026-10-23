# SPEC-i18n — Italian & English

**Status:** Accepted (MVP) — 2026-10-20  
**Date:** 2026-10-20  
**Idea:** [demand-compass-experience.md](../ideas/demand-compass-experience.md)  
**Plan:** [2026-10-20-i18n-and-visual-dashboard.md](../superpowers/plans/2026-10-20-i18n-and-visual-dashboard.md)

## 1. Goal

Ship FMI UI and assistant-facing copy in **Italian (`it`)** and **English (`en`)** so freelancers can use the Demand Compass in their preferred language without changing evidence semantics.

## 2. Non-goals

- Translating raw job titles/descriptions from sources (keep original).
- Machine-translating KPI numbers or inventing localized “market” claims.
- More than two locales in MVP.
- Backend API response localization of metric **values** (keys may stay English; UI maps labels).
- **Italian (or other) LLM/evidence narrative generation in MVP** — see §4 / acceptance notes.

## 3. Locale model

| Concern | Rule |
|---------|------|
| Supported | `it`, `en` |
| Default | `Accept-Language` → `it` if primary tag is `it`, else `en` |
| Override | User prefs `locale` (localStorage + profile API when present) |
| Document lang | `<html lang="{locale}">` |
| URL | Prefer App Router locale segment `[locale]` (`/en/…`, `/it/…`) with middleware; deep links preserve locale |
| RTL | Not required |

## 4. What is translated

### Must (MVP)

- Nav, page titles, buttons, empty states, errors, tooltips
- Guided methodology short strings + disclaimers
- Demand Compass: lens names, Market scan / My focus, crawl status lines
- Assistant brief-type chips and apply/accept labels
- Chart titles, axis labels, legend, thin-sample messages
- Prefs panel (view mode, period, locale)

### Must not invent

- Sample sizes, growth %, currencies, ISO country codes (format numbers with `Intl` per locale)
- Evidence definitions may be translated but must stay faithful to ADR-001

### LLM / MCP

- `locale` (`en`|`it`) accepted on `POST /assistant/propose` and `POST /assistant/brief`; echoed in `meta.locale`.
- **MVP limit (do not invent Italian narratives):** evidence / propose / brief **narrative prose stays English**. API always echoes `meta.narrative_locale` = `en` regardless of request `locale`. Do not invent Italian KPI numbers or translate metric values — UI chrome stays next-intl.
- Later: pass locale into LLM prompts (“Respond UI-facing prose in Italian|English; keep metric keys and numbers unchanged.”) and set `narrative_locale` accordingly.
- ReportSpec markdown body may follow locale later; grounding block stays structured.

## 5. Technical approach

- Library: **`next-intl`** (App Router) unless repo constraints forbid—document choice in plan.
- Messages: `frontend/messages/en.json`, `frontend/messages/it.json` (flat or nested by namespace: `nav`, `executive`, `compass`, `charts`, …).
- No hardcoded user-visible English in components after migration (eslint `i18n` discipline Later).
- Date/number: `Intl.DateTimeFormat` / `Intl.NumberFormat` with active locale.
- Server Components: pass locale from segment; Client: `useTranslations`.

## 6. API / prefs

| Field | Where |
|-------|--------|
| `locale: "it" \| "en"` | Dashboard prefs (localStorage key bump e.g. `fmi:dashboardPrefs:v2`) |
| Same on profile dashboard-prefs when synced | Backend already has prefs JSON—extend schema validation |

Assistant: `POST /assistant/propose` and `POST /assistant/brief` accept optional `locale` (`en`|`it`, default `en`); response includes `meta.locale` + `meta.narrative_locale` (`narrative_locale` fixed `en` in MVP).

## 7. Acceptance criteria

### Chrome / routing

- [x] Toggle IT ↔ EN updates chrome + Executive + Trends without full remount of data layer. *(AppChrome → prefs + `router.replace` locale; data hooks key on period/lens, not locale.)*
- [x] Refresh restores last locale from prefs. *(`fmi:dashboardPrefs:v2`)*
- [x] `/it` and `/en` serve correct `lang` and messages. *(`app/[locale]/layout.tsx` `html lang={locale}`; next-intl middleware)*
- [x] Chart thin-sample and empty crawler copy exist in both languages. *(`charts.*`, `compass.discoveryWarn`, explorer/jobs empty hints)*
- [x] Job list still shows original titles; surrounding UI is localized.
- [x] Message key parity `en` ↔ `it` (all namespaces, including `jobs` / `skills` / `quality` / `assistant`). *(294 leaves each, checked 2026-10-20)*
- [x] `npm run build` green with both locale entrypoints. *(prior green builds under `frontend/.next`; re-run after large UI churn)*

### Assistant locale

- [x] Frontend `ProposeSection` + `DemandCompassSection` pass `useLocale()` into propose/brief APIs.
- [x] Backend accepts `locale` `en`|`it` and echoes `meta.locale` + `meta.narrative_locale`.
- [x] **MVP:** `meta.narrative_locale` is always `en` — no Italian narrative generation. Documented in API module docstring + this SPEC.

## 8. Test plan

- Unit: message keys parity (`en` keys ⊆ `it` keys and vice versa). *(manual check 2026-10-20; CI script Later)*
- Component: locale toggle smoke.
- Manual: IT guided Executive, EN trends_only, assistant brief chips in IT (narrative body may still be EN).

## 9. Acceptance notes (2026-10-20)

| Item | Evidence |
|------|----------|
| next-intl | `frontend/middleware.ts`, `app/[locale]/…`, `messages/{en,it}.json` |
| Prefs locale | `dashboardPrefs.ts` v2 + chrome toggle |
| Assistant | `backend/app/api/v1/assistant.py` `_locale_meta`; FE `useLocale()` |
| Narrative MVP | `_NARRATIVE_LOCALE_MVP = "en"` — Italian UI chrome only |
| Residual | Some `Intl.NumberFormat("en")` call sites; ChartFrame footer uses a short EN “thin” marker; automated parity test in CI not yet wired |

**Sign-off:** MVP acceptance for SPEC-i18n is **complete** for shipped paths. Italian narrative generation remains explicitly out of MVP.
