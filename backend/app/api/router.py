"""
Main API router — aggregates all endpoint modules under /api prefix.
"""

from fastapi import APIRouter
from app.api.health import router as health_router
from app.api.cv import router as cv_router
from app.api.jobs import router as jobs_router
from app.api.documents import router as documents_router
from app.api.scraper import router as scraper_router

api_router = APIRouter(prefix="/api")

api_router.include_router(health_router)
api_router.include_router(cv_router)
api_router.include_router(jobs_router)
api_router.include_router(documents_router)
api_router.include_router(scraper_router)
