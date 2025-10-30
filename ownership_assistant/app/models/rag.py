"""RAG-specific models for document management."""
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class KnowledgeDocument(SQLModel, table=True):
    """Document in the knowledge base."""
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str
    source: str  # e.g., "product_matrix", "notion", "confluence"
    source_id: Optional[str] = None  # External ID from source
    metadata: Optional[str] = None  # JSON metadata
    embedding_id: Optional[str] = None  # Reference to vector store
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

