#!/usr/bin/env python
import os
import django
import requests
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Main_Application.settings')
django.setup()

from accounts.models import User

# Get admin user token
admin_user = User.objects.filter(is_staff=True).first()
if admin_user:
    print(f"Admin user: {admin_user.email}")
    
    # Test API endpoint
    url = "http://localhost:8000/api/orders/order/"
    headers = {
        'Authorization': f'Bearer {admin_user.auth_token.key if hasattr(admin_user, "auth_token") else "test_token"}',
        'Content-Type': 'application/json'
    }
    
    print(f"Testing API: {url}")
    print(f"Headers: {headers}")
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
else:
    print("No admin user found")
