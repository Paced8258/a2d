"""Ownership-related schemas."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# Request schemas
class OwnershipQuery(BaseModel):
    """Request to query ownership."""
    query: str = Field(..., description="Natural language query about ownership")
    context: Optional[str] = Field(None, description="Additional context")


class IngestData(BaseModel):
    """Request to ingest ownership data."""
    source: str = Field(..., description="Data source (e.g., 'product_matrix', 'notion')")
    data: list = Field(..., description="List of ownership data records")


# Response schemas
class OwnerInfo(BaseModel):
    """Owner information."""
    id: int
    name: str
    email: str
    team: Optional[str] = None
    role: Optional[str] = None


class OwnershipResolution(BaseModel):
    """Ownership resolution result."""
    query: str
    owner: OwnerInfo
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    supporting_context: Optional[str] = None
    area_name: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class HealthCheck(BaseModel):
    """Health check response."""
    status: str = "ok"
    version: str = "0.1.0"

