from fastapi import APIRouter
from app.api.v1 import auth
from app.api.v1 import shopping
api_router = APIRouter()
from app.api.v1 import meal_planning
# Auth routes
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

#Shopping List routes
api_router.include_router(shopping.router, prefix="/shopping_list", tags=["shopping_list"])

# Meal planning routes
api_router.include_router(
    meal_planning.router, 
    prefix="/meal-planning", 
    tags=["meal-planning"]
)
