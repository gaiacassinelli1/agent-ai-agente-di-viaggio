# 🌍 Travel AI Assistant v2

Un assistente di viaggio intelligente che utilizza LLM, API esterne e RAG per creare itinerari personalizzati.

## Funzionalità

- **Parsing Query**: Estrae automaticamente destinazione, date, budget e interessi dalla query utente
- **API Integration**: Raccoglie dati da:
  - Amadeus (voli)
  - OpenWeatherMap (meteo)
  - Google Places (monumenti)
  - Ticketmaster (eventi)
  - Currency Exchange (cambi valuta)
- **RAG System**: Recupera informazioni da guide di viaggio su GitHub
- **Piano Personalizzato**: Genera un itinerario completo e discorsivo

## Struttura del Progetto

```
agentediviaggio_v2/
├── agents/
│   ├── base_agent.py          # Classe base per tutti gli agenti
│   ├── query_parser.py         # Estrae info dalla query utente
│   ├── data_collector.py       # Gestisce chiamate API esterne
│   ├── rag_manager.py          # Sistema RAG per documenti
│   └── plan_generator.py       # Genera il piano finale
├── core/
│   ├── orchestrator.py         # Coordina il flusso di lavoro
│   └── config.py               # Configurazione
├── data/
│   └── airports_iata.json      # Codici aeroporti
├── main.py                     # Entry point
├── requirements.txt
└── .env.example
```

## Installazione

1. Clona il repository e vai nella cartella v2:
```bash
cd agentediviaggio_v2
```

2. Crea un ambiente virtuale:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

3. Installa le dipendenze:
```bash
pip install -r requirements.txt
```

4. Crea il file `.env` con le tue API keys:
```
OPENAI_API_KEY=your_key_here
VOLI_API_KEY=your_amadeus_key
VOLI_API_SECRET=your_amadeus_secret
MONUMENTS_API_KEY=your_google_places_key
OPENWEATHER_API_KEY=your_openweather_key
TICKETMASTER_API_KEY=your_ticketmaster_key
GITHUB_TOKEN=your_github_token
```

## Utilizzo

```bash
python main.py
```

Esempio di query:
```
Voglio andare a Parigi dal 15 al 19 novembre partendo da Roma
```

## Architettura

### 1. Query Parser
Estrae informazioni strutturate dalla query in linguaggio naturale:
- Destinazione
- Città di partenza
- Date (inizio/fine)
- Numero viaggiatori
- Budget
- Interessi

### 2. Data Collector
Esegue chiamate parallele alle API per raccogliere:
- Voli disponibili
- Previsioni meteo
- Monumenti e attrazioni
- Eventi locali
- Tassi di cambio valuta

### 3. RAG Manager
- Scarica guide di viaggio da repository GitHub
- Crea vector database con ChromaDB
- Recupera informazioni rilevanti in base alla destinazione

### 4. Plan Generator
Combina tutti i dati raccolti e genera un itinerario personalizzato usando LLM

### 5. Orchestrator
Coordina il flusso:
1. Parse query → travel_info
2. Collect API data → api_results
3. RAG retrieval → rag_context
4. Generate plan → final_itinerary

## Configurazione Avanzata

Puoi personalizzare i modelli LLM e altri parametri in `core/config.py`:

```python
OPENAI_MODEL = "gpt-4"  # Modello principale
OPENAI_TEMPERATURE = 0.7  # Creatività (0-1)
RAG_CHUNK_SIZE = 1000  # Dimensione chunks per RAG
RAG_TOP_K = 5  # Numero documenti da recuperare
```

## Note

- Alcune API richiedono una registrazione (Amadeus, Google Places, etc.)
- Il sistema supporta fallback graceful se alcune API non sono disponibili
- I dati RAG vengono cachati localmente in `chroma_db/`

## Licenza

MIT
