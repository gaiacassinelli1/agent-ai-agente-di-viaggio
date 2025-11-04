"""CLI interface for user authentication.

Provides a command-line interface for:
- User login
- User registration
- Password management
"""
import getpass
from typing import Optional, Dict, Any
from .database import TravelDB
from .auth_manager import AuthManager


class AuthCLI:
    """Command-line interface for authentication."""
    
    def __init__(self, db: TravelDB, auth_manager: AuthManager):
        """
        Initialize authentication CLI.
        
        Args:
            db: TravelDB instance
            auth_manager: AuthManager instance
        """
        self.db = db
        self.auth = auth_manager
    
    def show_menu(self) -> str:
        """
        Display authentication menu.
        
        Returns:
            User choice
        """
        print("\n" + "=" * 70)
        print(" " * 20 + "🔐 AUTENTICAZIONE")
        print("=" * 70)
        print("\n1. 🔑 Login")
        print("2. ✏️  Registrati")
        print("3. ❌ Esci")
        print("\n" + "=" * 70)
        
        return input("\n💬 Scegli un'opzione (1-3): ").strip()
    
    def login_flow(self) -> Optional[Dict[str, Any]]:
        """
        Handle login flow.
        
        Returns:
            User data if successful, None otherwise
        """
        print("\n" + "-" * 70)
        print(" " * 25 + "🔑 LOGIN")
        print("-" * 70 + "\n")
        
        max_attempts = 3
        attempts = 0
        
        while attempts < max_attempts:
            username = input("👤 Username: ").strip()
            
            if not username:
                print("⚠️  Username non può essere vuoto.")
                continue
            
            # Use getpass to hide password (works in most terminals)
            try:
                password = getpass.getpass("🔐 Password: ")
            except:
                # Fallback if getpass doesn't work
                password = input("🔐 Password: ").strip()
            
            user = self.auth.login(username, password)
            
            if user:
                print(f"\n✅ Login effettuato con successo!")
                print(f"   Benvenuto, {user['username']}! 👋")
                return user
            else:
                attempts += 1
                remaining = max_attempts - attempts
                if remaining > 0:
                    print(f"\n❌ Username o password errati.")
                    print(f"   Tentativi rimasti: {remaining}")
                else:
                    print("\n❌ Troppi tentativi falliti.")
        
        return None
    
    def register_flow(self) -> bool:
        """
        Handle registration flow.
        
        Returns:
            True if successful, False otherwise
        """
        print("\n" + "-" * 70)
        print(" " * 25 + "✏️  REGISTRAZIONE")
        print("-" * 70 + "\n")
        
        # Get username
        while True:
            username = input("👤 Scegli un username: ").strip()
            
            if not username:
                print("⚠️  Username non può essere vuoto.")
                continue
            
            if len(username) < 3:
                print("⚠️  Username deve essere almeno 3 caratteri.")
                continue
            
            break
        
        # Get password
        while True:
            try:
                password = getpass.getpass("🔐 Scegli una password: ")
                password_confirm = getpass.getpass("🔐 Conferma password: ")
            except:
                password = input("🔐 Scegli una password: ").strip()
                password_confirm = input("🔐 Conferma password: ").strip()
            
            if not password:
                print("⚠️  Password non può essere vuota.")
                continue
            
            if len(password) < 6:
                print("⚠️  Password deve essere almeno 6 caratteri.")
                continue
            
            if password != password_confirm:
                print("⚠️  Le password non corrispondono.")
                continue
            
            break
        
        # Get email (optional)
        email = input("📧 Email (opzionale, premi Enter per saltare): ").strip()
        if email and "@" not in email:
            print("⚠️  Email non valida, continuo senza email.")
            email = None
        
        # Register user
        success = self.auth.register(username, password, email)
        
        if success:
            print("\n✅ Registrazione completata con successo!")
            print(f"   Puoi ora effettuare il login con username: {username}")
            return True
        else:
            print("\n❌ Registrazione fallita.")
            print("   Username già esistente o errore del database.")
            return False
    
    def run(self) -> Optional[Dict[str, Any]]:
        """
        Run authentication flow.
        
        Returns:
            User data if authenticated, None otherwise
        """
        while True:
            choice = self.show_menu()
            
            if choice == "1":
                user = self.login_flow()
                if user:
                    return user
            
            elif choice == "2":
                self.register_flow()
                # After registration, loop back to menu
            
            elif choice == "3":
                print("\n👋 Arrivederci!")
                return None
            
            else:
                print("\n⚠️  Scelta non valida. Riprova.")
