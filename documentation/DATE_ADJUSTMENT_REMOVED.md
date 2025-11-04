# Ripristino Comportamento Date API

## Modifica Effettuata

Rimosso il fallback automatico che modificava le date dell'utente per adattarle ai limiti dell'API test di Amadeus.

## Motivazione

Il sistema precedente **contraddiceva l'intento dell'utente**:
- Utente sceglie: "Voglio viaggiare a Vienna dal 2026-04-30"
- Sistema modificava: "Ti mostro voli per 2025-11-12" 
- ❌ **Sbagliato**: Contraddice completamente il piano dell'utente

## Comportamento Precedente (RIMOSSO)

```python
# CODICE RIMOSSO - NON FARE PIÙ COSÌ!
max_future_days = 90
if (flight_date - today).days > max_future_days:
    logger.warning(f"Flight date {date} too far in future, adjusting...")
    flight_date = today + timedelta(days=30)
    date = flight_date.strftime('%Y-%m-%d')
```

## Comportamento Attuale (CORRETTO)

### Ricerca Voli
```python
# Usa esattamente la data richiesta dall'utente
params = {
    "originLocationCode": departure_iata,
    "destinationLocationCode": destination_iata,
    "departureDate": date,  # Data originale, non modificata!
    "adults": 1,
    "max": 5,
    "currencyCode": "EUR"
}

# Se l'API non trova risultati, ritorna lista vuota
# L'applicazione può comunque generare un piano senza dati API
```

### Ricerca Hotel
```python
# Usa esattamente le date richieste dall'utente
offers_params = {
    "hotelIds": ",".join(current_hotel_ids),
    "checkInDate": check_in,      # Data originale!
    "checkOutDate": check_out,     # Data originale!
    "adults": adults,
    "currency": "EUR"
}

# Se non ci sono tariffe disponibili, ritorna:
# - Lista vuota, oppure
# - Info hotel di base senza prezzi
```

## Gestione Risultati Vuoti

### Scenario 1: Date nel Futuro (es. Aprile 2026)
```
1. User: "Voglio andare a Vienna dal 30 aprile 2026"
2. Sistema chiama API Amadeus con data 2026-04-30
3. API Amadeus: Nessun risultato (test API ha dati limitati)
4. Sistema: flights = [], hotels = []
5. Piano Viaggio generato usando:
   - Conoscenza generale OpenAI
   - Guide PDF (se disponibili)
   - Senza dati specifici voli/hotel
```

### Scenario 2: Date Vicine (es. Prossimi 90 giorni)
```
1. User: "Voglio andare a Roma tra 2 settimane"
2. Sistema chiama API con data reale
3. API Amadeus: Trova voli e hotel disponibili
4. Sistema: flights = [3-5 voli], hotels = [5-10 hotel]
5. Piano Viaggio con dati reali e prezzi aggiornati
```

## Vantaggi del Nuovo Approccio

✅ **Rispetta l'Utente**: Usa sempre le date scelte dall'utente
✅ **Trasparente**: Se non ci sono dati API, è chiaro
✅ **Flessibile**: L'app funziona anche senza dati API
✅ **Onesto**: Non mostra dati per date diverse da quelle richieste

## Logging Migliorato

```python
# Ora il sistema logga chiaramente:
logger.warning(f"No flights found for {departure} to {destination} on {date}")
logger.info("Rate not available for these dates - this is normal for test API")
logger.info("Returning basic hotel info without pricing")
```

## Note sull'API Test Amadeus

L'API test di Amadeus ha **limitazioni conosciute**:
- Dati disponibili solo per ~90 giorni nel futuro
- Non tutti gli aeroporti hanno dati
- Non tutte le date hanno tariffe hotel

**Questo è normale e previsto per un ambiente test.**

## Per Produzione

In produzione con API Amadeus **reale** (non test):
- ✅ Dati disponibili per date future oltre 90 giorni
- ✅ Copertura completa aeroporti mondiali
- ✅ Tariffe hotel aggiornate in tempo reale
- ✅ Prezzi e disponibilità accurati

## File Modificati

**`src/agents/data_collector.py`**
- Rimossa logica di date adjustment in `search_flights()` (righe ~133-147)
- Rimossa logica di date adjustment in `_search_amadeus_hotels()` (righe ~466-480)
- Migliorato logging per chiarire quando non ci sono risultati

## Test

```bash
# Test con date future
venv\Scripts\python.exe run_api.py

# POST /api/plan
# Body: {"query": "Viaggio a Vienna dal 30 aprile 2026"}
# Risultato: Piano generato anche se API non restituisce voli/hotel
```

---

**Status**: ✅ COMPLETATO  
**Data**: 2025-01-30  
**Versione**: 3.0  
**Comportamento**: Rispetta sempre le date dell'utente
