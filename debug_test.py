"""Debug test to see the actual error"""
import requests
import json

BASE_URL = "http://localhost:8000"

# Test user registration
user_data = {
    "name": "Test User",
    "email": "test@example.com",
    "password": "testpassword123",
    "street_address": "123 Test Street, Test City, TS 12345"
}

print("Testing user registration...")
response = requests.post(f"{BASE_URL}/users", json=user_data)
print(f"Status Code: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# If successful, try to login
if response.status_code == 201:
    print("\n\nTesting login...")
    login_data = {
        "username": "test@example.com",
        "password": "testpassword123"
    }
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

