"""Orchestrator.
Coordinates the entire travel planning workflow.
"""
import logging
from typing import Dict, Any, Optional
from src.agents.query_parser import QueryParser
from src.agents.data_collector import DataCollector
from src.agents.rag_manager import RAGManager
from src.agents.plan_generator import PlanGenerator
from src.utils.exporter import TravelPlanExporter
from src.core import config

logger = logging.getLogger(__name__)


class Orchestrator:
    """
    Orchestrates the travel planning workflow.
    Coordinates all agents to process user queries and generate travel plans.
    """
    
    def __init__(self, api_key: str, export_dir: str = "exports"):
        """
        Initialize orchestrator with all agents.
        
        Args:
            api_key: OpenAI API key
            export_dir: Directory for exporting travel plans
        """
        logger.info("Initializing Orchestrator...")
        
        self.api_key = api_key
        
        # Initialize agents
        self.query_parser = QueryParser(api_key)
        self.data_collector = DataCollector(api_key)
        self.rag_manager = RAGManager(api_key)
        self.plan_generator = PlanGenerator(api_key)
        self.exporter = TravelPlanExporter(export_dir)
        
        # State
        self.travel_info = {}
        self.api_data = {}
        self.rag_context = ""
        self.last_plan = ""
        self.last_export_path = None
        
        logger.info("Orchestrator initialized successfully")
    
    def process_travel_request(self, user_query: str, auto_export: bool = True) -> str:
        """
        Process a user travel request and generate a complete travel plan.
        
        This is the main workflow that:
        1. Parses the user query to extract travel information
        2. Collects data from external APIs
        3. Retrieves relevant context from travel guides (RAG)
        4. Generates a comprehensive travel plan
        5. Optionally exports the plan to Markdown
        
        Args:
            user_query: User's travel query in natural language
            auto_export: If True, automatically export to Markdown (default: True)
        
        Returns:
            Complete travel plan as formatted string
        """
        logger.info("=" * 60)
        logger.info("Processing new travel request")
        logger.info("=" * 60)
        
        try:
            # Step 1: Parse Query
            logger.info("\n🔍 Step 1: Parsing user query...")
            self.travel_info = self.query_parser.parse_query(user_query)
            logger.info(f"✓ Extracted travel info: {self.travel_info['destination']}, "
                       f"{self.travel_info['country']} "
                       f"({self.travel_info['start_date']} to {self.travel_info['end_date']})")
            
            # Step 2: Collect API Data
            logger.info("\n📡 Step 2: Collecting data from external APIs...")
            self.api_data = self.data_collector.collect_all_data(self.travel_info)
            
            # Log what data was collected
            data_summary = []
            if self.api_data.get("flights") and not self.api_data["flights"].get("error"):
                flight_count = len(self.api_data["flights"].get("flights", []))
                data_summary.append(f"{flight_count} flights")
            if self.api_data.get("weather") and not self.api_data["weather"].get("error"):
                forecast_count = len(self.api_data["weather"].get("forecasts", []))
                data_summary.append(f"{forecast_count} day weather forecast")
            if self.api_data.get("monuments"):
                data_summary.append(f"{len(self.api_data['monuments'])} attractions")
            if self.api_data.get("events"):
                data_summary.append(f"{len(self.api_data['events'])} events")
            
            if data_summary:
                logger.info(f"✓ Collected: {', '.join(data_summary)}")
            else:
                logger.warning("⚠ No API data collected (check API configurations)")
            
            # Step 3: Retrieve RAG Context
            logger.info("\n📚 Step 3: Retrieving travel guides and context...")
            self.rag_context = self.rag_manager.get_travel_context(self.travel_info)
            
            if "No additional" in self.rag_context:
                logger.warning("⚠ No travel guides found in RAG system")
            else:
                logger.info("✓ Retrieved relevant travel guide information")
            
            # Step 4: Generate Plan
            logger.info("\n✍️ Step 4: Generating comprehensive travel plan...")
            travel_plan = self.plan_generator.generate_plan(
                travel_info=self.travel_info,
                api_data=self.api_data,
                rag_context=self.rag_context
            )
            logger.info("✓ Travel plan generated successfully")
            
            # Save plan in state
            self.last_plan = travel_plan
            
            # Step 5: Auto-export to Markdown (optional)
            if auto_export:
                logger.info("\n💾 Step 5: Exporting to Markdown and iCalendar...")
                try:
                    # Export Markdown
                    self.last_export_path = self.export_to_markdown(
                        travel_plan=travel_plan,
                        travel_info=self.travel_info
                    )
                    logger.info(f"✓ Markdown exported to: {self.last_export_path}")
                    
                    # Export iCalendar
                    ics_path = self.export_to_icalendar(
                        travel_plan=travel_plan,
                        travel_info=self.travel_info,
                        api_data=self.api_data
                    )
                    logger.info(f"✓ iCalendar exported to: {ics_path}")
                    
                except Exception as e:
                    logger.warning(f"⚠ Export failed (plan still available): {e}")
            
            logger.info("\n" + "=" * 60)
            logger.info("Travel request processed successfully")
            logger.info("=" * 60 + "\n")
            
            return travel_plan
            
        except Exception as e:
            logger.exception("Failed to process travel request")
            return self._generate_error_response(str(e))
    
    def handle_user_interaction(self, current_plan: str, user_input: str) -> Dict[str, Any]:
        """
        Handle user interaction after plan generation using LLM to determine intent.
        Can either modify the plan or provide additional information.
        
        Args:
            current_plan: Current travel plan
            user_input: User's input/question
        
        Returns:
            Dictionary with 'type' (modification/info/done) and 'response'
        """
        logger.info(f"Handling user interaction: {user_input[:100]}")
        
        try:
            # Use LLM to classify the intent and respond appropriately
            system_message = """Sei un assistente di viaggio intelligente. L'utente ha ricevuto un piano di viaggio 
e ora sta interagendo con te. Il tuo compito è riconoscere l'intento in linguaggio naturale, anche se non vengono usate parole chiave esplicite.

Identifica l'intento più adatto tra:
- "modification": l'utente chiede di cambiare o aggiornare parte del piano (aggiungere giorni, sostituire attività, modificare costi, ecc.)
- "information": l'utente desidera chiarimenti o dettagli aggiuntivi sul piano esistente senza modificarlo (es. "come arrivo in centro?", "quanto dura la visita?")
- "new_trip": l'utente vuole iniziare a pianificare un viaggio diverso o cambiare completamente destinazione/periodo
- "done": l'utente ringrazia, conclude, dice che è tutto o non necessita di altro

Esempi indicativi:
- "Perfetto così, grazie" → done
- "Potresti aggiungere un giorno al mare?" → modification
- "Mi spieghi come muovermi dall'aeroporto?" → information
- "In realtà vorrei andare a Tokyo a dicembre" → new_trip

Rispondi SEMPRE in formato JSON con questa struttura:
{
    "intent": "modification" | "information" | "new_trip" | "done",
    "response": "La tua risposta dettagliata in italiano"
}

Per "modification": restituisci un piano aggiornato o spiega come lo modificherai. 
Per "information": rispondi alla domanda con consigli concreti usando il piano esistente. 
Per "new_trip": conferma che hai compreso e invita l'utente a fornire i dettagli del nuovo viaggio. 
Per "done": chiudi con cortesia e conferma la conclusione.

Se il messaggio è ambiguo, scegli l'intento più utile per l'utente motivando brevemente nella risposta."""

            prompt = f"""Piano di Viaggio Attuale:
{current_plan}

Richiesta dell'utente:
{user_input}

Analizza la richiesta e rispondi in formato JSON come specificato."""

            response = self.plan_generator.call_llm(
                prompt=prompt,
                system_message=system_message,
                model=config.OPENAI_MODEL,
                temperature=0.3,
                max_tokens=3000
            )
            
            # Parse JSON response
            import json
            try:
                result = json.loads(response)
                logger.info(f"✓ Intent detected: {result.get('intent', 'unknown')}")
                return result
            except json.JSONDecodeError:
                # Fallback: treat as modification
                logger.warning("Could not parse JSON response, treating as modification")
                return {
                    "intent": "modification",
                    "response": response
                }
            
        except Exception as e:
            logger.error(f"Failed to handle user interaction: {e}")
            return {
                "intent": "error",
                "response": f"Mi dispiace, ho riscontrato un errore nell'elaborare la tua richiesta: {str(e)}"
            }
    
    def refine_plan(self, current_plan: str, refinement_query: str) -> str:
        """
        Refine an existing travel plan based on user feedback.
        
        Args:
            current_plan: Current travel plan
            refinement_query: User's refinement request
        
        Returns:
            Updated travel plan
        """
        logger.info(f"Refining plan based on: {refinement_query[:100]}")
        
        try:
            system_message = """You are a travel planning assistant helping to refine an existing travel plan.
The user has a current plan and wants to make changes or improvements.
Update the plan according to their request while maintaining consistency and practicality."""

            prompt = f"""Current Travel Plan:
{current_plan}

User's Refinement Request:
{refinement_query}

Please update the travel plan according to the user's request. Keep all other aspects 
of the plan that weren't mentioned in the refinement. Maintain the same format and 
structure as the original plan."""

            refined_plan = self.plan_generator.call_llm(
                prompt=prompt,
                system_message=system_message,
                model=config.OPENAI_MODEL,
                temperature=0.7,
                max_tokens=3000
            )
            
            logger.info("✓ Plan refined successfully")
            return refined_plan
            
        except Exception as e:
            logger.error(f"Failed to refine plan: {e}")
            return current_plan + f"\n\n[Note: Could not apply refinement: {str(e)}]"
    
    def export_to_markdown(
        self, 
        travel_plan: Optional[str] = None,
        travel_info: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Export travel plan to Markdown file.
        
        Args:
            travel_plan: Plan to export (default: last generated plan)
            travel_info: Travel info (default: last processed info)
            metadata: Additional metadata to include
        
        Returns:
            Path to exported file
        """
        plan = travel_plan or self.last_plan
        info = travel_info or self.travel_info
        
        if not plan:
            raise ValueError("No travel plan available to export")
        if not info:
            raise ValueError("No travel info available for export")
        
        return self.exporter.export_to_markdown(plan, info, metadata)
    
    def export_to_icalendar(
        self,
        travel_plan: Optional[str] = None,
        travel_info: Optional[Dict[str, Any]] = None,
        api_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Export travel plan to iCalendar (.ics) file.
        
        Args:
            travel_plan: Plan to export (default: last generated plan)
            travel_info: Travel info (default: last processed info)
            api_data: API data with flights and events (default: last collected data)
        
        Returns:
            Path to exported .ics file
        """
        plan = travel_plan or self.last_plan
        info = travel_info or self.travel_info
        data = api_data or self.api_data
        
        if not plan:
            raise ValueError("No travel plan available to export")
        if not info:
            raise ValueError("No travel info available for export")
        
        return self.exporter.export_to_icalendar(plan, info, data)
    
    def list_exports(self) -> list:
        """
        List all exported travel plans.
        
        Returns:
            List of exported files with metadata
        """
        return self.exporter.list_exported_plans()
    
    def _generate_error_response(self, error_message: str) -> str:
        """
        Generate a user-friendly error response.
        
        Args:
            error_message: Technical error message
        
        Returns:
            User-friendly error message
        """
        return f"""
# ⚠️ Si è verificato un problema

Mi dispiace, ma ho riscontrato un errore durante l'elaborazione della tua richiesta di viaggio.

**Dettagli tecnici:** {error_message}

## 💡 Cosa puoi fare:

1. **Verifica la tua richiesta**: Assicurati di aver specificato una destinazione e delle date valide
2. **Controlla la configurazione**: Verifica che le API key siano configurate correttamente nel file .env
3. **Riprova**: A volte i servizi esterni possono essere temporaneamente non disponibili

## Esempio di richiesta valida:
"Voglio andare a Parigi dal 15 al 19 novembre partendo da Roma"

Se il problema persiste, controlla i log per maggiori dettagli.
"""
