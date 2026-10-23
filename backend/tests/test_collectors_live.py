"""Live connector smoke tests — skip if network/API unavailable."""

from __future__ import annotations

import pytest

from app.collectors.arbetsformedlingen import ArbetsformedlingenCollector
from app.collectors.ats_boards import GreenhouseCollector, LeverCollector
from app.collectors.himalayas import HimalayasCollector
from app.collectors.hn_whoishiring import HnWhoIsHiringCollector
from app.collectors.devitjobs import DevITJobsCollector
from app.collectors.getonbrd import GetOnBoardCollector
from app.collectors.jobicy import JobicyCollector
from app.collectors.authentic_jobs import AuthenticJobsCollector
from app.collectors.dou_ua import DouUaCollector
from app.collectors.duunitori import DuunitoriCollector
from app.collectors.hasjob import HasjobCollector
from app.collectors.helloworld_rs import HelloworldRsCollector
from app.collectors.instahyre import InstahyreCollector
from app.collectors.jobindex import JobindexCollector
from app.collectors.jobup import JobUpCollector
from app.collectors.jobweb_kenya import JobwebKenyaCollector
from app.collectors.kalibrr import KalibrrCollector
from app.collectors.landing_jobs import LandingJobsCollector
from app.collectors.mycareersfuture import MyCareersFutureCollector
from app.collectors.nav_arbeidsplassen import NavArbeidsplassenCollector
from app.collectors.nav_stilling_feed import NavStillingFeedCollector
from app.collectors.nofluffjobs import NoFluffJobsCollector
from app.collectors.posao_hr import PosaoHrCollector
from app.collectors.reed import ReedCollector
from app.collectors.pinpoint import PinpointCollector
from app.collectors.recruitee import RecruiteeCollector
from app.collectors.teamtailor import TeamtailorCollector
from app.collectors.workable import WorkableCollector
from app.collectors.workday import WorkdayCollector
from app.collectors.findmethatdamjob import FindMeThatDamJobCollector
from app.collectors.tecnoempleo import TecnoempleoCollector
from app.collectors.wanted import WantedCollector
from app.collectors.wantedly import WantedlyCollector
from app.collectors.remoteok import RemoteOKCollector
from app.collectors.smartrecruiters import SmartRecruitersCollector
from app.collectors.remotive import RemotiveCollector
from app.collectors.themuse import TheMuseCollector
from app.collectors.weworkremotely import WeWorkRemotelyCollector
from app.collectors.working_nomads import WorkingNomadsCollector
from app.fx.rates import fetch_frankfurter_rates
from app.sources.catalog import catalog_summary, load_catalog


@pytest.mark.asyncio
async def test_remotive_live():
    result = await RemotiveCollector().collect()
    if result.errors and not result.records:
        pytest.skip(f"remotive unavailable: {result.errors}")
    assert len(result.records) >= 1
    assert result.records[0].source_job_id


@pytest.mark.asyncio
async def test_remoteok_live():
    result = await RemoteOKCollector().collect()
    if result.errors and not result.records:
        pytest.skip(f"remoteok unavailable: {result.errors}")
    assert len(result.records) >= 1


@pytest.mark.asyncio
async def test_working_nomads_live():
    result = await WorkingNomadsCollector().collect()
    if result.errors and not result.records:
        pytest.skip(f"working_nomads unavailable: {result.errors}")
    assert len(result.records) >= 1


@pytest.mark.asyncio
async def test_weworkremotely_live():
    result = await WeWorkRemotelyCollector().collect()
    if result.errors and not result.records:
        pytest.skip(f"wwr unavailable: {result.errors}")
    assert len(result.records) >= 1


@pytest.mark.asyncio
async def test_themuse_live():
    result = await TheMuseCollector().collect()
    if result.errors and not result.records:
        pytest.skip(f"themuse unavailable: {result.errors}")
    assert len(result.records) >= 1


@pytest.mark.asyncio
async def test_greenhouse_airbnb_live():
    result = await GreenhouseCollector().collect()
    if result.errors and not result.records:
        pytest.skip(f"greenhouse unavailable: {result.errors}")
    assert len(result.records) >= 1


@pytest.mark.asyncio
async def test_lever_spotify_live():
    result = await LeverCollector().collect()
    if result.errors and not result.records:
        pytest.skip(f"lever unavailable: {result.errors}")
    assert len(result.records) >= 1


@pytest.mark.asyncio
async def test_teamtailor_live():
    result = await TeamtailorCollector().collect()
    if result.errors and not result.records:
        pytest.skip(f"teamtailor unavailable: {result.errors}")
    assert len(result.records) >= 1
    assert result.records[0].source_job_id
    assert result.records[0].url


@pytest.mark.asyncio
async def test_recruitee_live():
    result = await RecruiteeCollector().collect()
    if result.errors and not result.records:
        pytest.skip(f"recruitee unavailable: {result.errors}")
    assert len(result.records) >= 1
    assert result.records[0].source_job_id
    assert result.records[0].url


@pytest.mark.asyncio
async def test_pinpoint_live():
    result = await PinpointCollector().collect()
    if result.errors and not result.records:
        pytest.skip(f"pinpoint unavailable: {result.errors}")
    assert len(result.records) >= 1
    assert result.records[0].source_job_id
    assert result.records[0].url


@pytest.mark.asyncio
async def test_workable_live():
    result = await WorkableCollector().collect()
    if result.errors and not result.records:
        pytest.skip(f"workable unavailable: {result.errors}")
    assert len(result.records) >= 1
    assert result.records[0].source_job_id
    assert result.records[0].url


@pytest.mark.asyncio
async def test_workday_live():
    result = await WorkdayCollector().collect()
    if result.errors and not result.records:
        pytest.skip(f"workday unavailable: {result.errors}")
    assert len(result.records) >= 1
    assert result.records[0].source_job_id
    assert result.records[0].url
    assert "myworkdayjobs.com" in result.records[0].url


@pytest.mark.asyncio
async def test_arbetsformedlingen_live():
    result = await ArbetsformedlingenCollector().collect("software")
    if result.errors and not result.records:
        pytest.skip(f"arbetsformedlingen unavailable: {result.errors}")
    assert len(result.records) >= 1
    assert result.records[0].source_job_id
    assert result.records[0].url


@pytest.mark.asyncio
async def test_jobicy_live():
    result = await JobicyCollector().collect("software")
    if result.errors and not result.records:
        pytest.skip(f"jobicy unavailable: {result.errors}")
    assert len(result.records) >= 1
    assert result.records[0].url


@pytest.mark.asyncio
async def test_himalayas_live():
    result = await HimalayasCollector().collect()
    if result.errors and not result.records:
        pytest.skip(f"himalayas unavailable: {result.errors}")
    assert len(result.records) >= 1


@pytest.mark.asyncio
async def test_hn_whoishiring_live():
    result = await HnWhoIsHiringCollector().collect()
    if result.errors and not result.records:
        pytest.skip(f"hn_whoishiring unavailable: {result.errors}")
    assert len(result.records) >= 1
    assert "ycombinator.com" in result.records[0].url or "news.ycombinator.com" in result.records[0].url


@pytest.mark.asyncio
async def test_smartrecruiters_live():
    result = await SmartRecruitersCollector().collect()
    if result.errors and not result.records:
        pytest.skip(f"smartrecruiters unavailable: {result.errors}")
    assert len(result.records) >= 1


@pytest.mark.asyncio
async def test_devitjobs_live():
    result = await DevITJobsCollector().collect("java")
    if result.errors and not result.records:
        pytest.skip(f"devitjobs unavailable: {result.errors}")
    assert len(result.records) >= 1
    assert "devitjobs." in result.records[0].url


@pytest.mark.asyncio
async def test_nofluffjobs_live():
    result = await NoFluffJobsCollector().collect("java")
    if result.errors and not result.records:
        pytest.skip(f"nofluffjobs unavailable: {result.errors}")
    assert len(result.records) >= 1
    assert "nofluffjobs.com" in result.records[0].url


@pytest.mark.asyncio
async def test_reed_rss_live():
    result = await ReedCollector().collect("java")
    if result.errors and not result.records:
        pytest.skip(f"reed rss unavailable: {result.errors}")
    assert len(result.records) >= 1
    assert "reed.co.uk" in result.records[0].url


@pytest.mark.asyncio
async def test_getonbrd_live():
    result = await GetOnBoardCollector().collect("java")
    if result.errors and not result.records:
        pytest.skip(f"getonbrd unavailable: {result.errors}")
    assert len(result.records) >= 1
    assert "getonbrd.com" in result.records[0].url


@pytest.mark.asyncio
async def test_mycareersfuture_live():
    result = await MyCareersFutureCollector().collect("java")
    if result.errors and not result.records:
        pytest.skip(f"mycareersfuture unavailable: {result.errors}")
    assert len(result.records) >= 1
    assert "mycareersfuture.gov.sg" in result.records[0].url


@pytest.mark.asyncio
async def test_jobup_live():
    result = await JobUpCollector().collect("java developer")
    if result.errors and not result.records:
        pytest.skip(f"jobup unavailable: {result.errors}")
    assert len(result.records) >= 1
    assert "jobup.ch" in result.records[0].url


@pytest.mark.asyncio
async def test_nav_arbeidsplassen_live():
    result = await NavArbeidsplassenCollector().collect("java")
    if result.errors and not result.records:
        pytest.skip(f"nav_arbeidsplassen unavailable: {result.errors}")
    assert len(result.records) >= 1
    assert "arbeidsplassen.nav.no" in result.records[0].url


@pytest.mark.asyncio
async def test_nav_stilling_feed_live():
    result = await NavStillingFeedCollector().collect(None)
    if result.errors and not result.records:
        pytest.skip(f"nav_stilling_feed unavailable: {result.errors}")
    assert len(result.records) >= 1
    assert "arbeidsplassen.nav.no" in result.records[0].url
    assert result.dump_complete is False


@pytest.mark.asyncio
async def test_landing_jobs_live():
    result = await LandingJobsCollector().collect("java")
    if result.errors and not result.records:
        pytest.skip(f"landing_jobs unavailable: {result.errors}")
    assert len(result.records) >= 1
    assert "landing.jobs" in result.records[0].url


@pytest.mark.asyncio
async def test_kalibrr_live():
    result = await KalibrrCollector().collect("java")
    if result.errors and not result.records:
        pytest.skip(f"kalibrr unavailable: {result.errors}")
    assert len(result.records) >= 1
    assert "kalibrr.com" in result.records[0].url


@pytest.mark.asyncio
async def test_dou_ua_live():
    result = await DouUaCollector().collect()
    if result.errors and not result.records:
        pytest.skip(f"dou_ua unavailable: {result.errors}")
    assert len(result.records) >= 1
    assert "dou.ua" in result.records[0].url


@pytest.mark.asyncio
async def test_authentic_jobs_live():
    result = await AuthenticJobsCollector().collect()
    if result.errors and not result.records:
        pytest.skip(f"authentic_jobs unavailable: {result.errors}")
    assert len(result.records) >= 1
    assert "authenticjobs.com" in result.records[0].url


@pytest.mark.asyncio
async def test_wantedly_live():
    result = await WantedlyCollector().collect("java")
    if result.errors and not result.records:
        pytest.skip(f"wantedly unavailable: {result.errors}")
    assert len(result.records) >= 1
    assert "wantedly.com" in result.records[0].url


@pytest.mark.asyncio
async def test_duunitori_live():
    result = await DuunitoriCollector().collect("java")
    if result.errors and not result.records:
        pytest.skip(f"duunitori unavailable: {result.errors}")
    assert len(result.records) >= 1
    assert "duunitori.fi" in result.records[0].url


@pytest.mark.asyncio
async def test_jobindex_live():
    result = await JobindexCollector().collect("java")
    if result.errors and not result.records:
        pytest.skip(f"jobindex unavailable: {result.errors}")
    assert len(result.records) >= 1
    assert "jobindex.dk" in result.records[0].url


@pytest.mark.asyncio
async def test_wanted_live():
    result = await WantedCollector().collect("java")
    if result.errors and not result.records:
        pytest.skip(f"wanted unavailable: {result.errors}")
    assert len(result.records) >= 1
    assert "wanted.co.kr" in result.records[0].url


@pytest.mark.asyncio
async def test_instahyre_live():
    result = await InstahyreCollector().collect("java")
    if result.errors and not result.records:
        pytest.skip(f"instahyre unavailable: {result.errors}")
    assert len(result.records) >= 1
    assert "instahyre.com" in result.records[0].url


@pytest.mark.asyncio
async def test_hasjob_live():
    result = await HasjobCollector().collect()
    if result.errors and not result.records:
        pytest.skip(f"hasjob unavailable: {result.errors}")
    assert len(result.records) >= 1
    assert "hasjob.co" in result.records[0].url


@pytest.mark.asyncio
async def test_helloworld_rs_live():
    result = await HelloworldRsCollector().collect()
    if result.errors and not result.records:
        pytest.skip(f"helloworld_rs unavailable: {result.errors}")
    assert len(result.records) >= 1
    assert "helloworld.rs" in result.records[0].url


@pytest.mark.asyncio
async def test_posao_hr_live():
    result = await PosaoHrCollector().collect()
    if result.errors and not result.records:
        pytest.skip(f"posao_hr unavailable: {result.errors}")
    assert len(result.records) >= 1
    assert "posao.hr" in result.records[0].url


@pytest.mark.asyncio
async def test_jobweb_kenya_live():
    result = await JobwebKenyaCollector().collect()
    if result.errors and not result.records:
        pytest.skip(f"jobweb_kenya unavailable: {result.errors}")
    assert len(result.records) >= 1
    assert "jobwebkenya.com" in result.records[0].url


@pytest.mark.asyncio
async def test_findmethatdamjob_live():
    result = await FindMeThatDamJobCollector().collect("engineer")
    if result.errors and not result.records:
        pytest.skip(f"findmethatdamjob unavailable: {result.errors}")
    assert len(result.records) >= 1
    assert result.records[0].url.startswith("http")


@pytest.mark.asyncio
async def test_tecnoempleo_live():
    result = await TecnoempleoCollector().collect()
    if result.errors and not result.records:
        pytest.skip(f"tecnoempleo unavailable: {result.errors}")
    assert len(result.records) >= 1
    assert "tecnoempleo.com" in result.records[0].url


@pytest.mark.asyncio
async def test_frankfurter_live():
    data = await fetch_frankfurter_rates()
    assert data["provider"] == "frankfurter"
    assert "USD" in data["rates"]


def test_catalog_loaded():
    data = load_catalog()
    assert len(data.get("sources") or []) >= 160
    summary = catalog_summary()
    assert summary["total"] >= 160
    assert "ACTIVE" in summary["by_status"]
    assert "remotive" in summary["active_connector_keys"]
    assert "devitjobs" in summary["active_connector_keys"]
    assert "nofluffjobs" in summary["active_connector_keys"]
    assert "reed" in summary["active_connector_keys"]
    assert "getonbrd" in summary["active_connector_keys"]
    assert "mycareersfuture" in summary["active_connector_keys"]
    assert "jobup" in summary["active_connector_keys"]
    assert "nav_arbeidsplassen" in summary["active_connector_keys"]
    assert "nav_stilling_feed" in summary["active_connector_keys"]
    assert "landing_jobs" in summary["active_connector_keys"]
    assert "kalibrr" in summary["active_connector_keys"]
    assert "dou_ua" in summary["active_connector_keys"]
    assert "authentic_jobs" in summary["active_connector_keys"]
    assert "wantedly" in summary["active_connector_keys"]
    assert "duunitori" in summary["active_connector_keys"]
    assert "jobindex" in summary["active_connector_keys"]
    assert "wanted" in summary["active_connector_keys"]
    assert "instahyre" in summary["active_connector_keys"]
    assert "hasjob" in summary["active_connector_keys"]
    assert "helloworld_rs" in summary["active_connector_keys"]
    assert "posao_hr" in summary["active_connector_keys"]
    assert "jobweb_kenya" in summary["active_connector_keys"]
    assert "tecnoempleo" in summary["active_connector_keys"]
    assert "le_forem" in summary["active_connector_keys"]
    assert "mpsv" in summary["active_connector_keys"]
    assert "findmethatdamjob" in summary["active_connector_keys"]
    assert "findwork" not in summary["active_connector_keys"]
