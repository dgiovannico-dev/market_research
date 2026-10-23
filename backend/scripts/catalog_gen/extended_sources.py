"""Extended A aggregators (175–193), remaining G (150), H (procurement), I (discovery)."""

from __future__ import annotations

from .registry import add


def register() -> None:
    add(
        175,
        "DevITJobs",
        "A",
        "https://devitjobs.uk/",
        status="ACTIVE",
        access="public_api",
        docs_url="https://devitjobs.uk/api/jobsLight",
        connector_key="devitjobs",
        notes="Free jobsLight JSON (uk/com hosts). No key. Good UK/IT coverage; prefer over paid aggregators.",
    )
    add(
        176,
        "NoFluffJobs",
        "A",
        "https://nofluffjobs.com/",
        status="ACTIVE",
        access="public_api",
        docs_url="https://nofluffjobs.com/api/posting",
        connector_key="nofluffjobs",
        notes="Free public posting dump (CEE IT; often B2B hourly). Large payload — connector caps + query filter. No key.",
    )
    add(
        177,
        "Get on Board",
        "A",
        "https://www.getonbrd.com/",
        status="ACTIVE",
        access="public_api",
        docs_url="https://www.getonbrd.com/api/v0/search/jobs",
        connector_key="getonbrd",
        notes="Free LATAM tech jobs JSON API (search + programming category). Often posts monthly salaries. No key.",
    )
    add(
        178,
        "MyCareersFuture",
        "A",
        "https://www.mycareersfuture.gov.sg/",
        status="ACTIVE",
        access="public_api",
        docs_url="https://api.mycareersfuture.gov.sg/v2/jobs",
        connector_key="mycareersfuture",
        notes="Free Singapore government jobs API v2 search. No key. Strong APAC IT coverage.",
    )
    add(
        179,
        "JobUp",
        "A",
        "https://www.jobup.ch/",
        status="ACTIVE",
        access="public_api",
        docs_url="https://www.jobup.ch/api/v1/public/search",
        connector_key="jobup",
        notes=(
            "Public search JSON works without a key. JobCloud ToS §7 and robots.txt Disallow: /api/ "
            "conflict with automated harvest — legal review / prefer affiliate feed before scaling. "
            "Prefer query= for IT filters. See IT_CH_LU_COVERAGE.md."
        ),
    )
    add(
        180,
        "NAV Arbeidsplassen",
        "A",
        "https://arbeidsplassen.nav.no/",
        status="ACTIVE",
        access="public_api",
        docs_url="https://arbeidsplassen.nav.no/stillinger/api/search",
        connector_key="nav_arbeidsplassen",
        notes=(
            "Free Norwegian PES stillinger search JSON (same API as the public UI). No key. "
            "Companion dump: nav_stilling_feed (catalog 41) — same vacancy UUIDs; ingest dedupes on canonical_url."
        ),
    )
    add(
        181,
        "Landing.jobs",
        "A",
        "https://landing.jobs/",
        status="ACTIVE",
        access="public_api",
        docs_url="https://landing.jobs/api/v1/jobs",
        connector_key="landing_jobs",
        notes="Free EU tech jobs JSON with EUR gross salary bands. Client-side query filter. No key.",
    )
    add(
        182,
        "Kalibrr",
        "A",
        "https://www.kalibrr.com/",
        status="ACTIVE",
        access="public_api",
        docs_url="https://www.kalibrr.com/api/job_board/search",
        connector_key="kalibrr",
        notes="Free SEA (PH-heavy) job board search JSON. No key.",
    )
    add(
        183,
        "DOU.ua",
        "A",
        "https://jobs.dou.ua/",
        status="ACTIVE",
        access="public_api",
        docs_url="https://jobs.dou.ua/vacancies/feeds/",
        connector_key="dou_ua",
        notes="Free Ukrainian IT category RSS feeds. No key. Default category Java.",
    )
    add(
        184,
        "Authentic Jobs",
        "A",
        "https://authenticjobs.com/",
        status="ACTIVE",
        access="public_api",
        docs_url="https://feeds.feedburner.com/AuthenticJobs",
        connector_key="authentic_jobs",
        notes="Free design/dev jobs RSS via FeedBurner (site /rss is editorial). No key.",
    )
    add(
        185,
        "Wantedly",
        "A",
        "https://www.wantedly.com/",
        status="ACTIVE",
        access="public_api",
        docs_url="https://www.wantedly.com/api/v1/projects",
        connector_key="wantedly",
        notes="Free Japan projects/jobs JSON search. No key. Strong JP IT coverage.",
    )
    add(
        186,
        "Duunitori",
        "A",
        "https://duunitori.fi/",
        status="ACTIVE",
        access="public_api",
        docs_url="https://duunitori.fi/api/v1/jobentries",
        connector_key="duunitori",
        notes="Free Finland jobentries JSON search. No key. Detail URL from slug.",
    )
    add(
        187,
        "Jobindex",
        "A",
        "https://www.jobindex.dk/",
        status="ACTIVE",
        access="public_api",
        docs_url="https://www.jobindex.dk/jobsoegning.rss",
        connector_key="jobindex",
        notes="Free Danish jobs RSS (?q=). No key.",
    )
    add(
        188,
        "Wanted",
        "A",
        "https://www.wanted.co.kr/",
        status="ACTIVE",
        access="public_api",
        docs_url="https://www.wanted.co.kr/api/v4/jobs",
        connector_key="wanted",
        notes="Free Korea jobs JSON (v4). No key. annual_from/to are experience years, not salary.",
    )
    add(
        189,
        "Instahyre",
        "A",
        "https://www.instahyre.com/",
        status="ACTIVE",
        access="public_api",
        docs_url="https://www.instahyre.com/api/v1/job_search/",
        connector_key="instahyre",
        notes="Free India tech job search JSON. No key.",
    )
    add(
        190,
        "Hasjob",
        "A",
        "https://hasjob.co/",
        status="ACTIVE",
        access="public_api",
        docs_url="https://hasjob.co/?format=json",
        connector_key="hasjob",
        notes="Free India/tech jobs JSON board (?format=json). No key.",
    )
    add(
        191,
        "HelloWorld.rs",
        "A",
        "https://www.helloworld.rs/",
        status="ACTIVE",
        access="public_api",
        docs_url="https://helloworld.rs/rss",
        connector_key="helloworld_rs",
        notes="Free Serbian IT jobs RSS. No key.",
    )
    add(
        192,
        "Posao.hr",
        "A",
        "https://www.posao.hr/",
        status="ACTIVE",
        access="public_api",
        docs_url="https://www.posao.hr/rss",
        connector_key="posao_hr",
        notes="Free Croatian jobs RSS (general board, filter via query). No key.",
    )
    add(
        193,
        "Jobweb Kenya",
        "A",
        "https://www.jobwebkenya.com/",
        status="ACTIVE",
        access="public_api",
        docs_url="https://www.jobwebkenya.com/feed/",
        connector_key="jobweb_kenya",
        notes="Free Kenya jobs RSS. No key. First Africa ACTIVE connector.",
    )
    add(
        197,
        "findmethatdamjob.nl",
        "A",
        "https://findmethatdamjob.nl/",
        status="ACTIVE",
        access="public_api",
        docs_url="https://findmethatdamjob.nl/docs/api/",
        connector_key="findmethatdamjob",
        notes=(
            "Free documented NL jobs API (gigsignal-api.fly.dev; location=amsterdam = NL-wide). "
            "Careers-page aggregator — not UWV/Werk.nl PES. ADR-003: no Werk.nl scrape."
        ),
    )
    add(
        198,
        "Dev Global Jobs",
        "A",
        "https://devglobaljobs.com/",
        status="ACTIVE",
        access="public_api",
        docs_url="https://devglobaljobs.com/developers",
        connector_key="devglobaljobs",
        notes=(
            "Free display API (no key; 120 req/min/IP). Attribution required. "
            "Default countries LU,BG via DEVGLOBALJOBS_COUNTRIES — fills LU/BG geo gaps. "
            "Live HTTP probe 200 (2026-10-21). Aggregator of public listings; not a national PES."
        ),
    )
    add(
        199,
        "ViewJobs",
        "A",
        "https://www.viewjobs.com.au/",
        status="ACTIVE",
        access="public_api",
        docs_url="https://www.viewjobs.com.au/for-agents",
        connector_key="viewjobs",
        notes=(
            "Free AU jobs MCP (Streamable HTTP /api/mcp search_jobs; no key). "
            "Regional + metro Australia. Keep listing URLs (utm attribution). "
            "Not Seek scrape — documented agent search surface (ADR-003)."
        ),
    )
    add(
        200,
        "okemprego",
        "A",
        "https://www.okemprego.com/",
        status="ACTIVE",
        access="public_api",
        docs_url="https://www.okemprego.com/pt/api",
        connector_key="okemprego",
        notes=(
            "Free PT/BR/AO jobs API (no key). Default OKEMPREGO_COUNTRIES=pt + category=it-data. "
            "Cite canonical okemprego URL (terms). Complements Landing.jobs for Iberia IT."
        ),
    )
    add(
        201,
        "Canada Job Bank (open data)",
        "A",
        "https://www.jobbank.gc.ca/",
        status="ACTIVE",
        access="open_data",
        docs_url=(
            "https://open.canada.ca/data/en/dataset/ea639e28-c0fc-48bf-b5dd-b8899bd43072"
        ),
        connector_key="jobbank_ca",
        notes=(
            "ESDC monthly Job Bank CSV (Open Government Licence – Canada). "
            "CKAN package_show picks latest EN all-job-postings TSV; IT via NOC21 212/2222 + title keywords. "
            "Snapshot IDs are point-in-time — URL is Job Bank search deep-link (not expired /jobposting/). "
            "No HTML scrape (ADR-003)."
        ),
    )
    add(
        195,
        "MPSV / Úřad práce — Volná místa",
        "A",
        "https://data.mpsv.cz/web/data/volna-mista-za-celou-cr",
        status="ACTIVE",
        access="open_data",
        docs_url="https://data.mpsv.cz/od/soubory/volna-mista/volna-mista.json",
        connector_key="mpsv",
        notes=(
            "CZ PES open-data dump (daily). Documented JSON URL 404 as of 2026-10-21; "
            "connector falls back to streaming volna-mista.jsonld (~180MB) with bounded "
            "IT keyword filter (MAX_RECORDS=300). No auth. Schema: volna-mista.schema.json."
        ),
    )
    add(150, "O*NET Web Services", "G", "https://services.onetcenter.org/", status="NEEDS_CREDENTIALS", access="api_key", notes="Registration required.")

    # --- H procurement ---
    for cid, name, url in [
        (151, "TED", "https://ted.europa.eu/"),
        (152, "EU Funding & Tenders Portal", "https://ec.europa.eu/info/funding-tenders/opportunities/portal/"),
        (153, "UK Contracts Finder", "https://www.contractsfinder.service.gov.uk/"),
        (154, "UK Find a Tender", "https://www.find-tender.service.gov.uk/"),
        (155, "US SAM.gov", "https://sam.gov/"),
        (156, "US FPDS", "https://www.fpds.gov/"),
        (157, "US GSA eBuy", "https://www.gsa.gov/"),
        (158, "CanadaBuys", "https://canadabuys.canada.ca/"),
        (159, "AusTender", "https://www.tenders.gov.au/"),
        (160, "Swiss SIMAP", "https://www.simap.ch/"),
        (161, "Open Contracting Data Standard", "https://standard.open-contracting.org/"),
        (162, "Open Contracting Partnership", "https://www.open-contracting.org/"),
    ]:
        add(cid, name, "H", url, status="UNDER_REVIEW", access="open_data_or_portal", notes="Procurement ≠ job postings. Separate ingest path Later; contract value ≠ day rate.")

    # --- I discovery support ---
    add(163, "Public APIs", "I", "https://github.com/public-apis/public-apis", status="VALIDATED", access="directory", notes="Discovery directory only — not a job source.")
    add(164, "API List", "I", "https://apilist.fun/", status="VALIDATED", access="directory", notes="Discovery directory only.")
    add(165, "Programmable Search Engine", "I", "https://programmablesearchengine.google.com/", status="NEEDS_CREDENTIALS", access="api_key", notes="CSE for discovery; not a job board.")
    add(166, "Common Crawl", "I", "https://commoncrawl.org/", status="REJECTED", access="crawl_index", notes="Not authorized job harvest path for FMI; ToS/use-case mismatch.")
    add(167, "Internet Archive", "I", "https://archive.org/", status="UNDER_REVIEW", access="api", notes="Historical pages; not primary live jobs.")
    add(168, "Schema.org JobPosting", "I", "https://schema.org/JobPosting", status="VALIDATED", access="standard", notes="Schema for normalization.")
    add(169, "Google Job Posting docs", "I", "https://developers.google.com/search/docs/appearance/structured-data/job-posting", status="DISCOVERED", access="duplicate", duplicate_of=13, notes="Same as catalog_id 13.")

    # Manual import always available
    add(170, "Manual CSV/JSON/XLSX Import", "I", "https://localhost/manual", status="ACTIVE", access="manual_import", connector_key="manual_import", notes="Lawful structured import path.")
