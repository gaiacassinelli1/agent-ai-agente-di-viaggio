"""
Query Parser Agent.
Extracts structured travel information from natural language queries.
"""
import logging
from typing import Dict, Any
from datetime import datetime, timedelta
from src.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class QueryParser(BaseAgent):
    """
    Parses user queries to extract travel information.
    """
    
    def parse_query(self, query: str) -> Dict[str, Any]:
        """
        Extract structured travel information from a natural language query.
        
        Args:
            query: User's travel query in natural language
        
        Returns:
            Dictionary with extracted travel information:
            - destination: Destination city
            - country: Destination country
            - departure_city: Departure city
            - start_date: Trip start date (YYYY-MM-DD)
            - end_date: Trip end date (YYYY-MM-DD)
            - travelers: Number of travelers
            - budget: Budget level or amount
            - interests: List of interests
        """
        logger.info("Parsing query: %s", query[:100])
        
        system_message = """You are a travel information extraction specialist.
Extract travel details from user queries and return them in JSON format.
Always extract: destination city, country, departure city, dates, number of travelers, budget, and interests.
Use ISO date format (YYYY-MM-DD) for dates.
If information is not provided, use reasonable defaults.
If information is in italian, use english equivalents."""

        prompt = f"""Extract travel information from this query:

Query: "{query}"

Return a JSON object with these fields:
- destination: destination city name
- country: destination country name
- departure_city: departure city (if mentioned, otherwise "unknown")
- start_date: trip start date in YYYY-MM-DD format (if not specified, use a date 2 months from now)
- end_date: trip end date in YYYY-MM-DD format (if not specified, assume 3-day trip)
- travelers: number of travelers as string (default "1")
- budget: budget level ("low", "medium", "high", or "any")
- interests: array of interests (e.g., ["culture", "food", "nature", "history"])

Current date is {datetime.now().strftime("%Y-%m-%d")}.

Return only valid JSON, no explanations."""

        try:
            response = self.call_llm(
                prompt=prompt,
                system_message=system_message,
                temperature=0.1,
                response_format="json_object"
            )
            
            travel_info = self.safe_json_parse(response)
            
            # Validate and set defaults
            travel_info = self._validate_travel_info(travel_info)
            
            logger.info("Extracted travel info: %s", travel_info)
            return travel_info
            
        except Exception as e:
            logger.error(f"Failed to parse query: {e}")
            return self._get_default_travel_info()
    
    def _validate_travel_info(self, info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and fill in missing travel information with defaults.
        
        Args:
            info: Extracted travel information
        
        Returns:
            Validated travel information
        """
        defaults = self._get_default_travel_info()
        
        # Merge with defaults
        for key, default_value in defaults.items():
            if key not in info or not info[key]:
                info[key] = default_value
        
        # Validate dates
        try:
            start = datetime.strptime(info["start_date"], "%Y-%m-%d")
            end = datetime.strptime(info["end_date"], "%Y-%m-%d")
            
            # Ensure end date is after start date
            if end <= start:
                info["end_date"] = (start + timedelta(days=3)).strftime("%Y-%m-%d")
        except ValueError:
            # If date parsing fails, use defaults
            today = datetime.now()
            info["start_date"] = (today + timedelta(days=60)).strftime("%Y-%m-%d")
            info["end_date"] = (today + timedelta(days=63)).strftime("%Y-%m-%d")
        
        return info
    
    def _get_default_travel_info(self) -> Dict[str, Any]:
        """
        Get default travel information structure.
        
        Returns:
            Default travel info dictionary
        """
        today = datetime.now()
        default_start = today + timedelta(days=60)
        default_end = default_start + timedelta(days=3)
        
        return {
            "destination": "any",
            "country": "any",
            "departure_city": "unknown",
            "start_date": default_start.strftime("%Y-%m-%d"),
            "end_date": default_end.strftime("%Y-%m-%d"),
            "travelers": "1",
            "budget": "medium",
            "interests": ["culture", "tourism"]
        }
