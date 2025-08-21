from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.router import api_router

import warnings
from langchain_core._api import LangChainDeprecationWarning
warnings.filterwarnings("ignore", category=LangChainDeprecationWarning)

def create_app() -> FastAPI:
    app = FastAPI(title=settings.PROJECT_NAME)
    app.include_router(api_router, prefix=settings.API_V1_STR)
    
    # Initialize meal planning agent on startup
    @app.on_event("startup")
    async def startup_event():
        try:
            from app.core.meal_agent import get_meal_agent
            get_meal_agent()  # Initialize the agent
            print("Agent Started!")
        except Exception as e:
            print(f"Error initializing meal planning agent: {e}")

        # Initialize food analysis service
        try:
            from app.core.food_analysis import get_food_analysis_service
            get_food_analysis_service()
            print("Food Analysis Service Started!")
        except Exception as e:
            print(f"Error initializing food analysis service: {e}")
            
    return app

app = create_app()