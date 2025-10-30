# Ownership Resolution Assistant

An LLM-powered system for Customer Support teams to quickly identify product owners using the same architecture as the Anti-To-Do Backend.

## Overview

This application helps support agents identify the correct product owner or responsible team for product features. It uses LangChain for LLM orchestration and follows the same patterns as the a2d project.

## Architecture

- **FastAPI**: REST API
- **LangChain**: LLM orchestration with structured JSON output
- **LangFuse**: Optional LLM observability
- **SQLModel**: Database ORM
- **SQLite**: Database storage

## Getting Started

### Prerequisites

- Python 3.9+
- Virtual environment
- OpenAI API key

### Installation

1. Activate virtual environment:
```bash
source ../venv_a2d/bin/activate  # or create new venv
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Configuration

Create `.env` file (copy from `.env.example`):

```bash
OPENAI_API_KEY=sk-your-key-here
MODEL=gpt-4o-mini
DATABASE_URL=sqlite:///ownership_assistant.db
```

### Running the Server

```bash
python main.py
```

Server runs on `http://localhost:8001` (different port from a2d)

## API Endpoints

### Query Ownership

**POST** `/query`

```json
{
  "query": "Who owns the search feature?",
  "context": "Customer reporting slow search"
}
```

Response:
```json
{
  "ticket_id": 1,
  "query": "Who owns the search feature?",
  "matches": [{
    "owner_name": "Jane Doe",
    "owner_email": "jane@example.com",
    "team": "Product",
    "role": "PM",
    "area_name": "Search Functionality",
    "rationale": "...",
    "confidence_score": 0.95
  }],
  "best_match": {...}
}
```

### Ingest Data

**POST** `/ingest`

```json
{
  "source": "product_matrix",
  "data": [{
    "feature_name": "Search",
    "description": "...",
    "category": "Core",
    "owner_name": "Jane Doe",
    "owner_email": "jane@example.com",
    "team": "Product",
    "role": "PM"
  }]
}
```

### Health Check

**GET** `/health`

Returns: `{"status": "ok"}`

## Project Structure

```
ownership_assistant/
├── main.py           # FastAPI application
├── models.py         # Database models
├── db.py             # Database initialization
├── prompts.py        # LLM prompt templates
├── settings.py       # Configuration
├── requirements.txt  # Dependencies
├── data/             # Sample data
└── notebooks/        # Exploration notebooks
```

## Features

- ✅ Natural language ownership queries
- ✅ Confidence scores for matches
- ✅ Structured ownership data ingestion
- ✅ LangFuse integration for observability
- ✅ Same architecture as a2d project

## Documentation

- **README.md** (this file) - Overview
- **ARCHITECTURE.md** - System architecture details
- **QUICKSTART.md** - Getting started guide
- **IMPLEMENTATION_NOTES.md** - Development roadmap

## License

MIT
