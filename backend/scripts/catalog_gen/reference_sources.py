"""Categories E (official stats), F (salary surveys), G (FX / taxonomy core)."""

from __future__ import annotations

from .registry import add


def register() -> None:
    # --- E official stats ---
    stat_e = [
        (97, "Eurostat", "https://ec.europa.eu/eurostat/", "open_data"),
        (98, "Cedefop Skills-OVATE", "https://www.cedefop.europa.eu/en/tools/skills-online-vacancies", "portal"),
        (99, "ESCO", "https://esco.ec.europa.eu/", "api"),
        (100, "OECD Data", "https://data.oecd.org/", "open_data"),
        (101, "ILOSTAT", "https://ilostat.ilo.org/", "open_data"),
        (102, "World Bank Data", "https://data.worldbank.org/", "open_data"),
        (103, "IMF Data", "https://www.imf.org/en/Data", "open_data"),
        (104, "UN Data", "https://data.un.org/", "open_data"),
        (105, "US Bureau of Labor Statistics", "https://www.bls.gov/data/", "api_key_optional"),
        (106, "US Census Bureau", "https://www.census.gov/data.html", "api_key"),
        (107, "US O*NET", "https://www.onetonline.org/", "api_key"),
        (108, "USAJOBS (stats ref)", "https://developer.usajobs.gov/", "duplicate"),
        (109, "Statistics Canada", "https://www.statcan.gc.ca/", "open_data"),
        (110, "Australian Bureau of Statistics", "https://www.abs.gov.au/", "open_data"),
        (111, "Australian Labour Market Insights", "https://labourmarketinsights.gov.au/", "portal"),
        (112, "Statistics New Zealand", "https://www.stats.govt.nz/", "open_data"),
        (113, "Swiss Federal Statistical Office", "https://www.bfs.admin.ch/", "open_data"),
        (114, "Salarium Switzerland", "https://www.salarium.bfs.admin.ch/", "portal"),
        (115, "SECO Switzerland", "https://www.seco.admin.ch/", "portal"),
        (116, "ISTAT", "https://www.istat.it/", "open_data"),
        (117, "INPS", "https://www.inps.it/", "portal"),
        (118, "Unioncamere Excelsior", "https://excelsior.unioncamere.net/", "portal"),
        (119, "Ministero del Lavoro IT", "https://www.lavoro.gov.it/", "portal"),
        (120, "Bundesagentur für Arbeit (stats)", "https://www.arbeitsagentur.de/", "duplicate"),
        (121, "France Travail (stats)", "https://www.francetravail.fr/", "duplicate"),
        (122, "UK ONS", "https://www.ons.gov.uk/", "open_data"),
        (123, "UK National Careers Service", "https://nationalcareers.service.gov.uk/", "portal"),
        (124, "Statistics Netherlands", "https://www.cbs.nl/", "open_data"),
        (125, "Statistics Norway", "https://www.ssb.no/", "open_data"),
        (126, "Statistics Sweden", "https://www.scb.se/", "open_data"),
        (127, "Statistics Finland", "https://stat.fi/", "open_data"),
        (128, "Statistics Denmark", "https://www.dst.dk/", "open_data"),
        (129, "Statistics Poland", "https://stat.gov.pl/", "open_data"),
        (130, "Stats NZ", "https://www.stats.govt.nz/", "duplicate"),
    ]
    for cid, name, url, access in stat_e:
        if access == "duplicate":
            dup = {108: 7, 120: 30, 121: 31, 130: 112}[cid]
            add(cid, name, "E", url, status="DISCOVERED", access="duplicate", duplicate_of=dup, notes=f"Duplicate reference of catalog_id {dup}.")
        elif cid == 97:
            add(
                cid,
                name,
                "E",
                url,
                status="VALIDATED",
                access="public_api",
                docs_url="https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/",
                notes="Free dissemination API via GET /api/v1/stats/eurostat/series. Official statistics reference only — never mixed into observed job KPIs.",
            )
        elif cid == 99:
            add(
                cid,
                name,
                "E",
                url,
                status="DISCOVERED",
                access="duplicate",
                duplicate_of=149,
                notes="Duplicate of catalog_id 149 (ESCO API taxonomy helper).",
            )
        else:
            add(cid, name, "E", url, status="UNDER_REVIEW", access=access, notes="Official statistics — import via datasets/API; do not mix incomparable series. Not wired as job connector.")

    # --- F salary surveys ---
    for cid, name, url in [
        (131, "Stack Overflow Developer Survey", "https://survey.stackoverflow.co/"),
        (132, "JetBrains Developer Ecosystem", "https://www.jetbrains.com/lp/devecosystem/"),
        (133, "GitHub Octoverse", "https://github.blog/news-insights/octoverse/"),
        (134, "CNCF Reports", "https://www.cncf.io/reports/"),
        (135, "DORA", "https://dora.dev/"),
        (136, "Levels.fyi", "https://www.levels.fyi/"),
        (137, "Glassdoor", "https://www.glassdoor.com/"),
        (138, "PayScale", "https://www.payscale.com/"),
        (139, "Salary.com", "https://www.salary.com/"),
        (140, "Hays Salary Guides", "https://www.hays.com/salary-guide"),
        (141, "Robert Half Salary Guides", "https://www.roberthalf.com/salary-guide"),
        (142, "Michael Page Salary Guides", "https://www.michaelpage.com/salary-guide"),
    ]:
        add(cid, name, "F", url, status="UNDER_REVIEW", access="report_or_dataset", notes="Survey/report — use lawful download/import; do not scrape paywalled pages. Not a live job connector.")

    # --- G FX / taxonomy (core; O*NET 150 registered after extended aggregators) ---
    add(
        143,
        "ECB Data API",
        "G",
        "https://data.ecb.europa.eu/help/api/data",
        status="ACTIVE",
        access="public_api",
        connector_key="ecb_fx",
        notes="EXR probe 200; FX helper implemented. Not a job connector — seed maps to connector_status=disabled.",
    )
    add(144, "Open Exchange Rates", "G", "https://openexchangerates.org/", status="NEEDS_CREDENTIALS", access="api_key", docs_url="https://docs.openexchangerates.org/", notes="Optional FX overlay via OPEN_EXCHANGE_RATES_APP_ID on GET /api/v1/fx/rates; Frankfurter/ECB remain primary. Not a job connector.")
    add(
        145,
        "Frankfurter",
        "G",
        "https://www.frankfurter.app/",
        status="ACTIVE",
        access="public_api",
        docs_url="https://api.frankfurter.app/",
        connector_key="frankfurter",
        notes="Live rates 200; FX helper primary. Not a job connector — seed maps to connector_status=disabled.",
    )
    add(146, "ExchangeRate-API", "G", "https://www.exchangerate-api.com/", status="NEEDS_CREDENTIALS", access="api_key", notes="API key required for production tiers.")
    add(147, "ISO 4217", "G", "https://www.iso.org/iso-4217-currency-codes.html", status="VALIDATED", access="standard", notes="Currency code standard reference (static).")
    add(148, "ISO 3166", "G", "https://www.iso.org/iso-3166-country-codes.html", status="VALIDATED", access="standard", notes="Country code standard reference (static).")
    add(
        149,
        "ESCO API",
        "G",
        "https://esco.ec.europa.eu/en/use-esco",
        status="VALIDATED",
        access="public_api",
        docs_url="https://ec.europa.eu/esco/api",
        notes="Free public search API validated via GET /api/v1/taxonomy/esco/search. Taxonomy reference only — not a job connector or rate source.",
    )
    add(
        174,
        "JobTech Taxonomy API",
        "G",
        "https://taxonomy.api.jobtechdev.se/",
        status="VALIDATED",
        access="public_api",
        docs_url="https://taxonomy.api.jobtechdev.se/",
        notes="Free Swedish labour taxonomy autocomplete via GET /api/v1/taxonomy/jobtech/search. Reference only — not jobs/rates.",
    )
