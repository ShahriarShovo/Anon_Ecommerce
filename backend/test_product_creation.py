#!/usr/bin/env python3
"""
Test script to create products with variants and images
"""
import requests
import json
import os
from pathlib import Path

# API Configuration
BASE_URL = "http://127.0.0.1:8000"
API_BASE = f"{BASE_URL}/api"

def get_auth_token():
    """Get authentication token"""
    login_data = {
        "username": "admin",  # Change to your admin username
        "password": "admin123"  # Change to your admin password
    }
    
    response = requests.post(f"{API_BASE}/auth/login/", json=login_data)
    if response.status_code == 200:
        data = response.json()
        return data.get('access')
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
        return None

def create_test_images():
    """Create test image files"""
    test_images = []
    
    # Create a simple test image (1x1 pixel PNG)
    test_image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xdd\x8d\xb4\x1c\x00\x00\x00\x00IEND\xaeB`\x82'
    
    for i in range(3):
        image_path = f"test_image_{i+1}.png"
        with open(image_path, 'wb') as f:
            f.write(test_image_data)
        test_images.append(image_path)
    
    return test_images

def test_simple_product_creation(token):
    """Test creating a simple product without variants"""
    print("\n=== Testing Simple Product Creation ===")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    product_data = {
        "title": "Test Simple Product",
        "description": "This is a test simple product",
        "short_description": "Test product",
        "category": 1,  # Assuming category with ID 1 exists
        "subcategory": 1,  # Assuming subcategory with ID 1 exists
        "product_type": "simple",
        "status": "active",
        "price": "25.99",
        "old_price": "35.99",
        "track_quantity": True,
        "quantity": 100,
        "allow_backorder": False,
        "weight_unit": "kg",
        "requires_shipping": True,
        "taxable": True,
        "featured": False
    }
    
    response = requests.post(f"{API_BASE}/products/product/", json=product_data, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 201:
        product_data = response.json()
        print(f"✅ Simple product created successfully! ID: {product_data.get('id')}")
        return product_data.get('id')
    else:
        print(f"❌ Simple product creation failed")
        return None

def test_variable_product_creation(token):
    """Test creating a variable product with variants using FormData"""
    print("\n=== Testing Variable Product Creation ===")
    
    headers = {
        'Authorization': f'Bearer {token}'
        # Don't set Content-Type for FormData
    }
    
    # Create test images
    test_images = create_test_images()
    
    # Prepare FormData
    form_data = {
        'title': 'Test Variable Product',
        'description': 'This is a test variable product with variants',
        'short_description': 'Test variable product',
        'category': '1',
        'subcategory': '1',
        'product_type': 'variable',
        'status': 'active',
        'price': '15.00',
        'old_price': '25.00',
        'track_quantity': 'true',
        'quantity': '50',
        'allow_backorder': 'false',
        'weight_unit': 'kg',
        'requires_shipping': 'true',
        'taxable': 'true',
        'featured': 'false',
        
        # Variant 1
        'variants[0][title]': 'Small Red',
        'variants[0][sku]': 'TEST-SMALL-RED',
        'variants[0][price]': '10.00',
        'variants[0][old_price]': '15.00',
        'variants[0][quantity]': '20',
        'variants[0][track_quantity]': 'true',
        'variants[0][allow_backorder]': 'false',
        'variants[0][weight_unit]': 'kg',
        'variants[0][position]': '1',
        'variants[0][is_active]': 'true',
        'variants[0][option1_name]': 'Size',
        'variants[0][option1_value]': 'Small',
        'variants[0][option2_name]': 'Color',
        'variants[0][option2_value]': 'Red',
        
        # Dynamic options for variant 1
        'variants[0][dynamic_options][0][name]': 'Size',
        'variants[0][dynamic_options][0][value]': 'Small',
        'variants[0][dynamic_options][0][position]': '1',
        'variants[0][dynamic_options][1][name]': 'Color',
        'variants[0][dynamic_options][1][value]': 'Red',
        'variants[0][dynamic_options][1][position]': '2',
        
        # Variant 2
        'variants[1][title]': 'Large Blue',
        'variants[1][sku]': 'TEST-LARGE-BLUE',
        'variants[1][price]': '20.00',
        'variants[1][old_price]': '30.00',
        'variants[1][quantity]': '15',
        'variants[1][track_quantity]': 'true',
        'variants[1][allow_backorder]': 'false',
        'variants[1][weight_unit]': 'kg',
        'variants[1][position]': '2',
        'variants[1][is_active]': 'true',
        'variants[1][option1_name]': 'Size',
        'variants[1][option1_value]': 'Large',
        'variants[1][option2_name]': 'Color',
        'variants[1][option2_value]': 'Blue',
        
        # Dynamic options for variant 2
        'variants[1][dynamic_options][0][name]': 'Size',
        'variants[1][dynamic_options][0][value]': 'Large',
        'variants[1][dynamic_options][0][position]': '1',
        'variants[1][dynamic_options][1][name]': 'Color',
        'variants[1][dynamic_options][1][value]': 'Blue',
        'variants[1][dynamic_options][1][position]': '2',
    }
    
    # Add image files
    files = {}
    for i, image_path in enumerate(test_images):
        files[f'uploaded_images'] = (image_path, open(image_path, 'rb'), 'image/png')
    
    print(f"Sending FormData with {len(form_data)} fields and {len(files)} files")
    print(f"FormData keys: {list(form_data.keys())}")
    
    response = requests.post(f"{API_BASE}/products/product/", data=form_data, files=files, headers=headers)
    
    # Close file handles
    for file_handle in files.values():
        file_handle[1].close()
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 201:
        product_data = response.json()
        print(f"✅ Variable product created successfully! ID: {product_data.get('id')}")
        return product_data.get('id')
    else:
        print(f"❌ Variable product creation failed")
        return None

def test_product_list(token):
    """Test getting product list"""
    print("\n=== Testing Product List ===")
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    response = requests.get(f"{API_BASE}/products/product/", headers=headers)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        products = response.json()
        print(f"✅ Found {len(products)} products")
        for product in products:
            print(f"  - {product.get('title')} (ID: {product.get('id')}, Type: {product.get('product_type')})")
    else:
        print(f"❌ Product list failed: {response.text}")

def cleanup_test_files():
    """Clean up test image files"""
    for i in range(3):
        image_path = f"test_image_{i+1}.png"
        if os.path.exists(image_path):
            os.remove(image_path)
            print(f"Cleaned up {image_path}")

def main():
    """Main test function"""
    print("🚀 Starting Product Creation Tests")
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        print("❌ Failed to get authentication token")
        return
    
    print(f"✅ Authentication successful")
    
    try:
        # Test simple product creation
        simple_product_id = test_simple_product_creation(token)
        
        # Test variable product creation
        variable_product_id = test_variable_product_creation(token)
        
        # Test product list
        test_product_list(token)
        
        print(f"\n📊 Test Results:")
        print(f"  - Simple Product: {'✅ Success' if simple_product_id else '❌ Failed'}")
        print(f"  - Variable Product: {'✅ Success' if variable_product_id else '❌ Failed'}")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up test files
        cleanup_test_files()

if __name__ == "__main__":
    main()
