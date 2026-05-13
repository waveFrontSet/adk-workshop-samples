from google.adk.agents import LlmAgent

from .config import settings


def get_weather(city: str) -> dict:
    """Retrieves the current weather for a given city.

    Args:
        city: The city name, e.g. "Berlin" or "Tokyo".
    """
    weather_data = {
        "berlin": {
            "status": "success",
            "city": "Berlin",
            "temperature": 18,
            "condition": "Partly cloudy",
            "unit": "Celsius",
        },
        "tokyo": {
            "status": "success",
            "city": "Tokyo",
            "temperature": 28,
            "condition": "Sunny",
            "unit": "Celsius",
        },
    }
    result = weather_data.get(city.lower())
    if result:
        return result
    return {"status": "error", "message": f"Weather data not available for '{city}'."}


root_agent = LlmAgent(
    name="weather_agent",
    model=settings.ai_model,
    instruction=(
        "You are a helpful weather assistant. "
        "Use the get_weather tool to answer questions about the weather in cities. "
        "If the tool returns an error, tell the user that weather data is only "
        "available for Berlin and Tokyo."
    ),
    description="An agent that provides current weather information.",
    tools=[get_weather],
)
