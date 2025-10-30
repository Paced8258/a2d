#!/usr/bin/env python3
"""
Quick test script for ownership resolution.
Run this to test the setup.
"""

import requests
import json

API_BASE = "http://localhost:8001"


def test_health():
    """Test health endpoint."""
    print("1. Testing health endpoint...")
    response = requests.get(f"{API_BASE}/health")
    assert response.status_code == 200
    print(f"   ✅ Health check passed: {response.json()}")


def test_ingest():
    """Test data ingestion."""
    print("\n2. Testing data ingestion...")
    
    # Load sample data
    with open("data/sample_product_matrix.json", "r") as f:
        sample_data = json.load(f)
    
    payload = {
        "source": "product_matrix",
        "data": sample_data
    }
    
    response = requests.post(f"{API_BASE}/ingest", json=payload)
    assert response.status_code == 200
    result = response.json()
    print(f"   ✅ Ingested {result['records_ingested']} records")


def test_query():
    """Test ownership query."""
    print("\n3. Testing ownership query...")
    
    payload = {
        "query": "Who owns the search feature?",
        "context": "Customer reporting slow search results"
    }
    
    response = requests.post(f"{API_BASE}/query", json=payload)
    assert response.status_code == 200
    result = response.json()
    print(f"   ✅ Query successful")
    print(f"   Ticket ID: {result['ticket_id']}")
    print(f"   Matches found: {len(result['matches'])}")
    
    if result['best_match']:
        print(f"\n   Best match:")
        print(f"   - Name: {result['best_match']['owner_name']}")
        print(f"   - Email: {result['best_match']['owner_email']}")
        print(f"   - Confidence: {result['best_match']['confidence_score']}")
        print(f"   - Rationale: {result['best_match']['rationale'][:100]}...")


def main():
    print("🧪 Testing Ownership Resolution Assistant\n")
    print("Make sure the server is running on http://localhost:8001\n")
    
    try:
        test_health()
        test_ingest()
        test_query()
        print("\n✅ All tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("\nMake sure to:")
        print("1. Start the server: python main.py")
        print("2. Configure .env with OPENAI_API_KEY")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

