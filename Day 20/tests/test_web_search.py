"""Unit tests for the Web Search tool."""

import pytest
from tools.web_search import WebSearchTool


@pytest.fixture
def search_tool():
    return WebSearchTool()


def test_web_search_valid_query(search_tool):
    res = search_tool.execute(query="Latest developments in artificial intelligence")
    assert res["success"] is True
    data = res["data"]
    assert data["query"] == "Latest developments in artificial intelligence"
    assert len(data["results"]) > 0
    assert "url" in data["results"][0]
    assert "snippet" in data["results"][0]


def test_web_search_result_limit(search_tool):
    res = search_tool.execute(query="Python programming", num_results=2)
    assert res["success"] is True
    assert len(res["data"]["results"]) <= 2


def test_web_search_empty_query(search_tool):
    res = search_tool.execute(query="")
    assert res["success"] is False
    assert res["error"]["type"] == "ValidationError"


def test_web_search_simulated_timeout(search_tool):
    res = search_tool.execute(query="Test query", simulate_error="timeout")
    assert res["success"] is False
    assert res["error"]["type"] == "ExternalServiceError"
    assert "timed out" in res["error"]["message"].lower()


def test_web_search_simulated_rate_limit(search_tool):
    res = search_tool.execute(query="Test query", simulate_error="rate_limit")
    assert res["success"] is False
    assert res["error"]["type"] == "ExternalServiceError"
    assert "rate limit" in res["error"]["message"].lower()
