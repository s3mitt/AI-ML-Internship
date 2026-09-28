"""Pydantic Models and Schemas for API Requests and Responses."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class HealthCheckResponse(BaseModel):
    """Overall system health evaluation schema."""

    status: str = Field(..., description="Overall health status: healthy, degraded, or unhealthy")
    app_name: str = Field(..., description="Application name")
    version: str = Field(..., description="Application semantic version")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    checks: Optional[Dict[str, Any]] = Field(default=None, description="Detailed sub-check evaluations")


class LivenessResponse(BaseModel):
    """Kubernetes / Docker liveness probe schema."""

    status: str = Field(default="alive", description="Process liveness status")
    uptime_seconds: float = Field(..., description="Process uptime in seconds")


class ReadinessResponse(BaseModel):
    """Kubernetes / Docker readiness probe schema."""

    status: str = Field(default="ready", description="Traffic acceptance readiness")
    ready: bool = Field(default=True, description="Boolean readiness state")
    checks: Dict[str, str] = Field(default_factory=dict, description="Dependent service check results")


class SystemTelemetryResponse(BaseModel):
    """Hardware and process telemetry schema."""

    timestamp: str
    uptime_seconds: float
    cpu: Dict[str, Any]
    memory: Dict[str, Any]
    disk: Dict[str, Any]
    process: Dict[str, Any]


class TaskCreateRequest(BaseModel):
    """Task creation request payload schema."""

    title: str = Field(..., min_length=3, max_length=100, description="Descriptive task title")
    task_type: str = Field(
        ...,
        pattern="^(unit_test|data_processing|analysis|system_audit)$",
        description="Type of task: unit_test, data_processing, analysis, system_audit",
    )
    payload: Dict[str, Any] = Field(default_factory=dict, description="Task specific payload parameters")
    priority: str = Field(
        default="medium",
        pattern="^(low|medium|high|critical)$",
        description="Task scheduling priority: low, medium, high, critical",
    )


class TaskResponse(BaseModel):
    """Task detail and result representation schema."""

    task_id: str = Field(..., description="Unique UUID identifying the task")
    title: str = Field(..., description="Task title")
    task_type: str = Field(..., description="Task type classification")
    priority: str = Field(..., description="Execution priority")
    status: str = Field(..., description="Current status: pending, processing, completed, failed")
    result: Optional[Dict[str, Any]] = Field(default=None, description="Output payload upon completion")
    error: Optional[str] = Field(default=None, description="Error message if execution failed")
    created_at: str = Field(..., description="Creation timestamp")
    completed_at: Optional[str] = Field(default=None, description="Completion timestamp")
    execution_time_ms: Optional[float] = Field(default=None, description="Processing duration in milliseconds")


class TaskListResponse(BaseModel):
    """Paginated or complete list of registered tasks."""

    total: int = Field(..., description="Total count of tasks in registry")
    tasks: List[TaskResponse] = Field(..., description="List of task records")


class ErrorResponse(BaseModel):
    """Standardized error response payload schema."""

    error: str = Field(..., description="High-level error classification")
    detail: Optional[str] = Field(default=None, description="Detailed error explanation")
    request_id: Optional[str] = Field(default=None, description="Correlation identifier for tracing")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
