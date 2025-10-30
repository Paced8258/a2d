"""Ownership resolution API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import Optional

from app.schemas.ownership import OwnershipQuery, OwnershipResolution, OwnerInfo
from app.services.rag_service import RAGService
from app.services.langfuse_service import langfuse_service
from app.core.database import get_session
from app.models.ownership import Owner

router = APIRouter(prefix="/ownership", tags=["ownership"])


async def query_ownership_endpoint(
    query_data: OwnershipQuery,
    session: Session = Depends(get_session)
) -> OwnershipResolution:
    """
    Query ownership using RAG.
    
    Args:
        query_data: Ownership query request
        session: Database session
    
    Returns:
        Ownership resolution with confidence score
    """
    # Initialize RAG service
    rag_service = RAGService()
    
    # Query using RAG
    result = await rag_service.query_ownership(
        query=query_data.query,
        context=query_data.context
    )
    
    # Track with LangFuse
    langfuse_service.track_query(
        query=query_data.query,
        result=result["result"],
        confidence=result["confidence"],
        metadata={"context": query_data.context}
    )
    
    # TODO: Parse result to extract owner information
    # For now, return mock data
    mock_owner = OwnerInfo(
        id=1,
        name="Jane Doe",
        email="jane@example.com",
        team="Product",
        role="PM"
    )
    
    return OwnershipResolution(
        query=query_data.query,
        owner=mock_owner,
        confidence_score=result["confidence"],
        supporting_context=result["retrieved_docs"][0] if result["retrieved_docs"] else None
    )


# Register endpoint
router.add_api_route("/query", query_ownership_endpoint, methods=["POST"])

