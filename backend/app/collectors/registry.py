from __future__ import annotations

from app.collectors.adzuna import AdzunaCollector
from app.collectors.arbetsformedlingen import ArbetsformedlingenCollector
from app.collectors.arbeitnow import ArbeitnowCollector
from app.collectors.ats_boards import (
    AshbyCollector,
    GreenhouseCollector,
    LeverCollector,
    PersonioCollector,
)
from app.collectors.authentic_jobs import AuthenticJobsCollector
from app.collectors.base import BaseCollector, CollectionMode
from app.collectors.bundesagentur import BundesagenturCollector
from app.collectors.careerjet import CareerjetCollector
from app.collectors.france_travail import FranceTravailCollector
from app.collectors.himalayas import HimalayasCollector
from app.collectors.infojobs import InfoJobsCollector
from app.collectors.hn_whoishiring import HnWhoIsHiringCollector
from app.collectors.devglobaljobs import DevGlobalJobsCollector
from app.collectors.devitjobs import DevITJobsCollector
from app.collectors.dou_ua import DouUaCollector
from app.collectors.duunitori import DuunitoriCollector
from app.collectors.findajob_dwp import FindAJobDwpCollector
from app.collectors.findmethatdamjob import FindMeThatDamJobCollector
from app.collectors.findwork import FindworkCollector
from app.collectors.freelancer import FreelancerCollector
from app.collectors.upwork import UpworkCollector
from app.collectors.getonbrd import GetOnBoardCollector
from app.collectors.hasjob import HasjobCollector
from app.collectors.helloworld_rs import HelloworldRsCollector
from app.collectors.instahyre import InstahyreCollector
from app.collectors.jobbank_ca import JobBankCaCollector
from app.collectors.jobicy import JobicyCollector
from app.collectors.jobindex import JobindexCollector
from app.collectors.jobup import JobUpCollector
from app.collectors.jobweb_kenya import JobwebKenyaCollector
from app.collectors.jooble import JoobleCollector
from app.collectors.kalibrr import KalibrrCollector
from app.collectors.landing_jobs import LandingJobsCollector
from app.collectors.le_forem import LeForemCollector
from app.collectors.mpsv import MpsvCollector
from app.collectors.mycareersfuture import MyCareersFutureCollector
from app.collectors.nav_arbeidsplassen import NavArbeidsplassenCollector
from app.collectors.nav_stilling_feed import NavStillingFeedCollector
from app.collectors.nofluffjobs import NoFluffJobsCollector
from app.collectors.okemprego import OkEmpregoCollector
from app.collectors.posao_hr import PosaoHrCollector
from app.collectors.bamboohr import BambooHRCollector
from app.collectors.pinpoint import PinpointCollector
from app.collectors.reed import ReedCollector
from app.collectors.robert_half import RobertHalfCollector
from app.collectors.recruitee import RecruiteeCollector
from app.collectors.remoteok import RemoteOKCollector
from app.collectors.remotive import RemotiveCollector
from app.collectors.smartrecruiters import SmartRecruitersCollector
from app.collectors.teamtailor import TeamtailorCollector
from app.collectors.tecnoempleo import TecnoempleoCollector
from app.collectors.themuse import TheMuseCollector
from app.collectors.usajobs import USAJobsCollector
from app.collectors.viewjobs import ViewJobsCollector
from app.collectors.wanted import WantedCollector
from app.collectors.wantedly import WantedlyCollector
from app.collectors.weworkremotely import WeWorkRemotelyCollector
from app.collectors.workable import WorkableCollector
from app.collectors.workday import WorkdayCollector
from app.collectors.working_nomads import WorkingNomadsCollector

COLLECTORS: dict[str, BaseCollector] = {
    "remotive": RemotiveCollector(),
    "arbeitnow": ArbeitnowCollector(),
    "remoteok": RemoteOKCollector(),
    "working_nomads": WorkingNomadsCollector(),
    "weworkremotely": WeWorkRemotelyCollector(),
    "themuse": TheMuseCollector(),
    "jobicy": JobicyCollector(),
    "himalayas": HimalayasCollector(),
    "hn_whoishiring": HnWhoIsHiringCollector(),
    "devitjobs": DevITJobsCollector(),
    "nofluffjobs": NoFluffJobsCollector(),
    "getonbrd": GetOnBoardCollector(),
    "mycareersfuture": MyCareersFutureCollector(),
    "jobup": JobUpCollector(),
    "nav_arbeidsplassen": NavArbeidsplassenCollector(),
    "nav_stilling_feed": NavStillingFeedCollector(),
    "landing_jobs": LandingJobsCollector(),
    "le_forem": LeForemCollector(),
    "mpsv": MpsvCollector(),
    "kalibrr": KalibrrCollector(),
    "dou_ua": DouUaCollector(),
    "authentic_jobs": AuthenticJobsCollector(),
    "wantedly": WantedlyCollector(),
    "duunitori": DuunitoriCollector(),
    "jobindex": JobindexCollector(),
    "wanted": WantedCollector(),
    "instahyre": InstahyreCollector(),
    "hasjob": HasjobCollector(),
    "helloworld_rs": HelloworldRsCollector(),
    "posao_hr": PosaoHrCollector(),
    "jobweb_kenya": JobwebKenyaCollector(),
    "tecnoempleo": TecnoempleoCollector(),
    "greenhouse": GreenhouseCollector(),
    "lever": LeverCollector(),
    "ashby": AshbyCollector(),
    "smartrecruiters": SmartRecruitersCollector(),
    "personio": PersonioCollector(),
    "teamtailor": TeamtailorCollector(),
    "recruitee": RecruiteeCollector(),
    "pinpoint": PinpointCollector(),
    "workable": WorkableCollector(),
    "workday": WorkdayCollector(),
    "bamboohr": BambooHRCollector(),
    "arbetsformedlingen": ArbetsformedlingenCollector(),
    "adzuna": AdzunaCollector(),
    "usajobs": USAJobsCollector(),
    "reed": ReedCollector(),
    "robert_half": RobertHalfCollector(),
    "france_travail": FranceTravailCollector(),
    "bundesagentur": BundesagenturCollector(),
    "jooble": JoobleCollector(),
    "findwork": FindworkCollector(),
    "findajob_dwp": FindAJobDwpCollector(),
    "freelancer": FreelancerCollector(),
    "upwork": UpworkCollector(),
    "findmethatdamjob": FindMeThatDamJobCollector(),
    "devglobaljobs": DevGlobalJobsCollector(),
    "viewjobs": ViewJobsCollector(),
    "okemprego": OkEmpregoCollector(),
    "jobbank_ca": JobBankCaCollector(),
    "careerjet": CareerjetCollector(),
    "infojobs": InfoJobsCollector(),
}

VALID_COLLECTION_MODES: frozenset[CollectionMode] = frozenset({"search", "dump", "feed"})

# Runnable when env credentials present; verification_status stays NEEDS_CREDENTIALS until live ACTIVE
CREDENTIALED_SCAFFOLDS = frozenset(
    {
        "adzuna",
        "usajobs",
        "france_travail",
        "bundesagentur",
        "jooble",
        "findwork",
        "findajob_dwp",
        "freelancer",
        "upwork",
        "careerjet",
        "infojobs",
    }
)

# ISO country codes (or remote) for geo affinity in pick_search_collectors
COLLECTOR_GEO: dict[str, frozenset[str]] = {
    "arbetsformedlingen": frozenset({"SE"}),
    # Adzuna country paths when ADZUNA_COUNTRIES includes them (commercial licence for product KPIs)
    "adzuna": frozenset({"GB", "UK", "US", "AU", "IT", "DE", "CH", "FR"}),
    "usajobs": frozenset({"US"}),
    "findwork": frozenset({"US"}),
    "findajob_dwp": frozenset({"GB", "UK"}),
    "reed": frozenset({"GB", "UK"}),
    "france_travail": frozenset({"FR"}),
    # InfoJobs Developer API is Spain (infojobs.net); InfoJobs.it closed 2025-12-31
    "infojobs": frozenset({"ES"}),
    "bundesagentur": frozenset({"DE"}),
    "careerjet": frozenset({"IT", "DE", "CH", "LU"}),
    # ATS boards — geo affinity via tenant allowlists (see ATS_TENANTS.md / IT_CH_LU_COVERAGE)
    "greenhouse": frozenset({"IT", "CH", "LU", "EU", "US", "GB"}),
    "lever": frozenset({"IT", "CH", "LU", "EU", "US"}),
    "ashby": frozenset({"IT", "CH", "LU", "EU", "US"}),
    "smartrecruiters": frozenset({"IT", "CH", "LU", "EU"}),
    "workday": frozenset({"IT", "CH", "LU", "EU", "US"}),
    "workable": frozenset({"IT", "CH", "LU", "EU"}),
    "pinpoint": frozenset({"IT", "CH", "LU", "EU", "GB"}),
    "nav_arbeidsplassen": frozenset({"NO"}),
    "nav_stilling_feed": frozenset({"NO"}),
    "jobup": frozenset({"CH"}),
    "mycareersfuture": frozenset({"SG"}),
    "getonbrd": frozenset({"CL", "MX", "AR", "CO", "PE", "BR"}),
    "devitjobs": frozenset({"GB", "UK", "NL", "EU"}),
    "findmethatdamjob": frozenset({"NL"}),
    "nofluffjobs": frozenset({"PL", "HU", "CZ", "SK", "UA"}),
    "dou_ua": frozenset({"UA"}),
    "wantedly": frozenset({"JP"}),
    "wanted": frozenset({"KR"}),
    "duunitori": frozenset({"FI"}),
    "jobindex": frozenset({"DK"}),
    "instahyre": frozenset({"IN"}),
    "kalibrr": frozenset({"PH", "ID"}),
    "hasjob": frozenset({"IN"}),
    "helloworld_rs": frozenset({"RS"}),
    "posao_hr": frozenset({"HR"}),
    "jobweb_kenya": frozenset({"KE"}),
    "tecnoempleo": frozenset({"ES"}),
    "landing_jobs": frozenset({"PT", "EU"}),
    "personio": frozenset({"DE", "CH", "AT", "EU"}),
    "le_forem": frozenset({"BE"}),
    "mpsv": frozenset({"CZ"}),
    "devglobaljobs": frozenset({"LU", "BG"}),
    "viewjobs": frozenset({"AU"}),
    "okemprego": frozenset({"PT", "BR", "AO"}),
    "jobbank_ca": frozenset({"CA"}),
}


def get_collector(source_key: str) -> BaseCollector | None:
    return COLLECTORS.get(source_key)


def get_collection_mode(collector: BaseCollector) -> CollectionMode:
    """Resolve ``collection_mode`` from the concrete collector class."""
    for cls in type(collector).__mro__:
        if cls is BaseCollector:
            break
        if "collection_mode" in cls.__dict__:
            mode = cls.__dict__["collection_mode"]
            if mode in VALID_COLLECTION_MODES:
                return mode  # type: ignore[return-value]
    raise AttributeError(
        f"collector {collector.source_key!r} missing explicit collection_mode"
    )


def collectors_by_mode(mode: CollectionMode) -> dict[str, BaseCollector]:
    """Return registered collectors whose ``collection_mode`` equals ``mode``."""
    return {
        key: collector
        for key, collector in COLLECTORS.items()
        if get_collection_mode(collector) == mode
    }


def list_collectors_by_mode() -> dict[CollectionMode, list[str]]:
    """Group registered collector source keys by collection_mode."""
    grouped: dict[CollectionMode, list[str]] = {"search": [], "dump": [], "feed": []}
    for key, collector in COLLECTORS.items():
        grouped[get_collection_mode(collector)].append(key)
    for mode in grouped:
        grouped[mode].sort()
    return grouped
