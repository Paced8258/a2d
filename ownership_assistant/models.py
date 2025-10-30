from datetime import datetime
from typing import Optional, List
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship


# Enums
class SenderType(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


# Entities
class SupportTicket(SQLModel, table=True):
    """Support ticket requiring ownership resolution."""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    query_text: str  # Natural language query about ownership
    context: Optional[str] = None  # Additional context from ticket
    
    # Resolution
    resolved_owner_id: Optional[int] = Field(foreign_key="owner.id", default=None)
    confidence_score: Optional[float] = None
    supporting_context: Optional[str] = None
    
    messages: List["OwnershipMessage"] = Relationship(back_populates="ticket")


class Owner(SQLModel, table=True):
    """Product owner (PM or team)."""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
    team: Optional[str] = None
    role: Optional[str] = None  # PM, Tech Lead, etc.
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    ownerships: List["Ownership"] = Relationship(back_populates="owner")


class ProductArea(SQLModel, table=True):
    """Product area or feature."""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    ownerships: List["Ownership"] = Relationship(back_populates="area")


class Ownership(SQLModel, table=True):
    """Mapping between product area and owner."""
    id: Optional[int] = Field(default=None, primary_key=True)
    area_id: int = Field(foreign_key="productarea.id")
    owner_id: int = Field(foreign_key="owner.id")
    confidence: float = Field(default=1.0)
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    area: ProductArea = Relationship(back_populates="ownerships")
    owner: Owner = Relationship(back_populates="ownerships")


class OwnershipMessage(SQLModel, table=True):
    """Messages in ownership resolution session."""
    id: Optional[int] = Field(default=None, primary_key=True)
    ticket_id: int = Field(foreign_key="supportticket.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    sender: SenderType
    content: str
    
    ticket: SupportTicket = Relationship(back_populates="messages")

