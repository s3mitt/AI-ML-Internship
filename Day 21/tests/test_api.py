"""Automated integration and unit test suite.

Tests all 10 required project capabilities:
1. Sync endpoint returns 200
2. Async endpoint returns 200
3. Correct response payload structure and calculations
4. Validation rejects invalid quantity (negative/zero)
5. Validation rejects invalid price (negative/zero)
6. Missing required fields return 422
7. Middleware injects `X-Process-Time` header
8. API versioning routing works under /api/v1
9. BackgroundTask writes audit logs to disk
10. FastAPI Dependency Injection functions and can be overridden
"""

import os
from pathlib import Path
import pytest
from starlette.testclient import TestClient

from app.dependencies.dependencies import get_item_service
from app.main import app
from app.models.schemas import ItemCreate, ItemResponse
from app.services.service import AUDIT_LOG_FILE, ItemService

client = TestClient(app)


@pytest.fixture(autouse=True)
def ensure_clean_log():
    """Ensure the log directory exists and clean test logs."""
    AUDIT_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    yield


def test_root_endpoint():
    """Verify application root welcome route and metadata."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["app_name"] == "FastAPI Async Performance Demo"
    assert "documentation" in data
    assert "endpoints" in data


def test_1_sync_endpoint_success():
    """Test 1: Verify synchronous endpoint returns 200 OK."""
    payload = {"name": "Mechanical Keyboard", "quantity": 3, "price": 4500.0}
    response = client.post("/api/v1/items/sync", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Mechanical Keyboard"
    assert data["status"] == "completed"
    assert data["processing_type"] == "sync"


def test_2_async_endpoint_success():
    """Test 2: Verify asynchronous endpoint returns 200 OK."""
    payload = {"name": "Ergonomic Mouse", "quantity": 2, "price": 2500.0}
    response = client.post("/api/v1/items/async", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Ergonomic Mouse"
    assert data["status"] == "completed"
    assert data["processing_type"] == "async"


def test_3_response_structure_validation():
    """Test 3: Verify all expected fields, types, and computed math."""
    payload = {"name": "4K Monitor", "quantity": 2, "price": 32000.0}
    response = client.post("/api/v1/items/async", json=payload)
    assert response.status_code == 200
    data = response.json()

    # Field presence assertions
    required_fields = [
        "id",
        "name",
        "quantity",
        "price",
        "total_price",
        "status",
        "processing_type",
        "processed_at",
        "message",
    ]
    for field in required_fields:
        assert field in data, f"Missing expected field: {field}"

    # Business logic verification
    assert data["total_price"] == round(payload["quantity"] * payload["price"], 2)
    assert len(data["id"]) > 0


def test_4_validation_rejects_invalid_quantity():
    """Test 4: Verify Pydantic rejects non-positive quantity with 422."""
    payload = {"name": "Tablet", "quantity": -1, "price": 15000.0}
    response = client.post("/api/v1/items/async", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    # Quantity error is reported
    errors = [err["loc"][-1] for err in data["detail"]]
    assert "quantity" in errors

    # Zero quantity should also be rejected
    payload_zero = {"name": "Tablet", "quantity": 0, "price": 15000.0}
    response_zero = client.post("/api/v1/items/async", json=payload_zero)
    assert response_zero.status_code == 422


def test_5_validation_rejects_invalid_price():
    """Test 5: Verify Pydantic rejects non-positive price with 422."""
    payload = {"name": "Tablet", "quantity": 1, "price": -500.0}
    response = client.post("/api/v1/items/async", json=payload)
    assert response.status_code == 422
    data = response.json()
    errors = [err["loc"][-1] for err in data["detail"]]
    assert "price" in errors

    # Zero price should also be rejected
    payload_zero = {"name": "Tablet", "quantity": 1, "price": 0.0}
    response_zero = client.post("/api/v1/items/async", json=payload_zero)
    assert response_zero.status_code == 422


def test_6_validation_rejects_missing_fields():
    """Test 6: Verify missing required fields trigger 422 Unprocessable Entity."""
    # Missing name
    response_no_name = client.post(
        "/api/v1/items/async", json={"quantity": 2, "price": 100.0}
    )
    assert response_no_name.status_code == 422

    # Missing quantity
    response_no_qty = client.post(
        "/api/v1/items/async", json={"name": "Headphones", "price": 100.0}
    )
    assert response_no_qty.status_code == 422

    # Missing price
    response_no_price = client.post(
        "/api/v1/items/async", json={"name": "Headphones", "quantity": 2}
    )
    assert response_no_price.status_code == 422

    # Name too short (< 2 chars)
    response_short_name = client.post(
        "/api/v1/items/async", json={"name": "A", "quantity": 2, "price": 100.0}
    )
    assert response_short_name.status_code == 422


def test_7_middleware_adds_x_process_time_header():
    """Test 7: Verify TimingMiddleware adds X-Process-Time response header."""
    payload = {"name": "Webcam", "quantity": 1, "price": 3500.0}
    response = client.post("/api/v1/items/sync", json=payload)
    assert "x-process-time" in response.headers
    process_time = float(response.headers["x-process-time"])
    assert process_time > 0.0


def test_8_api_versioning_works():
    """Test 8: Verify routes are mounted under /api/v1 and future versions are cleanly separated."""
    # V1 Health route exists
    v1_health = client.get("/api/v1/items/health")
    assert v1_health.status_code == 200
    assert v1_health.json() == {"status": "ok", "version": "v1"}

    # V2 does not exist yet (should return 404)
    v2_attempt = client.get("/api/v2/items/health")
    assert v2_attempt.status_code == 404

    # Unversioned route should return 404
    unversioned = client.post(
        "/items/sync", json={"name": "Test", "quantity": 1, "price": 10.0}
    )
    assert unversioned.status_code == 404


def test_9_background_task_is_triggered():
    """Test 9: Verify BackgroundTasks writes audit event to disk."""
    unique_name = f"AuditProduct-{os.urandom(4).hex()}"
    payload = {"name": unique_name, "quantity": 5, "price": 120.0}

    # Execute request
    response = client.post("/api/v1/items/async", json=payload)
    assert response.status_code == 200
    item_id = response.json()["id"]

    # Background task writes to AUDIT_LOG_FILE
    assert AUDIT_LOG_FILE.exists()
    content = AUDIT_LOG_FILE.read_text(encoding="utf-8")
    assert item_id in content
    assert unique_name in content
    assert "AUDIT_RECORDED" in content


def test_10_dependency_injection_works():
    """Test 10: Verify Dependency Injection works and can be overridden for testing."""

    class MockItemService(ItemService):
        def process_item_sync(self, item: ItemCreate, client_ip: str = "unknown"):
            # Instant mock execution without delay
            return ItemResponse(
                id="mock-id-12345",
                name=f"MOCKED_{item.name}",
                quantity=item.quantity,
                price=item.price,
                total_price=round(item.quantity * item.price, 2),
                status="mock_completed",
                processing_type="sync",
                processed_at="2026-09-24T00:00:00Z",
                message="Mock dependency injected successfully",
            )

    # Apply override
    app.dependency_overrides[get_item_service] = MockItemService

    try:
        payload = {"name": "Desk Lamp", "quantity": 1, "price": 1500.0}
        response = client.post("/api/v1/items/sync", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "mock-id-12345"
        assert data["name"] == "MOCKED_Desk Lamp"
        assert data["status"] == "mock_completed"
    finally:
        # Clean up dependency override
        app.dependency_overrides.clear()
