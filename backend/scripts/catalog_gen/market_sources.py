"""Categories A (core aggregators), B (freelance), C (agencies), D (ATS)."""

from __future__ import annotations

from .registry import add


def register() -> None:
    # --- A aggregators ---
    add(1, "Adzuna", "A", "https://developer.adzuna.com/", status="NEEDS_CREDENTIALS", access="api_key", docs_url="https://developer.adzuna.com/", connector_key="adzuna", notes="Connector implemented; enable with ADZUNA_APP_ID + ADZUNA_APP_KEY then seed. ACTIVE only when keys present and live.")
    add(2, "Jooble", "A", "https://jooble.org/api/about", status="NEEDS_CREDENTIALS", access="api_key", docs_url="https://jooble.org/api/about", connector_key="jooble", notes="Connector implemented; set JOOBLE_API_KEY. ACTIVE only after live run.")
    add(
        196,
        "Findwork.dev",
        "A",
        "https://findwork.dev/",
        status="NEEDS_CREDENTIALS",
        access="api_key",
        docs_url="https://findwork.dev/developers/",
        connector_key="findwork",
        notes="Connector scaffolded (findwork.py); set FINDWORK_API_KEY (Authorization: Token). Optional FINDWORK_LOCATION. ACTIVE only after registry wire + live run.",
    )
    add(
        3,
        "Careerjet",
        "A",
        "https://www.careerjet.com/partners/api",
        status="NEEDS_CREDENTIALS",
        access="partner_api",
        docs_url="https://www.careerjet.com/partners/api/",
        connector_key="careerjet",
        notes="Connector scaffolded (careerjet.py); CAREERJET_API_KEY + CAREERJET_USER_IP. Locales IT/DE/CH/LU. ACTIVE only after live run.",
    )
    add(4, "Remotive", "A", "https://remotive.com/remote-jobs/api", status="ACTIVE", access="public_api", docs_url="https://remotive.com/api/remote-jobs", connector_key="remotive", notes="Live GET 200; connector implemented and tested.")
    add(5, "Arbeitnow", "A", "https://www.arbeitnow.com/", status="ACTIVE", access="public_api", docs_url="https://www.arbeitnow.com/api/job-board-api", connector_key="arbeitnow", notes="Live GET 200; connector implemented and tested.")
    add(6, "The Muse", "A", "https://www.themuse.com/developers/api/v2", status="ACTIVE", access="public_api", docs_url="https://www.themuse.com/api/public/jobs", connector_key="themuse", notes="Live GET 200 with jobs; connector implemented.")
    add(7, "USAJOBS", "A", "https://developer.usajobs.gov/", status="NEEDS_CREDENTIALS", access="api_key", docs_url="https://developer.usajobs.gov/", connector_key="usajobs", notes="Connector implemented; enable with USAJOBS_API_KEY + USAJOBS_USER_AGENT (email). ACTIVE only after live run with keys.")
    add(
        8,
        "Find a Job UK DWP",
        "A",
        "https://findajob.dwp.gov.uk/",
        status="NEEDS_CREDENTIALS",
        access="api_key",
        docs_url="https://www.api.gov.uk/dwp/find-a-job/",
        connector_key="findajob_dwp",
        notes="Connector scaffolded (findajob_dwp.py); FINDAJOB_DWP_API_ID + FINDAJOB_DWP_API_KEY. GET /api/search. ACTIVE only after live run with keys.",
    )
    add(9, "EURES", "A", "https://eures.europa.eu/", status="NEEDS_CREDENTIALS", access="partner_api", notes="EURES API typically requires registration; not probed with credentials.")
    add(10, "Indeed", "A", "https://www.indeed.com/", status="NEEDS_CREDENTIALS", access="publisher_api", notes="Authorized publisher/partner APIs only. No scraping.")
    add(11, "LinkedIn Jobs", "A", "https://www.linkedin.com/jobs/", status="NEEDS_CREDENTIALS", access="partner_api", notes="Official partner APIs only. No scraping.")
    add(12, "Glassdoor Jobs", "A", "https://www.glassdoor.com/Job/", status="NEEDS_CREDENTIALS", access="partner_api", notes="No verified public open API; ToS restricts scraping.")
    add(13, "Google for Jobs", "A", "https://developers.google.com/search/docs/appearance/structured-data/job-posting", status="REJECTED", access="schema_markup", notes="Structured data for employers publishing jobs to Google; not a job-search API for bulk pull.")
    add(
        14,
        "Talent.com",
        "A",
        "https://www.talent.com/",
        status="NEEDS_CREDENTIALS",
        access="partner_api",
        docs_url="https://employers.talent.com/publishers",
        notes=(
            "Publisher program (XML feeds / Job API) via publishers@talent.com. "
            "Public integrations docs are employer→Talent only. No open schema until partnership."
        ),
    )
    add(
        15,
        "SimplyHired",
        "A",
        "https://www.simplyhired.com/",
        status="REJECTED",
        access="unknown",
        notes="REJECTED: Indeed-family destination; legacy partner API ended ~2016. No public inventory pull API.",
    )
    add(16, "ZipRecruiter", "A", "https://www.ziprecruiter.com/", status="NEEDS_CREDENTIALS", access="partner_api", notes="Partner integrations; credentials required.")
    add(
        17,
        "Reed",
        "A",
        "https://www.reed.co.uk/",
        status="ACTIVE",
        access="rss",
        docs_url="https://www.reed.co.uk/jobs/rss",
        connector_key="reed",
        notes="Free public RSS `GET /jobs/rss?keywords=` verified 200. Optional REED_API_KEY for richer JSON API.",
    )
    add(
        18,
        "Totaljobs",
        "A",
        "https://www.totaljobs.com/",
        status="REJECTED",
        access="partner_api",
        docs_url="https://api.stepstone.com/knowledge-base/totaljobs-uk/",
        notes="REJECTED: StepStone JobFeed is employer post-in only (PUSH/PULL of customer ATS). No documented inventory outfeed. Prefer Reed/Adzuna.",
    )
    add(
        19,
        "CV-Library",
        "A",
        "https://www.cv-library.co.uk/",
        status="NEEDS_CREDENTIALS",
        access="partner_api",
        docs_url="https://www.cv-library.co.uk/developers/job-search-api",
        notes=(
            "Partner Job Search/View APIs + affiliate XML/CSV (partners@cv-library.co.uk). "
            "API docs disallow bulk download — negotiate XML feed + MI reuse before connector."
        ),
    )
    add(
        20,
        "CWJobs",
        "A",
        "https://www.cwjobs.co.uk/",
        status="REJECTED",
        access="partner_api",
        docs_url="https://api.stepstone.com/",
        notes="REJECTED: StepStone UK brand; public APIs are employer posting only. No consumer inventory API.",
    )
    add(
        21,
        "Technojobs",
        "A",
        "https://www.technojobs.co.uk/",
        status="UNDER_REVIEW",
        access="rss",
        docs_url="https://www.technojobs.co.uk/rss-about.phtml",
        notes="Candidate search RSS exists; confirm ToS/commercial reuse before connector. No partner inventory API found.",
    )
    add(
        22,
        "Welcome to the Jungle",
        "A",
        "https://www.welcometothejungle.com/",
        status="NEEDS_CREDENTIALS",
        access="partner_api",
        docs_url="https://developers.welcomekit.co/jobs-api/jobs/list-all-jobs",
        notes=(
            "Partner Solutions API: GET /api/v1/external/jobs/all requires dedicated partnership "
            "+ Bearer with su_jobs_r. Org-scoped Solutions tokens ≠ board inventory."
        ),
    )
    add(
        23,
        "No Fluff Jobs",
        "A",
        "https://nofluffjobs.com/",
        status="DISCOVERED",
        access="duplicate",
        duplicate_of=176,
        notes="Duplicate of catalog_id 176 (NoFluffJobs ACTIVE connector).",
    )
    add(
        24,
        "Tecnoempleo",
        "A",
        "https://www.tecnoempleo.com/",
        status="ACTIVE",
        access="rss",
        docs_url="https://www.tecnoempleo.com/alertas-empleo-rss.php",
        connector_key="tecnoempleo",
        notes="Free Spain IT RSS (alertas-empleo-rss.php; optional ?te=). ADR-003: RSS only — no Empléate Solr scrape.",
    )
    add(
        25,
        "InfoJobs",
        "A",
        "https://www.infojobs.net/",
        status="NEEDS_CREDENTIALS",
        access="partner_api",
        docs_url="https://developer.infojobs.net/documentation/operation/offer-list-1.xhtml",
        connector_key="infojobs",
        notes=(
            "Spain InfoJobs Developer API (api.infojobs.net). InfoJobs.it closed 2025-12-31 — "
            "do not treat as Italy. INFOJOBS_CLIENT_ID + SECRET (HTTP Basic). "
            "ACTIVE only after live run. Storage/redistribution may need partner agreement."
        ),
    )
    add(
        26,
        "jobs.ch",
        "A",
        "https://www.jobs.ch/",
        status="NEEDS_CREDENTIALS",
        access="partner_api",
        docs_url="https://www.jobcloud.ch/c/en/blog/jobcloud-affiliate-program-how-to-partner-with-jobs-ch-jobup-ch-and-jobscout24/",
        notes=(
            "JobCloud affiliate inventory (XML/JSON) via affiliates@jobcloud.ch. "
            "Public /api/ robots-disallowed; ToS forbids bots — no scrape collector."
        ),
    )
    add(
        27,
        "JobScout24",
        "A",
        "https://www.jobscout24.ch/",
        status="NEEDS_CREDENTIALS",
        access="partner_api",
        docs_url="https://www.jobcloud.ch/c/en/blog/jobcloud-affiliate-program-how-to-partner-with-jobs-ch-jobup-ch-and-jobscout24/",
        notes="JobCloud affiliate same as jobs.ch/jobup.ch — request JobScout24 in affiliates@jobcloud.ch deal. No public API.",
    )
    add(28, "StepStone", "A", "https://www.stepstone.com/", status="NEEDS_CREDENTIALS", access="partner_api", notes="Commercial partner feeds; credentials required.")
    add(29, "XING Jobs", "A", "https://www.xing.com/jobs", status="NEEDS_CREDENTIALS", access="partner_api", notes="XING APIs require developer/partner access.")
    add(30, "Bundesagentur für Arbeit", "A", "https://www.arbeitsagentur.de/jobsuche/", status="NEEDS_CREDENTIALS", access="api_key", docs_url="https://jobsuche.api.bund.dev/", connector_key="bundesagentur", notes="Connector implemented; set BUNDESAGENTUR_API_KEY (Jobsuche X-API-Key). ACTIVE only after live run. Confirm reuse terms.")
    add(31, "France Travail", "A", "https://www.francetravail.fr/", status="NEEDS_CREDENTIALS", access="api_key", docs_url="https://francetravail.io/", connector_key="france_travail", notes="Connector implemented; FRANCE_TRAVAIL_CLIENT_ID + SECRET (OAuth2). Access may require subscription on francetravail.io. ACTIVE only after live run.")
    add(
        32,
        "APEC",
        "A",
        "https://www.apec.fr/",
        status="REJECTED",
        access="unknown",
        notes=(
            "REJECTED: no consumer job-search API. data.gouv APEC = surveys/salary only. "
            "ADEP is ATS→APEC publish. FR inventory → France Travail partner path."
        ),
    )
    add(
        33,
        "VDAB",
        "A",
        "https://www.vdab.be/",
        status="NEEDS_CREDENTIALS",
        access="api_key",
        docs_url="https://developer.vdab.be/opendata/",
        notes=(
            "Official open-data Vacatures API (register → Client Id/Secret → subscribe). "
            "Base api.vdab.be/services/openservices/vacatures/v4/ (GET /vacatures, /bulk). "
            "Header X-IBM-Client-Id. Contact openservices@vdab.be. ACTIVE after live keys."
        ),
    )
    add(
        34,
        "Actiris",
        "A",
        "https://www.actiris.brussels/",
        status="REJECTED",
        access="unknown",
        notes="REJECTED: no official vacancy API/open-data dump. opendata.brussels = stats only. Partner programme ≠ job feed.",
    )
    add(
        35,
        "Le Forem",
        "A",
        "https://www.leforem.be/",
        status="ACTIVE",
        access="open_data",
        docs_url="https://www.odwb.be/explore/dataset/offres-d-emploi-forem/",
        connector_key="le_forem",
        notes=(
            "Free Wallonia BE ODWB open data (Explore API records, dump cap 200). "
            "No key. Partner HR-XML / VDAB out of scope. ADR-003 open data only."
        ),
    )
    add(
        36,
        "Nationale Vacaturebank",
        "A",
        "https://www.nationalevacaturebank.nl/",
        status="REJECTED",
        access="unknown",
        notes=(
            "REJECTED: documented keys are employer Job Poster API only. "
            "Unofficial api.nationalevacaturebank.nl reverse-engines ≠ contract. "
            "NL: findmethatdamjob / Adzuna nl."
        ),
    )
    add(
        37,
        "IrishJobs",
        "A",
        "https://www.irishjobs.ie/",
        status="REJECTED",
        access="partner_api",
        notes="REJECTED: StepStone group; integrations are outbound posting XML only. No inventory pull API.",
    )
    add(
        38,
        "Pracuj.pl",
        "A",
        "https://www.pracuj.pl/",
        status="REJECTED",
        access="unknown",
        notes="REJECTED: no official consumer job API; press/PDF reports only. Employer ATS posting ≠ pull feed.",
    )
    add(
        39,
        "Jobly",
        "A",
        "https://www.jobly.fi/",
        status="REJECTED",
        access="api_key",
        docs_url="https://jobly.almamedia.fi/api/",
        notes="REJECTED: official API is import-only (POST add/delete). No search/export. Prefer Finnish PES open data.",
    )
    add(
        40,
        "Arbetsförmedlingen",
        "A",
        "https://arbetsformedlingen.se/",
        status="ACTIVE",
        access="open_data",
        docs_url="https://jobsearch.api.jobtechdev.se/",
        connector_key="arbetsformedlingen",
        notes="JobTech JobSearch GET /search live 200 (2026-10-20); public, no API key. Connector implemented.",
    )
    add(
        41,
        "NAV Stillingsfeed",
        "A",
        "https://pam-stilling-feed.nav.no/",
        status="ACTIVE",
        access="public_api",
        docs_url="https://navikt.github.io/pam-stilling-feed/",
        connector_key="nav_stilling_feed",
        notes=(
            "pam-stilling-feed dump (JWT via /api/publicToken; rotates). "
            "ACTIVE-only window via If-Modified-Since. "
            "Dedupe with nav_arbeidsplassen (search) on same stilling UUID/canonical_url. "
            "Private consumer token recommended for production."
        ),
    )
    add(42, "InfoJobs Spain", "A", "https://www.infojobs.net/", status="DISCOVERED", access="duplicate", duplicate_of=25, notes="Duplicate of catalog_id 25 (same domain).")

    # --- B freelance marketplaces ---
    add(
        45,
        "Freelancer.com projects",
        "B",
        "https://www.freelancer.com/",
        status="NEEDS_CREDENTIALS",
        access="oauth",
        docs_url="https://developers.freelancer.com/",
        connector_key="freelancer",
        notes="Connector scaffolded (freelancer.py); FREELANCER_OAUTH_TOKEN Bearer. GET /projects/0.1/projects/active/. ACTIVE only after live run with token.",
    )
    add(
        44,
        "Upwork GraphQL",
        "B",
        "https://www.upwork.com/",
        status="NEEDS_CREDENTIALS",
        access="oauth",
        docs_url="https://www.upwork.com/developer/",
        connector_key="upwork",
        notes="Connector scaffolded (upwork.py); UPWORK_OAUTH_TOKEN Bearer + optional UPWORK_TENANT_ID. POST api.upwork.com/graphql marketplaceJobPostingsSearch. ACTIVE only after approved key + live run.",
    )
    for cid, name, url, notes in [
        (
            43,
            "Malt",
            "https://www.malt.com/",
            "PARTNER: api.malt.com = invoices/SCIM (org tokens via Malt rep). No marketplace listings feed for MI.",
        ),
        (46, "Toptal", "https://www.toptal.com/", "REJECTED: no public marketplace/partner inventory API."),
        (
            47,
            "Contra",
            "https://contra.com/",
            "NEEDS_CREDENTIALS: Public API + MCP (X-API-Key) for experts/programs/rates — talent supply, not classic job RSS. Request key.",
        ),
        (
            48,
            "PeoplePerHour",
            "https://www.peopleperhour.com/",
            "UNDER_REVIEW: legacy PHP client (app id/secret) exists historically; no live developer portal — BD ask before REJECT.",
        ),
        (49, "Guru", "https://www.guru.com/", "REJECTED: no guru.com marketplace API (do not confuse with getguru.com KB)."),
        (50, "Worksome", "https://www.worksome.com/", "Enterprise access."),
        (
            51,
            "YunoJuno",
            "https://www.yunojuno.com/",
            "NEEDS_CREDENTIALS: Client API/OAuth for own FMS tenancy (job posts scoped to client). Not public board crawl.",
        ),
        (
            52,
            "freelancermap",
            "https://www.freelancermap.com/",
            "REJECTED: inbound recruiter XML/JSON import only (~3h fetch); no outbound projects API; no scraping.",
        ),
        (53, "GULP", "https://www.gulp.de/", "REJECTED: no documented public API/XML outbound feed."),
        (54, "Fiverr", "https://www.fiverr.com/", "Partner API; credentials."),
        (
            55,
            "FlexJobs",
            "https://www.flexjobs.com/",
            "REJECTED: inbound employer XML only; paid membership UI ≠ API.",
        ),
        (
            56,
            "Braintrust",
            "https://www.usebraintrust.com/",
            "UNDER_REVIEW: undocumented dashboard aggregate JSON observed; not a job API — formalize ToS before use. Not braintrust.dev.",
        ),
        (57, "Catalant", "https://gocatalant.com/", "Enterprise."),
        (58, "A.Team", "https://www.a.team/", "REJECTED: invite network; no public API/OpenAPI."),
        (
            59,
            "Lemon.io",
            "https://lemon.io/",
            "PARTNER: MCP hire-request tools + Co-Sell referrals — not a listing export API.",
        ),
        (60, "Arc", "https://arc.dev/", "REJECTED: partnerships are GTM/referral only; no public data API."),
        (61, "Gun.io", "https://www.gun.io/", "REJECTED: referral/affiliate only; unofficial cookie APIs out of scope."),
    ]:
        if notes.startswith("REJECTED:"):
            st = "REJECTED"
        elif notes.startswith("NEEDS_CREDENTIALS:") or notes.startswith("PARTNER:"):
            st = "NEEDS_CREDENTIALS"
        elif notes.startswith("UNDER_REVIEW:"):
            st = "UNDER_REVIEW"
        elif any(tok in notes for tok in ("Partner API", "OAuth", "Enterprise", "credentials")):
            st = "NEEDS_CREDENTIALS"
        elif "No verified public API" in notes or "no public API" in notes.lower():
            st = "REJECTED"
        else:
            st = "UNDER_REVIEW"
        add(cid, name, "B", url, status=st, access="partner_or_unknown", notes=notes)

    add(62, "We Work Remotely", "B", "https://weworkremotely.com/", status="ACTIVE", access="rss", docs_url="https://weworkremotely.com/categories/remote-programming-jobs.rss", connector_key="weworkremotely", notes="RSS 200; connector implemented.")
    add(63, "Remote OK", "B", "https://remoteok.com/", status="ACTIVE", access="public_api", docs_url="https://remoteok.com/api", connector_key="remoteok", notes="API 200; ToS requires attribution link. Connector implemented.")
    add(64, "Working Nomads", "B", "https://www.workingnomads.com/", status="ACTIVE", access="public_api", docs_url="https://www.workingnomads.com/api/exposed_jobs/", connector_key="working_nomads", notes="Exposed jobs API 200; connector implemented.")
    add(65, "Wellfound", "B", "https://wellfound.com/", status="NEEDS_CREDENTIALS", access="unknown", notes="Formerly AngelList; no verified open bulk API. Prefer free Jobicy/Himalayas/HN over paid scrapers.")
    add(
        171,
        "Jobicy",
        "B",
        "https://jobicy.com/",
        status="ACTIVE",
        access="public_api",
        docs_url="https://jobicy.com/api/v2/remote-jobs",
        connector_key="jobicy",
        notes="Free public remote API 200 (2026-10-20). Attribution to Jobicy required. Prefer over paid aggregator APIs.",
    )
    add(
        172,
        "Himalayas",
        "B",
        "https://himalayas.app/",
        status="ACTIVE",
        access="public_api",
        docs_url="https://himalayas.app/jobs/api",
        connector_key="himalayas",
        notes="Free public jobs API 200 (2026-10-20). No key. Prefer over paid aggregator APIs.",
    )
    add(
        173,
        "HN Who is hiring",
        "B",
        "https://news.ycombinator.com/",
        status="ACTIVE",
        access="public_api",
        docs_url="https://hn.algolia.com/api",
        connector_key="hn_whoishiring",
        notes="Monthly Who is hiring via Algolia public API (not HTML scrape). Filters seeking-work comments.",
    )
    add(
        66,
        "Flexiple",
        "B",
        "https://flexiple.com/",
        status="REJECTED",
        access="unknown",
        notes="REJECTED: no official developer/partner API docs.",
    )

    # --- C agencies ---
    add(
        69,
        "Robert Half",
        "C",
        "https://www.roberthalf.com/",
        status="ACTIVE",
        access="public_feed",
        docs_url="https://joblist.roberthalf.com/IZ/",
        connector_key="robert_half",
        notes=(
            "Official public XML syndication JobPositionPosting: "
            "joblist.roberthalf.com/IZ/general_rh-{cc}.xml (keyless). "
            "Defaults ROBERT_HALF_COUNTRIES=ch,uk. Workday board = corporate careers only."
        ),
    )
    for cid, name, url, notes in [
        (67, "Hays", "https://www.hays.com/", "REJECTED: proprietary job search; UKG Ultipro US careers ≠ placement feed."),
        (68, "Michael Page", "https://www.michaelpage.com/", "REJECTED: PageGroup Salesforce; no public board API."),
        (
            70,
            "Randstad",
            "https://www.randstad.com/",
            "UNDER_REVIEW: Workday randstad.wd502 / randstadcareers = corporate hiring only; placement sites proprietary.",
        ),
        (71, "Adecco", "https://www.adecco.com/", "REJECTED: robots Disallow /jobs/; sitemap ≠ API; SR AdeccoStaffingUSA1 empty."),
        (
            72,
            "Manpower",
            "https://www.manpower.com/",
            "UNDER_REVIEW: SmartRecruiters ManpowerFrance has stale 2018 postings — freshness gate if probed.",
        ),
        (73, "Experis", "https://www.experis.com/", "REJECTED: SR ExperisManpowerGroup1 ≈ stale; placements on proprietary site."),
        (
            74,
            "TEKsystems",
            "https://www.teksystems.com/",
            "PARTNER: Phenom CareerConnect (TESYUS) — needs Phenom collector or partner docs (not in stack).",
        ),
        (
            75,
            "Kforce",
            "https://www.kforce.com/",
            "UNDER_REVIEW: SR Kforce-Phoenix remnant (2014–2016); main inventory on kforce.com HTML — no scrape.",
        ),
        (76, "Robert Walters", "https://www.robertwalters.com/", "REJECTED: proprietary talentsource; no public ATS board."),
        (
            77,
            "Harvey Nash",
            "https://www.harveynash.com/",
            "UNDER_REVIEW: Workable harvey-nash-108 widget empty; recheck periodically.",
        ),
        (
            78,
            "Computer Futures",
            "https://www.computerfutures.com/",
            "UNDER_REVIEW: SR ComputerFutures3 public but 2016–2017 stale; live demand on SThree HTML — no scrape.",
        ),
        (79, "Nigel Frank", "https://www.nigelfrank.com/", "REJECTED: SR NigelFrank1 corporate-only; placements on custom FRG app."),
        (
            80,
            "Huxley",
            "https://www.huxley.com/",
            "UNDER_REVIEW: SR Huxley1 (~2019) likely stale; live list on huxley.com — no scrape.",
        ),
        (
            81,
            "La Fosse",
            "https://www.lafosse.com/",
            "UNDER_REVIEW: Workable lafosse live but mostly internal recruiter roles; client placements HTML.",
        ),
        (82, "Brio Digital", "https://www.briodigital.io/", "REJECTED: Webflow HTML vacancies + email apply; no ATS/API."),
    ]:
        if notes.startswith("REJECTED:"):
            st = "REJECTED"
        elif notes.startswith("PARTNER:"):
            st = "NEEDS_CREDENTIALS"
        else:
            st = "UNDER_REVIEW"
        add(cid, name, "C", url, status=st, access="website_or_feed", notes=notes)

    # --- D ATS ---
    add(83, "Greenhouse Job Board API", "D", "https://developers.greenhouse.io/job-board.html", status="ACTIVE", access="public_api_per_board", connector_key="greenhouse", notes="Per-board public API. Defaults GREENHOUSE_BOARDS=69 tenants (multi-agent probe 2026-10-21). Empty → non-runnable.")
    add(84, "Lever Postings API", "D", "https://github.com/lever/postings-api", status="ACTIVE", access="public_api_per_site", connector_key="lever", notes="Per-site API. Defaults LEVER_SITES=spotify,palantir,wealthfront (probed 2026-10-21). Empty → non-runnable.")
    add(
        85,
        "SmartRecruiters API",
        "D",
        "https://developers.smartrecruiters.com/",
        status="ACTIVE",
        access="public_api_per_company",
        docs_url="https://developers.smartrecruiters.com/",
        connector_key="smartrecruiters",
        notes="Public postings API. Defaults SMARTRECRUITERS_COMPANIES include endava,ServiceNow,DeliveryHero,Wise,Allegro,Uber (probed 2026-10-20). Empty → non-runnable.",
    )
    add(86, "Ashby Job Postings", "D", "https://developers.ashbyhq.com/", status="ACTIVE", access="public_api_per_org", connector_key="ashby", notes="Public posting API. Defaults ASHBY_ORGS=51 orgs (multi-agent probe 2026-10-21). Empty → non-runnable.")
    add(
        87,
        "Workable careers widget",
        "D",
        "https://www.workable.com/",
        status="ACTIVE",
        access="public_api_per_company",
        docs_url="https://help.workable.com/hc/en-us/articles/115012771647",
        connector_key="workable",
        notes="Keyless GET apply.workable.com/api/v1/widget/accounts/{slug}?details=true. Defaults WORKABLE_SLUGS=huggingface,jasper,skillshare,riot (non-empty boards probed 2026-10-21). Many brand slugs return jobs:[]. Back off on HTTP 429. SPI v3 remains tenant-keyed.",
    )
    add(
        88,
        "Workday Careers CXS",
        "D",
        "https://www.workday.com/",
        status="ACTIVE",
        access="public_api_per_tenant",
        docs_url="https://www.workday.com/",
        connector_key="workday",
        notes="Keyless POST https://{tenant}.{wd}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs. Defaults WORKDAY_TENANTS=37 tech-leaning CXS (multi-agent probe 2026-10-21; retail megaboards omitted). Empty → non-runnable. No cross-tenant search.",
    )
    add(89, "SAP SuccessFactors Recruiting", "D", "https://www.sap.com/", status="NEEDS_CREDENTIALS", access="enterprise", notes="Enterprise OData; customer tenant credentials.")
    add(90, "Oracle Recruiting", "D", "https://www.oracle.com/", status="NEEDS_CREDENTIALS", access="enterprise", notes="Enterprise cloud credentials.")
    add(91, "iCIMS", "D", "https://www.icims.com/", status="NEEDS_CREDENTIALS", access="enterprise", notes="Customer credentials.")
    add(
        92,
        "Personio public career boards",
        "D",
        "https://www.personio.com/",
        status="ACTIVE",
        access="public_api_per_company",
        docs_url="https://github.com/personio/api-docs/blob/master/personio-recruiting-api.yaml",
        connector_key="personio",
        notes="Public listing GET {slug}.jobs.personio.de/search.json (no HTML scrape). Defaults PERSONIO_COMPANIES=15 DACH/EU tech slugs (probed 2026-10-21). Employer Recruiting API remains credentialed separately.",
    )
    add(
        93,
        "Teamtailor career JSON Feed",
        "D",
        "https://www.teamtailor.com/",
        status="ACTIVE",
        access="public_api_per_host",
        docs_url="https://support.teamtailor.com/en/articles/5963369-use-our-teamtailor-api",
        connector_key="teamtailor",
        notes="Keyless GET https://{host}/jobs.json (JSON Feed items). Defaults TEAMTAILOR_HOSTS=26 Nordic/EU hosts (probed 2026-10-21). Empty → non-runnable. JSON:API remains tenant-keyed.",
    )
    add(
        94,
        "Recruitee Careers Site offers",
        "D",
        "https://recruitee.com/",
        status="ACTIVE",
        access="public_api_per_company",
        docs_url="https://docs.recruitee.com/reference/intro-to-careers-site-api",
        connector_key="recruitee",
        notes="Keyless GET https://{slug}.recruitee.com/api/offers/ until 2027-02-10. Defaults RECRUITEE_SLUGS=9 slugs (probed 2026-10-21). Empty → non-runnable. Plan X-Careers-Sites-Token after deadline.",
    )
    add(
        95,
        "BambooHR public careers",
        "D",
        "https://www.bamboohr.com/",
        status="ACTIVE",
        access="public_api_per_company",
        docs_url="https://documentation.bamboohr.com/reference/applicant-tracking",
        connector_key="bamboohr",
        notes="Keyless GET {slug}.bamboohr.com/careers/list (+ optional /detail). Defaults BAMBOOHR_COMPANIES=flyio (live 200 from API container 2026-10-22). DC egress may still 503 on some networks — re-probe before expanding. Open API ATS remains credentialed/PARTNER.",
    )
    add(
        96,
        "Pinpoint postings.json",
        "D",
        "https://www.pinpointhq.com/",
        status="ACTIVE",
        access="public_api_per_company",
        docs_url="https://developers.pinpointhq.com/docs/jobs-json-endpoint",
        connector_key="pinpoint",
        notes="Keyless GET https://{subdomain}.pinpointhq.com/postings.json. Defaults PINPOINT_SUBDOMAINS=10 (+hazelcast,smartthings; probed 2026-10-21; skipped DEI demos). Empty → non-runnable.",
    )
