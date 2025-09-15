#!/usr/bin/env python
import requests
import json

def test_category_api():
    try:
        # Test GET categories
        print("Testing GET /api/products/category/")
        response = requests.get("http://127.0.0.1:8000/api/products/category/")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Categories:")
            print(json.dumps(data, indent=2))
        else:
            print(f"Error: {response.text}")
        
        print("\n" + "="*50 + "\n")
        
        # Test with admin login
        print("Testing with admin login...")
        login_data = {
            "email": "admin@gmail.com",
            "password": "admin123456"
        }
        
        login_response = requests.post("http://127.0.0.1:8000/accounts/login/", json=login_data)
        if login_response.status_code == 200:
            login_result = login_response.json()
            token = login_result['token']['access']
            print(f"Login successful! Token: {token[:20]}...")
            
            # Test authenticated GET
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            print("\nTesting authenticated GET /api/products/category/")
            auth_response = requests.get("http://127.0.0.1:8000/api/products/category/", headers=headers)
            print(f"Status Code: {auth_response.status_code}")
            if auth_response.status_code == 200:
                data = auth_response.json()
                print("Authenticated Categories:")
                print(json.dumps(data, indent=2))
            else:
                print(f"Error: {auth_response.text}")
                
        else:
            print(f"Login failed: {login_response.status_code}")
            print(login_response.text)
            
    except requests.exceptions.ConnectionError as e:
        print(f"Connection Error: {e}")
        print("Make sure Django server is running on http://127.0.0.1:8000")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    test_category_api()
