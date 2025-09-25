#!/usr/bin/env python
"""
Create test users for chat system testing
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Main_Application.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

def create_test_users():
    """Create test users for chat system"""
    
    with transaction.atomic():
        # Create customer user
        customer, created = User.objects.get_or_create(
            email='customer@example.com',
            defaults={
                'is_active': True,
                'is_staff': False,
                'is_superuser': False
            }
        )
        if created:
            customer.set_password('password123')
            customer.save()
            # Update profile
            customer.profile.full_name = 'Test Customer'
            customer.profile.save()
            print("✅ Customer user created: customer@example.com / password123")
        else:
            print("ℹ️ Customer user already exists")
        
        # Create admin user
        admin, created = User.objects.get_or_create(
            email='admin@example.com',
            defaults={
                'is_active': True,
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            # Update profile
            admin.profile.full_name = 'Test Admin'
            admin.profile.save()
            print("✅ Admin user created: admin@example.com / admin123")
        else:
            print("ℹ️ Admin user already exists")
        
        # Create staff user
        staff, created = User.objects.get_or_create(
            email='staff@example.com',
            defaults={
                'is_active': True,
                'is_staff': True,
                'is_superuser': False
            }
        )
        if created:
            staff.set_password('staff123')
            staff.save()
            # Update profile
            staff.profile.full_name = 'Test Staff'
            staff.profile.save()
            print("✅ Staff user created: staff@example.com / staff123")
        else:
            print("ℹ️ Staff user already exists")
    
    print("\n🎯 Test users ready for chat system testing!")
    print("=" * 50)
    print("Customer: customer@example.com / password123")
    print("Admin: admin@example.com / admin123") 
    print("Staff: staff@example.com / staff123")
    print("=" * 50)

if __name__ == "__main__":
    create_test_users()
