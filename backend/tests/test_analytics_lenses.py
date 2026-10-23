"""Analytics lenses via job_intent_matches (SPEC §3.3)."""

from datetime import datetime, timezone

import pytest

from app.analytics.lenses import (
    compare_counts,
    job_ids_for_lens,
    parse_lens,
    parse_query_ids,
    resolve_lens_job_ids,
)
from app.analytics.jobs_list import list_jobs
from app.storage.db import SessionLocal
from app.storage.models import Job, JobIntentMatch, SearchQuery, Source


@pytest.fixture()
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


def _source(db, suffix: str) -> Source:
    src = Source(
        name=f"lens_src_{suffix}_{datetime.now(timezone.utc).timestamp()}",
        source_type="api",
        connector_type="remotive",
        connector_status="enabled",
        enabled=True,
    )
    db.add(src)
    db.flush()
    return src


def _job(db, source: Source, *, slug: str) -> Job:
    job = Job(
        source_id=source.id,
        source_job_id=slug,
        canonical_url=f"https://example.com/jobs/{slug}-{datetime.now(timezone.utc).timestamp()}",
        title_original=f"Role {slug}",
        company_original="Acme",
        country_code="IT",
        published_at=datetime.now(timezone.utc),
        is_canonical=True,
    )
    db.add(job)
    db.flush()
    return job


def _intent(db, *, kind: str, name: str, enabled: bool = True) -> SearchQuery:
    row = SearchQuery(
        name=f"{name}_{datetime.now(timezone.utc).timestamp()}",
        query_text=name,
        kind=kind,
        origin="seed_discovery" if kind == "discovery" else "user",
        enabled=enabled,
    )
    db.add(row)
    db.flush()
    return row


def _match(db, job: Job, intent: SearchQuery) -> JobIntentMatch:
    m = JobIntentMatch(job_id=job.id, query_id=intent.id)
    db.add(m)
    db.flush()
    return m


def test_focus_only_excluded_from_market_dual_match_in_both(db):
    src = _source(db, "dual")
    discovery = _intent(db, kind="discovery", name="disc")
    focus = _intent(db, kind="focus", name="focus")

    unlabeled = _job(db, src, slug="unlabeled")
    discovery_only = _job(db, src, slug="disc_only")
    focus_only = _job(db, src, slug="focus_only")
    dual = _job(db, src, slug="dual")

    _match(db, discovery_only, discovery)
    _match(db, focus_only, focus)
    _match(db, dual, discovery)
    _match(db, dual, focus)

    market = job_ids_for_lens(db, lens="market")
    focus_ids = job_ids_for_lens(db, lens="focus")
    compare = job_ids_for_lens(db, lens="compare", query_ids=[focus.id])

    assert isinstance(market, set)
    assert isinstance(focus_ids, set)
    assert isinstance(compare, dict)

    assert unlabeled.id in market
    assert discovery_only.id in market
    assert dual.id in market
    assert focus_only.id not in market

    assert focus_only.id in focus_ids
    assert dual.id in focus_ids
    assert unlabeled.id not in focus_ids
    assert discovery_only.id not in focus_ids

    assert dual.id in compare["market"] and dual.id in compare["focus"]
    assert focus_only.id in compare["focus"] and focus_only.id not in compare["market"]

    counts = compare_counts(db, query_ids=[focus.id])
    assert set(counts) == {"market_n", "focus_n", "overlap_n"}
    assert dual.id in (compare["market"] & compare["focus"])
    assert counts["overlap_n"] == len(compare["market"] & compare["focus"])


def test_parse_lens_none_means_unfiltered():
    """API omit/blank/all → no lens filter (all jobs); explicit market when requested."""
    assert parse_lens(None) is None
    assert parse_lens("") is None
    assert parse_lens("all") is None
    assert parse_lens("market") == "market"
    assert parse_lens("FOCUS") == "focus"
    assert parse_lens("compare") == "compare"
    assert parse_query_ids("1,2") == [1, 2]
    assert parse_query_ids(["3", "4,5"]) == [3, 4, 5]
    assert parse_query_ids(None) is None
    assert parse_query_ids("  ,  ") is None
    with pytest.raises(ValueError, match="Unknown lens"):
        parse_lens("orbit")


def test_focus_query_ids_filter(db):
    src = _source(db, "qids")
    f1 = _intent(db, kind="focus", name="f1")
    f2 = _intent(db, kind="focus", name="f2")
    j1 = _job(db, src, slug="j1")
    j2 = _job(db, src, slug="j2")
    _match(db, j1, f1)
    _match(db, j2, f2)

    only_f1 = job_ids_for_lens(db, lens="focus", query_ids=[f1.id])
    assert isinstance(only_f1, set)
    assert j1.id in only_f1
    assert j2.id not in only_f1


def test_resolve_lens_job_ids_unfiltered_and_union(db):
    src = _source(db, "resolve")
    discovery = _intent(db, kind="discovery", name="disc_r")
    focus = _intent(db, kind="focus", name="focus_r")
    unlabeled = _job(db, src, slug="unlab_r")
    focus_only = _job(db, src, slug="focus_r")
    _match(db, focus_only, focus)
    disc_job = _job(db, src, slug="disc_r")
    _match(db, disc_job, discovery)

    assert resolve_lens_job_ids(db, lens=None) is None
    assert resolve_lens_job_ids(db, lens="all") is None

    market = resolve_lens_job_ids(db, lens="market")
    assert isinstance(market, set)
    assert unlabeled.id in market
    assert disc_job.id in market
    assert focus_only.id not in market

    focus_ids = resolve_lens_job_ids(db, lens="focus", query_ids=[focus.id])
    assert isinstance(focus_ids, set)
    assert focus_only.id in focus_ids
    assert unlabeled.id not in focus_ids

    compare = resolve_lens_job_ids(db, lens="compare", query_ids=[focus.id])
    assert isinstance(compare, set)
    assert unlabeled.id in compare
    assert focus_only.id in compare
    assert disc_job.id in compare


def test_disabled_focus_excluded_unless_query_ids(db):
    src = _source(db, "disabled")
    enabled = _intent(db, kind="focus", name="en_f", enabled=True)
    disabled = _intent(db, kind="focus", name="dis_f", enabled=False)
    j_en = _job(db, src, slug="en_j")
    j_dis = _job(db, src, slug="dis_j")
    _match(db, j_en, enabled)
    _match(db, j_dis, disabled)

    default_focus = job_ids_for_lens(db, lens="focus")
    assert isinstance(default_focus, set)
    assert j_en.id in default_focus
    assert j_dis.id not in default_focus

    explicit = job_ids_for_lens(db, lens="focus", query_ids=[disabled.id])
    assert isinstance(explicit, set)
    assert j_dis.id in explicit


def test_list_jobs_item_includes_evidence_tier(db):
    src = _source(db, "tier")
    job = _job(db, src, slug="tiered")
    job.evidence_tier = "thin"
    db.flush()

    page = list_jobs(db, skip=0, limit=50, lens="market")
    by_id = {item["id"]: item for item in page["items"]}
    assert by_id[job.id]["evidence_tier"] == "thin"


def test_list_jobs_compare_shape(db):
    """Market jobs list with lens=compare includes overlap counts."""
    page = list_jobs(db, skip=0, limit=5, lens="compare")
    assert page["lens"] == "compare"
    assert page["skip"] == 0
    assert page["limit"] == 5
    assert isinstance(page["total"], int)
    assert isinstance(page["items"], list)
    assert set(page) >= {
        "total",
        "skip",
        "limit",
        "lens",
        "query_ids",
        "items",
        "market_n",
        "focus_n",
        "overlap_n",
    }
    assert page["market_n"] >= 0
    assert page["focus_n"] >= 0
    assert page["overlap_n"] >= 0
    assert page["overlap_n"] <= min(page["market_n"], page["focus_n"])


def test_dashboard_summary_compare_lifts_data_quality(db):
    """Compare wrapper must expose top-level data_quality for executive UI."""
    from app.analytics import kpis

    out = kpis.dashboard_summary(db, days=30, lens="compare", query_ids=[])
    assert out["lens"] == "compare"
    assert isinstance(out.get("data_quality"), dict)
    assert "last_source_success_at" in out["data_quality"]
    assert "sources_total" in out["data_quality"]
    assert out.get("period_days") == 30
    assert isinstance(out.get("kpis"), list)
    assert out.get("growth_status") is not None
    assert isinstance(out.get("top_technologies"), list)
    assert isinstance(out.get("top_countries"), list)
    assert isinstance(out.get("market"), dict)
    assert isinstance(out.get("focus"), dict)


def test_technology_trends_compare_lifts_period_and_evidence(db):
    """Compare wrapper must expose period_days / excluded_thin_n at top level."""
    from app.analytics import kpis

    out = kpis.technology_trends(db, days=90, lens="compare", query_ids=[])
    assert out["lens"] == "compare"
    assert out.get("period_days") == 90
    assert "min_support" in out
    assert "excluded_thin_n" in out
    assert isinstance(out.get("market"), dict)
    assert isinstance(out.get("focus"), dict)
    assert "items" in out["market"]
    assert "items" in out["focus"]


def test_country_comparison_compare_lifts_disclaimer(db):
    """Compare wrapper must expose disclaimer / period_days at top level."""
    from app.analytics.countries import country_comparison

    out = country_comparison(db, days=90, lens="compare", query_ids=[])
    assert out["lens"] == "compare"
    assert out.get("period_days") == 90
    assert isinstance(out.get("disclaimer"), str)
    assert isinstance(out.get("coverage_notes"), list)
    assert isinstance(out.get("market"), dict)
    assert isinstance(out.get("focus"), dict)
