"""Structured Logging Configuration for Production Observability.

Implements JSON structured logging, log level management, contextvars-based
request correlation tracking (Request ID), and integration with standard Python logging.
"""

from contextvars import ContextVar
import logging
import sys
from typing import Optional
from pythonjsonlogger import jsonlogger

# Context variable to hold request correlation ID across async execution contexts
correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id", default="system")


def get_correlation_id() -> str:
    """Get the current request correlation ID."""
    return correlation_id_ctx.get()


def set_correlation_id(correlation_id: str) -> None:
    """Set the current request correlation ID."""
    correlation_id_ctx.set(correlation_id)


class CorrelationIdFilter(logging.Filter):
    """Logging filter that injects correlation ID and service metadata into every log record."""

    def __init__(self, service_name: str = "linkific-service", env: str = "development") -> None:
        super().__init__()
        self.service_name = service_name
        self.env = env

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_correlation_id()
        record.service = self.service_name
        record.env = self.env
        return True


def setup_logging(
    log_level: str = "INFO",
    log_format: str = "json",
    service_name: str = "linkific-service",
    env: str = "development",
) -> None:
    """Configure root logger and standard loggers with structured formatting."""
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Remove existing handlers to avoid duplicates
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)

    # Attach correlation filter
    corr_filter = CorrelationIdFilter(service_name=service_name, env=env)
    console_handler.addFilter(corr_filter)

    if log_format.lower() == "json":
        formatter = jsonlogger.JsonFormatter(
            fmt="%(asctime)s %(levelname)s %(name)s %(request_id)s %(service)s %(env)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S%z",
        )
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [req:%(request_id)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Configure uvicorn loggers to use root handlers
    for uvicorn_logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        u_logger = logging.getLogger(uvicorn_logger_name)
        u_logger.handlers = [console_handler]
        u_logger.propagate = False
        u_logger.setLevel(numeric_level)


def get_logger(name: str) -> logging.Logger:
    """Retrieve named logger."""
    return logging.getLogger(name)
