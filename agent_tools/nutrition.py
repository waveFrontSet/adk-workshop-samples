from google.adk.agents import LlmAgent

from .config import settings

NUTRITION_DB = {
    "chicken breast": {
        "calories": 165,
        "protein": 31,
        "carbs": 0,
        "fat": 3.6,
        "per": "100g",
    },
    "salmon": {"calories": 208, "protein": 20, "carbs": 0, "fat": 13, "per": "100g"},
    "rice": {"calories": 130, "protein": 2.7, "carbs": 28, "fat": 0.3, "per": "100g"},
    "broccoli": {"calories": 34, "protein": 2.8, "carbs": 7, "fat": 0.4, "per": "100g"},
    "egg": {"calories": 155, "protein": 13, "carbs": 1.1, "fat": 11, "per": "100g"},
    "pasta": {"calories": 131, "protein": 5, "carbs": 25, "fat": 1.1, "per": "100g"},
    "avocado": {"calories": 160, "protein": 2, "carbs": 9, "fat": 15, "per": "100g"},
    "tofu": {"calories": 76, "protein": 8, "carbs": 1.9, "fat": 4.8, "per": "100g"},
}


def lookup_nutrition(ingredient: str) -> dict:
    """Looks up nutritional information for a common ingredient.

    Args:
        ingredient: The ingredient name, e.g. "chicken breast" or "rice".
    """
    data = NUTRITION_DB.get(ingredient.lower())
    if data:
        return {"status": "success", "ingredient": ingredient, **data}
    available = ", ".join(sorted(NUTRITION_DB.keys()))
    return {
        "status": "error",
        "message": f"No data for '{ingredient}'. Available: {available}.",
    }


nutrition_expert = LlmAgent(
    name="nutrition_expert",
    model=settings.ai_model,
    instruction=(
        "You are a nutrition expert. Use the lookup_nutrition tool to answer "
        "questions about the nutritional content of ingredients. Be precise "
        "and concise. Always mention the per-serving basis (per 100g)."
    ),
    description="Answers nutrition questions about ingredients — calories, protein, carbs, fat.",
    tools=[lookup_nutrition],
)
