"""Unit tests for the Weather tool."""

import pytest
from tools.weather import WeatherTool


@pytest.fixture
def weather_tool():
    return WeatherTool()


def test_weather_known_city_kolkata(weather_tool):
    res = weather_tool.execute(location="Kolkata")
    assert res["success"] is True
    data = res["data"]
    assert data["location"] == "Kolkata"
    assert data["temperature"] == 28.5
    assert "condition" in data
    assert "humidity" in data
    assert "wind_speed" in data
    assert "source" in data


def test_weather_unknown_city_mock_generator(weather_tool):
    res = weather_tool.execute(location="Reykjavik")
    assert res["success"] is True
    data = res["data"]
    assert data["location"] == "Reykjavik"
    assert isinstance(data["temperature"], (int, float))


def test_weather_empty_location(weather_tool):
    res = weather_tool.execute(location="")
    assert res["success"] is False
    assert res["error"]["type"] == "ValidationError"


def test_weather_simulated_api_failure(weather_tool):
    res = weather_tool.execute(location="Delhi", simulate_error="api_failure")
    assert res["success"] is False
    assert res["error"]["type"] == "ExternalServiceError"


def test_weather_simulated_timeout(weather_tool):
    res = weather_tool.execute(location="Delhi", simulate_error="timeout")
    assert res["success"] is False
    assert res["error"]["type"] == "ExternalServiceError"
