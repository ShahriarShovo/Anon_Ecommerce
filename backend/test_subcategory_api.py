#!/usr/bin/env python
import requests
import json

def test_subcategory_api():
    try:
        # First login to get token
        print("1. Testing login...")
        login_data = {
            "email": "admin@gmail.com",
            "password": "admin123456"
        }
        
        login_response = requests.post("http://127.0.0.1:8000/accounts/login/", json=login_data)
        print(f"Login Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            token = login_result['token']['access']
            print(f"Token received: {token[:20]}...")
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            # Test subcategory API
            print("\n2. Testing subcategory API...")
            subcategory_response = requests.get("http://127.0.0.1:8000/api/products/subcategory/", headers=headers)
            print(f"SubCategory Status: {subcategory_response.status_code}")
            if subcategory_response.status_code == 200:
                subcategory_data = subcategory_response.json()
                print(f"SubCategories found: {len(subcategory_data)}")
                for subcat in subcategory_data[:3]:  # Show first 3
                    print(f"  - {subcat.get('name')} (ID: {subcat.get('id')}, Category: {subcat.get('category')})")
            else:
                print(f"SubCategory Error: {subcategory_response.text}")
                
        else:
            print(f"Login failed: {login_response.status_code}")
            print(login_response.text)
            
    except requests.exceptions.ConnectionError as e:
        print(f"Connection Error: {e}")
        print("Make sure Django server is running on http://127.0.0.1:8000")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    test_subcategory_api()
