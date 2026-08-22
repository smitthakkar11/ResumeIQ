"""Phase 1 tests: the app boots, routes are mounted, and CORS is configured."""

from fastapi.testclient import TestClient


def test_root_returns_service_metadata(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["app"] == "ResumeIQ"


def test_health_endpoint_reports_ok(client: TestClient) -> None:
    response = client.get("/api/health")
    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "ok"
    assert body["app"] == "ResumeIQ"
    assert "environment" in body


def test_openapi_schema_is_generated(client: TestClient) -> None:
    """Proves every route's Pydantic models are valid and serialisable."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "/api/health" in response.json()["paths"]


def test_cors_preflight_allows_the_vite_dev_server(client: TestClient) -> None:
    response = client.options(
        "/api/health",
        headers={
            "Origin": "http://localhost:5174",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5174"
