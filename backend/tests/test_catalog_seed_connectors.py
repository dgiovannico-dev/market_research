"""Dry-run: catalog keys + seed enablement predicates (no DB / Docker)."""

from __future__ import annotations

from app.collectors.credentials import has_credentials
from app.collectors.registry import COLLECTORS, CREDENTIALED_SCAFFOLDS
from app.core.config import get_settings
from app.sources.catalog import load_catalog
from app.storage.seed import _STATUS_TO_CONNECTOR

# Free public connectors expected enabled after seed without API keys.
_FREE_ACTIVE = ("tecnoempleo", "le_forem", "mpsv", "findmethatdamjob", "nav_stilling_feed")
# Credentialed scaffold: catalog NEEDS_CREDENTIALS; enabled only when key present.
_CREDENTIALED = ("findwork", "findajob_dwp", "freelancer", "upwork", "careerjet", "infojobs")


def _catalog_by_connector_key() -> dict[str, dict]:
    data = load_catalog()
    out: dict[str, dict] = {}
    for item in data.get("sources") or []:
        key = item.get("connector_key")
        if key and not item.get("duplicate_of"):
            out[key] = item
    return out


def _seed_would_enable(key: str, item: dict) -> bool:
    """Mirror seed_reference_data / _sync_catalog_sources runnable rules (no DB)."""
    vstatus = item.get("verification_status") or "DISCOVERED"
    if key not in COLLECTORS:
        return False
    if key in CREDENTIALED_SCAFFOLDS:
        return has_credentials(key)
    if key in {
        "ashby",
        "greenhouse",
        "lever",
        "smartrecruiters",
        "personio",
        "teamtailor",
        "recruitee",
        "pinpoint",
        "workable",
        "workday",
        "bamboohr",
    }:
        return has_credentials(key)
    if key in {"frankfurter", "ecb_fx", "manual_import"}:
        return False
    if item.get("category") in {"E", "F", "G", "H", "I"} and key not in COLLECTORS:
        return False
    return vstatus in {"ACTIVE", "IMPLEMENTED", "DEGRADED"}


def test_catalog_has_new_connector_keys():
    by_key = _catalog_by_connector_key()
    for key in (*_FREE_ACTIVE, *_CREDENTIALED):
        assert key in by_key, f"catalog missing connector_key={key}"
        assert by_key[key]["connector_key"] == key


def test_registry_registers_new_connectors():
    for key in (*_FREE_ACTIVE, *_CREDENTIALED):
        assert key in COLLECTORS, f"COLLECTORS missing {key}"


def test_free_connectors_seed_enabled_without_keys(monkeypatch):
    # Ensure no accidental env keys change free-path defaults.
    monkeypatch.delenv("FINDWORK_API_KEY", raising=False)
    get_settings.cache_clear()

    by_key = _catalog_by_connector_key()
    for key in _FREE_ACTIVE:
        item = by_key[key]
        assert item["verification_status"] == "ACTIVE", key
        assert key not in CREDENTIALED_SCAFFOLDS, key
        assert has_credentials(key) is True, key
        assert _seed_would_enable(key, item) is True, key
        # Catalog ACTIVE maps to enabled connector_status when runnable.
        assert _STATUS_TO_CONNECTOR["ACTIVE"] == "enabled"


def test_careerjet_stays_credentials_gated(monkeypatch):
    monkeypatch.setenv("CAREERJET_API_KEY", "")
    monkeypatch.setenv("CAREERJET_USER_IP", "")
    get_settings.cache_clear()

    by_key = _catalog_by_connector_key()
    item = by_key["careerjet"]
    assert item["verification_status"] == "NEEDS_CREDENTIALS"
    assert "careerjet" in CREDENTIALED_SCAFFOLDS
    assert has_credentials("careerjet") is False
    assert _seed_would_enable("careerjet", item) is False

    monkeypatch.setenv("CAREERJET_API_KEY", "test-key")
    monkeypatch.setenv("CAREERJET_USER_IP", "203.0.113.1")
    get_settings.cache_clear()
    assert has_credentials("careerjet") is True
    assert _seed_would_enable("careerjet", item) is True
    assert item["verification_status"] == "NEEDS_CREDENTIALS"


def test_infojobs_stays_credentials_gated(monkeypatch):
    monkeypatch.setenv("INFOJOBS_CLIENT_ID", "")
    monkeypatch.setenv("INFOJOBS_CLIENT_SECRET", "")
    get_settings.cache_clear()

    by_key = _catalog_by_connector_key()
    item = by_key["infojobs"]
    assert item["verification_status"] == "NEEDS_CREDENTIALS"
    assert "infojobs" in CREDENTIALED_SCAFFOLDS
    assert has_credentials("infojobs") is False
    assert _seed_would_enable("infojobs", item) is False

    monkeypatch.setenv("INFOJOBS_CLIENT_ID", "test-id")
    monkeypatch.setenv("INFOJOBS_CLIENT_SECRET", "test-secret")
    get_settings.cache_clear()
    assert has_credentials("infojobs") is True
    assert _seed_would_enable("infojobs", item) is True
    assert item["verification_status"] == "NEEDS_CREDENTIALS"


def test_findwork_stays_credentials_gated(monkeypatch):
    monkeypatch.setenv("FINDWORK_API_KEY", "")
    get_settings.cache_clear()

    by_key = _catalog_by_connector_key()
    item = by_key["findwork"]
    assert item["verification_status"] == "NEEDS_CREDENTIALS"
    assert "findwork" in CREDENTIALED_SCAFFOLDS
    assert has_credentials("findwork") is False
    assert _seed_would_enable("findwork", item) is False

    monkeypatch.setenv("FINDWORK_API_KEY", "test-token")
    get_settings.cache_clear()
    assert has_credentials("findwork") is True
    assert _seed_would_enable("findwork", item) is True
    # Keys alone must not imply catalog ACTIVE.
    assert item["verification_status"] == "NEEDS_CREDENTIALS"
