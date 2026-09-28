"""API integration tests for Task Management and Execution Endpoints."""

from typing import Any, Dict
from fastapi.testclient import TestClient
import pytest


@pytest.mark.api
class TestTasksApi:
    """Test suite verifying task CRUD, execution workflows, schema validation, and error responses."""

    def test_create_task_success(self, client: TestClient, sample_task_payload: Dict[str, Any]):
        """Verify successful task creation returns 201 and pending task record."""
        response = client.post("/api/v1/tasks", json=sample_task_payload)
        assert response.status_code == 201
        data = response.json()
        assert data["task_id"] is not None
        assert data["title"] == sample_task_payload["title"]
        assert data["task_type"] == sample_task_payload["task_type"]
        assert data["status"] == "pending"
        assert data["result"] is None

    def test_create_task_validation_errors(self, client: TestClient):
        """Verify 422 Unprocessable Entity for invalid payloads."""
        # 1. Title too short (<3 chars)
        res1 = client.post("/api/v1/tasks", json={"title": "ab", "task_type": "unit_test"})
        assert res1.status_code == 422
        assert res1.json()["error"] == "ValidationError"

        # 2. Unsupported task_type
        res2 = client.post("/api/v1/tasks", json={"title": "Valid Title", "task_type": "invalid_type"})
        assert res2.status_code == 422

        # 3. Invalid priority
        res3 = client.post(
            "/api/v1/tasks",
            json={"title": "Valid Title", "task_type": "unit_test", "priority": "ultra"},
        )
        assert res3.status_code == 422

    def test_get_task_by_id(self, client: TestClient, sample_task_payload: Dict[str, Any]):
        """Verify retrieving task by valid ID returns 200."""
        create_res = client.post("/api/v1/tasks", json=sample_task_payload)
        task_id = create_res.json()["task_id"]

        get_res = client.get(f"/api/v1/tasks/{task_id}")
        assert get_res.status_code == 200
        assert get_res.json()["task_id"] == task_id

    def test_get_task_not_found(self, client: TestClient):
        """Verify retrieving non-existent task ID returns 404."""
        response = client.get("/api/v1/tasks/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404
        assert response.json()["error"] == "ClientError"

    def test_execute_task_success(self, client: TestClient, sample_task_payload: Dict[str, Any]):
        """Verify executing an existing task transitions state to completed with metrics."""
        create_res = client.post("/api/v1/tasks", json=sample_task_payload)
        task_id = create_res.json()["task_id"]

        exec_res = client.post(f"/api/v1/tasks/{task_id}/execute")
        assert exec_res.status_code == 200
        data = exec_res.json()
        assert data["task_id"] == task_id
        assert data["status"] == "completed"
        assert data["result"] is not None
        assert data["completed_at"] is not None
        assert data["execution_time_ms"] is not None

    def test_execute_task_not_found(self, client: TestClient):
        """Verify executing non-existent task returns 404."""
        response = client.post("/api/v1/tasks/invalid-id/execute")
        assert response.status_code == 404

    def test_list_tasks_and_filter(self, client: TestClient):
        """Verify listing all tasks and filtering by status."""
        client.post("/api/v1/tasks", json={"title": "Task A", "task_type": "unit_test"})
        res2 = client.post("/api/v1/tasks", json={"title": "Task B", "task_type": "analysis"})
        task_b_id = res2.json()["task_id"]

        # Execute Task B
        client.post(f"/api/v1/tasks/{task_b_id}/execute")

        # List all
        all_res = client.get("/api/v1/tasks")
        assert all_res.status_code == 200
        assert all_res.json()["total"] == 2

        # Filter completed
        completed_res = client.get("/api/v1/tasks?status=completed")
        assert completed_res.status_code == 200
        assert completed_res.json()["total"] == 1
        assert completed_res.json()["tasks"][0]["task_id"] == task_b_id

    def test_delete_task(self, client: TestClient, sample_task_payload: Dict[str, Any]):
        """Verify deleting task returns 204, then 404 on subsequent lookups."""
        create_res = client.post("/api/v1/tasks", json=sample_task_payload)
        task_id = create_res.json()["task_id"]

        # Delete
        del_res = client.delete(f"/api/v1/tasks/{task_id}")
        assert del_res.status_code == 204

        # Verify gone
        get_res = client.get(f"/api/v1/tasks/{task_id}")
        assert get_res.status_code == 404

        # Delete again -> 404
        del_again = client.delete(f"/api/v1/tasks/{task_id}")
        assert del_again.status_code == 404

    def test_end_to_end_lifecycle(self, client: TestClient):
        """Full end-to-end task workflow lifecycle test."""
        # Step 1: Create
        payload = {
            "title": "Full Lifecycle Pipeline Test",
            "task_type": "system_audit",
            "priority": "critical",
            "payload": {"environment": "production"},
        }
        res_create = client.post("/api/v1/tasks", json=payload)
        assert res_create.status_code == 201
        task_id = res_create.json()["task_id"]

        # Step 2: Verify in pending list
        res_pending = client.get("/api/v1/tasks?status=pending")
        assert any(t["task_id"] == task_id for t in res_pending.json()["tasks"])

        # Step 3: Execute
        res_exec = client.post(f"/api/v1/tasks/{task_id}/execute")
        assert res_exec.status_code == 200
        assert res_exec.json()["status"] == "completed"

        # Step 4: Verify in completed list
        res_completed = client.get("/api/v1/tasks?status=completed")
        assert any(t["task_id"] == task_id for t in res_completed.json()["tasks"])

        # Step 5: Clean up
        res_del = client.delete(f"/api/v1/tasks/{task_id}")
        assert res_del.status_code == 204
