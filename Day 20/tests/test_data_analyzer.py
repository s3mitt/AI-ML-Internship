"""Unit tests for the Data Analyzer tool."""

import pytest
from tools.data_analyzer import DataAnalyzerTool


@pytest.fixture
def analyzer():
    return DataAnalyzerTool()


def test_data_analyzer_csv_file(analyzer):
    res = analyzer.execute(file_path="data/employees.csv")
    assert res["success"] is True
    data = res["data"]
    assert data["rows"] == 10
    assert "salary" in data["statistics"]
    assert data["statistics"]["salary"]["mean"] > 0
    assert data["statistics"]["salary"]["min"] == 45000
    assert data["statistics"]["salary"]["max"] == 95000


def test_data_analyzer_group_by_department(analyzer):
    res = analyzer.execute(file_path="data/employees.csv", group_by="department")
    assert res["success"] is True
    groups = res["data"]["group_by"]["groups"]
    assert "Engineering" in groups
    assert groups["Engineering"]["row_count"] == 5
    assert "avg_salary" in groups["Engineering"]


def test_data_analyzer_in_memory_records(analyzer):
    records = [
        {"item": "Laptop", "price": 1200},
        {"item": "Mouse", "price": 40},
        {"item": "Monitor", "price": 300},
    ]
    res = analyzer.execute(data=records)
    assert res["success"] is True
    assert res["data"]["rows"] == 3
    assert res["data"]["statistics"]["price"]["mean"] > 0


def test_data_analyzer_nonexistent_file(analyzer):
    res = analyzer.execute(file_path="data/missing_analytics.csv")
    assert res["success"] is False
    assert res["error"]["type"] == "ResourceNotFoundError"


def test_data_analyzer_invalid_target_column(analyzer):
    res = analyzer.execute(file_path="data/employees.csv", target_column="nonexistent_column")
    assert res["success"] is False
    assert res["error"]["type"] == "ValidationError"


def test_data_analyzer_empty_in_memory_data(analyzer):
    res = analyzer.execute(data=[])
    assert res["success"] is False
    assert res["error"]["type"] == "ValidationError"
