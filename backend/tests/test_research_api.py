"""Research Intent API (Demand Compass Task 6)."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://fmi:fmi_dev_password_change_me@localhost:5432/fmi",
)
os.environ["ENABLE_SCHEDULER"] = "false"

from app.main import app  # noqa: E402
from app.storage.db import SessionLocal  # noqa: E402
from app.storage.models import SearchQuery  # noqa: E402


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def unique_suffix():
    return f"{datetime.now(timezone.utc).timestamp():.6f}"


def test_create_list_patch_soft_delete(client, unique_suffix):
    name = f"Focus API {unique_suffix}"
    create = client.post(
        "/api/v1/research/intents",
        json={
            "name": name,
            "query_text": "python fastapi",
            "kind": "focus",
            "countries": ["DE", "NL"],
            "enabled": True,
        },
    )
    assert create.status_code == 201, create.text
    body = create.json()
    intent_id = body["id"]
    assert body["kind"] == "focus"
    assert body["origin"] == "user"
    assert body["deleted_at"] is None
    assert body["label"] == name

    listed = client.get("/api/v1/research/intents", params={"kind": "focus"})
    assert listed.status_code == 200
    ids = {item["id"] for item in listed.json()["items"]}
    assert intent_id in ids
    for item in listed.json()["items"]:
        assert item["deleted_at"] is None

    patched = client.patch(
        f"/api/v1/research/intents/{intent_id}",
        json={"enabled": False, "query_text": "python OR fastapi"},
    )
    assert patched.status_code == 200, patched.text
    assert patched.json()["enabled"] is False
    assert patched.json()["query_text"] == "python OR fastapi"
    assert patched.json()["version"] >= 2

    deleted = client.delete(f"/api/v1/research/intents/{intent_id}")
    assert deleted.status_code == 200
    assert deleted.json()["status"] == "deleted"

    after = client.get("/api/v1/research/intents", params={"kind": "focus"})
    assert intent_id not in {item["id"] for item in after.json()["items"]}

    with_deleted = client.get(
        "/api/v1/research/intents",
        params={"kind": "focus", "include_deleted": True},
    )
    assert with_deleted.status_code == 200
    soft = next((i for i in with_deleted.json()["items"] if i["id"] == intent_id), None)
    assert soft is not None
    assert soft["deleted_at"] is not None

    # Soft-deleted cannot be patched
    assert client.patch(f"/api/v1/research/intents/{intent_id}", json={"enabled": True}).status_code == 404


def test_list_discovery_kind(client):
    res = client.get("/api/v1/research/intents", params={"kind": "discovery"})
    assert res.status_code == 200
    for item in res.json()["items"]:
        assert item["kind"] == "discovery"
        assert item["deleted_at"] is None


def test_accept_watch(client, unique_suffix):
    res = client.post(
        "/api/v1/research/watches/accept",
        json={
            "name": f"LLM Watch {unique_suffix}",
            "query_text": "rust systems",
            "kind": "focus",
            "countries": ["US"],
        },
    )
    assert res.status_code == 201, res.text
    body = res.json()
    assert body["origin"] == "llm_accepted"
    assert body["enabled"] is True
    assert body["kind"] == "focus"

    # cleanup soft-delete
    client.delete(f"/api/v1/research/intents/{body['id']}")


def test_create_accepts_label_alias(client, unique_suffix):
    label = f"Label Alias {unique_suffix}"
    res = client.post(
        "/api/v1/research/intents",
        json={
            "label": label,
            "query_text": "typescript react",
            "kind": "focus",
        },
    )
    assert res.status_code == 201, res.text
    body = res.json()
    assert body["name"] == label
    assert body["label"] == label
    client.delete(f"/api/v1/research/intents/{body['id']}")


def test_research_jobs_db_only(client):
    res = client.get("/api/v1/research/jobs", params={"q": "engineer", "limit": 5})
    assert res.status_code == 200, res.text
    body = res.json()
    assert "items" in body
    assert "total" in body
    assert body["limit"] == 5
    assert body["skip"] == 0


def _assert_research_jobs_shape(body: dict, *, lens, limit: int) -> None:
    required = {"total", "skip", "limit", "lens", "query_id", "q", "country_code", "items"}
    assert required <= set(body)
    assert body["lens"] == lens
    assert body["limit"] == limit
    assert body["skip"] == 0
    assert isinstance(body["total"], int)
    assert isinstance(body["items"], list)
    assert len(body["items"]) <= limit
    for item in body["items"]:
        assert {"id", "title", "company", "country_code", "canonical_url", "evidence_tier"} <= set(
            item
        )
        assert item["evidence_tier"] in ("standard", "thin")


def test_research_jobs_lens_and_query_id(client, unique_suffix):
    # Create a disposable intent so query_id filter is valid even if no matches
    create = client.post(
        "/api/v1/research/intents",
        json={
            "name": f"Jobs Filter {unique_suffix}",
            "query_text": "unlikely-token-xyz",
            "kind": "focus",
        },
    )
    assert create.status_code == 201
    intent_id = create.json()["id"]

    by_id = client.get("/api/v1/research/jobs", params={"query_id": intent_id})
    assert by_id.status_code == 200
    assert by_id.json()["query_id"] == intent_id
    assert by_id.json()["total"] == 0

    market = client.get("/api/v1/research/jobs", params={"lens": "market", "limit": 10})
    assert market.status_code == 200
    _assert_research_jobs_shape(market.json(), lens="market", limit=10)

    focus = client.get("/api/v1/research/jobs", params={"lens": "focus", "limit": 10})
    assert focus.status_code == 200
    _assert_research_jobs_shape(focus.json(), lens="focus", limit=10)

    compare = client.get("/api/v1/research/jobs", params={"lens": "compare", "limit": 10})
    assert compare.status_code == 200
    _assert_research_jobs_shape(compare.json(), lens="compare", limit=10)

    client.delete(f"/api/v1/research/intents/{intent_id}")


def test_research_jobs_facets_shape(client):
    res = client.get("/api/v1/research/jobs/facets")
    assert res.status_code == 200, res.text
    body = res.json()
    assert {"countries", "sources", "contracts", "remotes"} <= set(body)
    assert isinstance(body["countries"], list)
    assert isinstance(body["sources"], list)
    assert isinstance(body["contracts"], list)
    assert isinstance(body["remotes"], list)
    for src in body["sources"]:
        assert {"id", "name"} <= set(src)


def test_research_jobs_multi_country_and_sort(client):
    facets = client.get("/api/v1/research/jobs/facets")
    assert facets.status_code == 200
    countries = facets.json()["countries"]
    if len(countries) >= 2:
        csv = f"{countries[0]},{countries[1]}"
        multi = client.get(
            "/api/v1/research/jobs",
            params={"country_code": csv, "limit": 20},
        )
        assert multi.status_code == 200, multi.text
        body = multi.json()
        assert set(body["countries"]) == {countries[0], countries[1]}
        for item in body["items"]:
            assert item["country_code"] in {countries[0], countries[1]}

    bad_sort = client.get(
        "/api/v1/research/jobs",
        params={"sort": "drop_table;--", "order": "asc", "limit": 5},
    )
    assert bad_sort.status_code == 200
    assert bad_sort.json()["sort"] == "published_at"
    assert bad_sort.json()["order"] == "asc"

    by_title = client.get(
        "/api/v1/research/jobs",
        params={"sort": "title", "order": "asc", "limit": 5},
    )
    assert by_title.status_code == 200
    assert by_title.json()["sort"] == "title"
    assert by_title.json()["order"] == "asc"


def test_list_intents_shape(client, unique_suffix):
    """Unfiltered intents list returns stable Explore payload keys."""
    name = f"List Shape {unique_suffix}"
    create = client.post(
        "/api/v1/research/intents",
        json={"name": name, "query_text": "shape probe", "kind": "focus"},
    )
    assert create.status_code == 201
    intent_id = create.json()["id"]

    res = client.get("/api/v1/research/intents")
    assert res.status_code == 200
    body = res.json()
    assert set(body) >= {"items", "total", "suggested_countries"}
    assert isinstance(body["items"], list)
    assert isinstance(body["suggested_countries"], list)
    assert body["total"] == len(body["items"])
    row = next(i for i in body["items"] if i["id"] == intent_id)
    assert set(row) >= {
        "id",
        "name",
        "label",
        "query_text",
        "kind",
        "enabled",
        "origin",
        "deleted_at",
        "countries",
        "role_families",
        "contract_types",
        "schedule_hint",
        "version",
    }
    assert row["kind"] == "focus"
    assert row["deleted_at"] is None
    assert row["label"] == name

    client.delete(f"/api/v1/research/intents/{intent_id}")


def test_sync_intent_mocked(client, unique_suffix):
    create = client.post(
        "/api/v1/research/intents",
        json={
            "name": f"Sync Me {unique_suffix}",
            "query_text": "kubernetes",
            "kind": "discovery",
            "origin": "user",
        },
    )
    assert create.status_code == 201
    intent_id = create.json()["id"]

    fake = {
        "query_id": intent_id,
        "status": "ok",
        "query_text": "kubernetes",
        "collections": [{"source": "mock", "status": "succeeded", "inserted": 0}],
    }
    with patch(
        "app.api.v1.research.sync_research_intent",
        new=AsyncMock(return_value=fake),
    ) as mocked:
        res = client.post(f"/api/v1/research/intents/{intent_id}/sync")
        assert res.status_code == 200, res.text
        assert res.json()["status"] == "ok"
        assert res.json()["query_id"] == intent_id
        mocked.assert_awaited_once()

    client.delete(f"/api/v1/research/intents/{intent_id}")


def test_create_rejects_blank_query(client, unique_suffix):
    res = client.post(
        "/api/v1/research/intents",
        json={
            "name": f"Blank {unique_suffix}",
            "query_text": "   ",
            "kind": "focus",
        },
    )
    # Pydantic min_length=1 may pass whitespace; endpoint strips and rejects
    assert res.status_code in {400, 422}


def test_soft_delete_sets_deleted_at_column(client, unique_suffix):
    create = client.post(
        "/api/v1/research/intents",
        json={
            "name": f"SoftCol {unique_suffix}",
            "query_text": "golang",
            "kind": "focus",
        },
    )
    intent_id = create.json()["id"]
    client.delete(f"/api/v1/research/intents/{intent_id}")

    db = SessionLocal()
    try:
        row = db.get(SearchQuery, intent_id)
        assert row is not None
        assert row.deleted_at is not None
        assert row.enabled is False
    finally:
        db.close()
