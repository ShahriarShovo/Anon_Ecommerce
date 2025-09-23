#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Main_Application.settings')
django.setup()

from accounts.views import admin_statistics
from django.test import RequestFactory
from accounts.models import User

print("=== Testing Admin Statistics API ===")

# Create a mock request
factory = RequestFactory()
request = factory.get('/api/accounts/statistics/')

# Create a mock admin user
try:
    admin_user = User.objects.filter(is_staff=True).first()
    if admin_user:
        request.user = admin_user
        print(f"Using admin user: {admin_user.email}")
        
        # Test the statistics function
        from rest_framework.response import Response
        response = admin_statistics(request)
        
        if hasattr(response, 'data'):
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.data}")
        else:
            print(f"Response: {response}")
    else:
        print("No admin user found")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
