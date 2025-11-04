"""Session manager for handling user state and trip context.

This module separates business logic from UI, making it easy to
integrate with web interfaces (Flask, Streamlit, Gradio, etc.)
"""
from typing import Optional, Dict, Any
from src.auth import TravelDB, AuthManager, TripManager


class SessionManager:
    """Manages user session, trips, and application state."""
    
    def __init__(self, db: TravelDB, auth_manager: AuthManager, 
                 trip_manager: TripManager, orchestrator):
        """
        Initialize session manager.
        
        Args:
            db: Database instance
            auth_manager: Authentication manager
            trip_manager: Trip manager
            orchestrator: Travel orchestrator
        """
        self.db = db
        self.auth = auth_manager
        self.trip_mgr = trip_manager
        self.orchestrator = orchestrator
        
        # Session state
        self.current_user: Optional[Dict[str, Any]] = None
        self.current_trip_id: Optional[int] = None
        self.current_plan: Optional[str] = None
        self.travel_info: Dict[str, Any] = {}
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        Login user.
        
        Args:
            username: Username
            password: Password
        
        Returns:
            Dict with success status and user data or error message
        """
        user = self.auth.login(username, password)
        
        if user:
            self.current_user = user
            # Check for active trip
            active_trip = self.trip_mgr.get_active_trip(user['id'])
            if active_trip:
                self.current_trip_id = active_trip['id']
                latest_plan = self.trip_mgr.get_latest_plan(active_trip['id'])
                if latest_plan:
                    self.current_plan = latest_plan['plan_content']
            
            return {
                'success': True,
                'user': user,
                'has_active_trip': active_trip is not None,
                'active_trip': active_trip
            }
        else:
            return {
                'success': False,
                'error': 'Username o password errati'
            }
    
    def login_with_user_object(self, user: Dict[str, Any]) -> Dict[str, Any]:
        """
        Login user with pre-authenticated user object (for CLI after auth_cli).
        
        Args:
            user: User dictionary from auth system
        
        Returns:
            Dict with success status and trip info
        """
        if not user or 'id' not in user:
            return {'success': False, 'error': 'Invalid user object'}
        
        self.current_user = user
        
        # Check for active trip
        active_trip = self.trip_mgr.get_active_trip(user['id'])
        if active_trip:
            self.current_trip_id = active_trip['id']
            latest_plan = self.trip_mgr.get_latest_plan(active_trip['id'])
            if latest_plan:
                self.current_plan = latest_plan['plan_content']
        
        return {
            'success': True,
            'user': user,
            'has_active_trip': active_trip is not None,
            'active_trip': active_trip
        }
    
    def register(self, username: str, password: str, email: str = None) -> Dict[str, Any]:
        """
        Register new user.
        
        Args:
            username: Username
            password: Password
            email: Optional email
        
        Returns:
            Dict with success status and message
        """
        success = self.auth.register(username, password, email)
        
        if success:
            return {
                'success': True,
                'message': f'Registrazione completata! Benvenuto {username}'
            }
        else:
            return {
                'success': False,
                'error': 'Username già esistente'
            }
    
    def logout(self):
        """Logout current user and clear session."""
        # Deactivate current trip if any
        if self.current_trip_id:
            self.trip_mgr.deactivate_trip(self.current_trip_id)
        
        self.current_user = None
        self.current_trip_id = None
        self.current_plan = None
        self.travel_info = {}
        
        return {
            'success': True,
            'message': 'Logout effettuato con successo'
        }
    
    def is_authenticated(self) -> bool:
        """
        Check if user is authenticated.
        
        Returns:
            True if user is logged in
        """
        return self.current_user is not None
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """
        Get current user info.
        
        Returns:
            User dict or None
        """
        return self.current_user
    
    def process_travel_query(self, user_query: str) -> Dict[str, Any]:
        """
        Process a new travel request.
        
        Args:
            user_query: User's travel query
        
        Returns:
            Dict with plan and trip info
        """
        if not self.current_user:
            return {'success': False, 'error': 'User not logged in'}
        
        try:
            # Generate travel plan
            travel_plan = self.orchestrator.process_travel_request(user_query)
            
            # Get travel info from orchestrator
            self.travel_info = self.orchestrator.travel_info
            
            # Create trip in database
            self.current_trip_id = self.trip_mgr.create_trip(
                user_id=self.current_user['id'],
                destination=self.travel_info.get('destination', ''),
                country=self.travel_info.get('country', ''),
                start_date=self.travel_info.get('start_date', ''),
                end_date=self.travel_info.get('end_date', ''),
                departure_city=self.travel_info.get('departure_city', '')
            )
            
            # Save plan
            self.trip_mgr.save_plan(self.current_trip_id, travel_plan)
            self.current_plan = travel_plan
            
            # Save initial interaction
            self.trip_mgr.save_interaction(
                trip_id=self.current_trip_id,
                user_input=user_query,
                intent='new_trip',
                response=travel_plan
            )
            
            return {
                'success': True,
                'plan': travel_plan,
                'trip_id': self.current_trip_id,
                'travel_info': self.travel_info
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def handle_interaction(self, user_input: str) -> Dict[str, Any]:
        """
        Handle user interaction with existing plan.
        
        Args:
            user_input: User's input
        
        Returns:
            Dict with intent and response
        """
        if not self.current_user:
            return {'success': False, 'error': 'User not logged in'}
        
        if not self.current_plan:
            return {'success': False, 'error': 'No active plan'}
        
        try:
            # Get LLM response
            result = self.orchestrator.handle_user_interaction(
                self.current_plan, 
                user_input
            )
            
            intent = result.get('intent', 'unknown')
            response = result.get('response', '')
            
            # Handle different intents
            if intent == 'new_trip':
                # Process as new trip
                return self.process_travel_query(user_input)
            
            elif intent == 'modification':
                # Update current plan
                self.current_plan = response
                # Save new version
                if self.current_trip_id:
                    self.trip_mgr.save_plan(self.current_trip_id, response)
                    self.trip_mgr.save_interaction(
                        trip_id=self.current_trip_id,
                        user_input=user_input,
                        intent=intent,
                        response=response
                    )
            
            elif intent in ['information', 'done']:
                # Save interaction only
                if self.current_trip_id:
                    self.trip_mgr.save_interaction(
                        trip_id=self.current_trip_id,
                        user_input=user_input,
                        intent=intent,
                        response=response
                    )
            
            return {
                'success': True,
                'intent': intent,
                'response': response,
                'updated_plan': self.current_plan if intent == 'modification' else None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_trip_history(self) -> Dict[str, Any]:
        """
        Get user's trip history.
        
        Returns:
            Dict with trips and stats
        """
        if not self.current_user:
            return {'success': False, 'error': 'User not logged in'}
        
        trips = self.trip_mgr.get_user_trips(self.current_user['id'], active_only=False)
        stats = self.trip_mgr.get_user_stats(self.current_user['id'])
        
        return {
            'success': True,
            'trips': trips,
            'stats': stats
        }
    
    def load_trip(self, trip_id: int) -> Dict[str, Any]:
        """
        Load a specific trip.
        
        Args:
            trip_id: Trip ID to load
        
        Returns:
            Dict with trip and plan data
        """
        if not self.current_user:
            return {'success': False, 'error': 'User not logged in'}
        
        trip = self.trip_mgr.get_trip(trip_id)
        
        if not trip or trip['user_id'] != self.current_user['id']:
            return {'success': False, 'error': 'Trip not found or unauthorized'}
        
        latest_plan = self.trip_mgr.get_latest_plan(trip_id)
        
        self.current_trip_id = trip_id
        self.current_plan = latest_plan['plan_content'] if latest_plan else None
        
        return {
            'success': True,
            'trip': trip,
            'plan': latest_plan
        }
    
    def finalize_trip(self) -> Dict[str, Any]:
        """
        Finalize current trip and deactivate it.
        
        Returns:
            Dict with success status
        """
        if not self.current_trip_id:
            return {'success': False, 'error': 'No active trip'}
        
        self.trip_mgr.deactivate_trip(self.current_trip_id)
        
        trip_data = {
            'trip_id': self.current_trip_id,
            'plan': self.current_plan
        }
        
        # Clear current state
        self.current_trip_id = None
        self.current_plan = None
        self.travel_info = {}
        
        return {
            'success': True,
            'message': 'Viaggio finalizzato!',
            'trip_data': trip_data
        }
