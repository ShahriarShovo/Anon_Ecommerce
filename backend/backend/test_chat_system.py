#!/usr/bin/env python
"""
Test script for chat system
Tests customer to admin messaging and admin reply functionality
"""

import requests
import json
import time
from datetime import datetime

# Base URL
BASE_URL = "http://127.0.0.1:8000"

def get_auth_token(email, password):
    """Get authentication token for user"""
    url = f"{BASE_URL}/api/accounts/login/"
    data = {
        "email": email,
        "password": password
    }
    
    response = requests.post(url, json=data)
    print(f"Login response for {email}: {response.status_code}")
    print(f"Response text: {response.text}")
    
    if response.status_code == 200:
        response_data = response.json()
        token_data = response_data.get('token', {})
        access_token = token_data.get('access')
        if access_token:
            print(f"✅ Access token received: {access_token[:20]}...")
            return access_token
        else:
            print(f"❌ No access token in response: {response_data}")
            return None
    else:
        print(f"❌ Login failed for {email}: {response.text}")
        return None

def create_conversation(token):
    """Create a new conversation as customer"""
    url = f"{BASE_URL}/api/chat/conversations/"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "status": "open"
    }
    
    response = requests.post(url, json=data, headers=headers)
    print(f"Create conversation response: {response.status_code}")
    print(f"Response text: {response.text}")
    
    if response.status_code == 201:
        conversation = response.json()
        print(f"✅ Conversation created: {conversation}")
        return conversation.get('id')
    else:
        print(f"❌ Failed to create conversation: {response.text}")
        return None

def send_message(token, conversation_id, message):
    """Send message to conversation"""
    url = f"{BASE_URL}/api/chat/messages/"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "conversation": conversation_id,
        "content": message,
        "message_type": "text"
    }
    
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 201:

        return True
    else:
        print(f"❌ Failed to send message: {response.text}")
        return False

def get_messages(token, conversation_id):
    """Get messages from conversation"""
    url = f"{BASE_URL}/api/chat/messages/"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"conversation": conversation_id}
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        messages = response.json()

        for msg in messages:
            sender = msg.get('sender_name') or msg.get('sender_email', 'Unknown')
            print(f"  {sender}: {msg.get('content', 'N/A')} ({msg.get('created_at', 'N/A')})")
        return messages
    else:
        print(f"❌ Failed to get messages: {response.text}")
        return []

def get_inbox(token):
    """Get admin inbox"""
    url = f"{BASE_URL}/api/chat/inbox/"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        conversations = response.json()
        print(f"📥 Admin inbox has {len(conversations)} conversations")
        for conv in conversations:
            customer_name = conv.get('customer_name', conv.get('customer_email', 'Unknown'))
            print(f"  Conversation {conv.get('id', 'N/A')}: {customer_name} - {conv.get('status', 'N/A')}")
        return conversations
    else:
        print(f"❌ Failed to get inbox: {response.text}")
        return []

def assign_conversation(token, conversation_id, staff_id):
    """Assign conversation to staff"""
    url = f"{BASE_URL}/api/chat/conversations/{conversation_id}/assign/"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"staff_id": staff_id}
    
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        print(f"✅ Conversation {conversation_id} assigned to staff {staff_id}")
        return True
    else:
        print(f"❌ Failed to assign conversation: {response.text}")
        return False

def main():
    print("🚀 Starting Chat System Test")
    print("=" * 50)
    
    # Step 1: Customer login
    print("\n1️⃣ Customer Login...")
    customer_token = get_auth_token("customer@example.com", "password123")
    if not customer_token:
        print("❌ Customer login failed. Please create a customer account first.")
        return
    
    # Step 2: Create conversation as customer
    print("\n2️⃣ Creating conversation...")
    conversation_id = create_conversation(customer_token)
    if not conversation_id:
        return
    
    # Step 3: Customer sends message
    print("\n3️⃣ Customer sending message...")
    customer_message = f"Hello Admin! I need help with my order. Test message at {datetime.now().strftime('%H:%M:%S')}"
    send_message(customer_token, conversation_id, customer_message)
    
    # Step 4: Admin login
    print("\n4️⃣ Admin Login...")
    admin_token = get_auth_token("admin@example.com", "admin123")
    if not admin_token:
        print("❌ Admin login failed. Please create an admin account first.")
        return
    
    # Step 5: Admin checks inbox
    print("\n5️⃣ Admin checking inbox...")
    inbox = get_inbox(admin_token)
    
    # Step 6: Admin assigns conversation to himself
    print("\n6️⃣ Admin assigning conversation...")
    # First get admin user ID (this would be done differently in real scenario)
    # For now, we'll assume admin can see the conversation
    
    # Step 7: Admin sends reply
    print("\n7️⃣ Admin sending reply...")
    admin_reply = f"Hello! I'm here to help you. Admin reply at {datetime.now().strftime('%H:%M:%S')}"
    send_message(admin_token, conversation_id, admin_reply)
    
    # Step 8: Check final messages
    print("\n8️⃣ Final message check...")
    time.sleep(1)  # Wait a moment
    get_messages(admin_token, conversation_id)
    
    print("\n✅ Chat System Test Complete!")
    print("=" * 50)

if __name__ == "__main__":
    main()
