"""Production Monitoring and Observability Module.

Provides Prometheus metrics instrumentation, latency measurement, system health checks,
and hardware telemetry (CPU, Memory, Disk) tracking.
"""

from datetime import datetime, timezone
import os
import time
from typing import Any, Dict, Tuple
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    REGISTRY,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)
import psutil

# Track process startup time for uptime calculation
START_TIME = time.time()


def _get_or_create_counter(name: str, documentation: str, labelnames: Tuple[str, ...] = ()) -> Counter:
    collector = REGISTRY._names_to_collectors.get(name)
    if collector is not None:
        return collector
    return Counter(name, documentation, labelnames=labelnames)


def _get_or_create_histogram(
    name: str, documentation: str, labelnames: Tuple[str, ...] = (), buckets: Tuple[float, ...] = Histogram.DEFAULT_BUCKETS
) -> Histogram:
    collector = REGISTRY._names_to_collectors.get(name)
    if collector is not None:
        return collector
    return Histogram(name, documentation, labelnames=labelnames, buckets=buckets)


def _get_or_create_gauge(name: str, documentation: str, labelnames: Tuple[str, ...] = ()) -> Gauge:
    collector = REGISTRY._names_to_collectors.get(name)
    if collector is not None:
        return collector
    return Gauge(name, documentation, labelnames=labelnames)


# Prometheus Metric Definitions
HTTP_REQUEST_COUNT = _get_or_create_counter(
    "http_requests_total",
    "Total count of HTTP requests processed by endpoint and status code",
    labelnames=("method", "endpoint", "status"),
)

HTTP_REQUEST_DURATION = _get_or_create_histogram(
    "http_request_duration_seconds",
    "Distribution of HTTP request durations in seconds",
    labelnames=("method", "endpoint"),
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)

HTTP_ACTIVE_REQUESTS = _get_or_create_gauge(
    "http_active_requests",
    "Number of HTTP requests currently being processed",
)

TASK_EXECUTION_COUNT = _get_or_create_counter(
    "task_executions_total",
    "Total count of task executions categorized by task type and status",
    labelnames=("task_type", "status"),
)

SYSTEM_CPU_GAUGE = _get_or_create_gauge(
    "system_cpu_usage_percent",
    "Current host/container CPU utilization percentage",
)

SYSTEM_MEMORY_GAUGE = _get_or_create_gauge(
    "system_memory_usage_percent",
    "Current host/container memory utilization percentage",
)


def record_request_metrics(method: str, endpoint: str, status_code: int, duration_seconds: float) -> None:
    """Record completed HTTP request metrics."""
    HTTP_REQUEST_COUNT.labels(
        method=method.upper(),
        endpoint=endpoint,
        status=str(status_code),
    ).inc()
    HTTP_REQUEST_DURATION.labels(
        method=method.upper(),
        endpoint=endpoint,
    ).observe(duration_seconds)


def record_task_metrics(task_type: str, status: str) -> None:
    """Record business logic task execution metrics."""
    TASK_EXECUTION_COUNT.labels(
        task_type=task_type,
        status=status,
    ).inc()


def get_system_telemetry() -> Dict[str, Any]:
    """Collect hardware utilization telemetry and process metrics."""
    cpu_percent = psutil.cpu_percent(interval=None)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage(os.path.abspath(os.sep))
    current_time = time.time()
    uptime_seconds = round(current_time - START_TIME, 2)

    # Update gauge values
    SYSTEM_CPU_GAUGE.set(cpu_percent)
    SYSTEM_MEMORY_GAUGE.set(mem.percent)

    process = psutil.Process()
    process_mem = process.memory_info()

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime_seconds": uptime_seconds,
        "cpu": {
            "usage_percent": cpu_percent,
            "core_count": psutil.cpu_count(logical=True),
        },
        "memory": {
            "total_bytes": mem.total,
            "used_bytes": mem.used,
            "free_bytes": mem.available,
            "usage_percent": mem.percent,
        },
        "disk": {
            "total_bytes": disk.total,
            "used_bytes": disk.used,
            "free_bytes": disk.free,
            "usage_percent": disk.percent,
        },
        "process": {
            "rss_bytes": process_mem.rss,
            "vms_bytes": process_mem.vms,
            "threads_count": process.num_threads(),
        },
    }


def check_health(memory_threshold: float = 95.0, disk_threshold: float = 95.0) -> Dict[str, Any]:
    """Evaluate application health against threshold constraints."""
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage(os.path.abspath(os.sep))

    checks = {
        "memory": {
            "status": "pass" if mem.percent < memory_threshold else "fail",
            "usage_percent": mem.percent,
            "threshold_percent": memory_threshold,
        },
        "disk": {
            "status": "pass" if disk.percent < disk_threshold else "fail",
            "usage_percent": disk.percent,
            "threshold_percent": disk_threshold,
        },
    }

    is_healthy = all(c["status"] == "pass" for c in checks.values())
    status_str = "healthy" if is_healthy else "degraded"

    return {
        "status": status_str,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
    }


def generate_prometheus_metrics() -> Tuple[bytes, str]:
    """Generate Prometheus formatted scrape text."""
    # Update system gauges before generating scrape
    mem = psutil.virtual_memory()
    cpu = psutil.cpu_percent(interval=None)
    SYSTEM_MEMORY_GAUGE.set(mem.percent)
    SYSTEM_CPU_GAUGE.set(cpu)

    output = generate_latest(REGISTRY)
    return output, CONTENT_TYPE_LATEST
