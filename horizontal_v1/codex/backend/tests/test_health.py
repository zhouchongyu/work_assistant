from fastapi.testclient import TestClient


def test_health_returns_envelope_and_request_id():
    from backend.main import app

    client = TestClient(app)
    res = client.get("/api/v1/health")

    assert res.status_code == 200
    body = res.json()
    assert body["code"] == 1000
    assert body["message"] == "success"
    assert body["result"] == {"status": "ok"}
    assert isinstance(body["request_id"], str)
    assert body["request_id"]
    assert res.headers["x-request-id"] == body["request_id"]


def test_health_echoes_x_request_id():
    from backend.main import app

    client = TestClient(app)
    res = client.get("/api/v1/health", headers={"x-request-id": "req-123"})

    assert res.status_code == 200
    body = res.json()
    assert body["request_id"] == "req-123"
    assert res.headers["x-request-id"] == "req-123"
