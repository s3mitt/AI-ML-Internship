"""Task Business Logic Service.

Implements core domain operations, error boundaries, audit logging,
and execution metric tracking.
"""

from datetime import datetime, timezone
import time
from typing import Dict, List, Optional
import uuid
from ..logging_config import get_logger
from ..models.schemas import TaskCreateRequest, TaskResponse
from ..monitoring import record_task_metrics

logger = get_logger("linkific.task_service")


class TaskService:
    """Service managing business task lifecycle, processing, and persistence."""

    def __init__(self) -> None:
        self._tasks: Dict[str, TaskResponse] = {}

    def create_task(self, req: TaskCreateRequest) -> TaskResponse:
        """Create and register a new task in pending state."""
        task_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        task = TaskResponse(
            task_id=task_id,
            title=req.title,
            task_type=req.task_type,
            priority=req.priority,
            status="pending",
            result=None,
            error=None,
            created_at=now,
            completed_at=None,
            execution_time_ms=None,
        )

        self._tasks[task_id] = task
        logger.info(
            "Task created successfully",
            extra={
                "task_id": task_id,
                "task_type": req.task_type,
                "priority": req.priority,
            },
        )
        return task

    def execute_task(self, task_id: str) -> TaskResponse:
        """Execute a registered task, update status, record telemetry, and log results."""
        task = self._tasks.get(task_id)
        if not task:
            logger.warning("Task execution requested for non-existent ID", extra={"task_id": task_id})
            raise ValueError(f"Task with ID '{task_id}' not found.")

        logger.info("Starting execution of task", extra={"task_id": task_id, "task_type": task.task_type})
        start_time = time.perf_counter()

        try:
            # Simulate real domain execution based on task_type
            result_data = self._process_task_logic(task.task_type, task.title)
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            now = datetime.now(timezone.utc).isoformat()

            updated_task = TaskResponse(
                task_id=task.task_id,
                title=task.title,
                task_type=task.task_type,
                priority=task.priority,
                status="completed",
                result=result_data,
                error=None,
                created_at=task.created_at,
                completed_at=now,
                execution_time_ms=duration_ms,
            )
            self._tasks[task_id] = updated_task
            record_task_metrics(task_type=task.task_type, status="success")

            logger.info(
                "Task completed successfully",
                extra={
                    "task_id": task_id,
                    "task_type": task.task_type,
                    "duration_ms": duration_ms,
                    "status": "completed",
                },
            )
            return updated_task

        except Exception as exc:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            now = datetime.now(timezone.utc).isoformat()

            failed_task = TaskResponse(
                task_id=task.task_id,
                title=task.title,
                task_type=task.task_type,
                priority=task.priority,
                status="failed",
                result=None,
                error=str(exc),
                created_at=task.created_at,
                completed_at=now,
                execution_time_ms=duration_ms,
            )
            self._tasks[task_id] = failed_task
            record_task_metrics(task_type=task.task_type, status="failure")

            logger.error(
                "Task execution failed",
                extra={
                    "task_id": task_id,
                    "task_type": task.task_type,
                    "error": str(exc),
                    "duration_ms": duration_ms,
                },
                exc_info=True,
            )
            return failed_task

    def _process_task_logic(self, task_type: str, title: str) -> Dict[str, str]:
        """Internal processor executing business task logic."""
        if task_type == "unit_test":
            return {
                "test_suite": title,
                "assertions_passed": "24",
                "coverage_pct": "98.5%",
                "status": "PASSED",
            }
        elif task_type == "data_processing":
            return {
                "processed_items": "1500",
                "validation_errors": "0",
                "transformation_status": "COMPLETED",
            }
        elif task_type == "analysis":
            return {
                "insights_generated": "5",
                "confidence_score": "0.96",
                "recommendation": "Deploy to production with current metrics",
            }
        elif task_type == "system_audit":
            return {
                "audit_checks": "12",
                "vulnerabilities_found": "0",
                "compliance_score": "100%",
            }
        else:
            raise ValueError(f"Unsupported task_type '{task_type}'")

    def get_task(self, task_id: str) -> Optional[TaskResponse]:
        """Retrieve task by identifier."""
        return self._tasks.get(task_id)

    def list_tasks(self, status: Optional[str] = None) -> List[TaskResponse]:
        """Retrieve all tasks, optionally filtered by status."""
        tasks = list(self._tasks.values())
        if status:
            tasks = [t for t in tasks if t.status.lower() == status.lower()]
        return tasks

    def delete_task(self, task_id: str) -> bool:
        """Delete task from store."""
        if task_id in self._tasks:
            del self._tasks[task_id]
            logger.info("Task deleted", extra={"task_id": task_id})
            return True
        return False

    def clear(self) -> None:
        """Reset task repository (useful for isolated testing)."""
        self._tasks.clear()


# Global service singleton instance
_task_service_instance: Optional[TaskService] = None


def get_task_service() -> TaskService:
    """Dependency provider for TaskService singleton."""
    global _task_service_instance
    if _task_service_instance is None:
        _task_service_instance = TaskService()
    return _task_service_instance
