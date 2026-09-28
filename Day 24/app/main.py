"""FastAPI Main Application Entrypoint.

Configures application lifecycle, CORS, structured logging, correlation ID tracking,
Prometheus request instrumentation middleware, error handling, and API routers.
"""

from contextlib import asynccontextmanager
import time
from typing import AsyncGenerator
import uuid
from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .config import get_settings
from .logging_config import get_logger, set_correlation_id, setup_logging
from .monitoring import HTTP_ACTIVE_REQUESTS, record_request_metrics
from .routers import health_router, metrics_router, tasks_router

logger = get_logger("linkific.main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan context manager for startup and shutdown hooks."""
    settings = get_settings()

    # Initialize structured logging
    setup_logging(
        log_level=settings.LOG_LEVEL,
        log_format=settings.LOG_FORMAT,
        service_name=settings.APP_NAME,
        env=settings.APP_ENV,
    )

    logger.info(
        "Application starting up",
        extra={
            "app_name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.APP_ENV,
            "debug": settings.APP_DEBUG,
            "port": settings.PORT,
            "metrics_enabled": settings.METRICS_ENABLED,
        },
    )

    yield

    logger.info("Application shutting down gracefully")


def create_application() -> FastAPI:
    """Factory function creating configured FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Production-grade API with Pytest, Logging, Docker, Env Vars, and Monitoring",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Middleware: Request Correlation ID and Prometheus Request Instrumentation
    @app.middleware("http")
    async def observability_middleware(request: Request, call_next):
        # 1. Correlation ID management
        req_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        set_correlation_id(req_id)

        # 2. Latency measurement and active connection tracking
        HTTP_ACTIVE_REQUESTS.inc()
        start_time = time.perf_counter()

        endpoint_path = request.url.path
        method = request.method

        logger.info(
            f"Incoming request: {method} {endpoint_path}",
            extra={"http_method": method, "path": endpoint_path, "client_ip": request.client.host if request.client else "unknown"},
        )

        try:
            response: Response = await call_next(request)
            duration = time.perf_counter() - start_time
            record_request_metrics(
                method=method,
                endpoint=endpoint_path,
                status_code=response.status_code,
                duration_seconds=duration,
            )

            # Attach correlation ID to response headers
            response.headers["X-Request-ID"] = req_id
            response.headers["X-Response-Time-Ms"] = f"{round(duration * 1000, 2)}"

            logger.info(
                f"Completed request: {method} {endpoint_path} - status {response.status_code}",
                extra={"status_code": response.status_code, "duration_ms": round(duration * 1000, 2)},
            )
            return response

        except Exception as exc:
            duration = time.perf_counter() - start_time
            record_request_metrics(
                method=method,
                endpoint=endpoint_path,
                status_code=500,
                duration_seconds=duration,
            )
            logger.error(
                f"Unhandled exception processing {method} {endpoint_path}: {exc}",
                extra={"error": str(exc), "duration_ms": round(duration * 1000, 2)},
                exc_info=True,
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "InternalServerError",
                    "detail": "An unexpected error occurred during request processing.",
                    "request_id": req_id,
                },
                headers={"X-Request-ID": req_id},
            )

        finally:
            HTTP_ACTIVE_REQUESTS.dec()

    # Exception Handlers
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        from .logging_config import get_correlation_id

        req_id = get_correlation_id()
        logger.warning(
            "Request validation failed",
            extra={"errors": exc.errors(), "body": str(exc.body)},
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "ValidationError",
                "detail": exc.errors(),
                "request_id": req_id,
            },
            headers={"X-Request-ID": req_id},
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        from .logging_config import get_correlation_id

        req_id = get_correlation_id()
        logger.warning(
            f"HTTP Exception: {exc.status_code} - {exc.detail}",
            extra={"status_code": exc.status_code, "detail": exc.detail},
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "ClientError" if exc.status_code < 500 else "ServerError",
                "detail": exc.detail,
                "request_id": req_id,
            },
            headers={"X-Request-ID": req_id},
        )

    # Register Routers
    app.include_router(health_router)
    app.include_router(metrics_router)
    app.include_router(tasks_router)

    # Root Discovery Endpoint
    @app.get("/", tags=["System"])
    async def root_index():
        return {
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.APP_ENV,
            "docs_url": "/docs",
            "health_check": "/health",
            "metrics": "/metrics",
        }

    return app


app = create_application()
