# 💬 Interactive Chat Guide

## Quick Start

### Interactive Chat Terminal
```bash
python chat_terminal.py
```

**Features:**
- Create custom sessions with different roles
- Full chat interface with recommendations
- Perfect for exploring different user types and testing

**Commands:**
- `/session [role] [industry] [pains]` - Create new session
- `/recs` - Get AI recommendations
- `/help` - Show all commands
- `/clear` - Clear screen
- `/quit` - Exit
- Just type a message to chat

## Example Usage

### Chat Session with Custom Role
```bash
$ python chat_terminal.py

🤖 Anti-To-Do Chat Terminal
==================================================
Commands:
  /session [role] [industry] [pains] - Create new session
  /recs - Get AI recommendations
  /help - Show this help
  /quit - Exit

You: /session Designer E-commerce "Client feedback loops"
✅ Created session (Thread ID: 6)
   Role: Designer
   Industry: E-commerce
   Pains: Client feedback loops

You: How can I reduce time spent on revisions?
🤖 Assistant: Stop incorporating every piece of client feedback...

You: /recs
🎯 AI Recommendations:

🎨 Design & Creation
-------------------
  1. Stop creating custom mockups for every client request
     💡 Designers waste hours on one-off mockups...
```

## Tips for Prompt Testing

### 1. Test Different User Types
```bash
# In chat_terminal.py
/session "Software Engineer" "Fintech" "Code reviews, deployment"
/session "Sales Manager" "B2B SaaS" "Reporting, follow-ups"
/session "Operations Lead" "Manufacturing" "Manual processes"
```

### 2. Iterate on Responses
- Ask the same question multiple times
- Tweak wording to see how responses change
- Test edge cases

### 3. Check Recommendation Quality
- Type `recs` or `/recs` frequently
- Check if categories make sense for the role
- Verify rationales are specific, not generic

### 4. Monitor LangFuse
- Every conversation is tracked in LangFuse
- Check costs, latency, and quality
- Compare different prompt approaches

## Troubleshooting

### "API server is not running"
```bash
# Start the server first
python main.py

# In another terminal, run chat
python chat_terminal.py
```

### Chat Freezes or Loops
- Press `Ctrl+C` to exit
- The EOFError is now handled, so it should exit gracefully

### "Thread not found"
- The chat scripts auto-create sessions
- If you see this, restart the chat script

### Strange Characters or Formatting
- Your terminal might not support emojis
- Set `LANG=en_US.UTF-8` in your shell

## API Endpoint Testing (Alternative)

If you prefer direct API testing without the chat interface:

```bash
# Create session
curl -X POST http://localhost:8000/onboard \
  -H "Content-Type: application/json" \
  -d '{"role":"PM","industry":"Tech","pains":"Meetings"}'

# Response: {"thread_id":1,"role_normalized":"Product Manager","onet_code":null}

# Chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"thread_id":1,"message":"What should I stop doing?"}'

# Get recommendations
curl -X POST http://localhost:8000/recommendations \
  -H "Content-Type: application/json" \
  -d '{"thread_id":1}'
```

## Development Workflow

### Recommended Iteration Cycle

1. **Start Server**
   ```bash
   python main.py
   ```

2. **Open LangFuse Dashboard**
   - Go to https://cloud.langfuse.com
   - Keep it open in a browser tab

3. **Start Chat**
   ```bash
   python chat_terminal.py
   ```

4. **Test & Iterate**
   - Have conversations
   - Request recommendations
   - Check LangFuse for traces

5. **Refine Prompts**
   - Edit `prompts.py` based on results
   - Restart server (Ctrl+C, then `python main.py`)
   - Test again

6. **Repeat**

### Fast Iteration Tips

- Keep `prompts.py` open in your editor
- Use `chat_terminal.py` for quick testing
- Check LangFuse after every major change
- Test same questions before/after prompt changes

## Next Steps

Once your prompts are refined:
1. Add more categories to `prompts.py`
2. Enhance few-shot examples
3. Fine-tune rationale generation
4. Test with real user profiles
5. Build a frontend! 🎨



