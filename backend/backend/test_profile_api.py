#!/usr/bin/env python
import requests
import json

def test_profile_api():
    try:
        # First login to get token
        login_data = {
            "email": "admin@gmail.com",
            "password": "admin123456"
        }
        
        login_response = requests.post("http://127.0.0.1:8000/accounts/login/", json=login_data)
        if login_response.status_code == 200:
            login_result = login_response.json()
            token = login_result['token']['access']
            
            # Now test profile API
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            profile_response = requests.get("http://127.0.0.1:8000/accounts/profile/", headers=headers)
            if profile_response.status_code == 200:
                profile_data = profile_response.json()
                print("Profile API Response:")
                print(json.dumps(profile_data, indent=2))
                
                print(f"\nIs Staff: {profile_data.get('is_staff', 'NOT FOUND')}")
                print(f"Is Superuser: {profile_data.get('is_superuser', 'NOT FOUND')}")
            else:
                print(f"Profile API failed with status: {profile_response.status_code}")
                print(profile_response.text)
        else:
            print(f"Login failed with status: {login_response.status_code}")
            print(login_response.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    test_profile_api()
