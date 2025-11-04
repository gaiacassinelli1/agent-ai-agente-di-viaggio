"""Plan Generator Agent.
Generates the final travel itinerary from collected data.
"""
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from src.agents.base_agent import BaseAgent
from src.core import config

logger = logging.getLogger(__name__)


class PlanGenerator(BaseAgent):
    """
    Generates comprehensive travel plans from collected data.
    """
    
    def generate_plan(
        self,
        travel_info: Dict[str, Any],
        api_data: Dict[str, Any],
        rag_context: str
    ) -> str:
        """
        Generate a comprehensive travel plan.
        
        Args:
            travel_info: Parsed travel information
            api_data: Data collected from APIs
            rag_context: Context from RAG system
        
        Returns:
            Formatted travel plan as string
        """
        logger.info("Generating travel plan...")
        
        # Build comprehensive context
        context = self._build_context(travel_info, api_data, rag_context)
        
        # Generate plan with LLM
        plan = self._generate_with_llm(context, travel_info)
        
        logger.info("Travel plan generated successfully")
        return plan
    
    def _build_context(
        self,
        travel_info: Dict[str, Any],
        api_data: Dict[str, Any],
        rag_context: str
    ) -> str:
        """
        Build comprehensive context for LLM.
        
        Args:
            travel_info: Travel information
            api_data: API data
            rag_context: RAG context
        
        Returns:
            Formatted context string
        """
        sections = []
        trip_window = self._compute_trip_window(travel_info)
        
        # Travel Information
        sections.append("=== TRAVEL DETAILS ===")
        sections.append(f"Destination: {travel_info.get('destination', 'N/A')}, {travel_info.get('country', 'N/A')}")
        sections.append(f"Departure City: {travel_info.get('departure_city', 'N/A')}")
        sections.append(f"Dates: {travel_info.get('start_date', 'N/A')} to {travel_info.get('end_date', 'N/A')}")
        if trip_window:
            sections.append(f"Duration (days): {trip_window['days']}")
            sections.append("Daily Dates: " + ", ".join(trip_window['date_labels']))
        sections.append(f"Travelers: {travel_info.get('travelers', '1')}")
        sections.append(f"Budget: {travel_info.get('budget', 'medium')}")
        sections.append(f"Interests: {', '.join(travel_info.get('interests', []))}")
        sections.append("")
        
        # Flights
        if api_data.get("flights") and not api_data["flights"].get("error"):
            sections.append("=== AVAILABLE FLIGHTS ===")
            flights = api_data["flights"].get("flights", [])
            for i, flight in enumerate(flights[:5], 1):
                sections.append(f"\nFlight {i}:")
                sections.append(f"  Carrier: {flight.get('carrier', 'N/A')} {flight.get('flight_number', 'N/A')}")
                sections.append(f"  Departure: {flight.get('departure_time', 'N/A')}")
                sections.append(f"  Arrival: {flight.get('arrival_time', 'N/A')}")
                sections.append(f"  Price: {flight.get('price', 'N/A')} {flight.get('currency', 'EUR')}")
            sections.append("")
        
        # Weather
        if api_data.get("weather") and not api_data["weather"].get("error"):
            sections.append("=== WEATHER FORECAST ===")
            forecasts = api_data["weather"].get("forecasts", [])
            for forecast in forecasts[:5]:
                sections.append(f"{forecast.get('date', 'N/A')}: "
                              f"{forecast.get('temp_min', 'N/A')}°C - {forecast.get('temp_max', 'N/A')}°C, "
                              f"{forecast.get('description', 'N/A')}")
            sections.append("")
        
        # Monuments
        if api_data.get("monuments"):
            sections.append("=== TOP ATTRACTIONS ===")
            for i, monument in enumerate(api_data["monuments"][:10], 1):
                sections.append(f"{i}. {monument.get('name', 'N/A')}")
                sections.append(f"   Address: {monument.get('address', 'N/A')}")
                sections.append(f"   Rating: {monument.get('rating', 'N/A')}/5")
            sections.append("")
        
        # Events
        if api_data.get("events"):
            sections.append("=== UPCOMING EVENTS ===")
            for i, event in enumerate(api_data["events"][:10], 1):
                sections.append(f"{i}. {event.get('name', 'N/A')}")
                sections.append(f"   Date: {event.get('date', 'N/A')}")
                sections.append(f"   Venue: {event.get('venue', 'N/A')}")
            sections.append("")
        
        # Currency
        if api_data.get("currency"):
            currency = api_data["currency"]
            if currency.get("currency") != "EUR":
                sections.append("=== CURRENCY INFORMATION ===")
                sections.append(f"Local Currency: {currency.get('currency', 'N/A')}")
                sections.append(f"Exchange Rate: {currency.get('rate_vs_eur', 'N/A')}")
                sections.append("")

        # Budget Inputs summary
        budget_inputs = self._collect_budget_inputs(api_data)
        if budget_inputs:
            sections.append("=== BUDGET INPUTS ===")
            sections.extend(budget_inputs)
            sections.append("")
        
        # RAG Context
        if rag_context and "No additional" not in rag_context:
            sections.append(rag_context)
            sections.append("")
        
        return "\n".join(sections)

    def _compute_trip_window(self, travel_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Return duration info for the itinerary if dates are available."""
        start_raw = travel_info.get('start_date')
        end_raw = travel_info.get('end_date')
        start_dt = self._parse_date(start_raw)
        end_dt = self._parse_date(end_raw)

        if not start_dt or not end_dt or end_dt < start_dt:
            return None

        days = (end_dt - start_dt).days + 1
        date_labels = [
            (start_dt + timedelta(days=i)).strftime('%Y-%m-%d')
            for i in range(days)
        ]

        return {
            'days': days,
            'start_date': start_dt,
            'end_date': end_dt,
            'start_label': start_dt.strftime('%Y-%m-%d'),
            'end_label': end_dt.strftime('%Y-%m-%d'),
            'date_labels': date_labels
        }

    def _collect_budget_inputs(self, api_data: Dict[str, Any]) -> List[str]:
        """Aggregate available price information to feed the LLM budget section."""
        inputs: List[str] = []

        flights_data = api_data.get('flights') or {}
        if flights_data and not flights_data.get('error'):
            flights = flights_data.get('flights', [])
            price_values: List[float] = []
            display_entries: List[str] = []
            currency = None

            for flight in flights[:5]:
                price = flight.get('price')
                if price is None:
                    continue
                currency = flight.get('currency', currency or 'EUR')
                display_entries.append(f"{price} {currency} ({flight.get('carrier', 'N/A')} {flight.get('flight_number', '')})")
                value = self._to_float(price)
                if value is not None:
                    price_values.append(value)

            if display_entries:
                if price_values:
                    inputs.append(f"- Voli: fascia stimata {min(price_values):.2f}-{max(price_values):.2f} {currency or 'EUR'} (fonte API voli)")
                else:
                    inputs.append(f"- Voli: prezzi indicativi {', '.join(display_entries)}")

        events = api_data.get('events') or []
        event_entries: List[str] = []
        for event in events[:5]:
            raw_price = event.get('price') or event.get('min_price') or event.get('max_price')
            if raw_price:
                event_entries.append(f"{event.get('name', 'Evento')} - {raw_price}")
        if event_entries:
            inputs.append(f"- Eventi: {', '.join(event_entries)}")

        monuments = api_data.get('monuments') or []
        monument_entries: List[str] = []
        for monument in monuments[:5]:
            ticket = monument.get('ticket_price') or monument.get('price')
            if ticket:
                monument_entries.append(f"{monument.get('name', 'Attrazione')} - {ticket}")
        if monument_entries:
            inputs.append(f"- Attrazioni: {', '.join(monument_entries)}")

        return inputs

    @staticmethod
    def _to_float(value: Any) -> Optional[float]:
        try:
            cleaned = str(value).replace('€', '').replace(',', '.').strip()
            return float(cleaned)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _parse_date(value: Any) -> Optional[datetime]:
        if not value:
            return None
        if isinstance(value, datetime):
            return value

        text = str(value).strip()
        for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d', '%d-%m-%Y'):
            try:
                return datetime.strptime(text, fmt)
            except ValueError:
                continue
        try:
            return datetime.fromisoformat(text)
        except ValueError:
            return None
    
    def _generate_with_llm(self, context: str, travel_info: Dict[str, Any]) -> str:
        """
        Generate travel plan using LLM.
        
        Args:
            context: Formatted context
            travel_info: Travel information
        
        Returns:
            Generated travel plan
        """
        system_message = """You are an expert travel planner. Your task is to create a comprehensive, 
personalized, and engaging travel itinerary based on the provided information.

IMPORTANT: Format your response in PLAIN TEXT with simple formatting:
- Use UPPERCASE for main section titles (e.g., "RIEPILOGO VIAGGIO")
- Use line breaks to separate sections
- Use "•" for bullet points
- Use simple indentation (2 spaces) for sub-items
- Use "---" to separate major sections
- DO NOT use markdown syntax (no **, ##, ###, etc.)
- DO NOT use special characters except: •, —, -, and basic punctuation

Blend structured API data (voli, meteo, eventi, valuta, input budget) and narrative insights from the RAG context to deliver accurate, vivid recommendations."""

        trip_window = self._compute_trip_window(travel_info)
        rag_present = "=== TRAVEL GUIDE INFORMATION" in context
        budget_inputs_present = "=== BUDGET INPUTS ===" in context

        if trip_window:
            itinerary_instruction = (
                f"Copri tutti i {trip_window['days']} giorni di viaggio (dal {trip_window['start_label']} al {trip_window['end_label']}) "
                "numerando Giorno 1, Giorno 2, ... e indicando la data accanto a ciascun giorno con attività mattina/pomeriggio/sera."
            )
            itinerary_section_detail = (
                f"Copri ogni giorno dal {trip_window['start_label']} al {trip_window['end_label']} (tot {trip_window['days']} giorni).\n"
                "Per ciascun giorno usa questo schema:\n"
                "Giorno X (DATA):\n"
                "  • Mattina: ...\n"
                "  • Pomeriggio: ...\n"
                "  • Sera: ..."
            )
        else:
            itinerary_instruction = (
                "Copri ogni giorno del viaggio in ordine cronologico, numerando Giorno 1, Giorno 2, ... e includendo attività per mattina, pomeriggio e sera."
            )
            itinerary_section_detail = (
                "Copri ogni giorno del viaggio, numerando Giorno 1, Giorno 2, ...\n"
                "Per ciascun giorno usa questo schema:\n"
                "Giorno X:\n"
                "  • Mattina: ...\n"
                "  • Pomeriggio: ...\n"
                "  • Sera: ..."
            )

        budget_instruction = (
            "Quando redigi STIMA BUDGET usa le cifre disponibili (voli, eventi, attrazioni, cambio valuta) come base, indicando range o totale stimato e citando la provenienza."
            if budget_inputs_present else
            "Stima il budget suddividendo le principali voci di spesa con importi realistici."
        )

        rag_instruction = (
            "Per ATTRAZIONI PRINCIPALI ed EVENTI LOCALI integra le descrizioni con i dettagli del contesto RAG (storia, suggerimenti, curiosità pratiche)."
            if rag_present else
            "Descrivi le attrazioni con dettagli pratici e consigli utili."
        )

        logistics_instruction = (
            "In LOGISTICA riassumi i voli disponibili con orari, compagnie e prezzi, aggiungendo consigli su collegamenti e trasporti locali."
        )

        guidelines = [
            itinerary_instruction,
            logistics_instruction,
            "Nel RIEPILOGO VIAGGIO sintetizza la motivazione e i punti salienti del tour.",
            budget_instruction,
            rag_instruction,
            "Mantieni il testo in italiano con tono coinvolgente e professionale."
        ]
        guidelines_text = "\n".join(f"- {item}" for item in guidelines if item)

        prompt = f"""Crea un itinerario di viaggio completo basandoti sulle informazioni seguenti.

CONTESTO DISPONIBILE:
{context}

LINEE GUIDA PRINCIPALI:
{guidelines_text}

FORMATTAZIONE:
- Usa titoli in MAIUSCOLO
- Separa le sezioni con "---"
- Usa "•" per gli elenchi puntati e due spazi per l'indentazione
- Nessun markdown (niente **, ##, ecc.)

SEZIONI OBBLIGATORIE:

---
RIEPILOGO VIAGGIO
Panoramica coinvolgente del viaggio con motivazioni principali.

---
LOGISTICA
Dettagli di volo e trasporti locali.
• Riporta i voli disponibili con orari, compagnie e prezzi.
• Suggerisci opzioni di trasferimento e tempi consigliati.

---
METEO E BAGAGLI
Previsioni meteo e consigli su cosa mettere in valigia.
• Temperature previste e condizioni significative.
• Suggerimenti su abbigliamento e accessori.

---
ITINERARIO GIORNALIERO
{itinerary_section_detail}

---
ATTRAZIONI PRINCIPALI
Luoghi da non perdere con dettagli pratici.
1. Nome attrazione
   Indirizzo: ...
   Orari: ...
   Costo: ...
   Suggerimento/curiosità: ...

---
EVENTI LOCALI
Evidenzia manifestazioni e attività temporanee durante il soggiorno.

---
SUGGERIMENTI PRATICI
Consigli su valuta, lingua, usi locali e sicurezza.
• Valuta e cambio
• Frasi utili e etichetta
• Suggerimenti di sicurezza

---
STIMA BUDGET
Quadratura dei costi principali.
• Voli: ...
• Alloggio: ...
• Cibo: ...
• Attività/Ingressi: ...
• Extra: ...
• Totale stimato: ...

---

Rendi il testo conversazionale, accurato e personalizzato sulle preferenze del viaggiatore!"""

        try:
            response = self.call_llm(
                prompt=prompt,
                system_message=system_message,
                model=config.OPENAI_MODEL,
                temperature=config.OPENAI_TEMPERATURE,
                max_tokens=3000
            )
            return response
        except Exception as e:
            logger.error(f"Failed to generate plan with LLM: {e}")
            return self._generate_fallback_plan(travel_info, context)
    
    def _generate_fallback_plan(
        self, 
        travel_info: Dict[str, Any], 
        context: str
    ) -> str:
        """
        Generate a simple fallback plan if LLM fails.
        
        Args:
            travel_info: Travel information
            context: Context string
        
        Returns:
            Simple formatted plan
        """
        destination = travel_info.get('destination', 'your destination')
        country = travel_info.get('country', '')
        start = travel_info.get('start_date', 'N/A')
        end = travel_info.get('end_date', 'N/A')
        
        plan = f"""
═══════════════════════════════════════════════════════
  PIANO DI VIAGGIO PER {destination.upper()}, {country.upper()}
═══════════════════════════════════════════════════════

---
RIEPILOGO VIAGGIO

Benvenuto nel tuo piano di viaggio personalizzato per {destination}!
Date del viaggio: dal {start} al {end}

Questo itinerario è stato creato appositamente per te considerando 
le tue preferenze e il tuo budget.

---
INFORMAZIONI RACCOLTE

{context}

---
PROSSIMI PASSI

• Prenota i voli e l'alloggio il prima possibile
• Verifica i requisiti per visto e documenti necessari
• Crea un itinerario dettagliato giorno per giorno
• Ricerca ristoranti e attività locali
• Prepara i bagagli in base al clima previsto
• Acquista un'assicurazione di viaggio

---

Buon viaggio! �✈️

"""
        return plan
