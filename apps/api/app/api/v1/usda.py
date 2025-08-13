from fastapi import APIRouter
from .usda_service import run_meal_planner

router = APIRouter()

@router.post("/meal-plan")
def get_meal_plan(user_input: str):
    return {"response": run_meal_planner(user_input)}
