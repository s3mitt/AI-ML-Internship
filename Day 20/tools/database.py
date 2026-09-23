"""Database Tool: Safe parameterized SQLite interaction with strict read-only query guardrails."""

from __future__ import annotations
import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from core.errors import ResourceNotFoundError, SecurityError, ValidationError
from tools.base import BaseTool

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "app.db"

FORBIDDEN_SQL_KEYWORDS = ["DROP", "DELETE", "TRUNCATE", "ALTER", "UPDATE", "INSERT", "GRANT", "REVOKE"]


def init_database(db_path: Path = DEFAULT_DB_PATH) -> None:
    """Create and seed default SQLite database if not present."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        department TEXT NOT NULL,
        role TEXT NOT NULL,
        salary REAL NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        status TEXT NOT NULL,
        owner TEXT NOT NULL
    )
    """)

    # Check if empty, seed if so
    cursor.execute("SELECT COUNT(*) FROM employees")
    if cursor.fetchone()[0] == 0:
        employees_data = [
            (1, "Alice Johnson", "Engineering", "Senior Software Engineer", 95000),
            (2, "Bob Smith", "Engineering", "DevOps Engineer", 82000),
            (3, "Charlie Brown", "Human Resources", "HR Manager", 65000),
            (4, "Diana Prince", "Engineering", "Backend Developer", 72000),
            (5, "Evan Wright", "Marketing", "Marketing Lead", 58000),
            (6, "Fiona Gallagher", "Sales", "Account Executive", 54000),
            (7, "George Clark", "Engineering", "Frontend Developer", 68000),
            (8, "Hannah Abbott", "Human Resources", "HR Coordinator", 45000),
            (9, "Ian Malcolm", "Engineering", "Data Scientist", 88000),
            (10, "Julia Roberts", "Marketing", "Content Specialist", 48000),
        ]
        cursor.executemany("INSERT INTO employees VALUES (?, ?, ?, ?, ?)", employees_data)

    cursor.execute("SELECT COUNT(*) FROM projects")
    if cursor.fetchone()[0] == 0:
        projects_data = [
            (1, "AI Autonomous Agent", "Active", "Alice Johnson"),
            (2, "Cloud Infrastructure Migration", "Active", "Bob Smith"),
            (3, "HR Talent Acquisition System", "Planning", "Charlie Brown"),
            (4, "Customer Portal Redesign", "Completed", "George Clark"),
            (5, "Analytics Dashboard", "Active", "Ian Malcolm"),
        ]
        cursor.executemany("INSERT INTO projects VALUES (?, ?, ?, ?)", projects_data)

    conn.commit()
    conn.close()


class DatabaseTool(BaseTool):
    """Executes safe, parameterized read queries against the SQLite database."""

    name = "database"
    description = (
        "Execute safe SQL queries on SQLite database tables (employees, projects). "
        "Allows querying employees by department/salary, department counts, and project statuses."
    )
    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "SQL SELECT query string (must use '?' placeholders for parameters).",
            },
            "parameters": {
                "type": "array",
                "description": "Positional parameter values for the parameterized SQL query.",
            },
            "db_path": {
                "type": "string",
                "description": "Optional custom database file path.",
            },
        },
        "required": ["query"],
    }
    examples = [
        {
            "query": "SELECT * FROM employees WHERE department = ? AND salary > ?",
            "parameters": ["Engineering", 70000],
        },
        {
            "query": "SELECT department, COUNT(*) as count, AVG(salary) as avg_salary FROM employees GROUP BY department",
        },
        {
            "query": "SELECT * FROM projects WHERE status = ?",
            "parameters": ["Active"],
        },
    ]

    def __init__(self, db_path: Optional[str] = None):
        super().__init__()
        self.default_db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        init_database(self.default_db_path)

    def _validate_sql_safety(self, sql: str) -> None:
        """Enforce strict read-only SELECT constraints to prevent destructive SQL execution."""
        clean = sql.strip().upper()
        if not clean.startswith("SELECT") and not clean.startswith("WITH"):
            raise SecurityError("Only SELECT queries are allowed. Destructive queries are strictly rejected.", tool_name=self.name)

        tokens = set(clean.replace(";", " ").split())
        for forbidden in FORBIDDEN_SQL_KEYWORDS:
            if forbidden in tokens:
                raise SecurityError(f"Forbidden SQL keyword '{forbidden}' detected.", tool_name=self.name)

    def run(self, query: str, parameters: Optional[List[Any]] = None, db_path: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Execute safe parameterized read query and return structured records."""
        if not query or not query.strip():
            raise ValidationError("SQL query cannot be empty.", tool_name=self.name)

        target_db = Path(db_path) if db_path else self.default_db_path
        if not target_db.exists():
            raise ResourceNotFoundError(f"Database file not found at: {target_db}", tool_name=self.name)

        self._validate_sql_safety(query)

        params: Tuple[Any, ...] = tuple(parameters) if parameters else ()

        try:
            conn = sqlite3.connect(str(target_db))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description] if cursor.description else []
            data = [dict(row) for row in rows]
            conn.close()
            return {
                "query": query,
                "parameters": list(params),
                "columns": columns,
                "row_count": len(data),
                "rows": data,
            }
        except sqlite3.OperationalError as oe:
            raise ValidationError(f"SQL execution error: {oe}", tool_name=self.name)
        except Exception as exc:
            raise ValidationError(f"Database query failure: {exc}", tool_name=self.name)
