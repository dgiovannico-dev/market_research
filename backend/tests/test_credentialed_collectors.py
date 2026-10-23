import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from app.collectors.adzuna import AdzunaCollector, resolve_adzuna_countries
from app.collectors.careerjet import CareerjetCollector, resolve_careerjet_locales
from app.collectors.bundesagentur import BundesagenturCollector
from app.collectors.findwork import FindworkCollector
from app.collectors.france_travail import FranceTravailCollector
from app.collectors.jooble import JoobleCollector
from app.collectors.usajobs import USAJobsCollector
from app.core.config import get_settings
from app.fx.rates import fetch_open_exchange_rates


def test_resolve_adzuna_countries_prefers_list():
    assert resolve_adzuna_countries("gb, us, AU", "de") == ["gb", "us", "au"]


def test_resolve_adzuna_countries_falls_back_to_single():
    assert resolve_adzuna_countries("", "it") == ["it"]
    assert resolve_adzuna_countries("  ", "") == ["gb"]


def test_adzuna_fails_closed_without_keys(monkeypatch):
    monkeypatch.setenv("ADZUNA_APP_ID", "")
    monkeypatch.setenv("ADZUNA_APP_KEY", "")
    get_settings.cache_clear()
    result = asyncio.run(AdzunaCollector().collect("software"))
    assert result.records == []
    assert any("ADZUNA" in e for e in result.errors)


def test_adzuna_collects_multiple_countries(monkeypatch):
    monkeypatch.setenv("ADZUNA_APP_ID", "test-app-id")
    monkeypatch.setenv("ADZUNA_APP_KEY", "test-app-key")
    monkeypatch.setenv("ADZUNA_COUNTRIES", "gb,us")
    monkeypatch.setenv("ADZUNA_COUNTRY", "de")
    get_settings.cache_clear()

    def _job(job_id: int, title: str) -> dict:
        return {
            "id": job_id,
            "title": title,
            "redirect_url": f"https://example.com/{job_id}",
            "created": "2026-01-15T12:00:00Z",
            "company": {"display_name": "Acme"},
            "location": {"display_name": "Remote"},
            "description": "desc",
        }

    responses = {
        "gb": {"results": [_job(101, "GB Engineer")]},
        "us": {"results": [_job(202, "US Engineer")]},
    }

    async def fake_get(url, params=None):  # noqa: ARG001
        country = url.rstrip("/").split("/")[-3]
        resp = MagicMock()
        resp.status_code = 200
        resp.raise_for_status = MagicMock()
        resp.json.return_value = responses[country]
        return resp

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=fake_get)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("app.collectors.adzuna.httpx.AsyncClient", return_value=mock_client):
        result = asyncio.run(AdzunaCollector().collect("software"))

    assert result.errors == []
    assert result.pages_scanned == 2
    assert {r.source_job_id for r in result.records} == {"101", "202"}
    by_id = {r.source_job_id: r for r in result.records}
    assert by_id["101"].raw.get("_adzuna_country") == "gb"
    assert by_id["202"].raw.get("_adzuna_country") == "us"
    urls = [call.args[0] for call in mock_client.get.await_args_list]
    assert any("/jobs/gb/search/1" in u for u in urls)
    assert any("/jobs/us/search/1" in u for u in urls)
    assert not any("/jobs/de/" in u for u in urls)


def test_usajobs_fails_closed_without_keys(monkeypatch):
    monkeypatch.setenv("USAJOBS_API_KEY", "")
    monkeypatch.setenv("USAJOBS_USER_AGENT", "")
    get_settings.cache_clear()
    result = asyncio.run(USAJobsCollector().collect("software"))
    assert result.records == []
    assert any("USAJOBS" in e for e in result.errors)


def test_usajobs_requires_user_agent(monkeypatch):
    monkeypatch.setenv("USAJOBS_API_KEY", "dummy-key")
    monkeypatch.setenv("USAJOBS_USER_AGENT", "")
    get_settings.cache_clear()
    result = asyncio.run(USAJobsCollector().collect("software"))
    assert result.records == []
    assert any("USER_AGENT" in e for e in result.errors)


def test_usajobs_passes_job_category_code(monkeypatch):
    monkeypatch.setenv("USAJOBS_API_KEY", "dummy-key")
    monkeypatch.setenv("USAJOBS_USER_AGENT", "dev@example.com")
    monkeypatch.setenv("USAJOBS_JOB_CATEGORY_CODE", "2210")
    get_settings.cache_clear()

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {"SearchResult": {"SearchResultItems": []}}

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_resp)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("app.collectors.usajobs.httpx.AsyncClient", return_value=mock_client):
        result = asyncio.run(USAJobsCollector().collect("software"))

    assert result.errors == []
    params = mock_client.get.await_args.kwargs.get("params") or {}
    assert params.get("JobCategoryCode") == "2210"
    assert params.get("Keyword")


def test_france_travail_fails_closed_without_keys(monkeypatch):
    monkeypatch.setenv("FRANCE_TRAVAIL_CLIENT_ID", "")
    monkeypatch.setenv("FRANCE_TRAVAIL_CLIENT_SECRET", "")
    get_settings.cache_clear()
    result = asyncio.run(FranceTravailCollector().collect("developpeur"))
    assert result.records == []
    assert result.pages_scanned == 0
    assert any("FRANCE_TRAVAIL" in e for e in result.errors)


def test_france_travail_build_search_params_it_density():
    from app.collectors.france_travail import build_search_params, parse_content_range_total

    params = build_search_params("python", start=0)
    assert params["motsCles"] == "python"
    assert params["range"] == "0-49"
    assert params["codeROME"] == ["M1805", "M1802", "M1806"]
    assert build_search_params("python", start=50)["range"] == "50-99"
    assert parse_content_range_total("offres 0-49/120") == 120
    assert parse_content_range_total("0-49/80") == 80
    assert parse_content_range_total(None) is None


def test_france_travail_mocked_search_and_pagination(monkeypatch):
    monkeypatch.setenv("FRANCE_TRAVAIL_CLIENT_ID", "ft-id")
    monkeypatch.setenv("FRANCE_TRAVAIL_CLIENT_SECRET", "ft-secret")
    get_settings.cache_clear()

    def _offre(job_id: str, title: str) -> dict:
        return {
            "id": job_id,
            "intitule": title,
            "description": "desc",
            "dateCreation": "2026-01-15T12:00:00Z",
            "typeContrat": "CDI",
            "lieuTravail": {"libelle": "Paris"},
            "entreprise": {"nom": "Acme"},
            "origineOffre": {"urlOrigine": f"https://example.com/{job_id}"},
        }

    page1 = [_offre(f"p1-{i}", f"Dev {i}") for i in range(50)]
    page2 = [_offre("p2-1", "Dev page2")]

    token_resp = MagicMock()
    token_resp.status_code = 200
    token_resp.raise_for_status = MagicMock()
    token_resp.json.return_value = {"access_token": "tok-123"}

    search_calls: list[dict] = []

    def _search_resp(payload: dict, content_range: str):
        resp = MagicMock()
        resp.status_code = 200
        resp.raise_for_status = MagicMock()
        resp.json.return_value = payload
        resp.headers = {"Content-Range": content_range}
        return resp

    async def fake_post(url, **kwargs):  # noqa: ARG001
        return token_resp

    async def fake_get(url, params=None, headers=None):  # noqa: ARG001
        search_calls.append(dict(params or {}))
        rng = (params or {}).get("range", "")
        if rng == "0-49":
            return _search_resp({"resultats": page1}, "offres 0-49/51")
        if rng == "50-99":
            return _search_resp({"resultats": page2}, "offres 50-50/51")
        raise AssertionError(f"unexpected range {rng!r}")

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(side_effect=fake_post)
    mock_client.get = AsyncMock(side_effect=fake_get)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("app.collectors.france_travail.httpx.AsyncClient", return_value=mock_client):
        result = asyncio.run(FranceTravailCollector().collect("developpeur python"))

    assert result.errors == []
    assert result.pages_scanned == 2
    assert len(result.records) == 51
    assert {r.source_job_id for r in result.records} >= {"p1-0", "p2-1"}
    assert len(search_calls) == 2
    assert search_calls[0]["motsCles"]
    assert search_calls[0]["codeROME"] == ["M1805", "M1802", "M1806"]
    assert search_calls[0]["range"] == "0-49"
    assert search_calls[1]["range"] == "50-99"


def test_france_travail_mocked_single_page_stops(monkeypatch):
    monkeypatch.setenv("FRANCE_TRAVAIL_CLIENT_ID", "ft-id")
    monkeypatch.setenv("FRANCE_TRAVAIL_CLIENT_SECRET", "ft-secret")
    get_settings.cache_clear()

    token_resp = MagicMock()
    token_resp.status_code = 200
    token_resp.raise_for_status = MagicMock()
    token_resp.json.return_value = {"access_token": "tok-123"}

    search_resp = MagicMock()
    search_resp.status_code = 200
    search_resp.raise_for_status = MagicMock()
    search_resp.headers = {"Content-Range": "offres 0-0/1"}
    search_resp.json.return_value = {
        "resultats": [
            {
                "id": "only-1",
                "intitule": "Dev",
                "origineOffre": {"urlOrigine": "https://example.com/1"},
            }
        ]
    }

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=token_resp)
    mock_client.get = AsyncMock(return_value=search_resp)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("app.collectors.france_travail.httpx.AsyncClient", return_value=mock_client):
        result = asyncio.run(FranceTravailCollector().collect("java"))

    assert result.errors == []
    assert result.pages_scanned == 1
    assert len(result.records) == 1
    assert mock_client.get.await_count == 1


def test_bundesagentur_fails_closed_without_key(monkeypatch):
    monkeypatch.setenv("BUNDESAGENTUR_API_KEY", "")
    get_settings.cache_clear()
    result = asyncio.run(BundesagenturCollector().collect("Informatik"))
    assert result.records == []
    assert any("BUNDESAGENTUR" in e for e in result.errors)


def test_jooble_fails_closed_without_key(monkeypatch):
    monkeypatch.setenv("JOOBLE_API_KEY", "")
    get_settings.cache_clear()
    result = asyncio.run(JoobleCollector().collect("software engineer"))
    assert result.records == []
    assert any("JOOBLE" in e for e in result.errors)


def test_resolve_careerjet_locales_defaults():
    assert resolve_careerjet_locales("") == [
        "it_IT",
        "de_DE",
        "de_CH",
        "fr_CH",
        "fr_LU",
    ]
    assert resolve_careerjet_locales("de_DE, it_IT, de_DE") == ["de_DE", "it_IT"]


def test_careerjet_fails_closed_without_key(monkeypatch):
    monkeypatch.setenv("CAREERJET_API_KEY", "")
    monkeypatch.setenv("CAREERJET_USER_IP", "203.0.113.1")
    get_settings.cache_clear()
    result = asyncio.run(CareerjetCollector().collect("software"))
    assert result.records == []
    assert result.pages_scanned == 0
    assert any("CAREERJET_API_KEY" in e for e in result.errors)


def test_careerjet_requires_user_ip(monkeypatch):
    monkeypatch.setenv("CAREERJET_API_KEY", "publisher-key")
    monkeypatch.setenv("CAREERJET_USER_IP", "")
    get_settings.cache_clear()
    result = asyncio.run(CareerjetCollector().collect("python"))
    assert result.records == []
    assert any("CAREERJET_USER_IP" in e for e in result.errors)


def test_careerjet_mock_multi_locale(monkeypatch):
    monkeypatch.setenv("CAREERJET_API_KEY", "publisher-key")
    monkeypatch.setenv("CAREERJET_USER_IP", "203.0.113.1")
    monkeypatch.setenv("CAREERJET_LOCALES", "it_IT,de_DE")
    monkeypatch.setenv("CAREERJET_CONTRACT_TYPE", "c")
    get_settings.cache_clear()

    def _job(title: str, url: str) -> dict:
        return {
            "title": title,
            "company": "Acme",
            "date": "Wed, 15 Nov 2025 19:13:43 GMT",
            "description": "snippet",
            "locations": "Milan",
            "salary": "€50k",
            "url": url,
        }

    responses = {
        "it_IT": {
            "type": "JOBS",
            "hits": 1,
            "pages": 1,
            "jobs": [_job("IT Dev", "https://example.com/it-1")],
        },
        "de_DE": {
            "type": "JOBS",
            "hits": 1,
            "pages": 1,
            "jobs": [_job("DE Dev", "https://example.com/de-1")],
        },
    }

    async def fake_get(url, params=None):  # noqa: ARG001
        locale = (params or {}).get("locale_code", "")
        resp = MagicMock()
        resp.status_code = 200
        resp.raise_for_status = MagicMock()
        resp.json.return_value = responses[locale]
        return resp

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=fake_get)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch(
        "app.collectors.careerjet.httpx.AsyncClient", return_value=mock_client
    ) as client_cls:
        result = asyncio.run(CareerjetCollector().collect("software engineer"))

    assert result.errors == []
    assert result.pages_scanned == 2
    assert {r.title for r in result.records} == {"IT Dev", "DE Dev"}
    assert all(r.raw.get("_careerjet_locale") in {"it_IT", "de_DE"} for r in result.records)
    calls = mock_client.get.await_args_list
    assert len(calls) == 2
    for call in calls:
        params = call.kwargs.get("params") or {}
        assert params.get("contract_type") == "c"
        assert params.get("user_ip") == "203.0.113.1"
        assert params.get("keywords") == "software engineer"
    init_headers = client_cls.call_args.kwargs.get("headers") or {}
    assert init_headers.get("Authorization", "").startswith("Basic ")


def test_findwork_fails_closed_without_key(monkeypatch):
    monkeypatch.setenv("FINDWORK_API_KEY", "")
    get_settings.cache_clear()
    result = asyncio.run(FindworkCollector().collect("python"))
    assert result.records == []
    assert result.pages_scanned == 0
    assert any("FINDWORK" in e for e in result.errors)


def test_findwork_missing_query():
    result = asyncio.run(FindworkCollector().collect(""))
    assert result.records == []
    assert result.errors == ["missing_query"]


def test_findwork_mock_search(monkeypatch):
    monkeypatch.setenv("FINDWORK_API_KEY", "test-token")
    monkeypatch.setenv("FINDWORK_LOCATION", "remote")
    get_settings.cache_clear()

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [
            {
                "id": 42,
                "title": "Python Engineer",
                "company_name": "Acme",
                "location": "Remote",
                "remote": True,
                "pub_date": "2026-03-01T12:00:00Z",
                "url": "https://findwork.dev/jobs/42/",
                "description": "Build APIs",
                "keywords": ["python", "django"],
            }
        ],
    }

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_resp)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch(
        "app.collectors.findwork.httpx.AsyncClient", return_value=mock_client
    ) as client_cls:
        result = asyncio.run(FindworkCollector().collect("python OR java"))

    assert result.errors == []
    assert len(result.records) == 1
    job = result.records[0]
    assert job.source_job_id == "42"
    assert job.title == "Python Engineer"
    assert job.company == "Acme"
    assert job.remote_hint is True
    assert "python" in job.tags
    init_kwargs = client_cls.call_args.kwargs
    assert init_kwargs.get("headers", {}).get("Authorization") == "Token test-token"
    params = mock_client.get.await_args.kwargs.get("params") or {}
    assert params.get("search") == "python"
    assert params.get("location") == "remote"
    assert params.get("page") == 1
    assert mock_client.get.await_args.args[0] == "https://findwork.dev/api/jobs/"


def test_oxr_reports_not_configured_without_key(monkeypatch):
    monkeypatch.setenv("OPEN_EXCHANGE_RATES_APP_ID", "")
    get_settings.cache_clear()
    result = asyncio.run(fetch_open_exchange_rates())
    assert result["enabled"] is False
    assert result["evidence_kind"] == "not_configured"
