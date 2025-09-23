#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Main_Application.settings')
django.setup()

from accounts.models import User
from rest_framework.authtoken.models import Token

# Get admin user
admin_user = User.objects.filter(is_staff=True).first()
if admin_user:
    print(f"Admin user: {admin_user.email}")
    
    # Get or create token
    token, created = Token.objects.get_or_create(user=admin_user)
    print(f"Token: {token.key}")
    print(f"Token created: {created}")
    
    # Test API with real token
    import requests
    
    url = "http://localhost:8000/api/orders/"
    headers = {
        'Authorization': f'Bearer {token.key}',
        'Content-Type': 'application/json'
    }
    
    print(f"\nTesting API with real token...")
    try:
        response = requests.get(url, headers=headers)
        print(f"Response status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Orders count: {len(data) if isinstance(data, list) else 'Unknown'}")
            print(f"Response: {data}")
        else:
            print(f"Error response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
else:
    print("No admin user found")
