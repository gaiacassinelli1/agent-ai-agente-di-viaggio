# 📋 Note Tecniche - Travel AI Assistant v2

## Architettura del Progetto

### Struttura dei File

```
agentediviaggio_v2/
├── agents/                  # Moduli degli agenti specializzati
│   ├── base_agent.py       # Classe base con funzionalità comuni
│   ├── query_parser.py     # Parsing query utente → struttura dati
│   ├── data_collector.py   # Chiamate API esterne (voli, meteo, etc.)
│   ├── rag_manager.py      # Sistema RAG (GitHub → Vector DB → Query)
│   ├── plan_generator.py   # Generazione piano finale con LLM
│   └── __init__.py
├── core/                    # Moduli core del sistema
│   ├── config.py           # Configurazione e variabili d'ambiente
│   ├── orchestrator.py     # Coordinatore del workflow completo
│   └── __init__.py
├── data/                    # Dati statici
│   └── airports_iata.json  # Mapping città → codici IATA
├── main.py                  # Entry point dell'applicazione
├── test_setup.py           # Script di test configurazione
├── requirements.txt        # Dipendenze Python
├── .env.example            # Template per variabili d'ambiente
├── .gitignore             # File da ignorare in Git
├── README.md              # Documentazione principale
└── QUICKSTART.md          # Guida rapida all'uso
```

## Flusso di Elaborazione

### 1. Query Parser (`query_parser.py`)
**Input:** Query utente in linguaggio naturale  
**Output:** Dizionario strutturato con informazioni di viaggio

```python
{
    "destination": "Paris",
    "country": "France",
    "departure_city": "Rome",
    "start_date": "2025-11-15",
    "end_date": "2025-11-19",
    "travelers": "1",
    "budget": "medium",
    "interests": ["culture", "food", "history"]
}
```

**Tecnologia:** OpenAI GPT per parsing NLP

### 2. Data Collector (`data_collector.py`)
**Input:** Informazioni di viaggio strutturate  
**Output:** Dati aggregati da multiple API

```python
{
    "flights": [...],      # Amadeus API
    "weather": {...},      # OpenWeatherMap API
    "monuments": [...],    # Google Places API
    "events": [...],       # Ticketmaster API
    "currency": {...}      # Dati statici
}
```

**API utilizzate:**
- **Amadeus** (voli): Autenticazione OAuth2, endpoint /v2/shopping/flight-offers
- **OpenWeatherMap** (meteo): API key, endpoint /data/2.5/forecast
- **Google Places** (monumenti): API key, text search
- **Ticketmaster** (eventi): API key, search events

### 3. RAG Manager (`rag_manager.py`)
**Input:** Destinazione e interessi  
**Output:** Contesto rilevante da guide di viaggio

**Pipeline RAG:**
1. **Fetch:** Scarica PDF da GitHub repository
2. **Extract:** Estrae testo dai PDF con PyPDF2
3. **Chunk:** Divide in chunks con RecursiveCharacterTextSplitter (800 char, 100 overlap)
4. **Embed:** Crea embeddings con OpenAI text-embedding-3-small
5. **Store:** Salva in ChromaDB (vector database locale)
6. **Query:** Similarity search per recuperare chunks rilevanti (top_k=5)

**Tecnologie:**
- LangChain per pipeline RAG
- ChromaDB per vector store
- OpenAI Embeddings
- PyPDF2 per PDF parsing

### 4. Plan Generator (`plan_generator.py`)
**Input:** Travel info + API data + RAG context  
**Output:** Piano di viaggio formattato

**Prompt Engineering:**
- System message: definisce ruolo e istruzioni
- User message: fornisce tutti i dati strutturati
- Temperature: 0.7 (bilanciamento creatività/coerenza)
- Max tokens: 3000

### 5. Orchestrator (`orchestrator.py`)
**Responsabilità:**
- Coordina tutti gli agenti in sequenza
- Gestisce errori e fallback
- Logging dettagliato di ogni fase
- Supporta refinement interattivo

## Decisioni Architetturali

### Perché Agenti Separati?
- **Separation of Concerns:** Ogni agente ha una responsabilità specifica
- **Testabilità:** Facile testare ogni componente isolatamente
- **Manutenibilità:** Modifiche localizzate senza impatto su altri moduli
- **Riusabilità:** Agenti possono essere usati in altri contesti

### Perché BaseAgent?
- Evita duplicazione codice (DRY principle)
- Client OpenAI condiviso
- Utility comuni (JSON parsing, token counting)
- Facilita estensioni future

### Gestione Errori
**Strategia graceful degradation:**
- Se API fallisce → log warning + continua senza quei dati
- Se LLM fallisce → fallback a template statico
- Nessun crash completo → user experience continuativa

### Caching e Performance
**Ottimizzazioni implementate:**
- Token Amadeus cachato (evita richieste ripetute)
- Vector DB persistente (no re-embedding ad ogni run)
- Timeout configurabili per API

**Future ottimizzazioni:**
- Cache Redis per risultati API
- Background workers per chiamate parallele
- Streaming response da LLM

## Dipendenze Chiave

### Core Dependencies
```
openai>=1.0.0              # LLM calls e embeddings
langchain>=0.1.0           # RAG pipeline
langchain-community        # Integrazioni (Chroma, etc.)
langchain-openai          # OpenAI integration per LangChain
chromadb>=0.4.0           # Vector database
```

### API & Network
```
requests>=2.31.0          # HTTP calls alle API
python-dotenv>=1.0.0      # Environment variables
```

### Document Processing
```
PyPDF2>=3.0.0            # PDF text extraction
```

## Configurazione Avanzata

### Variabili d'Ambiente Opzionali

```env
# Models
OPENAI_MODEL=gpt-4                    # Default: gpt-3.5-turbo
OPENAI_TEMPERATURE=0.7                # Default: 0.7

# Timeouts
REQUEST_TIMEOUT=30                    # Default: 15 seconds

# RAG Settings
CHUNK_SIZE=1000                       # Default: 800
CHUNK_OVERLAP=200                     # Default: 100
RAG_TOP_K=10                         # Default: 5
VECTOR_DB_DIR=./my_vector_db         # Default: ./chroma_db

# GitHub
GITHUB_REPO_URL=https://github.com/user/repo  # Custom repo
```

### Modelli OpenAI Supportati
- **gpt-3.5-turbo:** Veloce, economico, ottimo per testing
- **gpt-4:** Più accurato, migliore reasoning, più costoso
- **gpt-4-turbo:** Bilanciamento prezzo/performance

## Testing

### Test Configurazione
```bash
python test_setup.py
```

Verifica:
- ✓ Dipendenze installate
- ✓ API keys configurate
- ✓ Moduli importabili
- ✓ File dati presenti

### Test Manuale
```python
from agents.query_parser import QueryParser

parser = QueryParser(api_key="sk-...")
result = parser.parse_query("Voglio andare a Parigi")
print(result)
```

## Logging

### Configurazione Logging
```python
# In main.py
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),           # Console
        logging.FileHandler('travel_assistant.log')  # File
    ]
)
```

### Log Levels
- **INFO:** Progresso normale (fase completata, dati raccolti)
- **WARNING:** Problemi non critici (API fallita ma continua)
- **ERROR:** Errori gestiti (parsing fallito, nessun dato)
- **CRITICAL:** Errori fatali (config mancante)

## Estensioni Future

### Possibili Miglioramenti
1. **Database persistente:** Salva piani generati (SQLite/PostgreSQL)
2. **Interfaccia web:** Streamlit o FastAPI + React
3. **Export:** PDF/Word/Markdown del piano generato
4. **Booking integration:** Link diretti per prenotazioni
5. **Mappe interattive:** Visualizzazione punti d'interesse
6. **Multi-lingua:** Supporto italiano/inglese/altre lingue
7. **Collaborative planning:** Più utenti sullo stesso viaggio
8. **Budget tracking:** Stima precisa costi totali
9. **Calendar sync:** Export a Google Calendar/Outlook

### Nuove API da Integrare
- **Booking.com:** Hotel e alloggi
- **TripAdvisor:** Reviews e raccomandazioni
- **Skyscanner:** Confronto prezzi voli
- **Rome2Rio:** Opzioni di trasporto
- **World Weather Online:** Meteo storico

## Troubleshooting Comune

### Import Errors
**Problema:** `Import "agents.xxx" could not be resolved`  
**Soluzione:** Questi sono errori del linter, non problemi reali. Il codice funziona se eseguito dalla root del progetto.

### API Rate Limits
**Problema:** Troppe richieste alle API  
**Soluzione:**
- Usa account a pagamento per limiti superiori
- Implementa caching locale
- Aggiungi delay tra richieste

### Vector DB Lock
**Problema:** `ChromaDB locked`  
**Soluzione:**
- Chiudi tutte le istanze dell'app
- Elimina `chroma_db/` e ricarica documenti

### LLM Output Parsing
**Problema:** JSON non valido dall'LLM  
**Soluzione:**
- Usa `response_format={"type": "json_object"}` (GPT-4/3.5-turbo)
- Aumenta esempi nel prompt
- Fallback a parsing robusto con regex

## Performance Benchmarks

### Tempi Medi (con tutte le API)
- Query parsing: ~2-3 secondi
- Data collection: ~5-10 secondi (parallelo)
- RAG retrieval: ~3-5 secondi
- Plan generation: ~10-20 secondi
- **Totale:** ~20-40 secondi

### Ottimizzazioni Possibili
- Chiamate API parallele con asyncio: -50% tempo
- Cache intelligente: -80% tempo su richieste ripetute
- Streaming LLM: user vede output progressivo

## Contribuire

Per contribuire al progetto:
1. Fork del repository
2. Crea feature branch
3. Test delle modifiche
4. Pull request con descrizione dettagliata

## Licenza

MIT License - Libero uso commerciale e personale

---

**Versione:** 2.0  
**Ultimo aggiornamento:** Ottobre 2025  
**Autore:** Travel AI Assistant Team
