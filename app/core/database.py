# app/core/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings


# Database URL from .env
DATABASE_URL = settings.DATABASE_URL




# SQLAlchemy Engine
engine = create_engine(
    DATABASE_URL
)

# Database Session Factory
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)


# Base class for all models
Base = declarative_base()


# Dependency Injection for FastAPI
def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()