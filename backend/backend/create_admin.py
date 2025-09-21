#!/usr/bin/env python
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Main_Application.settings')
django.setup()

from accounts.models import User

def create_admin_user():
    # Check if admin user already exists
    admin_user = User.objects.filter(is_staff=True).first()
    
    if admin_user:
        print(f"Admin user already exists: {admin_user.email}")
        return admin_user
    
    # Create admin user
    admin_user = User.objects.create_user(
        email='admin@greatkart.com',
        password='Admin123!',
        is_staff=True,
        is_superuser=True
    )
    
    print(f"Admin user created successfully: {admin_user.email}")
    print("Login credentials:")
    print("Email: admin@greatkart.com")
    print("Password: Admin123!")
    
    return admin_user

if __name__ == '__main__':
    create_admin_user()
