from functools import lru_cache
from typing import Self

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_PROD_ENVS = frozenset({"production", "prod"})


def assert_safe_prod_cors(app_env: str, origins: list[str]) -> None:
    """Fail closed in production when CORS is empty or wildcard."""
    if app_env.strip().lower() not in _PROD_ENVS:
        return
    if not origins or "*" in origins:
        raise ValueError(
            "In production (APP_ENV=production|prod), API_CORS_ORIGINS must be a "
            "non-empty comma-separated list of explicit origins (no '*')."
        )


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # development|dev (default) | production|prod — prod rejects empty/* CORS
    app_env: str = "development"
    database_url: str = "postgresql+psycopg://fmi:fmi_dev_password_change_me@localhost:5432/fmi"
    # Prefer a SELECT-only role for MCP stdio (falls back to database_url if empty)
    database_url_readonly: str = ""
    redis_url: str = "redis://localhost:6379/0"
    # Include both localhost and 127.0.0.1 — browsers treat them as distinct origins.
    api_cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    api_key: str = ""
    # Ops mutating endpoints (connector credentials PUT/DELETE) — empty = reject writes
    ops_api_token: str = ""
    # Fernet key for source_credentials ciphertext (python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
    credentials_master_key: str = ""
    # Keycloak / OIDC (ADR-009). When oidc_enabled, browser routes expect Bearer JWT.
    oidc_enabled: bool = False
    oidc_issuer: str = ""
    oidc_audience: str = ""
    oidc_client_id: str = "fmi-frontend"
    # Optional override; default = {issuer}/protocol/openid-connect/certs
    oidc_jwks_url: str = ""
    # When true and OIDC on, reject requests without valid user JWT (API_KEY still bypasses for machines)
    oidc_require_user: bool = False
    classification_mode: str = "hybrid"  # rules | llm | hybrid
    llm_provider: str = "none"  # none | ollama | vllm
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    vllm_base_url: str = "http://localhost:8001/v1"
    vllm_api_key: str = ""
    vllm_model: str = ""
    fx_hours_per_day: float = 8.0
    log_level: str = "INFO"
    methodology_version: str = "1.1.0"
    enable_scheduler: bool = False
    scheduler_interval_seconds: int = 3600
    rate_limit_per_minute: int = 180
    # memory (default) | redis — redis uses REDIS_URL; falls back to memory if unavailable
    rate_limit_backend: str = "memory"
    # Baseline response headers (X-Content-Type-Options, X-Frame-Options, Referrer-Policy)
    security_headers_enabled: bool = True

    # Comma-separated public ATS board/site identifiers (no secrets)
    # Public board tokens last HTTP-probed green (2026-10-21); re-probe before expanding
    greenhouse_boards: str = (
        "airbnb,stripe,gitlab,discord,cloudflare,figma,twilio,datadog,dropbox,coinbase,"
        "robinhood,mongodb,elastic,databricks,okta,pendo,duolingo,asana,block,anthropic,"
        "scaleai,brex,affirm,gusto,pinterest,reddit,coursera,khanacademy,lyft,"
        "waymo,spacex,janestreet,instacart,roblox,epicgames,mozilla,pagerduty,"
        "airtable,vercel,mercury,"
        "adyen,grafanalabs,natera,deliveroo,celonis,riotgames,intercom,getyourguide,"
        "chime,monzo,nintendo,fastly,sofi,launchdarkly,beamtherapeutics,billcom,"
        "n26,contentful,honeycomb,melio,flatironhealth,wise,generatebiomedicines,"
        "ginkgobioworks,circleci,cockroachlabs,planetscale,typeform,netlify,"
        # IT focus (probed 2026-10-23): thefork Milan/Turin; truelayer Milan
        "thefork,truelayer"
    )
    lever_sites: str = "spotify,palantir,wealthfront,musixmatch"
    ashby_orgs: str = (
        "notion,linear,vercel,openai,ramp,cursor,warp,granola,runway,supabase,"
        "mercor,harvey,sierra,cognition,perplexity,midjourney,snowflake,replit,"
        "plaid,miro,ashby,elevenlabs,temporal,webflow,sentry,docker,"
        "clickhouse,cohere,langchain,baseten,fireworks,lovable,modal,n8n,"
        "amplitude,hex,watershed,render,level,redis,workos,latchbio,anyscale,"
        "column,mesh,insitro,phantom,airbyte,posthog,moderntreasury,railway,"
        # IT focus: satispay (Ashby); docebo Milan/Biassono (probed 2026-10-23)
        "satispay,docebo"
    )
    # SmartRecruiters public company identifiers (comma-separated)
    # Talan/Devoteam: LU IT consultancies (probed country=lu 2026-10-22)
    smartrecruiters_companies: str = (
        "endava,ServiceNow,DeliveryHero,Wise,Allegro,Uber,Talan,Devoteam"
    )
    # Personio public career boards: https://{slug}.jobs.personio.de/search.json
    personio_companies: str = (
        "1komma5grad,chrono24,finanzguru,tado,kiwi,personio-gmbh,alcemy,researchgate,"
        "cloover,42watt,autonomous-teaming,aampere,cargoboard,getquin,getsafe"
    )
    # Teamtailor public career hosts (subdomain or custom domain) → GET https://{host}/jobs.json
    teamtailor_hosts: str = (
        "polestar.teamtailor.com,careers.oatly.com,storytel.teamtailor.com,"
        "krea.teamtailor.com,hedvig.teamtailor.com,"
        "doktor.teamtailor.com,schibsted.teamtailor.com,foodora.teamtailor.com,"
        "securitas.teamtailor.com,mindler.teamtailor.com,"
        "careers.voi.com,instabee.teamtailor.com,iqm.teamtailor.com,lunar.teamtailor.com,"
        "careers.acast.com,careers.nordhealth.com,rebtel.teamtailor.com,vipps.teamtailor.com,"
        "bambuser.teamtailor.com,detectify.teamtailor.com,netinsight.teamtailor.com,"
        "career.knowit.se,hiq.teamtailor.com,omegapoint.teamtailor.com,siili.teamtailor.com,"
        "pinetree.teamtailor.com"
    )
    # Recruitee Careers Site slugs → GET https://{slug}.recruitee.com/api/offers/ (keyless until 2027-02-10)
    recruitee_slugs: str = (
        "jobs,personio,bunq,adjust,riverflex,holded,hostaway,simvia,intelic"
    )
    # Pinpoint public postings → GET https://{subdomain}.pinpointhq.com/postings.json
    pinpoint_subdomains: str = (
        "made-tech,accenture,bendingspoons,arm,freeagent,workwithus,imagination,confluence,"
        "hazelcast,smartthings"
    )
    # Workable public careers widget → GET apply.workable.com/api/v1/widget/accounts/{slug}
    # Prefer non-empty boards; many guessed brand slugs return jobs:[]. Back off on HTTP 429.
    # moneyfarm: IT fintech (probed 2026-10-22, non-empty widget)
    workable_slugs: str = "huggingface,jasper,skillshare,riot,moneyfarm"
    # Workday public CXS → POST https://{tenant}.{wd}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs
    # CSV of tenant:wdN:siteSlug (probed non-empty boards). Empty → non-runnable.
    # Prefer tech/engineering-heavy boards; skip retail megaboards (CVS/Lowes/Target).
    workday_tenants: str = (
        "nvidia:wd5:NVIDIAExternalCareerSite,redhat:wd5:jobs,intel:wd1:External,"
        "salesforce:wd12:External_Career_Site,adobe:wd5:external_experienced,paypal:wd1:jobs,"
        "micron:wd1:External,nxp:wd3:careers,analogdevices:wd1:External,"
        "cisco:wd5:Cisco_Careers,pfizer:wd1:PfizerCareers,workday:wd5:Workday,"
        "autodesk:wd1:Ext,tmobile:wd1:External,bbva:wd3:BBVA,"
        "paloaltonetworks:wd5:panwexternalcareers,crowdstrike:wd5:crowdstrikecareers,"
        "capitalone:wd12:Capital_One,mastercard:wd1:CorporateCareers,visa:wd5:Visa,"
        "amat:wd1:External,accenture:wd103:AccentureCareers,ms:wd5:External,citi:wd5:2,"
        "abb:wd3:External_Career_Page,philips:wd3:jobs-and-careers,amgen:wd1:Careers,"
        "roche:wd3:roche-ext,sanofi:wd3:SanofiCareers,msd:wd5:SearchJobs,"
        "gilead:wd1:gileadcareers,modernatx:wd1:M_tx,biibhr:wd3:external,"
        "geaerospace:wd5:GE_ExternalSite,gevernova:wd5:Vernova_ExternalSite,"
        "jj:wd5:JJ,ghr:wd1:lateral-us,"
        # CH/LU: Swisscom; Julius Baer (Zurich + Luxembourg offices, probed 2026-10-23)
        "swisscom:wd103:SwisscomExternalCareers,"
        "juliusbaer:wd3:External"
    )
    # BambooHR public careers → GET https://{slug}.bamboohr.com/careers/list (no follow redirect)
    # Default flyio (probed 200+jobs); DC egress may still 503 — see data/sources/catalog.json
    bamboohr_companies: str = "flyio"
    # Robert Half public XML feeds: ISO country suffixes for general_rh-{cc}.xml
    robert_half_countries: str = "ch,uk"
    # Free public remote boards (prefer over paid aggregator APIs)
    himalayas_page_limit: int = 40
    # DevITJobs hosts (comma-separated TLDs: uk, com, …)
    devitjobs_hosts: str = "uk,com"
    # Adzuna Job Search API (https://developer.adzuna.com/) — leave empty to keep non-runnable
    adzuna_app_id: str = ""
    adzuna_app_key: str = ""
    # Single-country fallback (used when ADZUNA_COUNTRIES is empty)
    adzuna_country: str = "gb"
    # Comma-separated country paths (e.g. gb,us,au,it,ch); empty → ADZUNA_COUNTRY → gb
    # Include it,ch for IT/CH coverage when keys + commercial licence allow product use
    adzuna_countries: str = "gb,us,au,it,de,ch,fr"
    # USAJOBS (https://developer.usajobs.gov/) — leave empty to keep non-runnable
    usajobs_api_key: str = ""
    usajobs_user_agent: str = ""
    # Optional OPM series filter (e.g. 2210 = IT Management); empty = Keyword-only
    usajobs_job_category_code: str = ""
    # Reed.co.uk — free RSS by default; optional REED_API_KEY for JSON search API
    reed_api_key: str = ""
    # France Travail Offres d'emploi v2 (francetravail.io) — OAuth2 client credentials
    france_travail_client_id: str = ""
    france_travail_client_secret: str = ""
    france_travail_scope: str = "api_offresdemploiv2 o2dsoffre"
    # Bundesagentur Jobsuche (rest.arbeitsagentur.de) — X-API-Key; leave empty to keep non-runnable
    bundesagentur_api_key: str = ""
    bundesagentur_location: str = "Berlin"
    # Jooble (https://jooble.org/api/about) — leave empty to keep non-runnable
    jooble_api_key: str = ""
    jooble_location: str = ""
    # Findwork.dev Jobs API (https://findwork.dev/developers/) — leave empty to keep non-runnable
    findwork_api_key: str = ""
    # Optional location filter (e.g. remote, city/country)
    findwork_location: str = ""
    # Find a Job UK DWP (https://www.api.gov.uk/dwp/find-a-job/) — leave empty to keep non-runnable
    findajob_dwp_api_id: str = ""
    findajob_dwp_api_key: str = ""
    # Optional location filter for `w=` (e.g. London, Scotland, E1W)
    findajob_dwp_location: str = ""
    # Freelancer.com REST 0.1 (OAuth access token) — leave empty to keep non-runnable
    freelancer_oauth_token: str = ""
    # Optional sandbox host override (default production)
    freelancer_api_base: str = "https://www.freelancer.com/api"
    # Upwork GraphQL (https://www.upwork.com/developer/) — leave empty to keep non-runnable
    upwork_oauth_token: str = ""
    # Optional organization / tenant id for X-Upwork-API-TenantId
    upwork_tenant_id: str = ""
    # Careerjet Partner API v4 (https://www.careerjet.com/partners/api/)
    careerjet_api_key: str = ""
    # End-user IP required by publisher API (set to your egress or permitted value)
    careerjet_user_ip: str = ""
    careerjet_user_agent: str = "FMI-MarketIntel/1.0"
    # Comma-separated locale_code values; empty → it_IT,de_DE,de_CH,fr_CH,fr_LU
    careerjet_locales: str = ""
    careerjet_location: str = ""
    # Optional contract_type filter (e.g. c = contract); empty = omit
    careerjet_contract_type: str = "c"
    # InfoJobs Developer API (https://developer.infojobs.net/) — HTTP Basic; leave empty to keep non-runnable
    infojobs_client_id: str = ""
    infojobs_client_secret: str = ""
    # Optional country slug (dictionary value, e.g. italia); empty = omit
    # Dictionary country slug (e.g. espana); empty = API default. Not Italy (site closed).
    infojobs_country: str = "espana"
    infojobs_max_results: int = 50
    # ADEM LU skills open data (CC0) — path to CSV for /stats/adem/skills-summary
    # Empty → endpoint returns not_configured (no auto-download of ~120MB portal file)
    adem_csv_path: str = ""
    # Dev Global Jobs free display API — ISO2 lowercase CSV (default lu,bg)
    devglobaljobs_countries: str = "lu,bg"
    # okemprego free API — ISO2 lowercase CSV (default pt; also supports br,ao)
    okemprego_countries: str = "pt"
    # Open Exchange Rates (optional FX overlay; Frankfurter/ECB remain primary)
    open_exchange_rates_app_id: str = ""
    # Demand Compass daily crawler budgets (SPEC-research-intents §6 / §8)
    sync_max_discovery_per_tick: int = 12
    sync_max_focus_per_tick: int = 10
    sync_max_collector_calls_per_intent: int = 5
    sync_max_total_collector_calls_per_tick: int = 100
    # Explicit ops smoke only — never used by daily tick
    ops_smoke_query: str = ""

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.api_cors_origins.split(",") if o.strip()]

    @model_validator(mode="after")
    def _reject_unsafe_prod_cors(self) -> Self:
        assert_safe_prod_cors(self.app_env, self.cors_origins_list)
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
