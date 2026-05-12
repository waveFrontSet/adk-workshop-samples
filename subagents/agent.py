import random
import string

from google.adk.agents import LlmAgent

MODEL = "gemini-2.5-flash"

MENU = """
Available Meal Kits:
1. Classic Cheeseburgers — juicy beef patties with cheddar, pickles, and special sauce
2. Creamy Mushroom Risotto — arborio rice with porcini mushrooms and parmesan
3. Thai Basil Chicken Stir-Fry — chicken thighs with Thai basil, chili, and jasmine rice
"""

# Mock database of existing orders
ORDER_DB = {
    "HF-1001": {
        "status": "shipped",
        "meal": "Classic Cheeseburgers",
        "servings": 4,
        "delivery_date": "2026-05-14",
        "tracking": "DHL-9876543",
    },
    "HF-1002": {
        "status": "preparing",
        "meal": "Creamy Mushroom Risotto",
        "servings": 2,
        "delivery_date": "2026-05-15",
        "tracking": None,
    },
    "HF-1003": {
        "status": "delivered",
        "meal": "Thai Basil Chicken Stir-Fry",
        "servings": 2,
        "delivery_date": "2026-05-10",
        "tracking": "DHL-1234567",
    },
}


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------
def place_order(meal: str, servings: int, delivery_date: str) -> dict:
    """Places a new meal kit order.

    Args:
        meal: The name of the meal kit to order.
        servings: Number of servings (2 or 4).
        delivery_date: Preferred delivery date in YYYY-MM-DD format.
    """
    order_id = "HF-" + "".join(random.choices(string.digits, k=4))
    return {
        "status": "success",
        "order_id": order_id,
        "meal": meal,
        "servings": servings,
        "delivery_date": delivery_date,
        "message": f"Order {order_id} confirmed! Your {meal} for {servings} servings will be delivered on {delivery_date}.",
    }


def check_order_status(order_id: str) -> dict:
    """Checks the status of an existing order.

    Args:
        order_id: The order ID, e.g. "HF-1001".
    """
    order = ORDER_DB.get(order_id.upper())
    if order:
        return {"status": "success", "order_id": order_id, **order}
    return {
        "status": "error",
        "message": f"No order found with ID '{order_id}'. Valid example IDs: HF-1001, HF-1002, HF-1003.",
    }


# ---------------------------------------------------------------------------
# Sub-agents
# ---------------------------------------------------------------------------
order_agent = LlmAgent(
    name="order_agent",
    model=MODEL,
    instruction=f"""You help customers place new meal kit orders. Follow this flow:

1. Show the customer the menu and ask which meal kit they'd like:
{MENU}
2. Ask how many servings they want (2 or 4).
3. Ask for their preferred delivery date.
4. Confirm the details and use the place_order tool to submit the order.
5. Share the order confirmation with the customer.

After the order is placed, transfer back to the greeter_agent.""",
    description="Handles placing new meal kit orders. Guides the customer through meal selection, servings, and delivery date.",
    tools=[place_order],
)

status_agent = LlmAgent(
    name="status_agent",
    model=MODEL,
    instruction="""You help customers check the status of their existing orders. Follow this flow:

1. Ask the customer for their order ID (format: HF-XXXX).
2. Use the check_order_status tool to look it up.
3. Share the order status details with the customer.

After sharing the status, transfer back to the greeter_agent.""",
    description="Handles checking the status of existing meal kit orders.",
    tools=[check_order_status],
)

# ---------------------------------------------------------------------------
# Root / coordinator agent
# ---------------------------------------------------------------------------
root_agent = LlmAgent(
    name="greeter_agent",
    model=MODEL,
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
