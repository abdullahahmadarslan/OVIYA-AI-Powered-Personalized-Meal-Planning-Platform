import openai
import json
from typing import Dict, Any
from app.core.config import settings

from app.core.recipe_utils import (
    create_recipe_prompt,
    parse_recipe_response,
    create_error_response,
)

# Initialize OpenAI client
client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)


def generate_recipe(meal_name: str, model: str = "gpt-4o") -> Dict[str, Any]:
    """
    Generate recipe data for a given meal name.

    Args:
        meal_name (str): Name of the meal to generate recipe for
        model (str): OpenAI model to use

    Returns:
        Dict containing ingredients list and instructions with headings
    """
    try:
        # Create a structured prompt for consistent output
        prompt = create_recipe_prompt(meal_name)

        # Call OpenAI API
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional chef assistant. Provide accurate, detailed recipes in the requested format.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=1000,
        )

        # Parse the response
        recipe_text = response.choices[0].message.content
        parsed_recipe = parse_recipe_response(recipe_text, meal_name)

        return parsed_recipe

    except Exception as e:
        return create_error_response(str(e), meal_name)
