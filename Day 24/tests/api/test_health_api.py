"""API integration tests for Health, Readiness, and Liveness Probe Endpoints."""

from fastapi.testclient import TestClient
import pytest


@pytest.mark.api
class TestHealthApi:
    """Test suite verifying service health, container orchestration probes, and root discovery."""

    def test_root_discovery_endpoint(self, client: TestClient):
        """Verify root endpoint returns system discovery metadata."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "version" in data
        assert data["docs_url"] == "/docs"
        assert data["health_check"] == "/health"
        assert data["metrics"] == "/metrics"

    def test_health_check_endpoint(self, client: TestClient):
        """Verify /health returns detailed status with component checks."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ("healthy", "degraded")
        assert "checks" in data
        assert "memory" in data["checks"]
        assert "disk" in data["checks"]

    def test_liveness_probe_endpoint(self, client: TestClient):
        """Verify /health/live container liveness probe."""
        response = client.get("/health/live")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"
        assert data["uptime_seconds"] >= 0

    def test_readiness_probe_endpoint(self, client: TestClient):
        """Verify /health/ready container readiness probe."""
        response = client.get("/health/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ("ready", "not_ready")
        assert data["ready"] is True
        assert data["checks"]["configuration"] == "loaded"

    def test_request_correlation_headers(self, client: TestClient):
        """Verify X-Request-ID correlation and latency headers are injected into response."""
        custom_req_id = "custom-trace-uuid-12345"
        response = client.get("/health/live", headers={"X-Request-ID": custom_req_id})
        assert response.status_code == 200
        assert response.headers.get("X-Request-ID") == custom_req_id
        assert "X-Response-Time-Ms" in response.headers
