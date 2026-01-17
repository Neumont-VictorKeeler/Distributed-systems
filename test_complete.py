import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_api():
    print("=" * 60)
    print("VIDEO GAME TRADING API - COMPREHENSIVE TEST")
    print("=" * 60)
    
    try:
        print("\n[1/10] Testing Root Endpoint...")
        response = requests.get(f"{BASE_URL}/", timeout=5)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "links" in data, "Missing HATEOAS links"
        print(f"✓ Root endpoint working - {len(data['links'])} HATEOAS links found")
        
        print("\n[2/10] Testing User Registration...")
        user_data = {
            "name": "Alice Smith",
            "email": "alice@example.com",
            "password": "securepass123",
            "street_address": "456 Oak Ave, Springfield, IL 62701"
        }
        response = requests.post(f"{BASE_URL}/users", json=user_data, timeout=5)
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"
        user = response.json()
        user_id = user["id"]
        assert "links" in user, "Missing HATEOAS links in user response"
        print(f"✓ User created (ID: {user_id}) with {len(user['links'])} HATEOAS links")
        
        print("\n[3/10] Testing Get User by ID...")
        response = requests.get(f"{BASE_URL}/users/{user_id}", timeout=5)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        user_data = response.json()
        assert user_data["email"] == "alice@example.com"
        print(f"✓ Retrieved user: {user_data['name']}")
        
        print("\n[4/10] Testing Get All Users...")
        response = requests.get(f"{BASE_URL}/users", timeout=5)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        users = response.json()
        assert "items" in users, "Missing items in collection"
        assert "links" in users, "Missing HATEOAS links in collection"
        print(f"✓ Retrieved {len(users['items'])} user(s)")
        
        print("\n[5/10] Testing Update User...")
        update_data = {
            "name": "Alice Johnson",
            "street_address": "789 Maple St, Springfield, IL 62702"
        }
        response = requests.put(f"{BASE_URL}/users/{user_id}", json=update_data, timeout=5)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        updated_user = response.json()
        assert updated_user["name"] == "Alice Johnson"
        print(f"✓ User updated: {updated_user['name']}")
        
        print("\n[6/10] Testing Create Video Game...")
        game_data = {
            "name": "Super Mario Bros",
            "publisher": "Nintendo",
            "year_published": 1985,
            "gaming_system": "NES",
            "condition": "good",
            "previous_owners": 3
        }
        response = requests.post(f"{BASE_URL}/games?owner_id={user_id}", json=game_data, timeout=5)
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"
        game = response.json()
        game_id = game["id"]
        assert "links" in game, "Missing HATEOAS links in game response"
        print(f"✓ Game created (ID: {game_id}): {game['name']}")
        
        print("\n[7/10] Testing Get Game by ID...")
        response = requests.get(f"{BASE_URL}/games/{game_id}", timeout=5)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        game_data = response.json()
        assert game_data["name"] == "Super Mario Bros"
        print(f"✓ Retrieved game: {game_data['name']} ({game_data['condition']})")
        
        print("\n[8/10] Testing Update Game...")
        update_game = {"condition": "mint"}
        response = requests.put(f"{BASE_URL}/games/{game_id}", json=update_game, timeout=5)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        updated_game = response.json()
        assert updated_game["condition"] == "mint"
        print(f"✓ Game condition updated to: {updated_game['condition']}")
        
        print("\n[9/10] Testing Get All Games...")
        response = requests.get(f"{BASE_URL}/games", timeout=5)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        games = response.json()
        assert "items" in games, "Missing items in collection"
        print(f"✓ Retrieved {len(games['items'])} game(s)")
        
        print("\n[10/10] Testing Delete Game...")
        response = requests.delete(f"{BASE_URL}/games/{game_id}", timeout=5)
        assert response.status_code == 204, f"Expected 204, got {response.status_code}"
        print(f"✓ Game deleted successfully")
        
        response = requests.get(f"{BASE_URL}/games/{game_id}", timeout=5)
        assert response.status_code == 404, "Game should not exist after deletion"
        print(f"✓ Verified game deletion (404 returned)")
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED! ✓")
        print("=" * 60)
        return True
        
    except requests.exceptions.ConnectionError:
        print("\n✗ ERROR: Cannot connect to server at http://localhost:8000")
        print("  Make sure the server is running: python run.py")
        return False
    except requests.exceptions.Timeout:
        print("\n✗ ERROR: Request timed out")
        return False
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_api()
    sys.exit(0 if success else 1)

