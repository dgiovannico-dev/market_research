"""Unit tests for OIDC role extraction (no live Keycloak)."""

from app.auth.oidc import AuthPrincipal, _roles_from_claims, extract_bearer


def test_extract_bearer() -> None:
    assert extract_bearer(None) is None
    assert extract_bearer("Basic x") is None
    assert extract_bearer("Bearer abc") == "abc"
    assert extract_bearer("bearer  xyz  ") == "xyz"


def test_roles_from_realm_and_client() -> None:
    claims = {
        "realm_access": {"roles": ["user", "offline_access"]},
        "resource_access": {"fmi-frontend": {"roles": ["admin"]}},
    }
    roles = _roles_from_claims(claims, "fmi-frontend")
    assert "user" in roles
    assert "admin" in roles


def test_principal_flags() -> None:
    p = AuthPrincipal(sub="1", email=None, roles=frozenset({"user"}), raw={})
    assert p.is_user and not p.is_admin
    a = AuthPrincipal(sub="2", email="a@b.c", roles=frozenset({"admin"}), raw={})
    assert a.is_admin and a.is_user
