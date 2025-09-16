#!/usr/bin/env python3
"""
Test Real Cart Functionality
============================

Test script to test real cart functionality with session management.
"""

import os
import sys
import django
import requests
import json

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Main_Application.settings')
django.setup()

def test_cart_with_requests():
    """Test cart functionality using requests library"""
    print("🧪 Testing Real Cart Functionality...")
    
    base_url = "http://127.0.0.1:8000"
    session = requests.Session()
    
    # Test 1: Get initial cart
    print("\n1️⃣ Testing get initial cart...")
    response = session.get(f"{base_url}/api/cart/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 2: Add item to cart
    print("\n2️⃣ Testing add item to cart...")
    add_data = {
        "product_id": 8,
        "quantity": 1,
        "variant_id": 3
    }
    response = session.post(f"{base_url}/api/cart/add/", json=add_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 3: Get cart after adding item
    print("\n3️⃣ Testing get cart after adding item...")
    response = session.get(f"{base_url}/api/cart/")
    print(f"Status: {response.status_code}")
    cart_data = response.json()
    print(f"Response: {cart_data}")
    
    if cart_data.get('success') and cart_data.get('cart'):
        cart = cart_data['cart']
        print(f"Cart ID: {cart.get('id')}")
        print(f"Session Key: {cart.get('session_key')}")
        print(f"Total Items: {cart.get('total_items')}")
        print(f"Items Count: {len(cart.get('items', []))}")
    
    # Test 4: Add another item
    print("\n4️⃣ Testing add another item...")
    add_data2 = {
        "product_id": 8,
        "quantity": 1,
        "variant_id": 3
    }
    response = session.post(f"{base_url}/api/cart/add/", json=add_data2)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 5: Get final cart
    print("\n5️⃣ Testing get final cart...")
    response = session.get(f"{base_url}/api/cart/")
    print(f"Status: {response.status_code}")
    cart_data = response.json()
    print(f"Response: {cart_data}")
    
    if cart_data.get('success') and cart_data.get('cart'):
        cart = cart_data['cart']
        print(f"Final Cart ID: {cart.get('id')}")
        print(f"Final Session Key: {cart.get('session_key')}")
        print(f"Final Total Items: {cart.get('total_items')}")
        print(f"Final Items Count: {len(cart.get('items', []))}")
    
    print("\n✅ Real cart functionality test completed!")

if __name__ == '__main__':
    test_cart_with_requests()
