"""Example integration with main application.

This file shows how to integrate the login system with your existing
Travel AI Assistant application.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from login.database import TravelDB
from login.auth_manager import AuthManager
from login.trip_manager import TripManager
from login.auth_cli import AuthCLI


def example_integration():
    """Example of how to integrate login system with main app."""
    
    # 1. Initialize database and managers
    db = TravelDB("travel_assistant.db")
    auth_manager = AuthManager(db)
    trip_manager = TripManager(db)
    auth_cli = AuthCLI(db, auth_manager)
    
    # 2. Authenticate user
    print("\n" + "=" * 70)
    print(" " * 15 + "🌍 TRAVEL AI ASSISTANT v2 🌍")
    print("=" * 70)
    
    user = auth_cli.run()
    
    if not user:
        print("\n⚠️  Autenticazione annullata.")
        return
    
    user_id = user['id']
    
    # 3. Check for existing active trip
    active_trip = trip_manager.get_active_trip(user_id)
    
    if active_trip:
        print(f"\n📌 Hai un viaggio attivo: {active_trip['destination']}")
        choice = input("   Vuoi continuare questo viaggio? (s/n): ").strip().lower()
        
        if choice in ['s', 'si', 'sì', 'y', 'yes']:
            # Load existing plan
            latest_plan = trip_manager.get_latest_plan(active_trip['id'])
            if latest_plan:
                print("\n" + "=" * 70)
                print(" " * 20 + "📝 PIANO SALVATO")
                print("=" * 70 + "\n")
                print(latest_plan['plan_content'])
                print("\n" + "=" * 70 + "\n")
                current_trip_id = active_trip['id']
                current_plan = latest_plan['plan_content']
            else:
                current_trip_id = None
                current_plan = None
        else:
            # Deactivate old trip
            trip_manager.deactivate_trip(active_trip['id'])
            current_trip_id = None
            current_plan = None
    else:
        current_trip_id = None
        current_plan = None
    
    # 4. Main travel planning loop
    while True:
        user_query = input("\n💬 In cosa posso essere utile? ").strip()
        
        if user_query.lower() in ['quit', 'exit', 'esci', 'q']:
            print("\n👋 Grazie per aver usato Travel AI Assistant!")
            print("   Buon viaggio! ✈️🌍")
            break
        
        # Example: Create new trip
        if not current_trip_id:
            # Parse travel info (you would use your QueryParser here)
            # For demo, we'll create a simple trip
            current_trip_id = trip_manager.create_trip(
                user_id=user_id,
                destination="Paris",
                country="France",
                start_date="2025-11-15",
                end_date="2025-11-19"
            )
            print(f"✅ Nuovo viaggio creato (ID: {current_trip_id})")
        
        # Save user interaction
        trip_manager.save_interaction(
            trip_id=current_trip_id,
            user_input=user_query,
            intent="example",
            response="Example response"
        )
        
        # Here you would call your orchestrator.process_travel_request()
        # For now, just demonstrate saving
        print("🤖 [Qui verrebbe elaborata la richiesta...]")
        
        # Save plan (example)
        if user_query.lower() != 'stats':
            example_plan = f"Piano di viaggio generato per: {user_query}"
            trip_manager.save_plan(current_trip_id, example_plan)
            current_plan = example_plan
            print(f"💾 Piano salvato (versione {trip_manager.get_latest_plan(current_trip_id)['version']})")
        
        # Show stats command
        if user_query.lower() == 'stats':
            stats = trip_manager.get_user_stats(user_id)
            print("\n📊 Le tue statistiche:")
            print(f"   Viaggi totali: {stats['total_trips']}")
            print(f"   Viaggi attivi: {stats['active_trips']}")
            if stats['favorite_destinations']:
                print("\n   Destinazioni preferite:")
                for dest in stats['favorite_destinations']:
                    print(f"   - {dest['destination']}, {dest['country']} ({dest['visit_count']} volte)")
    
    # 5. Cleanup
    db.close()


if __name__ == "__main__":
    example_integration()
