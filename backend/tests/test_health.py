from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_api_health() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "backend"}


def test_database_health_requires_configuration(monkeypatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    response = client.get("/api/health/db")
    assert response.status_code == 503
    assert response.json() == {"detail": "Database is not configured"}
