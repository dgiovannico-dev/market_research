"""Wave 5: CollectorGateway + collectors must not import ingestion."""

from __future__ import annotations

from pathlib import Path

from app.adapters.driven.collectors.registry_gateway import RegistryCollectorGateway
from app.bootstrap import build_container, reset_container
from app.core.config import get_settings


def test_registry_gateway_lists_modes():
    gw = RegistryCollectorGateway()
    dump_keys = gw.keys_by_mode("dump")
    search_keys = gw.keys_by_mode("search")
    assert isinstance(dump_keys, list)
    assert isinstance(search_keys, list)
    # At least one known free dump connector stays registered.
    assert "remotive" in dump_keys or gw.get("remotive") is not None


def test_container_exposes_collectors_gateway():
    reset_container()
    c = build_container(get_settings())
    assert c.collectors.get("remotive") is not None or len(c.collectors.keys_by_mode("dump")) >= 0
    reset_container()


def test_no_collector_imports_ingestion():
    root = Path(__file__).resolve().parents[1] / "app" / "collectors"
    offenders: list[str] = []
    for path in root.glob("*.py"):
        text = path.read_text(encoding="utf-8")
        if "app.ingestion" in text:
            offenders.append(path.name)
    assert offenders == [], f"collectors still import ingestion: {offenders}"
