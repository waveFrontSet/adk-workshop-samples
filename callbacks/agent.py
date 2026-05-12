from typing import Optional

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.adk.tools import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types

MODEL = "gemini-2.5-flash"

# Phrases that should never reach the LLM. In production you would use a
# dedicated service such as LLM Guard or Model Armor rather than keyword
# matching.
BLOCKED_PHRASES = [
    "ignore previous instructions",
    "ignore all instructions",
    "system prompt",
    "drop table",
    "password",
    "credit card",
    "ssn",
]


# ---------------------------------------------------------------------------
# before_model_callback — input guardrail
# ---------------------------------------------------------------------------
def content_guardrail(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """Block requests containing potentially malicious or sensitive phrases."""
    last_user_text = ""
    if llm_request.contents:
        for content in reversed(llm_request.contents):
            if content.role == "user" and content.parts:
                last_user_text = content.parts[0].text or ""
                break

    text_lower = last_user_text.lower()
    for phrase in BLOCKED_PHRASES:
        if phrase in text_lower:
            print(f"[GUARDRAIL] Blocked phrase detected: '{phrase}'")
            return LlmResponse(
                content=types.Content(
                    role="model",
                    parts=[
                        types.Part(
                            text=(
                                "I'm sorry, but I can't process that request. "
                                "It contains content that has been flagged by "
                                "our safety filters."
                            )
                        )
                    ],
                )
            )

    return None  # proceed normally


# ---------------------------------------------------------------------------
# before_tool_callback — log tool invocations
# ---------------------------------------------------------------------------
def log_tool_call(
    tool: BaseTool, args: dict, tool_context: ToolContext
) -> Optional[dict]:
    """Log every tool call before execution."""
    print(f"[TOOL LOG] >>> Calling '{tool.name}' with args: {args}")
    return None  # don't modify anything


# ---------------------------------------------------------------------------
# after_tool_callback — log tool responses
# ---------------------------------------------------------------------------
def log_tool_response(
    tool: BaseTool, args: dict, tool_context: ToolContext, tool_response: dict
) -> Optional[dict]:
    """Log every tool response after execution."""
    print(f"[TOOL LOG] <<< '{tool.name}' returned: {tool_response}")
    return None  # don't modify anything


# ---------------------------------------------------------------------------
# Tool — same weather mock as simple_tool for continuity
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------
root_agent = LlmAgent(
    name="guarded_weather_agent",
    model=MODEL,
    instruction=(
        "You are a helpful weather assistant. "
        "Use the get_weather tool to answer questions about the weather in cities. "
        "If the tool returns an error, tell the user that weather data is only "
        "available for Berlin and Tokyo."
    ),
    description="A weather agent with guardrails and tool logging.",
    tools=[get_weather],
    before_model_callback=content_guardrail,
    before_tool_callback=log_tool_call,
    after_tool_callback=log_tool_response,
)
