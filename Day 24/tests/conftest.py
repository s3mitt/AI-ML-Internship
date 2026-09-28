"""Pytest Shared Fixtures for Unit and API Integration Tests."""

from typing import Any, Dict, Generator
from fastapi.testclient import TestClient
import pytest
from app.config import Settings, get_settings
from app.main import create_application
from app.services.task_service import TaskService, get_task_service


@pytest.fixture(scope="session")
def app_instance():
    """Create application instance for testing."""
    return create_application()


@pytest.fixture(scope="session")
def client(app_instance) -> Generator[TestClient, None, None]:
    """Test client fixture configured with test application."""
    with TestClient(app_instance) as c:
        yield c


@pytest.fixture(autouse=True)
def clean_task_service() -> Generator[TaskService, None, None]:
    """Ensure the in-memory task service is cleared before and after each test."""
    service = get_task_service()
    service.clear()
    yield service
    service.clear()


@pytest.fixture
def sample_task_payload() -> Dict[str, Any]:
    """Generate a valid task creation payload dictionary."""
    return {
        "title": "Automated Unit Test Execution",
        "task_type": "unit_test",
        "priority": "high",
        "payload": {
            "test_runner": "pytest",
            "coverage_target": 95.0,
        },
    }


@pytest.fixture
def mock_env(monkeypatch: pytest.MonkeyPatch):
    """Fixture providing helper to dynamically patch environment variables."""

    def _set_env(**kwargs: Any):
        for k, v in kwargs.items():
            monkeypatch.setenv(k, str(v))
        get_settings.cache_clear()

    return _set_env
