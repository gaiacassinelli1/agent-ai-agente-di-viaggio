"""Authentication manager for user login and registration.

Handles:
- User registration with password hashing
- User login and session management
- Password security (SHA-256 hashing)
"""
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any
from .database import TravelDB


class AuthManager:
    """Manages user authentication and registration."""
    
    def __init__(self, db: TravelDB):
        """
        Initialize authentication manager.
        
        Args:
            db: TravelDB instance
        """
        self.db = db
    
    def hash_password(self, password: str) -> str:
        """
        Hash password using SHA-256.
        
        Args:
            password: Plain text password
        
        Returns:
            Hashed password
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register(self, username: str, password: str, email: Optional[str] = None) -> bool:
        """
        Register a new user.
        
        Args:
            username: Username (must be unique)
            password: Plain text password
            email: Optional email address
        
        Returns:
            True if registration successful, False if username exists
        """
        # Check if username already exists
        existing_user = self.db.fetch_one(
            "SELECT id FROM users WHERE username = ?",
            (username,)
        )
        
        if existing_user:
            return False
        
        # Hash password and insert user
        password_hash = self.hash_password(password)
        
        try:
            self.db.execute_query(
                "INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)",
                (username, password_hash, email)
            )
            return True
        except Exception as e:
            print(f"Error during registration: {e}")
            return False
    
    def login(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate user login.
        
        Args:
            username: Username
            password: Plain text password
        
        Returns:
            User data dictionary if successful, None if failed
        """
        # Get user from database
        user = self.db.fetch_one(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        )
        
        if not user:
            return None
        
        # Verify password
        password_hash = self.hash_password(password)
        if password_hash != user['password_hash']:
            return None
        
        # Update last login timestamp
        self.db.execute_query(
            "UPDATE users SET last_login = ? WHERE id = ?",
            (datetime.now().isoformat(), user['id'])
        )
        
        # Return user data (without password hash)
        return {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'created_at': user['created_at'],
            'last_login': user['last_login']
        }
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
        
        Returns:
            User data dictionary or None
        """
        user = self.db.fetch_one(
            "SELECT id, username, email, created_at, last_login FROM users WHERE id = ?",
            (user_id,)
        )
        return user
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """
        Change user password.
        
        Args:
            user_id: User ID
            old_password: Current password
            new_password: New password
        
        Returns:
            True if successful, False otherwise
        """
        # Verify old password
        user = self.db.fetch_one(
            "SELECT password_hash FROM users WHERE id = ?",
            (user_id,)
        )
        
        if not user:
            return False
        
        old_password_hash = self.hash_password(old_password)
        if old_password_hash != user['password_hash']:
            return False
        
        # Update password
        new_password_hash = self.hash_password(new_password)
        self.db.execute_query(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (new_password_hash, user_id)
        )
        
        return True
    
    def delete_user(self, user_id: int) -> bool:
        """
        Delete user account and all associated data.
        
        Args:
            user_id: User ID
        
        Returns:
            True if successful
        """
        try:
            self.db.execute_query("DELETE FROM users WHERE id = ?", (user_id,))
            return True
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False
