from fastapi import APIRouter
from app.api.v1 import auth, usda  
api_router = APIRouter()

# Auth routes
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# USDA routes
api_router.include_router(usda.router, prefix="/usda", tags=["usda"])
