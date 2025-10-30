"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import ownership, health, ingestion
from app.core.database import init_db
from app.core.config import settings

# Initialize FastAPI app
app = FastAPI(
    title="Ownership Resolution Assistant",
    version="0.1.0",
    description="LLM-powered ownership resolution for Customer Support teams"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup():
    init_db()
    print("✅ Database initialized")

# Include routers
app.include_router(
    ownership.router,
    prefix=settings.api_v1_prefix
)
app.include_router(
    ingestion.router,
    prefix=settings.api_v1_prefix
)
app.include_router(health.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Ownership Resolution Assistant",
        "version": "0.1.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

