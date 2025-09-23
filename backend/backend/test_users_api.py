#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Main_Application.settings')
django.setup()

from accounts.models import User

print("=== Users in Database ===")
total_users = User.objects.count()
print(f"Total users: {total_users}")

if total_users > 0:
    for user in User.objects.all():
        print(f"User {user.id}: {user.email}")
        print(f"  Name: {user.profile.full_name if hasattr(user, 'profile') and user.profile else 'N/A'}")
        print(f"  Role: {'Super Admin' if user.is_superuser else 'Admin' if user.is_staff else 'Customer'}")
        print(f"  Status: {'Active' if user.is_active else 'Inactive'}")
        print(f"  Joined: {user.date_joined}")
        print(f"  Last Login: {user.last_login or 'Never'}")
        print()
else:
    print("No users found in database")
