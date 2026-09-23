"""Weather Tool: Location weather reporter supporting live API queries with safe mock fallback."""

from __future__ import annotations
import os
import requests
from typing import Any, Dict, Optional
from core.errors import ExternalServiceError, ValidationError
from tools.base import BaseTool

MOCK_CITY_WEATHER: Dict[str, Dict[str, Any]] = {
    "kolkata": {
        "location": "Kolkata",
        "temperature": 28.5,
        "condition": "Partly Cloudy",
        "humidity": "72%",
        "wind_speed": "12 km/h",
    },
    "mumbai": {
        "location": "Mumbai",
        "temperature": 30.0,
        "condition": "Humid / Haze",
        "humidity": "80%",
        "wind_speed": "18 km/h",
    },
    "delhi": {
        "location": "Delhi",
        "temperature": 32.0,
        "condition": "Sunny",
        "humidity": "45%",
        "wind_speed": "10 km/h",
    },
    "bengaluru": {
        "location": "Bengaluru",
        "temperature": 24.0,
        "condition": "Pleasant / Breezy",
        "humidity": "58%",
        "wind_speed": "15 km/h",
    },
    "bangalore": {
        "location": "Bengaluru",
        "temperature": 24.0,
        "condition": "Pleasant / Breezy",
        "humidity": "58%",
        "wind_speed": "15 km/h",
    },
    "london": {
        "location": "London",
        "temperature": 16.0,
        "condition": "Light Rain",
        "humidity": "78%",
        "wind_speed": "20 km/h",
    },
    "new york": {
        "location": "New York",
        "temperature": 19.0,
        "condition": "Clear Sky",
        "humidity": "52%",
        "wind_speed": "14 km/h",
    },
    "tokyo": {
        "location": "Tokyo",
        "temperature": 21.5,
        "condition": "Mild / Clear",
        "humidity": "60%",
        "wind_speed": "11 km/h",
    },
}


class WeatherTool(BaseTool):
    """Fetches real-time or simulated meteorological reports for any city or coordinate."""

    name = "weather"
    description = (
        "Get current weather data for a city/location. "
        "Returns temperature (°C), condition, humidity, wind speed, and data source."
    )
    parameters = {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "City or geographical location name (e.g. 'Kolkata', 'London').",
            }
        },
        "required": ["location"],
    }
    examples = [
        {"location": "Kolkata"},
        {"location": "London"},
    ]

    def _query_live_api(self, location: str) -> Dict[str, Any]:
        """Fetch current weather from OpenWeatherMap API using WEATHER_API_KEY."""
        api_key = os.getenv("WEATHER_API_KEY")
        url = f"https://api.openweathermap.org/data/2.5/weather"
        params = {"q": location, "appid": api_key, "units": "metric"}

        try:
            resp = requests.get(url, params=params, timeout=5.0)
            if resp.status_code == 404:
                raise ValidationError(f"City '{location}' not found in weather registry.", tool_name=self.name)
            if resp.status_code != 200:
                raise ExternalServiceError(
                    f"Weather API error HTTP {resp.status_code}: {resp.text[:200]}",
                    tool_name=self.name,
                )
            data = resp.json()
            return {
                "location": data.get("name", location),
                "temperature": round(data["main"]["temp"], 1),
                "condition": data["weather"][0]["description"].title() if data.get("weather") else "Clear",
                "humidity": f"{data['main']['humidity']}%",
                "wind_speed": f"{round(data['wind']['speed'] * 3.6, 1)} km/h",
                "source": "live (OpenWeatherMap)",
            }
        except requests.Timeout:
            raise ExternalServiceError("Weather service request timed out.", tool_name=self.name)
        except requests.RequestException as e:
            raise ExternalServiceError(f"Weather service connection error: {str(e)}", tool_name=self.name)

    def _query_mock(self, location: str) -> Dict[str, Any]:
        """Provide realistic meteorological readings from offline index."""
        loc_key = location.lower().strip()
        if loc_key in MOCK_CITY_WEATHER:
            base = dict(MOCK_CITY_WEATHER[loc_key])
            base["source"] = "mock (offline mode - set WEATHER_API_KEY for live readings)"
            return base

        # Generate deterministic reading for unknown cities
        char_sum = sum(ord(c) for c in loc_key)
        simulated_temp = 15.0 + (char_sum % 18)
        simulated_humidity = 40 + (char_sum % 45)
        simulated_wind = 8 + (char_sum % 16)
        conditions = ["Sunny", "Partly Cloudy", "Breezy", "Overcast", "Light Showers"]
        cond = conditions[char_sum % len(conditions)]

        return {
            "location": location.title(),
            "temperature": round(float(simulated_temp), 1),
            "condition": cond,
            "humidity": f"{simulated_humidity}%",
            "wind_speed": f"{simulated_wind} km/h",
            "source": "mock (offline mode - set WEATHER_API_KEY for live readings)",
        }

    def run(self, location: str, simulate_error: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Fetch weather data for the specified location."""
        if not location or not location.strip():
            raise ValidationError("Location parameter cannot be empty.", tool_name=self.name)

        clean_loc = location.strip()

        if simulate_error == "timeout":
            raise ExternalServiceError("Weather service timed out after 5.0 seconds.", tool_name=self.name)
        if simulate_error == "api_failure":
            raise ExternalServiceError("Weather API service unavailable (HTTP 503).", tool_name=self.name)

        api_key = os.getenv("WEATHER_API_KEY")
        if api_key:
            return self._query_live_api(clean_loc)
        return self._query_mock(clean_loc)
