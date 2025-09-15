#!/usr/bin/env python
import requests
import json

def test_auth_token():
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
            
            # Test profile API
            print("\n2. Testing profile API...")
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            profile_response = requests.get("http://127.0.0.1:8000/accounts/profile/", headers=headers)
            print(f"Profile Status: {profile_response.status_code}")
            if profile_response.status_code == 200:
                profile_data = profile_response.json()
                print(f"User: {profile_data.get('username')}")
                print(f"Is Staff: {profile_data.get('is_staff')}")
                print(f"Is Superuser: {profile_data.get('is_superuser')}")
            
            # Test category API
            print("\n3. Testing category API...")
            category_response = requests.get("http://127.0.0.1:8000/api/products/category/", headers=headers)
            print(f"Category Status: {category_response.status_code}")
            if category_response.status_code == 200:
                category_data = category_response.json()
                print(f"Categories found: {len(category_data)}")
                for cat in category_data[:3]:  # Show first 3
                    print(f"  - {cat.get('name')} (ID: {cat.get('id')})")
            else:
                print(f"Category Error: {category_response.text}")
                
        else:
            print(f"Login failed: {login_response.status_code}")
            print(login_response.text)
            
    except requests.exceptions.ConnectionError as e:
        print(f"Connection Error: {e}")
        print("Make sure Django server is running on http://127.0.0.1:8000")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    test_auth_token()
