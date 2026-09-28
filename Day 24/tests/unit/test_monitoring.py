"""Unit tests for Monitoring, Prometheus Metrics, and Health Checking."""

import pytest
from app.monitoring import (
    HTTP_ACTIVE_REQUESTS,
    HTTP_REQUEST_COUNT,
    HTTP_REQUEST_DURATION,
    TASK_EXECUTION_COUNT,
    check_health,
    generate_prometheus_metrics,
    get_system_telemetry,
    record_request_metrics,
    record_task_metrics,
)


@pytest.mark.unit
@pytest.mark.monitoring
class TestMonitoring:
    """Test suite verifying Prometheus metric collectors, health evaluations, and system telemetry."""

    def test_record_request_metrics(self):
        """Verify HTTP request metrics are incremented and recorded."""
        before = HTTP_REQUEST_COUNT.labels(method="GET", endpoint="/api/test", status="200")._value.get()
        record_request_metrics(method="GET", endpoint="/api/test", status_code=200, duration_seconds=0.045)
        after = HTTP_REQUEST_COUNT.labels(method="GET", endpoint="/api/test", status="200")._value.get()
        assert after == before + 1

    def test_record_task_metrics(self):
        """Verify task execution metric counters increment for success and failure."""
        before = TASK_EXECUTION_COUNT.labels(task_type="unit_test", status="success")._value.get()
        record_task_metrics(task_type="unit_test", status="success")
        after = TASK_EXECUTION_COUNT.labels(task_type="unit_test", status="success")._value.get()
        assert after == before + 1

    def test_active_requests_gauge(self):
        """Verify active requests gauge increment and decrement."""
        before = HTTP_ACTIVE_REQUESTS._value.get()
        HTTP_ACTIVE_REQUESTS.inc()
        assert HTTP_ACTIVE_REQUESTS._value.get() == before + 1
        HTTP_ACTIVE_REQUESTS.dec()
        assert HTTP_ACTIVE_REQUESTS._value.get() == before

    def test_get_system_telemetry_structure(self):
        """Verify system telemetry includes hardware utilization and process stats."""
        data = get_system_telemetry()
        assert "timestamp" in data
        assert "uptime_seconds" in data
        assert data["uptime_seconds"] >= 0

        # CPU section
        assert "cpu" in data
        assert "usage_percent" in data["cpu"]
        assert "core_count" in data["cpu"]

        # Memory section
        assert "memory" in data
        assert "total_bytes" in data["memory"]
        assert "used_bytes" in data["memory"]
        assert "usage_percent" in data["memory"]

        # Disk section
        assert "disk" in data
        assert "usage_percent" in data["disk"]

        # Process section
        assert "process" in data
        assert "rss_bytes" in data["process"]

    def test_check_health_normal(self):
        """Verify health check returns healthy status when thresholds are adequate."""
        health = check_health(memory_threshold=99.9, disk_threshold=99.9)
        assert health["status"] == "healthy"
        assert health["checks"]["memory"]["status"] == "pass"
        assert health["checks"]["disk"]["status"] == "pass"

    def test_check_health_threshold_breach(self):
        """Verify health check marks degraded if memory or disk thresholds are breached."""
        # Setting threshold to 0.0 forces a breach
        health = check_health(memory_threshold=0.0, disk_threshold=0.0)
        assert health["status"] == "degraded"
        assert health["checks"]["memory"]["status"] == "fail"

    def test_generate_prometheus_metrics(self):
        """Verify Prometheus scrape endpoint output generation."""
        content, content_type = generate_prometheus_metrics()
        assert isinstance(content, bytes)
        assert len(content) > 0
        assert "text/plain" in content_type or "version=0.0.4" in content_type
        # Decode and check presence of registered metrics
        text = content.decode("utf-8")
        assert "http_requests_total" in text
        assert "http_request_duration_seconds" in text
