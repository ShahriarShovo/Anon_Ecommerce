import requests
import json

# Admin login
login_data = {'email': 'admin@example.com', 'password': 'admin123'}
login_response = requests.post('http://localhost:8000/api/accounts/login/', json=login_data)
admin_token = login_response.json()['token']['access']

# Get admin inbox
headers = {'Authorization': f'Bearer {admin_token}'}
inbox_response = requests.get('http://localhost:8000/api/chat/inbox/', headers=headers)
conversations = inbox_response.json()

print(f'Admin inbox has {len(conversations)} conversations')
for conv in conversations[:10]:
    print(f'  Conversation {conv["id"]}: {conv.get("customer_name", "Unknown")} - {conv["status"]}')
