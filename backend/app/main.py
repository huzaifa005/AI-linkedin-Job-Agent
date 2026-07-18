"""
AI Job Match Agent — FastAPI Application Entry Point

A micro SaaS that evaluates LinkedIn job listings against your CV using AI,
then generates tailored CVs and cover letters for matching positions.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import create_db_and_tables
from app.api.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — runs on startup and shutdown."""
    # Startup: create database tables
    create_db_and_tables()
    yield
    # Shutdown: cleanup if needed


app = FastAPI(
    title=settings.app_name,
    description=(
        "AI-powered job matching agent that evaluates LinkedIn job listings "
        "against your CV, scores the fit, and generates tailored CVs and "
        "cover letters for matching positions."
    ),
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all API routes
app.include_router(api_router)


@app.get("/", include_in_schema=False)
async def root():
    """Root redirect to API documentation."""
    return {
        "message": f"Welcome to {settings.app_name}",
        "docs": "/docs",
        "api": "/api/health",
    }
