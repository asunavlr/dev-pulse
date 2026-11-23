import pytest
from fastapi.testclient import TestClient

from devpulse.db import Base, engine
from devpulse.main import app


HEADERS = {"X-API-Key": "dev-only-change-me"}


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_health_and_readiness():
    with TestClient(app) as client:
        assert client.get("/health").json() == {"status": "ok"}
        assert client.get("/ready").json() == {"status": "ready"}


def test_protected_routes_require_api_key():
    with TestClient(app) as client:
        assert client.get("/targets").status_code == 401
        assert client.get("/targets", headers=HEADERS).status_code == 200
        assert client.get("/metrics", headers=HEADERS).status_code == 200


def test_create_list_and_delete_target():
    with TestClient(app) as client:
        created = client.post(
            "/targets",
            headers=HEADERS,
            json={
                "name": "Example",
                "url": "https://1.1.1.1/health",
                "timeout_seconds": 3,
                "latency_threshold_ms": 500,
            },
        )
        assert created.status_code == 201
        target_id = created.json()["id"]
        assert client.get("/targets", headers=HEADERS).json()[0]["name"] == "Example"
        assert client.delete(f"/targets/{target_id}", headers=HEADERS).status_code == 204


def test_rejects_private_target():
    with TestClient(app) as client:
        response = client.post(
            "/targets",
            headers=HEADERS,
            json={
                "name": "Metadata",
                "url": "http://169.254.169.254/latest/meta-data/",
            },
        )
        assert response.status_code == 422
