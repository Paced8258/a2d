"""RAG service for semantic search over ownership knowledge base."""
import chromadb
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.core.config import settings


class RAGService:
    """Service for RAG-based ownership resolution."""
    
    def __init__(self):
        """Initialize RAG service with embeddings and vector store."""
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=settings.openai_api_key
        )
        self.llm = ChatOpenAI(
            model=settings.model,
            api_key=settings.openai_api_key,
            temperature=0.3
        )
        self.vectorstore = Chroma(
            persist_directory=settings.chroma_persist_dir,
            embedding_function=self.embeddings,
            collection_name="ownership_knowledge"
        )
        self._init_prompts()
    
    def _init_prompts(self):
        """Initialize prompt templates."""
        self.ownership_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an ownership resolution assistant for Customer Support.
Your job is to help identify the correct product owner based on the context and retrieved information.

Principles:
- Be precise and factual
- Provide confidence scores based on evidence
- If unsure, indicate low confidence
- Always cite supporting context"""),
            ("user", """Based on the following retrieved context, identify the owner for this query:
Query: {query}
Context: {context}

Provide the owner name, contact, and confidence score (0-1).""")
        ])
    
    async def query_ownership(
        self, 
        query: str, 
        context: str = None
    ) -> Dict[str, Any]:
        """
        Query ownership using RAG.
        
        Args:
            query: Natural language query about ownership
            context: Additional context for the query
            
        Returns:
            Ownership resolution with confidence score
        """
        # Retrieve relevant documents
        retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": settings.retrieval_top_k}
        )
        
        # Retrieve documents
        docs = retriever.get_relevant_documents(query)
        
        # Build context from retrieved documents
        context_text = "\n\n".join([doc.page_content for doc in docs])
        if context:
            context_text = f"User context: {context}\n\n{context_text}"
        
        # Build RAG chain
        chain = (
            {"query": RunnablePassthrough(), "context": lambda x: context_text}
            | self.ownership_prompt
            | self.llm
            | StrOutputParser()
        )
        
        # Execute query
        result = chain.invoke({"query": query})
        
        return {
            "result": result,
            "retrieved_docs": [doc.page_content for doc in docs],
            "confidence": self._calculate_confidence(docs, query)
        }
    
    def _calculate_confidence(self, docs: List, query: str) -> float:
        """
        Calculate confidence score based on retrieved documents.
        
        This is a placeholder - in production, use more sophisticated scoring.
        """
        if not docs:
            return 0.0
        
        # Simple heuristic: more relevant docs = higher confidence
        base_confidence = min(len(docs) / settings.retrieval_top_k, 1.0)
        
        # TODO: Add semantic similarity scoring
        return round(base_confidence, 2)
    
    def add_documents(self, documents: List[str], metadatas: List[Dict] = None):
        """
        Add documents to the knowledge base.
        
        Args:
            documents: List of document texts
            metadatas: List of metadata dicts (optional)
        """
        self.vectorstore.add_texts(
            texts=documents,
            metadatas=metadatas or [{}] * len(documents)
        )

