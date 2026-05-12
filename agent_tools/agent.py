from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool

MODEL = "gemini-2.5-flash"


# ---------------------------------------------------------------------------
# Nutrition expert — tools & agent
# ---------------------------------------------------------------------------
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
    model=MODEL,
    instruction=(
        "You are a nutrition expert. Use the lookup_nutrition tool to answer "
        "questions about the nutritional content of ingredients. Be precise "
        "and concise. Always mention the per-serving basis (per 100g)."
    ),
    description="Answers nutrition questions about ingredients — calories, protein, carbs, fat.",
    tools=[lookup_nutrition],
)


# ---------------------------------------------------------------------------
# Recipe expert — tools & agent
# ---------------------------------------------------------------------------
RECIPE_DB = {
    "chicken": [
        {
            "name": "Lemon Herb Chicken",
            "description": "Pan-seared chicken breast with lemon, thyme, and roasted vegetables.",
            "time": "30 min",
        },
        {
            "name": "Chicken Teriyaki Bowl",
            "description": "Glazed chicken thighs over steamed rice with pickled cucumber.",
            "time": "25 min",
        },
    ],
    "salmon": [
        {
            "name": "Honey Garlic Salmon",
            "description": "Oven-baked salmon with a honey-garlic glaze and asparagus.",
            "time": "25 min",
        },
        {
            "name": "Salmon Poke Bowl",
            "description": "Fresh salmon cubes with rice, avocado, edamame, and soy dressing.",
            "time": "15 min",
        },
    ],
    "pasta": [
        {
            "name": "Creamy Tomato Pasta",
            "description": "Penne in a sun-dried tomato cream sauce with fresh basil.",
            "time": "20 min",
        },
        {
            "name": "Pasta Primavera",
            "description": "Spaghetti with sautéed seasonal vegetables and parmesan.",
            "time": "25 min",
        },
    ],
    "tofu": [
        {
            "name": "Crispy Tofu Stir-Fry",
            "description": "Crispy pan-fried tofu with broccoli, peppers, and teriyaki sauce.",
            "time": "20 min",
        },
        {
            "name": "Tofu Scramble",
            "description": "Seasoned crumbled tofu with spinach, tomatoes, and spices.",
            "time": "15 min",
        },
    ],
}


def search_recipes(ingredients: str) -> dict:
    """Searches for recipe suggestions based on a main ingredient.

    Args:
        ingredients: The main ingredient to search recipes for, e.g. "chicken" or "salmon".
    """
    recipes = RECIPE_DB.get(ingredients.lower())
    if recipes:
        return {"status": "success", "ingredient": ingredients, "recipes": recipes}
    available = ", ".join(sorted(RECIPE_DB.keys()))
    return {
        "status": "error",
        "message": f"No recipes found for '{ingredients}'. Try: {available}.",
    }


recipe_expert = LlmAgent(
    name="recipe_expert",
    model=MODEL,
    instruction=(
        "You are a recipe expert. Use the search_recipes tool to suggest "
        "recipes based on the ingredients the user mentions. Present each "
        "recipe with its name, a short description, and cooking time."
    ),
    description="Suggests recipes based on available ingredients.",
    tools=[search_recipes],
)


# ---------------------------------------------------------------------------
# Root agent — uses experts as AgentTools
# ---------------------------------------------------------------------------
# AgentTool wraps each expert so the root agent can call them like functions.
# Unlike sub-agents, each AgentTool call gets a fresh, isolated context —
# the expert does not see the parent's conversation history.
nutrition_tool = AgentTool(agent=nutrition_expert)
recipe_tool = AgentTool(agent=recipe_expert)

root_agent = LlmAgent(
    name="kitchen_assistant",
    model=MODEL,
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
