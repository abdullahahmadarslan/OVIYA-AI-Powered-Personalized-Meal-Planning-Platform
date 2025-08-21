from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Meals"
    API_V1_STR: str = "/api/v1"

    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    # Database
    SQLALCHEMY_DATABASE_URI: str
    
    # new for ingestion & vector db
    USDA_API_KEY: str
    OPENAI_API_KEY:str
    
    
    # Agent Configuration
    AGENT_MAX_ITERATIONS: int = 20
    AGENT_TEMPERATURE: float = 0.0
    AGENT_MODEL: str = "gpt-4o"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache
def get_settings():
    return Settings()

settings = get_settings()
