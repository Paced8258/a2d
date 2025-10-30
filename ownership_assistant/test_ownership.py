#!/usr/bin/env python3
"""
Quick test script for the ownership resolution assistant.
Run this to test the setup before building the full system.
"""

import json
import asyncio
from app.core.database import init_db
from app.services.rag_service import RAGService
from app.services.ingestion_service import IngestionService
from app.core.database import get_session


async def test_ownership_resolution():
    """Test ownership resolution."""
    print("🧪 Testing Ownership Resolution Assistant\n")
    
    # Initialize database
    print("1. Initializing database...")
    init_db()
    print("   ✅ Database initialized")
    
    # Load sample data
    print("\n2. Loading sample data...")
    with open("data/sample_product_matrix.json", "r") as f:
        sample_data = json.load(f)
    print(f"   ✅ Loaded {len(sample_data)} records")
    
    # Initialize services
    print("\n3. Initializing services...")
    rag_service = RAGService()
    ingestion_service = IngestionService(rag_service)
    print("   ✅ Services initialized")
    
    # Ingest data
    print("\n4. Ingesting data...")
    session = next(get_session())
    await ingestion_service.ingest_product_matrix(sample_data, session)
    print("   ✅ Data ingested")
    
    # Test queries
    print("\n5. Testing ownership queries...")
    
    test_queries = [
        "Who owns the search feature?",
        "I need to contact someone about payment processing",
        "Who can help with analytics?"
    ]
    
    for query in test_queries:
        print(f"\n   Query: {query}")
        result = await rag_service.query_ownership(query)
        print(f"   Confidence: {result['confidence']}")
        print(f"   Result preview: {result['result'][:100]}...")
    
    print("\n✅ All tests passed!")


if __name__ == "__main__":
    asyncio.run(test_ownership_resolution())

