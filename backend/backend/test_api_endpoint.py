#!/usr/bin/env python
import requests
import json

# Test the API endpoint
url = "http://localhost:8000/api/orders/"
headers = {
    'Authorization': 'Bearer test_token',
    'Content-Type': 'application/json'
}

print(f"Testing API endpoint: {url}")
print(f"Headers: {headers}")

try:
    response = requests.get(url, headers=headers)
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
