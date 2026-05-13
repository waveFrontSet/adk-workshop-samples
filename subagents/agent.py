from google.adk.agents import LlmAgent

from .config import settings
from .ordering import order_agent
from .status import status_agent

root_agent = LlmAgent(
    name="greeter_agent",
    model=settings.ai_model,
    instruction="""You are the front-desk assistant for a meal kit delivery service. \
Greet the customer warmly and determine what they need help with.

- If they want to place a new order, transfer to order_agent.
- If they want to check an existing order's status, transfer to status_agent.
- For anything else, answer to the best of your ability or let them know \
you can help with ordering and order status.

Be friendly and concise.""",
    description="Main greeter and router for the meal kit delivery customer service.",
    sub_agents=[order_agent, status_agent],
)
