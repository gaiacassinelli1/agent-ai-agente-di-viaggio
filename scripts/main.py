"""
Main entry point for Travel AI Assistant v2.
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
from src.core import config

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
    print(" " * 15 + "🌍 Agente di vIAggio v2.0 🌍")
    print("=" * 70)
    print("\n✈️  Il tuo assistente personale per pianificare viaggi indimenticabili!")
    print("\n📝 Come funziona:")
    print("   1. Descrivi il tuo viaggio desiderato")
    print("   2. L'assistente raccoglie informazioni da varie fonti")
    print("   3. Ricevi un itinerario completo e personalizzato")
    print("   4. Il piano viene automaticamente salvato in formato Markdown")
    print("\n💡 Esempio di richiesta:")
    print('   "Voglio andare a Parigi dal 15 al 19 novembre partendo da Roma"')
    print("\n⌨️  Comandi:")
    print("   - Scrivi 'quit' o 'exit' per uscire")
    print("   - Dopo aver ricevuto un piano, puoi chiedere modifiche")
    print("   - Scrivi 'exports' per vedere tutti i piani salvati")
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
    
    # Initialize orchestrator
    try:
        orchestrator = Orchestrator(api_key)
    except Exception as e:
        logger.exception("Failed to initialize orchestrator")
        print(f"\n❌ Errore durante l'inizializzazione: {e}")
        return
    
    # Print welcome
    print_welcome()
    
    # Main interaction loop
    while True:
        try:
            # Get user query
            user_query = input("In cosa posso essere utile? ").strip()
            
            # Check for exit commands
            if user_query.lower() in ['quit', 'exit', 'esci', 'q']:
                print("\n👋 Grazie per aver usato Travel AI Assistant!")
                print("   Buon viaggio! ✈️🌍")
                break
            
            # Check for exports command
            if user_query.lower() in ['exports', 'export', 'lista', 'list']:
                print("\n📁 Piani di viaggio salvati:")
                print("-" * 70)
                exports = orchestrator.list_exports()
                if exports:
                    for i, exp in enumerate(exports, 1):
                        print(f"\n{i}. {exp['filename']}")
                        print(f"   📊 Dimensione: {exp['size_kb']} KB")
                        print(f"   📅 Creato: {exp['created']}")
                        print(f"   📝 Modificato: {exp['modified']}")
                        print(f"   📂 Percorso: {exp['path']}")
                else:
                    print("\nNessun piano salvato ancora.")
                print("-" * 70 + "\n")
                continue
            
            # Check for empty input
            if not user_query:
                print("⚠️  Per favore, inserisci una descrizione del viaggio.")
                continue
            
            # Process travel request
            print("\n🤖 Sto elaborando la tua richiesta...")
            print("    (Questo potrebbe richiedere 30-60 secondi)\n")
            
            travel_plan = orchestrator.process_travel_request(user_query)
            
            # Display the plan
            print("\n" + "=" * 70)
            print(" " * 20 + "🎉 IL TUO PIANO DI VIAGGIO 🎉")
            print("=" * 70 + "\n")
            print(travel_plan)
            print("\n" + "=" * 70 + "\n")
            
            # Show export paths if available
            if orchestrator.last_export_path:
                print(f"\n💾 File salvati:")
                print(f"   📝 Markdown: {orchestrator.last_export_path}")
                
                # Cerca file .ics corrispondente
                import os
                md_base = os.path.splitext(orchestrator.last_export_path)[0]
                ics_path = md_base + ".ics"
                if os.path.exists(ics_path):
                    print(f"   📅 Calendar: {ics_path}")
                    print(f"\n💡 Tip: Apri il file .ics per importare il viaggio nel tuo calendario!")
            
            print("\n")
            
            # Refinement loop
            current_plan = travel_plan
            while True:
                refinement = input(
                    "💬 Vuoi modificare qualcosa? "
                    "(scrivi le modifiche o 'done' per finire): "
                ).strip()
                
                if not refinement:
                    continue
                
                if refinement.lower() in ['done', 'no', 'n', 'ok']:
                    print("\n✅ Piano finalizzato!")
                    print("   Salva questo piano e inizia a preparare la valigia! 🧳")
                    break
                
                if refinement.lower() in ['quit', 'exit', 'esci', 'q']:
                    print("\n👋 Arrivederci!")
                    return
                
                # Apply refinement
                print("\n🔄 Sto applicando le modifiche...\n")
                try:
                    updated_plan = orchestrator.refine_plan(current_plan, refinement)
                    print("\n" + "-" * 70)
                    print(" " * 25 + "📝 PIANO AGGIORNATO")
                    print("-" * 70 + "\n")
                    print(updated_plan)
                    print("\n" + "-" * 70 + "\n")
                    current_plan = updated_plan
                except Exception as e:
                    logger.exception("Failed to refine plan")
                    print(f"⚠️  Non sono riuscito ad applicare le modifiche: {e}")
                    print("   Riprova con una richiesta diversa o digita 'done'.")
            
            # Ask if user wants to plan another trip
            another = input("\n🌍 Vuoi pianificare un altro viaggio? (sì/no): ").strip().lower()
            if another not in ['sì', 'si', 'yes', 'y', 's']:
                print("\n👋 Grazie per aver usato Travel AI Assistant!")
                print("   Buon viaggio! ✈️🌍")
                break
            
            print("\n" + "=" * 70 + "\n")
        
        except KeyboardInterrupt:
            print("\n\n👋 Interruzione ricevuta. Arrivederci!")
            break
        
        except Exception as e:
            logger.exception("Unexpected error in main loop")
            print(f"\n❌ Si è verificato un errore imprevisto: {e}")
            print("   Controlla i log per maggiori dettagli.")
            print("   Puoi riprovare o digitare 'exit' per uscire.\n")


if __name__ == "__main__":
    main()
