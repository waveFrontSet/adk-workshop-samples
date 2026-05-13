import random
import string

from google.adk.agents import LlmAgent

from .config import settings

MENU = """
Available Meal Kits:
1. Classic Cheeseburgers — juicy beef patties with cheddar, pickles, and special sauce
2. Creamy Mushroom Risotto — arborio rice with porcini mushrooms and parmesan
3. Thai Basil Chicken Stir-Fry — chicken thighs with Thai basil, chili, and jasmine rice
"""


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


order_agent = LlmAgent(
    name="order_agent",
    model=settings.ai_model,
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
