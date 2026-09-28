"""Unit tests for Task Service Business Logic and Execution Engine."""

import pytest
from app.models.schemas import TaskCreateRequest
from app.services.task_service import TaskService


@pytest.mark.unit
class TestTaskService:
    """Test suite verifying task creation, state transitions, execution, and error handling."""

    def test_create_task(self):
        """Verify task creation produces valid pending task."""
        service = TaskService()
        req = TaskCreateRequest(
            title="Database Migration Audit",
            task_type="system_audit",
            priority="high",
            payload={"target_schema": "v2"},
        )
        task = service.create_task(req)

        assert task.task_id is not None
        assert task.title == "Database Migration Audit"
        assert task.task_type == "system_audit"
        assert task.priority == "high"
        assert task.status == "pending"
        assert task.result is None
        assert task.error is None

    @pytest.mark.parametrize(
        "task_type",
        ["unit_test", "data_processing", "analysis", "system_audit"],
    )
    def test_execute_task_supported_types(self, task_type: str):
        """Verify execution succeeds across all supported task types."""
        service = TaskService()
        req = TaskCreateRequest(
            title=f"Sample {task_type} operation",
            task_type=task_type,
            priority="medium",
        )
        created = service.create_task(req)
        executed = service.execute_task(created.task_id)

        assert executed.status == "completed"
        assert executed.result is not None
        assert executed.error is None
        assert executed.completed_at is not None
        assert executed.execution_time_ms is not None
        assert executed.execution_time_ms >= 0

    def test_execute_nonexistent_task_raises_error(self):
        """Verify executing an uncreated task ID raises ValueError."""
        service = TaskService()
        with pytest.raises(ValueError) as exc:
            service.execute_task("nonexistent-uuid-12345")
        assert "not found" in str(exc.value)

    def test_get_task(self):
        """Verify task retrieval by ID."""
        service = TaskService()
        req = TaskCreateRequest(
            title="Telemetry Audit",
            task_type="system_audit",
            priority="low",
        )
        created = service.create_task(req)

        retrieved = service.get_task(created.task_id)
        assert retrieved is not None
        assert retrieved.task_id == created.task_id

        assert service.get_task("missing-id") is None

    def test_list_tasks_and_filter_by_status(self):
        """Verify task listing and filtering by status."""
        service = TaskService()
        req1 = TaskCreateRequest(title="Task 1", task_type="unit_test")
        req2 = TaskCreateRequest(title="Task 2", task_type="analysis")

        t1 = service.create_task(req1)
        t2 = service.create_task(req2)

        service.execute_task(t1.task_id)

        all_tasks = service.list_tasks()
        assert len(all_tasks) == 2

        pending_tasks = service.list_tasks(status="pending")
        assert len(pending_tasks) == 1
        assert pending_tasks[0].task_id == t2.task_id

        completed_tasks = service.list_tasks(status="completed")
        assert len(completed_tasks) == 1
        assert completed_tasks[0].task_id == t1.task_id

    def test_delete_task(self):
        """Verify task deletion."""
        service = TaskService()
        req = TaskCreateRequest(title="Ephemeral Task", task_type="analysis")
        t = service.create_task(req)

        assert service.delete_task(t.task_id) is True
        assert service.get_task(t.task_id) is None
        assert service.delete_task(t.task_id) is False
