from google.adk.agents import LlmAgent

from .config import settings

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


status_agent = LlmAgent(
    name="status_agent",
    model=settings.ai_model,
    instruction="""You help customers check the status of their existing orders. Follow this flow:

1. Ask the customer for their order ID (format: HF-XXXX).
2. Use the check_order_status tool to look it up.
3. Share the order status details with the customer.

After sharing the status, transfer back to the greeter_agent.""",
    description="Handles checking the status of existing meal kit orders.",
    tools=[check_order_status],
)
