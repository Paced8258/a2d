# main.py — LangChain version
# Purpose: Keep the same REST surface (/onboard, /recommendations, /chat),
# but route LLM calls through LangChain (ChatOpenAI + structured JSON parsing).

import json
from typing import Optional, List, Tuple

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlmodel import select

# ---- Local modules (unchanged from your project) ----
from db import init_db, get_session
from models import SessionThread, ChatMessage, Recommendation
from settings import settings
from prompts import build_recommendations_prompt

# ---- LangChain imports ----
# LangChain v0.2+ splits providers & core
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
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
app = FastAPI(title="Anti-To-Do Backend (LangChain)", version="0.2")

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
class OnboardIn(BaseModel):
    role: str
    industry: str
    pains: str

class OnboardOut(BaseModel):
    thread_id: int
    role_normalized: Optional[str] = None
    onet_code: Optional[str] = None

class RecsIn(BaseModel):
    thread_id: int

class RecItem(BaseModel):
    item: str
    rationale: str
    category: str
    estimated_gain_minutes: int
    difficulty: str

class RecsOut(BaseModel):
    thread_id: int
    items: List[RecItem]

class ChatIn(BaseModel):
    thread_id: int
    message: str

class ChatOut(BaseModel):
    thread_id: int
    reply: str

# ---------- Helpers ----------
def _normalize_role(role: str, industry: str) -> Tuple[Optional[str], Optional[str]]:
    r = role.strip().lower()
    alias = {
        "pm": "Product Manager",
        "product boss": "Product Manager",
        "ops": "Operations Manager",
        "ops lead": "Operations Manager",
        "software dev": "Software Engineer",
        "swe": "Software Engineer",
    }
    normalized = alias.get(r, role.title())
    return normalized, None

def _get_langfuse_handler():
    """
    Get LangFuse CallbackHandler if credentials are configured.
    Returns None if LangFuse is not configured or not available.
    """
    if (LANGFUSE_AVAILABLE and 
        settings.langfuse_secret_key and 
        settings.langfuse_public_key):
        # Initialize LangFuse client
        langfuse = Langfuse(
            public_key=settings.langfuse_public_key,
            secret_key=settings.langfuse_secret_key,
            host=settings.langfuse_host
        )
        # Create callback handler
        return CallbackHandler()
    return None

def _get_lc_model(callbacks=None):
    """
    Single place to instantiate the LC model.
    Uses environment variable OPENAI_API_KEY via settings.
    """
    # You can swap models here without touching business logic.
    return ChatOpenAI(
        model=settings.model,       # e.g., "gpt-4o-mini"
        temperature=0.3,
        api_key=settings.openai_api_key,
        callbacks=callbacks or [],
    )

# ---------- LangChain: Recommendation chain ----------
def _build_recommendations_chain(prompt_blob: dict, callbacks=None):
    """
    Build a deterministic chain:
    System + user JSON blob --> JSON output.
    """
    # Prepare pieces
    system_text = prompt_blob["system"]
    instructions = prompt_blob["instructions"]
    context = prompt_blob["context"]
    few_shot = prompt_blob["few_shot"]

    # We pass a single "payload" variable to the LLM as the user message
    # to keep things deterministic and easily reproducible.
    user_payload = {
        "instructions": instructions,
        "context": context,
        "few_shot": few_shot
    }

    # Prompt template: fixed system + dynamic user content
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_text),
        ("user", "{payload}")
    ])

    # JSON parser to force structured output (raises on invalid JSON)
    parser = JsonOutputParser()

    # Chain: input -> prompt.format -> llm -> parser
    chain = (
        {"payload": RunnablePassthrough()}  # pass through our dict
        | prompt
        | _get_lc_model(callbacks=callbacks)
        | parser
    )
    return chain, user_payload

# ---------- Routes ----------
@app.post("/onboard", response_model=OnboardOut)
def onboard(payload: OnboardIn, session=Depends(get_session)):
    role_n, onet = _normalize_role(payload.role, payload.industry)
    thread = SessionThread(
        role_raw=payload.role,
        industry_raw=payload.industry,
        pains_raw=payload.pains,
        role_normalized=role_n,
        onet_code=onet
    )
    session.add(thread)
    session.commit()
    session.refresh(thread)

    # Seed initial messages for continuity
    session.add(ChatMessage(thread_id=thread.id, sender="system",
                            content="Anti-To-Do assistant initialized."))
    session.add(ChatMessage(thread_id=thread.id, sender="user",
                            content=f"Role={payload.role}; Industry={payload.industry}; Pains={payload.pains}"))
    session.commit()

    return OnboardOut(thread_id=thread.id, role_normalized=role_n, onet_code=onet)

@app.post("/recommendations", response_model=RecsOut)
def recommendations(payload: RecsIn, session=Depends(get_session)):
    thread = session.get(SessionThread, payload.thread_id)
    if not thread:
        raise HTTPException(404, "Thread not found")
    
    # Get LangFuse handler for tracing
    langfuse_handler = _get_langfuse_handler()
    callbacks = [langfuse_handler] if langfuse_handler else []

    # Build context + chain
    prompt_blob = build_recommendations_prompt(
        role_raw=thread.role_raw,
        industry_raw=thread.industry_raw,
        pains_raw=thread.pains_raw,
        role_normalized=thread.role_normalized,
        onet_code=thread.onet_code
    )
    chain, user_payload = _build_recommendations_chain(prompt_blob, callbacks=callbacks)

    # Run the chain (returns Python dict thanks to JsonOutputParser)
    try:
        data = chain.invoke(user_payload, config={"callbacks": callbacks})
    except Exception as e:
        raise HTTPException(500, f"Model failed to produce JSON: {e}")

    # Persist recs - handle new structured format
    items: List[RecItem] = []
    
    # Handle both old format (items) and new format (categories)
    if "categories" in data:
        # New structured format by category
        for category_data in data.get("categories", []):
            category_name = category_data.get("category_name", "General")
            for it in category_data.get("items", []):
                try:
                    rec = Recommendation(
                        thread_id=thread.id,
                        item=str(it["item"]),
                        rationale=str(it.get("rationale", "")),
                        category=str(category_name),
                        estimated_gain_minutes=int(it.get("estimated_gain_minutes", 0)),
                        difficulty=str(it.get("difficulty", "medium"))
                    )
                    session.add(rec)
                    items.append(RecItem(**{
                        "item": rec.item,
                        "rationale": rec.rationale,
                        "category": rec.category,
                        "estimated_gain_minutes": rec.estimated_gain_minutes,
                        "difficulty": rec.difficulty
                    }))
                except Exception as e:
                    # skip invalid items rather than 500 the whole request
                    continue
    else:
        # Fallback to old format for backward compatibility
        for it in data.get("items", [])[:5]:
            try:
                rec = Recommendation(
                    thread_id=thread.id,
                    item=str(it["item"]),
                    rationale=str(it.get("rationale", "")),
                    category=str(it.get("category", "General")),
                    estimated_gain_minutes=int(it.get("estimated_gain_minutes", 0)),
                    difficulty=str(it.get("difficulty", "medium"))
                )
                session.add(rec)
                items.append(RecItem(**{
                    "item": rec.item,
                    "rationale": rec.rationale,
                    "category": rec.category,
                    "estimated_gain_minutes": rec.estimated_gain_minutes,
                    "difficulty": rec.difficulty
                }))
            except Exception:
                continue
    
    session.commit()

    # Log assistant output as a message (optional)
    session.add(ChatMessage(thread_id=thread.id, sender="assistant", content=json.dumps(data)))
    session.commit()

    return RecsOut(thread_id=thread.id, items=items)

@app.post("/chat", response_model=ChatOut)
def chat(payload: ChatIn, session=Depends(get_session)):
    thread = session.get(SessionThread, payload.thread_id)
    if not thread:
        raise HTTPException(404, "Thread not found")
    
    # Get LangFuse handler for tracing
    langfuse_handler = _get_langfuse_handler()
    callbacks = [langfuse_handler] if langfuse_handler else []

    # Pull a short history window
    q = select(ChatMessage).where(ChatMessage.thread_id == thread.id)\
                           .order_by(ChatMessage.created_at.desc()).limit(12)
    history = list(reversed(session.exec(q).all()))

    # LangChain prompt with a history placeholder
    base_system = (
        "You are the Anti-To-Do assistant. "
        "Be concise and actionable; avoid stereotypes; clarify only if essential."
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", base_system),
        MessagesPlaceholder(variable_name="history"),
        ("user", "{user_msg}")
    ])
    llm = _get_lc_model(callbacks=callbacks)

    # Prepare LC "history" messages in LangChain's expected format
    # Convert our stored messages to tuples ("user"/"assistant", content)
    lc_history = []
    for m in history:
        role = "assistant" if m.sender == "assistant" else "user" if m.sender == "user" else "system"
        # Only include user/assistant in the rolling history; system is already set above
        if role in ("user", "assistant"):
            lc_history.append((role, m.content))

    chain = prompt | llm

    try:
        resp = chain.invoke({"history": lc_history, "user_msg": payload.message}, config={"callbacks": callbacks})
        reply_text = resp.content if hasattr(resp, "content") else str(resp)
    except Exception as e:
        raise HTTPException(500, f"Chat model error: {e}")

    # Persist the exchange
    session.add(ChatMessage(thread_id=thread.id, sender="user", content=payload.message))
    session.add(ChatMessage(thread_id=thread.id, sender="assistant", content=reply_text))
    session.commit()

    return ChatOut(thread_id=thread.id, reply=reply_text)

# ---- (Optional) health checks ----
@app.get("/health")
def health():
    return {"status": "ok"}

# # ---- Start the server ----
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)