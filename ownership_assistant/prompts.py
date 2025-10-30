SYSTEM_PROMPT = """You are an Ownership Resolution Assistant for Customer Support teams.
Your job: help identify the correct product owner or responsible team for product features and areas.

Principles:
- Be precise and factual based on the information provided
- Provide confidence scores based on evidence quality
- If unsure, indicate low confidence
- Always cite supporting context
- Return ownership information in the specified JSON format
"""

OWNERSHIP_RESOLUTION_INSTRUCTIONS = """Using the provided ownership information, identify the most relevant owner for the given query.

For EACH ownership match, include:
- owner_name: Name of the product owner
- owner_email: Email contact
- team: Team or department
- role: Role title (PM, Tech Lead, etc.)
- area_name: Product area/feature name
- rationale: Why this owner is relevant (based on query and context)
- confidence_score: Float between 0 and 1

Output JSON:
{
  "matches": [
    {
      "owner_name": "...",
      "owner_email": "...",
      "team": "...",
      "role": "...",
      "area_name": "...",
      "rationale": "...",
      "confidence_score": 0.85
    }
  ]
}
"""

# Few-shot examples
FEW_SHOT_EXAMPLE = {
    "query": "Who owns the search functionality?",
    "context": "Customer reporting slow search results",
    "matches": [
        {
            "owner_name": "Jane Doe",
            "owner_email": "jane@example.com",
            "team": "Product",
            "role": "PM",
            "area_name": "Search Functionality",
            "rationale": "Jane Doe is the PM for Search Functionality which handles search features and performance.",
            "confidence_score": 0.95
        }
    ]
}


def build_ownership_resolution_prompt(query: str, context: str = None, ownership_data: list = None):
    """Build prompt for ownership resolution."""
    
    # Build context from ownership data
    context_text = "\n\n".join([
        f"Product Area: {item.get('area_name', 'N/A')}\n"
        f"Description: {item.get('description', 'N/A')}\n"
        f"Category: {item.get('category', 'N/A')}\n"
        f"Owner: {item.get('owner_name', 'N/A')}\n"
        f"Email: {item.get('owner_email', 'N/A')}\n"
        f"Team: {item.get('team', 'N/A')}\n"
        f"Role: {item.get('role', 'N/A')}"
        for item in (ownership_data or [])
    ])
    
    if context:
        context_text = f"User Context: {context}\n\n{context_text}"
    
    return {
        "system": SYSTEM_PROMPT,
        "instructions": OWNERSHIP_RESOLUTION_INSTRUCTIONS,
        "context": context_text,
        "few_shot": FEW_SHOT_EXAMPLE,
        "query": query
    }

