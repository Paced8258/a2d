"""LangFuse integration for observability and evaluations."""
from typing import Optional
from app.core.config import settings


class LangFuseService:
    """Service for LangFuse observability."""
    
    def __init__(self):
        """Initialize LangFuse if credentials are provided."""
        self.enabled = False
        self.langfuse = None
        self.handler = None
        
        if settings.langfuse_secret_key and settings.langfuse_public_key:
            try:
                from langfuse import Langfuse
                from langfuse.langchain import CallbackHandler
                
                self.langfuse = Langfuse(
                    public_key=settings.langfuse_public_key,
                    secret_key=settings.langfuse_secret_key,
                    host=settings.langfuse_host
                )
                self.handler = CallbackHandler()
                self.enabled = True
                print("✅ LangFuse initialized")
            except ImportError:
                print("ℹ️  LangFuse not available")
        else:
            print("ℹ️  LangFuse not configured (optional)")
    
    def get_callbacks(self):
        """Get callbacks for LangChain."""
        return [self.handler] if self.enabled and self.handler else []
    
    def track_query(
        self,
        query: str,
        result: str,
        confidence: float,
        metadata: Optional[dict] = None
    ):
        """Track a query for evaluation."""
        if not self.enabled:
            return
        
        try:
            trace = self.langfuse.trace(name="ownership_query")
            trace.generation(
                name="ownership_resolution",
                input=query,
                output=result,
                metadata={
                    "confidence": confidence,
                    **(metadata or {})
                }
            )
        except Exception as e:
            print(f"⚠️  LangFuse tracking failed: {e}")


# Singleton instance
langfuse_service = LangFuseService()

