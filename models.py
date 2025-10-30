from datetime import datetime
from typing import Optional, List
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship

# Enums
class SenderType(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class DifficultyLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

# Entities
class SessionThread(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    role_raw: str
    industry_raw: str
    pains_raw: str
    role_normalized: Optional[str] = None
    onet_code: Optional[str] = None

    messages: List["ChatMessage"] = Relationship(back_populates="thread")
    recommendations: List["Recommendation"] = Relationship(back_populates="thread")

class ChatMessage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    thread_id: int = Field(foreign_key="sessionthread.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    sender: SenderType
    content: str

    thread: SessionThread = Relationship(back_populates="messages")

class Recommendation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    thread_id: int = Field(foreign_key="sessionthread.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    item: str                   # concise Anti-To-Do action
    rationale: str              # why this matters for this role/industry
    estimated_gain_minutes: int # rough weekly time reclaimed
    difficulty: DifficultyLevel
    category: str               # automate / outsource / batch / eliminate / delegate

    thread: SessionThread = Relationship(back_populates="recommendations")