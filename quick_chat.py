#!/usr/bin/env python3
"""
Quick chat script for testing prompts
Usage: python quick_chat.py
"""

import requests
import json

API_BASE = "http://localhost:8000"

def create_session():
    """Create a new session"""
    payload = {
        "role": "Product Manager",
        "industry": "SaaS", 
        "pains": "Too many meetings, context switching"
    }
    
    response = requests.post(f"{API_BASE}/onboard", json=payload)
    data = response.json()
    thread_id = data["thread_id"]
    print(f"✅ Created session: Thread {thread_id}")
    return thread_id

def chat(thread_id, message):
    """Send a message"""
    payload = {
        "thread_id": thread_id,
        "message": message
    }
    
    response = requests.post(f"{API_BASE}/chat", json=payload)
    data = response.json()
    return data["reply"]

def get_recs(thread_id):
    """Get recommendations"""
    payload = {"thread_id": thread_id}
    response = requests.post(f"{API_BASE}/recommendations", json=payload)
    data = response.json()
    
    print("\n🎯 Recommendations:")
    
    # Handle structured format by category
    if "categories" in data:
        for category in data["categories"]:
            category_name = category.get("category_name", "General")
            emoji = category.get("emoji", "📋")
            items = category.get("items", [])
            
            print(f"\n{emoji} {category_name}")
            print("-" * (len(category_name) + 3))
            
            for i, item in enumerate(items, 1):
                print(f"  {i}. {item['item']}")
                print(f"     💡 {item.get('rationale', 'No rationale provided')}")
                print(f"     ⏱️  {item.get('estimated_gain_minutes', 0)} min saved, {item.get('difficulty', 'medium')} difficulty")
                print()
    else:
        # Fallback to old format
        for i, item in enumerate(data["items"], 1):
            print(f"{i}. {item['item']}")
            print(f"   💡 {item.get('rationale', 'No rationale provided')}")
            print(f"   ⏱️  {item.get('estimated_gain_minutes', 0)} min saved, {item.get('difficulty', 'medium')} difficulty")
            print()

def main():
    print("🤖 Quick Chat - Anti-To-Do Assistant")
    print("=" * 40)
    
    # Create session
    thread_id = create_session()
    
    print("\n💬 Chat started! Type messages (or 'recs' for recommendations, 'quit' to exit)")
    print()
    
    while True:
        try:
            message = input("You: ").strip()
            
            if message.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if message.lower() == 'recs':
                get_recs(thread_id)
                continue
            
            if not message:
                continue
            
            print("🤖 Assistant: ", end="", flush=True)
            response = chat(thread_id, message)
            print(response)
            print()
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except EOFError:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
