"""
Test script per l'API Flask
Esegui questo script mentre l'API è in esecuzione per testare tutti gli endpoint.
"""
import requests
import json

BASE_URL = "http://localhost:5000/api"

def print_response(title, response):
    """Stampa la risposta in modo formattato."""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        data = response.json()
        print(f"Response:\n{json.dumps(data, indent=2, ensure_ascii=False)}")
    except:
        print(f"Response: {response.text}")

def test_api():
    """Test completo dell'API."""
    session = requests.Session()
    
    print("\n" + "="*60)
    print("🚀 TRAVEL AI ASSISTANT - API TEST")
    print("="*60)
    
    # Test 1: Health Check
    print("\n[1/9] Health Check...")
    response = session.get(f"{BASE_URL}/health")
    print_response("Health Check", response)
    
    # Test 2: Register
    print("\n[2/9] Registrazione nuovo utente...")
    response = session.post(f"{BASE_URL}/auth/register", json={
        "username": "test_user",
        "password": "test123456",
        "email": "test@example.com"
    })
    print_response("Register", response)
    
    # Test 3: Login
    print("\n[3/9] Login...")
    response = session.post(f"{BASE_URL}/auth/login", json={
        "username": "test_user",
        "password": "test123456"
    })
    print_response("Login", response)
    
    # Test 4: Auth Status
    print("\n[4/9] Controllo stato autenticazione...")
    response = session.get(f"{BASE_URL}/auth/status")
    print_response("Auth Status", response)
    
    # Test 5: New Travel Query
    print("\n[5/9] Creazione nuovo viaggio...")
    response = session.post(f"{BASE_URL}/travel/query", json={
        "query": "Voglio andare a Roma per 3 giorni con un budget di 800 euro"
    })
    print_response("Travel Query", response)
    
    # Test 6: Interaction (Modification)
    print("\n[6/9] Interazione - Modifica piano...")
    response = session.post(f"{BASE_URL}/travel/interact", json={
        "input": "Aggiungi una visita al Colosseo"
    })
    print_response("Interaction (Modification)", response)
    
    # Test 7: Interaction (Information)
    print("\n[7/9] Interazione - Richiesta informazioni...")
    response = session.post(f"{BASE_URL}/travel/interact", json={
        "input": "Quali sono gli orari di apertura del Colosseo?"
    })
    print_response("Interaction (Information)", response)
    
    # Test 8: Finalize Trip
    print("\n[8/9] Finalizzazione viaggio...")
    response = session.post(f"{BASE_URL}/travel/finalize")
    print_response("Finalize Trip", response)
    
    # Test 9: Get History
    print("\n[9/9] Recupero cronologia viaggi...")
    response = session.get(f"{BASE_URL}/history")
    print_response("History", response)
    
    # Test 10: Logout
    print("\n[10/10] Logout...")
    response = session.post(f"{BASE_URL}/auth/logout")
    print_response("Logout", response)
    
    print("\n" + "="*60)
    print("✅ TEST COMPLETATO!")
    print("="*60)

if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERRORE: Impossibile connettersi all'API")
        print("Assicurati che l'API sia in esecuzione su http://localhost:5000")
        print("\nPer avviare l'API, esegui:")
        print('  python api_flask.py')
    except Exception as e:
        print(f"\n❌ ERRORE: {e}")
