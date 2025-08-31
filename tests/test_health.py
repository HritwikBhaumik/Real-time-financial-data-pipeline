from fastapi.testclient import TestClient
from src.app.api import app

def test_health():
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    assert "status" in r.json()
