"""Allowlisted secret fields per credentialed connector (not ATS board lists)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ConnectorSecretSchema:
    """Secret field names stored in DB ciphertext; required for has_credentials."""

    fields: tuple[str, ...]
    required: tuple[str, ...]


# Field names are API/store keys (not env var names). Env mapping lives in resolve.
CONNECTOR_SECRET_FIELDS: dict[str, ConnectorSecretSchema] = {
    "adzuna": ConnectorSecretSchema(
        fields=("app_id", "app_key"),
        required=("app_id", "app_key"),
    ),
    "usajobs": ConnectorSecretSchema(
        fields=("api_key", "user_agent"),
        required=("api_key", "user_agent"),
    ),
    "france_travail": ConnectorSecretSchema(
        fields=("client_id", "client_secret"),
        required=("client_id", "client_secret"),
    ),
    "bundesagentur": ConnectorSecretSchema(
        fields=("api_key",),
        required=("api_key",),
    ),
    "jooble": ConnectorSecretSchema(
        fields=("api_key",),
        required=("api_key",),
    ),
    "findwork": ConnectorSecretSchema(
        fields=("api_key",),
        required=("api_key",),
    ),
    "findajob_dwp": ConnectorSecretSchema(
        fields=("api_id", "api_key"),
        required=("api_id", "api_key"),
    ),
    "freelancer": ConnectorSecretSchema(
        fields=("oauth_token",),
        required=("oauth_token",),
    ),
    "upwork": ConnectorSecretSchema(
        fields=("oauth_token", "tenant_id"),
        required=("oauth_token",),
    ),
    "careerjet": ConnectorSecretSchema(
        fields=("api_key", "user_ip"),
        required=("api_key", "user_ip"),
    ),
    "infojobs": ConnectorSecretSchema(
        fields=("client_id", "client_secret"),
        required=("client_id", "client_secret"),
    ),
}


def required_fields(connector_key: str) -> tuple[str, ...]:
    schema = CONNECTOR_SECRET_FIELDS.get(connector_key)
    return schema.required if schema else ()


def all_fields(connector_key: str) -> tuple[str, ...]:
    schema = CONNECTOR_SECRET_FIELDS.get(connector_key)
    return schema.fields if schema else ()
