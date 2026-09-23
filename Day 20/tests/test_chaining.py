"""Unit tests for multi-tool chaining workflows."""

import pytest
from core.chain_orchestrator import ToolChainOrchestrator


@pytest.fixture
def orchestrator():
    return ToolChainOrchestrator()


def test_chain_1_file_reader_to_data_analyzer(orchestrator):
    query = "Read employees.csv and calculate the average salary."
    res = orchestrator.execute_request(query)
    assert res["is_chain"] is True
    assert res["tools_called"] == ["file_reader", "data_analyzer"]
    assert len(res["trace"]) == 2
    assert res["trace"][0]["output"]["success"] is True
    assert res["trace"][1]["output"]["success"] is True
    assert "Mean salary is $" in res["final_answer"]


def test_chain_2_weather_to_calculator(orchestrator):
    query = "Get the weather in Kolkata and convert the temperature to Fahrenheit."
    res = orchestrator.execute_request(query)
    assert res["is_chain"] is True
    assert res["tools_called"] == ["weather", "calculator"]
    assert len(res["trace"]) == 2
    assert res["trace"][0]["output"]["success"] is True
    assert res["trace"][1]["output"]["success"] is True
    # Kolkata is 28.5 C -> 83.3 F
    assert "°F" in res["final_answer"]


def test_chain_3_database_to_data_analyzer(orchestrator):
    query = "Find all Engineering employees from the database and calculate their average salary."
    res = orchestrator.execute_request(query)
    assert res["is_chain"] is True
    assert res["tools_called"] == ["database", "data_analyzer"]
    assert len(res["trace"]) == 2
    assert res["trace"][0]["output"]["success"] is True
    assert res["trace"][1]["output"]["success"] is True
    assert "Average salary is $" in res["final_answer"]


def test_chain_4_file_reader_to_analyzer_json(orchestrator):
    query = "Read the project status from sample.json and prepare a summary."
    res = orchestrator.execute_request(query)
    assert res["is_chain"] is True
    assert res["tools_called"] == ["file_reader", "data_analyzer"]
    assert len(res["trace"]) == 2
    assert res["trace"][0]["output"]["success"] is True
    assert "Project Summary" in res["final_answer"]


def test_chain_5_weather_to_email(orchestrator):
    query = "Find the current weather for Kolkata and email the result to mentor@example.com"
    res = orchestrator.execute_request(query)
    assert res["is_chain"] is True
    assert res["tools_called"] == ["weather", "email"]
    assert len(res["trace"]) == 2
    assert res["trace"][0]["output"]["success"] is True
    assert res["trace"][1]["output"]["success"] is True
    assert "queued automated email briefing" in res["final_answer"]


def test_chain_graceful_failure_when_file_missing(orchestrator):
    query = "Read nonexistent_file_999.csv and calculate the average salary."
    res = orchestrator.execute_request(query)
    assert res["is_chain"] is True
    assert "stopped with error" in res["final_answer"]
    assert res["trace"][0]["output"]["success"] is False
