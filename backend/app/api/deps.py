from fastapi import Header, HTTPException, status

from app.auth.oidc import AuthPrincipal, extract_bearer, validate_access_token
from app.bootstrap import AppContainer, get_container
from app.core.config import get_settings


def get_app_container() -> AppContainer:
    """FastAPI Depends: shared composition root (ADR-008)."""
    return get_container()


async def verify_api_key(x_api_key: str | None = Header(default=None)) -> None:
    settings = get_settings()
    if not settings.api_key:
        return
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")


def _extract_ops_token(
    x_ops_token: str | None,
    authorization: str | None,
) -> str | None:
    if x_ops_token and x_ops_token.strip():
        return x_ops_token.strip()
    # Only treat Bearer as ops token when OIDC is disabled (break-glass / legacy).
    settings = get_settings()
    if settings.oidc_enabled:
        return None
    if authorization and authorization.lower().startswith("bearer "):
        return authorization[7:].strip() or None
    return None


async def verify_ops_token(
    x_ops_token: str | None = Header(default=None, alias="X-Ops-Token"),
    authorization: str | None = Header(default=None),
) -> None:
    """Legacy: require OPS_API_TOKEN. Prefer require_admin when OIDC is enabled."""
    settings = get_settings()
    expected = (settings.ops_api_token or "").strip()
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="OPS_API_TOKEN is not configured",
        )
    provided = _extract_ops_token(x_ops_token, authorization)
    if not provided or provided != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid ops token")


async def get_optional_principal(
    authorization: str | None = Header(default=None),
    x_api_key: str | None = Header(default=None),
) -> AuthPrincipal | None:
    """Return JWT principal when OIDC is on and Bearer is valid; None otherwise.

    Valid ``X-Api-Key`` (machine) yields None principal but is accepted by
    ``require_user`` / route-level ``verify_api_key`` separately.
    """
    settings = get_settings()
    if not settings.oidc_enabled:
        return None
    token = extract_bearer(authorization)
    if not token:
        return None
    # If the bearer matches ops break-glass token, do not treat as user JWT
    ops = (settings.ops_api_token or "").strip()
    if ops and token == ops:
        return None
    try:
        return validate_access_token(token, settings)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid access token: {exc}",
        ) from exc


async def require_user(
    authorization: str | None = Header(default=None),
    x_api_key: str | None = Header(default=None),
) -> AuthPrincipal | None:
    """When OIDC require_user is on, demand a JWT with role user|admin (unless API key)."""
    settings = get_settings()
    if settings.api_key and x_api_key == settings.api_key:
        return None
    if not settings.oidc_enabled or not settings.oidc_require_user:
        return await get_optional_principal(authorization=authorization, x_api_key=x_api_key)
    principal = await get_optional_principal(authorization=authorization, x_api_key=x_api_key)
    if principal is None or not principal.is_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    return principal


async def require_admin(
    authorization: str | None = Header(default=None),
    x_api_key: str | None = Header(default=None),
    x_ops_token: str | None = Header(default=None, alias="X-Ops-Token"),
) -> AuthPrincipal | None:
    """Admin JWT role, or break-glass OPS_API_TOKEN / matching API_KEY for machines.

    When OIDC is disabled, falls back to ``verify_ops_token`` semantics.
    """
    settings = get_settings()

    # Machine API key: allow admin ops for cron tooling if configured
    if settings.api_key and x_api_key == settings.api_key:
        return None

    if settings.oidc_enabled:
        principal = await get_optional_principal(authorization=authorization, x_api_key=x_api_key)
        if principal is not None and principal.is_admin:
            return principal
        # Break-glass ops token via header only (not Bearer when OIDC on)
        expected = (settings.ops_api_token or "").strip()
        if expected and x_ops_token and x_ops_token.strip() == expected:
            return None
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )

    await verify_ops_token(x_ops_token=x_ops_token, authorization=authorization)
    return None
