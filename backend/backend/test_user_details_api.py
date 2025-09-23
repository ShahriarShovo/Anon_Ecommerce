#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Main_Application.settings')
django.setup()

from accounts.models import User
from accounts.serializers import UserListSerializer

print("=== Testing UserListSerializer with Addresses and Order Stats ===")

# Get a user with profile
user = User.objects.select_related('profile').first()
if user:
    print(f"User: {user.email}")
    print(f"Profile: {user.profile}")
    print(f"Full name: {user.profile.full_name if user.profile else 'No profile'}")
    
    # Test serializer
    serializer = UserListSerializer(user)
    data = serializer.data
    
    print(f"\n=== Serialized Data ===")
    print(f"ID: {data['id']}")
    print(f"Email: {data['email']}")
    print(f"Full Name: {data['full_name']}")
    print(f"Username: {data['username']}")
    print(f"Phone: {data['phone']}")
    print(f"Orders Count: {data['orders_count']}")
    print(f"Total Spent: ${data['total_spent']}")
    print(f"Addresses Count: {len(data['addresses'])}")
    
    if data['addresses']:
        print(f"\n=== Addresses ===")
        for i, addr in enumerate(data['addresses']):
            print(f"Address {i+1}: {addr['full_name']} - {addr['address_line_1']}, {addr['city']}")
    else:
        print(f"\n=== No Addresses Found ===")
        
else:
    print("No users found")
