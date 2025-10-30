"""Ownership models for product features and areas."""
from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


class ProductArea(SQLModel, table=True):
    """Product area or feature."""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    ownerships: List["Ownership"] = Relationship(back_populates="area")


class Owner(SQLModel, table=True):
    """Product owner (PM or team)."""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
    team: Optional[str] = None
    role: Optional[str] = None  # PM, Tech Lead, etc.
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    ownerships: List["Ownership"] = Relationship(back_populates="owner")


class Ownership(SQLModel, table=True):
    """Mapping between product area and owner."""
    id: Optional[int] = Field(default=None, primary_key=True)
    area_id: int = Field(foreign_key="productarea.id")
    owner_id: int = Field(foreign_key="owner.id")
    confidence: float = Field(default=1.0)  # Initial confidence score
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    area: ProductArea = Relationship(back_populates="ownerships")
    owner: Owner = Relationship(back_populates="ownerships")


class QueryHistory(SQLModel, table=True):
    """Historical ownership queries for learning."""
    id: Optional[int] = Field(default=None, primary_key=True)
    query_text: str
    resolved_owner_id: Optional[int] = Field(foreign_key="owner.id", default=None)
    confidence_score: float
    source: Optional[str] = None  # User feedback, API, etc.
    created_at: datetime = Field(default_factory=datetime.utcnow)

