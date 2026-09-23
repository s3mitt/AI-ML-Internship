"""Unit tests for the Database tool."""

import pytest
from tools.database import DatabaseTool


@pytest.fixture
def db():
    return DatabaseTool()


def test_database_find_engineering_employees(db):
    res = db.execute(
        query="SELECT * FROM employees WHERE department = ?",
        parameters=["Engineering"],
    )
    assert res["success"] is True
    rows = res["data"]["rows"]
    assert len(rows) >= 5
    assert all(r["department"] == "Engineering" for r in rows)


def test_database_salary_filter(db):
    res = db.execute(
        query="SELECT * FROM employees WHERE salary > ?",
        parameters=[50000],
    )
    assert res["success"] is True
    rows = res["data"]["rows"]
    assert len(rows) > 0
    assert all(r["salary"] > 50000 for r in rows)


def test_database_count_by_department(db):
    res = db.execute(
        query="SELECT department, COUNT(*) as count FROM employees GROUP BY department"
    )
    assert res["success"] is True
    rows = res["data"]["rows"]
    depts = [r["department"] for r in rows]
    assert "Engineering" in depts
    assert "Human Resources" in depts


def test_database_project_information(db):
    res = db.execute(
        query="SELECT * FROM projects WHERE status = ?",
        parameters=["Active"],
    )
    assert res["success"] is True
    rows = res["data"]["rows"]
    assert len(rows) >= 3


def test_database_blocks_destructive_sql(db):
    res = db.execute(query="DROP TABLE employees")
    assert res["success"] is False
    assert res["error"]["type"] == "SecurityError"
    assert "Only SELECT queries are allowed" in res["error"]["message"]


def test_database_malformed_sql(db):
    res = db.execute(query="SELECT * FROM nonexistent_table_xyz")
    assert res["success"] is False
    assert res["error"]["type"] == "ValidationError"
