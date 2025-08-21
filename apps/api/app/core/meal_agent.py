from langchain.agents import initialize_agent, Tool
from langchain.prompts import MessagesPlaceholder
from langchain.schema import SystemMessage
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
import requests
import os
from typing import Dict, Any, List
from app.core.config import settings

class MealPlanningAgent:
    def __init__(self, openai_api_key: str, usda_api_key: str):
        self.openai_api_key = openai_api_key
        self.usda_api_key = usda_api_key
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=openai_api_key)
        self.agent = self._initialize_agent()
    
    def search_food(self, query: str, page_size: int = 2, page_number: int = 1) -> List[Dict]:
        """Search USDA database for foods"""
        url = "https://api.nal.usda.gov/fdc/v1/foods/search"
        params = {
            "api_key": self.usda_api_key,
            "query": query,
            "pageSize": page_size,
            "pageNumber": page_number
        }
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                results = []
                for food in data.get("foods", []):
                    results.append({
                        "description": food['description'],
                        "fdcId": food['fdcId'],
                        "foodCategory": food.get('foodCategory')
                    })
                return results
            else:
                return []
        except Exception as e:
            return []

    def get_nutrients(self, fdc_id: int) -> Dict[str, Any]:
        """Get nutrient details for a given food using its fdcId"""
        url = f"https://api.nal.usda.gov/fdc/v1/food/{fdc_id}"
        params = {"api_key": self.usda_api_key}
        
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                food_details = response.json()
                nutrients_list = []
                for nutrient in food_details.get("foodNutrients", []):
                    name = nutrient.get("nutrient", {}).get("name")
                    amount = nutrient.get("amount")
                    unit = nutrient.get("nutrient", {}).get("unitName")
                    if name and amount is not None:
                        nutrients_list.append({
                            "name": name,
                            "amount": amount,
                            "unit": unit
                        })
                return {
                    "description": food_details.get("description"),
                    "nutrients": nutrients_list
                }
            else:
                return {"error": f"Failed to fetch nutrients for FDC ID: {fdc_id}"}
        except Exception as e:
            return {"error": str(e)}

    def _get_system_prompt(self) -> str:
        """Load system prompt from the document you provided"""
        return """
ROLE
You are a Meal Planning Assistant that designs personalized meal plans based on a user's height, weight, BMI, dietary preferences, likes, dislikes, and fitness goals. You have access to tools to search foods and fetch nutrient data.

MISSION
Suggest the best Breakfast, Lunch, Dinner, and Snacks, plan, using strict tool-verified nutrient analysis. For each meal, ONLY THE SELECTED ONES IN THE END AND NOT IN BETWEEN STEPS, : list items, portion guidance, and macro breakdown (calories, protein g, carbs g, fat g; include sugar and fiber when available)

CRITICAL OUTPUT RULES:
- During tool usage: Output ONLY pure valid JSON syntax
- For Final Answer: Output ONLY A a proper formatted breakdown of the meal of breakfast, lunch, dinner and snacks separately and in a JSON format which can be converted to python dictionary.
- Never mix JSON and natural language in the same response
- For each meal, ONLY THE SELECTED ONES IN THE END AND NOT IN BETWEEN STEPS, : list items, portion guidance, and macro breakdown (calories, protein g, carbs g, fat g; include sugar and fiber when available)

WORKFLOW RULES

1. Understand User Profile:
   Parse height, weight, BMI, dietary type (vegan/vegetarian/etc.), likes, dislikes, and goal (weight loss/muscle gain/maintenance).
   If a detail is missing, estimate reasonable defaults to proceed (e.g., calorie targets from Mifflin-St Jeor approximations or standard splits).

2. Meal Brainstorming:
   For the current meal type, brainstorm at least 2 candidate meals that use liked foods and avoid disliked foods and respect restrictions.
   Aim for macro distribution across the day; a simple default split is: Breakfast ~25% calories, Lunch ~35%, Dinner ~30%, Snacks ~10%.

3. Nutrient Validation Process (per candidate meal):
   For each item in the meal, in order:
   a) Call tool "search_food" with the food name.
   b) Choose the most relevant match from the returned list (based on description match and plausible category).
   c) Call tool "get_nutrients" with the chosen FDC ID.
   Sum the nutrients for the meal using only tool outputs; never guess nutrient values.

4. Check the meal against goals and constraints:
   - Calories fit target window for this meal.
   - Macros (protein, carbs, fat) move the day toward the user's goal (e.g., higher protein and lower sugar for weight loss).
   - Respect dietary rules (e.g., vegan compliance), and consider sugar/sodium/fiber as appropriate.

5. Decision Making:
   If a candidate meets criteria, mark it as current best and stop evaluating further candidates for this meal.
   If it fails, evaluate the next candidate. If all fail, brainstorm new candidates and repeat.

6. Meal Progression:
   Finish one meal type completely (best candidate selected) before starting the next.
   Usual order: Breakfast -> Lunch -> Dinner -> Snacks

FINAL OUTPUT FORMAT
When all meal types(lunch, breakfast, dinner and snacks) requested are finalized, respond with Final Answer containing:
- A clearly formatted plan listing the selected best meal for each category.
- For each meal: list items, portion guidance, and macro breakdown (calories, protein g, carbs g, fat g; include sugar and fiber when available)
- Make sure you provide lunch, breakfast, dinner and snacks details. Don't give the final response before that.

TOOL USAGE INSTRUCTIONS
- Use "search_food" only to look up candidate items by name.
- Always follow with "get_nutrients" for the chosen FDC ID to verify actual nutrient values.
- Never invent FDC IDs, never fabricate nutrients, and do not skip validation for any item.
- You may call tools multiple times until a best-fitting meal is found for the current meal type.

GUARDRAILS
- During tool calls: Output ONLY JSON format
- If a tool returns multiple plausible results, prefer the closest name match and appropriate category.
- Make sure you provide lunch, breakfast, dinner and snacks details. Don't give the final response before that.
"""

    def _initialize_agent(self):
        """Initialize the LangChain agent with tools and memory"""
        tools = [
            Tool(
                name="search_food",
                func=lambda q: self.search_food(q),
                description="Search USDA database for foods. Input is a food name (string). Output is a list of matching foods with description, fdcId, and category."
            ),
            Tool(
                name="get_nutrients",
                func=lambda fdc_id: self.get_nutrients(int(fdc_id)),
                description="Get nutrient details for a given food using its fdcId."
            )
        ]
        
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        
        agent = initialize_agent(
            tools,
            self.llm,
            agent_type="chat-conversational-react-description",
            handle_parsing_errors=True,
            verbose=True,
            memory=memory,
            agent_kwargs={
                "system_message": SystemMessage(content=self._get_system_prompt()),
                "extra_prompt_messages": [
                    MessagesPlaceholder(variable_name="chat_history")
                ]
            },
            max_iterations=20,
            early_stopping_method="generate"
        )
        return agent

    def generate_meal_plan(self, user_input: str) -> Dict[str, Any]:
        """Generate meal plan based on user input"""
        try:
            result = self.agent.run(user_input)
            return {
                "success": True,
                "meal_plan": result,
                "message": "Meal plan generated successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "meal_plan": None,
                "message": f"Error generating meal plan: {str(e)}"
            }

# Singleton instance 
meal_agent: MealPlanningAgent = None

def get_meal_agent() -> MealPlanningAgent:
    """Get the meal planning agent instance"""
    global meal_agent
    if meal_agent is None:
        # These should be loaded from environment variables or config
        openai_key = settings.OPENAI_API_KEY
        usda_key =  settings.USDA_API_KEY
        meal_agent = MealPlanningAgent(openai_key, usda_key)
    return meal_agent
