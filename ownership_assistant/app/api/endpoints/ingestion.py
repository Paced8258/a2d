"""Data ingestion API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import Any

from app.schemas.ownership import IngestData
from app.services.ingestion_service import IngestionService
from app.services.rag_service import RAGService
from app.core.database import get_session

router = APIRouter(prefix="/ingest", tags=["ingestion"])


async def ingest_data_endpoint(
    ingest_data: IngestData,
    session: Session = Depends(get_session)
) -> dict:
    """
    Ingest ownership data from various sources.
    
    Args:
        ingest_data: Data ingestion request
        session: Database session
    
    Returns:
        Ingest result
    """
    rag_service = RAGService()
    ingestion_service = IngestionService(rag_service)
    
    try:
        if ingest_data.source == "product_matrix":
            await ingestion_service.ingest_product_matrix(
                data=ingest_data.data,
                session=session
            )
        elif ingest_data.source == "notion":
            await ingestion_service.ingest_notion(
                data=ingest_data.data,
                session=session
            )
        elif ingest_data.source == "confluence":
            await ingestion_service.ingest_confluence(
                data=ingest_data.data,
                session=session
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported source: {ingest_data.source}"
            )
        
        return {
            "status": "success",
            "source": ingest_data.source,
            "records_ingested": len(ingest_data.data)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ingestion failed: {str(e)}"
        )


# Register endpoint
router.add_api_route("/", ingest_data_endpoint, methods=["POST"])

