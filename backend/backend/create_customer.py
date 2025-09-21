#!/usr/bin/env python
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Main_Application.settings')
django.setup()

from accounts.models import User

def create_customer_user():
    # Check if customer user already exists
    customer_user = User.objects.filter(email='customer@greatkart.com').first()
    
    if customer_user:
        print(f"Customer user already exists: {customer_user.email}")
        return customer_user
    
    # Create customer user
    customer_user = User.objects.create_user(
        email='customer@greatkart.com',
        password='Customer123!',
        is_staff=False,
        is_superuser=False
    )
    
    print(f"Customer user created successfully: {customer_user.email}")
    print("Login credentials:")
    print("Email: customer@greatkart.com")
    print("Password: Customer123!")
    
    return customer_user

if __name__ == '__main__':
    create_customer_user()
