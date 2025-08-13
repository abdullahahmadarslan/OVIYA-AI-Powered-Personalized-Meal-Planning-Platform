# app/api/v1/usda_service.py
import os
import requests
from langchain.agents import initialize_agent, Tool
from langchain.memory import ConversationBufferMemory
from langchain.prompts import MessagesPlaceholder
from langchain_openai import OpenAI

API_KEY = os.getenv("USDA_API_KEY")

def search_food(query: str, page_size=2, page_number=1):
    url = "https://api.nal.usda.gov/fdc/v1/foods/search"
    params = {
        "api_key": API_KEY,
        "query": query,
        "pageSize": page_size,
        "pageNumber": page_number
    }
    resp = requests.get(url, params=params)
    if resp.status_code == 200:
        foods = resp.json().get("foods", [])
        return [
            {
                "description": f["description"],
                "fdcId": f["fdcId"],
                "foodCategory": f.get("foodCategory")
            }
            for f in foods
        ]
    return {"error": f"{resp.status_code}: {resp.text}"}

def get_nutrients(fdc_id: int):
    url = f"https://api.nal.usda.gov/fdc/v1/food/{fdc_id}"
    params = {"api_key": API_KEY}
    resp = requests.get(url, params=params)
    if resp.status_code == 200:
        details = resp.json()
        return {
            "description": details.get("description"),
            "nutrients": [
                {
                    "name": n.get("nutrient", {}).get("name"),
                    "amount": n.get("amount"),
                    "unit": n.get("nutrient", {}).get("unitName")
                }
                for n in details.get("foodNutrients", [])
                if n.get("nutrient", {}).get("name") and n.get("amount") is not None
            ]
        }
    return {"error": f"{resp.status_code}: {resp.text}"}

system_prompt = """...your big system prompt here..."""

# Prepare agent
llm = OpenAI()
tools = [
    Tool(
        name="search_food",
        func=lambda q: search_food(q),
        description="Search USDA database..."
    ),
    Tool(
        name="get_nutrients",
        func=lambda fdc_id: get_nutrients(int(fdc_id)),
        description="Get nutrient details..."
    )
]
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
agent = initialize_agent(
    tools,
    llm,
    agent="chat-conversational-react-description",
    verbose=True,
    memory=memory,
    agent_kwargs={
        "system_message": system_prompt,
        "extra_prompt_messages": [MessagesPlaceholder(variable_name="chat_history")]
    }
)

def run_meal_planner(user_input: str):
    return agent.run(user_input)
