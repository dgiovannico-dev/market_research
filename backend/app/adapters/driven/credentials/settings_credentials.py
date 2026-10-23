"""ConnectorCredentialsPort — secrets + ATS CSV allowlists (see port docstring)."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.collectors.credentials import has_credentials as _has_credentials


class SettingsConnectorCredentials:
    def has_credentials(self, connector_key: str, db: Session | None = None) -> bool:
        return _has_credentials(connector_key, db=db)


DEFAULT_CONNECTOR_CREDENTIALS = SettingsConnectorCredentials()
