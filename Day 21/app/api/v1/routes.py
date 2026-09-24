"""Version 1 API routes for item processing.

Demonstrates:
- Synchronous blocking endpoint (`POST /sync`)
- Asynchronous non-blocking endpoint (`POST /async`)
- Dependency Injection with `Depends`
- BackgroundTasks scheduling
- Strict Pydantic input/output validation
"""

from fastapi import APIRouter, BackgroundTasks, Depends, status
from app.dependencies.dependencies import (
    RequestContext,
    get_item_service,
    get_request_context,
)
from app.models.schemas import ItemCreate, ItemResponse
from app.services.service import ItemService

router = APIRouter(prefix="/items", tags=["Item Processing - V1"])


@router.post(
    "/sync",
    response_model=ItemResponse,
    status_code=status.HTTP_200_OK,
    summary="Process Item Synchronously",
    description="""
Processes an incoming item request using **synchronous, blocking I/O**.

**Key Architectural Notes:**
- Defined using standard `def` (synchronous Python).
- Uses `time.sleep()` strictly to simulate a blocking database query or external I/O.
- FastAPI automatically executes standard `def` routes in an external threadpool.
- Under heavy concurrent load, threadpool contention and thread context switching limit concurrency and increase latency.
- Dispatches non-critical audit logging to a background task upon response completion.
    """,
    responses={
        200: {
            "description": "Item processed successfully via synchronous pipeline.",
            "model": ItemResponse,
        },
        422: {"description": "Validation Error (e.g. negative price or missing name)."},
    },
)
def process_item_sync(
    item: ItemCreate,
    background_tasks: BackgroundTasks,
    service: ItemService = Depends(get_item_service),
    context: RequestContext = Depends(get_request_context),
) -> ItemResponse:
    """Synchronous item processing endpoint."""
    # 1. Execute synchronous business logic (with simulated blocking I/O)
    result = service.process_item_sync(item, client_ip=context.client_host)

    # 2. Queue asynchronous background task for non-critical audit trail
    background_tasks.add_task(
        service.log_background_audit,
        item_id=result.id,
        item_name=result.name,
        processing_type="sync",
        client_ip=context.client_host,
    )

    return result


@router.post(
    "/async",
    response_model=ItemResponse,
    status_code=status.HTTP_200_OK,
    summary="Process Item Asynchronously",
    description="""
Processes an incoming item request using **asynchronous, non-blocking I/O**.

**Key Architectural Notes:**
- Defined using `async def` and non-blocking `await`.
- Uses `await asyncio.sleep()` to yield execution to the asyncio event loop while waiting for I/O.
- The single thread event loop can concurrently switch to other requests without waiting or spawning OS threads.
- Achieves higher throughput and reduced queue latency under concurrent traffic.
- Dispatches non-critical audit logging to a background task upon response completion.
    """,
    responses={
        200: {
            "description": "Item processed successfully via asynchronous pipeline.",
            "model": ItemResponse,
        },
        422: {"description": "Validation Error (e.g. negative price or missing name)."},
    },
)
async def process_item_async(
    item: ItemCreate,
    background_tasks: BackgroundTasks,
    service: ItemService = Depends(get_item_service),
    context: RequestContext = Depends(get_request_context),
) -> ItemResponse:
    """Asynchronous item processing endpoint."""
    # 1. Execute asynchronous business logic (yielding to the event loop)
    result = await service.process_item_async(item, client_ip=context.client_host)

    # 2. Queue background task for non-critical audit trail
    background_tasks.add_task(
        service.log_background_audit,
        item_id=result.id,
        item_name=result.name,
        processing_type="async",
        client_ip=context.client_host,
    )

    return result


@router.get(
    "/health",
    summary="V1 API Health Check",
    description="Returns the operational status of the V1 API router.",
    tags=["System"],
)
async def health_check():
    """Simple health check endpoint for monitoring."""
    return {"status": "ok", "version": "v1"}
