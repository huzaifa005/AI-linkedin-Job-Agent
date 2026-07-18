"""
Application configuration loaded from environment variables.
Uses pydantic-settings for type-safe, validated configuration.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from .env file or environment variables."""

    # --- Groq LLM ---
    groq_api_key: str
    groq_model: str = "llama-3.3-70b-versatile"
    groq_match_temperature: float = 0.1
    groq_match_max_tokens: int = 150
    groq_assets_temperature: float = 0.2
    groq_assets_max_tokens: int = 3000

    # --- Database ---
    database_url: str = "sqlite:///./data/app.db"

    # --- File Storage ---
    storage_path: str = "./storage/outputs"

    # --- API / CORS ---
    cors_origins: List[str] = ["http://localhost:3000"]
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # --- Business Logic ---
    match_threshold: int = 6

    # --- App Metadata ---
    app_name: str = "AI Job Match Agent"
    app_version: str = "1.0.0"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


# Singleton instance
settings = Settings()
