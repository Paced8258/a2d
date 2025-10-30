#!/usr/bin/env python3
"""
Interactive terminal chat with your Anti-To-Do API
Perfect for prompt testing and iteration!
"""

import requests
import json
import sys
from typing import Optional

# Configuration
API_BASE = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}

class AntiToDoChat:
    def __init__(self):
        self.thread_id: Optional[int] = None
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
    
    def create_session(self, role: str = "Product Manager", industry: str = "SaaS", pains: str = "Too many meetings"):
        """Create a new chat session"""
        payload = {
            "role": role,
            "industry": industry,
            "pains": pains
        }
        
        try:
            response = self.session.post(f"{API_BASE}/onboard", json=payload)
            response.raise_for_status()
            data = response.json()
            self.thread_id = data["thread_id"]
            print(f"✅ Created session (Thread ID: {self.thread_id})")
            print(f"   Role: {role}")
            print(f"   Industry: {industry}")
            print(f"   Pains: {pains}")
            return True
        except Exception as e:
            print(f"❌ Failed to create session: {e}")
            return False
    
    def send_message(self, message: str) -> str:
        """Send a message and get response"""
        if not self.thread_id:
            print("❌ No active session. Create one first with /session")
            return ""
        
        payload = {
            "thread_id": self.thread_id,
            "message": message
        }
        
        try:
            response = self.session.post(f"{API_BASE}/chat", json=payload)
            response.raise_for_status()
            data = response.json()
            return data["reply"]
        except Exception as e:
            print(f"❌ Failed to send message: {e}")
            return ""
    
    def get_recommendations(self) -> str:
        """Get AI recommendations"""
        if not self.thread_id:
            print("❌ No active session. Create one first with /session")
            return ""
        
        payload = {"thread_id": self.thread_id}
        
        try:
            response = self.session.post(f"{API_BASE}/recommendations", json=payload)
            response.raise_for_status()
            data = response.json()
            
            # Format recommendations nicely
            result = "🎯 AI Recommendations:\n\n"
            for i, item in enumerate(data["items"], 1):
                result += f"{i}. {item['item']}\n"
                result += f"   💡 Rationale: {item['rationale']}\n"
                result += f"   ⏱️  Time saved: {item['estimated_gain_minutes']} minutes\n"
                result += f"   📊 Difficulty: {item['difficulty']}\n\n"
            
            return result
        except Exception as e:
            print(f"❌ Failed to get recommendations: {e}")
            return ""
    
    def run(self):
        """Main chat loop"""
        print("🤖 Anti-To-Do Chat Terminal")
        print("=" * 50)
        print("Commands:")
        print("  /session [role] [industry] [pains] - Create new session")
        print("  /recs - Get AI recommendations")
        print("  /help - Show this help")
        print("  /quit - Exit")
        print("  /clear - Clear screen")
        print()
        print("Or just type a message to chat!")
        print()
        
        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.startswith("/"):
                    self.handle_command(user_input)
                    continue
                
                # Send message
                print("🤖 Assistant: ", end="", flush=True)
                response = self.send_message(user_input)
                if response:
                    print(response)
                print()
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except EOFError:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def handle_command(self, command: str):
        """Handle special commands"""
        parts = command.split()
        cmd = parts[0].lower()
        
        if cmd == "/quit" or cmd == "/exit":
            print("👋 Goodbye!")
            sys.exit(0)
        
        elif cmd == "/clear":
            import os
            os.system('clear' if os.name == 'posix' else 'cls')
        
        elif cmd == "/help":
            print("\n🤖 Anti-To-Do Chat Commands:")
            print("  /session [role] [industry] [pains] - Create new session")
            print("  /recs - Get AI recommendations")
            print("  /help - Show this help")
            print("  /quit - Exit")
            print("  /clear - Clear screen")
            print("  Just type a message to chat!")
            print()
        
        elif cmd == "/session":
            # Parse session parameters
            role = parts[1] if len(parts) > 1 else "Product Manager"
            industry = parts[2] if len(parts) > 2 else "SaaS"
            pains = " ".join(parts[3:]) if len(parts) > 3 else "Too many meetings"
            
            self.create_session(role, industry, pains)
            print()
        
        elif cmd == "/recs":
            print("🎯 Getting recommendations...")
            recs = self.get_recommendations()
            if recs:
                print(recs)
            print()
        
        else:
            print(f"❌ Unknown command: {cmd}")
            print("Type /help for available commands")

def check_server():
    """Check if the API server is running"""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def main():
    print("🔍 Checking if API server is running...")
    
    if not check_server():
        print("❌ API server is not running!")
        print("Please start your server first:")
        print("  python main.py")
        sys.exit(1)
    
    print("✅ API server is running!")
    print()
    
    # Start chat
    chat = AntiToDoChat()
    chat.run()

if __name__ == "__main__":
    main()
