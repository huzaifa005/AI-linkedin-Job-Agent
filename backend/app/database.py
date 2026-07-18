"""
Database connection and session management using SQLModel.
"""

import os
from sqlmodel import SQLModel, Session, create_engine
from app.config import settings


# Ensure the data directory exists for SQLite
db_url = settings.database_url
if db_url.startswith("sqlite"):
    db_path = db_url.replace("sqlite:///", "")
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

engine = create_engine(
    db_url,
    echo=False,
    connect_args={"check_same_thread": False} if db_url.startswith("sqlite") else {},
)


def create_db_and_tables():
    """Create all SQLModel tables if they don't exist."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Dependency that yields a database session."""
    with Session(engine) as session:
        yield session
