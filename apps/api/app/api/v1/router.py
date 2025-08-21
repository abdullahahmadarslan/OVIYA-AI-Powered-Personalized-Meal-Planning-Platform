from fastapi import APIRouter
from app.api.v1 import auth
from app.api.v1 import meal_planning
api_router = APIRouter()

# Auth routes
api_router.include_router(auth.router,
                          prefix="/auth", 
                          tags=["auth"])

# Meal planning routes
api_router.include_router(
    meal_planning.router, 
    prefix="/meal-planning", 
    tags=["meal-planning"]
)