import pytest
from fastapi.testclient import TestClient
from devpulse.db import Base, engine
from devpulse.main import app

@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def test_health_and_metrics():
    with TestClient(app) as client:
        assert client.get("/health").json() == {"status": "ok"}
        assert client.get("/metrics").status_code == 200

def test_create_list_and_delete_target():
    with TestClient(app) as client:
        created = client.post("/targets", json={
            "name": "Example", "url": "https://example.com/health",
            "timeout_seconds": 3, "latency_threshold_ms": 500
        })
        assert created.status_code == 201
        target_id = created.json()["id"]
        assert client.get("/targets").json()[0]["name"] == "Example"
        assert client.delete(f"/targets/{target_id}").status_code == 204
        assert client.get(f"/targets/{target_id}").status_code == 404

def test_reject_invalid_target_url():
    with TestClient(app) as client:
        response = client.post("/targets", json={"name": "Bad", "url": "not-a-url"})
        assert response.status_code == 422
