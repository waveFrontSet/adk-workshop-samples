from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool

from .config import settings
from .nutrition import nutrition_expert
from .recipes import recipe_expert

# AgentTool wraps each expert so the root agent can call them like functions.
# Unlike sub-agents, each AgentTool call gets a fresh, isolated context —
# the expert does not see the parent's conversation history.
nutrition_tool = AgentTool(agent=nutrition_expert)
recipe_tool = AgentTool(agent=recipe_expert)

root_agent = LlmAgent(
    name="kitchen_assistant",
    model=settings.ai_model,
    instruction="""You are a friendly kitchen assistant for a meal kit service. \
You can help customers with two things:

1. **Nutrition questions** — use the nutrition_expert tool to look up \
nutritional information about ingredients.
2. **Recipe suggestions** — use the recipe_expert tool to find recipes \
based on ingredients the customer has or is interested in.

Decide which expert to consult based on the customer's question. You can \
consult both experts in a single conversation. Always present the expert's \
answer in a friendly, readable way.""",
    description="A kitchen assistant that consults nutrition and recipe experts.",
    tools=[nutrition_tool, recipe_tool],
)
