"""FastAPI Dependency Injection providers.

This module illustrates FastAPI's Dependency Injection (DI) system using `Depends`.
Dependency Injection allows endpoints to declare their operational requirements
(services, database sessions, request contexts, security credentials) declaratively,
promoting separation of concerns, reusability, and trivial mocking in unit tests.
"""

from dataclasses import dataclass
import uuid
from fastapi import Request
from app.services.service import ItemService


@dataclass
class RequestContext:
    """Encapsulates caller metadata extracted from incoming HTTP requests."""

    request_id: str
    client_host: str
    user_agent: str


def get_request_context(request: Request) -> RequestContext:
    """Dependency that extracts and packages caller metadata.

    Flow:
    Incoming Request -> get_request_context -> Endpoint Parameter

    Extracts:
    - Unique or forwarded Request-ID (or generates a fresh UUID)
    - Client IP address (handling proxy headers if available)
    - User-Agent header
    """
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    client_host = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("User-Agent", "Unknown-Agent")

    return RequestContext(
        request_id=request_id,
        client_host=client_host,
        user_agent=user_agent,
    )


def get_item_service() -> ItemService:
    """Dependency that provides an instance of ItemService.

    Flow:
    Incoming Request -> get_item_service -> Endpoint Parameter -> Service Operation

    Benefits of this pattern:
    - Decouples endpoint routing logic from service instantiation.
    - Enables easy dependency override during testing (`app.dependency_overrides`).
    - Centralizes lifecycle configuration and potential resource pooling.
    """
    return ItemService()
