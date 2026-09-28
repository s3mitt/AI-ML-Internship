"""Task Management API Router with Validation and Structured Logging."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from ..logging_config import get_logger
from ..models.schemas import TaskCreateRequest, TaskListResponse, TaskResponse
from ..services.task_service import TaskService, get_task_service

logger = get_logger("linkific.tasks_router")
router = APIRouter(prefix="/api/v1/tasks", tags=["Tasks"])


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a New Task",
    description="Registers a new task in pending state.",
)
async def create_task(
    payload: TaskCreateRequest,
    service: TaskService = Depends(get_task_service),
) -> TaskResponse:
    """Create a new task."""
    logger.info("Received request to create task", extra={"title": payload.title, "type": payload.task_type})
    return service.create_task(payload)


@router.post(
    "/{task_id}/execute",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Execute a Task",
    description="Runs the execution pipeline for a specified task and records execution metrics.",
)
async def execute_task(
    task_id: str,
    service: TaskService = Depends(get_task_service),
) -> TaskResponse:
    """Execute task by ID."""
    logger.info("Received request to execute task", extra={"task_id": task_id})
    try:
        return service.execute_task(task_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Task by ID",
    description="Retrieves the current state and result of a specific task.",
)
async def get_task(
    task_id: str,
    service: TaskService = Depends(get_task_service),
) -> TaskResponse:
    """Get single task details."""
    task = service.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID '{task_id}' not found.",
        )
    return task


@router.get(
    "",
    response_model=TaskListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Tasks",
    description="Returns all registered tasks, with optional status filtering.",
)
async def list_tasks(
    status: Optional[str] = Query(None, description="Filter by status (pending, completed, failed)"),
    service: TaskService = Depends(get_task_service),
) -> TaskListResponse:
    """List tasks with optional status filter."""
    tasks = service.list_tasks(status=status)
    return TaskListResponse(total=len(tasks), tasks=tasks)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a Task",
    description="Deletes a task from the active registry.",
)
async def delete_task(
    task_id: str,
    service: TaskService = Depends(get_task_service),
) -> None:
    """Delete a task by ID."""
    deleted = service.delete_task(task_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID '{task_id}' not found.",
        )
    return None
