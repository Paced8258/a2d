from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    openai_api_key: str
    model: str = "gpt-4o-mini"
    
    # LangFuse settings (optional - leave empty to disable tracking)
    langfuse_secret_key: Optional[str] = None
    langfuse_public_key: Optional[str] = None
    langfuse_host: str = "https://cloud.langfuse.com"
    
    # Database settings
    database_url: str = "sqlite:///ownership_assistant.db"
    
    class Config:
        env_file = ".env"


settings = Settings()

