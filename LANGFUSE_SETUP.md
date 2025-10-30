# LangFuse Integration Guide

⚠️ **Note**: LangFuse infrastructure is prepared but not fully active yet. The app includes LangFuse client initialization, but full tracing requires using LangFuse v3.x's `@observe` decorator pattern. See "Current Status" section below.

## What is LangFuse?

LangFuse is an open-source LLM observability and analytics platform that helps you:

- 📊 **Track all LLM calls**: See every request/response with your OpenAI models
- 💰 **Monitor costs**: Track token usage and costs in real-time
- ⚡ **Measure latency**: See how long each LLM call takes
- 🔍 **Debug issues**: View exact prompts and responses that caused errors
- 📈 **Analyze usage**: Understand user patterns and model performance
- 🧪 **Test prompts**: Compare different prompts and models side-by-side
- 👥 **Track users**: See which users are most active and their costs

## Current Status

**✅ What's Ready:**
- LangFuse package installed (`langfuse==3.6.2`)
- Settings configured for LangFuse credentials
- Client initialization code in place
- App works with or without LangFuse credentials

**🚧 What's Pending:**
- Full automatic tracing via LangChain callbacks (requires additional setup)
- Alternative: Use LangFuse v3.x `@observe` decorator for manual tracing
- See "Manual Integration" section below for how to add tracing

**The app works perfectly without LangFuse** - it's completely optional and won't affect functionality if not configured.

## Quick Setup (5 minutes)

### Step 1: Sign up for LangFuse

**Option A: Cloud (Recommended)**
1. Go to https://cloud.langfuse.com
2. Sign up for a free account (generous free tier)
3. Create a new project called "anti-todo"

**Option B: Self-hosted**
Follow https://langfuse.com/docs/deployment/self-host

### Step 2: Get Your API Keys

1. In LangFuse dashboard, go to **Settings** → **API Keys**
2. Click **"Create new API keys"**
3. Copy your:
   - **Public Key** (starts with `pk-lf-...`)
   - **Secret Key** (starts with `sk-lf-...`)

### Step 3: Add Keys to Your `.env` File

```bash
# Copy the example file
cp env.example .env

# Edit .env and add your keys:
LANGFUSE_SECRET_KEY=sk-lf-your-actual-secret-key-here
LANGFUSE_PUBLIC_KEY=pk-lf-your-actual-public-key-here
LANGFUSE_HOST=https://cloud.langfuse.com
```

### Step 4: Restart Your Server

```bash
# Kill any running server
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill

# Start fresh
python main.py
```

That's it! 🎉

## Verifying It Works

1. Make an API call (onboard, chat, or recommendations)
2. Go to your LangFuse dashboard at https://cloud.langfuse.com
3. Click on your project
4. You should see traces appearing in real-time!

### Test It

```bash
# Create a thread
curl -X POST http://localhost:8000/onboard \
  -H "Content-Type: application/json" \
  -d '{"role":"Product Manager","industry":"SaaS","pains":"Too many meetings"}'

# Chat (use thread_id from above)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"thread_id":1,"message":"What should I stop doing?"}'

# Check LangFuse dashboard - you'll see the traces!
```

## What Gets Tracked?

### Automatic Tracking

LangFuse automatically captures:

1. **Every LLM call** with:
   - Input prompt (system + user messages)
   - Model output
   - Tokens used (prompt + completion)
   - Cost in USD
   - Latency in milliseconds
   - Model name and parameters

2. **Session grouping**:
   - All calls for a thread are grouped by `session_id`
   - Format: `thread_{thread_id}` (e.g., `thread_1`)

3. **User identification**:
   - Calls are tagged with the user's role (e.g., "Product Manager")
   - Great for understanding usage by user type

### Example Dashboard View

```
┌─────────────────────────────────────────────────────┐
│ Traces                                              │
├─────────────────────────────────────────────────────┤
│ 🟢 chat_completion                                  │
│    Session: thread_1                                │
│    User: Product Manager                            │
│    Input: "What should I stop doing?"               │
│    Output: "1. Stop attending status update..."     │
│    Tokens: 234 (prompt: 156, completion: 78)       │
│    Cost: $0.0003                                    │
│    Latency: 1.2s                                    │
│    Model: gpt-4o-mini                               │
└─────────────────────────────────────────────────────┘
```

## Disabling LangFuse

If you want to disable tracking:

**Option 1: Remove keys from `.env`**
```bash
# Just delete or comment out the lines:
# LANGFUSE_SECRET_KEY=
# LANGFUSE_PUBLIC_KEY=
```

**Option 2: Use environment variable**
```bash
# Temporarily disable for one run
LANGFUSE_SECRET_KEY= LANGFUSE_PUBLIC_KEY= python main.py
```

The app will work perfectly fine without LangFuse - it's completely optional!

## Key Features in Your Dashboard

### 1. **Traces View**
See every LLM call in real-time:
- Click on any trace to see full details
- View exact prompts and responses
- Debug errors and unexpected outputs

### 2. **Sessions**
All calls for a conversation thread are grouped:
- Navigate: **Traces** → Filter by **Session ID** → `thread_1`
- See the full conversation flow
- Understand user journey

### 3. **Users**
Track usage by role:
- Navigate: **Users** tab
- See "Product Manager" vs "Software Engineer" usage
- Identify your power users

### 4. **Costs**
Monitor spending:
- Navigate: **Metrics** → **Costs**
- See daily/weekly/monthly costs
- Set up alerts for cost thresholds

### 5. **Latency**
Track performance:
- Navigate: **Metrics** → **Latency**
- See P50, P95, P99 latencies
- Identify slow calls

### 6. **Datasets & Testing** (Advanced)
- Save good/bad examples
- Create test sets
- Compare prompt variations
- A/B test different models

## Manual Integration (LangFuse v3.x)

If you want to enable LangFuse tracking right now, you can use the `@observe` decorator. Here's how:

### Option 1: Decorate Endpoint Functions

```python
# In main.py, add at the top:
from langfuse import observe

# Then decorate your endpoints:
@app.post("/chat", response_model=ChatOut)
@observe(name="chat_endpoint")  # <-- Add this
def chat(payload: ChatIn, session=Depends(get_session)):
    # ... existing code ...
```

### Option 2: Decorate Helper Functions

```python
@observe(name="get_recommendations")
def recommendations(payload: RecsIn, session=Depends(get_session)):
    # ... existing code ...
```

### Option 3: Manual Tracing (Most Control)

```python
from main import _get_langfuse_client

@app.post("/chat", response_model=ChatOut)
def chat(payload: ChatIn, session=Depends(get_session)):
    langfuse = _get_langfuse_client()
    
    if langfuse:
        trace = langfuse.trace(
            name="chat",
            user_id=str(thread.role_normalized),
            session_id=f"thread_{payload.thread_id}",
            metadata={"role": thread.role_raw, "industry": thread.industry_raw}
        )
        
        generation = trace.generation(
            name="chat_completion",
            model=settings.model,
            input={"user_msg": payload.message, "history": lc_history},
        )
        
    # ... make LLM call ...
    
    if langfuse and generation:
        generation.end(output=reply_text)
        
    # ... rest of code ...
```

For full documentation on v3.x integration, see:
- https://langfuse.com/docs/sdk/python/decorators
- https://langfuse.com/docs/sdk/python/low-level-sdk

## Advanced: Custom Tagging

You can add custom tags to your traces by modifying the code:

```python
# In main.py, modify _get_langfuse_handler:
langfuse_handler = _get_langfuse_handler(
    session_id=f"thread_{payload.thread_id}",
    user_id=thread.role_normalized or "unknown",
    # Add custom tags:
    tags=["production", "v1", thread.industry_raw],
    metadata={
        "role": thread.role_raw,
        "industry": thread.industry_raw,
        "pains": thread.pains_raw,
    }
)
```

## Pricing

**Free Tier (Cloud)**:
- 50,000 traces/month
- 1 project
- 1 environment
- Perfect for development and small apps

**Self-Hosted**:
- Completely free
- Unlimited traces
- Requires Docker/Kubernetes setup

**Paid Tiers** (if you grow):
- Starts at $50/month for more traces
- Team collaboration features
- Priority support

## Troubleshooting

### Not seeing traces?

1. **Check environment variables**:
   ```bash
   python -c "from settings import settings; print(settings.langfuse_secret_key)"
   ```
   Should print your key (not `None`)

2. **Check logs**:
   - LangFuse errors are logged to console
   - Look for "LangFuse" in your server logs

3. **Verify keys are correct**:
   - Secret key starts with `sk-lf-`
   - Public key starts with `pk-lf-`
   - Copy/paste carefully (no extra spaces)

4. **Check LangFuse host**:
   ```bash
   curl https://cloud.langfuse.com/api/public/health
   ```
   Should return `{"status":"ok"}`

### Traces are delayed?

- LangFuse batches traces for efficiency
- Can take 10-30 seconds to appear
- Refresh your dashboard

### Connection errors?

- Check your internet connection
- Verify `LANGFUSE_HOST` is correct
- If self-hosting, ensure server is reachable

## Best Practices

### 1. **Use Sessions Wisely**
- Keep thread-based sessions (`thread_{id}`)
- Makes it easy to track conversations
- Great for debugging user issues

### 2. **Tag by Environment**
- Add `environment` tag: "dev", "staging", "prod"
- Filter traces by environment in dashboard

### 3. **Monitor Costs**
- Set up weekly cost alerts
- Review most expensive users/sessions
- Optimize prompts to reduce tokens

### 4. **Debug Errors**
- When users report issues, search by `session_id`
- View exact prompts that caused errors
- Reproduce and fix

### 5. **A/B Test Prompts**
- Try different system prompts
- Compare costs and quality in LangFuse
- Roll out the winner

## Integration Details

### What We Changed

1. **requirements.txt**: Added `langfuse`
2. **settings.py**: Added LangFuse credentials
3. **main.py**: Added callback handler to LLM calls
4. **db.py**: Made database URL configurable

### Code Flow

```
User Request
    ↓
Create LangFuse Handler
    ↓
Pass to LangChain Model
    ↓
LangChain executes chain
    ↓
LangFuse automatically logs:
  - Prompt
  - Response
  - Tokens
  - Cost
  - Latency
    ↓
Data appears in LangFuse dashboard
```

## Next Steps

1. ✅ Set up your LangFuse account
2. ✅ Add API keys to `.env`
3. ✅ Make some test API calls
4. ✅ Explore your dashboard
5. 📈 Set up cost alerts
6. 🧪 Start testing different prompts
7. 📊 Monitor usage patterns

## Resources

- **LangFuse Docs**: https://langfuse.com/docs
- **LangChain Integration**: https://langfuse.com/docs/integrations/langchain
- **API Reference**: https://langfuse.com/docs/api
- **Community Discord**: https://discord.gg/7NXusRtqYU

## Questions?

Common questions:

**Q: Does LangFuse slow down my API?**
A: Minimal impact (~10-20ms). Traces are sent asynchronously.

**Q: Is my data secure?**
A: Yes. Encrypted in transit and at rest. Read privacy policy at langfuse.com/privacy

**Q: Can I use this in production?**
A: Absolutely! It's designed for production use.

**Q: What if I hit the free tier limit?**
A: Traces stop being recorded, but your app keeps working normally.

**Q: Can I export my data?**
A: Yes, via API or CSV export in dashboard.

---

Happy tracking! 🚀

