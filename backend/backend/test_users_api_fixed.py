#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Main_Application.settings')
django.setup()

from accounts.models import User
from accounts.serializers import UserListSerializer

print("=== Testing UserListSerializer ===")

# Get a user with profile
user = User.objects.select_related('profile').first()
if user:
    print(f"User: {user.email}")
    print(f"Profile: {user.profile}")
    print(f"Full name: {user.profile.full_name if user.profile else 'No profile'}")
    
    # Test serializer
    serializer = UserListSerializer(user)
    print(f"Serialized data: {serializer.data}")
else:
    print("No users found")
