# Anti-To-Do Backend API

A FastAPI-based backend service that provides AI-powered productivity recommendations using LangChain and OpenAI.

## Overview

This application helps users identify tasks they should **stop doing** rather than adding more to their plate. It uses LangChain to integrate with OpenAI's models to provide personalized recommendations based on user role, industry, and pain points.

## Getting Started

### Prerequisites

- Python 3.9+
- Virtual environment (`venv_a2d/`)
- OpenAI API key (set in environment variables)

### Installation

1. Activate the virtual environment:
```bash
source venv_a2d/bin/activate
```

2. Install dependencies (if needed):
```bash
pip install -r requirements.txt
```

### Running the Server

**Option 1: Run directly with Python**
```bash
python main.py
```

**Option 2: Run with uvicorn (recommended for development)**
```bash
uvicorn main:app --reload
```

The server will start on `http://localhost:8000`

### Stopping the Server

If you need to stop a running server:

1. **Find the process using port 8000:**
```bash
lsof -i :8000
```

2. **Kill the process by PID:**
```bash
kill <PID>
```

Or kill all Python processes running main.py:
```bash
pkill -f "python.*main.py"
```

## API Documentation

Once the server is running, you can access:

- **Interactive API docs**: http://localhost:8000/docs (Swagger UI)
- **Alternative docs**: http://localhost:8000/redoc
- **Health check**: http://localhost:8000/health

## API Endpoints

### 1. Health Check
**GET** `/health`

Simple endpoint to verify the server is running.

**Response:**
```json
{
  "status": "ok"
}
```

### 2. Onboard User
**POST** `/onboard`

Create a new session thread for a user. **This must be called first** before using other endpoints.

**Request Body:**
```json
{
  "role": "Product Manager",
  "industry": "SaaS",
  "pains": "Too many meetings, context switching, unclear priorities"
}
```

**Response:**
```json
{
  "thread_id": 1,
  "role_normalized": "Product Manager",
  "onet_code": null
}
```

**Note:** Save the `thread_id` - you'll need it for subsequent requests.

### 3. Get Recommendations
**POST** `/recommendations`

Get AI-powered recommendations for what the user should stop doing.

**Request Body:**
```json
{
  "thread_id": 1
}
```

**Response:**
```json
{
  "thread_id": 1,
  "items": [
    {
      "item": "Stop attending status update meetings",
      "rationale": "Use async updates via Slack instead",
      "category": "meetings",
      "estimated_gain_minutes": 120,
      "difficulty": "medium"
    },
    // ... more recommendations
  ]
}
```

### 4. Chat with Assistant
**POST** `/chat`

Have a conversation with the Anti-To-Do assistant. The chat maintains history within the thread.

**Request Body:**
```json
{
  "thread_id": 1,
  "message": "What are some ways I can reduce meeting time?"
}
```

**Response:**
```json
{
  "thread_id": 1,
  "reply": "1. Set clear agendas: Share a focused agenda before each meeting.\n2. Limit participants: Invite only essential stakeholders.\n..."
}
```

## Workflow Example

Here's the typical flow for using the API:

```bash
# 1. Create a session thread
curl -X POST http://localhost:8000/onboard \
  -H "Content-Type: application/json" \
  -d '{
    "role": "Product Manager",
    "industry": "SaaS",
    "pains": "Too many meetings, context switching"
  }'
# Response: {"thread_id": 1, ...}

# 2. Get recommendations
curl -X POST http://localhost:8000/recommendations \
  -H "Content-Type: application/json" \
  -d '{"thread_id": 1}'

# 3. Chat with the assistant
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "thread_id": 1,
    "message": "How can I reduce context switching?"
  }'
```

## Troubleshooting

### "Address already in use" error

**Problem:** You see `ERROR: [Errno 48] error while attempting to bind on address ('0.0.0.0', 8000): address already in use`

**Solution:** An old server instance is still running. Kill it:
```bash
lsof -i :8000
kill <PID_from_above_command>
```

### "Thread not found" error

**Problem:** Getting 404 error when calling `/chat` or `/recommendations`

**Solution:** You need to call `/onboard` first to create a session thread, then use the returned `thread_id`.

### Database issues

The application uses SQLite (`anti_todo.db`). If you need to reset the database:
```bash
rm anti_todo.db
# The database will be recreated on next server start
```

## Architecture

### Tech Stack
- **FastAPI**: Web framework
- **LangChain**: LLM orchestration
- **OpenAI**: Language model (GPT-4o-mini)
- **SQLModel**: Database ORM
- **SQLite**: Database

### Key Components
- `main.py`: FastAPI application and routes
- `models.py`: Database models (SessionThread, ChatMessage, Recommendation)
- `db.py`: Database initialization and session management
- `prompts.py`: LLM prompt templates
- `settings.py`: Configuration and environment variables
- `chat_terminal.py`: Interactive terminal client for testing the API

### LangChain Integration

The application uses LangChain for:
- **Structured output**: JsonOutputParser ensures consistent JSON responses
- **Chat history**: MessagesPlaceholder maintains conversation context
- **Prompt templates**: Reusable, testable prompt structures
- **Model abstraction**: Easy to swap between different LLM providers

## Known Warnings

### urllib3 OpenSSL Warning
```
NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+
```
This is a compatibility notice and won't affect functionality. The system is using LibreSSL instead of OpenSSL.

### FastAPI Deprecation Warning
```
DeprecationWarning: on_event is deprecated, use lifespan event handlers instead
```
The `@app.on_event("startup")` decorator is deprecated in newer FastAPI versions. This will be migrated to lifespan handlers in a future update.

## Development

### Environment Variables
Set in `settings.py` or `.env` file:
- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `MODEL`: Model name (default: "gpt-4o-mini")
- `DATABASE_URL`: Database connection string (default: "sqlite:///anti_todo.db")
- `LANGFUSE_SECRET_KEY`: LangFuse secret key (optional - for observability)
- `LANGFUSE_PUBLIC_KEY`: LangFuse public key (optional - for observability)
- `LANGFUSE_HOST`: LangFuse host URL (default: "https://cloud.langfuse.com")

Copy `env.example` to `.env` and fill in your values:
```bash
cp env.example .env
# Edit .env with your API keys
```

### LangFuse Integration (Optional)

This app includes **LangFuse** integration for LLM observability - track costs, latency, and debug prompts in real-time.

**To enable LangFuse:**
1. Sign up at https://cloud.langfuse.com (free tier available)
2. Get your API keys from Settings → API Keys
3. Add them to your `.env` file
4. Restart the server

**To disable LangFuse:**
- Just leave the `LANGFUSE_*` variables empty or remove them from `.env`
- The app works perfectly without LangFuse

See **[LANGFUSE_SETUP.md](LANGFUSE_SETUP.md)** for detailed setup instructions and features.

### Database Schema
- **SessionThread**: Stores user onboarding info and session state
- **ChatMessage**: Stores conversation history
- **Recommendation**: Stores generated anti-todo recommendations

### Inspecting the Database

The application uses SQLite, stored in `anti_todo.db`. Here are several ways to view it:

**Option 1: SQLite Command Line (Quick)**

```bash
# Show all tables
sqlite3 anti_todo.db ".tables"

# View all session threads
sqlite3 anti_todo.db "SELECT * FROM sessionthread;"

# View chat messages (formatted)
sqlite3 anti_todo.db -header -column "SELECT id, thread_id, sender, substr(content, 1, 50) as content_preview FROM chatmessage ORDER BY created_at;"

# View recommendations
sqlite3 anti_todo.db -header -column "SELECT * FROM recommendation;"

# Interactive mode (type .quit to exit)
sqlite3 anti_todo.db
```

**Option 2: Python Script**

```bash
python -c "
from db import get_session
from models import SessionThread, ChatMessage, Recommendation
from sqlmodel import select

session = next(get_session())

# View threads
threads = session.exec(select(SessionThread)).all()
for t in threads:
    print(f'Thread {t.id}: {t.role_normalized} in {t.industry_raw}')

# View messages
messages = session.exec(select(ChatMessage)).all()
for m in messages:
    print(f'{m.sender}: {m.content[:50]}...')
"
```

**Option 3: GUI Tools**

- **DB Browser for SQLite**: https://sqlitebrowser.org/ (Free, cross-platform)
- **VS Code Extension**: Install "SQLite Viewer" or "SQLite" extension
- **TablePlus**: https://tableplus.com/ (Free tier available)

Just open `anti_todo.db` in any of these tools to browse the data visually.

**Option 4: Interactive SQLite Shell**

```bash
sqlite3 anti_todo.db

# Then use these commands:
.tables                    # Show all tables
.schema sessionthread      # Show table structure
.headers on                # Show column headers
.mode column              # Format output in columns
SELECT * FROM sessionthread;
.quit                      # Exit
```

## License

[Add your license here]

## Contributors

[Add contributors here]

