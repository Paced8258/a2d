"""Application configuration and settings."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenAI Configuration
    openai_api_key: str
    model: str = "gpt-4o-mini"
    
    # LangFuse settings (optional)
    langfuse_secret_key: Optional[str] = None
    langfuse_public_key: Optional[str] = None
    langfuse_host: str = "https://cloud.langfuse.com"
    
    # Database settings
    database_url: str = "sqlite:///./ownership_assistant.db"
    
    # Vector store settings
    chroma_persist_dir: str = "./chroma_db"
    
    # RAG settings
    retrieval_top_k: int = 5
    min_confidence_score: float = 0.7
    
    # API settings
    api_v1_prefix: str = "/api/v1"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

