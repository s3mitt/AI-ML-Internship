"""Main FastAPI application entry point.

Initializes the FastAPI application, mounts custom timing middleware,
registers versioned API routers, and configures Swagger/OpenAPI documentation.
"""

from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.api.v1.routes import router as api_v1_router
from app.middleware.timing import TimingMiddleware

# Setup application-level logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle events."""
    logger.info("Starting FastAPI Async Performance Application...")
    yield
    logger.info("Shutting down FastAPI Async Performance Application...")


app = FastAPI(
    title="FastAPI Async Performance Demo",
    version="1.0.0",
    description="""
An educational, production-structured demonstration of FastAPI comparing
**Synchronous** vs **Asynchronous** endpoint performance under concurrent load.

### Core Features Demonstrated:
- **Async/Await Concurrency**: Non-blocking cooperative multitasking vs blocking thread execution.
- **Middleware Diagnostics**: Automated request timing and `X-Process-Time` response header injection.
- **Background Tasks**: Non-blocking post-response telemetry and audit logging.
- **Dependency Injection**: Declarative request context and service decoupling with `Depends`.
- **API Versioning**: Extensible prefix routing under `/api/v1`.
- **Pydantic Validation**: Strict type enforcement and bounds checking.
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# 1. Register Custom Middleware
app.add_middleware(TimingMiddleware)

# 2. Register Versioned Routers
app.include_router(api_v1_router, prefix="/api/v1")


# 3. Root Endpoint
@app.get(
    "/",
    tags=["Root"],
    summary="Application Welcome & Meta",
    description="Provides quick navigation links to OpenAPI interactive documentation and available API versions.",
)
async def root():
    return JSONResponse(
        content={
            "app_name": "FastAPI Async Performance Demo",
            "version": "1.0.0",
            "status": "online",
            "documentation": {
                "swagger_ui": "/docs",
                "redoc": "/redoc",
                "openapi_json": "/openapi.json",
            },
            "endpoints": {
                "sync_processing": "/api/v1/items/sync",
                "async_processing": "/api/v1/items/async",
                "health_check": "/api/v1/items/health",
            },
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
