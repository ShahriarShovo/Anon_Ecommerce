#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Main_Application.settings')
django.setup()

from analytics.views import generate_excel_report
from django.test import RequestFactory
from accounts.models import User

print("=== Testing Excel Report API with Debug ===")

# Create a mock request
factory = RequestFactory()
request = factory.get('/api/analytics/excel-report/?type=users&period=30')

# Create a mock admin user
try:
    admin_user = User.objects.filter(is_staff=True).first()
    if admin_user:
        request.user = admin_user
        print(f"Using admin user: {admin_user.email}")
        
        # Test the Excel report function
        response = generate_excel_report(request)
        
        if hasattr(response, 'status_code'):
            print(f"Response status: {response.status_code}")
            print(f"Response content type: {response.get('Content-Type', 'N/A')}")
            print(f"Response content disposition: {response.get('Content-Disposition', 'N/A')}")
        else:
            print(f"Response: {response}")
    else:
        print("No admin user found")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
