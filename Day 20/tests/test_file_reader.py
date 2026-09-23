"""Unit tests for the File Reader tool."""

import pytest
from tools.file_reader import FileReaderTool


@pytest.fixture
def reader():
    return FileReaderTool()


def test_file_reader_read_markdown(reader):
    res = reader.execute(file_path="data/internship_notes.md")
    assert res["success"] is True
    assert "Tool Creation" in res["data"]["content"]
    assert res["data"]["metadata"]["extension"] == ".md"


def test_file_reader_read_text(reader):
    res = reader.execute(file_path="data/notes.txt")
    assert res["success"] is True
    assert "Linkific" in res["data"]["content"]


def test_file_reader_read_json(reader):
    res = reader.execute(file_path="data/sample.json")
    assert res["success"] is True
    content = res["data"]["content"]
    assert isinstance(content, dict)
    assert content["project_name"] == "Project Antigravity Agent"


def test_file_reader_read_csv(reader):
    res = reader.execute(file_path="data/employees.csv")
    assert res["success"] is True
    content = res["data"]["content"]
    assert "headers" in content
    assert "Alice Johnson" in str(content["rows"])


def test_file_reader_path_traversal_blocked(reader):
    res = reader.execute(file_path="../../Windows/System32/drivers/etc/hosts")
    assert res["success"] is False
    assert res["error"]["type"] == "SecurityError"


def test_file_reader_missing_file(reader):
    res = reader.execute(file_path="data/missing_file_abc.txt")
    assert res["success"] is False
    assert res["error"]["type"] == "ResourceNotFoundError"


def test_file_reader_unsupported_extension(reader):
    res = reader.execute(file_path="main.py")
    # main.py is python (.py), allowed are .txt, .md, .json, .csv
    assert res["success"] is False
    assert res["error"]["type"] == "ValidationError"
