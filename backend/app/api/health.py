"""
Health check endpoint.
"""

from fastapi import APIRouter
from app.config import settings
from app.schemas.schemas import HealthResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Returns the application status, version, and name.",
)
async def health_check():
    return HealthResponse(
        status="ok",
        version=settings.app_version,
        app_name=settings.app_name,
    )
