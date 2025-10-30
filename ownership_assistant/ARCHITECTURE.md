# Architecture Overview

This document describes the architecture of the Ownership Resolution Assistant.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Client Layer                           │
│  (Chat UI / Slack Bot / Support Tool)                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                      API Layer                              │
│  FastAPI REST API                                           │
│  - /api/v1/ownership/query                                  │
│  - /api/v1/ingest/                                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   RAG Pipeline                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Query      │───▶│  Retrieval   │───▶│  Generation  │  │
│  │   Parser     │    │  (Vector DB) │    │  (LLM)       │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Knowledge Base & Storage                       │
│  ┌──────────────────┐        ┌──────────────────┐         │
│  │   ChromaDB       │        │   SQLite DB      │         │
│  │   (Vector Store) │        │   (Structured)   │         │
│  └──────────────────┘        └──────────────────┘         │
└─────────────────────────────────────────────────────────────┘
                     ▲
                     │
┌────────────────────┴────────────────────────────────────────┐
│                   Data Sources                              │
│  - Product Feature Matrix                                   │
│  - Notion                                                   │
│  - Confluence                                               │
│  - Historical Support Tickets                               │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. API Layer

**Technology**: FastAPI

**Endpoints**:
- `POST /api/v1/ownership/query` - Query ownership
- `POST /api/v1/ingest/` - Ingest data
- `GET /health` - Health check

### 2. RAG Pipeline

**Technology**: LangChain + OpenAI

**Components**:
- **Retrieval**: Semantic search over vector database
- **Generation**: LLM-powered reasoning and extraction
- **Orchestration**: LangChain chains for structured output

**Flow**:
1. Parse natural language query
2. Retrieve relevant documents from vector store
3. Generate ownership resolution with confidence
4. Return structured result

### 3. Data Storage

#### ChromaDB (Vector Store)
- Stores embeddings of ownership documents
- Enables semantic search
- Persistent storage on disk

#### SQLite (Structured Data)
- ProductArea: Product features/areas
- Owner: PM and team information
- Ownership: Mapping between areas and owners
- QueryHistory: Historical queries for learning

### 4. Data Sources

**Product Feature Matrix**:
```json
{
  "feature_name": "Search",
  "owner_name": "Jane Doe",
  "owner_email": "jane@example.com"
}
```

**Notion** (Future):
- Extract ownership from Notion databases

**Confluence** (Future):
- Parse ownership from Confluence pages

## Data Flow

### Query Flow

```
User Query
   ↓
API Endpoint
   ↓
RAG Service
   ↓
Vector Retrieval (top-k documents)
   ↓
LLM Generation (extract ownership)
   ↓
LangFuse Tracking
   ↓
Structured Response
```

### Ingestion Flow

```
Data Source (Product Matrix)
   ↓
Ingestion Service
   ↓
Extract Ownership Info
   ↓
Store in SQLite
   ↓
Create Knowledge Documents
   ↓
Generate Embeddings
   ↓
Store in ChromaDB
```

## Configuration

All configuration is managed via environment variables:

- `OPENAI_API_KEY`: Required for LLM
- `LANGFUSE_*`: Optional for observability
- `DATABASE_URL`: SQLite database path
- `CHROMA_PERSIST_DIR`: Vector store location

## Observability

**LangFuse Integration**:
- Track all queries and responses
- Measure latency and costs
- Evaluate accuracy with historical data
- A/B test prompt variations

## Future Enhancements

1. **Multi-modal RAG**: Support images and charts
2. **Active Learning**: Improve from user feedback
3. **Slack Integration**: Direct Slack bot
4. **Real-time Updates**: Live sync with data sources
5. **Advanced Eval**: Automated accuracy testing

## Performance Considerations

- **Vector Retrieval**: O(log n) with ChromaDB
- **LLM Generation**: ~2-5 seconds per query
- **Caching**: Consider Redis for frequent queries
- **Batch Processing**: Process historical data in batches

## Security

- API key management via environment variables
- No PII stored in vector database
- Rate limiting (to be added)
- Authentication (to be added)

