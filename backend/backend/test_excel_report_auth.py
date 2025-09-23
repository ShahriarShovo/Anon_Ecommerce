#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Main_Application.settings')
django.setup()

from django.test import Client
from accounts.models import User
from rest_framework_simplejwt.tokens import RefreshToken

print("=== Testing Excel Report API with Authentication ===")

try:
    # Get admin user
    admin_user = User.objects.filter(is_staff=True).first()
    if admin_user:
        print(f"Using admin user: {admin_user.email}")
        
        # Generate JWT token
        refresh = RefreshToken.for_user(admin_user)
        access_token = str(refresh.access_token)
        print(f"Generated access token: {access_token[:50]}...")
        
        # Create test client
        client = Client()
        
        # Test the Excel report endpoint
        response = client.get(
            '/api/analytics/excel-report/?type=users&period=30',
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response content type: {response.get('Content-Type', 'N/A')}")
        print(f"Response content disposition: {response.get('Content-Disposition', 'N/A')}")
        
        if response.status_code == 200:
            print("Excel report generated successfully!")
            print(f"Response content length: {len(response.content)} bytes")
        else:
            print(f"Error response: {response.content.decode()}")
            
    else:
        print("No admin user found")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
