# 🚀 Quick Start Guide

## Avvio Rapido

### 1. CLI Base (Senza Login)
```bash
python run.py
```

### 2. CLI con Autenticazione
```bash
python run_with_login.py
```

### 3. API Server
```bash
python run_api.py
```
L'API sarà disponibile su `http://127.0.0.1:5000`

### 4. Frontend Web
1. Avvia l'API: `python run_api.py`
2. Apri `frontend/index.html` nel browser

## 📋 Requisiti

- Python 3.8+
- Ambiente virtuale attivato
- File `.env` configurato con API keys

## 🔑 Configurazione

Crea un file `.env` nella root:
```env
OPENAI_API_KEY=your_key
VOLI_API_KEY=amadeus_key
VOLI_API_SECRET=amadeus_secret
OPENWEATHER_API_KEY=weather_key
MONUMENTS_API_KEY=google_places_key
TICKETMASTER_API_KEY=ticketmaster_key
```

## 📦 Installazione Dipendenze

```bash
pip install -r requirements.txt
```

## 📚 Documentazione Completa

Vedi `documentation/` per:
- `PROJECT_STRUCTURE.md` - Struttura progetto ottimizzata
- `ARCHITECTURE.md` - Architettura dettagliata
- `API_README.md` - Documentazione API
- `QUICKSTART.md` - Guida rapida

---

**Travel AI Assistant v2.0** 🌍✈️
