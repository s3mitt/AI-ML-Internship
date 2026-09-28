"""Health, Liveness, and Readiness Probe Routers for Container Orchestration."""

import time
from fastapi import APIRouter, status
from ..config import get_settings
from ..models.schemas import HealthCheckResponse, LivenessResponse, ReadinessResponse
from ..monitoring import START_TIME, check_health

router = APIRouter(prefix="/health", tags=["Health & Probes"])


@router.get(
    "",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Comprehensive System Health Check",
    description="Returns detailed health status including resource threshold evaluations.",
)
async def get_health() -> HealthCheckResponse:
    """Evaluate overall system health."""
    settings = get_settings()
    health_data = check_health()
    return HealthCheckResponse(
        status=health_data["status"],
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        timestamp=health_data["timestamp"],
        checks=health_data["checks"],
    )


@router.get(
    "/live",
    response_model=LivenessResponse,
    status_code=status.HTTP_200_OK,
    summary="Container Liveness Probe",
    description="Kubernetes/Docker liveness probe to verify that the application process is running.",
)
async def get_liveness() -> LivenessResponse:
    """Verify application liveness."""
    uptime = round(time.time() - START_TIME, 2)
    return LivenessResponse(status="alive", uptime_seconds=uptime)


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    status_code=status.HTTP_200_OK,
    summary="Container Readiness Probe",
    description="Kubernetes/Docker readiness probe to confirm readiness to serve incoming traffic.",
)
async def get_readiness() -> ReadinessResponse:
    """Verify application readiness for incoming traffic."""
    # Readiness checks: configurations loaded, memory available
    health_data = check_health()
    is_ready = health_data["status"] in ("healthy", "degraded")
    return ReadinessResponse(
        status="ready" if is_ready else "not_ready",
        ready=is_ready,
        checks={
            "configuration": "loaded",
            "memory_pressure": health_data["checks"]["memory"]["status"],
            "disk_pressure": health_data["checks"]["disk"]["status"],
        },
    )
