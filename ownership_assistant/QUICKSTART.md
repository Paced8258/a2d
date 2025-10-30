# Quick Start Guide

Get your ownership resolution assistant up and running in 5 minutes.

## Prerequisites

- Python 3.9+
- OpenAI API key
- (Optional) LangFuse credentials

## Setup

### 1. Install Dependencies

```bash
cd ownership_assistant
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```bash
OPENAI_API_KEY=sk-your-actual-key-here
```

### 3. Run Quick Test

Test the setup with sample data:

```bash
python test_ownership.py
```

This will:
- Initialize the database
- Load sample product matrix data
- Test ownership queries

### 4. Start the Server

```bash
python -m app.main
```

Or with uvicorn:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## Usage Examples

### 1. Health Check

```bash
curl http://localhost:8000/health
```

### 2. Query Ownership

```bash
curl -X POST http://localhost:8000/api/v1/ownership/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Who owns the search feature?",
    "context": "Customer reporting search issues"
  }'
```

### 3. Ingest Data

```bash
curl -X POST http://localhost:8000/api/v1/ingest/ \
  -H "Content-Type: application/json" \
  -d '{
    "source": "product_matrix",
    "data": [{
      "feature_name": "New Feature",
      "description": "Feature description",
      "category": "Core",
      "owner_name": "John Doe",
      "owner_email": "john@example.com",
      "team": "Product",
      "role": "PM"
    }]
  }'
```

## Next Steps

1. **Customize Data Sources**: Update `ingestion_service.py` to integrate with your actual data sources
2. **Improve Prompts**: Tune the RAG prompts in `rag_service.py` for better results
3. **Add Eval Framework**: Set up LangFuse for tracking and evaluation
4. **Build UI**: Create a chat interface or Slack integration

## Project Structure

```
ownership_assistant/
├── app/
│   ├── api/              # API endpoints
│   ├── core/             # Configuration
│   ├── models/           # Database models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   └── main.py           # FastAPI app
├── data/                 # Sample data
├── notebooks/            # Exploration notebooks
└── requirements.txt      # Dependencies
```

## Troubleshooting

### "ModuleNotFoundError"

Make sure you've installed dependencies:

```bash
pip install -r requirements.txt
```

### "OPENAI_API_KEY not found"

Check your `.env` file and ensure it's in the project root.

### Database errors

Delete the database file and restart:

```bash
rm ownership_assistant.db
python -m app.main
```

## Need Help?

- Check the main [README.md](README.md)
- Review the API docs at `http://localhost:8000/docs`
- Explore the notebook in `notebooks/00_explore_data.ipynb`

