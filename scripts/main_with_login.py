"""
Main entry point for Travel AI Assistant v2 with Login System.

This CLI interface uses SessionManager for business logic,
making it easy to swap with web UI (Flask/Streamlit/Gradio).
"""
import os
import sys
import logging
from dotenv import load_dotenv

# Fix Unicode encoding issues on Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.core.orchestrator import Orchestrator
from src.core.session_manager import SessionManager
from src.core import config
from src.auth import TravelDB, AuthManager, TripManager
from src.auth.auth_cli import AuthCLI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('travel_assistant.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)


def print_welcome():
    """Print welcome message."""
    print("\n" + "=" * 70)
    print(" " * 15 + "🌍 TRAVEL AI ASSISTANT v2 🌍")
    print("=" * 70)
    print("\n✈️  Il tuo assistente personale per pianificare viaggi indimenticabili!")
    print("\n📝 Come funziona:")
    print("   1. Effettua il login o registrati")
    print("   2. Descrivi il tuo viaggio desiderato")
    print("   3. L'assistente raccoglie informazioni da varie fonti")
    print("   4. Ricevi un itinerario completo e personalizzato")
    print("   5. I tuoi viaggi vengono salvati automaticamente!")
    print("\n💡 Esempio di richiesta:")
    print('   "Voglio andare a Parigi dal 15 al 19 novembre partendo da Roma"')
    print("\n⌨️  Comandi speciali:")
    print("   - 'history' - Mostra storico viaggi")
    print("   - 'stats' - Mostra statistiche personali")
    print("   - 'done' - Finalizza viaggio corrente")
    print("   - 'logout' - Esci e permetti nuovo login")
    print("   - 'quit' - Esci dall'applicazione")
    print("\n" + "=" * 70 + "\n")


def main():
    """Main application loop."""
    # Load environment variables
    load_dotenv()
    
    # Validate configuration
    try:
        config.validate_config()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"\n❌ Errore di configurazione: {e}")
        print("\n💡 Assicurati di avere un file .env con tutte le chiavi API necessarie.")
        print("   Vedi .env.example per un template.")
        return
    
    # Get API key
    api_key = config.OPENAI_API_KEY
    if not api_key:
        print("\n❌ OPENAI_API_KEY non trovata!")
        print("   Crea un file .env e aggiungi: OPENAI_API_KEY=your_key_here")
        return
    
    # Initialize core components
    try:
        orchestrator = Orchestrator(api_key)
        db = TravelDB("travel_assistant.db")
        auth_manager = AuthManager(db)
        trip_manager = TripManager(db)
        session = SessionManager(db, auth_manager, trip_manager, orchestrator)
    except Exception as e:
        logger.exception("Failed to initialize application")
        print(f"\n❌ Errore durante l'inizializzazione: {e}")
        return
    
    # Print welcome
    print_welcome()
    
    # Authentication
    auth_cli = AuthCLI(db, auth_manager)
    user = auth_cli.run()
    
    if not user:
        print("\n⚠️  Autenticazione annullata.")
        db.close()
        return
    
    # Login to session using the pre-authenticated user object
    login_result = session.login_with_user_object(user)
    
    if not login_result['success']:
        print(f"\n❌ Errore: {login_result['error']}")
        db.close()
        return
    
    print(f"\n✨ Benvenuto, {user['username']}!")
    
    # Check for active trip
    if login_result.get('has_active_trip'):
        active_trip = login_result['active_trip']
        print(f"\n📌 Hai un viaggio attivo: {active_trip['destination']}")
        choice = input("   Vuoi continuare questo viaggio? (s/n): ").strip().lower()
        
        if choice in ['s', 'si', 'sì', 'y', 'yes']:
            load_result = session.load_trip(active_trip['id'])
            if load_result['success'] and load_result.get('plan'):
                print("\n" + "=" * 70)
                print(" " * 20 + "📝 PIANO SALVATO")
                print("=" * 70 + "\n")
                print(load_result['plan']['plan_content'])
                print("\n" + "=" * 70 + "\n")
        else:
            session.trip_mgr.deactivate_trip(active_trip['id'])
            print("✅ Viaggio precedente archiviato.")
    
    # Main interaction loop
    run_cli_loop(session, db, auth_manager, trip_manager, orchestrator)
    
    # Cleanup
    db.close()


def run_cli_loop(session: SessionManager, db: TravelDB, auth_manager: AuthManager, 
                 trip_manager: TripManager, orchestrator: Orchestrator):
    """
    Run the main CLI interaction loop.
    
    This function is separated to make it easy to replace with web UI.
    Supports logout and re-login functionality.
    
    Args:
        session: SessionManager instance
        db: Database instance
        auth_manager: AuthManager instance
        trip_manager: TripManager instance
        orchestrator: Orchestrator instance
    """
    while True:
        try:
            # Check if user is authenticated
            if not session.is_authenticated():
                print("\n🔒 Sessione scaduta. Effettua di nuovo il login.")
                auth_cli = AuthCLI(db, auth_manager)
                user = auth_cli.run()
                
                if not user:
                    print("\n👋 Arrivederci!")
                    break
                
                login_result = session.login_with_user_object(user)
                if not login_result['success']:
                    print(f"\n❌ Errore: {login_result['error']}")
                    break
                
                print(f"\n✨ Bentornato, {user['username']}!")
            
            # Get user query
            user_query = input("\n💬 In cosa posso essere utile? ").strip()
            
            # Check for exit commands
            if user_query.lower() in ['quit', 'exit', 'esci', 'q']:
                print("\n👋 Grazie per aver usato Travel AI Assistant!")
                print("   Buon viaggio! ✈️🌍")
                break
            
            # Check for logout
            if user_query.lower() == 'logout':
                logout_result = session.logout()
                print(f"\n✅ {logout_result['message']}")
                print("💡 Puoi effettuare un nuovo login o digitare 'quit' per uscire.")
                continue
            
            # Check for empty input
            if not user_query:
                print("⚠️  Per favore, inserisci una richiesta.")
                continue
            
            # Special commands
            if user_query.lower() == 'history':
                show_history(session)
                continue
            
            if user_query.lower() == 'stats':
                show_stats(session)
                continue
            
            # If no active plan, process as new trip
            if not session.current_plan:
                print("\n🤖 Sto elaborando la tua richiesta...")
                print("    (Questo potrebbe richiedere 30-60 secondi)\n")
                
                result = session.process_travel_query(user_query)
                
                if result['success']:
                    print("\n" + "=" * 70)
                    print(" " * 20 + "🎉 IL TUO PIANO DI VIAGGIO 🎉")
                    print("=" * 70 + "\n")
                    print(result['plan'])
                    print("\n" + "=" * 70 + "\n")
                    print("💾 Piano salvato automaticamente!")
                else:
                    print(f"\n❌ Errore: {result['error']}")
                    continue
            
            else:
                # Handle interaction with existing plan
                handle_interaction(session, user_query)
        
        except KeyboardInterrupt:
            print("\n\n👋 Interruzione ricevuta. Arrivederci!")
            break
        
        except Exception as e:
            logger.exception("Unexpected error in main loop")
            print(f"\n❌ Si è verificato un errore imprevisto: {e}")
            print("   Controlla i log per maggiori dettagli.")


def handle_interaction(session: SessionManager, user_input: str):
    """
    Handle user interaction with existing plan.
    
    Args:
        session: SessionManager instance
        user_input: User's input
    """
    # Check for manual done/quit
    if user_input.lower() in ['done', 'finito', 'basta', 'ok']:
        result = session.finalize_trip()
        print("\n✅ " + result['message'])
        print("   Buon viaggio! ✈️🌍")
        print("\n💡 Puoi pianificare un nuovo viaggio o digitare 'quit' per uscire.")
        return
    
    # Process with LLM
    print("\n🤖 Sto elaborando la tua richiesta...\n")
    
    result = session.handle_interaction(user_input)
    
    if not result['success']:
        print(f"❌ Errore: {result['error']}")
        return
    
    intent = result['intent']
    response = result['response']
    
    if intent == 'done':
        session.finalize_trip()
        print("\n✅ " + response)
        print("   Buon viaggio! ✈️🌍")
        print("\n💡 Puoi pianificare un nuovo viaggio o digitare 'quit' per uscire.")
    
    elif intent == 'modification':
        print("\n" + "-" * 70)
        print(" " * 25 + "📝 PIANO AGGIORNATO")
        print("-" * 70 + "\n")
        print(response)
        print("\n" + "-" * 70 + "\n")
        print("💾 Modifiche salvate!")
    
    elif intent == 'information':
        print("\n" + "-" * 70)
        print(" " * 20 + "ℹ️  INFORMAZIONI AGGIUNTIVE")
        print("-" * 70 + "\n")
        print(response)
        print("\n" + "-" * 70 + "\n")
    
    elif intent == 'new_trip':
        # Already processed as new trip in handle_interaction
        print("\n" + "=" * 70)
        print(" " * 20 + "🎉 IL TUO NUOVO PIANO DI VIAGGIO 🎉")
        print("=" * 70 + "\n")
        print(response)
        print("\n" + "=" * 70 + "\n")
        print("💾 Nuovo viaggio salvato!")
    
    else:
        print(f"\n⚠️  {response}")


def show_history(session: SessionManager):
    """Show user's trip history."""
    result = session.get_trip_history()
    
    if not result['success']:
        print(f"❌ {result['error']}")
        return
    
    trips = result['trips']
    
    if not trips:
        print("\n📭 Nessun viaggio salvato.")
        return
    
    print("\n" + "=" * 70)
    print(" " * 25 + "📚 STORICO VIAGGI")
    print("=" * 70 + "\n")
    
    for i, trip in enumerate(trips[:10], 1):  # Show last 10
        status = "🟢 Attivo" if trip['is_active'] else "⚪ Archiviato"
        print(f"{i}. {status} - {trip['destination']}, {trip['country']}")
        print(f"    📅 {trip['start_date']} → {trip['end_date']}")
        if trip['departure_city']:
            print(f"    ✈️  Da: {trip['departure_city']}")
        print(f"    🕒 Creato: {trip['created_at'][:10]}")
        print()
    
    print("=" * 70 + "\n")


def show_stats(session: SessionManager):
    """Show user statistics."""
    result = session.get_trip_history()
    
    if not result['success']:
        print(f"❌ {result['error']}")
        return
    
    stats = result['stats']
    
    print("\n" + "=" * 70)
    print(" " * 25 + "📊 STATISTICHE")
    print("=" * 70 + "\n")
    
    print(f"📍 Viaggi totali: {stats['total_trips']}")
    print(f"🟢 Viaggi attivi: {stats['active_trips']}")
    
    if stats['favorite_destinations']:
        print("\n🌟 Destinazioni preferite:")
        for dest in stats['favorite_destinations']:
            print(f"   • {dest['destination']}, {dest['country']} - {dest['visit_count']} volte")
    
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()
