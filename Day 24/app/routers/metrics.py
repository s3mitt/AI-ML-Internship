"""Prometheus Scrape Endpoint and Telemetry API Router."""

from fastapi import APIRouter, HTTPException, Response, status
from ..config import get_settings
from ..models.schemas import SystemTelemetryResponse
from ..monitoring import generate_prometheus_metrics, get_system_telemetry

router = APIRouter(tags=["Monitoring & Telemetry"])


@router.get(
    "/metrics",
    summary="Prometheus Metrics Scrape Endpoint",
    description="Exposes application and runtime metrics in Prometheus text exposition format.",
)
async def get_prometheus_metrics() -> Response:
    """Return standard Prometheus metrics text."""
    settings = get_settings()
    if not settings.METRICS_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prometheus metrics collection is disabled in configuration.",
        )

    output, content_type = generate_prometheus_metrics()
    return Response(content=output, media_type=content_type)


@router.get(
    "/api/v1/telemetry",
    response_model=SystemTelemetryResponse,
    status_code=status.HTTP_200_OK,
    summary="Host & Process Telemetry",
    description="Returns real-time telemetry metrics including CPU, memory, and disk statistics.",
)
async def get_telemetry() -> SystemTelemetryResponse:
    """Return JSON hardware and process utilization statistics."""
    settings = get_settings()
    if not settings.ENABLE_SYSTEM_TELEMETRY:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="System telemetry is disabled in configuration.",
        )
    data = get_system_telemetry()
    return SystemTelemetryResponse(**data)
