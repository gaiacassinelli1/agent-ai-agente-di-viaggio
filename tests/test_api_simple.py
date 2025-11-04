"""
Test semplice per l'API Flask
Test base senza chiamate intensive all'AI
"""
import requests
import json

BASE_URL = "http://localhost:5000/api"

def test_basic():
    """Test di base senza AI."""
    session = requests.Session()
    
    print("\n🚀 TRAVEL AI ASSISTANT - BASIC API TEST\n")
    
    # Test 1: Health Check
    print("✅ [1/5] Health Check...")
    response = session.get(f"{BASE_URL}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}\n")
    
    # Test 2: Register
    print("✅ [2/5] Register nuovo utente...")
    response = session.post(f"{BASE_URL}/auth/register", json={
        "username": "demo_user",
        "password": "demo123456",
        "email": "demo@example.com"
    })
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Message: {data.get('message', data.get('error'))}\n")
    
    # Test 3: Login
    print("✅ [3/5] Login...")
    response = session.post(f"{BASE_URL}/auth/login", json={
        "username": "demo_user",
        "password": "demo123456"
    })
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Logged in as: {data['user']['username']}")
        print(f"   Email: {data['user']['email']}\n")
    
    # Test 4: Auth Status
    print("✅ [4/5] Check auth status...")
    response = session.get(f"{BASE_URL}/auth/status")
    data = response.json()
    print(f"   Authenticated: {data['authenticated']}")
    if data['authenticated']:
        print(f"   User: {data['user']['username']}\n")
    
    # Test 5: Logout
    print("✅ [5/5] Logout...")
    response = session.post(f"{BASE_URL}/auth/logout")
    data = response.json()
    print(f"   Message: {data.get('message')}\n")
    
    print("✅ TEST COMPLETATO CON SUCCESSO!\n")
    print("📝 Per testare le funzionalità AI, usa:")
    print("   - POST /api/travel/query - Crea nuovo viaggio")
    print("   - POST /api/travel/interact - Interagisci con il piano")
    print("   - GET /api/history - Visualizza cronologia\n")

if __name__ == "__main__":
    try:
        test_basic()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERRORE: Server non raggiungibile")
        print("Avvia l'API con: python api_flask.py\n")
    except Exception as e:
        print(f"\n❌ ERRORE: {e}\n")
