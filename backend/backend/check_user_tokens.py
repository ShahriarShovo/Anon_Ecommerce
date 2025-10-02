#!/usr/bin/env python
"""
Check User Verification Tokens
============================

This script checks all users and their verification tokens in the database.
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Main_Application.settings')
django.setup()

from accounts.models import User

def check_user_tokens():
    """Check all users and their verification tokens"""

    print("=" * 60)
    
    users = User.objects.all().order_by('-date_joined')
    
    if not users.exists():

        return
    
    print(f"📊 Total users: {users.count()}")
    print()
    
    for user in users:
        print(f"👤 User: {user.email}")
        print(f"   ID: {user.id}")
        print(f"   Email Verified: {user.is_email_verified}")
        print(f"   Verification Token: {user.email_verification_token}")
        print(f"   Token Sent At: {user.email_verification_sent_at}")
        print(f"   Date Joined: {user.date_joined}")
        print("-" * 40)
    
    print()

if __name__ == "__main__":
    check_user_tokens()
