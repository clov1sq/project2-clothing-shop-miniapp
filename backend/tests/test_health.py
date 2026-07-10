from fastapi.testclient import TestClient

from app.main import app


def test_live_health() -> None:
    client = TestClient(app)
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json()["ok"] is True


def test_meta_contains_feature_flags() -> None:
    client = TestClient(app)
    response = client.get("/api/meta")
    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["data"]["features"]["catalog"] is False
