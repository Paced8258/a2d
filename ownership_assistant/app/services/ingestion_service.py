"""Data ingestion service for ownership data."""
from typing import List, Dict, Any
from app.models.ownership import ProductArea, Owner, Ownership
from app.models.rag import KnowledgeDocument
from app.services.rag_service import RAGService


class IngestionService:
    """Service for ingesting ownership data from various sources."""
    
    def __init__(self, rag_service: RAGService):
        """Initialize ingestion service."""
        self.rag_service = rag_service
    
    async def ingest_product_matrix(
        self,
        data: List[Dict[str, Any]],
        session
    ):
        """
        Ingest data from Product Feature Matrix.
        
        Args:
            data: List of product matrix records
            session: Database session
        """
        for record in data:
            # Extract product area
            area = ProductArea(
                name=record.get("feature_name"),
                description=record.get("description"),
                category=record.get("category")
            )
            session.add(area)
            session.commit()
            session.refresh(area)
            
            # Extract owner information
            owner = self._get_or_create_owner(
                name=record.get("owner_name"),
                email=record.get("owner_email"),
                team=record.get("team"),
                role=record.get("role"),
                session=session
            )
            
            # Create ownership mapping
            ownership = Ownership(
                area_id=area.id,
                owner_id=owner.id,
                confidence=1.0,
                notes=record.get("notes")
            )
            session.add(ownership)
            
            # Add to knowledge base
            kb_doc = self._create_kb_document(record)
            self.rag_service.add_documents([kb_doc["content"]], [kb_doc["metadata"]])
        
        session.commit()
    
    def _get_or_create_owner(
        self,
        name: str,
        email: str,
        team: str = None,
        role: str = None,
        session = None
    ) -> Owner:
        """Get or create an owner."""
        # Check if owner exists
        from sqlmodel import select
        
        statement = select(Owner).where(Owner.email == email)
        existing = session.exec(statement).first()
        
        if existing:
            return existing
        
        # Create new owner
        owner = Owner(
            name=name,
            email=email,
            team=team,
            role=role
        )
        session.add(owner)
        session.commit()
        session.refresh(owner)
        
        return owner
    
    def _create_kb_document(self, record: Dict[str, Any]) -> Dict[str, str]:
        """Create a knowledge base document from a record."""
        content = f"""
        Product Area: {record.get('feature_name')}
        Description: {record.get('description', 'N/A')}
        Category: {record.get('category', 'N/A')}
        Owner: {record.get('owner_name')}
        Team: {record.get('team', 'N/A')}
        Role: {record.get('role', 'N/A')}
        Contact: {record.get('owner_email')}
        Notes: {record.get('notes', 'N/A')}
        """
        
        metadata = {
            "source": "product_matrix",
            "feature_name": record.get("feature_name"),
            "category": record.get("category"),
            "owner": record.get("owner_name")
        }
        
        return {
            "content": content.strip(),
            "metadata": metadata
        }
    
    async def ingest_notion(self, data: List[Dict], session):
        """Ingest data from Notion."""
        # TODO: Implement Notion ingestion
        pass
    
    async def ingest_confluence(self, data: List[Dict], session):
        """Ingest data from Confluence."""
        # TODO: Implement Confluence ingestion
        pass

