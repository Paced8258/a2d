# LLM-Powered Ownership Resolution Assistant

A RAG-based system for Customer Support teams to quickly identify product owners and responsible teams for product features and areas.

## Architecture

- **RAG (Retrieval-Augmented Generation)**: Combines vector search with LLM reasoning
- **FastAPI**: REST API for ownership queries
- **LangChain**: LLM orchestration and RAG pipeline
- **ChromaDB**: Vector store for semantic search
- **LangFuse**: Observability and evaluations
- **SQLModel**: Structured ownership data and history

## Features

- 📊 Ingest structured data from Product Feature Matrix
- 🔍 Semantic search over ownership knowledge base
- 💬 Natural language queries via chat or Slack
- 📈 Confidence scores and supporting context
- 🔄 Learn from historical support tickets
- 📝 LangFuse-powered evaluations

## Project Structure

```
ownership_assistant/
├── app/
│   ├── api/
│   │   └── endpoints/      # API route handlers
│   ├── core/               # Configuration and settings
│   ├── models/             # Database models
│   ├── schemas/            # Pydantic schemas
│   └── services/           # Business logic (RAG, ingestion, etc.)
├── data/                   # Data sources and test files
├── notebooks/              # Exploratory notebooks
└── requirements.txt
```

## Getting Started

### 1. Install Dependencies

```bash
cd ownership_assistant
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file:

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-your-key-here
MODEL=gpt-4o-mini

# LangFuse (optional)
LANGFUSE_SECRET_KEY=sk-lf-your-key-here
LANGFUSE_PUBLIC_KEY=pk-lf-your-key-here
LANGFUSE_HOST=https://cloud.langfuse.com

# Database
DATABASE_URL=sqlite:///./ownership_assistant.db

# Vector Store
CHROMA_PERSIST_DIR=./chroma_db
```

### 3. Run the Server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Query Ownership

```
POST /api/v1/ownership/query
{
  "query": "Who owns the search feature?",
  "context": "Customer is reporting search issues"
}
```

### Ingest Data

```
POST /api/v1/ingest
{
  "source": "product_matrix",
  "data": [...]
}
```

### Health Check

```
GET /health
```

## Next Steps

1. Set up data ingestion pipeline
2. Configure RAG pipeline
3. Add LangFuse evals
4. Build Slack integration

## License

MIT

