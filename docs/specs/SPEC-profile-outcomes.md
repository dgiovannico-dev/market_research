# Spec: profile-outcomes

## Objective

Let the persona maintain a skill/profile snapshot, track applications/outcomes, evaluate alert rules, and generate a weekly JSON report—used primarily in **guided** mode.

## In scope

- Profile CRUD (skills, positioning fields as implemented).
- Skill-gap vs observed demand.
- Positioning recommendations.
- Applications create/list with outcomes.
- Alert rules list + `POST /api/v1/alerts/evaluate`.
- Weekly report `GET /api/v1/reports/weekly`.

## Out of scope

- Full ATS / email sync.
- PDF export (Later).
- Showing recommendations in `trends_only` mode (dashboard suppresses them).

## Acceptance criteria

- [ ] Profile and skill-gaps endpoints return 200 with structured gaps.
- [ ] Application can be created from UI and listed.
- [ ] Alert evaluate returns fired evidence without crashing on empty rules.
- [ ] Weekly report includes observed KPI snippets and top gaps (JSON).
- [ ] Guided UI surfaces these; trends-only does not push recommendation panels.

## Key paths

- `backend/app/api/v1/profile_apps.py`
- `backend/app/analytics/positioning.py`
- `backend/app/analytics/outcomes.py`
- `backend/app/reports/weekly.py`
- `backend/app/scheduler/runner.py` (alert evaluation)
- `frontend/app/profile/`, `applications/`, `alerts/`, `report/`
