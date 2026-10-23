from fastapi import Header, HTTPException, status

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
    if authorization and authorization.lower().startswith("bearer "):
        return authorization[7:].strip() or None
    return None


async def verify_ops_token(
    x_ops_token: str | None = Header(default=None, alias="X-Ops-Token"),
    authorization: str | None = Header(default=None),
) -> None:
    """Require OPS_API_TOKEN for credential mutate / field-detail endpoints."""
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
