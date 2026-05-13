from google.adk.agents import LlmAgent

from .config import settings

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
    model=settings.ai_model,
    instruction=(
        "You are a recipe expert. Use the search_recipes tool to suggest "
        "recipes based on the ingredients the user mentions. Present each "
        "recipe with its name, a short description, and cooking time."
    ),
    description="Suggests recipes based on available ingredients.",
    tools=[search_recipes],
)
