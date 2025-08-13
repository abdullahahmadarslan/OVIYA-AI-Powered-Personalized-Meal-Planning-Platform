from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings


engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    future=True,
    echo=False  # set True for SQL debug logs
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

Base = declarative_base()

# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
        
