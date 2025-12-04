"""
Weather Service - Toy Service for Semantic Interface Fabric POC
===============================================================

This service demonstrates semantic capability expression instead of rigid APIs.
It exposes weather-related capabilities that can be discovered and negotiated with.
"""

import json
import random
from typing import Dict, Any, List
from semantic_ontology import Capability, DataSchema, DataType, ProtocolType


class WeatherService:
    """
    Toy weather service that exposes semantic capabilities.

    Instead of endpoints like:
    - GET /weather/current
    - POST /weather/alert

    It expresses what it can do semantically:
    - "I can provide current weather conditions"
    - "I can generate weather alerts"
    """

    def __init__(self, service_id: str = "weather_svc_001"):
        self.service_id = service_id
        self.capabilities = self._define_capabilities()

    def _define_capabilities(self) -> List[Capability]:
        """Define what this service can do semantically."""

        # Capability 1: Get current weather
        get_weather_cap = Capability(
            id=f"{self.service_id}_get_weather",
            name="get_weather",
            description="Retrieve current weather conditions for a location",
            domain="weather",
            inputs=[
                DataSchema(
                    type=DataType.STRING,
                    description="Location name or coordinates",
                    required=True,
                    constraints={"max_length": 100}
                )
            ],
            outputs=[
                DataSchema(
                    type=DataType.JSON,
                    description="Weather data including temperature, conditions, humidity",
                    required=True
                )
            ],
            constraints={
                "rate_limit": 100,  # requests per hour
                "cost": 0.01,  # per request
                "accuracy": 0.95  # 95% accuracy
            },
            protocols_supported=[ProtocolType.REQUEST_RESPONSE, ProtocolType.EVENT_DRIVEN],
            semantic_tags=["real_time", "current_conditions", "temperature", "humidity"]
        )

        # Capability 2: Generate weather alerts
        alert_cap = Capability(
            id=f"{self.service_id}_weather_alert",
            name="generate_weather_alert",
            description="Generate weather alerts for severe conditions",
            domain="weather",
            inputs=[
                DataSchema(
                    type=DataType.STRING,
                    description="Location to monitor",
                    required=True
                ),
                DataSchema(
                    type=DataType.STRING,
                    description="Alert threshold (e.g., 'severe', 'extreme')",
                    required=False,
                    constraints={"default": "severe"}
                )
            ],
            outputs=[
                DataSchema(
                    type=DataType.JSON,
                    description="Alert data with severity, message, and recommendations",
                    required=True
                )
            ],
            constraints={
                "rate_limit": 50,
                "cost": 0.05,
                "reliability": 0.99
            },
            protocols_supported=[ProtocolType.EVENT_DRIVEN, ProtocolType.REQUEST_RESPONSE],
            semantic_tags=["alerts", "severe_weather", "emergency", "forecast"]
        )

        # Capability 3: Weather forecast
        forecast_cap = Capability(
            id=f"{self.service_id}_forecast",
            name="get_forecast",
            description="Provide weather forecast for upcoming days",
            domain="weather",
            inputs=[
                DataSchema(
                    type=DataType.STRING,
                    description="Location for forecast",
                    required=True
                ),
                DataSchema(
                    type=DataType.INTEGER,
                    description="Number of days to forecast",
                    required=False,
                    constraints={"min": 1, "max": 7, "default": 3}
                )
            ],
            outputs=[
                DataSchema(
                    type=DataType.JSON,
                    description="Forecast data with daily predictions",
                    required=True
                )
            ],
            constraints={
                "rate_limit": 25,
                "cost": 0.03,
                "accuracy": 0.85
            },
            protocols_supported=[ProtocolType.REQUEST_RESPONSE],
            semantic_tags=["forecast", "prediction", "planning", "multi_day"]
        )

        return [get_weather_cap, alert_cap, forecast_cap]

    def get_capabilities(self) -> List[Capability]:
        """Return all capabilities this service offers."""
        return self.capabilities

    def execute_capability(self, capability_id: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a capability with given inputs.

        This simulates the actual service logic.
        In a real system, this would call weather APIs, databases, etc.
        """

        if capability_id == f"{self.service_id}_get_weather":
            return self._get_current_weather(inputs.get("location", "Unknown"))

        elif capability_id == f"{self.service_id}_weather_alert":
            return self._generate_alert(
                inputs.get("location", "Unknown"),
                inputs.get("threshold", "severe")
            )

        elif capability_id == f"{self.service_id}_forecast":
            return self._get_forecast(
                inputs.get("location", "Unknown"),
                inputs.get("days", 3)
            )

        else:
            raise ValueError(f"Unknown capability: {capability_id}")

    def _get_current_weather(self, location: str) -> Dict[str, Any]:
        """Simulate getting current weather data."""
        conditions = ["Sunny", "Cloudy", "Rainy", "Stormy", "Snowy"]
        return {
            "location": location,
            "temperature": round(random.uniform(10, 30), 1),
            "conditions": random.choice(conditions),
            "humidity": random.randint(30, 90),
            "wind_speed": round(random.uniform(0, 20), 1),
            "timestamp": "2024-12-04T10:00:00Z"
        }

    def _generate_alert(self, location: str, threshold: str) -> Dict[str, Any]:
        """Simulate generating weather alerts."""
        severity_levels = {
            "mild": {"level": 1, "message": "Minor weather changes expected"},
            "moderate": {"level": 2, "message": "Weather conditions may affect activities"},
            "severe": {"level": 3, "message": "Severe weather conditions detected"},
            "extreme": {"level": 4, "message": "Extreme weather emergency"}
        }

        alert_data = severity_levels.get(threshold, severity_levels["severe"])
        return {
            "location": location,
            "severity": alert_data["level"],
            "message": alert_data["message"],
            "recommendations": ["Stay indoors", "Prepare emergency kit", "Monitor updates"],
            "timestamp": "2024-12-04T10:00:00Z"
        }

    def _get_forecast(self, location: str, days: int) -> Dict[str, Any]:
        """Simulate getting weather forecast."""
        forecast = []
        conditions = ["Sunny", "Cloudy", "Rainy", "Partly Cloudy", "Overcast"]

        for i in range(days):
            forecast.append({
                "day": i + 1,
                "date": f"2024-12-0{i+5}T12:00:00Z",
                "high_temp": round(random.uniform(15, 35), 1),
                "low_temp": round(random.uniform(5, 20), 1),
                "conditions": random.choice(conditions),
                "precipitation_chance": random.randint(0, 100)
            })

        return {
            "location": location,
            "forecast": forecast,
            "generated_at": "2024-12-04T10:00:00Z"
        }


# Test the service
if __name__ == "__main__":
    service = WeatherService()
    print("Weather Service Capabilities:")
    for cap in service.get_capabilities():
        print(f"- {cap.name}: {cap.description}")

    # Test execution
    result = service.execute_capability(
        f"{service.service_id}_get_weather",
        {"location": "New York"}
    )
    print(f"\nWeather Result: {json.dumps(result, indent=2)}")