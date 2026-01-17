"""
Simple test script to verify the API is working correctly.
Run this after starting the server with: python run.py
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def print_response(response, title):
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response:\n{json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")

def test_api():
    print("Testing Video Game Trading API")
    
    # Test 1: Root endpoint
    response = requests.get(f"{BASE_URL}/")
    print_response(response, "1. Root Endpoint (HATEOAS Links)")
    
    # Test 2: Register a user
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword123",
        "street_address": "123 Test Street, Test City, TS 12345"
    }
    response = requests.post(f"{BASE_URL}/users", json=user_data)
    print_response(response, "2. Register User")
    
    # Test 3: Login
    login_data = {
        "username": "test@example.com",
        "password": "testpassword123"
    }
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    print_response(response, "3. Login")
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test 4: Get current user
        response = requests.get(f"{BASE_URL}/users/me", headers=headers)
        print_response(response, "4. Get Current User")
        
        # Test 5: Create a video game
        game_data = {
            "name": "The Legend of Zelda: Breath of the Wild",
            "publisher": "Nintendo",
            "year_published": 2017,
            "gaming_system": "Nintendo Switch",
            "condition": "mint",
            "previous_owners": 1
        }
        response = requests.post(f"{BASE_URL}/games", json=game_data, headers=headers)
        print_response(response, "5. Create Video Game")
        
        if response.status_code == 201:
            game_id = response.json()["id"]
            
            # Test 6: Get the game
            response = requests.get(f"{BASE_URL}/games/{game_id}", headers=headers)
            print_response(response, "6. Get Video Game (with HATEOAS links)")
            
            # Test 7: Update the game
            update_data = {
                "condition": "good",
                "previous_owners": 2
            }
            response = requests.put(f"{BASE_URL}/games/{game_id}", json=update_data, headers=headers)
            print_response(response, "7. Update Video Game")
            
            # Test 8: Get all games
            response = requests.get(f"{BASE_URL}/games", headers=headers)
            print_response(response, "8. Get All Games (Collection with HATEOAS)")
            
            # Test 9: Delete the game
            response = requests.delete(f"{BASE_URL}/games/{game_id}", headers=headers)
            print_response(response, "9. Delete Video Game")
    
    print("\n" + "="*60)
    print("Testing Complete!")
    print("="*60)
    print("\nVisit http://localhost:8000/docs for interactive API documentation")

if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API.")
        print("Make sure the server is running with: python run.py")
    except Exception as e:
        print(f"Error: {e}")

