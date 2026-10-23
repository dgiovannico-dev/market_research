"""Driven port: credential readiness for connectors (not catalog ACTIVE).

Semantics (do not collapse):
- **Secret scaffolds** (Adzuna, USAJobs, …): encrypted DB bundle or env keys.
- **ATS allowlists** (Greenhouse, Lever, Ashby, …): Settings CSV tenant lists —
  presence of tenants counts as “credentials”, not a secret store entry.
"""

from __future__ import annotations

from typing import Protocol

from sqlalchemy.orm import Session


class ConnectorCredentialsPort(Protocol):
    def has_credentials(self, connector_key: str, db: Session | None = None) -> bool:
        """True when a collect attempt is allowed. Does **not** mean ACTIVE."""
        ...
