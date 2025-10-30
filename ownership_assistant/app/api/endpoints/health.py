"""Health check endpoint."""
from fastapi import APIRouter
from app.schemas.ownership import HealthCheck

router = APIRouter()


@router.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint."""
    return HealthCheck()

