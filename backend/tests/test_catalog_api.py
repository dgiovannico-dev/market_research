import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://fmi:fmi_dev_password_change_me@localhost:5432/fmi",
)
os.environ["ENABLE_SCHEDULER"] = "false"

from app.main import app  # noqa: E402


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_catalog_summary(client):
    res = client.get("/api/v1/sources/catalog/summary")
    assert res.status_code == 200
    body = res.json()
    assert body["total"] >= 160
    assert "by_status" in body


def test_catalog_filter_active(client):
    res = client.get("/api/v1/sources/catalog", params={"status": "ACTIVE"})
    assert res.status_code == 200
    items = res.json()["items"]
    assert any(i.get("connector_key") == "remotive" for i in items)
    remotive = next(i for i in items if i.get("connector_key") == "remotive")
    assert remotive.get("is_credentialed_scaffold") is False


def test_catalog_filter_kind(client):
    free = client.get("/api/v1/sources/catalog", params={"kind": "free"})
    cred = client.get("/api/v1/sources/catalog", params={"kind": "credentialed"})
    assert free.status_code == 200 and cred.status_code == 200
    free_items = free.json()["items"]
    cred_items = cred.json()["items"]
    assert all(i.get("verification_status") != "NEEDS_CREDENTIALS" for i in free_items)
    assert all(not i.get("is_credentialed_scaffold") for i in free_items)
    assert any(i.get("connector_key") == "findwork" for i in cred_items)
    assert not any(i.get("connector_key") == "findwork" for i in free_items)
    # Partner boards (no connector_key) appear under Access=Needs credentials
    cred_names = {i.get("name") for i in cred_items}
    assert "Indeed" in cred_names
    assert "LinkedIn Jobs" in cred_names
    assert all(
        i.get("is_credentialed_scaffold") or i.get("verification_status") == "NEEDS_CREDENTIALS"
        for i in cred_items
    )


def test_sources_list_includes_insert_evidence(client):
    res = client.get("/api/v1/sources")
    assert res.status_code == 200
    items = res.json()["items"]
    assert items
    sample = items[0]
    assert "has_insert_evidence" in sample
    assert "insert_runs_count" in sample
    assert "last_insert_at" in sample
    assert isinstance(sample["has_insert_evidence"], bool)
    assert isinstance(sample["insert_runs_count"], int)


def test_fx_rates(client):
    res = client.get("/api/v1/fx/rates")
    assert res.status_code == 200
    body = res.json()
    assert "frankfurter" in body
    assert body["frankfurter"].get("rates")
