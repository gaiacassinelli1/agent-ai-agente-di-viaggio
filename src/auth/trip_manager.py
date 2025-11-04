"""Trip manager for handling travel plans and interactions.

Manages:
- Creating and retrieving trips
- Saving and versioning travel plans
- Recording user interactions
- Trip history and analytics
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from .database import TravelDB


class TripManager:
    """Manages trips, plans, and interactions."""
    
    def __init__(self, db: TravelDB):
        """
        Initialize trip manager.
        
        Args:
            db: TravelDB instance
        """
        self.db = db
    
    def create_trip(self, user_id: int, destination: str, country: str = "",
                   start_date: str = "", end_date: str = "",
                   departure_city: str = "") -> int:
        """
        Create a new trip.
        
        Args:
            user_id: User ID
            destination: Destination city
            country: Destination country
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            departure_city: Departure city
        
        Returns:
            Trip ID
        """
        cursor = self.db.execute_query(
            """INSERT INTO trips 
               (user_id, destination, country, start_date, end_date, departure_city)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, destination, country, start_date, end_date, departure_city)
        )
        return cursor.lastrowid
    
    def save_plan(self, trip_id: int, plan_content: str) -> int:
        """
        Save a travel plan (creates new version).
        
        Args:
            trip_id: Trip ID
            plan_content: Full plan text
        
        Returns:
            Plan ID
        """
        # Get current version number
        result = self.db.fetch_one(
            "SELECT MAX(version) as max_version FROM plans WHERE trip_id = ?",
            (trip_id,)
        )
        
        next_version = (result['max_version'] or 0) + 1
        
        # Insert new plan version
        cursor = self.db.execute_query(
            "INSERT INTO plans (trip_id, plan_content, version) VALUES (?, ?, ?)",
            (trip_id, plan_content, next_version)
        )
        
        # Update trip timestamp
        self.db.execute_query(
            "UPDATE trips SET updated_at = ? WHERE id = ?",
            (datetime.now().isoformat(), trip_id)
        )
        
        return cursor.lastrowid
    
    def get_latest_plan(self, trip_id: int) -> Optional[Dict[str, Any]]:
        """
        Get the latest plan for a trip.
        
        Args:
            trip_id: Trip ID
        
        Returns:
            Plan dictionary or None
        """
        return self.db.fetch_one(
            """SELECT * FROM plans 
               WHERE trip_id = ? 
               ORDER BY version DESC 
               LIMIT 1""",
            (trip_id,)
        )
    
    def get_all_plans(self, trip_id: int) -> List[Dict[str, Any]]:
        """
        Get all plan versions for a trip.
        
        Args:
            trip_id: Trip ID
        
        Returns:
            List of plan dictionaries
        """
        return self.db.fetch_all(
            "SELECT * FROM plans WHERE trip_id = ? ORDER BY version DESC",
            (trip_id,)
        )
    
    def save_interaction(self, trip_id: int, user_input: str,
                        intent: str = "", response: str = "") -> int:
        """
        Save a user interaction.
        
        Args:
            trip_id: Trip ID
            user_input: User's input text
            intent: Detected intent (modification/information/new_trip/done)
            response: System response
        
        Returns:
            Interaction ID
        """
        cursor = self.db.execute_query(
            """INSERT INTO interactions 
               (trip_id, user_input, intent, response)
               VALUES (?, ?, ?, ?)""",
            (trip_id, user_input, intent, response)
        )
        return cursor.lastrowid
    
    def get_trip(self, trip_id: int) -> Optional[Dict[str, Any]]:
        """
        Get trip by ID.
        
        Args:
            trip_id: Trip ID
        
        Returns:
            Trip dictionary or None
        """
        return self.db.fetch_one(
            "SELECT * FROM trips WHERE id = ?",
            (trip_id,)
        )
    
    def get_user_trips(self, user_id: int, active_only: bool = True) -> List[Dict[str, Any]]:
        """
        Get all trips for a user.
        
        Args:
            user_id: User ID
            active_only: Only return active trips
        
        Returns:
            List of trip dictionaries
        """
        query = "SELECT * FROM trips WHERE user_id = ?"
        if active_only:
            query += " AND is_active = 1"
        query += " ORDER BY created_at DESC"
        
        return self.db.fetch_all(query, (user_id,))
    
    def get_active_trip(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get the most recent active trip for a user.
        
        Args:
            user_id: User ID
        
        Returns:
            Trip dictionary or None
        """
        return self.db.fetch_one(
            """SELECT * FROM trips 
               WHERE user_id = ? AND is_active = 1 
               ORDER BY updated_at DESC 
               LIMIT 1""",
            (user_id,)
        )
    
    def deactivate_trip(self, trip_id: int) -> bool:
        """
        Mark a trip as inactive.
        
        Args:
            trip_id: Trip ID
        
        Returns:
            True if successful
        """
        try:
            self.db.execute_query(
                "UPDATE trips SET is_active = 0 WHERE id = ?",
                (trip_id,)
            )
            return True
        except Exception as e:
            print(f"Error deactivating trip: {e}")
            return False
    
    def delete_trip(self, trip_id: int) -> bool:
        """
        Delete a trip and all associated data.
        
        Args:
            trip_id: Trip ID
        
        Returns:
            True if successful
        """
        try:
            self.db.execute_query("DELETE FROM trips WHERE id = ?", (trip_id,))
            return True
        except Exception as e:
            print(f"Error deleting trip: {e}")
            return False
    
    def get_trip_interactions(self, trip_id: int) -> List[Dict[str, Any]]:
        """
        Get all interactions for a trip.
        
        Args:
            trip_id: Trip ID
        
        Returns:
            List of interaction dictionaries
        """
        return self.db.fetch_all(
            "SELECT * FROM interactions WHERE trip_id = ? ORDER BY created_at ASC",
            (trip_id,)
        )
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Get statistics for a user.
        
        Args:
            user_id: User ID
        
        Returns:
            Dictionary with statistics
        """
        total_trips = self.db.fetch_one(
            "SELECT COUNT(*) as count FROM trips WHERE user_id = ?",
            (user_id,)
        )
        
        active_trips = self.db.fetch_one(
            "SELECT COUNT(*) as count FROM trips WHERE user_id = ? AND is_active = 1",
            (user_id,)
        )
        
        destinations = self.db.fetch_all(
            """SELECT destination, country, COUNT(*) as visit_count 
               FROM trips 
               WHERE user_id = ? 
               GROUP BY destination, country 
               ORDER BY visit_count DESC""",
            (user_id,)
        )
        
        return {
            'total_trips': total_trips['count'] if total_trips else 0,
            'active_trips': active_trips['count'] if active_trips else 0,
            'favorite_destinations': destinations[:5]  # Top 5
        }
