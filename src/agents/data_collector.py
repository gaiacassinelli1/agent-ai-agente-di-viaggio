"""Data Collector Agent.
Handles all external API calls for flights, weather, monuments, events, and currency.
"""
import os
import json
import logging
import requests
from typing import Dict, Any, List, Optional
from src.agents.base_agent import BaseAgent
from src.core import config

logger = logging.getLogger(__name__)


class DataCollector(BaseAgent):
    """
    Collects data from various external APIs.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize data collector with API credentials."""
        super().__init__(api_key)
        self.amadeus_key = config.AMADEUS_API_KEY
        self.amadeus_secret = config.AMADEUS_API_SECRET
        self.weather_key = config.OPENWEATHER_API_KEY
        self.monuments_key = config.MONUMENTS_API_KEY
        self.ticketmaster_key = config.TICKETMASTER_API_KEY
        self.timeout = config.REQUEST_TIMEOUT
        self._amadeus_token = None
    
    def collect_all_data(self, travel_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Collect all available data for the travel destination.
        
        Args:
            travel_info: Parsed travel information
        
        Returns:
            Dictionary with all collected data
        """
        destination = travel_info.get("destination", "")
        country = travel_info.get("country", "")
        departure_city = travel_info.get("departure_city", "unknown")
        start_date = travel_info.get("start_date", "")
        
        results = {
            "flights": None,
            "weather": None,
            "monuments": None,
            "events": None,
            "currency": None,
            "accommodations": None
        }
        
        logger.info("Collecting data for destination: %s", destination)
        
        # Collect flights
        if departure_city != "unknown" and destination and start_date:
            try:
                results["flights"] = self.search_flights(
                    departure_city, destination, start_date
                )
            except Exception as e:
                logger.warning(f"Failed to fetch flights: {e}")
        
        # Collect weather
        if destination:
            try:
                results["weather"] = self.get_weather_forecast(destination)
            except Exception as e:
                logger.warning(f"Failed to fetch weather: {e}")
        
        # Collect monuments
        if destination:
            try:
                results["monuments"] = self.get_monuments(destination)
            except Exception as e:
                logger.warning(f"Failed to fetch monuments: {e}")
        
        # Collect events
        if destination:
            try:
                results["events"] = self.get_events(destination)
            except Exception as e:
                logger.warning(f"Failed to fetch events: {e}")
        
        # Collect accommodations
        if destination and start_date:
            try:
                end_date = travel_info.get("end_date", "")
                adults = travel_info.get("travelers", 1)
                results["accommodations"] = self.collect_accommodations(
                    destination, start_date, end_date, adults
                )
            except Exception as e:
                logger.warning(f"Failed to fetch accommodations: {e}")
        
        # Collect currency info
        if country:
            try:
                results["currency"] = self.get_currency_info(country)
            except Exception as e:
                logger.warning(f"Failed to fetch currency info: {e}")
        
        return results
    
    def search_flights(self, departure: str, destination: str, date: str) -> Dict[str, Any]:
        """
        Search for flights using Amadeus API.
        
        Args:
            departure: Departure city
            destination: Destination city
            date: Departure date (YYYY-MM-DD)
        
        Returns:
            Dictionary with flight information
        """
        if not self.amadeus_key or not self.amadeus_secret:
            logger.warning("Amadeus credentials not configured")
            return {"error": "Amadeus API not configured"}
        
        # Get IATA codes
        departure_iata = self._get_iata_code(departure)
        destination_iata = self._get_iata_code(destination)
        
        if not departure_iata or not destination_iata:
            logger.warning(f"Could not find IATA codes for {departure} or {destination}")
            return {"error": "Airport codes not found"}
        
        # Get access token
        token = self._get_amadeus_token()
        if not token:
            return {"error": "Failed to authenticate with Amadeus API"}
        
        # Search flights
        params = {
            "originLocationCode": departure_iata,
            "destinationLocationCode": destination_iata,
            "departureDate": date,
            "adults": 1,
            "max": 5,
            "currencyCode": "EUR"
        }
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }
        
        try:
            response = requests.get(
                config.AMADEUS_FLIGHT_URL,
                params=params,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            # Parse flight offers
            flights = []
            for offer in data.get("data", [])[:5]:
                itinerary = offer.get("itineraries", [{}])[0]
                segments = itinerary.get("segments", [])
                if segments:
                    first_segment = segments[0]
                    last_segment = segments[-1]
                    
                    flights.append({
                        "carrier": first_segment.get("carrierCode", "N/A"),
                        "flight_number": first_segment.get("number", "N/A"),
                        "departure_time": first_segment.get("departure", {}).get("at", "N/A"),
                        "arrival_time": last_segment.get("arrival", {}).get("at", "N/A"),
                        "price": offer.get("price", {}).get("total", "N/A"),
                        "currency": offer.get("price", {}).get("currency", "EUR")
                    })
            
            if flights:
                logger.info(f"Found {len(flights)} flights")
            else:
                logger.warning(f"No flights found for {departure} to {destination} on {date}")
            
            return {"flights": flights}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Flight search failed: {e}")
            return {"error": str(e)}
    
    def get_weather_forecast(self, city: str) -> Dict[str, Any]:
        """
        Get weather forecast for a city.
        
        Args:
            city: City name
        
        Returns:
            Dictionary with weather forecast
        """
        if not self.weather_key:
            logger.warning("OpenWeather API key not configured")
            return {"error": "Weather API not configured"}
        
        params = {
            "q": city,
            "appid": self.weather_key,
            "units": "metric",
            "lang": "it"
        }
        
        try:
            response = requests.get(
                config.OPENWEATHER_URL,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            # Parse forecast data
            forecasts = {}
            for item in data.get("list", []):
                date = item.get("dt_txt", "").split(" ")[0]
                if date not in forecasts:
                    forecasts[date] = {
                        "date": date,
                        "temp_max": item["main"]["temp_max"],
                        "temp_min": item["main"]["temp_min"],
                        "description": item["weather"][0]["description"]
                    }
                else:
                    # Update min/max
                    forecasts[date]["temp_max"] = max(
                        forecasts[date]["temp_max"],
                        item["main"]["temp_max"]
                    )
                    forecasts[date]["temp_min"] = min(
                        forecasts[date]["temp_min"],
                        item["main"]["temp_min"]
                    )
            
            logger.info(f"Found weather forecast for {len(forecasts)} days")
            return {"forecasts": list(forecasts.values())}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Weather fetch failed: {e}")
            return {"error": str(e)}
    
    def get_monuments(self, city: str) -> List[Dict[str, Any]]:
        """
        Get famous monuments and attractions in a city.
        
        Args:
            city: City name
        
        Returns:
            List of monuments
        """
        if not self.monuments_key:
            logger.warning("Google Places API key not configured")
            return []
        
        params = {
            "query": f"famous monuments in {city}",
            "key": self.monuments_key,
            "language": "it"
        }
        
        try:
            response = requests.get(
                config.GOOGLE_PLACES_URL,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            monuments = []
            for place in data.get("results", [])[:10]:
                monuments.append({
                    "name": place.get("name", ""),
                    "address": place.get("formatted_address", ""),
                    "rating": place.get("rating", 0)
                })
            
            logger.info(f"Found {len(monuments)} monuments")
            return monuments
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Monuments fetch failed: {e}")
            return []
    
    def get_events(self, city: str) -> List[Dict[str, Any]]:
        """
        Get upcoming events in a city.
        
        Args:
            city: City name
        
        Returns:
            List of events
        """
        if not self.ticketmaster_key:
            logger.warning("Ticketmaster API key not configured")
            return []
        
        params = {
            "apikey": self.ticketmaster_key,
            "city": city,
            "locale": "it",
            "size": 10,
            "sort": "date,asc"
        }
        
        try:
            response = requests.get(
                config.TICKETMASTER_URL,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            events = []
            for event in data.get("_embedded", {}).get("events", []):
                events.append({
                    "name": event.get("name", ""),
                    "date": event.get("dates", {}).get("start", {}).get("localDate", ""),
                    "venue": event.get("_embedded", {}).get("venues", [{}])[0].get("name", "")
                })
            
            logger.info(f"Found {len(events)} events")
            return events
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Events fetch failed: {e}")
            return []
    
    def get_currency_info(self, country: str) -> Dict[str, str]:
        """
        Get currency information for a country.
        
        Args:
            country: Country name
        
        Returns:
            Currency information
        """
        country_normalized = country.strip().title()
        currency_data = config.CURRENCY_DATA.get(country_normalized)
        
        if currency_data:
            logger.info(f"Found currency info for {country}")
            return currency_data
        else:
            logger.warning(f"No currency info for {country}")
            return {"currency": "Unknown", "rate_vs_eur": "N/A"}
    
    def collect_accommodations(
        self, 
        city: str, 
        check_in: str, 
        check_out: str = None, 
        adults: int = 1
    ) -> Dict[str, Any]:
        """
        Collect accommodation data using hybrid approach:
        1. Get pricing from Amadeus Hotel API
        2. Get variety/reviews from Google Places
        3. Merge data for comprehensive results
        
        Args:
            city: Destination city
            check_in: Check-in date (YYYY-MM-DD)
            check_out: Check-out date (YYYY-MM-DD), if None uses check_in + 3 days
            adults: Number of adults
        
        Returns:
            Dictionary with hotel data from both sources
        """
        from datetime import datetime, timedelta
        
        # Calculate check_out if not provided
        if not check_out:
            try:
                check_in_date = datetime.strptime(check_in, "%Y-%m-%d")
                check_out_date = check_in_date + timedelta(days=3)
                check_out = check_out_date.strftime("%Y-%m-%d")
            except ValueError:
                logger.warning(f"Invalid check-in date: {check_in}")
                check_out = check_in
        
        results = {
            "amadeus_hotels": [],
            "google_hotels": [],
            "merged_hotels": []
        }
        
        # 1. Get Amadeus hotel data (pricing, availability)
        try:
            amadeus_data = self._search_amadeus_hotels(city, check_in, check_out, adults)
            results["amadeus_hotels"] = amadeus_data
            logger.info(f"Found {len(amadeus_data)} hotels from Amadeus")
        except Exception as e:
            logger.warning(f"Amadeus hotel search failed: {e}")
        
        # 2. Get Google Places hotel data (variety, reviews)
        try:
            google_data = self._search_google_hotels(city)
            results["google_hotels"] = google_data
            logger.info(f"Found {len(google_data)} hotels from Google Places")
        except Exception as e:
            logger.warning(f"Google hotel search failed: {e}")
        
        # 3. Merge data (enrich Google results with Amadeus prices)
        results["merged_hotels"] = self._merge_hotel_data(
            results["google_hotels"],
            results["amadeus_hotels"]
        )
        
        logger.info(f"Merged {len(results['merged_hotels'])} hotel results")
        return results
    
    def _search_amadeus_hotels(
        self, 
        city: str, 
        check_in: str, 
        check_out: str, 
        adults: int
    ) -> List[Dict[str, Any]]:
        """
        Search hotels using Amadeus Hotel Search API (two-step process).
        
        Args:
            city: City name
            check_in: Check-in date (YYYY-MM-DD)
            check_out: Check-out date (YYYY-MM-DD)
            adults: Number of adults
        
        Returns:
            List of hotel offers with pricing
        """
        if not self.amadeus_key or not self.amadeus_secret:
            logger.warning("Amadeus credentials not configured")
            return []
        
        # Get IATA city code
        city_code = self._get_iata_code(city)
        if not city_code:
            logger.warning(f"Could not find IATA code for {city}")
            return []
        
        # Get access token
        token = self._get_amadeus_token()
        if not token:
            logger.error("Failed to authenticate with Amadeus API")
            return []
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }
        
        try:
            # Step 1: Get hotel IDs by city code
            search_params = {"cityCode": city_code}
            
            search_response = requests.get(
                config.AMADEUS_HOTEL_SEARCH_URL,
                params=search_params,
                headers=headers,
                timeout=self.timeout
            )
            search_response.raise_for_status()
            search_data = search_response.json()
            
            # Extract hotel IDs (limit to 5 to avoid quota issues with test API)
            hotel_ids = [hotel["hotelId"] for hotel in search_data.get("data", [])[:5]]
            
            if not hotel_ids:
                logger.warning(f"No hotels found in {city}")
                return []
            
            logger.info(f"Found {len(hotel_ids)} hotel IDs, fetching offers...")
            
            # Step 2: Get offers for those hotel IDs (with retry mechanism)
            offers_response = None
            
            # Try with all hotel IDs first, then reduce if it fails
            for attempt, batch_size in enumerate([len(hotel_ids), min(3, len(hotel_ids)), 1]):
                try:
                    current_hotel_ids = hotel_ids[:batch_size]
                    offers_params = {
                        "hotelIds": ",".join(current_hotel_ids),
                        "checkInDate": check_in,
                        "checkOutDate": check_out,
                        "adults": adults,
                        "currency": "EUR"
                    }
                    
                    # Log the request details for debugging
                    logger.info(f"Attempt {attempt + 1}: Hotel offers request with {len(current_hotel_ids)} hotels")
                    logger.info(f"Request params: {offers_params}")
                    
                    offers_response = requests.get(
                        config.AMADEUS_HOTEL_URL,
                        params=offers_params,
                        headers=headers,
                        timeout=self.timeout
                    )
                    
                    logger.info(f"Response status: {offers_response.status_code}")
                    offers_response.raise_for_status()
                    break  # Success, exit retry loop
                    
                except requests.exceptions.HTTPError as e:
                    logger.warning(f"Attempt {attempt + 1} failed with {batch_size} hotels: {e}")
                    if offers_response and offers_response.status_code == 400:
                        error_text = offers_response.text
                        logger.warning(f"Bad request response: {error_text[:200]}")
                        
                        # Check if it's a "RATE NOT AVAILABLE" error
                        if "RATE NOT AVAILABLE" in error_text:
                            logger.info("Rate not available for these dates/hotels - this is normal for test API")
                            if attempt == 2:  # Last attempt
                                logger.info("No rates available for any hotels, returning empty list")
                                return []
                        
                    if attempt == 2:  # Last attempt
                        raise  # Re-raise the exception to be caught by outer try-except
                    continue  # Try with fewer hotels
            
            if not offers_response:
                logger.error("All hotel offers requests failed")
                return []
            data = offers_response.json()
            
            # Parse hotel offers
            hotels = []
            for offer in data.get("data", [])[:10]:
                hotel_data = offer.get("hotel", {})
                offers_list = offer.get("offers", [])
                
                if offers_list:
                    best_offer = offers_list[0]
                    hotels.append({
                        "name": hotel_data.get("name", "N/A"),
                        "hotel_id": hotel_data.get("hotelId", ""),
                        "chain_code": hotel_data.get("chainCode", ""),
                        "price": best_offer.get("price", {}).get("total", "N/A"),
                        "currency": best_offer.get("price", {}).get("currency", "EUR"),
                        "room_type": best_offer.get("room", {}).get("typeEstimated", {}).get("category", "N/A"),
                        "beds": best_offer.get("room", {}).get("typeEstimated", {}).get("beds", 1),
                        "source": "amadeus"
                    })
            
            logger.info(f"Amadeus API returned {len(hotels)} hotels with offers")
            return hotels
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"Amadeus hotel API HTTP error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                error_text = e.response.text
                logger.error(f"Response content: {error_text[:500]}")
                
                # If it's a rate availability issue, return basic hotel info without prices
                if "RATE NOT AVAILABLE" in error_text and 'hotel_ids' in locals():
                    logger.info("Returning basic hotel info without pricing due to rate unavailability")
                    basic_hotels = []
                    for i, hotel_id in enumerate(hotel_ids[:3]):  # Limit to first 3
                        basic_hotels.append({
                            "name": f"Hotel in {city}",
                            "hotel_id": hotel_id,
                            "chain_code": "N/A",
                            "price": "Prezzi non disponibili per queste date",
                            "currency": "EUR",
                            "room_type": "Standard",
                            "beds": 1,
                            "source": "amadeus_basic"
                        })
                    return basic_hotels
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Amadeus hotel search failed: {e}")
            return []
    
    def _search_google_hotels(self, city: str) -> List[Dict[str, Any]]:
        """
        Search hotels using Google Places API.
        
        Args:
            city: City name
        
        Returns:
            List of hotels with reviews and details
        """
        if not self.monuments_key:  # Google Places API key
            logger.warning("Google Places API key not configured")
            return []
        
        params = {
            "query": f"hotels in {city}",
            "key": self.monuments_key,
            "language": "it",
            "type": "lodging"
        }
        
        try:
            response = requests.get(
                config.GOOGLE_PLACES_URL,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            hotels = []
            for place in data.get("results", [])[:15]:
                hotels.append({
                    "name": place.get("name", ""),
                    "address": place.get("formatted_address", ""),
                    "rating": place.get("rating", 0),
                    "user_ratings_total": place.get("user_ratings_total", 0),
                    "place_id": place.get("place_id", ""),
                    "price_level": place.get("price_level", 0),  # 0-4 scale
                    "source": "google"
                })
            
            logger.info(f"Google Places returned {len(hotels)} hotels")
            return hotels
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Google hotel search failed: {e}")
            return []
    
    def _merge_hotel_data(
        self, 
        google_hotels: List[Dict[str, Any]], 
        amadeus_hotels: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Merge hotel data from Google and Amadeus.
        Enrich Google results with Amadeus pricing where possible.
        
        Args:
            google_hotels: Hotels from Google Places
            amadeus_hotels: Hotels from Amadeus
        
        Returns:
            Merged list with best information from both sources
        """
        merged = []
        
        # Create name index for Amadeus hotels
        amadeus_by_name = {
            hotel["name"].lower().strip(): hotel 
            for hotel in amadeus_hotels
        }
        
        # Merge Google hotels with Amadeus pricing
        for google_hotel in google_hotels:
            hotel_name = google_hotel["name"].lower().strip()
            
            # Try to find matching Amadeus hotel
            amadeus_match = amadeus_by_name.get(hotel_name)
            
            if amadeus_match:
                # Merge data - Google info + Amadeus pricing
                merged_hotel = {
                    **google_hotel,
                    "price": amadeus_match["price"],
                    "currency": amadeus_match["currency"],
                    "room_type": amadeus_match["room_type"],
                    "has_pricing": True
                }
            else:
                # Only Google data
                merged_hotel = {
                    **google_hotel,
                    "price": "N/A",
                    "currency": "EUR",
                    "has_pricing": False
                }
            
            merged.append(merged_hotel)
        
        # Add Amadeus-only hotels (not in Google results)
        google_names = {h["name"].lower().strip() for h in google_hotels}
        for amadeus_hotel in amadeus_hotels:
            if amadeus_hotel["name"].lower().strip() not in google_names:
                merged.append({
                    "name": amadeus_hotel["name"],
                    "price": amadeus_hotel["price"],
                    "currency": amadeus_hotel["currency"],
                    "room_type": amadeus_hotel["room_type"],
                    "address": "N/A",
                    "rating": 0,
                    "user_ratings_total": 0,
                    "has_pricing": True,
                    "source": "amadeus"
                })
        
        # Sort by: 1) has pricing, 2) rating, 3) price
        merged.sort(
            key=lambda x: (
                -int(x["has_pricing"]),
                -x.get("rating", 0),
                float(x["price"]) if x["price"] != "N/A" else 9999
            )
        )
        
        return merged[:10]  # Return top 10
    
    def _get_amadeus_token(self) -> Optional[str]:
        """Get Amadeus API access token."""
        if self._amadeus_token:
            return self._amadeus_token
        
        data = {
            "grant_type": "client_credentials",
            "client_id": self.amadeus_key,
            "client_secret": self.amadeus_secret
        }
        
        try:
            response = requests.post(
                config.AMADEUS_TOKEN_URL,
                data=data,
                timeout=self.timeout
            )
            response.raise_for_status()
            self._amadeus_token = response.json().get("access_token")
            return self._amadeus_token
        except requests.exceptions.RequestException as e:
            logger.error(f"Amadeus authentication failed: {e}")
            return None
    
    def _get_iata_code(self, city: str) -> Optional[str]:
        """
        Get IATA airport code for a city.
        
        Args:
            city: City name
        
        Returns:
            IATA code or None
        """
        # Load IATA codes from JSON file
        try:
            json_path = os.path.join("data", "airports_iata.json")
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    iata_codes = json.load(f)
                    return iata_codes.get(city.strip().title())
        except Exception as e:
            logger.warning(f"Failed to load IATA codes: {e}")
        
        # Fallback to common airports
        fallback = {
            "Rome": "FCO",
            "Milan": "MXP",
            "Paris": "CDG",
            "London": "LHR",
            "Barcelona": "BCN",
            "Madrid": "MAD",
            "Berlin": "BER",
            "Amsterdam": "AMS",
            "New York": "JFK",
            "Tokyo": "NRT"
        }
        
        return fallback.get(city.strip().title())
