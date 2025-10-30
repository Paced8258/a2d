# Structure Comparison: a2d vs ownership_assistant

Both projects now use the same flat structure and patterns.

## File Structure

### a2d (Anti-To-Do Backend)
```
a2d/
├── main.py           # FastAPI app
├── models.py         # Database models
├── db.py             # Database init
├── prompts.py        # LLM prompts
├── settings.py       # Config
├── requirements.txt  # Dependencies
└── ...
```

### ownership_assistant
```
ownership_assistant/
├── main.py           # FastAPI app
├── models.py         # Database models
├── db.py             # Database init
├── prompts.py        # LLM prompts
├── settings.py       # Config
├── requirements.txt  # Dependencies
└── ...
```

## Common Patterns

### 1. Imports
Both use direct imports:
```python
from db import init_db, get_session
from models import SessionThread, ChatMessage, Recommendation
from settings import settings
from prompts import build_recommendations_prompt
```

### 2. LangChain Setup
Both use same LangChain pattern:
```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnablePassthrough
```

### 3. LangFuse Integration
Both use optional LangFuse:
```python
try:
    from langfuse import Langfuse
    from langfuse.langchain import CallbackHandler
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
```

### 4. Settings
Both use pydantic_settings:
```python
from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    openai_api_key: str
    model: str = "gpt-4o-mini"
    # ...
```

### 5. Database
Both use SQLModel with same pattern:
```python
from sqlmodel import SQLModel, create_engine, Session
engine = create_engine(settings.database_url, echo=False)
```

### 6. Prompt Building
Both build prompts similarly:
```python
def build_prompt(**kwargs):
    return {
        "system": SYSTEM_PROMPT,
        "instructions": INSTRUCTIONS,
        "context": ...,
        ...
    }
```

### 7. Chain Building
Both build LangChain chains the same way:
```python
chain = (
    {"payload": RunnablePassthrough()}
    | prompt
    | _get_lc_model(callbacks=callbacks)
    | parser
)
```

## Key Differences

| Aspect | a2d | ownership_assistant |
|--------|-----|---------------------|
| Purpose | Anti-To-Do recommendations | Ownership resolution |
| Port | 8000 | 8001 |
| Database | anti_todo.db | ownership_assistant.db |
| Models | SessionThread, ChatMessage, Recommendation | SupportTicket, Owner, ProductArea, Ownership |
| Endpoints | /onboard, /recommendations, /chat | /query, /ingest |
| Complexity | Full chat history | Query-response |

## Benefits of Matching Structure

1. **Easy to Learn**: Same patterns across projects
2. **Code Reuse**: Similar functions and helpers
3. **Consistency**: Same import style and organization
4. **Maintainability**: Easier to maintain parallel projects

## Example Comparison

### a2d: Building recommendations chain
```python
def _build_recommendations_chain(prompt_blob: dict, callbacks=None):
    # ... same pattern as ownership
```

### ownership_assistant: Building ownership chain
```python
def _build_ownership_chain(prompt_blob: dict, callbacks=None):
    # ... same pattern as a2d
```

Both follow identical structure!

