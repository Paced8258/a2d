# LangFuse Quick Test Guide

🎉 **LangFuse tracing is now fully integrated!**

## What's Active

✅ `@observe` decorators on `/chat` and `/recommendations` endpoints
✅ Automatic user/session tracking
✅ Metadata capture (role, industry, pains)
✅ Works with or without LangFuse credentials

## How to Enable (3 Steps)

### Step 1: Get LangFuse Account (2 minutes)

1. Go to https://cloud.langfuse.com
2. Sign up (free tier: 50k traces/month)
3. Create a project (e.g., "anti-todo")
4. Go to **Settings** → **API Keys**
5. Click **"Create new API keys"**
6. Copy both keys

### Step 2: Add Keys to .env

Create/edit your `.env` file:

```bash
# Required
OPENAI_API_KEY=sk-your-openai-key-here

# Optional (leave commented to disable)
LANGFUSE_SECRET_KEY=sk-lf-your-secret-key-here
LANGFUSE_PUBLIC_KEY=pk-lf-your-public-key-here
LANGFUSE_HOST=https://cloud.langfuse.com
```

### Step 3: Restart Server

```bash
# Kill old server if running
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill 2>/dev/null

# Start server
python main.py
```

You should see:
```
✅ LangFuse initialized: https://cloud.langfuse.com
```

## Testing the Integration

### 1. Make API Calls

```bash
# Create a thread
curl -X POST http://localhost:8000/onboard \
  -H "Content-Type: application/json" \
  -d '{
    "role": "Product Manager",
    "industry": "SaaS",
    "pains": "Too many meetings, context switching"
  }'

# Get recommendations (replace thread_id with the one from above)
curl -X POST http://localhost:8000/recommendations \
  -H "Content-Type: application/json" \
  -d '{"thread_id": 1}'

# Chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "thread_id": 1,
    "message": "How can I reduce context switching?"
  }'
```

### 2. View in LangFuse Dashboard

1. Go to https://cloud.langfuse.com
2. Open your project
3. Click **"Traces"** in sidebar
4. You should see your API calls! 🎉

### What You'll See

```
┌─────────────────────────────────────────────────────────────┐
│ Trace: chat_endpoint                                        │
├─────────────────────────────────────────────────────────────┤
│ User: Product Manager                                       │
│ Session: thread_1                                           │
│ Metadata:                                                   │
│   - role: Product Manager                                   │
│   - industry: SaaS                                          │
│                                                             │
│ Input: "How can I reduce context switching?"                │
│ Output: "1. Batch similar tasks together..."               │
│                                                             │
│ Tokens: 234 (prompt: 156, completion: 78)                  │
│ Cost: $0.0003                                               │
│ Latency: 1.2s                                               │
│ Model: gpt-4o-mini                                          │
└─────────────────────────────────────────────────────────────┘
```

## What Gets Tracked Automatically

### For `/chat` endpoint:
- ✅ User message
- ✅ AI response
- ✅ Conversation history
- ✅ User role (Product Manager, etc.)
- ✅ Session ID (thread_1, thread_2, etc.)
- ✅ Industry metadata
- ✅ Token usage & cost
- ✅ Response time

### For `/recommendations` endpoint:
- ✅ User context (role, industry, pains)
- ✅ Generated recommendations
- ✅ Session grouping
- ✅ Token usage & cost
- ✅ Response time

## Troubleshooting

### "No traces appearing"

**Check 1: Verify credentials**
```bash
python -c "from settings import settings; print(f'Secret: {settings.langfuse_secret_key[:10]}...' if settings.langfuse_secret_key else 'NOT SET')"
```

**Check 2: Server logs**
Look for this when server starts:
```
✅ LangFuse initialized: https://cloud.langfuse.com
```

If you see:
```
ℹ️  LangFuse not configured (optional)
```
Your credentials aren't loaded. Check your `.env` file.

**Check 3: Trace delay**
- Traces can take 10-30 seconds to appear
- Refresh your LangFuse dashboard

**Check 4: Environment variables**
```bash
# In your activated venv:
python -c "
from settings import settings
print(f'LangFuse Secret: {bool(settings.langfuse_secret_key)}')
print(f'LangFuse Public: {bool(settings.langfuse_public_key)}')
"
```

### "Import errors"

Make sure langfuse is installed:
```bash
pip install langfuse
```

### "Still not working"

The app works fine without LangFuse! Just use it normally and add observability later.

## Without LangFuse Credentials

If you don't add credentials, the app works normally:
- ✅ All endpoints work
- ✅ No errors
- ✅ No tracking (privacy-first!)
- ✅ Zero overhead

The `@observe` decorators become no-ops and don't affect performance.

## Dashboard Features to Explore

### 1. **Traces** (Main View)
- See all API calls in real-time
- Click any trace for full details
- Filter by user, session, or date

### 2. **Sessions**
- Group by `thread_1`, `thread_2`, etc.
- See full conversation flow
- Track user journey

### 3. **Users**
- See usage by role (Product Manager, Engineer, etc.)
- Identify power users
- Track costs per user type

### 4. **Metrics**
- **Costs**: Daily/weekly/monthly spending
- **Latency**: P50, P95, P99 response times
- **Volume**: Traces per day

### 5. **Datasets** (Advanced)
- Save example conversations
- Build test sets
- Regression testing

## Cost Tracking

LangFuse automatically calculates OpenAI costs:

| Model | Cost per 1K tokens |
|-------|-------------------|
| gpt-4o-mini (input) | $0.00015 |
| gpt-4o-mini (output) | $0.0006 |

You'll see exact costs for each call and totals over time!

## Next Steps

1. ✅ Set up LangFuse account
2. ✅ Add credentials to `.env`
3. ✅ Make some test calls
4. ✅ View traces in dashboard
5. 📊 Set up cost alerts (Settings → Alerts)
6. 🧪 Create test datasets for regression testing
7. 📈 Monitor usage patterns

## Advanced: More Tracking

Want to track more? Add `@observe` to other functions:

```python
@observe(name="build_prompt")
def build_recommendations_prompt(...):
    # Your code
    return prompt

@observe(name="parse_response")
def parse_llm_response(data):
    # Your code
    return parsed
```

Every function decorated with `@observe` becomes a "span" in your trace!

## Support

- **Docs**: https://langfuse.com/docs
- **Discord**: https://discord.gg/7NXusRtqYU
- **Examples**: https://langfuse.com/docs/sdk/python/example

---

Happy tracking! 🚀

**Remember**: LangFuse is optional. Your app works perfectly without it!


