from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional

from app.core.meal_agent import get_meal_agent, MealPlanningAgent

router = APIRouter()

class MealPlanRequest(BaseModel):
    user_profile: str
    dietary_preferences: Optional[str] = None
    additional_requirements: Optional[str] = None

class MealPlanResponse(BaseModel):
    success: bool
    meal_plan: Optional[str] = None
    message: str

@router.post("/generate", response_model=MealPlanResponse)
async def generate_meal_plan(
    request: MealPlanRequest,
    agent: MealPlanningAgent = Depends(get_meal_agent)
):
    """
    Generate a personalized meal plan based on user profile and preferences using agentic workflow.
    
    - **user_profile**: User's physical stats and goals (height, weight, dietary type, goals, etc.)
    - **dietary_preferences**: Optional additional dietary preferences
    - **additional_requirements**: Any additional requirements or constraints
    """
    try:
        # Construct the full user input
        user_input = request.user_profile
        if request.dietary_preferences:
            user_input += f" {request.dietary_preferences}"
        if request.additional_requirements:
            user_input += f" {request.additional_requirements}"
            
        # Add the standard request format
        user_input += " Suggest me breakfast, lunch, dinner and snacks now. For each meal: list items, portion guidance, and macro breakdown (calories, protein g, carbs g, fat g; include sugar and fiber when available), don't reason way too much."
        
        result = agent.generate_meal_plan(user_input)
        
        return MealPlanResponse(
            success=result["success"],
            meal_plan=result["meal_plan"],
            message=result["message"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
