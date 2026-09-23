"""Unit tests for the Function Calling Router."""

import pytest
from core.router import FunctionCallingRouter


@pytest.fixture
def router():
    return FunctionCallingRouter()


def test_router_single_tool_calculator(router):
    decision = router.route("Calculate 45 * 23")
    assert decision.is_chain is False
    assert decision.tools == ["calculator"]
    assert "45 * 23" in decision.initial_params["expression"]


def test_router_single_tool_weather(router):
    decision = router.route("What's the weather in Kolkata?")
    assert decision.is_chain is False
    assert decision.tools == ["weather"]
    assert decision.initial_params["location"].lower() == "kolkata"


def test_router_single_tool_web_search(router):
    decision = router.route("Search the web for the latest AI news.")
    assert decision.is_chain is False
    assert decision.tools == ["web_search"]
    assert "query" in decision.initial_params


def test_router_single_tool_database(router):
    decision = router.route("Find Engineering employees earning above 50000.")
    assert decision.is_chain is False
    assert decision.tools == ["database"]
    assert "query" in decision.initial_params


def test_router_single_tool_date(router):
    decision = router.route("What date will it be 45 days from today?")
    assert decision.is_chain is False
    assert decision.tools == ["date_tool"]
    assert decision.initial_params["action"] == "add_days"
    assert decision.initial_params["days"] == 45


def test_router_chain_file_to_analytics(router):
    decision = router.route("Read employees.csv and calculate the average salary.")
    assert decision.is_chain is True
    assert decision.tools == ["file_reader", "data_analyzer"]


def test_router_chain_weather_to_calc(router):
    decision = router.route("Get the weather in Kolkata and convert the temperature to Fahrenheit.")
    assert decision.is_chain is True
    assert decision.tools == ["weather", "calculator"]


def test_router_chain_db_to_analyzer(router):
    decision = router.route("Find all Engineering employees from the database and calculate their average salary.")
    assert decision.is_chain is True
    assert decision.tools == ["database", "data_analyzer"]


def test_router_tools_schema_generation(router):
    schemas = router.get_tools_schema()
    assert len(schemas) >= 8
    names = [s["function"]["name"] for s in schemas]
    assert "calculator" in names
    assert "weather" in names
    assert "database" in names
    assert "file_reader" in names
