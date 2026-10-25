"""Validate Keycloak (OIDC) access tokens via JWKS."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any

import httpx
import jwt
from jwt import PyJWKClient

from app.core.config import Settings, get_settings


@dataclass(frozen=True)
class AuthPrincipal:
    sub: str
    email: str | None
    roles: frozenset[str]
    raw: dict[str, Any]

    @property
    def is_admin(self) -> bool:
        return "admin" in self.roles

    @property
    def is_user(self) -> bool:
        return self.is_admin or "user" in self.roles


def extract_bearer(authorization: str | None) -> str | None:
    if not authorization:
        return None
    parts = authorization.split(None, 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    token = parts[1].strip()
    return token or None


def _roles_from_claims(claims: dict[str, Any], client_id: str) -> frozenset[str]:
    roles: set[str] = set()
    realm = claims.get("realm_access") or {}
    if isinstance(realm, dict):
        for r in realm.get("roles") or []:
            if isinstance(r, str):
                roles.add(r)
    resource = claims.get("resource_access") or {}
    if isinstance(resource, dict) and client_id:
        client = resource.get(client_id) or {}
        if isinstance(client, dict):
            for r in client.get("roles") or []:
                if isinstance(r, str):
                    roles.add(r)
    # Also accept a flat "roles" claim (some mappers)
    flat = claims.get("roles")
    if isinstance(flat, list):
        for r in flat:
            if isinstance(r, str):
                roles.add(r)
    return frozenset(roles)


@lru_cache(maxsize=4)
def _jwk_client(jwks_url: str) -> PyJWKClient:
    return PyJWKClient(jwks_url, cache_keys=True, lifespan=3600)


def jwks_url_for(settings: Settings) -> str:
    if settings.oidc_jwks_url.strip():
        return settings.oidc_jwks_url.strip()
    issuer = settings.oidc_issuer.rstrip("/")
    return f"{issuer}/protocol/openid-connect/certs"


def validate_access_token(token: str, settings: Settings | None = None) -> AuthPrincipal:
    settings = settings or get_settings()
    if not settings.oidc_enabled:
        raise ValueError("OIDC is disabled")
    issuer = settings.oidc_issuer.rstrip("/")
    if not issuer:
        raise ValueError("OIDC_ISSUER is not set")
    jwks_url = jwks_url_for(settings)
    client = _jwk_client(jwks_url)
    signing_key = client.get_signing_key_from_jwt(token)
    decode_kwargs: dict[str, Any] = {
        "algorithms": ["RS256"],
        "issuer": issuer,
        "options": {"verify_aud": bool(settings.oidc_audience.strip())},
    }
    if settings.oidc_audience.strip():
        decode_kwargs["audience"] = settings.oidc_audience.strip()
    claims = jwt.decode(token, signing_key.key, **decode_kwargs)
    sub = str(claims.get("sub") or "").strip()
    if not sub:
        raise ValueError("token missing sub")
    email = claims.get("email")
    email_s = str(email).strip() if email else None
    roles = _roles_from_claims(claims, settings.oidc_client_id.strip())
    return AuthPrincipal(sub=sub, email=email_s, roles=roles, raw=claims)


def probe_jwks(settings: Settings | None = None) -> bool:
    """Return True if JWKS endpoint is reachable (ops smoke)."""
    settings = settings or get_settings()
    url = jwks_url_for(settings)
    try:
        r = httpx.get(url, timeout=5.0)
        return r.status_code == 200
    except Exception:
        return False
