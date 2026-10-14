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

def test_tauri_desktop_origin_is_allowed() -> None:
    response = client.options(
        "/api/health",
        headers={
            "Origin": "http://tauri.localhost",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://tauri.localhost"


def test_untrusted_origin_is_not_allowed() -> None:
    response = client.options(
        "/api/health",
        headers={
            "Origin": "https://example.invalid",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert "access-control-allow-origin" not in response.headers
