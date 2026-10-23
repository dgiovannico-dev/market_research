"""SourceCatalogPort over data/sources/catalog.json."""

from __future__ import annotations

from typing import Any

from app.sources import catalog as catalog_mod


class JsonFileSourceCatalog:
    def load(self) -> dict[str, Any]:
        return catalog_mod.load_catalog()

    def summary(self) -> dict[str, Any]:
        return catalog_mod.catalog_summary()


DEFAULT_SOURCE_CATALOG = JsonFileSourceCatalog()
