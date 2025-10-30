# main.py — Ownership Resolution Assistant
# Purpose: REST API for ownership queries with LangChain integration

import json
from typing import Optional, List

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlmodel import select

# ---- Local modules ----
from db import init_db, get_session
from models import SupportTicket, Owner, ProductArea, Ownership, OwnershipMessage
from settings import settings
from prompts import build_ownership_resolution_prompt

# ---- LangChain imports ----
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnablePassthrough

# ---- LangFuse integration (optional) ----
try:
    from langfuse import Langfuse
    from langfuse.langchain import CallbackHandler
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    Langfuse = None
    CallbackHandler = None


# ---------- FastAPI app ----------
app = FastAPI(title="Ownership Resolution Assistant", version="0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()
    
    # Initialize LangFuse if credentials are provided
    if LANGFUSE_AVAILABLE and settings.langfuse_secret_key and settings.langfuse_public_key:
        print(f"✅ LangFuse initialized: {settings.langfuse_host}")
    else:
        print("ℹ️  LangFuse not configured (optional)")


# ---------- Pydantic Schemas ----------
class OwnershipQueryIn(BaseModel):
    query: str
    context: Optional[str] = None

class OwnerMatch(BaseModel):
    owner_name: str
    owner_email: str
    team: Optional[str] = None
    role: Optional[str] = None
    area_name: Optional[str] = None
    rationale: str
    confidence_score: float

class OwnershipQueryOut(BaseModel):
    ticket_id: int
    query: str
    matches: List[OwnerMatch]
    best_match: Optional[OwnerMatch] = None

class IngestDataIn(BaseModel):
    source: str  # product_matrix, notion, confluence
    data: List[dict]

class IngestDataOut(BaseModel):
    status: str
    records_ingested: int


# ---------- Helpers ----------
def _get_langfuse_handler():
    """Get LangFuse CallbackHandler if configured."""
    if (LANGFUSE_AVAILABLE and 
        settings.langfuse_secret_key and 
        settings.langfuse_public_key):
        langfuse = Langfuse(
            public_key=settings.langfuse_public_key,
            secret_key=settings.langfuse_secret_key,
            host=settings.langfuse_host
        )
        return CallbackHandler()
    return None

def _get_lc_model(callbacks=None):
    """Get LangChain model instance."""
    return ChatOpenAI(
        model=settings.model,
        temperature=0.3,
        api_key=settings.openai_api_key,
        callbacks=callbacks or [],
    )


# ---------- LangChain: Ownership resolution chain ----------
def _build_ownership_chain(prompt_blob: dict, callbacks=None):
    """Build chain for ownership resolution."""
    
    system_text = prompt_blob["system"]
    instructions = prompt_blob["instructions"]
    context = prompt_blob["context"]
    few_shot = prompt_blob["few_shot"]
    query = prompt_blob["query"]
    
    # Build user payload
    user_payload = json.dumps({
        "instructions": instructions,
        "query": query,
        "context": context,
        "example": few_shot
    }, indent=2)
    
    # Create prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_text),
        ("user", "{payload}")
    ])
    
    # JSON parser
    parser = JsonOutputParser()
    
    # Build chain
    chain = (
        {"payload": RunnablePassthrough()}
        | prompt
        | _get_lc_model(callbacks=callbacks)
        | parser
    )
    
    return chain, user_payload


# ---------- Routes ----------
@app.post("/query", response_model=OwnershipQueryOut)
def query_ownership(payload: OwnershipQueryIn, session=Depends(get_session)):
    """Query ownership for a feature or product area."""
    
    # Get all ownership data from database
    ownership_records = []
    for ownership in session.exec(select(Ownership)).all():
        area = session.get(ProductArea, ownership.area_id)
        owner = session.get(Owner, ownership.owner_id)
        ownership_records.append({
            "area_name": area.name,
            "description": area.description,
            "category": area.category,
            "owner_name": owner.name,
            "owner_email": owner.email,
            "team": owner.team,
            "role": owner.role
        })
    
    # Build prompt
    prompt_blob = build_ownership_resolution_prompt(
        query=payload.query,
        context=payload.context,
        ownership_data=ownership_records
    )
    
    # Get LangFuse handler
    langfuse_handler = _get_langfuse_handler()
    callbacks = [langfuse_handler] if langfuse_handler else []
    
    # Build chain
    chain, user_payload = _build_ownership_chain(prompt_blob, callbacks=callbacks)
    
    # Run the chain
    try:
        data = chain.invoke(user_payload, config={"callbacks": callbacks})
    except Exception as e:
        raise HTTPException(500, f"Model failed to produce JSON: {e}")
    
    # Create support ticket
    ticket = SupportTicket(
        query_text=payload.query,
        context=payload.context
    )
    session.add(ticket)
    session.commit()
    session.refresh(ticket)
    
    # Store best match
    if data.get("matches") and len(data["matches"]) > 0:
        best_match = data["matches"][0]
        ticket.resolved_owner_id = 1  # TODO: Look up actual owner
        ticket.confidence_score = best_match.get("confidence_score", 0.0)
        ticket.supporting_context = best_match.get("rationale", "")
        session.commit()
    
    # Convert matches to response format
    matches = [OwnerMatch(**match) for match in data.get("matches", [])]
    best_match = matches[0] if matches else None
    
    # Store messages
    session.add(OwnershipMessage(
        ticket_id=ticket.id,
        sender="user",
        content=payload.query
    ))
    session.add(OwnershipMessage(
        ticket_id=ticket.id,
        sender="assistant",
        content=json.dumps(data, indent=2)
    ))
    session.commit()
    
    return OwnershipQueryOut(
        ticket_id=ticket.id,
        query=payload.query,
        matches=matches,
        best_match=best_match
    )


@app.post("/ingest", response_model=IngestDataOut)
def ingest_data(payload: IngestDataIn, session=Depends(get_session)):
    """Ingest ownership data from external sources."""
    
    records_ingested = 0
    
    for record in payload.data:
        # Create or get owner
        owner_stmt = select(Owner).where(Owner.email == record.get("owner_email"))
        owner = session.exec(owner_stmt).first()
        
        if not owner:
            owner = Owner(
                name=record.get("owner_name"),
                email=record.get("owner_email"),
                team=record.get("team"),
                role=record.get("role")
            )
            session.add(owner)
            session.commit()
            session.refresh(owner)
        
        # Create or get product area
        area_stmt = select(ProductArea).where(ProductArea.name == record.get("feature_name"))
        area = session.exec(area_stmt).first()
        
        if not area:
            area = ProductArea(
                name=record.get("feature_name"),
                description=record.get("description"),
                category=record.get("category")
            )
            session.add(area)
            session.commit()
            session.refresh(area)
        
        # Create ownership mapping
        ownership_stmt = select(Ownership).where(
            Ownership.area_id == area.id,
            Ownership.owner_id == owner.id
        )
        ownership = session.exec(ownership_stmt).first()
        
        if not ownership:
            ownership = Ownership(
                area_id=area.id,
                owner_id=owner.id,
                confidence=1.0,
                notes=record.get("notes")
            )
            session.add(ownership)
            records_ingested += 1
    
    session.commit()
    
    return IngestDataOut(
        status="success",
        records_ingested=records_ingested
    )


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok"}


# ---- Start the server ----
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)  # Different port from a2d

