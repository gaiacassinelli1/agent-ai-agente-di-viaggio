#!/usr/bin/env python3
"""
Test script per verificare le API Amadeus.
"""
import os
import sys
import requests
from dotenv import load_dotenv

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Load environment
load_dotenv(os.path.join(project_root, '.env'))

def test_amadeus_auth():
    """Test Amadeus authentication."""
    api_key = os.getenv("VOLI_API_KEY")
    api_secret = os.getenv("VOLI_API_SECRET")
    
    print(f"API Key: {api_key[:10]}..." if api_key else "API Key: Not found")
    print(f"API Secret: {api_secret[:10]}..." if api_secret else "API Secret: Not found")
    
    if not api_key or not api_secret:
        print("❌ Credenziali Amadeus mancanti!")
        return None
    
    # Test authentication
    token_url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": api_key,
        "client_secret": api_secret
    }
    
    try:
        response = requests.post(token_url, data=data, timeout=10)
        print(f"Auth response status: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Autenticazione riuscita!")
            print(f"Token type: {token_data.get('type')}")
            print(f"Expires in: {token_data.get('expires_in')} seconds")
            return token_data.get("access_token")
        else:
            print(f"❌ Autenticazione fallita!")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Errore di connessione: {e}")
        return None

def test_flight_search(token):
    """Test flight search."""
    if not token:
        print("⏭️ Saltando test voli - nessun token")
        return
    
    print("\n🔍 Test ricerca voli...")
    
    flight_url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    
    # Test semplice: Roma -> Parigi con data vicina
    from datetime import datetime, timedelta
    future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    
    params = {
        "originLocationCode": "FCO",  # Roma Fiumicino
        "destinationLocationCode": "CDG",  # Parigi Charles de Gaulle
        "departureDate": future_date,  # Data tra 30 giorni
        "adults": 1,
        "max": 3,
        "currencyCode": "EUR"
    }
    
    try:
        print(f"Parametri: {params}")
        response = requests.get(flight_url, params=params, headers=headers, timeout=15)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            flight_count = len(data.get("data", []))
            print(f"✅ Trovati {flight_count} voli!")
        else:
            print(f"❌ Errore {response.status_code}")
            print(f"Response: {response.text[:300]}")
            
    except Exception as e:
        print(f"❌ Errore richiesta voli: {e}")

def test_hotel_search(token):
    """Test hotel search."""
    if not token:
        print("⏭️ Saltando test hotel - nessun token")
        return
    
    print("\n🔍 Test ricerca hotel...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    
    # Step 1: Get hotel IDs for Vienna
    search_url = "https://test.api.amadeus.com/v1/reference-data/locations/hotels/by-city"
    search_params = {"cityCode": "VIE"}  # Vienna
    
    try:
        print(f"Step 1 - Ricerca hotel a Vienna...")
        print(f"URL: {search_url}")
        print(f"Parametri: {search_params}")
        
        search_response = requests.get(search_url, params=search_params, headers=headers, timeout=15)
        print(f"Status: {search_response.status_code}")
        
        if search_response.status_code == 200:
            search_data = search_response.json()
            hotel_count = len(search_data.get("data", []))
            print(f"✅ Trovati {hotel_count} hotel!")
            
            if hotel_count > 0:
                # Take first 2 hotels for offers test
                hotel_ids = [hotel["hotelId"] for hotel in search_data.get("data", [])[:2]]
                print(f"Hotel IDs: {hotel_ids}")
                
                # Step 2: Get offers con date vicine
                from datetime import datetime, timedelta
                check_in = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
                check_out = (datetime.now() + timedelta(days=32)).strftime("%Y-%m-%d")
                
                offers_url = "https://test.api.amadeus.com/v3/shopping/hotel-offers"
                offers_params = {
                    "hotelIds": ",".join(hotel_ids),
                    "checkInDate": check_in,
                    "checkOutDate": check_out,
                    "adults": 1,
                    "currency": "EUR"
                }
                
                print(f"\nStep 2 - Ricerca offerte...")
                print(f"URL: {offers_url}")
                print(f"Parametri: {offers_params}")
                
                offers_response = requests.get(offers_url, params=offers_params, headers=headers, timeout=15)
                print(f"Status: {offers_response.status_code}")
                
                if offers_response.status_code == 200:
                    offers_data = offers_response.json()
                    offers_count = len(offers_data.get("data", []))
                    print(f"✅ Trovate {offers_count} offerte!")
                else:
                    print(f"❌ Errore nella ricerca offerte: {offers_response.status_code}")
                    print(f"Response: {offers_response.text[:300]}")
            
        else:
            print(f"❌ Errore nella ricerca hotel: {search_response.status_code}")
            print(f"Response: {search_response.text[:300]}")
            
    except Exception as e:
        print(f"❌ Errore richiesta hotel: {e}")

if __name__ == "__main__":
    print("🧪 Test API Amadeus")
    print("=" * 50)
    
    # Test authentication
    token = test_amadeus_auth()
    
    # Test flights
    test_flight_search(token)
    
    # Test hotels
    test_hotel_search(token)
    
    print("\n" + "=" * 50)
    print("Test completato!")