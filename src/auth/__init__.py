"""Login module for Travel AI Assistant.

This module provides:
- User authentication (login/registration)
- Database management with SQLite
- Trip and plan persistence
- User session management
"""

from .database import TravelDB
from .auth_manager import AuthManager
from .trip_manager import TripManager

__all__ = ['TravelDB', 'AuthManager', 'TripManager']
