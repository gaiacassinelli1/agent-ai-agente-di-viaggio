"""
Configuration module for Travel AI Assistant.
Loads environment variables and provides configuration constants.
"""
import os
from dotenv import load_dotenv

# Load environment variables from project root
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env_path = os.path.join(project_root, '.env')
load_dotenv(env_path)

# === API Keys ===
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AMADEUS_API_KEY = os.getenv("VOLI_API_KEY")
AMADEUS_API_SECRET = os.getenv("VOLI_API_SECRET")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
MONUMENTS_API_KEY = os.getenv("MONUMENTS_API_KEY")
TICKETMASTER_API_KEY = os.getenv("TICKETMASTER_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")



# === OpenAI Configuration ===
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))

# === API Configuration ===
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "15"))

# === RAG Configuration ===
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))
RAG_TOP_K = int(os.getenv("RAG_TOP_K", "5"))
RAG_CONTEXT_MAX_CHARS = int(os.getenv("RAG_CONTEXT_MAX_CHARS", "2800"))
RAG_CONTEXT_MAX_DOC_CHARS = int(os.getenv("RAG_CONTEXT_MAX_DOC_CHARS", "650"))
VECTOR_DB_DIR = "chroma_db"

# === GitHub Repository for Travel Guides ===
GITHUB_REPO_URL = "https://github.com/u7127755622-tech/Prova-"

# === API Endpoints ===
AMADEUS_TOKEN_URL = "https://test.api.amadeus.com/v1/security/oauth2/token"
AMADEUS_FLIGHT_URL = "https://test.api.amadeus.com/v2/shopping/flight-offers"
AMADEUS_HOTEL_SEARCH_URL = "https://test.api.amadeus.com/v1/reference-data/locations/hotels/by-city"
AMADEUS_HOTEL_URL = "https://test.api.amadeus.com/v3/shopping/hotel-offers"
OPENWEATHER_URL = "http://api.openweathermap.org/data/2.5/forecast"
GOOGLE_PLACES_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
TICKETMASTER_URL = "https://app.ticketmaster.com/discovery/v2/events.json"

#TODO: evitare l'utilizzo di questa fonte statica
# === Currency Data (Static fallback) ===
CURRENCY_DATA = {
    "Italy": {"currency": "EUR", "rate_vs_eur": "1.00"},
    "Spain": {"currency": "EUR", "rate_vs_eur": "1.00"},
    "France": {"currency": "EUR", "rate_vs_eur": "1.00"},
    "Germany": {"currency": "EUR", "rate_vs_eur": "1.00"},
    "United States": {"currency": "USD", "rate_vs_eur": "1 EUR = 1.08 USD"},
    "United Kingdom": {"currency": "GBP", "rate_vs_eur": "1 EUR = 0.86 GBP"},
    "Japan": {"currency": "JPY", "rate_vs_eur": "1 EUR = 165.20 JPY"},
    "Thailand": {"currency": "THB", "rate_vs_eur": "1 EUR = 39.50 THB"},
    "Brazil": {"currency": "BRL", "rate_vs_eur": "1 EUR = 5.75 BRL"},
    "Mexico": {"currency": "MXN", "rate_vs_eur": "1 EUR = 18.50 MXN"},
    "China": {"currency": "CNY", "rate_vs_eur": "1 EUR = 7.78 CNY"},
    "India": {"currency": "INR", "rate_vs_eur": "1 EUR = 88.50 INR"},
    "Turkey": {"currency": "TRY", "rate_vs_eur": "1 EUR = 35.10 TRY"},
}

def validate_config():
    """Validate that essential configuration is present."""
    missing = []
    if not OPENAI_API_KEY:
        missing.append("OPENAI_API_KEY")
    
    if missing:
        raise ValueError(f"Missing required configuration: {', '.join(missing)}")
    
    return True
