"""API integration tests for Prometheus Metrics and System Telemetry."""

from fastapi.testclient import TestClient
import pytest
from app.config import Settings, get_settings


@pytest.mark.api
@pytest.mark.monitoring
class TestMetricsApi:
    """Test suite verifying metrics scraping and system telemetry endpoints."""

    def test_prometheus_metrics_scrape_endpoint(self, client: TestClient):
        """Verify /metrics returns Prometheus formatted exposition."""
        # Trigger an endpoint first so there are request metrics to report
        client.get("/health/live")

        response = client.get("/metrics")
        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]
        text = response.text
        assert "http_requests_total" in text
        assert "http_request_duration_seconds" in text
        assert "system_cpu_usage_percent" in text

    def test_system_telemetry_endpoint(self, client: TestClient):
        """Verify /api/v1/telemetry returns hardware and process metrics JSON."""
        response = client.get("/api/v1/telemetry")
        assert response.status_code == 200
        data = response.json()
        assert "cpu" in data
        assert "memory" in data
        assert "disk" in data
        assert "process" in data
        assert "uptime_seconds" in data
        assert data["cpu"]["core_count"] > 0

    def test_disabled_metrics_endpoint(self, monkeypatch: pytest.MonkeyPatch, client: TestClient):
        """Verify disabled metrics configuration yields 404."""
        disabled_settings = Settings(METRICS_ENABLED=False)
        monkeypatch.setattr("app.routers.metrics.get_settings", lambda: disabled_settings)

        response = client.get("/metrics")
        assert response.status_code == 404
        assert "disabled" in response.json()["detail"]

    def test_disabled_telemetry_endpoint(self, monkeypatch: pytest.MonkeyPatch, client: TestClient):
        """Verify disabled telemetry configuration yields 404."""
        disabled_settings = Settings(ENABLE_SYSTEM_TELEMETRY=False)
        monkeypatch.setattr("app.routers.metrics.get_settings", lambda: disabled_settings)

        response = client.get("/api/v1/telemetry")
        assert response.status_code == 404
        assert "disabled" in response.json()["detail"]
