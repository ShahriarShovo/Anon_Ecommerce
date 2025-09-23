#!/usr/bin/env python
import requests
import json

# Test the login API endpoint
url = "http://localhost:8000/api/accounts/login/"
data = {
    "email": "admin@gmail.com",
    "password": "admin123"
}
headers = {
    'Content-Type': 'application/json'
}

print(f"Testing login API endpoint: {url}")
print(f"Data: {data}")

try:
    response = requests.post(url, headers=headers, json=data)
    print(f"Response status code: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")
    print(f"Response content type: {response.headers.get('content-type', 'Unknown')}")
    print(f"Response text (first 500 chars): {response.text[:500]}")
    
    if response.headers.get('content-type', '').startswith('application/json'):
        try:
            data = response.json()
            print(f"JSON data: {json.dumps(data, indent=2)}")
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
    else:
        print("Response is not JSON")
        
except requests.exceptions.RequestException as e:
    print(f"Request error: {e}")
