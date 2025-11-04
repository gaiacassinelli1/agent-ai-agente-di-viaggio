"""
Export Manager - Esporta piani di viaggio in vari formati
"""
import os
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from icalendar import Calendar, Event, vText

logger = logging.getLogger(__name__)

#TODO: impostare sovrascrittura dell'export post modifiche del refine

class TravelPlanExporter:
    """Gestisce l'export dei piani di viaggio in diversi formati"""
    
    def __init__(self, export_dir: str = "exports"):
        """
        Inizializza l'exporter
        
        Args:
            export_dir: Directory dove salvare gli export
        """
        self.export_dir = export_dir
        self._ensure_export_dir()
    
    def _ensure_export_dir(self):
        """Crea la directory di export se non esiste"""
        if not os.path.exists(self.export_dir):
            os.makedirs(self.export_dir)
            logger.info(f"📁 Creata directory di export: {self.export_dir}")
    
    def _sanitize_filename(self, destination: str) -> str:
        """
        Sanitizza il nome della destinazione per usarlo come nome file
        
        Args:
            destination: Nome della destinazione
            
        Returns:
            Nome file sanitizzato
        """
        # Rimuovi caratteri non validi per filename
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            destination = destination.replace(char, '_')
        return destination.strip()
    
    def _generate_filename(self, travel_info: Dict[str, Any], extension: str) -> str:
        """
        Genera nome file univoco per l'export
        
        Args:
            travel_info: Informazioni sul viaggio
            extension: Estensione del file (es. 'md', 'pdf')
            
        Returns:
            Nome file completo
        """
        destination = travel_info.get('destination', 'unknown')
        destination = self._sanitize_filename(destination)
        
        start_date = travel_info.get('start_date', '')
        if start_date:
            date_str = start_date.replace('-', '')
        else:
            date_str = datetime.now().strftime('%Y%m%d')
        
        timestamp = datetime.now().strftime('%H%M%S')
        filename = f"piano_viaggio_{destination}_{date_str}_{timestamp}.{extension}"
        
        return os.path.join(self.export_dir, filename)
    
    def export_to_markdown(
        self, 
        travel_plan: str, 
        travel_info: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Esporta il piano di viaggio in formato Markdown
        
        Args:
            travel_plan: Piano di viaggio generato
            travel_info: Informazioni strutturate sul viaggio
            metadata: Metadati aggiuntivi da includere (opzionale)
            
        Returns:
            Percorso del file creato
        """
        try:
            filename = self._generate_filename(travel_info, 'md')
            
            # Costruisci il contenuto Markdown
            content = self._build_markdown_content(travel_plan, travel_info, metadata)
            
            # Salva il file
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"✅ Piano esportato in Markdown: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"❌ Errore durante export Markdown: {e}")
            raise
    
    def _build_markdown_content(
        self, 
        travel_plan: str, 
        travel_info: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Costruisce il contenuto Markdown completo con metadata
        
        Args:
            travel_plan: Piano di viaggio
            travel_info: Informazioni viaggio
            metadata: Metadati aggiuntivi
            
        Returns:
            Contenuto Markdown formattato
        """
        # Header con metadata
        destination = travel_info.get('destination', 'N/A')
        country = travel_info.get('country', '')
        start_date = travel_info.get('start_date', 'N/A')
        end_date = travel_info.get('end_date', 'N/A')
        travelers = travel_info.get('travelers', 'N/A')
        budget = travel_info.get('budget', 'N/A')
        
        content = f"""# ✈️ Piano di Viaggio: {destination}

---

## 📋 Informazioni Viaggio

| Campo | Valore |
|-------|--------|
| **Destinazione** | {destination}{f', {country}' if country else ''} |
| **Date** | {start_date} → {end_date} |
| **Viaggiatori** | {travelers} |
| **Budget** | {budget} |
| **Generato il** | {datetime.now().strftime('%d/%m/%Y alle %H:%M')} |

"""
        
        # Aggiungi interessi se presenti
        if 'interests' in travel_info and travel_info['interests']:
            interests = ', '.join(travel_info['interests'])
            content += f"**Interessi:** {interests}\n\n"
        
        # Aggiungi metadata aggiuntivi se presenti
        if metadata:
            content += "## 🔍 Metadata Aggiuntivi\n\n"
            for key, value in metadata.items():
                content += f"- **{key}:** {value}\n"
            content += "\n"
        
        # Separator
        content += "---\n\n"
        
        # Piano di viaggio principale
        content += travel_plan
        
        # Footer
        content += f"""

---

## ℹ️ Note

- Questo piano è stato generato automaticamente da **Travel AI Assistant v2**
- I dati sui voli e gli eventi sono aggiornati al momento della generazione
- Si consiglia di verificare disponibilità e prezzi prima della prenotazione
- Per modifiche o domande, rigenerare il piano con nuove specifiche

---

*Buon viaggio! 🌍✨*
"""
        
        return content
    
    def list_exported_plans(self) -> list:
        """
        Elenca tutti i piani esportati
        
        Returns:
            Lista di dizionari con info sui file esportati
        """
        try:
            files = []
            for filename in os.listdir(self.export_dir):
                filepath = os.path.join(self.export_dir, filename)
                if os.path.isfile(filepath):
                    stat = os.stat(filepath)
                    files.append({
                        'filename': filename,
                        'path': filepath,
                        'size_kb': round(stat.st_size / 1024, 2),
                        'created': datetime.fromtimestamp(stat.st_ctime).strftime('%d/%m/%Y %H:%M'),
                        'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%d/%m/%Y %H:%M')
                    })
            
            # Ordina per data di modifica (più recenti prima)
            files.sort(key=lambda x: x['modified'], reverse=True)
            return files
            
        except Exception as e:
            logger.error(f"❌ Errore durante lettura exports: {e}")
            return []
    
    def export_to_icalendar(
        self,
        travel_plan: str,
        travel_info: Dict[str, Any],
        api_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Esporta il piano di viaggio in formato iCalendar (.ics)
        
        Args:
            travel_plan: Piano di viaggio generato
            travel_info: Informazioni strutturate sul viaggio
            api_data: Dati dalle API (voli, eventi, etc.)
            
        Returns:
            Percorso del file .ics creato
        """
        try:
            filename = self._generate_filename(travel_info, 'ics')
            
            # Crea calendario
            cal = Calendar()
            cal.add('prodid', '-//Travel AI Assistant v2//EN')
            cal.add('version', '2.0')
            cal.add('calscale', 'GREGORIAN')
            cal.add('method', 'PUBLISH')
            cal.add('x-wr-calname', f"Viaggio a {travel_info.get('destination', 'Unknown')}")
            cal.add('x-wr-timezone', 'Europe/Rome')
            cal.add('x-wr-caldesc', f"Itinerario completo per il viaggio a {travel_info.get('destination', 'Unknown')}")
            
            # Aggiungi evento principale del viaggio
            self._add_main_trip_event(cal, travel_info)
            
            # Estrai e aggiungi eventi dall'itinerario
            self._extract_and_add_daily_events(cal, travel_plan, travel_info)
            
            # Aggiungi voli se disponibili
            if api_data and 'flights' in api_data:
                self._add_flight_events(cal, api_data['flights'], travel_info)
            
            # Aggiungi eventi se disponibili
            if api_data and 'events' in api_data:
                self._add_ticketmaster_events(cal, api_data['events'], travel_info)
            
            # Salva il file
            with open(filename, 'wb') as f:
                f.write(cal.to_ical())
            
            logger.info(f"✅ Piano esportato in iCalendar: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"❌ Errore durante export iCalendar: {e}")
            raise
    
    def _add_main_trip_event(self, cal: Calendar, travel_info: Dict[str, Any]):
        """Aggiunge l'evento principale del viaggio"""
        try:
            event = Event()
            
            destination = travel_info.get('destination', 'Destinazione')
            start_date = self._parse_date(travel_info.get('start_date'))
            end_date = self._parse_date(travel_info.get('end_date'))
            
            if not start_date or not end_date:
                logger.warning("Date non valide per evento principale")
                return
            
            # Evento all-day per l'intero viaggio
            event.add('summary', f"🌍 Viaggio a {destination}")
            event.add('dtstart', start_date.date())
            event.add('dtend', (end_date + timedelta(days=1)).date())  # +1 perché end è esclusivo
            event.add('dtstamp', datetime.now())
            event.add('uid', f"trip-{destination}-{start_date.strftime('%Y%m%d')}@travelai")
            
            # Descrizione
            description = f"Viaggio a {destination}"
            country = travel_info.get('country')
            if country:
                description += f", {country}"
            
            travelers = travel_info.get('travelers')
            budget = travel_info.get('budget')
            if travelers:
                description += f"\nViaggiatori: {travelers}"
            if budget:
                description += f"\nBudget: {budget}"
            
            event.add('description', description)
            event.add('location', f"{destination}, {country}" if country else destination)
            event.add('status', 'CONFIRMED')
            event.add('transp', 'OPAQUE')  # Segna come occupato
            
            # Categorie
            event.add('categories', ['VIAGGIO', 'VACANZA'])
            
            # Allarmi
            # Allarme 1 settimana prima
            from icalendar import Alarm
            alarm1 = Alarm()
            alarm1.add('action', 'DISPLAY')
            alarm1.add('description', f'Viaggio a {destination} tra 1 settimana!')
            alarm1.add('trigger', timedelta(weeks=-1))
            event.add_component(alarm1)
            
            # Allarme 1 giorno prima
            alarm2 = Alarm()
            alarm2.add('action', 'DISPLAY')
            alarm2.add('description', f'Viaggio a {destination} domani!')
            alarm2.add('trigger', timedelta(days=-1))
            event.add_component(alarm2)
            
            cal.add_component(event)
            logger.info(f"✓ Aggiunto evento principale: Viaggio a {destination}")
            
        except Exception as e:
            logger.error(f"Errore aggiunta evento principale: {e}")
    
    def _extract_and_add_daily_events(self, cal: Calendar, travel_plan: str, travel_info: Dict[str, Any]):
        """Estrae eventi giornalieri dal piano e li aggiunge al calendario"""
        try:
            # Pattern per estrarre giorni dall'itinerario
            # Cerca pattern come "Giorno 1", "Day 1", "### Giorno 1 -", etc.
            day_pattern = r'(?:###?\s*)?(?:Giorno|Day)\s+(\d+)(?:\s*-\s*(.+?))?(?:\n|:)'
            
            matches = re.finditer(day_pattern, travel_plan, re.IGNORECASE)
            
            start_date = self._parse_date(travel_info.get('start_date'))
            if not start_date:
                return
            
            destination = travel_info.get('destination', 'Destinazione')
            
            for match in matches:
                day_num = int(match.group(1))
                day_title = match.group(2) if match.group(2) else f"Giorno {day_num}"
                
                # Calcola la data per questo giorno
                event_date = start_date + timedelta(days=day_num - 1)
                
                # Estrai le attività per questo giorno
                activities = self._extract_day_activities(travel_plan, match.end())
                
                # Crea eventi per mattina, pomeriggio, sera
                time_slots = [
                    ('Mattina', 9, 0, activities.get('Mattina', '')),
                    ('Pomeriggio', 14, 0, activities.get('Pomeriggio', '')),
                    ('Sera', 19, 0, activities.get('Sera', ''))
                ]
                
                for slot_name, hour, minute, activity in time_slots:
                    if activity:
                        event = Event()
                        event.add('summary', f"{destination} - {day_title}: {slot_name}")
                        
                        event_start = datetime.combine(event_date.date(), datetime.min.time().replace(hour=hour, minute=minute))
                        event_end = event_start + timedelta(hours=3)  # 3 ore per slot
                        
                        event.add('dtstart', event_start)
                        event.add('dtend', event_end)
                        event.add('dtstamp', datetime.now())
                        event.add('uid', f"day{day_num}-{slot_name}-{destination}@travelai")
                        event.add('description', activity)
                        event.add('location', destination)
                        event.add('categories', ['VIAGGIO', 'ATTIVITÀ'])
                        
                        cal.add_component(event)
            
            logger.info(f"✓ Aggiunti eventi giornalieri dall'itinerario")
            
        except Exception as e:
            logger.error(f"Errore estrazione eventi giornalieri: {e}")
    
    def _extract_day_activities(self, travel_plan: str, start_pos: int) -> Dict[str, str]:
        """Estrae le attività per fasce orarie da una sezione del piano"""
        activities = {}
        
        # Cerca le prossime 1000 caratteri dal punto di inizio
        section = travel_plan[start_pos:start_pos + 1000]
        
        # Pattern per estrarre attività per fascia oraria
        time_patterns = [
            (r'\*\*Mattina[:\*]*\s*(.+?)(?=\*\*(?:Pomeriggio|Sera|Giorno)|$)', 'Mattina'),
            (r'\*\*Pomeriggio[:\*]*\s*(.+?)(?=\*\*(?:Sera|Giorno)|$)', 'Pomeriggio'),
            (r'\*\*Sera[:\*]*\s*(.+?)(?=\*\*Giorno|###|$)', 'Sera')
        ]
        
        for pattern, time_slot in time_patterns:
            match = re.search(pattern, section, re.IGNORECASE | re.DOTALL)
            if match:
                activity = match.group(1).strip()
                # Pulisci e limita lunghezza
                activity = re.sub(r'\s+', ' ', activity)[:200]
                activities[time_slot] = activity
        
        return activities
    
    def _add_flight_events(self, cal: Calendar, flights_data: Dict[str, Any], travel_info: Dict[str, Any]):
        """Aggiunge eventi per i voli"""
        try:
            if flights_data.get('error'):
                return
            
            flights = flights_data.get('flights', [])
            destination = travel_info.get('destination', 'Destinazione')
            
            for i, flight in enumerate(flights[:2], 1):  # Solo primi 2 voli (andata e ritorno)
                event = Event()
                
                airline = flight.get('airline', 'Airline')
                flight_num = flight.get('flight_number', 'N/A')
                departure = flight.get('departure', 'N/A')
                arrival = flight.get('arrival', 'N/A')
                dep_time = flight.get('departure_time', 'N/A')
                arr_time = flight.get('arrival_time', 'N/A')
                price = flight.get('price', 'N/A')
                
                event.add('summary', f"✈️ Volo {airline} {flight_num}")
                
                # Cerca di parsare le date dei voli
                start_date = self._parse_date(travel_info.get('start_date'))
                if i == 1 and start_date:  # Volo di andata
                    flight_datetime = self._combine_date_time(start_date, dep_time)
                    event.add('dtstart', flight_datetime)
                    event.add('dtend', flight_datetime + timedelta(hours=2))
                elif i == 2 and travel_info.get('end_date'):  # Volo di ritorno
                    end_date = self._parse_date(travel_info.get('end_date'))
                    if end_date:
                        flight_datetime = self._combine_date_time(end_date, dep_time)
                        event.add('dtstart', flight_datetime)
                        event.add('dtend', flight_datetime + timedelta(hours=2))
                else:
                    continue
                
                event.add('dtstamp', datetime.now())
                event.add('uid', f"flight-{flight_num}-{i}@travelai")
                
                description = f"Volo: {airline} {flight_num}\n"
                description += f"Partenza: {departure} alle {dep_time}\n"
                description += f"Arrivo: {arrival} alle {arr_time}\n"
                description += f"Prezzo: {price}"
                
                event.add('description', description)
                event.add('location', f"{departure} → {arrival}")
                event.add('categories', ['VIAGGIO', 'VOLO'])
                
                # Allarme 3 ore prima
                from icalendar import Alarm
                alarm = Alarm()
                alarm.add('action', 'DISPLAY')
                alarm.add('description', f'Volo {flight_num} tra 3 ore!')
                alarm.add('trigger', timedelta(hours=-3))
                event.add_component(alarm)
                
                cal.add_component(event)
            
            logger.info(f"✓ Aggiunti eventi voli")
            
        except Exception as e:
            logger.error(f"Errore aggiunta voli: {e}")
    
    def _add_ticketmaster_events(self, cal: Calendar, events_data: List[Dict[str, Any]], travel_info: Dict[str, Any]):
        """Aggiunge eventi da Ticketmaster"""
        try:
            destination = travel_info.get('destination', 'Destinazione')
            
            for event_data in events_data[:5]:  # Max 5 eventi
                event = Event()
                
                name = event_data.get('name', 'Evento')
                date = event_data.get('date', '')
                time = event_data.get('time', '')
                venue = event_data.get('venue', '')
                
                event.add('summary', f"🎭 {name}")
                
                # Parse data evento
                if date:
                    event_date = self._parse_event_date(date, time)
                    if event_date:
                        event.add('dtstart', event_date)
                        event.add('dtend', event_date + timedelta(hours=2))
                    else:
                        continue
                else:
                    continue
                
                event.add('dtstamp', datetime.now())
                event.add('uid', f"event-{name[:20]}-{date}@travelai")
                event.add('description', f"Evento: {name}\nVenue: {venue}")
                event.add('location', f"{venue}, {destination}")
                event.add('categories', ['VIAGGIO', 'EVENTO', 'CULTURA'])
                
                cal.add_component(event)
            
            logger.info(f"✓ Aggiunti eventi culturali")
            
        except Exception as e:
            logger.error(f"Errore aggiunta eventi: {e}")
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse una stringa data in vari formati"""
        if not date_str:
            return None
        
        formats = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d']
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        logger.warning(f"Impossibile parsare data: {date_str}")
        return None
    
    def _combine_date_time(self, date: datetime, time_str: str) -> datetime:
        """Combina una data con un orario in formato stringa"""
        try:
            # Cerca pattern HH:MM
            time_match = re.search(r'(\d{1,2}):(\d{2})', time_str)
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2))
                return datetime.combine(date.date(), datetime.min.time().replace(hour=hour, minute=minute))
        except Exception as e:
            logger.warning(f"Errore parsing time '{time_str}': {e}")
        
        # Default: usa la data con ore 9:00
        return datetime.combine(date.date(), datetime.min.time().replace(hour=9, minute=0))
    
    def _parse_event_date(self, date_str: str, time_str: str) -> Optional[datetime]:
        """Parse data e ora di un evento"""
        date = self._parse_date(date_str)
        if not date:
            return None
        
        return self._combine_date_time(date, time_str)
