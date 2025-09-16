#!/usr/bin/env python3
"""
Test Session Debug
==================

Test script to debug session management issues.
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Main_Application.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.sessions.models import Session
from cart.views.cart import get_or_create_cart, get_cart
from cart.models import Cart, CartItem

def test_session_management():
    """Test session management"""
    print("🧪 Testing Session Management...")
    
    # Create a request factory
    factory = RequestFactory()
    
    # Test 1: Create request without session
    print("\n1️⃣ Testing request without session...")
    request = factory.get('/api/cart/')
    
    # Add user attribute
    from django.contrib.auth.models import AnonymousUser
    request.user = AnonymousUser()
    
    # Manually create session
    from django.contrib.sessions.backends.db import SessionStore
    request.session = SessionStore()
    request.session.create()
    
    print(f"Session key: {request.session.session_key}")
    
    # Test get_or_create_cart
    cart = get_or_create_cart(request)
    print(f"Cart ID: {cart.id}")
    print(f"Cart Session Key: {cart.session_key}")
    print(f"Cart User: {cart.user}")
    
    # Test 2: Create another request with same session key
    print("\n2️⃣ Testing request with same session key...")
    request2 = factory.get('/api/cart/')
    request2.user = AnonymousUser()
    request2.session = SessionStore()
    request2.session._session_key = request.session.session_key
    
    cart2 = get_or_create_cart(request2)
    print(f"Cart2 ID: {cart2.id}")
    print(f"Cart2 Session Key: {cart2.session_key}")
    print(f"Same cart? {cart.id == cart2.id}")
    
    # Test 3: Test get_cart
    print("\n3️⃣ Testing get_cart...")
    cart_data = get_cart(request)
    print(f"Get cart response: {cart_data.data}")
    
    print("\n✅ Session management test completed!")

if __name__ == '__main__':
    test_session_management()
